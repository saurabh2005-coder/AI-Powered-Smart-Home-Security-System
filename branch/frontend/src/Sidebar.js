import { motion, AnimatePresence } from "framer-motion";
import "./Sidebar.css";

function Sidebar({ isOpen, setIsOpen, currentPage, setPage, onLogout }) {
  const navItems = [
    { id: "main", icon: "📊", label: "Dashboard", page: "main" },
    { id: "live", icon: "📺", label: "Live Feed", page: "live" },
    { id: "register", icon: "👤", label: "Register Face", page: "register" },
  ];

  const settingsItems = [
    { id: "notifications", icon: "🔔", label: "Notifications" },
    { id: "history", icon: "📜", label: "History" },
    { id: "storage", icon: "💾", label: "Storage" },
  ];

  const handleNavClick = (page) => {
    setPage(page);
    setIsOpen(false);
  };

  const handleProfileClick = () => {
    setPage("profile");
    setIsOpen(false);
  };

  return (
    <>
      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="sidebar-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        className="sidebar"
        initial={{ x: -300 }}
        animate={{ x: isOpen ? 0 : -300 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <div className="sidebar-header">
          <div className="sidebar-logo">🏠</div>
          <h2>SecureHome</h2>
          <button
            className="sidebar-close"
            onClick={() => setIsOpen(false)}
          >
            ✕
          </button>
        </div>

        {/* Profile Section */}
        <button 
          className="sidebar-profile"
          onClick={handleProfileClick}
        >
          <div className="profile-avatar">👤</div>
          <div className="profile-info">
            <h3>User Profile</h3>
            <p>system@home.local</p>
          </div>
        </button>

        {/* Main Navigation */}
        <nav className="sidebar-nav">
          <div className="nav-section-title">Main</div>
          {navItems.map((item, idx) => (
            <motion.button
              key={item.id}
              className={`nav-item ${currentPage === item.page ? "active" : ""}`}
              onClick={() => handleNavClick(item.page)}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ x: 5 }}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </motion.button>
          ))}
        </nav>

        {/* Settings Section */}
        <nav className="sidebar-nav settings-nav">
          <div className="nav-section-title">Settings</div>
          {settingsItems.map((item, idx) => (
            <motion.button
              key={item.id}
              className="nav-item"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: (navItems.length + idx) * 0.05 }}
              whileHover={{ x: 5 }}
              disabled
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </motion.button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <motion.button
            className="logout-btn"
            onClick={onLogout}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            🚪 Logout
          </motion.button>
        </div>
      </motion.div>

      {/* Hamburger Button (visible when sidebar closed) */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            className="hamburger-btn"
            onClick={() => setIsOpen(true)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            whileHover={{ scale: 1.1 }}
          >
            ☰
          </motion.button>
        )}
      </AnimatePresence>
    </>
  );
}

export default Sidebar;
