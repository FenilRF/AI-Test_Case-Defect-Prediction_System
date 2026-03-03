/**
 * App Root — Router & Navigation Layout
 */

import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import { FiHome, FiUpload, FiList, FiActivity, FiShield, FiPenTool, FiMoon, FiSun } from "react-icons/fi";

import HomePage from "./pages/HomePage";
import UploadRequirement from "./pages/UploadRequirement";
import GeneratedTestCases from "./pages/GeneratedTestCases";
import DefectPrediction from "./pages/DefectPrediction";
import UploadDesign from "./pages/UploadDesign";

import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === "dark" ? "light" : "dark");

  return (
    <Router>
      <div className="app-container">
        {/* ── Sidebar Navigation ─────────────────────────── */}
        <nav className="sidebar">
          <div className="sidebar-brand">
            <FiShield className="brand-icon" />
            <span className="brand-text">AI TestGuard</span>
          </div>

          <ul className="sidebar-nav">
            <li>
              <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                <FiHome /> <span>Dashboard</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/upload" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                <FiUpload /> <span>Upload Requirement</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/design" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                <FiPenTool /> <span>Upload Design</span>
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
            <small style={{ marginTop: "0.5rem", display: "block" }}>v1.0.0 — AI Powered</small>
          </div>
        </nav>

        {/* ── Main Content ───────────────────────────────── */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadRequirement />} />
            <Route path="/design" element={<UploadDesign />} />
            <Route path="/test-cases" element={<GeneratedTestCases />} />
            <Route path="/defect-prediction" element={<DefectPrediction />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
