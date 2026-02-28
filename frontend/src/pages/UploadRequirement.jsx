/**
 * Upload Requirement Page
 * -------------------------
 * Textarea input → NLP parse → test case generation.
 * Supports Standard mode and Enterprise mode (5-phase exhaustive engine).
 * Shows parsed requirement info, generated test case table,
 * multi-layer risk analysis, coverage report, and Save to Excel button.
 */

import { useState } from "react";
import {
    FiSend, FiCpu, FiCheckCircle, FiFileText, FiAlertTriangle,
    FiSave, FiZap, FiTarget, FiLayers, FiShield,
} from "react-icons/fi";
import { generateTestCases, generateEnterprise, exportTestCasesExcel } from "../services/api";

export default function UploadRequirement() {
    const [text, setText] = useState("");
    const [designText, setDesignText] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [excelSaving, setExcelSaving] = useState(false);
    const [excelMessage, setExcelMessage] = useState("");
    const [excelFileName, setExcelFileName] = useState("TC_Export");
    const [enterpriseMode, setEnterpriseMode] = useState(false);

    const handleGenerate = async () => {
        if (text.trim().length < 5) {
            setError("Please enter a requirement with at least 5 characters.");
            return;
        }
        setError("");
        setLoading(true);
        setResult(null);
        setExcelMessage("");

        try {
            const api = enterpriseMode ? generateEnterprise : generateTestCases;
            const res = await api(text, designText || null);
            setResult({ ...res.data, _enterprise: enterpriseMode });
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to generate test cases. Is the backend running?");
        } finally {
            setLoading(false);
        }
    };

    const handleSaveExcel = async () => {
        if (!result || !result.requirement_id) return;
        if (!excelFileName.trim()) return;

        setExcelSaving(true);
        setExcelMessage("");
        try {
            const res = await exportTestCasesExcel(result.requirement_id, excelFileName);
            const blob = new Blob([res.data], {
                type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${excelFileName.replace(/\.xlsx$/, '')}.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
            setExcelMessage(`✓ Download triggered and saved to folder.`);
        } catch (err) {
            setExcelMessage(`✗ ${err.response?.data?.detail || "Failed to save Excel"}`);
        } finally {
            setExcelSaving(false);
        }
    };

    const riskBadgeClass = (level) => {
        if (level === "High") return "badge badge-high";
        if (level === "Medium") return "badge badge-medium";
        return "badge badge-low";
    };

    return (
        <div>
            <div className="page-header animate-in">
                <h1>Upload Requirement</h1>
                <p>Enter a software requirement to auto-generate comprehensive test cases</p>
            </div>

            {/* ── Input Form ─────────────────────────────────── */}
            <div className="form-section animate-in">
                <h3><FiCpu style={{ marginRight: "0.5rem", verticalAlign: "middle" }} /> Requirement Input</h3>

                {/* Enterprise Toggle */}
                <div className="enterprise-toggle-row">
                    <div className="enterprise-toggle-info">
                        <FiZap className={`toggle-icon ${enterpriseMode ? "active" : ""}`} />
                        <div>
                            <span className="toggle-label">Enterprise Mode</span>
                            <span className="toggle-desc">
                                {enterpriseMode
                                    ? "5-phase exhaustive engine • 13 scenario categories • No limit"
                                    : "Standard quick generation • 5 test types"}
                            </span>
                        </div>
                    </div>
                    <label className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={enterpriseMode}
                            onChange={(e) => setEnterpriseMode(e.target.checked)}
                        />
                        <span className="toggle-slider"></span>
                    </label>
                </div>

                <div className="form-group">
                    <label htmlFor="req-text">Requirement Description</label>
                    <textarea
                        id="req-text"
                        className="form-textarea"
                        placeholder="e.g., The system shall allow users to login using their email and password. The email must be in a valid format and the password is required with a minimum length of 8 characters."
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="design-text">Design Document (Optional)</label>
                    <textarea
                        id="design-text"
                        className="form-textarea"
                        placeholder="Paste optional design document text here for enhanced risk analysis..."
                        value={designText}
                        onChange={(e) => setDesignText(e.target.value)}
                        style={{ minHeight: "100px" }}
                    />
                </div>

                {error && <div className="alert alert-error">{error}</div>}

                <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                    <button
                        className={`btn-gradient ${enterpriseMode ? "btn-enterprise" : ""}`}
                        onClick={handleGenerate}
                        disabled={loading || text.trim().length < 5}
                    >
                        {loading ? (
                            <>
                                <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></div>
                                {enterpriseMode ? "Running 5-Phase Engine..." : "Generating..."}
                            </>
                        ) : (
                            <>
                                {enterpriseMode ? <FiZap /> : <FiSend />}
                                {enterpriseMode ? " Enterprise Generate" : " Generate Test Cases"}
                            </>
                        )}
                    </button>

                    {result && (
                        <>
                            <input
                                type="text"
                                className="form-input"
                                value={excelFileName}
                                onChange={(e) => setExcelFileName(e.target.value)}
                                style={{ width: "150px", marginBottom: 0 }}
                                placeholder="File Name"
                            />
                            <button
                                className="btn-gradient btn-excel"
                                onClick={handleSaveExcel}
                                disabled={excelSaving || !excelFileName.trim()}
                            >
                                {excelSaving ? (
                                    <>
                                        <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></div>
                                        Saving...
                                    </>
                                ) : (
                                    <><FiSave /> Save to Excel</>
                                )}
                            </button>
                        </>
                    )}
                </div>

                {excelMessage && (
                    <div className={`alert ${excelMessage.startsWith("✓") ? "alert-success" : "alert-error"}`} style={{ marginTop: "0.75rem" }}>
                        {excelMessage}
                    </div>
                )}
            </div>

            {/* ── Results ├─────────────────────────────────── */}
            {result && (
                <>
                    {/* ── Enterprise Coverage Report ───────────── */}
                    {result._enterprise && result.coverage && (
                        <div className="form-section animate-in">
                            <h3>
                                <FiTarget style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "var(--accent-mid)" }} />
                                Coverage Validation Report
                            </h3>

                            {/* Coverage Score Gauge + Stats */}
                            <div className="coverage-header-grid">
                                <div className="coverage-gauge-card">
                                    <div className="coverage-gauge">
                                        <svg viewBox="0 0 120 120" className="gauge-svg">
                                            <circle cx="60" cy="60" r="52" className="gauge-bg" />
                                            <circle
                                                cx="60" cy="60" r="52"
                                                className={`gauge-fill ${result.coverage.coverage_confidence_score >= 80 ? "gauge-high" : result.coverage.coverage_confidence_score >= 50 ? "gauge-mid" : "gauge-low"}`}
                                                strokeDasharray={`${(result.coverage.coverage_confidence_score / 100) * 327} 327`}
                                            />
                                        </svg>
                                        <div className="gauge-text">
                                            <span className="gauge-value">{result.coverage.coverage_confidence_score}</span>
                                            <span className="gauge-label">%</span>
                                        </div>
                                    </div>
                                    <div className="gauge-caption">Coverage Confidence</div>
                                </div>

                                <div className="coverage-stats-col">
                                    <div className="cov-stat">
                                        <FiLayers className="cov-stat-icon" />
                                        <div>
                                            <div className="cov-stat-val">{result.coverage.total_modules_detected}</div>
                                            <div className="cov-stat-lbl">Modules Detected</div>
                                        </div>
                                    </div>
                                    <div className="cov-stat">
                                        <FiShield className="cov-stat-icon" />
                                        <div>
                                            <div className="cov-stat-val">{result.coverage.total_scenarios_generated}</div>
                                            <div className="cov-stat-lbl">Total Test Scenarios</div>
                                        </div>
                                    </div>
                                    <div className="cov-stat">
                                        <FiTarget className="cov-stat-icon" />
                                        <div>
                                            <div className="cov-stat-val">{Object.keys(result.coverage.scenarios_by_type).length}</div>
                                            <div className="cov-stat-lbl">Scenario Categories</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Scenarios by Type */}
                            <div style={{ marginTop: "1.25rem" }}>
                                <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
                                    Scenarios by Category
                                </h4>
                                <div className="scenario-type-grid">
                                    {Object.entries(result.coverage.scenarios_by_type)
                                        .sort(([, a], [, b]) => b - a)
                                        .map(([type, count]) => (
                                            <div key={type} className="scenario-type-chip">
                                                <span className="stc-name">{type.replace(/_/g, " ")}</span>
                                                <span className="stc-count">{count}</span>
                                            </div>
                                        ))}
                                </div>
                            </div>

                            {/* Module Categories */}
                            {result.coverage.module_categories?.length > 0 && (
                                <div style={{ marginTop: "1rem" }}>
                                    <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.5rem" }}>
                                        Detected Module Categories
                                    </h4>
                                    <div className="parsed-tags">
                                        {result.coverage.module_categories.map((m, i) => (
                                            <span key={i} className="parsed-tag action">{m}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Ambiguity Warnings */}
                            {result.coverage.ambiguity_warnings?.length > 0 && (
                                <div style={{ marginTop: "1rem" }}>
                                    <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--color-warning)", marginBottom: "0.5rem" }}>
                                        <FiAlertTriangle style={{ marginRight: "0.3rem", verticalAlign: "middle" }} />
                                        Ambiguity Warnings
                                    </h4>
                                    {result.coverage.ambiguity_warnings.map((w, i) => (
                                        <div key={i} className="ambiguity-warning">{w}</div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── Decomposition Panel (Enterprise) ─────── */}
                    {result._enterprise && result.decomposition && result.decomposition.modules?.length > 0 && (
                        <div className="form-section animate-in">
                            <h3>
                                <FiLayers style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "var(--accent-mid)" }} />
                                Requirement Decomposition ({result.decomposition.total_modules} modules)
                            </h3>

                            <div className="decomp-modules-grid">
                                {result.decomposition.modules.map((mod, i) => (
                                    <div key={i} className="decomp-module-card">
                                        <div className="decomp-mod-header">
                                            <span className="decomp-mod-name">{mod.category}</span>
                                            <span className="decomp-mod-score">R: {mod.relevance_score}</span>
                                        </div>
                                        <div className="parsed-tags" style={{ marginBottom: "0.35rem" }}>
                                            {mod.matched_keywords.slice(0, 6).map((kw, j) => (
                                                <span key={j} className="parsed-tag field" style={{ fontSize: "0.68rem" }}>{kw}</span>
                                            ))}
                                            {mod.matched_keywords.length > 6 && (
                                                <span className="parsed-tag" style={{ fontSize: "0.68rem", opacity: 0.6 }}>+{mod.matched_keywords.length - 6}</span>
                                            )}
                                        </div>
                                        {mod.explicit_rules.length > 0 && (
                                            <div className="decomp-detail">
                                                <span className="dd-label">Rules:</span> {mod.explicit_rules.length}
                                            </div>
                                        )}
                                        {mod.negative_paths.length > 0 && (
                                            <div className="decomp-detail">
                                                <span className="dd-label">Negatives:</span> {mod.negative_paths.length}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ── NLP Analysis Result (always shown) ──────── */}
                    <div className="form-section animate-in">
                        <h3><FiCheckCircle style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "var(--color-success)" }} /> NLP Analysis Result</h3>

                        <div className="parsed-result">
                            <h4>Module: {result.parsed.module}</h4>

                            <div style={{ marginBottom: "0.5rem" }}>
                                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>ACTIONS:</span>
                                <div className="parsed-tags">
                                    {result.parsed.actions.map((a, i) => (
                                        <span key={i} className="parsed-tag action">{a}</span>
                                    ))}
                                </div>
                            </div>

                            <div style={{ marginBottom: "0.5rem" }}>
                                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>FIELDS:</span>
                                <div className="parsed-tags">
                                    {result.parsed.fields.map((f, i) => (
                                        <span key={i} className="parsed-tag field">{f}</span>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>VALIDATIONS:</span>
                                <div className="parsed-tags">
                                    {result.parsed.validations.map((v, i) => (
                                        <span key={i} className="parsed-tag validation">{v}</span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {result.folder_path && (
                            <div className="alert alert-info" style={{ marginTop: "1rem" }}>
                                <FiFileText /> Saved to folder: <code style={{ fontSize: "0.8rem", opacity: 0.9 }}>{result.folder_path}</code>
                            </div>
                        )}
                    </div>

                    {/* ── Multi-Layer Risk Analysis ──────────────────── */}
                    {result.risk_analysis && (
                        <div className="form-section animate-in">
                            <h3><FiAlertTriangle style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "var(--color-warning)" }} /> Multi-Layer Risk Analysis</h3>

                            <div className="risk-summary" style={{ marginBottom: "1.25rem" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.5rem" }}>
                                    <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Overall Risk:</span>
                                    <span className={riskBadgeClass(result.risk_analysis.overall_risk_level)} style={{ fontSize: "0.85rem", padding: "0.3rem 0.9rem" }}>
                                        {result.risk_analysis.overall_risk_level} ({(result.risk_analysis.overall_score * 100).toFixed(0)}%)
                                    </span>
                                </div>
                                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: 0 }}>{result.risk_analysis.summary}</p>
                            </div>

                            <div className="risk-layers-grid">
                                {Object.entries(result.risk_analysis.layers).map(([layer, data]) => (
                                    <div key={layer} className="risk-layer-card">
                                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                                            <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>{layer}</span>
                                            <span className={riskBadgeClass(data.risk_level)}>
                                                {data.risk_level}
                                            </span>
                                        </div>
                                        <div className="risk-bar-track">
                                            <div
                                                className={`risk-bar-fill risk-bar-${data.risk_level.toLowerCase()}`}
                                                style={{ width: `${Math.min(data.score * 100, 100)}%` }}
                                            />
                                        </div>
                                        {data.found_signals.length > 0 && (
                                            <div className="risk-signals">
                                                {data.found_signals.slice(0, 5).map((s, i) => (
                                                    <span key={i} className="risk-signal-tag">{s}</span>
                                                ))}
                                                {data.found_signals.length > 5 && (
                                                    <span className="risk-signal-tag" style={{ opacity: 0.6 }}>+{data.found_signals.length - 5} more</span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ── Generated Test Cases Table ────────────────── */}
                    <div className="data-table-wrapper animate-in">
                        <div className="data-table-header">
                            <h3>Generated Test Cases ({result.test_cases.length})</h3>
                            <span className="badge badge-positive">Requirement #{result.requirement_id}</span>
                        </div>
                        <div style={{ overflowX: "auto" }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Module</th>
                                        <th>Scenario</th>
                                        <th>Type</th>
                                        <th>Level</th>
                                        <th>Expected Result</th>
                                        <th>Priority</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {result.test_cases.map((tc, idx) => (
                                        <tr key={tc.test_id}>
                                            <td>{idx + 1}</td>
                                            <td>{tc.module_name}</td>
                                            <td>{tc.scenario}</td>
                                            <td>
                                                <span className={`badge badge-${tc.test_type}`}>
                                                    {tc.test_type.replace(/_/g, " ")}
                                                </span>
                                            </td>
                                            <td>
                                                <span className={`badge badge-level-${(tc.test_level || 'unit').toLowerCase()}`}>
                                                    {tc.test_level || 'Unit'}
                                                </span>
                                            </td>
                                            <td>{tc.expected_result}</td>
                                            <td>
                                                <span className={`badge badge-${tc.priority.toLowerCase()}`}>
                                                    {tc.priority}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
