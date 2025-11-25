import "./Profile.css";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:5000";

function ProfilePage({ onBackClicked }) {
  const [userEmail, setUserEmail] = useState("");
  const [systemStats, setSystemStats] = useState({
    armed: false,
    totalEvents: 0,
    recognizedFaces: 0,
  });

  useEffect(() => {
    // Get user email from localStorage
    const user = localStorage.getItem("user");
    if (user) {
      setUserEmail(user);
    }

    // Fetch system stats
    Promise.all([
      fetch(`${API_BASE}/get-armed`)
        .then((res) => res.json())
        .then((data) => ({ armed: data.armed }))
        .catch(() => ({ armed: false })),
      fetch(`${API_BASE}/get-logs?startDate=2024-01-01&endDate=2024-12-31`)
        .then((res) => res.json())
        .then((data) => ({ totalEvents: data.logs?.length || 0 }))
        .catch(() => ({ totalEvents: 0 })),
    ]).then((results) => {
      setSystemStats({
        armed: results[0].armed,
        totalEvents: results[1].totalEvents,
        recognizedFaces: 0,
      });
    });
  }, []);

  return (
    <div className="profile-page">
      <motion.div
        className="profile-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <button className="back-btn" onClick={onBackClicked}>
          ← Back
        </button>
        <h1>👤 User Profile</h1>
      </motion.div>

      <div className="profile-content">
        {/* Profile Card */}
        <motion.div
          className="profile-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="profile-avatar-large">👤</div>
          <div className="profile-details">
            <h2>System Administrator</h2>
            <p className="email">{userEmail || "system@home.local"}</p>
            <p className="role">Smart Home Security Manager</p>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="stats-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <h3>System Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">🎯</div>
              <div className="stat-info">
                <p className="stat-label">System Status</p>
                <p className="stat-value">
                  {systemStats.armed ? "🟢 Armed" : "🔴 Disarmed"}
                </p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📹</div>
              <div className="stat-info">
                <p className="stat-label">Total Events</p>
                <p className="stat-value">{systemStats.totalEvents}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-info">
                <p className="stat-label">Registered Faces</p>
                <p className="stat-value">{systemStats.recognizedFaces}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Info Section */}
        <motion.div
          className="info-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <h3>System Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Application:</span>
              <span className="info-value">Smart Home Security System</span>
            </div>
            <div className="info-item">
              <span className="info-label">Version:</span>
              <span className="info-value">1.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">API Server:</span>
              <span className="info-value">http://127.0.0.1:5000</span>
            </div>
            <div className="info-item">
              <span className="info-label">Camera Support:</span>
              <span className="info-value">Facial Recognition Enabled</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default ProfilePage;
