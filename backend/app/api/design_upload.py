"""
API Routes — Design Documentation Upload (Enterprise Intelligence Engine)
-------------------------------------------------------------------------
Endpoints:
  POST /api/design/upload           → upload design files/images/URLs + enterprise analysis
  GET  /api/design/{design_id}      → get design document details
  GET  /api/design/by-requirement/{req_id} → list designs for a requirement
"""

import json
import logging
import os
import shutil
import traceback
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import DesignDocument, Requirement
from app.schemas.schemas import (
    EnterpriseDesignUploadResponse,
    DesignDocumentOut,
)
from app.services.folder_storage_service import (
    create_design_folder,
    save_design_links,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/design", tags=["Design Documentation"])

# Allowed file extensions
_ALLOWED_DOC_EXTENSIONS = {".pdf", ".docx", ".pptx", ".txt"}
_ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
_ALLOWED_EXTENSIONS = _ALLOWED_DOC_EXTENSIONS | _ALLOWED_IMAGE_EXTENSIONS
_MAX_FILE_SIZE_MB = 20


def _validate_file(file: UploadFile) -> str:
    """Validate uploaded file extension. Returns the lowercase extension."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )
    return ext


@router.post("/upload", response_model=EnterpriseDesignUploadResponse)
async def upload_design(
    design_text: str = Form(None),
    design_url: str = Form(None),
    file: UploadFile = File(None),
    requirement_id: Optional[int] = Form(None, description="Associated requirement ID"),
    db: Session = Depends(get_db),
):
    """
    Upload design documentation — files, images, and/or URLs.

    Enterprise Intelligence Engine:
    1. Detects input type (URL/Document/Image)
    2. Extracts UI components via DOM + Vision LLM (Llama 4 Scout)
    3. Builds structured UI Schema
    4. Detects user flows
    5. Generates enterprise test cases via LLM (gpt-oss-120b)
    6. Validates coverage and quality
    """
    # ── Parse URLs ────────────────────────────────────────
    import re
    design_urls = []
    if design_url and design_url.strip():
        u = design_url.strip()
        if not u.startswith("http"):
            u = "https://" + u
        url_pattern = re.compile(r"^(https?://)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$")
        if not url_pattern.match(u):
            raise HTTPException(status_code=400, detail=f"Invalid URL format: {u}")
        design_urls.append(u)

    # ── Collect all upload files ──────────────────────────
    all_files: List[UploadFile] = []
    if file:
        all_files.append(file)

    # ── Validate: at least one input required ─────────────
    if not all_files and not design_urls and not (design_text and design_text.strip()):
        raise HTTPException(
            status_code=400,
            detail="At least one input is required: text, file, image, or URL.",
        )

    # ── Validate requirement_id (if provided) ─────────────
    if requirement_id:
        req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        if not req:
            raise HTTPException(status_code=404, detail=f"Requirement #{requirement_id} not found")

    # ── Create design folder ─────────────────────────────
    design_folder = create_design_folder(module_name="Design_Analysis")

    # ── Validate & save files ─────────────────────────────
    saved_file_names = []
    saved_file_paths = []

    for f in all_files:
        ext = _validate_file(f)

        # Safe filename
        safe_name = f.filename.replace("..", "_").replace("/", "_").replace("\\", "_")
        dest_path = os.path.join(design_folder, safe_name)

        try:
            contents = await f.read()
            if len(contents) > _MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{f.filename}' exceeds {_MAX_FILE_SIZE_MB}MB limit",
                )
            with open(dest_path, "wb") as out:
                out.write(contents)
            saved_file_names.append(safe_name)
            saved_file_paths.append(dest_path)
            logger.info("Saved design file: %s → %s", f.filename, dest_path)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to save file %s: %s", f.filename, e)
            raise HTTPException(status_code=500, detail=f"Failed to save file '{f.filename}': {str(e)}")

    # ── Save design URLs ──────────────────────────────────
    if design_urls:
        save_design_links(design_folder, design_urls)

    # ═══════════════════════════════════════════════════════
    # ENTERPRISE DESIGN INTELLIGENCE ENGINE
    # ═══════════════════════════════════════════════════════
    try:
        from app.services.design_intelligence_engine import analyze_design_intelligent

        intelligence_result = await analyze_design_intelligent(
            file_paths=saved_file_paths,
            urls=design_urls,
            design_text=design_text if design_text and design_text.strip() else None,
            output_dir=design_folder,
        )

        source_type = intelligence_result.get("source_type", "unknown")
        total_pages = intelligence_result.get("total_pages_analyzed", 0)
        total_components = intelligence_result.get("total_ui_components_detected", 0)
        total_flows = intelligence_result.get("total_flows_detected", 0)
        total_tests = intelligence_result.get("total_test_cases_generated", 0)
        coverage_pct = intelligence_result.get("enterprise_coverage_percentage", 0.0)
        analysis_summary = intelligence_result.get("analysis_summary", "")
        ui_schema = intelligence_result.get("ui_schema", {})
        detected_flows = intelligence_result.get("detected_flows", {})
        test_result = intelligence_result.get("test_generation_result", {})
        test_cases = test_result.get("test_cases", [])
        coverage = test_result.get("coverage", {})
        modules_grouped = test_result.get("modules_grouped", {})

    except Exception as e:
        logger.error("Design Intelligence Engine failed: %s", e)
        logger.error("Full traceback:\n%s", traceback.format_exc())
        # Graceful fallback — still store the upload even if LLM fails
        source_type = "unknown"
        total_pages = 0
        total_components = 0
        total_flows = 0
        total_tests = 0
        coverage_pct = 0.0
        analysis_summary = f"Intelligence engine encountered an error: {str(e)}"
        ui_schema = {}
        detected_flows = {}
        test_cases = []
        coverage = {}
        modules_grouped = {}

    # ── Save test cases to folder ─────────────────────────
    if test_cases:
        try:
            tc_file_path = os.path.join(design_folder, "enterprise_test_cases.json")
            with open(tc_file_path, "w", encoding="utf-8") as f:
                json.dump(test_cases, f, indent=2, default=str)
            logger.info("Saved %d enterprise test cases to %s", len(test_cases), tc_file_path)
        except Exception as e:
            logger.warning("Could not save test cases JSON: %s", e)

    # ── Build legacy analysis for backward compat ─────────
    legacy_analysis = {
        "modules": [m.get("module_name", "Unknown") for m in ui_schema.get("modules", [])],
        "module_count": ui_schema.get("total_modules", 0),
        "integrations": [],
        "integration_count": 0,
        "classification": {
            "ui_score": total_components,
            "api_score": 0,
            "system_score": 0,
            "primary_type": "UI-Focused",
        },
        "design_sources": {
            "files": saved_file_names,
            "urls": design_urls,
        },
        "summary": analysis_summary,
    }

    # ── Store metadata in database ────────────────────────
    try:
        design_doc = DesignDocument(
            requirement_id=requirement_id,
            file_names=json.dumps(saved_file_names),
            file_paths=json.dumps(saved_file_paths),
            design_urls=json.dumps(design_urls),
            analysis_result=json.dumps(legacy_analysis),
            folder_path=design_folder,
            ui_schema=json.dumps(ui_schema, default=str),
            detected_flows=json.dumps(detected_flows, default=str),
            coverage_percentage=coverage_pct,
            total_components=total_components,
            total_pages=total_pages,
            source_type=source_type,
        )
        db.add(design_doc)
        db.commit()
        db.refresh(design_doc)
    except Exception as e:
        logger.error("DB commit failed: %s", e)
        logger.error("Full traceback:\n%s", traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    logger.info(
        "Design uploaded: id=%d, req_id=%s, files=%d, urls=%d, tests=%d, coverage=%.1f%%",
        design_doc.id, requirement_id, len(saved_file_names), len(design_urls),
        total_tests, coverage_pct,
    )

    # ── Build response ────────────────────────────────────
    file_count = len(saved_file_names)
    url_count = len(design_urls)
    msg_parts = []
    if file_count:
        msg_parts.append(f"{file_count} file(s) uploaded")
    if url_count:
        msg_parts.append(f"{url_count} URL(s) linked")
    if total_tests > 0:
        msg_parts.append(f"{total_tests} enterprise test cases generated")
    message = " and ".join(msg_parts) + " successfully." if msg_parts else "Design processed."

    try:
        return EnterpriseDesignUploadResponse(
            design_id=design_doc.id,
            requirement_id=requirement_id,
            uploaded_files=saved_file_names,
            design_urls=design_urls,
            folder_path=design_folder,
            source_type=source_type,
            message=message,
            total_pages_analyzed=total_pages,
            total_ui_components_detected=total_components,
            total_flows_detected=total_flows,
            total_test_cases_generated=total_tests,
            enterprise_coverage_percentage=coverage_pct,
            analysis_summary=analysis_summary,
            ui_schema=ui_schema,
            detected_flows=detected_flows,
            coverage=coverage,
            test_cases=test_cases,
            modules_grouped_test_cases=modules_grouped,
            analysis=legacy_analysis,
        )
    except Exception as e:
        logger.error("Response serialization failed: %s", e)
        logger.error("Full traceback:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Response error: {str(e)}")


@router.get("/{design_id}")
def get_design_document(design_id: int, db: Session = Depends(get_db)):
    """Retrieve a single design document by ID."""
    doc = db.query(DesignDocument).filter(DesignDocument.id == design_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Design document not found")

    return {
        "id": doc.id,
        "requirement_id": doc.requirement_id,
        "file_names": json.loads(doc.file_names) if doc.file_names else [],
        "design_urls": json.loads(doc.design_urls) if doc.design_urls else [],
        "folder_path": doc.folder_path,
        "analysis": json.loads(doc.analysis_result) if doc.analysis_result else None,
        "ui_schema": json.loads(doc.ui_schema) if doc.ui_schema else None,
        "detected_flows": json.loads(doc.detected_flows) if doc.detected_flows else None,
        "coverage_percentage": doc.coverage_percentage,
        "total_components": doc.total_components,
        "total_pages": doc.total_pages,
        "source_type": doc.source_type,
        "created_at": doc.created_at,
    }


@router.get("/by-requirement/{req_id}")
def list_designs_for_requirement(req_id: int, db: Session = Depends(get_db)):
    """List all design documents for a specific requirement."""
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    docs = db.query(DesignDocument).filter(DesignDocument.requirement_id == req_id).all()
    return [
        {
            "id": doc.id,
            "requirement_id": doc.requirement_id,
            "file_names": json.loads(doc.file_names) if doc.file_names else [],
            "design_urls": json.loads(doc.design_urls) if doc.design_urls else [],
            "folder_path": doc.folder_path,
            "analysis": json.loads(doc.analysis_result) if doc.analysis_result else None,
            "source_type": doc.source_type,
            "total_components": doc.total_components,
            "coverage_percentage": doc.coverage_percentage,
            "created_at": doc.created_at,
        }
        for doc in docs
    ]
