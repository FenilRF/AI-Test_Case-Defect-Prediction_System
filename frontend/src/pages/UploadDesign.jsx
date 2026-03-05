/**
 * Upload Design Page — Enterprise Intelligence Engine
 * -------------------------------------------------------
 * Upload design documentation (files, images, URLs)
 * and receive enterprise-grade UI analysis + test cases.
 *
 * Features:
 *   • Multi-step progress stepper during analysis
 *   • Enterprise stats dashboard (pages, components, flows, coverage)
 *   • UI Schema viewer with collapsible modules
 *   • Detected flows display (primary, alternate, cross-flow)
 *   • Full enterprise test cases table with filtering
 *   • Coverage breakdown visualization
 */

import { useState, useRef, useEffect } from "react";
import {
    FiUploadCloud, FiFile, FiImage, FiLink, FiX, FiCheckCircle,
    FiAlertTriangle, FiCpu, FiLayers, FiGrid, FiActivity,
    FiTarget, FiShield, FiZap, FiEye, FiChevronDown, FiChevronRight,
    FiFilter, FiList, FiCompass,
} from "react-icons/fi";
import { uploadDesign, getRequirements } from "../services/api";

const ALLOWED_DOC_TYPES = ".pdf,.docx,.pptx,.txt";
const ALLOWED_IMAGE_TYPES = ".png,.jpg,.jpeg";

/* ── Analysis progress stages ─────────────────────────── */
const STAGES = [
    { key: "upload", label: "Uploading", icon: <FiUploadCloud /> },
    { key: "extract", label: "Extracting", icon: <FiFile /> },
    { key: "vision", label: "Analyzing (Vision AI)", icon: <FiEye /> },
    { key: "schema", label: "Building Schema", icon: <FiLayers /> },
    { key: "generate", label: "Generating Tests", icon: <FiZap /> },
    { key: "validate", label: "Quality Filter", icon: <FiShield /> },
];

