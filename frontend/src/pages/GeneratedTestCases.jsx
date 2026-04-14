/**
 * Generated Test Cases Page
 * ----------------------------
 * Lists all stored test cases with filtering by type/level,
 * search, CSV/JSON/Excel export, checkbox selection,
 * Delete Selected, Clear All, and confirmation modals.
 */

import React, { useState, useEffect, useRef } from "react";
import { FiDownload, FiFilter, FiList, FiSearch, FiFileText, FiTrash2, FiXCircle, FiAlertTriangle, FiLayers, FiChevronDown, FiChevronRight } from "react-icons/fi";
import {
    getTestCases,
    exportTestCasesCSV,
    exportTestCasesJSON,
    exportTestCasesExcel,
    deleteTestCase,
    deleteSelectedTestCases,
    clearAllTestCases,
    clearModuleTestCases,
} from "../services/api";

export default function GeneratedTestCases() {
    const [testCases, setTestCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filterType, setFilterType] = useState("");
    const [filterLevel, setFilterLevel] = useState("");
    const [filterModule, setFilterModule] = useState("");
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedIds, setSelectedIds] = useState(new Set());
    const [expandedRows, setExpandedRows] = useState(new Set());

    // Modal state
    const [modal, setModal] = useState({ show: false, type: "", data: null });
    const [actionLoading, setActionLoading] = useState(false);
    const [excelFileName, setExcelFileName] = useState("TC_Export");
    const [showModuleNav, setShowModuleNav] = useState(false);

    const moduleNavRef = useRef(null);

    useEffect(() => {
        fetchTestCases();
    }, [filterType]);

    // Close module nav dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (moduleNavRef.current && !moduleNavRef.current.contains(e.target)) {
                setShowModuleNav(false);
            }
        };
        if (showModuleNav) {
            document.addEventListener("mousedown", handleClickOutside);
        }
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [showModuleNav]);

    const fetchTestCases = async () => {
        setLoading(true);
        try {
            const params = { limit: 10000 };
            if (filterType) params.test_type = filterType;
            const res = await getTestCases(params);
            setTestCases(res.data);
        } catch (err) {
            console.error("Fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    // ── Selection Handlers ────────────────────────────────
    const toggleSelect = (id) => {
        setSelectedIds((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const toggleExpand = (id) => {
        setExpandedRows((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const selectAll = () => {
        if (selectedIds.size === filtered.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(filtered.map((tc) => tc.test_id)));
        }
    };

    // ── Modal Handlers ────────────────────────────────────
    const openModal = (type, data = null) => setModal({ show: true, type, data });
    const closeModal = () => { setModal({ show: false, type: "", data: null }); };

    const handleConfirm = async () => {
        setActionLoading(true);
        try {
            if (modal.type === "delete-single") {
                await deleteTestCase(modal.data);
                setTestCases(prev => prev.filter(tc => tc.test_id !== modal.data));
                setSelectedIds(prev => { const next = new Set(prev); next.delete(modal.data); return next; });
            } else if (modal.type === "delete-selected") {
                await deleteSelectedTestCases([...selectedIds]);
                setTestCases(prev => prev.filter(tc => !selectedIds.has(tc.test_id)));
                setSelectedIds(new Set());
            } else if (modal.type === "clear-all") {
                await clearAllTestCases();
                setTestCases([]);
                setSelectedIds(new Set());
                sessionStorage.removeItem("upload_req_result");
                sessionStorage.removeItem("upload_design_result");
            } else if (modal.type === "delete-module") {
                await clearModuleTestCases(modal.data);
                setTestCases(prev => prev.filter(tc => tc.module_name !== modal.data));
                setSelectedIds(prev => {
                    const next = new Set(prev);
                    testCases.filter(tc => tc.module_name === modal.data).forEach(tc => next.delete(tc.test_id));
                    return next;
                });
            }
            closeModal();
        } catch (err) {
            console.error("Action error:", err);
            closeModal();
        } finally {
            setActionLoading(false);
        }
    };

    // ── Export Handlers ───────────────────────────────────
    const handleExportCSV = async () => {
        try {
            const res = await exportTestCasesCSV();
            const blob = new Blob([res.data], { type: "text/csv" });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "test_cases.csv";
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("CSV export error:", err);
        }
    };

    const handleExportJSON = async () => {
        try {
            const res = await exportTestCasesJSON();
            const blob = new Blob([JSON.stringify(res.data, null, 2)], {
                type: "application/json",
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "test_cases.json";
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("JSON export error:", err);
        }
    };

    const handleExportExcel = async () => {
        if (!excelFileName.trim()) return;
        try {
            const res = await exportTestCasesExcel(null, excelFileName);
            const blob = new Blob([res.data], {
                type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${excelFileName.replace(/\.xlsx$/, '')}.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Excel export error:", err);
        }
    };

    const handleExportModuleExcel = async (moduleName) => {
        try {
            const safeName = moduleName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
            const res = await exportTestCasesExcel(null, `Module_${safeName}_Export`, moduleName);
            const blob = new Blob([res.data], {
                type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Module_${safeName}_Export.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Module Excel export error:", err);
        }
    };

    // ── Filtering ─────────────────────────────────────────
    const allModules = [...new Set(testCases.map(tc => tc.module_name || "General"))].sort();

    const filtered = testCases.filter((tc) => {
        if (filterLevel && (tc.test_level || "Unit") !== filterLevel) return false;
        if (filterModule && (tc.module_name || "General") !== filterModule) return false;
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return (
            tc.module_name.toLowerCase().includes(term) ||
            tc.scenario.toLowerCase().includes(term) ||
            tc.expected_result.toLowerCase().includes(term)
        );
    });

    // Count by level for summary pills
    const levelCounts = testCases.reduce((acc, tc) => {
        const level = tc.test_level || "Unit";
        acc[level] = (acc[level] || 0) + 1;
        return acc;
    }, {});

    // Get unique requirement IDs for Clear All dropdown
    const requirementIds = [...new Set(testCases.map((tc) => tc.test_id).filter(Boolean))];

    // ── Modal message helper ──────────────────────────────
    const getModalMessage = () => {
        switch (modal.type) {
            case "delete-single":
                return `Are you sure you want to remove test case #${modal.data} from the list?`;
            case "delete-selected":
                return `Are you sure you want to remove ${selectedIds.size} selected test case(s) from the list?`;
            case "clear-all":
                return `Are you sure you want to clear all generated test cases?`;
            case "delete-module":
                return `Are you sure you want to delete ALL test cases in the "${modal.data}" module? This cannot be undone.`;
            default:
                return "";
        }
    };

    return (
        <div>

            {/* ── Confirmation Modal ─────────────────────────── */}
            {modal.show && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-icon">
                            <FiAlertTriangle />
                        </div>
                        <h3 className="modal-title">Confirm Action</h3>
                        <p className="modal-message">{getModalMessage()}</p>
                        <div className="modal-actions">
                            <button className="btn-outline" onClick={closeModal} disabled={actionLoading}>
                                Cancel
                            </button>
                            <button className="btn-danger" onClick={handleConfirm} disabled={actionLoading}>
                                {actionLoading ? (
                                    <>
                                        <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></div>
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <FiTrash2 /> Confirm Delete
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Page Header (always visible) ──────────────── */}
            <div className="page-header animate-in" style={{ paddingBottom: "0.5rem", marginBottom: "0.5rem" }}>
                <h1>Generated Test Cases</h1>
                <p>Browse, manage, and export all generated test cases.</p>
            </div>

            {/* ── Loading Spinner ────────────────────────────── */}
            {loading && (
                <div className="spinner-container">
                    <div className="spinner"></div>
                </div>
            )}

            {/* ── Sticky Toolbar ───────────────────────────── */}
            {!loading && (
                <div className="sticky-page-header" style={{ position: "sticky", top: 56, zIndex: 10, paddingBottom: "0.5rem", marginBottom: "0.5rem", background: "var(--bg-primary, #0f0f1a)" }}>
                    <div className="tc-toolbar-card animate-in">
                        {/* ── Search + Filters Row */}
                        <div className="tc-search-row">
                            <div className="tc-search-box">
                                <FiSearch className="tc-search-icon" />
                                <input
                                    type="text"
                                    className="tc-search-input"
                                    placeholder="Search scenarios, IDs, modules..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                            <select className="tc-filter-select" value={filterModule} onChange={(e) => setFilterModule(e.target.value)}>
                                <option value="">All Modules</option>
                                {allModules.map(m => (<option key={m} value={m}>{m}</option>))}
                            </select>
                            <select className="tc-filter-select" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                                <option value="">All Types</option>
                                <option value="positive">Positive</option>
                                <option value="negative">Negative</option>
                                <option value="boundary">Boundary</option>
                                <option value="edge">Edge</option>
                                <option value="security">Security</option>
                            </select>
                            <select className="tc-filter-select" value={filterLevel} onChange={(e) => setFilterLevel(e.target.value)}>
                                <option value="">All Levels</option>
                                <option value="Unit">Unit</option>
                                <option value="Integration">Integration</option>
                                <option value="System">System</option>
                                <option value="UAT">UAT</option>
                            </select>
                        </div>

                        {/* ── Export + Actions Row */}
                        <div className="tc-actions-row">
                            <div className="tc-export-group">
                                <button className="tc-export-btn" onClick={handleExportCSV} disabled={testCases.length === 0}>
                                    <FiDownload /> CSV
                                </button>
                                <button className="tc-export-btn" onClick={handleExportJSON} disabled={testCases.length === 0}>
                                    {'{ }'} JSON
                                </button>
                                <button className="tc-export-btn excel" onClick={handleExportExcel} disabled={testCases.length === 0}>
                                    <FiFileText /> EXCEL
                                </button>
                            </div>
                            <div style={{ flex: 1 }} />
                            {selectedIds.size > 0 && (
                                <button className="btn-danger-outline" onClick={() => openModal("delete-selected")} style={{ fontSize: "0.78rem", padding: "0.3rem 0.65rem" }}>
                                    <FiTrash2 /> Remove {selectedIds.size}
                                </button>
                            )}
                            <button className="tc-clear-all-btn" onClick={() => openModal("clear-all")} disabled={testCases.length === 0}>
                                <FiXCircle /> Clear Entire Test Case List
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Test Cases — Module-Grouped Tables ─────────── */}
            {!loading && filtered.length === 0 ? (
                <div className="form-section animate-in">
                    <div className="empty-state">
                        <FiList />
                        <h4>No test cases found</h4>
                        <p>Generate test cases from the Upload Requirement page, or adjust your filters.</p>
                    </div>
                </div>
            ) : (() => {
                // Group filtered test cases by module
                const grouped = {};
                filtered.forEach(tc => {
                    const mod = tc.module_name || "General";
                    if (!grouped[mod]) grouped[mod] = [];
                    grouped[mod].push(tc);
                });
                const moduleNames = Object.keys(grouped).sort();

                const formatDate = (dateStr) => {
                    if (!dateStr) return "—";
                    const d = new Date(dateStr);
                    if (isNaN(d.getTime())) return "—";
                    const day = String(d.getDate()).padStart(2, "0");
                    const mon = String(d.getMonth() + 1).padStart(2, "0");
                    const yr = d.getFullYear();
                    const hr = String(d.getHours()).padStart(2, "0");
                    const min = String(d.getMinutes()).padStart(2, "0");
                    return `${day}-${mon}-${yr} ${hr}:${min}`;
                };

                const renderStars = (score) => {
                    const s = score || 1;
                    return "★".repeat(s) + "☆".repeat(5 - s);
                };

                const scrollToModule = (name) => {
                    const el = document.getElementById(`module-${name.replace(/\s+/g, "-")}`);
                    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
                };

                return (
                    <>
                        {/* ── Floating Action Buttons (bottom-right) */}
                        {moduleNames.length > 0 && (
                            <div ref={moduleNavRef} style={{ position: "fixed", right: "1.25rem", bottom: "1.5rem", zIndex: 20, display: "flex", flexDirection: "column", alignItems: "center", gap: "0.6rem" }}>
                                {/* Scroll to Top */}
                                <button
                                    onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                                    style={{
                                        width: "42px", height: "42px", borderRadius: "50%",
                                        background: "linear-gradient(135deg, #10b981, #059669)",
                                        border: "none", color: "#fff", fontSize: "1.1rem",
                                        cursor: "pointer", boxShadow: "0 4px 12px rgba(16,185,129,0.35)",
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        transition: "transform 0.2s",
                                    }}
                                    title="Scroll to Top"
                                    onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
                                    onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
                                >
                                    ↑
                                </button>
                                {/* Module Nav Toggle */}
                                <div style={{ position: "relative" }}>
                                    <button
                                        onClick={() => setShowModuleNav(prev => !prev)}
                                        style={{
                                            width: "48px", height: "48px", borderRadius: "50%",
                                            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                                            border: "none", color: "#fff", fontSize: "1.2rem",
                                            cursor: "pointer", boxShadow: "0 4px 15px rgba(99,102,241,0.4)",
                                            display: "flex", alignItems: "center", justifyContent: "center",
                                            transition: "transform 0.2s",
                                        }}
                                        title="Jump to Module"
                                        onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
                                        onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
                                    >
                                        <FiLayers />
                                    </button>
                                    {showModuleNav && (
                                        <div style={{
                                            position: "absolute", bottom: "60px", right: 0,
                                            background: "rgba(20, 20, 40, 0.95)", borderRadius: "12px",
                                            padding: "0.75rem", backdropFilter: "blur(10px)",
                                            border: "1px solid rgba(255,255,255,0.1)",
                                            minWidth: "200px", maxHeight: "50vh", overflowY: "auto",
                                            boxShadow: "0 8px 30px rgba(0,0,0,0.4)",
                                            display: "flex", flexDirection: "column", gap: "0.35rem",
                                        }}>
                                            <span style={{ fontSize: "0.7rem", textTransform: "uppercase", opacity: 0.5, letterSpacing: "1px", paddingBottom: "0.3rem", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>Jump to Module</span>
                                            {moduleNames.map(name => (
                                                <button
                                                    key={name}
                                                    onClick={() => { scrollToModule(name); setShowModuleNav(false); }}
                                                    style={{
                                                        background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)",
                                                        color: "#a5b4fc", borderRadius: "8px", padding: "0.5rem 0.75rem",
                                                        fontSize: "0.8rem", cursor: "pointer",
                                                        textAlign: "left", transition: "all 0.2s",
                                                    }}
                                                    onMouseEnter={e => { e.target.style.background = "rgba(99, 102, 241, 0.3)"; e.target.style.color = "#fff"; }}
                                                    onMouseLeave={e => { e.target.style.background = "rgba(99, 102, 241, 0.1)"; e.target.style.color = "#a5b4fc"; }}
                                                >
                                                    {name}
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}


                        {/* ── Module Tables ────────────────────────── */}
                        {moduleNames.map(moduleName => (
                            <div key={moduleName} id={`module-${moduleName.replace(/\s+/g, "-")}`} className="data-table-wrapper animate-in" style={{ marginBottom: "1.5rem", scrollMarginTop: "160px" }}>
                                <div className="data-table-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
                                    <h3 style={{ margin: 0, flex: 1, minWidth: 0 }}>
                                        <FiLayers style={{ marginRight: 6, verticalAlign: "middle" }} />
                                        {moduleName} Module
                                        <span style={{ fontWeight: 400, fontSize: "0.85rem", marginLeft: 8, opacity: 0.7 }}>
                                            ({grouped[moduleName].length} cases)
                                        </span>
                                    </h3>
                                    <div style={{ display: "flex", gap: "0.5rem", flexShrink: 0 }}>
                                        <button
                                            className="tc-export-btn excel"
                                            style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem", whiteSpace: "nowrap", display: "flex", alignItems: "center", gap: "0.35rem" }}
                                            onClick={() => handleExportModuleExcel(moduleName)}
                                            title={`Export ${moduleName} test cases to Excel`}
                                        >
                                            <FiFileText /> Export Excel
                                        </button>
                                        <button
                                            className="btn-danger-outline"
                                            style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem", whiteSpace: "nowrap", display: "flex", alignItems: "center", gap: "0.35rem" }}
                                            onClick={() => openModal("delete-module", moduleName)}
                                            title={`Delete all ${moduleName} test cases`}
                                        >
                                            <FiTrash2 /> Delete Module
                                        </button>
                                    </div>
                                </div>
                                <div style={{ overflowX: "auto" }}>
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th style={{ width: "40px" }}>
                                                    <input
                                                        type="checkbox"
                                                        className="tc-checkbox"
                                                        checked={grouped[moduleName].every(tc => selectedIds.has(tc.test_id))}
                                                        onChange={() => {
                                                            const ids = grouped[moduleName].map(tc => tc.test_id);
                                                            const allSelected = ids.every(id => selectedIds.has(id));
                                                            setSelectedIds(prev => {
                                                                const next = new Set(prev);
                                                                ids.forEach(id => allSelected ? next.delete(id) : next.add(id));
                                                                return next;
                                                            });
                                                        }}
                                                    />
                                                </th>
                                                <th>ID</th>
                                                <th>Scenario</th>
                                                <th>Type</th>
                                                <th>Level</th>
                                                <th>Expected Result</th>
                                                <th>Priority</th>
                                                <th>Generated On</th>
                                                <th style={{ width: "60px" }}>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {grouped[moduleName].map((tc, idx) => (
                                                <React.Fragment key={tc.test_id}>
                                                    <tr className={selectedIds.has(tc.test_id) ? "row-selected" : ""}>
                                                        <td>
                                                            <input
                                                                type="checkbox"
                                                                className="tc-checkbox"
                                                                checked={selectedIds.has(tc.test_id)}
                                                                onChange={() => toggleSelect(tc.test_id)}
                                                            />
                                                        </td>
                                                        <td>{idx + 1}</td>
                                                        <td
                                                            onClick={() => toggleExpand(tc.test_id)}
                                                            style={{ cursor: "pointer" }}
                                                        >
                                                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                                                {expandedRows.has(tc.test_id) ? <FiChevronDown /> : <FiChevronRight />}
                                                                <span>{tc.scenario}</span>
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <span className={`badge badge-${tc.test_type}`}>
                                                                {tc.test_type}
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <span className={`badge badge-level-${(tc.test_level || "unit").toLowerCase()}`}>
                                                                {tc.test_level || "Unit"}
                                                            </span>
                                                        </td>
                                                        <td>{tc.expected_result}</td>
                                                        <td>
                                                            <span className={`badge badge-${tc.priority.toLowerCase()}`}>
                                                                {tc.priority}
                                                            </span>
                                                        </td>
                                                        <td style={{ fontSize: "0.8rem", whiteSpace: "nowrap", opacity: 0.8 }}>
                                                            {formatDate(tc.created_at)}
                                                        </td>
                                                        <td>
                                                            <button
                                                                className="btn-icon-danger"
                                                                onClick={() => openModal("delete-single", tc.test_id)}
                                                                title="Delete test case"
                                                            >
                                                                <FiTrash2 />
                                                            </button>
                                                        </td>
                                                    </tr>
                                                    {expandedRows.has(tc.test_id) && (
                                                        <tr className="expanded-details-row">
                                                            <td colSpan="9" style={{ backgroundColor: "#f8fafc", padding: "1rem" }}>
                                                                <div style={{ display: "flex", flexDirection: "column", gap: "10px", paddingLeft: "40px" }}>
                                                                    {tc.precondition && (
                                                                        <div>
                                                                            <strong>Precondition:</strong> {tc.precondition}
                                                                        </div>
                                                                    )}
                                                                    {tc.test_steps && tc.test_steps.length > 0 && (
                                                                        <div>
                                                                            <strong>Test Steps:</strong>
                                                                            <ol style={{ margin: "5px 0 0 20px", padding: 0 }}>
                                                                                {tc.test_steps.map((step, sIdx) => (
                                                                                    <li key={sIdx}>{step}</li>
                                                                                ))}
                                                                            </ol>
                                                                        </div>
                                                                    )}
                                                                    {(!tc.precondition && (!tc.test_steps || tc.test_steps.length === 0)) && (
                                                                        <div style={{ fontStyle: "italic", color: "#64748b" }}>
                                                                            No additional details available.
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    )}
                                                </React.Fragment>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        ))}
                    </>
                );
            })()}
        </div>
    );
}
