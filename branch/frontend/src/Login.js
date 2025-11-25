import { useState } from "react";
import { motion } from "framer-motion";
import "./Login.css";

function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Simulate login (replace with real API call if needed)
    setTimeout(() => {
      if (email && password) {
        localStorage.setItem("user", JSON.stringify({ email }));
        onLoginSuccess();
      } else {
        setError("Please enter both email and password");
      }
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="login-page">
      <motion.div
        className="login-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div
          className="login-header"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="logo-circle">🏠</div>
          <h1>Smart Security</h1>
          <p>Intelligent Home Monitoring System</p>
        </motion.div>

        <motion.form
          className="login-form"
          onSubmit={handleLogin}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="form-group">
            <label>Email Address</label>
            <motion.input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              whileFocus={{ scale: 1.02 }}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <motion.input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              whileFocus={{ scale: 1.02 }}
              className="form-input"
            />
          </div>

          {error && (
            <motion.div
              className="error-message"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
            >
              {error}
            </motion.div>
          )}

          <motion.button
            type="submit"
            className="login-btn"
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Logging in...
              </>
            ) : (
              "Sign In"
            )}
          </motion.button>
        </motion.form>

        <motion.div
          className="login-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p>Demo credentials: any email & password</p>
        </motion.div>
      </motion.div>

      <motion.div
        className="login-bg-shape"
        animate={{
          y: [0, 20, 0],
          rotate: [0, 5, 0],
        }}
        transition={{ duration: 6, repeat: Infinity }}
      />
    </div>
  );
}

export default LoginPage;
