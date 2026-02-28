"""
Defect Prediction Service
---------------------------
Loads the trained Logistic Regression model and provides:
  • predict()          — single-module defect probability
  • classify_risk()    — map probability → risk level
  • risk_to_priority() — map risk level → QA priority
"""

import os
import logging
from typing import Optional

import numpy as np
import joblib

from app.config import get_settings
from app.schemas.schemas import DefectPredictionRequest, DefectPredictionResponse

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Model singleton ──────────────────────────────────────────
_model = None
_scaler = None


def _load_model():
    """Lazily load the trained model and scaler from disk."""
    global _model, _scaler

    model_path = os.path.join(settings.ML_MODEL_DIR, "defect_model.pkl")
    scaler_path = os.path.join(settings.ML_MODEL_DIR, "scaler.pkl")

    if os.path.exists(model_path):
        _model = joblib.load(model_path)
        logger.info("Loaded defect prediction model from %s", model_path)
    else:
        logger.warning("Model file not found at %s — using fallback heuristic", model_path)

    if os.path.exists(scaler_path):
        _scaler = joblib.load(scaler_path)
        logger.info("Loaded feature scaler from %s", scaler_path)
    else:
        logger.warning("Scaler file not found at %s", scaler_path)


def classify_risk(probability: float) -> str:
    """
    Map defect probability to a risk level.

    Risk thresholds
    ----------------
    0.0–0.4 → Low
    0.4–0.7 → Medium
    0.7–1.0 → High
    """
    if probability >= 0.7:
        return "High"
    elif probability >= 0.4:
        return "Medium"
    return "Low"


def risk_to_priority(risk_level: str) -> str:
    """
    Map risk level to QA priority label.

    High   → P1
    Medium → P2
    Low    → P3
    """
    mapping = {"High": "P1", "Medium": "P2", "Low": "P3"}
    return mapping.get(risk_level, "P3")


# ── Defect Risk Category Classification ───────────────────
# Maps module name + metrics into one of 6 defect categories:
#   UI Level, API Level, Integration Level,
#   Function Level, System Level, Non-functional Level

_CATEGORY_KEYWORDS = {
    "UI Level": {
        "ui", "frontend", "view", "page", "component", "form",
        "button", "layout", "template", "css", "style", "render",
        "display", "dashboard", "widget", "theme",
    },
    "API Level": {
        "api", "endpoint", "rest", "graphql", "controller",
        "route", "request", "response", "http", "webhook",
        "middleware", "gateway", "swagger",
    },
    "Integration Level": {
        "integration", "connector", "adapter", "bridge", "sync",
        "messaging", "queue", "kafka", "rabbitmq", "event",
        "external", "third-party", "plugin", "socket",
    },
    "System Level": {
        "system", "kernel", "os", "infra", "deploy", "docker",
        "server", "network", "cluster", "monitor", "logging",
        "config", "env", "scheduler", "cron",
    },
    "Non-functional Level": {
        "performance", "security", "auth", "encryption", "ssl",
        "cache", "scalability", "load", "stress", "compliance",
        "audit", "backup", "recovery", "resilience",
    },
}


def classify_defect_category(
    module_name: str,
    complexity_score: float = 0,
    past_defects: int = 0,
    combined_context: str = "",
) -> str:
    """Classify the most likely defect category for a module using text and heuristics."""
    name_lower = f"{module_name} {combined_context}".lower().replace("_", " ").replace("-", " ")

    # Score each category by keyword overlap
    best_category = "Function Level"
    best_score = 0

    for category, keywords in _CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in name_lower)
        if score > best_score:
            best_score = score
            best_category = category

    # If no keyword match, use metrics-based heuristic
    if best_score == 0:
        if complexity_score >= 40 and past_defects >= 15:
            best_category = "System Level"
        elif complexity_score >= 30:
            best_category = "Non-functional Level"
        elif past_defects >= 10:
            best_category = "Integration Level"
        else:
            best_category = "Function Level"

    return best_category


def _fallback_heuristic(req: DefectPredictionRequest) -> float:
    """
    Simple heuristic when no trained model is available.
    Combines normalised metrics into a 0–1 score.
    """
    loc_score = min(req.lines_of_code / 5000, 1.0) * 0.25
    complexity_score = min(req.complexity_score / 50, 1.0) * 0.30
    defect_score = min(req.past_defects / 20, 1.0) * 0.30
    churn_score = min(req.code_churn / 200, 1.0) * 0.15
    return round(loc_score + complexity_score + defect_score + churn_score, 4)


def predict(req: DefectPredictionRequest) -> DefectPredictionResponse:
    """
    Predict defect probability for a single module.

    Falls back to a heuristic if the ML model hasn't been trained yet.
    """
    global _model, _scaler

    # Lazy-load on first call
    if _model is None:
        _load_model()

    if _model is not None:
        features = np.array([[
            req.lines_of_code,
            req.complexity_score,
            req.past_defects,
            req.code_churn,
        ]])

        if _scaler is not None:
            features = _scaler.transform(features)

        # predict_proba returns [[prob_class_0, prob_class_1]]
        probability = float(_model.predict_proba(features)[0][1])
    else:
        probability = _fallback_heuristic(req)

    risk_level = classify_risk(probability)
    defect_category = classify_defect_category(
        req.module_name, req.complexity_score, req.past_defects,
        combined_context=f"{req.requirement_text or ''} {req.design_text or ''} {req.test_cases_text or ''}",
    )
    logger.info(
        "Prediction for %s: probability=%.4f, risk=%s, category=%s",
        req.module_name, probability, risk_level, defect_category,
    )

    return DefectPredictionResponse(
        module_name=req.module_name,
        defect_probability=round(probability, 4),
        risk_level=risk_level,
        defect_category=defect_category,
    )


def reload_model():
    """Force-reload the model (e.g. after retraining)."""
    global _model, _scaler
    _model = None
    _scaler = None
    _load_model()
