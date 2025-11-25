import "./Log.css";
import { useRef, useEffect } from "react";
import { motion } from "framer-motion";

function Log({ onClick, url, date }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (!video || !canvas) return;
    video.crossOrigin = "anonymous";

    const handleLoadedMetadata = () => {
      video.currentTime = 0.5;
    };

    const handleSeeked = () => {
      try {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      } catch (err) {
        console.error("Error drawing video frame:", err);
      }
    };

    video.addEventListener("loadedmetadata", handleLoadedMetadata);
    video.addEventListener("seeked", handleSeeked);
    video.load();

    return () => {
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
      video.removeEventListener("seeked", handleSeeked);
    };
  }, [url]);

  return (
    <motion.div
      onClick={onClick}
      className="log-card"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.97 }}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <div className="thumbnail">
        <canvas ref={canvasRef} width="200" height="140" />
      </div>
      <div className="details">
        <h3>🎥 Person Motion Detected</h3>
        <p>{date}</p>
      </div>
      <video ref={videoRef} src={url} style={{ display: "none" }} />
    </motion.div>
  );
}

export default Log;