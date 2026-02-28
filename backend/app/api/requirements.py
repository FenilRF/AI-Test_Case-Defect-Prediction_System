"""
API Routes — Requirements & Test Case Generation
---------------------------------------------------
Endpoints:
  POST /api/requirements              → store requirement
  GET  /api/requirements               → list all requirements
  GET  /api/requirements/{req_id}      → single requirement
  POST /api/generate-testcases         → parse + generate + store + risk analysis
  GET  /api/test-cases                 → list saved test cases
  DELETE /api/test-cases/{test_id}     → delete single test case
  POST /api/test-cases/delete-selected → delete multiple test cases
  DELETE /api/test-cases/clear/{req_id}→ clear all test cases for requirement
  GET  /api/test-cases/export/csv      → download CSV
  GET  /api/test-cases/export/json     → download JSON
  GET  /api/test-cases/export/excel    → download Excel
  POST /api/test-cases/save-excel/{req_id} → save Excel to requirement folder
  POST /api/risk-analysis              → standalone risk analysis
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse, Response
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import Requirement, TestCase
from app.schemas.schemas import (
    RequirementCreate,
    RequirementResponse,
    TestCaseGenerationRequest,
    TestCaseGenerationResponse,
    TestCaseOut,
    DeleteTestCasesRequest,
    DeleteTestCasesResponse,
    SaveExcelResponse,
    RiskAnalysisResponse,
)
from app.services.nlp_service import parse_requirement
from app.services.test_case_generator import generate_test_cases
from app.services.defect_prediction_service import classify_risk, risk_to_priority
from app.services.risk_analysis_service import analyse_risk
from app.services.folder_storage_service import (
    create_requirement_folder,
    save_excel_to_folder,
)
from app.utils.export import test_cases_to_csv, test_cases_to_json, test_cases_to_excel
from app.schemas.schemas import DefectPredictionRequest, ExportExcelRequest
from app.models.models import Prediction
from app.services.defect_prediction_service import predict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Requirements & Test Cases"])


# ── Requirements CRUD ─────────────────────────────────────────

@router.post("/requirements", response_model=RequirementResponse, status_code=201)
def create_requirement(payload: RequirementCreate, db: Session = Depends(get_db)):
    """Save a raw requirement to the database."""
    req = Requirement(text=payload.text)
    db.add(req)
    db.commit()
    db.refresh(req)
    logger.info("Stored requirement id=%d", req.id)
    return req


@router.get("/requirements", response_model=list[RequirementResponse])
def list_requirements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Return all stored requirements with pagination."""
    return db.query(Requirement).offset(skip).limit(limit).all()


@router.get("/requirements/{req_id}", response_model=RequirementResponse)
def get_requirement(req_id: int, db: Session = Depends(get_db)):
    """Retrieve a single requirement by ID."""
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


# ── Test Case Generation ──────────────────────────────────────

