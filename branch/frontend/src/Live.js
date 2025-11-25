import "./Live.css";
import { motion } from "framer-motion";
import { useEffect } from "react";

const API_BASE = "http://127.0.0.1:5000";

function LivePage({ onBackClicked }) {
  useEffect(() => {
    // Cleanup when component unmounts (when back button is clicked)
    return () => {
      // Stop the live stream by requesting the /stop-live endpoint
      fetch(`${API_BASE}/stop-live`, { method: "POST" }).catch(() => {});
    };
  }, []);

  const enterFullscreen = () => {
    const el = document.getElementById("live-wrapper");
    if (!el) return;
    if (el.requestFullscreen) el.requestFullscreen();
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    else if (el.msRequestFullscreen) el.msRequestFullscreen();
  };

  return (
    <div className="live-page">
      <motion.div
        className="live-top"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <button className="back-btn" onClick={onBackClicked}>
          ← Back
        </button>
        <h2>Live Camera Feed</h2>
        <div className="live-controls">
          <span className="live-badge">● LIVE</span>
          <button className="fs-btn" onClick={enterFullscreen}>
            Fullscreen
          </button>
        </div>
      </motion.div>

      <motion.div
        id="live-wrapper"
        className="live-stream-wrapper"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <img
          className="live-stream"
          src={`${API_BASE}/live?t=${Date.now()}`}
          alt="Live stream"
        />
      </motion.div>
    </div>
  );
}

export default LivePage;
