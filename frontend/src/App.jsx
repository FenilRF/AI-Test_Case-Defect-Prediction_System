/**
 * App Root — Router & Navigation Layout
 * Includes top header bar, sidebar, breadcrumbs
 */

import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation, Link } from "react-router-dom";
import {
  FiHome, FiUpload, FiList, FiActivity, FiShield, FiPenTool,
  FiMoon, FiSun, FiMenu, FiX, FiSettings, FiBell, FiUser,
  FiPlus, FiChevronRight,
} from "react-icons/fi";

import HomePage from "./pages/HomePage";
import UploadRequirement from "./pages/UploadRequirement";
import GeneratedTestCases from "./pages/GeneratedTestCases";
import DefectPrediction from "./pages/DefectPrediction";
import UploadDesign from "./pages/UploadDesign";

import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

/* ── Breadcrumb Map ─────────────────────────────────── */
const BREADCRUMB_MAP = {
  "/": { label: "Dashboard", parent: null },
  "/upload": { label: "Requirement Analysis", parent: "/" },
  "/design": { label: "Design Upload", parent: "/" },
  "/test-cases": { label: "Test Cases", parent: "/" },
  "/defect-prediction": { label: "Defect Prediction", parent: "/" },
};

/* ── Top Header Nav Tabs ────────────────────────────── */
const NAV_TABS = [
  { label: "Overview", path: "/" },
  { label: "Test Suite", path: "/test-cases" },
  { label: "Risk Analysis", path: "/defect-prediction" },
];

function Breadcrumbs() {
  const { pathname } = useLocation();
  const current = BREADCRUMB_MAP[pathname];
  if (!current || !current.parent) return null;

  const crumbs = [];
  let path = pathname;
  while (path && BREADCRUMB_MAP[path]) {
    crumbs.unshift({ path, label: BREADCRUMB_MAP[path].label });
    path = BREADCRUMB_MAP[path].parent;
  }

  return (
    <nav className="breadcrumbs">
      {crumbs.map((c, i) => (
        <span key={c.path} className="breadcrumb-item">
          {i > 0 && <FiChevronRight className="breadcrumb-sep" />}
          {i < crumbs.length - 1 ? (
            <Link to={c.path} className="breadcrumb-link">{c.label}</Link>
          ) : (
            <span className="breadcrumb-current">{c.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}

function AppContent() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Auto-close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  const toggleTheme = () => setTheme(prev => prev === "dark" ? "light" : "dark");

  return (
    <div className="app-container">
      {/* ── Hamburger Button (mobile only) ─────────────── */}
      <button
        className="hamburger-btn"
        onClick={() => setSidebarOpen(prev => !prev)}
        aria-label="Toggle navigation"
      >
        {sidebarOpen ? <FiX /> : <FiMenu />}
      </button>

      {/* ── Mobile Overlay ────────────────────────────── */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* ── Sidebar Navigation ─────────────────────────── */}
      <nav className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-brand">
          <FiShield className="brand-icon" />
          <div className="brand-info">
            <span className="brand-text">QA Platform</span>
            <span className="brand-sub">ENTERPRISE AI</span>
          </div>
        </div>

        <ul className="sidebar-nav">
          <li>
            <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <FiHome /> <span>Dashboard</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/upload" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <FiUpload /> <span>Requirement Upload</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/design" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <FiPenTool /> <span>Design Upload</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/test-cases" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <FiList /> <span>Test Cases</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/defect-prediction" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <FiActivity /> <span>Defect Prediction</span>
            </NavLink>
          </li>
        </ul>

        <div className="sidebar-footer">
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === "dark" ? <FiSun /> : <FiMoon />}
            <span>{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
          </button>
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">
              <FiUser />
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">QA Engineer</span>
              <span className="sidebar-user-role">AI Platform v2.0</span>
            </div>
          </div>
        </div>
      </nav>

      {/* ── Main Content Wrapper ───────────────────────── */}
      <div className="main-wrapper">
        {/* ── Top Header Bar ────────────────────────────── */}
        <header className="top-header">
          <div className="top-header-tabs">
            {NAV_TABS.map(tab => (
              <NavLink
                key={tab.path}
                to={tab.path}
                end={tab.path === "/"}
                className={({ isActive }) => `top-tab ${isActive ? "active" : ""}`}
              >
                {tab.label}
              </NavLink>
            ))}
          </div>
          <div className="top-header-actions">
            <button className="top-icon-btn" title="Settings">
              <FiSettings />
            </button>
            <Link to="/design" className="top-icon-btn" title="Design Upload">
              <FiPenTool />
            </Link>
            <div className="top-avatar">
              <FiUser />
            </div>
            <Link to="/upload" className="btn-generate-test">
              <FiPlus /> Generate Test
            </Link>
          </div>
        </header>

        {/* ── Page Content ─────────────────────────────── */}
        <main className="main-content">
          <Breadcrumbs />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadRequirement />} />
            <Route path="/design" element={<UploadDesign />} />
            <Route path="/test-cases" element={<GeneratedTestCases />} />
            <Route path="/defect-prediction" element={<DefectPrediction />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