@router.post("/generate-testcases", response_model=TestCaseGenerationResponse)
def generate_testcases(payload: TestCaseGenerationRequest, db: Session = Depends(get_db)):
    """
    End-to-end pipeline:
      1. Store the requirement
      2. Parse it with the NLP engine
      3. Generate test cases
      4. Persist test cases to DB
      5. Run multi-layer risk analysis
      6. Create folder-based storage
      7. Return everything
    """
    # 1. Store requirement
    requirement = Requirement(
        text=payload.requirement_text,
        design_text=payload.design_text,
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    # 2. Parse
    parsed = parse_requirement(payload.requirement_text)

    # 3. Generate
    raw_cases = generate_test_cases(parsed)

    # 4. Persist
    db_cases = []
    for rc in raw_cases:
        tc = TestCase(
            requirement_id=requirement.id,
            module_name=rc["module_name"],
            scenario=rc["scenario"],
            test_type=rc["test_type"],
            test_level=rc.get("test_level", "Unit"),
            expected_result=rc["expected_result"],
            priority=rc["priority"],
        )
        db.add(tc)
        db_cases.append(tc)
    db.commit()

    # Refresh to get auto-generated IDs
    for tc in db_cases:
        db.refresh(tc)

    # 5. Risk analysis
    risk_report = analyse_risk(
        payload.requirement_text,
        payload.design_text or "",
    )

    # 5.5 Automatically run Defect Prediction
    tc_text = " ".join([tc.scenario for tc in db_cases])
    pred_req = DefectPredictionRequest(
        module_name=parsed.module,
        lines_of_code=len(db_cases) * 50,
        complexity_score=len(db_cases) * 5.0,
        past_defects=0,
        code_churn=0,
        requirement_text=payload.requirement_text,
        design_text=payload.design_text or "",
        test_cases_text=tc_text
    )
    pred_result = predict(pred_req)
    pred_db = Prediction(
        module_name=pred_result.module_name,
        probability=pred_result.defect_probability,
        risk_level=pred_result.risk_level,
        defect_category=pred_result.defect_category,
    )
    db.add(pred_db)
    # We will commit this at the end
    
    defect_pred_dict = {
        "module_name": pred_db.module_name,
        "probability": pred_db.probability,
        "risk_level": pred_db.risk_level,
        "defect_category": pred_db.defect_category,
    }

    # 6. Folder storage
    tc_dicts = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in db_cases
    ]
    try:
        folder_path = create_requirement_folder(
            module_name=parsed.module,
            requirement_text=payload.requirement_text,
            design_text=payload.design_text,
            test_cases=tc_dicts,
            risk_analysis=risk_report,
            defect_prediction=defect_pred_dict,
        )
        # Update requirement with folder path
        requirement.folder_path = folder_path
        db.commit()
        logger.info("Requirement id=%d folder: %s", requirement.id, folder_path)
    except Exception as e:
        logger.exception("Failed to create requirement folder: %s", e)
        folder_path = None

    # 7. Build response
    test_case_responses = [
        TestCaseOut(
            test_id=tc.id,
            module_name=tc.module_name,
            scenario=tc.scenario,
            test_type=tc.test_type,
            test_level=tc.test_level or "Unit",
            expected_result=tc.expected_result,
            priority=tc.priority,
        )
        for tc in db_cases
    ]

    return TestCaseGenerationResponse(
        requirement_id=requirement.id,
        parsed=parsed,
        test_cases=test_case_responses,
        folder_path=folder_path,
        risk_analysis=risk_report,
    )


# ── Test Cases Listing ────────────────────────────────────────

@router.get("/test-cases", response_model=list[TestCaseOut])
def list_test_cases(
    requirement_id: Optional[int] = None,
    test_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List test cases with optional filters."""
    query = db.query(TestCase)
    if requirement_id:
        query = query.filter(TestCase.requirement_id == requirement_id)
    if test_type:
        query = query.filter(TestCase.test_type == test_type)
    cases = query.offset(skip).limit(limit).all()
    return [
        TestCaseOut(
            test_id=tc.id,
            module_name=tc.module_name,
            scenario=tc.scenario,
            test_type=tc.test_type,
            test_level=tc.test_level or "Unit",
            expected_result=tc.expected_result,
            priority=tc.priority,
        )
        for tc in cases
    ]


# ── Test Case Deletion ───────────────────────────────────────

@router.delete("/test-cases/{test_id}", response_model=DeleteTestCasesResponse)
def delete_test_case(test_id: int, db: Session = Depends(get_db)):
    """Delete a single test case by ID."""
    tc = db.query(TestCase).filter(TestCase.id == test_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    db.delete(tc)
    db.commit()
    logger.info("Deleted test case id=%d", test_id)
    return DeleteTestCasesResponse(deleted_count=1, message=f"Test case {test_id} deleted successfully")


@router.post("/test-cases/delete-selected", response_model=DeleteTestCasesResponse)
def delete_selected_test_cases(payload: DeleteTestCasesRequest, db: Session = Depends(get_db)):
    """Delete multiple test cases by their IDs."""
    deleted = (
        db.query(TestCase)
        .filter(TestCase.id.in_(payload.test_case_ids))
        .delete(synchronize_session="fetch")
    )
    db.commit()
    logger.info("Deleted %d test cases (requested %d)", deleted, len(payload.test_case_ids))
    return DeleteTestCasesResponse(
        deleted_count=deleted,
        message=f"Successfully deleted {deleted} test case(s)",
    )


@router.delete("/test-cases/clear/{req_id}", response_model=DeleteTestCasesResponse)
def clear_test_cases_for_requirement(req_id: int, db: Session = Depends(get_db)):
    """Delete ALL test cases for a specific requirement."""
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    deleted = (
        db.query(TestCase)
        .filter(TestCase.requirement_id == req_id)
        .delete(synchronize_session="fetch")
    )
    db.commit()
    logger.info("Cleared %d test cases for requirement id=%d", deleted, req_id)
    return DeleteTestCasesResponse(
        deleted_count=deleted,
        message=f"Cleared {deleted} test case(s) for requirement #{req_id}",
    )


# ── Export Endpoints ──────────────────────────────────────────

@router.get("/test-cases/export/csv")
def export_csv(
    requirement_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Export test cases as CSV download."""
    query = db.query(TestCase)
    if requirement_id:
        query = query.filter(TestCase.requirement_id == requirement_id)
    cases = query.all()

    data = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in cases
    ]
    csv_str = test_cases_to_csv(data)
    return PlainTextResponse(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=test_cases.csv"},
    )


