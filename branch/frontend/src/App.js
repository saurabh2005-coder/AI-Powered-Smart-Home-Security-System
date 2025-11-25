import { useState, useEffect } from "react";
import MainPage from "./Main";
import DetailsPage from "./Details";
import LivePage from "./Live";
import RegisterPage from "./Register";
import LoginPage from "./Login";
import ProfilePage from "./Profile";
import Sidebar from "./Sidebar";

const MAIN_PAGE = "main";
const DETAILS_PAGE = "details_page";
const LIVE_PAGE = "live";
const REGISTER_PAGE = "register";
const PROFILE_PAGE = "profile";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [page, setPage] = useState(MAIN_PAGE);
  const [log, setLog] = useState(undefined);

  useEffect(() => {
    // Check if user is already logged in
    const user = localStorage.getItem("user");
    if (user) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    setSidebarOpen(false);
    setPage(MAIN_PAGE);
  };

  if (!isLoggedIn) {
    return <LoginPage onLoginSuccess={handleLogin} />;
  }

  const renderPage = () => {
    switch (page) {
      case MAIN_PAGE:
        return (
          <MainPage
            onLogClicked={(url, date) => {
              setLog({ url, date });
              setPage(DETAILS_PAGE);
            }}
            onLiveClicked={() => setPage(LIVE_PAGE)}
            onRegisterClicked={() => setPage(REGISTER_PAGE)}
          />
        );
      case DETAILS_PAGE:
        return (
          <DetailsPage
            onBackClicked={() => {
              setPage(MAIN_PAGE);
              setLog(undefined);
            }}
            {...log}
          />
        );
      case LIVE_PAGE:
        return (
          <LivePage
            onBackClicked={() => {
              setPage(MAIN_PAGE);
            }}
          />
        );
      case REGISTER_PAGE:
        return <RegisterPage onBackClicked={() => setPage(MAIN_PAGE)} />;
      case PROFILE_PAGE:
        return <ProfilePage onBackClicked={() => setPage(MAIN_PAGE)} />;
      default:
        return null;
    }
  };

  return (
    <div className="app-layout">
      {sidebarOpen && (
        <Sidebar
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
          currentPage={page}
          setPage={setPage}
          onLogout={handleLogout}
        />
      )}
      <button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
      >
        {sidebarOpen ? "✕" : "☰"}
      </button>
      <div className={`page-container ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
        {renderPage()}
      </div>
    </div>
  );
}

export default App;
