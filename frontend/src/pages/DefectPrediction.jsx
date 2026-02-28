/**
 * Defect Prediction Dashboard
 * ------------------------------
 * Form to input module metrics → ML prediction → risk visualization.
 * Shows prediction history with Chart.js bar chart.
 */

import { useState, useEffect } from "react";
import { FiActivity, FiCpu, FiBarChart2, FiClock } from "react-icons/fi";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Tooltip,
    Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { predictDefect, getPredictions } from "../services/api";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const INITIAL_FORM = {
    module_name: "",
    lines_of_code: "",
    complexity_score: "",
    past_defects: "",
    code_churn: "",
};

export default function DefectPrediction() {
    const [form, setForm] = useState(INITIAL_FORM);
    const [loading, setLoading] = useState(false);
    const [prediction, setPrediction] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchPredictions();
    }, []);

    const fetchPredictions = async () => {
        try {
            const res = await getPredictions(0, 50);
            setPredictions(res.data);
        } catch (err) {
            console.error("Failed to fetch predictions:", err);
        }
    };

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handlePredict = async (e) => {
        e.preventDefault();
        setError("");
        setPrediction(null);

        // Validate
        if (!form.module_name.trim()) {
            setError("Module name is required.");
            return;
        }

        const payload = {
            module_name: form.module_name.trim(),
            lines_of_code: parseInt(form.lines_of_code) || 0,
            complexity_score: parseFloat(form.complexity_score) || 0,
            past_defects: parseInt(form.past_defects) || 0,
            code_churn: parseInt(form.code_churn) || 0,
        };

        if (payload.lines_of_code <= 0) {
            setError("Lines of code must be greater than 0.");
            return;
        }

        setLoading(true);
        try {
            const res = await predictDefect(payload);
            setPrediction(res.data);
            // Refresh predictions list
            fetchPredictions();
        } catch (err) {
            setError(err.response?.data?.detail || "Prediction failed. Is the backend running?");
        } finally {
            setLoading(false);
        }
    };

    // ── Chart Data ──────────────────────────────────────
    const barData = {
        labels: predictions.slice(0, 15).map((p) => p.module_name),
        datasets: [
            {
                label: "Defect Probability (%)",
                data: predictions.slice(0, 15).map((p) => (p.probability * 100).toFixed(1)),
                backgroundColor: predictions.slice(0, 15).map((p) =>
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
                ticks: { color: "#64748b", font: { size: 11 }, maxRotation: 45 },
                grid: { color: "rgba(148,163,184,0.06)" },
            },
            y: {
                ticks: { color: "#64748b" },
                grid: { color: "rgba(148,163,184,0.06)" },
                max: 100,
                title: { display: true, text: "Probability (%)", color: "#64748b" },
            },
        },
    };

    const riskClass = prediction
        ? prediction.risk_level.toLowerCase()
        : "";

    return (
        <div>
            <div className="page-header animate-in">
                <h1>Defect Prediction</h1>
                <p>Predict defect probability for modules using ML-based analysis</p>
            </div>

            <div className="section-grid two-col">
                {/* ── Prediction Form ──────────────────────────── */}
                <div className="form-section animate-in">
                    <h3><FiCpu style={{ marginRight: "0.5rem", verticalAlign: "middle" }} /> Module Metrics</h3>

                    <form onSubmit={handlePredict}>
                        <div className="form-group">
                            <label htmlFor="module_name">Module Name</label>
                            <input
                                id="module_name"
                                name="module_name"
                                type="text"
                                className="form-input"
                                placeholder="e.g., Payment, Authentication"
                                value={form.module_name}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="metrics-grid">
                            <div className="form-group">
                                <label htmlFor="lines_of_code">Lines of Code</label>
                                <input
                                    id="lines_of_code"
                                    name="lines_of_code"
                                    type="number"
                                    className="form-input"
                                    placeholder="e.g., 3500"
                                    value={form.lines_of_code}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="complexity_score">Complexity Score</label>
                                <input
                                    id="complexity_score"
                                    name="complexity_score"
                                    type="number"
                                    step="0.1"
                                    className="form-input"
                                    placeholder="e.g., 35.0"
                                    value={form.complexity_score}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="past_defects">Past Defects</label>
                                <input
                                    id="past_defects"
                                    name="past_defects"
                                    type="number"
                                    className="form-input"
                                    placeholder="e.g., 12"
                                    value={form.past_defects}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="code_churn">Code Churn</label>
                                <input
                                    id="code_churn"
                                    name="code_churn"
                                    type="number"
                                    className="form-input"
                                    placeholder="e.g., 180"
                                    value={form.code_churn}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        {error && <div className="alert alert-error">{error}</div>}

                        <button
                            type="submit"
                            className="btn-gradient"
                            disabled={loading}
                            style={{ marginTop: "0.5rem" }}
                        >
                            {loading ? (
                                <>
                                    <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></div>
                                    Predicting...
                                </>
                            ) : (
                                <>
                                    <FiActivity /> Predict Defect
                                </>
                            )}
                        </button>
                    </form>
                </div>

                {/* ── Prediction Result ────────────────────────── */}
                <div className="animate-in">
                    {prediction ? (
                        <div className={`prediction-result ${riskClass}`}>
                            <FiBarChart2 style={{ fontSize: "2rem", color: "var(--text-muted)" }} />
                            <div className="prediction-module">{prediction.module_name}</div>
                            <div className={`prediction-probability ${riskClass}`}>
                                {(prediction.defect_probability * 100).toFixed(1)}%
                            </div>
                            <div className="prediction-risk" style={{ marginBottom: "0.75rem" }}>
                                <span className={`badge badge-${riskClass}`} style={{ fontSize: "0.85rem", padding: "0.35rem 1rem" }}>
                                    {prediction.risk_level} Risk
                                </span>
                            </div>
                            <div className="prediction-category" style={{ marginBottom: "1rem" }}>
                                <span className={`badge badge-category`} style={{ fontSize: "0.82rem", padding: "0.3rem 0.9rem" }}>
                                    {prediction.defect_category || "Function Level"}
                                </span>
                            </div>
                            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                                Priority: <strong>{prediction.risk_level === "High" ? "P1" : prediction.risk_level === "Medium" ? "P2" : "P3"}</strong>
                            </p>
                        </div>
                    ) : (
                        <div className="form-section" style={{ textAlign: "center", padding: "3rem" }}>
                            <div className="empty-state">
                                <FiActivity />
                                <h4>No prediction yet</h4>
                                <p>Fill the form and click "Predict Defect" to see results</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* ── Predictions History Chart ──────────────────── */}
            <div className="chart-container animate-in" style={{ marginTop: "2rem" }}>
                <h3><FiClock style={{ marginRight: "0.5rem", verticalAlign: "middle" }} /> Prediction History</h3>
                <div style={{ height: "320px" }}>
                    {predictions.length > 0 ? (
                        <Bar data={barData} options={chartOptions} />
                    ) : (
                        <div className="empty-state">
                            <FiBarChart2 />
                            <h4>No predictions recorded</h4>
                            <p>Predictions will appear here after you run defect analysis</p>
                        </div>
                    )}
                </div>
            </div>

            {/* ── Predictions Table ──────────────────────────── */}
            {predictions.length > 0 && (
                <div className="data-table-wrapper animate-in">
                    <div className="data-table-header">
                        <h3>All Predictions ({predictions.length})</h3>
                    </div>
                    <div style={{ overflowX: "auto" }}>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Module</th>
                                    <th>Probability</th>
                                    <th>Risk Level</th>
                                    <th>Defect Category</th>
                                    <th>Priority</th>
                                    <th>Predicted At</th>
                                </tr>
                            </thead>
                            <tbody>
                                {predictions.map((p) => (
                                    <tr key={p.id}>
                                        <td style={{ fontWeight: 500 }}>{p.module_name}</td>
                                        <td>{(p.probability * 100).toFixed(1)}%</td>
                                        <td>
                                            <span className={`badge badge-${p.risk_level.toLowerCase()}`}>
                                                {p.risk_level}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="badge badge-category">
                                                {p.defect_category || "Function Level"}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge badge-${p.risk_level === "High" ? "p1" : p.risk_level === "Medium" ? "p2" : "p3"}`}>
                                                {p.risk_level === "High" ? "P1" : p.risk_level === "Medium" ? "P2" : "P3"}
                                            </span>
                                        </td>
                                        <td style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                                            {new Date(p.created_at).toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
