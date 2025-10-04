# detector.py
"""
Main detector script:
- Opens camera (index or RTSP)
- Runs person detector (MobileNet-SSD via OpenCV DNN)
- For person boxes, runs face detection & embedding
- Pulls known embeddings from server DB (via server endpoint or direct Mongo)
- If no match -> POST alert to server with snapshot
"""

import cv2, time, requests, os, json
import numpy as np
from utils.face_utils import rgb_from_bgr, find_face_locations, get_face_embeddings, normalize_embedding, find_best_match
from utils.storage import save_image
import config

# ---------- Person detector model files (MobileNetSSD) ----------
# Download these files and set paths before running:
PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
CAFFEMODEL = "models/MobileNetSSD_deploy.caffemodel"
PERSON_CLASS_ID = 15
CONF_THRESH = 0.5

# Load net
net = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)

# Get camera
src = int(config.CAMERA_SOURCE) if config.CAMERA_SOURCE.isdigit() else config.CAMERA_SOURCE
cap = cv2.VideoCapture(src)

# Known embeddings cached in memory; refresh periodically
KNOWN_EMBEDDINGS = {}
LAST_REFRESH = 0
REFRESH_INTERVAL = 30  # seconds

def refresh_known_embeddings():
    global KNOWN_EMBEDDINGS, LAST_REFRESH
    try:
        # Option A: call server endpoint to get embeddings (if implemented)
        # For simplicity here, directly call Mongo via REST or implement server /embeddings
        res = requests.get("http://localhost:8000/embeddings")  # implement on server to return dict
        if res.status_code == 200:
            KNOWN_EMBEDDINGS = {k: np.array(v) for k,v in res.json().items()}
        LAST_REFRESH = time.time()
    except Exception as e:
        print("Failed to refresh embeddings:", e)

def post_alert(camera_id, reason, image_path, similarity=None):
    url = config.ALERT_WEBHOOK
    files = {'file': open(image_path, 'rb')}
    data = {'camera': camera_id, 'reason': reason}
    if similarity is not None:
        data['similarity'] = str(similarity)
    try:
        r = requests.post(url, data=data, files=files, timeout=5)
        print("Alert posted, status:", r.status_code)
    except Exception as e:
        print("Alert post error:", e)

while True:
    ret, frame = cap.read()
    if not ret:
        print("No frame from camera")
        time.sleep(1)
        continue

    now = time.time()
    if now - LAST_REFRESH > REFRESH_INTERVAL:
        refresh_known_embeddings()

    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300,300)), 0.007843, (300,300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    person_boxes = []
    for i in range(detections.shape[2]):
        conf = detections[0,0,i,2]
        cls = int(detections[0,0,i,1])
        if conf > CONF_THRESH and cls == PERSON_CLASS_ID:
            box = detections[0,0,i,3:7] * np.array([w,h,w,h])
            sx, sy, ex, ey = box.astype(int)
            person_boxes.append((sx, sy, ex, ey))

    for (sx, sy, ex, ey) in person_boxes:
        pad = 10
        sx, sy = max(0, sx-pad), max(0, sy-pad)
        ex, ey = min(w, ex+pad), min(h, ey+pad)
        person_roi = frame[sy:ey, sx:ex]
        rgb = rgb_from_bgr(person_roi)
        face_locs = find_face_locations(rgb, model="hog")
        if not face_locs:
            continue
        # for now take first face
        face_embs = get_face_embeddings(rgb, face_locations=face_locs)
        if not face_embs:
            continue
        emb = normalize_embedding(face_embs[0])

        # match against known
        name, score = find_best_match(emb, KNOWN_EMBEDDINGS)
        # KNOWN_EMBEDDINGS are numpy arrays (un-normalized maybe) - ensure normalized in server side return
        if name is None or score < config.MATCH_THRESHOLD:
            # Unknown: save snapshot and post alert
            if config.SAVE_UNKNOWN_SNAPSHOT:
                folder = os.path.join(config.STORAGE_PATH, "unknowns")
                path = save_image(frame, folder, prefix="unknown")
            else:
                path = None
            print("Unknown detected! score:", score)
            post_alert(camera_id="cam1", reason="unknown_person", image_path=path if path else "", similarity=score)
        else:
            print(f"Recognized {name} (score {score:.3f})")

    # Debug display - remove in headless installs
    for (sx, sy, ex, ey) in person_boxes:
        cv2.rectangle(frame, (sx, sy), (ex, ey), (0,255,0), 2)
    cv2.imshow("detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
