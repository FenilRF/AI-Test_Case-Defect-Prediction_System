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
    precondition: str = ""
    test_steps: List[str] = []
    priority: str
    created_at: Optional[datetime] = None
    complexity_score: int = 1
    duplicate_score: float = 0.0
    coverage_tag: str = ""

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
# Enterprise Design Intelligence Schemas
# ═══════════════════════════════════════════════════════

class UIComponentOut(BaseModel):
    """Single detected UI component."""
    type: str = ""
    label: str = ""
    source: str = ""
    section: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class UIModuleOut(BaseModel):
    """Module with components, pages, flows, validations."""
    module_name: str
    pages: List[str] = []
    ui_components: List[Dict[str, Any]] = []
    flows: List[Dict[str, Any]] = []
    validations_detected: List[str] = []


class UISchemaOut(BaseModel):
    """Full UI schema output."""
    modules: List[UIModuleOut] = []
    total_components: int = 0
    total_pages: int = 0
    total_modules: int = 0


class DetectedFlowOut(BaseModel):
    """Detected user flows."""
    primary_flows: List[Dict[str, Any]] = []
    alternate_flows: List[Dict[str, Any]] = []
    cross_flows: List[Dict[str, Any]] = []
    total_flows: int = 0


class EnterpriseDesignTestCase(BaseModel):
    """Enterprise-grade test case from design analysis."""
    id: str = ""
    module: str = ""
    scenario: str = ""
    type: str = ""
    level: str = "UI"
    priority: str = "P3"
    precondition: str = ""
    test_steps: List[str] = []
    expected_result: str = ""
    complexity_score: int = 2
    coverage_tag: str = ""


class DesignCoverageResult(BaseModel):
    """Coverage validation result."""
    total_test_cases: int = 0
    enterprise_coverage_percentage: float = 0.0
    type_distribution: Dict[str, int] = {}
    module_distribution: Dict[str, int] = {}
    level_distribution: Dict[str, int] = {}
    missing_coverage: List[str] = []


class EnterpriseDesignUploadResponse(BaseModel):
    """Full enterprise design upload response."""
    design_id: int
    requirement_id: Optional[int] = None
    uploaded_files: List[str] = []
    design_urls: List[str] = []
    folder_path: str = ""
    source_type: str = ""
    message: str = ""
    # Enterprise analysis results
    total_pages_analyzed: int = 0
    total_ui_components_detected: int = 0
    total_flows_detected: int = 0
    total_test_cases_generated: int = 0
    enterprise_coverage_percentage: float = 0.0
    analysis_summary: str = ""
    ui_schema: Optional[Dict[str, Any]] = None
    detected_flows: Optional[Dict[str, Any]] = None
    coverage: Optional[Dict[str, Any]] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    modules_grouped_test_cases: Optional[Dict[str, Any]] = None
    # Legacy fields for backward compat
    analysis: Optional[Dict[str, Any]] = None


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
    precondition: str = ""
    test_steps: List[str] = []
    priority: str
    created_at: Optional[datetime] = None
    complexity_score: int = 1
    duplicate_score: float = 0.0
    coverage_tag: str = ""


class GroupedTestCasesResponse(BaseModel):
    """Module-wise grouped test cases."""
    modules: Dict[str, List[TestCaseOut]]
    total: int


class CoverageReport(BaseModel):
    """Coverage validation report."""
    total_requirements_detected: int
    total_test_cases_generated: int
    coverage_percentage: float
    uncovered_areas: List[str]


class EnterpriseGenerationResponse(BaseModel):
    """Full enterprise 5-phase test generation response."""
    requirement_id: int
    parsed: ParsedRequirement
    decomposition: RequirementDecomposition
    test_cases: List[EnterpriseTestCaseOut]
    coverage: CoverageValidation
    risk_analysis: Optional[Dict[str, Any]] = None
    folder_path: Optional[str] = None

