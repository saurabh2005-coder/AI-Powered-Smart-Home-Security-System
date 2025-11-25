import "./Main.css";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Log from "./Log";

const API_BASE = "http://127.0.0.1:5000";

function MainPage({ onLogClicked, onLiveClicked, onRegisterClicked }) {
  const [armed, setArmed] = useState(false);
  const [logs, setLogs] = useState([]);
  const [daysOffset, setDaysOffset] = useState(0);

  useEffect(() => {
    fetch(API_BASE + "/get-armed")
      .then((res) => res.json())
      .then((data) => setArmed(data["armed"]))
      .catch(() => alert("Error retrieving armed status from camera."));
  }, []);

  useEffect(() => {
    fetch(
      `${API_BASE}/get-logs?startDate=${getDateXDaysAgo(
        daysOffset
      )}&endDate=${getDateXDaysAgo(daysOffset - 1)}`
    )
      .then((res) => res.json())
      .then((data) => setLogs(data["logs"]))
      .catch(() => setLogs([]));
  }, [daysOffset]);

  const getDateXDaysAgo = (x) => {
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - x);
    const yyyy = pastDate.getFullYear();
    const mm = String(pastDate.getMonth() + 1).padStart(2, "0");
    const dd = String(pastDate.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
  };

  const toggleArmed = () => {
    const options = { method: "POST" };
    setArmed(!armed);
    if (armed) fetch(API_BASE + "/disarm", options);
    else fetch(API_BASE + "/arm", options);
  };

  return (
    <div className="main-page">
      {/* Header */}
      <motion.div
        className="header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1>🏠 Smart Security Control Panel</h1>
        <div className="header-actions">
          <button className="open-live-btn" onClick={onLiveClicked}>
            ▶ Go Live
          </button>
          <button className="open-register-btn" onClick={onRegisterClicked}>
            ✚ Register Face
          </button>
        </div>
        <div className="toggle-container">
          <h2>
            System Status:{" "}
            {armed ? (
              <span className="armed-text">Armed</span>
            ) : (
              <span className="disarmed-text">Disarmed</span>
            )}
          </h2>
          <label className="switch">
            <input type="checkbox" checked={armed} onChange={toggleArmed} />
            <span className="slider round"></span>
          </label>
        </div>
      </motion.div>

      {/* Logs Section */}
      <div className="logs-container">
        <div className="logs-header">
          <h3>📹 Motion Detection Logs</h3>
          <div className="pages">
            <button
              className="nav-btn"
              onClick={() => setDaysOffset(daysOffset + 1)}
            >
              ← Previous
            </button>
            <p className="date-text">{getDateXDaysAgo(daysOffset)}</p>
            <button
              className="nav-btn"
              onClick={() => daysOffset > 0 && setDaysOffset(daysOffset - 1)}
            >
              Next →
            </button>
          </div>
        </div>

        <motion.div
          className="logs-grid"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: { staggerChildren: 0.1 },
            },
          }}
        >
          <AnimatePresence>
            {logs.length > 0 ? (
              logs.map((log, i) => (
                <Log
                  key={i}
                  url={log.url}
                  date={log.date}
                  onClick={() => onLogClicked(log.url, log.date)}
                />
              ))
            ) : (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="no-logs no-logs-message"
              >
                No motion detected for this day.
              </motion.p>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}

export default MainPage;
 