@router.get("/test-cases/export/json")
def export_json(
    requirement_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Export test cases as JSON download."""
    query = db.query(TestCase)
    if requirement_id:
        query = query.filter(TestCase.requirement_id == requirement_id)
    cases = query.all()

    data = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in cases
    ]
    json_str = test_cases_to_json(data)
    return JSONResponse(
        content={"test_cases": data},
        headers={"Content-Disposition": "attachment; filename=test_cases.json"},
    )


@router.post("/test-cases/export/excel")
def export_excel(
    payload: ExportExcelRequest,
    requirement_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Export test cases as a styled Excel (.xlsx) download and save to folder."""
    query = db.query(TestCase)
    if requirement_id:
        query = query.filter(TestCase.requirement_id == requirement_id)
    cases = query.all()

    module_name = "AllModules"
    if requirement_id and cases:
        module_name = cases[0].module_name

    data = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in cases
    ]
    excel_bytes = test_cases_to_excel(data)

    filename = payload.file_name if payload.file_name else "TC_Export"
    if not filename.endswith(".xlsx"):
        filename += ".xlsx"

    from app.services.folder_storage_service import _BASE_DIR
    import os
    os.makedirs(_BASE_DIR, exist_ok=True)
    
    save_dir = _BASE_DIR
    if requirement_id:
        req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        if req and req.folder_path:
            save_dir = req.folder_path
            
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as f:
        f.write(excel_bytes)
        
    logger.info("Saved exported Excel to %s", save_path)

    import io
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Save to Excel (to requirement folder) ─────────────────────

@router.post("/test-cases/save-excel/{req_id}", response_model=SaveExcelResponse)
def save_excel_to_requirement_folder(req_id: int, db: Session = Depends(get_db)):
    """
    Save test cases as Excel into the requirement's folder.
    Uses the folder_path stored in the requirement record.
    """
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if not req.folder_path:
        raise HTTPException(
            status_code=400,
            detail="No folder associated with this requirement. Re-generate test cases first.",
        )

    cases = db.query(TestCase).filter(TestCase.requirement_id == req_id).all()
    if not cases:
        raise HTTPException(status_code=404, detail="No test cases found for this requirement")

    data = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in cases
    ]
    excel_bytes = test_cases_to_excel(data)

    try:
        file_path = save_excel_to_folder(req.folder_path, excel_bytes)
    except Exception as e:
        logger.exception("Failed to save Excel to folder: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to save Excel: {str(e)}")

    # Generate display filename
    module_name = cases[0].module_name if cases else "Unknown"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_module = "".join(c if c.isalnum() else "_" for c in module_name)[:40]
    file_name = f"Requirement_{safe_module}_{timestamp}.xlsx"

    logger.info("Saved Excel for requirement id=%d → %s", req_id, file_path)
    return SaveExcelResponse(
        file_path=file_path,
        file_name=file_name,
        message=f"Excel saved successfully to requirement folder",
    )


# ── Standalone Risk Analysis ──────────────────────────────────

