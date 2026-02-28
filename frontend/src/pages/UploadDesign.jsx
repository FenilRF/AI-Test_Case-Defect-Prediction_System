/**
 * Upload Design Page
 * -------------------------
 * Upload design documentation (files, images, URLs)
 * associated with a requirement.
 *
 * Supports: PDF, DOCX, PPTX, TXT (documents)
 *           PNG, JPG (images)
 *           URLs (Figma, design links)
 */

import { useState, useRef, useEffect } from "react";
import useSessionState from "../hooks/useSessionState";
import {
    FiUploadCloud, FiFile, FiImage, FiLink, FiX, FiCheckCircle,
    FiAlertTriangle, FiCpu, FiLayers, FiGrid,
} from "react-icons/fi";
import { uploadDesign, getRequirements } from "../services/api";

const ALLOWED_DOC_TYPES = ".pdf,.docx,.pptx,.txt";
const ALLOWED_IMAGE_TYPES = ".png,.jpg,.jpeg";

export default function UploadDesign() {
    const [files, setFiles] = useState([]);
    const [images, setImages] = useState([]);
    const [urlInput, setUrlInput] = useState("");
    const [urls, setUrls] = useState([]);
    const [requirementId, setRequirementId] = useState("");
    const [requirements, setRequirements] = useState([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useSessionState("upload_design_result", null);
    const [error, setError] = useState("");

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

    // ── Upload handler ───────────────────────────────────
    const handleUpload = async () => {
        if (files.length === 0 && images.length === 0 && urls.length === 0) {
            setError("At least one input is required: file, image, or URL.");
            return;
        }

        setError("");
        setLoading(true);
        setResult(null);

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
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Failed to upload design. Is the backend running?"
            );
        } finally {
            setLoading(false);
        }
    };

    // ── Helpers ───────────────────────────────────────────
    const hasInput = files.length > 0 || images.length > 0 || urls.length > 0;

    const classificationBarWidth = (score, total) => {
        if (total === 0) return 0;
        return Math.round((score / total) * 100);
    };

    return (
        <div>
            <div className="page-header animate-in">
                <h1>Upload Design</h1>
                <p>Upload design documentation to enhance test generation and defect prediction</p>
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
                    <div
                        className="upload-zone"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept={ALLOWED_DOC_TYPES}
                            onChange={handleFileSelect}
                            style={{ display: "none" }}
                        />
                        <div className="upload-zone-icon doc-icon">
                            <FiFile />
                        </div>
                        <h4>Documents</h4>
                        <p>PDF, DOCX, PPTX, TXT</p>
                        <span className="upload-zone-hint">Click to browse</span>
                    </div>

                    {/* Image Upload Zone */}
                    <div
                        className="upload-zone"
                        onClick={() => imageInputRef.current?.click()}
                    >
                        <input
                            ref={imageInputRef}
                            type="file"
                            multiple
                            accept={ALLOWED_IMAGE_TYPES}
                            onChange={handleImageSelect}
                            style={{ display: "none" }}
                        />
                        <div className="upload-zone-icon img-icon">
                            <FiImage />
                        </div>
                        <h4>Images</h4>
                        <p>PNG, JPG</p>
                        <span className="upload-zone-hint">Click to browse</span>
                    </div>

                    {/* URL Input Zone */}
                    <div className="upload-zone url-zone" onClick={(e) => e.stopPropagation()}>
                        <div className="upload-zone-icon url-icon">
                            <FiLink />
                        </div>
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
                            Uploading & Analysing...
                        </>
                    ) : (
                        <>
                            <FiUploadCloud /> Upload & Analyse Design
                        </>
                    )}
                </button>
            </div>

            {/* ── Results ──────────────────────────────────── */}
            {result && (
                <>
                    {/* Success Notification */}
                    <div className="alert alert-success animate-in" style={{ marginBottom: "1.5rem" }}>
                        <FiCheckCircle /> {result.message}
                    </div>

                    {/* Analysis Summary */}
                    <div className="form-section animate-in">
                        <h3>
                            <FiCpu style={{ marginRight: "0.5rem", verticalAlign: "middle", color: "var(--accent-mid)" }} />
                            Design Analysis Result
                        </h3>

                        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1.25rem" }}>
                            {result.analysis.summary}
                        </p>

                        {/* Classification + Summary Cards */}
                        <div className="design-stats-grid">
                            <div className="design-stat-card">
                                <div className="design-stat-icon" style={{ background: "rgba(139, 92, 246, 0.12)", color: "var(--accent-mid)" }}>
                                    <FiLayers />
                                </div>
                                <div>
                                    <div className="design-stat-value">{result.analysis.module_count}</div>
                                    <div className="design-stat-label">Modules</div>
                                </div>
                            </div>
                            <div className="design-stat-card">
                                <div className="design-stat-icon" style={{ background: "rgba(59, 130, 246, 0.12)", color: "var(--color-info)" }}>
                                    <FiGrid />
                                </div>
                                <div>
                                    <div className="design-stat-value">{result.analysis.integration_count}</div>
                                    <div className="design-stat-label">Integrations</div>
                                </div>
                            </div>
                            <div className="design-stat-card">
                                <div className="design-stat-icon" style={{
                                    background: result.analysis.classification.primary_type === "UI-Focused"
                                        ? "rgba(34, 197, 94, 0.12)"
                                        : result.analysis.classification.primary_type === "API-Focused"
                                            ? "rgba(245, 158, 11, 0.12)"
                                            : "rgba(239, 68, 68, 0.12)",
                                    color: result.analysis.classification.primary_type === "UI-Focused"
                                        ? "var(--color-success)"
                                        : result.analysis.classification.primary_type === "API-Focused"
                                            ? "var(--color-warning)"
                                            : "var(--color-danger)",
                                }}>
                                    <FiCpu />
                                </div>
                                <div>
                                    <div className="design-stat-value" style={{ fontSize: "1rem" }}>
                                        {result.analysis.classification.primary_type}
                                    </div>
                                    <div className="design-stat-label">Classification</div>
                                </div>
                            </div>
                        </div>

                        {/* Classification Breakdown */}
                        {(() => {
                            const { ui_score, api_score, system_score } = result.analysis.classification;
                            const total = ui_score + api_score + system_score || 1;
                            return (
                                <div className="classification-breakdown">
                                    <h4 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.75rem", color: "var(--text-secondary)" }}>
                                        Classification Breakdown
                                    </h4>
                                    <div className="class-bar-row">
                                        <span className="class-bar-label">UI</span>
                                        <div className="class-bar-track">
                                            <div className="class-bar-fill class-bar-ui" style={{ width: `${classificationBarWidth(ui_score, total)}%` }} />
                                        </div>
                                        <span className="class-bar-score">{ui_score}</span>
                                    </div>
                                    <div className="class-bar-row">
                                        <span className="class-bar-label">API</span>
                                        <div className="class-bar-track">
                                            <div className="class-bar-fill class-bar-api" style={{ width: `${classificationBarWidth(api_score, total)}%` }} />
                                        </div>
                                        <span className="class-bar-score">{api_score}</span>
                                    </div>
                                    <div className="class-bar-row">
                                        <span className="class-bar-label">System</span>
                                        <div className="class-bar-track">
                                            <div className="class-bar-fill class-bar-system" style={{ width: `${classificationBarWidth(system_score, total)}%` }} />
                                        </div>
                                        <span className="class-bar-score">{system_score}</span>
                                    </div>
                                </div>
                            );
                        })()}

                        {/* Extracted Modules */}
                        {result.analysis.modules.length > 0 && (
                            <div style={{ marginTop: "1.25rem" }}>
                                <h4 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.5rem", color: "var(--text-secondary)" }}>
                                    Identified Modules
                                </h4>
                                <div className="parsed-tags">
                                    {result.analysis.modules.map((m, i) => (
                                        <span key={i} className="parsed-tag">{m}</span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Integrations */}
                        {result.analysis.integrations.length > 0 && (
                            <div style={{ marginTop: "0.75rem" }}>
                                <h4 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.5rem", color: "var(--text-secondary)" }}>
                                    Integration Points
                                </h4>
                                <div className="parsed-tags">
                                    {result.analysis.integrations.map((ig, i) => (
                                        <span key={i} className="parsed-tag action">{ig}</span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Folder path */}
                        {result.folder_path && (
                            <div className="alert alert-info" style={{ marginTop: "1rem" }}>
                                <FiFile /> Stored at: <code style={{ fontSize: "0.8rem", opacity: 0.9 }}>{result.folder_path}</code>
                            </div>
                        )}
                    </div>

                    {/* ── Generated Test Cases Table ────────────────── */}
                    {result.test_cases && result.test_cases.length > 0 && (
                        <div className="data-table-wrapper animate-in">
                            <div className="data-table-header">
                                <h3>Generated Test Cases ({result.test_cases.length})</h3>
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
                                                        {tc.test_type}
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
                    )}
                </>
            )}
        </div>
    );
}
