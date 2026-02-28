"""
Pydantic Schemas (Request / Response models)
----------------------------------------------
Provides data validation and serialization for all API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════
# Requirement Schemas
# ═══════════════════════════════════════════════════════

class RequirementCreate(BaseModel):
    """Payload for submitting a new requirement."""
    text: str = Field(..., min_length=5, description="Raw requirement text")


class RequirementResponse(BaseModel):
    """Response schema for a stored requirement."""
    id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════
# NLP Parsed Requirement
# ═══════════════════════════════════════════════════════

class ParsedRequirement(BaseModel):
    """Structured output from the NLP engine."""
    module: str
    actions: list[str]
    fields: list[str]
    validations: list[str]


# ═══════════════════════════════════════════════════════
# Test Case Schemas
# ═══════════════════════════════════════════════════════

class TestCaseOut(BaseModel):
    """Single test case response."""
    test_id: int
    module_name: str
    scenario: str
    test_type: str
    test_level: str = "Unit"  # Unit / Integration / System / UAT
    expected_result: str
    priority: str

    class Config:
        from_attributes = True


class TestCaseGenerationRequest(BaseModel):
    """Request body for bulk test-case generation."""
    requirement_text: str = Field(..., min_length=5)
    design_text: Optional[str] = Field(None, description="Optional design document text")


class TestCaseGenerationResponse(BaseModel):
    """Response wrapping generated test cases."""
    requirement_id: int
    parsed: ParsedRequirement
    test_cases: list[TestCaseOut]
    folder_path: Optional[str] = None
    risk_analysis: Optional[Dict[str, Any]] = None


# ═══════════════════════════════════════════════════════
# Defect Prediction Schemas
# ═══════════════════════════════════════════════════════

class DefectPredictionRequest(BaseModel):
    """Module metrics sent for defect prediction."""
    module_name: str = Field(..., min_length=1)
    lines_of_code: int = Field(..., gt=0)
    complexity_score: float = Field(..., ge=0)
    past_defects: int = Field(..., ge=0)
    code_churn: int = Field(..., ge=0)
    requirement_text: Optional[str] = ""
    design_text: Optional[str] = ""
    test_cases_text: Optional[str] = ""


class DefectPredictionResponse(BaseModel):
    """Prediction result."""
    module_name: str
    defect_probability: float
    risk_level: str  # Low / Medium / High
    defect_category: str = "Function Level"  # UI / API / Integration / Function / System / Non-functional


class PredictionHistoryResponse(BaseModel):
    """Stored prediction record."""
    id: int
    module_name: str
    probability: float
    risk_level: str
    defect_category: Optional[str] = "Function Level"
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════
# Defect Data (training data) Schemas
# ═══════════════════════════════════════════════════════

class DefectDataCreate(BaseModel):
    """Schema for adding a defect-data record."""
    module_name: str
    lines_of_code: int = Field(..., gt=0)
    complexity_score: float = Field(..., ge=0)
    past_defects: int = Field(..., ge=0)
    code_churn: int = Field(..., ge=0)


class DefectDataResponse(BaseModel):
    id: int
    module_name: str
    lines_of_code: int
    complexity_score: float
    past_defects: int
    code_churn: int

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════
# Dashboard / Aggregation
# ═══════════════════════════════════════════════════════

class DashboardStats(BaseModel):
    """High-level statistics for the dashboard."""
    total_requirements: int
    total_test_cases: int
    total_predictions: int
    high_risk_modules: int
    medium_risk_modules: int
    low_risk_modules: int


# ═══════════════════════════════════════════════════════
# Risk Analysis Schemas
# ═══════════════════════════════════════════════════════

class RiskLayerResult(BaseModel):
    """Risk result for a single analysis layer."""
    score: float
    risk_level: str
    found_signals: List[str]


class RiskAnalysisResponse(BaseModel):
    """Full multi-layer risk analysis report."""
    layers: Dict[str, RiskLayerResult]
    overall_score: float
    overall_risk_level: str
    summary: str


# ═══════════════════════════════════════════════════════
# Test Case Management Schemas
# ═══════════════════════════════════════════════════════

class DeleteTestCasesRequest(BaseModel):
    """Request to delete specific test cases by ID."""
    test_case_ids: List[int] = Field(..., min_length=1, description="List of test case IDs to delete")


class DeleteTestCasesResponse(BaseModel):
    """Response after deleting test cases."""
    deleted_count: int
    message: str


# ═══════════════════════════════════════════════════════
# Save to Excel Schemas
# ═══════════════════════════════════════════════════════

class SaveExcelResponse(BaseModel):
    """Response after saving Excel to requirement folder."""
    file_path: str
    file_name: str
    message: str


# ═══════════════════════════════════════════════════════
# Design Upload Schemas
# ═══════════════════════════════════════════════════════

class DesignClassification(BaseModel):
    """UI vs API vs System classification scores."""
    ui_score: int
    api_score: int
    system_score: int
    primary_type: str


class DesignAnalysisResult(BaseModel):
    """Result of lightweight design document analysis."""
    modules: List[str]
    module_count: int
    integrations: List[str]
    integration_count: int
    classification: DesignClassification
    design_sources: Dict[str, Any]
    summary: str


class DesignUploadResponse(BaseModel):
    """Response after design documentation upload."""
    design_id: int
    requirement_id: Optional[int] = None
    uploaded_files: List[str]
    design_urls: List[str]
    folder_path: str
    analysis: DesignAnalysisResult
    message: str
    test_cases: Optional[List[Dict[str, Any]]] = None

class ExportExcelRequest(BaseModel):
    file_name: str



class DesignDocumentOut(BaseModel):
    """Single design document record for listing."""
    id: int
    requirement_id: Optional[int] = None
    file_names: Optional[List[str]] = None
    design_urls: Optional[List[str]] = None
    folder_path: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════
# Enterprise Test Generation Schemas
# ═══════════════════════════════════════════════════════

class DecomposedModule(BaseModel):
    """Single module from the requirement decomposition."""
    category: str
    matched_keywords: List[str]
    matched_phrases: List[str]
    relevance_score: int
    explicit_rules: List[str]
    implicit_rules: List[str]
    boundaries: List[str]
    negative_paths: List[str]


class RequirementDecomposition(BaseModel):
    """Full Phase 1+2 decomposition output."""
    modules: List[DecomposedModule]
    total_modules: int
    design_integration: Optional[Dict[str, Any]] = None
    ambiguity_warnings: List[str]


class CoverageValidation(BaseModel):
    """Phase 5 coverage validation report."""
    total_modules_detected: int
    module_categories: List[str]
    total_scenarios_generated: int
    scenarios_by_type: Dict[str, int]
    coverage_confidence_score: int
    ambiguity_warnings: List[str]


class EnterpriseTestCaseOut(BaseModel):
    """Single enterprise test case."""
    test_id: int
    module_name: str
    scenario: str
    test_type: str
    test_level: str = "Unit"
    expected_result: str
    priority: str


class EnterpriseGenerationResponse(BaseModel):
    """Full enterprise 5-phase test generation response."""
    requirement_id: int
    parsed: ParsedRequirement
    decomposition: RequirementDecomposition
    test_cases: List[EnterpriseTestCaseOut]
    coverage: CoverageValidation
    risk_analysis: Optional[Dict[str, Any]] = None
    folder_path: Optional[str] = None