@router.post("/risk-analysis", response_model=RiskAnalysisResponse)
def run_risk_analysis(payload: TestCaseGenerationRequest):
    """
    Run multi-layer risk analysis on requirement + optional design text.
    Does NOT generate test cases — use /generate-testcases for full pipeline.
    """
    report = analyse_risk(
        payload.requirement_text,
        payload.design_text or "",
    )
    return RiskAnalysisResponse(**report)


# ── Enterprise Test Generation ─────────────────────────────────

@router.post("/generate-enterprise")
def generate_enterprise(payload: TestCaseGenerationRequest, db: Session = Depends(get_db)):
    """
    Enterprise 5-phase test generation pipeline:
      Phase 1: Full input analysis (12-module decomposition)
      Phase 2: Deep requirement decomposition
      Phase 3: Exhaustive scenario generation (13 categories)
      Phase 4: Duplicate elimination
      Phase 5: Coverage validation

    No limit on test case count — optimizes for complete coverage.
    """
    from app.services.enterprise_test_engine import generate_enterprise_test_cases

    # 1. Store requirement
    requirement = Requirement(
        text=payload.requirement_text,
        design_text=payload.design_text,
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    # 2. Parse with NLP (for backward-compat response shape)
    parsed = parse_requirement(payload.requirement_text)

    # 3. Run enterprise engine
    engine_result = generate_enterprise_test_cases(
        requirement_text=payload.requirement_text,
        design_text=payload.design_text,
    )

    # 4. Persist test cases to DB
    db_cases = []
    for tc in engine_result["test_cases"]:
        db_tc = TestCase(
            requirement_id=requirement.id,
            module_name=tc["module_name"],
            scenario=tc["scenario"],
            test_type=tc["test_type"],
            test_level=tc.get("test_level", "Unit"),
            expected_result=tc["expected_result"],
            priority=tc["priority"],
        )
        db.add(db_tc)
        db_cases.append(db_tc)
    db.commit()

    for tc in db_cases:
        db.refresh(tc)

    # 5. Risk analysis
    risk_report = analyse_risk(
        payload.requirement_text,
        payload.design_text or "",
    )

    # 6. Defect prediction
    tc_text = " ".join([tc.scenario for tc in db_cases[:50]])
    pred_req = DefectPredictionRequest(
        module_name=parsed.module,
        lines_of_code=len(db_cases) * 50,
        complexity_score=len(db_cases) * 5.0,
        past_defects=0,
        code_churn=0,
        requirement_text=payload.requirement_text,
        design_text=payload.design_text or "",
        test_cases_text=tc_text,
    )
    pred_result = predict(pred_req)
    pred_db = Prediction(
        module_name=pred_result.module_name,
        probability=pred_result.defect_probability,
        risk_level=pred_result.risk_level,
        defect_category=pred_result.defect_category,
    )
    db.add(pred_db)

    defect_pred_dict = {
        "module_name": pred_db.module_name,
        "probability": pred_db.probability,
        "risk_level": pred_db.risk_level,
        "defect_category": pred_db.defect_category,
    }

    # 7. Folder storage
    tc_dicts = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in db_cases
    ]
    try:
        folder_path = create_requirement_folder(
            module_name=parsed.module,
            requirement_text=payload.requirement_text,
            design_text=payload.design_text,
            test_cases=tc_dicts,
            risk_analysis=risk_report,
            defect_prediction=defect_pred_dict,
        )
        requirement.folder_path = folder_path
        db.commit()
    except Exception as e:
        logger.exception("Failed to create folder: %s", e)
        folder_path = None

    # 8. Build response — update test IDs from DB
    response_cases = [
        {
            "test_id": tc.id,
            "module_name": tc.module_name,
            "scenario": tc.scenario,
            "test_type": tc.test_type,
            "test_level": tc.test_level or "Unit",
            "expected_result": tc.expected_result,
            "priority": tc.priority,
        }
        for tc in db_cases
    ]

    return {
        "requirement_id": requirement.id,
        "parsed": parsed.model_dump(),
        "decomposition": engine_result["decomposition"],
        "test_cases": response_cases,
        "coverage": engine_result["coverage"],
        "risk_analysis": risk_report,
        "folder_path": folder_path,
    }

