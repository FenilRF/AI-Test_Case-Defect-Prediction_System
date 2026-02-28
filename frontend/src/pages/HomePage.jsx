/**
 * Home Page — Dashboard
 * -----------------------
 * Shows aggregated stats, recent predictions chart, and quick actions.
 */

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
    FiHome, FiFileText, FiCheckSquare, FiActivity,
    FiAlertTriangle, FiAlertCircle, FiShield, FiUpload, FiList
} from "react-icons/fi";
import {
    Chart as ChartJS,
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement,
    Tooltip,
    Legend,
} from "chart.js";
import { Doughnut, Bar } from "react-chartjs-2";
import { getDashboardStats, getPredictions } from "../services/api";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function HomePage() {
    const [stats, setStats] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [statsRes, predsRes] = await Promise.all([
                    getDashboardStats(),
                    getPredictions(0, 20),
                ]);
                setStats(statsRes.data);
                setPredictions(predsRes.data);
            } catch (err) {
                console.error("Dashboard fetch error:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="spinner-container">
                <div className="spinner"></div>
            </div>
        );
    }

    // ── Chart Data ──────────────────────────────────────
    const riskDoughnut = {
        labels: ["High Risk", "Medium Risk", "Low Risk"],
        datasets: [
            {
                data: [
                    stats?.high_risk_modules || 0,
                    stats?.medium_risk_modules || 0,
                    stats?.low_risk_modules || 0,
                ],
                backgroundColor: [
                    "rgba(239, 68, 68, 0.8)",
                    "rgba(245, 158, 11, 0.8)",
                    "rgba(34, 197, 94, 0.8)",
                ],
                borderColor: [
                    "rgba(239, 68, 68, 1)",
                    "rgba(245, 158, 11, 1)",
                    "rgba(34, 197, 94, 1)",
                ],
                borderWidth: 2,
                hoverOffset: 8,
            },
        ],
    };

    const barData = {
        labels: predictions.slice(0, 10).map((p) => p.module_name),
        datasets: [
            {
                label: "Defect Probability (%)",
                data: predictions.slice(0, 10).map((p) => (p.probability * 100).toFixed(1)),
                backgroundColor: predictions.slice(0, 10).map((p) =>
                    p.risk_level === "High"
                        ? "rgba(239, 68, 68, 0.7)"
                        : p.risk_level === "Medium"
                            ? "rgba(245, 158, 11, 0.7)"
                            : "rgba(34, 197, 94, 0.7)"
                ),
                borderRadius: 6,
                borderSkipped: false,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: "#94a3b8", font: { family: "Inter" } },
            },
            tooltip: {
                backgroundColor: "#1a2235",
                titleColor: "#f1f5f9",
                bodyColor: "#94a3b8",
                borderColor: "rgba(99,102,241,0.3)",
                borderWidth: 1,
                cornerRadius: 8,
            },
        },
        scales: {
            x: {
                ticks: { color: "#64748b", font: { size: 11 } },
                grid: { color: "rgba(148,163,184,0.06)" },
            },
            y: {
                ticks: { color: "#64748b" },
                grid: { color: "rgba(148,163,184,0.06)" },
            },
        },
    };

    return (
        <div>
            <div className="page-header animate-in">
                <h1>Dashboard</h1>
                <p>Overview of test generation and defect prediction metrics</p>
            </div>

            {/* ── Stats Cards ────────────────────────────────── */}
            <div className="stats-grid">
                <div className="stat-card animate-in animate-in-delay-1">
                    <div className="stat-icon purple"><FiFileText /></div>
                    <div className="stat-value">{stats?.total_requirements || 0}</div>
                    <div className="stat-label">Requirements</div>
                </div>
                <div className="stat-card animate-in animate-in-delay-2">
                    <div className="stat-icon blue"><FiCheckSquare /></div>
                    <div className="stat-value">{stats?.total_test_cases || 0}</div>
                    <div className="stat-label">Test Cases</div>
                </div>
                <div className="stat-card animate-in animate-in-delay-3">
                    <div className="stat-icon green"><FiActivity /></div>
                    <div className="stat-value">{stats?.total_predictions || 0}</div>
                    <div className="stat-label">Predictions Made</div>
                </div>
                <div className="stat-card animate-in animate-in-delay-1">
                    <div className="stat-icon red"><FiAlertTriangle /></div>
                    <div className="stat-value">{stats?.high_risk_modules || 0}</div>
                    <div className="stat-label">High Risk</div>
                </div>
                <div className="stat-card animate-in animate-in-delay-2">
                    <div className="stat-icon amber"><FiAlertCircle /></div>
                    <div className="stat-value">{stats?.medium_risk_modules || 0}</div>
                    <div className="stat-label">Medium Risk</div>
                </div>
                <div className="stat-card animate-in animate-in-delay-3">
                    <div className="stat-icon green"><FiShield /></div>
                    <div className="stat-value">{stats?.low_risk_modules || 0}</div>
                    <div className="stat-label">Low Risk</div>
                </div>
            </div>

            {/* ── Charts ─────────────────────────────────────── */}
            <div className="section-grid two-col">
                <div className="chart-container animate-in">
                    <h3>Risk Distribution</h3>
                    <div style={{ height: "280px", display: "flex", justifyContent: "center" }}>
                        {(stats?.total_predictions || 0) > 0 ? (
                            <Doughnut
                                data={riskDoughnut}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: "bottom",
                                            labels: { color: "#94a3b8", padding: 16, font: { family: "Inter" } },
                                        },
                                    },
                                    cutout: "65%",
                                }}
                            />
                        ) : (
                            <div className="empty-state">
                                <FiActivity />
                                <h4>No predictions yet</h4>
                                <p>Run defect predictions to see risk distribution</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="chart-container animate-in">
                    <h3>Recent Predictions — Defect Probability (%)</h3>
                    <div style={{ height: "280px" }}>
                        {predictions.length > 0 ? (
                            <Bar data={barData} options={chartOptions} />
                        ) : (
                            <div className="empty-state">
                                <FiActivity />
                                <h4>No prediction data</h4>
                                <p>Predict defects to populate this chart</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* ── Quick Actions ──────────────────────────────── */}
            <div className="form-section animate-in" style={{ textAlign: "center" }}>
                <h3>Quick Actions</h3>
                <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap", marginTop: "1rem" }}>
                    <Link to="/upload" className="btn-gradient" style={{ textDecoration: "none" }}>
                        <FiUpload /> Generate Test Cases
                    </Link>
                    <Link to="/defect-prediction" className="btn-outline" style={{ textDecoration: "none" }}>
                        <FiActivity /> Predict Defects
                    </Link>
                    <Link to="/test-cases" className="btn-outline" style={{ textDecoration: "none" }}>
                        <FiList /> View Test Cases
                    </Link>
                </div>
            </div>
        </div>
    );
}