export default function UploadDesign() {
    const [files, setFiles] = useState([]);
    const [images, setImages] = useState([]);
    const [urlInput, setUrlInput] = useState("");
    const [urls, setUrls] = useState([]);
    const [requirementId, setRequirementId] = useState("");
    const [requirements, setRequirements] = useState([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [currentStage, setCurrentStage] = useState(0);

    /* ── Filter state for test cases table ──────────────── */
    const [filterModule, setFilterModule] = useState("");
    const [filterType, setFilterType] = useState("");
    const [filterPriority, setFilterPriority] = useState("");
    const [filterLevel, setFilterLevel] = useState("");
    const [expandedRows, setExpandedRows] = useState(new Set());
    const [expandedModules, setExpandedModules] = useState(new Set());

    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);

    // Fetch requirements for the dropdown
    useEffect(() => {
        (async () => {
            try {
                const res = await getRequirements();
                setRequirements(res.data);
            } catch (e) {
                console.error("Failed to fetch requirements:", e);
            }
        })();
    }, []);

    // ── File handlers ────────────────────────────────────
    const handleFileSelect = (e) => {
        const selected = Array.from(e.target.files);
        setFiles((prev) => [...prev, ...selected]);
        e.target.value = "";
    };

    const handleImageSelect = (e) => {
        const selected = Array.from(e.target.files);
        setImages((prev) => [...prev, ...selected]);
        e.target.value = "";
    };

    const removeFile = (idx) => setFiles((prev) => prev.filter((_, i) => i !== idx));
    const removeImage = (idx) => setImages((prev) => prev.filter((_, i) => i !== idx));

    // ── URL handlers ─────────────────────────────────────
    const addUrl = () => {
        const trimmed = urlInput.trim();
        if (trimmed && !urls.includes(trimmed)) {
            setUrls((prev) => [...prev, trimmed]);
            setUrlInput("");
        }
    };
    const removeUrl = (idx) => setUrls((prev) => prev.filter((_, i) => i !== idx));
    const handleUrlKeyDown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            addUrl();
        }
    };

    // ── Progress simulation ──────────────────────────────
    const simulateProgress = () => {
        const timings = [0, 2000, 5000, 10000, 18000, 28000];
        timings.forEach((ms, idx) => {
            setTimeout(() => setCurrentStage(idx), ms);
        });
    };

    // ── Upload handler ───────────────────────────────────
    const handleUpload = async () => {
        if (files.length === 0 && images.length === 0 && urls.length === 0) {
            setError("At least one input is required: file, image, or URL.");
            return;
        }

        setError("");
        setLoading(true);
        setResult(null);
        setCurrentStage(0);
        simulateProgress();

        try {
            const formData = new FormData();
            formData.append("design_text", "");

            if (urls.length > 0) {
                formData.append("design_url", urls[0]);
            }

            if (files.length > 0) {
                formData.append("file", files[0]);
            } else if (images.length > 0) {
                formData.append("file", images[0]);
            }

            if (requirementId) {
                formData.append("requirement_id", requirementId);
            }

            const res = await uploadDesign(formData);
            setResult(res.data);
            setCurrentStage(STAGES.length - 1);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Failed to upload design. Check if the backend is running and GROQ_API_KEY is configured."
            );
        } finally {
            setLoading(false);
        }
    };

    // ── Helpers ───────────────────────────────────────────
    const hasInput = files.length > 0 || images.length > 0 || urls.length > 0;

    const toggleRowExpand = (id) => {
        setExpandedRows((prev) => {
            const n = new Set(prev);
            n.has(id) ? n.delete(id) : n.add(id);
            return n;
        });
    };

    const toggleModuleExpand = (name) => {
        setExpandedModules((prev) => {
            const n = new Set(prev);
            n.has(name) ? n.delete(name) : n.add(name);
            return n;
        });
    };

    const getFilteredTestCases = () => {
        if (!result?.test_cases) return [];
        return result.test_cases.filter((tc) => {
            if (filterModule && tc.module !== filterModule) return false;
            if (filterType && tc.type !== filterType) return false;
            if (filterPriority && tc.priority !== filterPriority) return false;
            if (filterLevel && tc.level !== filterLevel) return false;
            return true;
        });
    };

    const uniqueValues = (arr, key) => [...new Set((arr || []).map((i) => i[key]).filter(Boolean))].sort();

    const getPriorityColor = (p) => {
        if (p === "P1") return "#ef4444";
        if (p === "P2") return "#f59e0b";
        return "#22c55e";
    };

    const getComplexityBar = (score) => {
        const pct = Math.max(0, Math.min(100, (score / 5) * 100));
        const color = score >= 4 ? "#ef4444" : score >= 3 ? "#f59e0b" : "#22c55e";
        return (
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <div style={{
                    width: "50px", height: "6px", borderRadius: "3px",
                    background: "rgba(255,255,255,0.08)",
                }}>
                    <div style={{
                        width: `${pct}%`, height: "100%", borderRadius: "3px",
                        background: color, transition: "width 0.3s ease",
                    }} />
                </div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{score}/5</span>
            </div>
        );
    };

    return (
        <div>
            <div className="page-header animate-in">
                <h1>Upload Design</h1>
                <p>Enterprise-grade UI intelligence engine — analyze designs and generate comprehensive test cases</p>
            </div>

            {/* ── Upload Form ──────────────────────────────── */}
            <div className="form-section animate-in">
                <h3>
                    <FiUploadCloud style={{ marginRight: "0.5rem", verticalAlign: "middle" }} />
                    Design Documentation Input
                </h3>

                {/* Requirement association */}
                <div className="form-group">
                    <label htmlFor="design-req-id">Associate with Requirement (Optional)</label>
                    <select
                        id="design-req-id"
                        className="form-input"
                        value={requirementId}
                        onChange={(e) => setRequirementId(e.target.value)}
                    >
                        <option value="">— None (standalone upload) —</option>
                        {requirements.map((r) => (
                            <option key={r.id} value={r.id}>
                                #{r.id} — {r.text.substring(0, 80)}{r.text.length > 80 ? "…" : ""}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Upload zones grid */}
                <div className="design-upload-grid">
                    {/* Document Upload Zone */}
                    <div className="upload-zone" onClick={() => fileInputRef.current?.click()}>
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept={ALLOWED_DOC_TYPES}
                            onChange={handleFileSelect}
                            style={{ display: "none" }}
                        />
                        <div className="upload-zone-icon doc-icon"><FiFile /></div>
                        <h4>Documents</h4>
                        <p>PDF, DOCX, PPTX, TXT</p>
                        <span className="upload-zone-hint">Click to browse</span>
                    </div>

                    {/* Image Upload Zone */}
                    <div className="upload-zone" onClick={() => imageInputRef.current?.click()}>
                        <input
                            ref={imageInputRef}
                            type="file"
                            multiple
                            accept={ALLOWED_IMAGE_TYPES}
                            onChange={handleImageSelect}
                            style={{ display: "none" }}
                        />
                        <div className="upload-zone-icon img-icon"><FiImage /></div>
                        <h4>Images</h4>
                        <p>PNG, JPG</p>
                        <span className="upload-zone-hint">Click to browse</span>
                    </div>

                    {/* URL Input Zone */}
                    <div className="upload-zone url-zone" onClick={(e) => e.stopPropagation()}>
                        <div className="upload-zone-icon url-icon"><FiLink /></div>
                        <h4>Design URLs</h4>
                        <p>Figma, Zeplin, etc.</p>
                        <div className="url-input-group" onClick={(e) => e.stopPropagation()}>
                            <input
                                type="url"
                                className="form-input"
                                placeholder="https://figma.com/..."
                                value={urlInput}
                                onChange={(e) => setUrlInput(e.target.value)}
                                onKeyDown={handleUrlKeyDown}
                                style={{ fontSize: "0.8rem", padding: "0.45rem 0.65rem" }}
                            />
                            <button
                                className="btn-outline"
                                onClick={addUrl}
                                disabled={!urlInput.trim()}
                                style={{ fontSize: "0.75rem", padding: "0.4rem 0.7rem" }}
                            >
                                Add
                            </button>
                        </div>
                    </div>
                </div>

                {/* Selected files display */}
                {(files.length > 0 || images.length > 0 || urls.length > 0) && (
                    <div className="selected-items-section">
                        {files.length > 0 && (
                            <div className="selected-group">
                                <span className="selected-label"><FiFile /> Documents ({files.length})</span>
                                <div className="selected-tags">
                                    {files.map((f, i) => (
                                        <span key={`file-${i}`} className="selected-tag doc-tag">
                                            {f.name}
                                            <button className="tag-remove" onClick={() => removeFile(i)}><FiX /></button>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {images.length > 0 && (
                            <div className="selected-group">
                                <span className="selected-label"><FiImage /> Images ({images.length})</span>
                                <div className="selected-tags">
                                    {images.map((img, i) => (
                                        <span key={`img-${i}`} className="selected-tag img-tag">
                                            {img.name}
                                            <button className="tag-remove" onClick={() => removeImage(i)}><FiX /></button>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {urls.length > 0 && (
                            <div className="selected-group">
                                <span className="selected-label"><FiLink /> URLs ({urls.length})</span>
                                <div className="selected-tags">
                                    {urls.map((u, i) => (
                                        <span key={`url-${i}`} className="selected-tag url-tag">
                                            {u.length > 50 ? u.substring(0, 50) + "…" : u}
                                            <button className="tag-remove" onClick={() => removeUrl(i)}><FiX /></button>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {error && <div className="alert alert-error"><FiAlertTriangle />{error}</div>}

                <button
                    className="btn-gradient"
                    onClick={handleUpload}
                    disabled={loading || !hasInput}
                    style={{ marginTop: "1rem" }}
                >
                    {loading ? (
                        <>
                            <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></div>
                            Analyzing Design…
                        </>
                    ) : (
                        <>
                            <FiZap /> Upload & Analyze (Enterprise)
                        </>
                    )}
                </button>
            </div>

            {/* ── Progress Stepper ─────────────────────────── */}
            {loading && (
                <div className="enterprise-stepper animate-in">
                    {STAGES.map((stage, idx) => (
                        <div
                            key={stage.key}
                            className={`stepper-step ${idx < currentStage ? "step-done" : ""} ${idx === currentStage ? "step-active" : ""} ${idx > currentStage ? "step-pending" : ""}`}
                        >
                            <div className="stepper-icon">
                                {idx < currentStage ? <FiCheckCircle /> : stage.icon}
                            </div>
                            <span className="stepper-label">{stage.label}</span>
                            {idx < STAGES.length - 1 && <div className="stepper-line" />}
                        </div>
                    ))}
                </div>
            )}

            {/* ══════════════════════════════════════════════ */}
            {/* RESULTS SECTION                               */}
            {/* ══════════════════════════════════════════════ */}
            {result && (
                <>
                    {/* Success banner */}
                    <div className="alert alert-success animate-in" style={{ marginBottom: "1.5rem" }}>
                        <FiCheckCircle /> {result.message}
                    </div>

                    {/* ── Enterprise Stats Dashboard ───────────── */}
                    <div className="form-section animate-in">
                        <h3>
                            <FiActivity style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "var(--accent-mid)" }} />
                            Enterprise Analysis Dashboard
                        </h3>
                        <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", marginBottom: "1.25rem" }}>
                            {result.analysis_summary}
                        </p>

                        <div className="enterprise-stats-grid">
                            <div className="enterprise-stat-card stat-pages">
                                <div className="enterprise-stat-icon"><FiFile /></div>
                                <div className="enterprise-stat-value">{result.total_pages_analyzed || 0}</div>
                                <div className="enterprise-stat-label">Pages Analyzed</div>
                            </div>
                            <div className="enterprise-stat-card stat-components">
                                <div className="enterprise-stat-icon"><FiGrid /></div>
                                <div className="enterprise-stat-value">{result.total_ui_components_detected || 0}</div>
                                <div className="enterprise-stat-label">UI Components</div>
                            </div>
                            <div className="enterprise-stat-card stat-flows">
                                <div className="enterprise-stat-icon"><FiCompass /></div>
                                <div className="enterprise-stat-value">{result.total_flows_detected || 0}</div>
                                <div className="enterprise-stat-label">Flows Detected</div>
                            </div>
                            <div className="enterprise-stat-card stat-tests">
                                <div className="enterprise-stat-icon"><FiTarget /></div>
                                <div className="enterprise-stat-value">{result.total_test_cases_generated || 0}</div>
                                <div className="enterprise-stat-label">Test Cases</div>
                            </div>
                            <div className="enterprise-stat-card stat-coverage">
                                <div className="enterprise-stat-icon"><FiShield /></div>
                                <div className="enterprise-stat-value">
                                    {(result.enterprise_coverage_percentage || 0).toFixed(1)}%
                                </div>
                                <div className="enterprise-stat-label">Coverage</div>
                            </div>
                        </div>

                        {/* Coverage breakdown bars */}
                        {result.coverage && result.coverage.type_distribution && (
                            <div className="coverage-breakdown" style={{ marginTop: "1.5rem" }}>
                                <h4 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.75rem", color: "var(--text-secondary)" }}>
                                    Test Type Distribution
                                </h4>
                                <div className="coverage-type-grid">
                                    {Object.entries(result.coverage.type_distribution).map(([type, count]) => (
                                        <div key={type} className="coverage-type-item">
                                            <span className="coverage-type-name">{type.replace(/_/g, " ")}</span>
                                            <span className="coverage-type-count">{count}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ── UI Schema Viewer ─────────────────────── */}
                    {result.ui_schema && result.ui_schema.modules && result.ui_schema.modules.length > 0 && (
                        <div className="form-section animate-in">
                            <h3>
                                <FiLayers style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "#a78bfa" }} />
                                UI Schema ({result.ui_schema.total_modules || 0} Modules)
                            </h3>
                            <div className="ui-schema-tree">
                                {result.ui_schema.modules.map((mod, midx) => (
                                    <div key={midx} className="schema-module">
                                        <div
                                            className="schema-module-header"
                                            onClick={() => toggleModuleExpand(mod.module_name)}
                                        >
                                            {expandedModules.has(mod.module_name)
                                                ? <FiChevronDown />
                                                : <FiChevronRight />}
                                            <span className="schema-module-name">{mod.module_name}</span>
                                            <span className="schema-module-count">
                                                {(mod.ui_components || []).length} components
                                            </span>
                                        </div>
                                        {expandedModules.has(mod.module_name) && (
                                            <div className="schema-module-body">
                                                {mod.validations_detected && mod.validations_detected.length > 0 && (
                                                    <div className="schema-validations">
                                                        <strong>Validations:</strong>
                                                        <div className="parsed-tags" style={{ marginTop: "0.4rem" }}>
                                                            {mod.validations_detected.map((v, vi) => (
                                                                <span key={vi} className="parsed-tag">{v}</span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                                {mod.ui_components && mod.ui_components.length > 0 && (
                                                    <div className="schema-components-list">
                                                        {mod.ui_components.slice(0, 30).map((comp, ci) => (
                                                            <div key={ci} className="schema-component-item">
                                                                <span className={`badge badge-${(comp.type || "unknown").toLowerCase()}`}>
                                                                    {comp.type || "unknown"}
                                                                </span>
                                                                <span>{comp.label || comp.text || "—"}</span>
                                                            </div>
                                                        ))}
                                                        {mod.ui_components.length > 30 && (
                                                            <div className="schema-more">
                                                                +{mod.ui_components.length - 30} more components
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ── Detected Flows ───────────────────────── */}
                    {result.detected_flows && (result.detected_flows.primary_flows?.length > 0 || result.detected_flows.alternate_flows?.length > 0) && (
                        <div className="form-section animate-in">
                            <h3>
                                <FiCompass style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "#06b6d4" }} />
                                Detected Flows ({result.detected_flows.total_flows || 0})
                            </h3>

                            {result.detected_flows.primary_flows?.length > 0 && (
                                <div style={{ marginBottom: "1rem" }}>
                                    <h4 className="flow-section-title">Primary Flows</h4>
                                    <div className="flows-grid">
                                        {result.detected_flows.primary_flows.map((flow, fi) => (
                                            <div key={fi} className="flow-card flow-primary">
                                                <div className="flow-card-header">{flow.name}</div>
                                                <div className="flow-card-type">{flow.type}</div>
                                                <div className="flow-steps">
                                                    {(flow.steps || []).map((step, si) => (
                                                        <div key={si} className="flow-step">
                                                            <span className="flow-step-num">{si + 1}</span>
                                                            {step}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {result.detected_flows.alternate_flows?.length > 0 && (
                                <div style={{ marginBottom: "1rem" }}>
                                    <h4 className="flow-section-title">Alternate Flows</h4>
                                    <div className="parsed-tags">
                                        {result.detected_flows.alternate_flows.map((af, ai) => (
                                            <span key={ai} className="parsed-tag action" title={af.description}>
                                                {af.name}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {result.detected_flows.cross_flows?.length > 0 && (
                                <div>
                                    <h4 className="flow-section-title">Cross-Flow Scenarios</h4>
                                    <div className="parsed-tags">
                                        {result.detected_flows.cross_flows.map((cf, ci) => (
                                            <span key={ci} className="parsed-tag">
                                                {cf.name}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── Enterprise Test Cases Table ──────────── */}
                    {result.test_cases && result.test_cases.length > 0 && (
                        <div className="data-table-wrapper animate-in">
                            <div className="data-table-header">
                                <h3>
                                    <FiTarget style={{ marginRight: "0.5rem", verticalAlign: "middle" }} />
                                    Enterprise Test Cases ({result.test_cases.length})
                                </h3>
                            </div>

                            {/* Filters */}
                            <div className="enterprise-filters">
                                <div className="filter-item">
                                    <FiFilter size={14} />
                                    <select value={filterModule} onChange={(e) => setFilterModule(e.target.value)}>
                                        <option value="">All Modules</option>
                                        {uniqueValues(result.test_cases, "module").map((m) => (
                                            <option key={m} value={m}>{m}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="filter-item">
                                    <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                                        <option value="">All Types</option>
                                        {uniqueValues(result.test_cases, "type").map((t) => (
                                            <option key={t} value={t}>{t}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="filter-item">
                                    <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
                                        <option value="">All Priorities</option>
                                        <option value="P1">P1</option>
                                        <option value="P2">P2</option>
                                        <option value="P3">P3</option>
                                    </select>
                                </div>
                                <div className="filter-item">
                                    <select value={filterLevel} onChange={(e) => setFilterLevel(e.target.value)}>
                                        <option value="">All Levels</option>
                                        {uniqueValues(result.test_cases, "level").map((l) => (
                                            <option key={l} value={l}>{l}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Table */}
                            <div style={{ overflowX: "auto" }}>
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th style={{ width: "30px" }}></th>
                                            <th>ID</th>
                                            <th>Module</th>
                                            <th>Scenario</th>
                                            <th>Type</th>
                                            <th>Level</th>
                                            <th>Priority</th>
                                            <th>Complexity</th>
                                            <th>Tag</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {getFilteredTestCases().map((tc) => (
                                            <>
                                                <tr key={tc.id} onClick={() => toggleRowExpand(tc.id)} style={{ cursor: "pointer" }}>
                                                    <td>
                                                        {expandedRows.has(tc.id)
                                                            ? <FiChevronDown size={14} />
                                                            : <FiChevronRight size={14} />}
                                                    </td>
                                                    <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{tc.id}</td>
                                                    <td>{tc.module}</td>
                                                    <td style={{ maxWidth: "320px" }}>
                                                        {tc.scenario?.length > 100
                                                            ? tc.scenario.substring(0, 100) + "…"
                                                            : tc.scenario}
                                                    </td>
                                                    <td>
                                                        <span className={`badge badge-${(tc.type || "").toLowerCase().replace(/_/g, "-")}`}>
                                                            {tc.type}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span className={`badge badge-level-${(tc.level || "ui").toLowerCase()}`}>
                                                            {tc.level}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span className="badge" style={{
                                                            background: `${getPriorityColor(tc.priority)}22`,
                                                            color: getPriorityColor(tc.priority),
                                                            border: `1px solid ${getPriorityColor(tc.priority)}44`,
                                                        }}>
                                                            {tc.priority}
                                                        </span>
                                                    </td>
                                                    <td>{getComplexityBar(tc.complexity_score || 2)}</td>
                                                    <td>
                                                        {tc.coverage_tag && (
                                                            <span className="parsed-tag" style={{ fontSize: "0.7rem", padding: "0.15rem 0.45rem" }}>
                                                                {tc.coverage_tag}
                                                            </span>
                                                        )}
                                                    </td>
                                                </tr>
                                                {expandedRows.has(tc.id) && (
                                                    <tr key={`${tc.id}-detail`} className="expanded-row">
                                                        <td colSpan={9}>
                                                            <div className="tc-detail-grid">
                                                                <div className="tc-detail-item">
                                                                    <strong>Precondition:</strong>
                                                                    <span>{tc.precondition || "—"}</span>
                                                                </div>
                                                                <div className="tc-detail-item">
                                                                    <strong>Expected Result:</strong>
                                                                    <span>{tc.expected_result || "—"}</span>
                                                                </div>
                                                                {tc.test_steps && tc.test_steps.length > 0 && (
                                                                    <div className="tc-detail-item tc-detail-steps">
                                                                        <strong>Test Steps:</strong>
                                                                        <ol>
                                                                            {tc.test_steps.map((step, si) => (
                                                                                <li key={si}>{step}</li>
                                                                            ))}
                                                                        </ol>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                )}
                                            </>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {getFilteredTestCases().length === 0 && (
                                <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                                    No test cases match the current filters.
                                </div>
                            )}
                        </div>
                    )}

                    {/* Folder path */}
                    {result.folder_path && (
                        <div className="alert alert-info animate-in" style={{ marginTop: "1rem" }}>
                            <FiFile /> Stored at: <code style={{ fontSize: "0.8rem", opacity: 0.9 }}>{result.folder_path}</code>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
