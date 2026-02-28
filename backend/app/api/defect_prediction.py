"""
API Routes — Defect Prediction
---------------------------------
Endpoints:
  POST /api/predict-defect           → predict defect probability for a module
  GET  /api/predictions              → list stored predictions
  POST /api/defect-data              → add training data record
  GET  /api/defect-data              → list training data
  GET  /api/dashboard/stats          → aggregated dashboard stats
  POST /api/model/reload             → force model reload after retraining
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import get_db
from app.models.models import DefectData, Prediction, Requirement, TestCase
from app.schemas.schemas import (
    DefectPredictionRequest,
    DefectPredictionResponse,
    DefectDataCreate,
    DefectDataResponse,
    PredictionHistoryResponse,
    DashboardStats,
)
from app.services.defect_prediction_service import predict, reload_model

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Defect Prediction"])


# ── Defect Prediction ─────────────────────────────────────────

@router.post("/predict-defect", response_model=DefectPredictionResponse)
def predict_defect(payload: DefectPredictionRequest, db: Session = Depends(get_db)):
    """
    Predict defect probability for the given module metrics.
    Stores the result in the predictions table.
    """
    result = predict(payload)

    # Persist prediction
    pred = Prediction(
        module_name=result.module_name,
        probability=result.defect_probability,
        risk_level=result.risk_level,
        defect_category=result.defect_category,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    logger.info("Prediction stored: id=%d, module=%s", pred.id, pred.module_name)
    return result


@router.get("/predictions", response_model=list[PredictionHistoryResponse])
def list_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all stored prediction results."""
    return (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── Defect Data (Training Data) CRUD ──────────────────────────

@router.post("/defect-data", response_model=DefectDataResponse, status_code=201)
def add_defect_data(payload: DefectDataCreate, db: Session = Depends(get_db)):
    """Add a module metrics record (for ML training)."""
    record = DefectData(
        module_name=payload.module_name,
        lines_of_code=payload.lines_of_code,
        complexity_score=payload.complexity_score,
        past_defects=payload.past_defects,
        code_churn=payload.code_churn,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/defect-data", response_model=list[DefectDataResponse])
def list_defect_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List module-level training data."""
    return db.query(DefectData).offset(skip).limit(limit).all()


# ── Dashboard Aggregation ─────────────────────────────────────

@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    """Return high-level statistics for the frontend dashboard."""
    total_requirements = db.query(func.count(Requirement.id)).scalar() or 0
    total_test_cases = db.query(func.count(TestCase.id)).scalar() or 0
    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0

    high_risk = (
        db.query(func.count(Prediction.id))
        .filter(Prediction.risk_level == "High")
        .scalar() or 0
    )
    medium_risk = (
        db.query(func.count(Prediction.id))
        .filter(Prediction.risk_level == "Medium")
        .scalar() or 0
    )
    low_risk = (
        db.query(func.count(Prediction.id))
        .filter(Prediction.risk_level == "Low")
        .scalar() or 0
    )

    return DashboardStats(
        total_requirements=total_requirements,
        total_test_cases=total_test_cases,
        total_predictions=total_predictions,
        high_risk_modules=high_risk,
        medium_risk_modules=medium_risk,
        low_risk_modules=low_risk,
    )


# ── Model Management ──────────────────────────────────────────

@router.post("/model/reload")
def reload_prediction_model():
    """Force-reload the ML model from disk (e.g. after retraining)."""
    try:
        reload_model()
        return {"message": "Model reloaded successfully"}
    except Exception as e:
        logger.exception("Failed to reload model")
        raise HTTPException(status_code=500, detail=str(e))
