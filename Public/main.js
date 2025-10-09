// main.js - client-side app that runs person detection in the browser using BodyPix

const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const ctx = overlay.getContext('2d');

const statusEl = document.getElementById('status');
const toggleBtn = document.getElementById('toggle');
const snapshotBtn = document.getElementById('snapshot');
const speedSelect = document.getElementById('speed');

let net = null;
let running = false;
let modelConfig = null;

// default model config mapping
function getModelConfig(mode) {
  if (mode === 'fast') {
    return {
      architecture: 'MobileNetV1',
      outputStride: 16,
      multiplier: 0.50,
      quantBytes: 2
    };
  } else if (mode === 'accurate') {
    return {
      architecture: 'ResNet50',
      outputStride: 32,
      quantBytes: 2
    };
  } else { // balanced
    return {
      architecture: 'MobileNetV1',
      outputStride: 16,
      multiplier: 0.75,
      quantBytes: 2
    };
  }
}

async function setupCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720, facingMode: 'user' },
      audio: false
    });
    video.srcObject = stream;

    return new Promise(resolve => {
      video.onloadedmetadata = () => {
        // set canvas to match video
        overlay.width = video.videoWidth;
        overlay.height = video.videoHeight;
        resolve();
      };
    });
  } catch (err) {
    alert('Could not access camera: ' + err.message);
    throw err;
  }
}

function drawBoundingBox(box, label='person') {
  const [x, y, w, h] = box;
  ctx.lineWidth = Math.max(2, Math.round(Math.max(overlay.width, overlay.height) / 400));
  ctx.strokeStyle = '#00FF80';
  ctx.fillStyle = '#00FF80';
  ctx.strokeRect(x, y, w, h);
  ctx.font = `${12 + Math.round(overlay.width/200)}px Arial`;
  ctx.fillText(label, x + 4, Math.max(y + 14, y + 12));
}

function maskToBoundingBoxes(mask) {
  // mask is 2D boolean array (height x width)
  // compute bounding box of all true pixels (single person)
  const height = mask.length;
  const width = mask[0].length;
  let minX = width, minY = height, maxX = 0, maxY = 0;
  let found = false;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (mask[y][x]) {
        found = true;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (!found) return [];
  // return single bounding box [x,y,w,h]
  return [[minX, minY, (maxX - minX + 1), (maxY - minY + 1)]];
}

function drawMask(segmentation, opacity = 0.6) {
  const {data, width, height} = segmentation;
  // make an ImageData object
  const img = ctx.createImageData(width, height);
  for (let i = 0; i < data.length; i++) {
    const n = i * 4;
    if (data[i] === 1) { // person
      img.data[n] = 0;      // R
      img.data[n+1] = 255;  // G
      img.data[n+2] = 128;  // B
      img.data[n+3] = Math.round(255 * opacity); // alpha
    } else {
      img.data[n+3] = 0;
    }
  }
  // draw the mask scaled to overlay size
  // create an offscreen canvas to scale pixel-perfect
  const off = document.createElement('canvas');
  off.width = width;
  off.height = height;
  const offCtx = off.getContext('2d');
  offCtx.putImageData(img, 0, 0);
  ctx.drawImage(off, 0, 0, overlay.width, overlay.height);
}

async function loadModel(mode) {
  statusEl.textContent = 'Status: loading model...';
  const cfg = getModelConfig(mode);
  net = await bodyPix.load(cfg);
  statusEl.textContent = 'Status: model loaded';
}

async function detectLoop() {
  if (!running) return;
  // run segmentation
  // options tuned for speed/quality
  const segmentationThreshold = 0.5;

  const segmentation = await net.segmentPerson(video, {
    flipHorizontal: false,
    internalResolution: 'medium',
    segmentationThreshold
  });

  // clear overlay
  ctx.clearRect(0, 0, overlay.width, overlay.height);

  // draw the mask
  // segmentation has width/height equal to video resolution
  drawMask(segmentation, 0.5);

  // convert segmentation mask into boolean 2D array
  const w = segmentation.width, h = segmentation.height;
  const mask = [];
  for (let y = 0; y < h; y++) {
    const row = [];
    for (let x = 0; x < w; x++) {
      row.push(segmentation.data[y * w + x] === 1);
    }
    mask.push(row);
  }

  // compute bounding boxes (simple approach: one blob -> one box)
  const boxes = maskToBoundingBoxes(mask);

  // scale box coordinates to overlay (they already match segmentation resolution
  // which is same as video in our case) — if not, rescale here.
  boxes.forEach(box => {
    drawBoundingBox(box);
  });

  // schedule next detection (use requestAnimationFrame for smoothness)
  requestAnimationFrame(detectLoop);
}

async function start() {
  toggleBtn.disabled = true;
  await setupCamera();
  modelConfig = getModelConfig(speedSelect.value);
  await loadModel(speedSelect.value);
  toggleBtn.disabled = false;
  toggleBtn.textContent = 'Stop';
  running = true;
  statusEl.textContent = 'Status: running';
  detectLoop();
}

function stop() {
  running = false;
  toggleBtn.textContent = 'Start';
  statusEl.textContent = 'Status: stopped';
  ctx.clearRect(0, 0, overlay.width, overlay.height);
}

// toggle button
toggleBtn.addEventListener('click', async () => {
  if (!running) {
    await start();
  } else {
    stop();
  }
});

// snapshot sends current overlay + video frame to Python backend (optional)
snapshotBtn.addEventListener('click', async () => {
  // compose a combined image (video + overlay)
  const temp = document.createElement('canvas');
  temp.width = overlay.width;
  temp.height = overlay.height;
  const tctx = temp.getContext('2d');
  // draw video
  tctx.drawImage(video, 0, 0, temp.width, temp.height);
  // draw current overlay (mask & boxes)
  tctx.drawImage(overlay, 0, 0, temp.width, temp.height);

  const dataUrl = temp.toDataURL('image/png');

  // send to Python backend (adjust url if running elsewhere)
  try {
    const resp = await fetch('http://localhost:5000/save_snapshot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl })
    });
    const json = await resp.json();
    alert('Snapshot saved: ' + json.filename);
  } catch (err) {
    alert('Could not send snapshot to Python backend: ' + err.message);
  }
});
