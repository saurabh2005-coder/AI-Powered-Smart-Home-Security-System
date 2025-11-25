import "./Details.css";
import ReactPlayer from "react-player";
import { motion } from "framer-motion";

function DetailsPage({ onBackClicked, url, date }) {
  return (
    <motion.div
      className="details-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="details-header">
        <motion.button
          onClick={onBackClicked}
          className="back-btn"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          ← Back
        </motion.button>
        <h2>🎥 Person Motion Detected</h2>
      </div>

      <motion.div
        className="video-wrapper"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <ReactPlayer
          url={url}
          controls={true}
          width="100%"
          height="100%"
          className="player"
        />
      </motion.div>

      <motion.p
        className="date-text"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        📅 {date}
      </motion.p>
    </motion.div>
  );
}

export default DetailsPage;