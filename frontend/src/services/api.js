/**
 * API Service Layer
 * --------------------
 * Centralised Axios instance and API call wrappers for
 * communicating with the FastAPI backend.
 */

import axios from "axios";

const API_BASE = "http://localhost:8000/api";

const api = axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json" },
    timeout: 30000,
});

// ── Requirements ────────────────────────────────────────────
export const createRequirement = (text) =>
    api.post("/requirements", { text });

export const getRequirements = (skip = 0, limit = 100) =>
    api.get("/requirements", { params: { skip, limit } });

export const getRequirement = (id) =>
    api.get(`/requirements/${id}`);

// ── Test Case Generation ────────────────────────────────────
export const generateTestCases = (requirementText, designText = null) =>
    api.post("/generate-testcases", {
        requirement_text: requirementText,
        design_text: designText,
    });

export const generateEnterprise = (requirementText, designText = null) =>
    api.post("/generate-enterprise", {
        requirement_text: requirementText,
        design_text: designText,
    }, { timeout: 120000 });

export const getTestCases = (params = {}) =>
    api.get("/test-cases", { params });

export const exportTestCasesCSV = (requirementId) => {
    const params = requirementId ? { requirement_id: requirementId } : {};
    return api.get("/test-cases/export/csv", {
        params,
        responseType: "blob",
    });
};

export const exportTestCasesJSON = (requirementId) => {
    const params = requirementId ? { requirement_id: requirementId } : {};
    return api.get("/test-cases/export/json", { params });
};

export const exportTestCasesExcel = (requirementId, fileName) => {
    const params = requirementId ? { requirement_id: requirementId } : {};
    return api.post("/test-cases/export/excel", { file_name: fileName }, {
        params,
        responseType: "blob",
    });
};

// ── Test Case Deletion ──────────────────────────────────────
export const deleteTestCase = (testId) =>
    api.delete(`/test-cases/${testId}`);

export const deleteSelectedTestCases = (testCaseIds) =>
    api.post("/test-cases/delete-selected", { test_case_ids: testCaseIds });

export const clearTestCasesForRequirement = (reqId) =>
    api.delete(`/test-cases/clear/${reqId}`);

// ── Save to Excel (requirement folder) ──────────────────────
export const saveExcelToFolder = (reqId) =>
    api.post(`/test-cases/save-excel/${reqId}`);

// ── Risk Analysis ───────────────────────────────────────────
export const runRiskAnalysis = (requirementText, designText = null) =>
    api.post("/risk-analysis", {
        requirement_text: requirementText,
        design_text: designText,
    });

// ── Defect Prediction ───────────────────────────────────────
export const predictDefect = (moduleData) =>
    api.post("/predict-defect", moduleData);

export const getPredictions = (skip = 0, limit = 100) =>
    api.get("/predictions", { params: { skip, limit } });

// ── Dashboard ───────────────────────────────────────────────
export const getDashboardStats = () =>
    api.get("/dashboard/stats");

// ── Defect Data ─────────────────────────────────────────────
export const addDefectData = (data) =>
    api.post("/defect-data", data);

export const getDefectData = () =>
    api.get("/defect-data");

// ── Design Documentation Upload ─────────────────────────────
export const uploadDesign = (formData) =>
    api.post("/design/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
    });

export const getDesignDocument = (designId) =>
    api.get(`/design/${designId}`);

export const getDesignsForRequirement = (reqId) =>
    api.get(`/design/by-requirement/${reqId}`);

export default api;
