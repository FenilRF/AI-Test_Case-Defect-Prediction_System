/**
 * Home Page — Dashboard
 * -----------------------
 * Enterprise-grade QA dashboard with workflow stepper,
 * redesigned stat cards, project activity, risk distribution,
 * recent test cases table, and quick action cards.
 */

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
    FiFileText, FiCheckSquare, FiActivity,
    FiAlertTriangle, FiShield, FiUpload, FiList,
    FiDownload, FiPlus, FiCheck, FiLoader, FiClock,
    FiPenTool, FiAlertCircle, FiTrendingUp,
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
import { Bar } from "react-chartjs-2";
import { getDashboardStats, getPredictions, getTestCases } from "../services/api";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function HomePage() {
    const [stats, setStats] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [recentCases, setRecentCases] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [statsRes, predsRes, casesRes] = await Promise.all([
                    getDashboardStats(),
                    getPredictions(0, 20),
                    getTestCases({ skip: 0, limit: 5 }),
                ]);
                setStats(statsRes.data);
                setPredictions(predsRes.data);
                setRecentCases(Array.isArray(casesRes.data) ? casesRes.data.slice(0, 5) : []);
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

    // ── Workflow Progress ──────────────────────────────
    const totalReqs = stats?.total_requirements || 0;
    const totalCases = stats?.total_test_cases || 0;
    const totalPreds = stats?.total_predictions || 0;
    const workflowSteps = [
        { label: "Requirement Analysis", done: totalReqs > 0 },
        { label: "Design Mapping", done: totalCases > 0 },
        { label: "Generation Phase", done: totalCases > 5, inProgress: totalCases > 0 && totalCases <= 5 },
        { label: "Review & Approve", done: totalPreds > 0 },
    ];
    const completedSteps = workflowSteps.filter(s => s.done).length;
    const progressPercent = Math.round((completedSteps / workflowSteps.length) * 100);

    // ── Avg Defect Probability ────────────────────────
    const avgDefect = predictions.length > 0
        ? (predictions.reduce((sum, p) => sum + p.probability, 0) / predictions.length * 100).toFixed(1)
        : "0.0";

    // ── Risk Distribution Counts ──────────────────────
    const riskCounts = {
        high: stats?.high_risk_modules || 0,
        medium: stats?.medium_risk_modules || 0,
        low: stats?.low_risk_modules || 0,
    };
    const riskTotal = riskCounts.high + riskCounts.medium + riskCounts.low || 1;

    // ── Project Activity Chart ────────────────────────
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
            {/* ── Page Header with Status & Actions ─────── */}
            <div className="page-header animate-in" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
                <div>
                    <div className="system-status-badge">
                        <span className="status-dot"></span>
                        SYSTEM ACTIVE
                        <span className="status-sync">• Last sync just now</span>
                    </div>
                    <h1>Dashboard Overview</h1>
                    <p>High-level insights for your QA test generation pipeline.</p>
                </div>
                <div className="header-actions">
                    <Link to="/test-cases" className="btn-outline" style={{ textDecoration: "none", gap: "0.4rem" }}>
                        <FiDownload /> Export Report
                    </Link>
                    <Link to="/upload" className="btn-gradient" style={{ textDecoration: "none", gap: "0.4rem" }}>
                        <FiPlus /> New Analysis
                    </Link>
                </div>
            </div>

            {/* ── AI Workflow Progress ──────────────────── */}
            <div className="workflow-section animate-in">
                <div className="workflow-header">
                    <h3>AI WORKFLOW PROGRESS</h3>
                    <span className="workflow-percent">{progressPercent}% Complete</span>
                </div>
                <div className="workflow-stepper">
                    {workflowSteps.map((step, i) => (
                        <div key={i} className={`workflow-step ${step.done ? "done" : step.inProgress ? "in-progress" : "pending"}`}>
                            <div className="step-circle">
                                {step.done ? <FiCheck /> : step.inProgress ? <FiLoader className="step-spin" /> : <span>{i + 1}</span>}
                            </div>
                            <span className="step-label">{step.label}</span>
                            {i < workflowSteps.length - 1 && <div className={`step-line ${step.done ? "done" : ""}`}></div>}
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Stats Cards ──────────────────────────── */}
            <div className="stats-grid four-col">
                <div className="stat-card-v2 animate-in animate-in-delay-1">
                    <div className="stat-card-v2-icon blue"><FiFileText /></div>
                    <div className="stat-card-v2-body">
                        <span className="stat-card-v2-label">Total Test Cases</span>
                        <span className="stat-card-v2-value">{totalCases.toLocaleString()}</span>
                    </div>
                    <span className="stat-card-v2-badge blue">{totalReqs} req</span>
                </div>
                <div className="stat-card-v2 animate-in animate-in-delay-2">
                    <div className="stat-card-v2-icon red"><FiAlertCircle /></div>
                    <div className="stat-card-v2-body">
                        <span className="stat-card-v2-label">Avg Defect Probability</span>
                        <span className="stat-card-v2-value">{avgDefect}%</span>
                    </div>
                    <span className="stat-card-v2-badge red">{riskCounts.high} high</span>
                </div>
                <div className="stat-card-v2 animate-in animate-in-delay-3">
                    <div className="stat-card-v2-icon green"><FiShield /></div>
                    <div className="stat-card-v2-body">
                        <span className="stat-card-v2-label">Low Risk Modules</span>
                        <span className="stat-card-v2-value">{riskCounts.low}</span>
                    </div>
                    <span className="stat-card-v2-badge green">Stable</span>
                </div>
                <div className="stat-card-v2 animate-in animate-in-delay-4">
                    <div className="stat-card-v2-icon purple"><FiTrendingUp /></div>
                    <div className="stat-card-v2-body">
                        <span className="stat-card-v2-label">Predictions Made</span>
                        <span className="stat-card-v2-value">{totalPreds}</span>
                    </div>
                    <span className="stat-card-v2-badge purple">{totalPreds} total</span>
                </div>
            </div>

            {/* ── Charts Row ───────────────────────────── */}
            <div className="section-grid two-col">
                {/* Project Activity */}
                <div className="chart-container animate-in">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                        <h3 style={{ margin: 0 }}>Project Activity</h3>
                        <div className="chart-legend-inline">
                            <span className="legend-dot green"></span> Generations
                            <span className="legend-dot blue" style={{ marginLeft: "1rem" }}></span> Predictions
                        </div>
                    </div>
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

                {/* Risk Distribution */}
                <div className="chart-container animate-in">
                    <h3>Risk Distribution</h3>
                    <div className="risk-dist-bars">
                        <div className="risk-dist-row">
                            <span className="risk-dist-label">High Risk</span>
                            <div className="risk-dist-track">
                                <div className="risk-dist-fill high" style={{ width: `${(riskCounts.high / riskTotal) * 100}%` }}></div>
                            </div>
                            <span className="risk-dist-count red">{riskCounts.high} MODULES</span>
                        </div>
                        <div className="risk-dist-row">
                            <span className="risk-dist-label">Medium Risk</span>
                            <div className="risk-dist-track">
                                <div className="risk-dist-fill medium" style={{ width: `${(riskCounts.medium / riskTotal) * 100}%` }}></div>
                            </div>
                            <span className="risk-dist-count amber">{riskCounts.medium} MODULES</span>
                        </div>
                        <div className="risk-dist-row">
                            <span className="risk-dist-label">Low Risk</span>
                            <div className="risk-dist-track">
                                <div className="risk-dist-fill low" style={{ width: `${(riskCounts.low / riskTotal) * 100}%` }}></div>
                            </div>
                            <span className="risk-dist-count green">{riskCounts.low} MODULES</span>
                        </div>
                    </div>
                    {(stats?.total_predictions || 0) === 0 && (
                        <div style={{ textAlign: "center", marginTop: "1rem" }}>
                            <Link to="/defect-prediction" className="btn-outline" style={{ textDecoration: "none", fontSize: "0.82rem" }}>
                                Get started →
                            </Link>
                        </div>
                    )}
                </div>
            </div>

            {/* ── Recent Test Cases ─────────────────────── */}
            <div className="data-table-wrapper animate-in">
                <div className="data-table-header">
                    <h3>Recent Test Cases</h3>
                    <Link to="/test-cases" className="view-all-link">View All</Link>
                </div>
                {recentCases.length > 0 ? (
                    <div style={{ overflowX: "auto" }}>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>TEST ID</th>
                                    <th>SCENARIO</th>
                                    <th>TYPE</th>
                                    <th>PRIORITY</th>
                                    <th>LEVEL</th>
                                    <th>MODULE</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentCases.map((tc, idx) => (
                                    <tr key={tc.test_id || idx}>
                                        <td style={{ fontWeight: 600, fontSize: "0.82rem" }}>TC-{String(idx + 2).padStart(4, "0")}</td>
                                        <td>{tc.scenario}</td>
                                        <td>
                                            <span className={`badge badge-${tc.test_type}`}>
                                                {tc.test_type}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge badge-${tc.priority?.toLowerCase()}`}>
                                                {tc.priority}
                                            </span>
                                        </td>
                                        <td>{tc.test_level || "Unit"}</td>
                                        <td>{tc.module_name}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state" style={{ padding: "2rem" }}>
                        <FiList />
                        <h4>No test cases yet</h4>
                        <p>Generate test cases to see them here</p>
                    </div>
                )}
            </div>

            {/* ── Quick Action Cards ───────────────────── */}
            <div className="quick-actions-grid animate-in">
                <Link to="/upload" className="quick-action-card">
                    <div className="qa-card-icon blue"><FiUpload /></div>
                    <h4>Upload Requirement</h4>
                    <p>Generate test cases from text or documents</p>
                </Link>
                <Link to="/design" className="quick-action-card">
                    <div className="qa-card-icon purple"><FiPenTool /></div>
                    <h4>Upload Design</h4>
                    <p>Analyze UI designs for comprehensive testing</p>
                </Link>
                <Link to="/defect-prediction" className="quick-action-card">
                    <div className="qa-card-icon red"><FiAlertTriangle /></div>
                    <h4>Predict Defects</h4>
                    <p>ML-based module risk prediction engine</p>
                </Link>
            </div>
        </div>
    );
}
