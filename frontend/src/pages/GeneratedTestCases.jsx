/**
 * Generated Test Cases Page
 * ----------------------------
 * Lists all stored test cases with filtering by type/level,
 * search, CSV/JSON/Excel export, checkbox selection,
 * Delete Selected, Clear All, and confirmation modals.
 */

import { useState, useEffect } from "react";
import { FiDownload, FiFilter, FiList, FiSearch, FiFileText, FiTrash2, FiXCircle, FiAlertTriangle, FiLayers } from "react-icons/fi";
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
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedIds, setSelectedIds] = useState(new Set());

    // Modal state
    const [modal, setModal] = useState({ show: false, type: "", data: null });
    const [actionLoading, setActionLoading] = useState(false);
    const [excelFileName, setExcelFileName] = useState("TC_Export");

    useEffect(() => {
        fetchTestCases();
    }, [filterType]);

    const fetchTestCases = async () => {
        setLoading(true);
        try {
            const params = {};
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

    // ── Filtering ─────────────────────────────────────────
    const filtered = testCases.filter((tc) => {
        if (filterLevel && (tc.test_level || "Unit") !== filterLevel) return false;
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
            <div className="page-header animate-in">
                <h1>Generated Test Cases</h1>
                <p>View, filter, manage, and export all generated test cases</p>
            </div>

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

            {/* ── Level Summary Pills ─────────────────────────── */}
            {testCases.length > 0 && (
                <div className="level-summary animate-in">
                    {["Unit", "Integration", "System", "UAT"].map((level) => (
                        <div
                            key={level}
                            className={`level-pill ${filterLevel === level ? "active" : ""}`}
                            onClick={() => setFilterLevel(filterLevel === level ? "" : level)}
                        >
                            <span className={`badge badge-level-${level.toLowerCase()}`}>{level}</span>
                            <span className="level-count">{levelCounts[level] || 0}</span>
                        </div>
                    ))}
                    {filterLevel && (
                        <button
                            className="btn-clear-filter"
                            onClick={() => setFilterLevel("")}
                        >
                            Clear Level Filter
                        </button>
                    )}
                </div>
            )}

            {/* ── Filters & Actions ──────────────────────────── */}
            <div className="form-section animate-in" style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}>
                <div className="form-group" style={{ flex: 1, minWidth: "200px", marginBottom: 0 }}>
                    <label><FiSearch style={{ marginRight: 4 }} /> Search</label>
                    <input
                        type="text"
                        className="form-input"
                        placeholder="Search by module, scenario..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div className="form-group" style={{ minWidth: "160px", marginBottom: 0 }}>
                    <label><FiFilter style={{ marginRight: 4 }} /> Test Type</label>
                    <select
                        className="form-input"
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                    >
                        <option value="">All Types</option>
                        <option value="positive">Positive</option>
                        <option value="negative">Negative</option>
                        <option value="boundary">Boundary</option>
                        <option value="edge">Edge</option>
                        <option value="security">Security</option>
                    </select>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                    <button className="btn-outline" onClick={handleExportCSV} disabled={testCases.length === 0}>
                        <FiDownload /> CSV
                    </button>
                    <button className="btn-outline" onClick={handleExportJSON} disabled={testCases.length === 0}>
                        <FiDownload /> JSON
                    </button>
                    <input
                        type="text"
                        className="form-input"
                        value={excelFileName}
                        onChange={(e) => setExcelFileName(e.target.value)}
                        style={{ width: "130px", marginBottom: 0 }}
                        placeholder="File Name"
                    />
                    <button className="btn-gradient btn-excel" onClick={handleExportExcel} disabled={testCases.length === 0 || !excelFileName.trim()}>
                        <FiFileText /> Excel
                    </button>
                </div>
            </div>

            {/* ── Bulk Actions Bar ────────────────────────────── */}
            {testCases.length > 0 && (
                <div className="form-section animate-in" style={{ display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap", padding: "1rem 2rem" }}>
                    <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                        {selectedIds.size > 0 ? `${selectedIds.size} selected` : "No selection"}
                    </span>
                    <button
                        className="btn-danger-outline"
                        onClick={() => openModal("delete-selected")}
                        disabled={selectedIds.size === 0}
                    >
                        <FiTrash2 /> Remove Selected
                    </button>
                    <div style={{ flex: 1 }} />
                    <div className="form-group" style={{ marginBottom: 0, minWidth: "130px" }}>
                        <button
                            className="btn-danger"
                            onClick={() => openModal("clear-all")}
                        >
                            <FiXCircle /> Clear Entire Test Case List
                        </button>
                    </div>
                </div>
            )}

            {/* ── Test Cases — Module-Grouped Tables ─────────── */}
            {loading ? (
                <div className="spinner-container">
                    <div className="spinner"></div>
                </div>
            ) : filtered.length === 0 ? (
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

                return moduleNames.map(moduleName => (
                    <div key={moduleName} className="data-table-wrapper animate-in" style={{ marginBottom: "1.5rem" }}>
                        <div className="data-table-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <h3 style={{ margin: 0 }}>
                                <FiLayers style={{ marginRight: 6, verticalAlign: "middle" }} />
                                {moduleName} Module
                                <span style={{ fontWeight: 400, fontSize: "0.85rem", marginLeft: 8, opacity: 0.7 }}>
                                    ({grouped[moduleName].length} cases)
                                </span>
                            </h3>
                            <button
                                className="btn-danger-outline"
                                style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem" }}
                                onClick={() => openModal("delete-module", moduleName)}
                                title={`Delete all ${moduleName} test cases`}
                            >
                                <FiTrash2 style={{ marginRight: 4 }} /> Delete Module
                            </button>
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
                                        <tr key={tc.test_id} className={selectedIds.has(tc.test_id) ? "row-selected" : ""}>
                                            <td>
                                                <input
                                                    type="checkbox"
                                                    className="tc-checkbox"
                                                    checked={selectedIds.has(tc.test_id)}
                                                    onChange={() => toggleSelect(tc.test_id)}
                                                />
                                            </td>
                                            <td>{idx + 1}</td>
                                            <td>{tc.scenario}</td>
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
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ));
            })()}
        </div>
    );
}
