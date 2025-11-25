import { useRef, useState, useEffect } from "react";
import "./Register.css";

const API_BASE = "http://127.0.0.1:5000";

function RegisterPage({ onBackClicked }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => {
    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStreaming(true);
      } catch (e) {
        console.error(e);
      }
    };
    start();

    return () => {
      const tracks = videoRef.current?.srcObject?.getTracks?.() || [];
      tracks.forEach((t) => t.stop());
    };
  }, []);

  const captureAndUpload = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);
    canvas.toBlob(async (blob) => {
      const fd = new FormData();
      fd.append("name", name);
      fd.append("image", blob, "capture.jpg");
      try {
        const res = await fetch(API_BASE + "/register-face", { method: "POST", body: fd });
        const data = await res.json();
        if (res.ok) alert("Registered: " + name);
        else alert("Error: " + (data.error || "Unknown"));
      } catch (e) {
        alert("Upload failed");
      }
    }, "image/jpeg");
  };

  return (
    <div className="register-page">
      <div className="register-top">
        <button className="back-btn" onClick={onBackClicked}>← Back</button>
        <h2>Register Face</h2>
      </div>

      <div className="register-body">
        <video ref={videoRef} className="register-video" />
        <canvas ref={canvasRef} style={{ display: "none" }} />

        <div className="register-controls">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
          <button className="capture-btn" onClick={captureAndUpload} disabled={!name}>
            Capture & Register
          </button>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
