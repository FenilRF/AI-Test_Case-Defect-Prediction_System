"""
Unit Tests — Defect Prediction Service
-----------------------------------------
Tests for defect prediction, risk classification, and priority mapping.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.defect_prediction_service import (
    classify_risk,
    risk_to_priority,
    predict,
    _fallback_heuristic,
)
from app.schemas.schemas import DefectPredictionRequest, DefectPredictionResponse


class TestClassifyRisk:
    """Tests for risk-level classification from probability."""

    def test_high_risk_at_boundary(self):
        assert classify_risk(0.7) == "High"

    def test_high_risk_above_boundary(self):
        assert classify_risk(0.9) == "High"

    def test_medium_risk_at_boundary(self):
        assert classify_risk(0.4) == "Medium"

    def test_medium_risk_mid(self):
        assert classify_risk(0.55) == "Medium"

    def test_low_risk(self):
        assert classify_risk(0.2) == "Low"

    def test_low_risk_zero(self):
        assert classify_risk(0.0) == "Low"

    def test_high_risk_max(self):
        assert classify_risk(1.0) == "High"

    def test_boundary_0_39(self):
        assert classify_risk(0.39) == "Low"

    def test_boundary_0_69(self):
        assert classify_risk(0.69) == "Medium"


class TestRiskToPriority:
    """Tests for risk → QA priority mapping."""

    def test_high_to_p1(self):
        assert risk_to_priority("High") == "P1"

    def test_medium_to_p2(self):
        assert risk_to_priority("Medium") == "P2"

    def test_low_to_p3(self):
        assert risk_to_priority("Low") == "P3"

    def test_unknown_defaults_p3(self):
        assert risk_to_priority("Unknown") == "P3"


class TestFallbackHeuristic:
    """Tests for the fallback prediction heuristic (used when no model is loaded)."""

    def test_low_risk_module(self):
        req = DefectPredictionRequest(
            module_name="Settings",
            lines_of_code=600,
            complexity_score=5,
            past_defects=0,
            code_churn=15,
        )
        score = _fallback_heuristic(req)
        assert 0 <= score <= 1
        assert classify_risk(score) == "Low"

    def test_high_risk_module(self):
        req = DefectPredictionRequest(
            module_name="Payment",
            lines_of_code=4200,
            complexity_score=42,
            past_defects=18,
            code_churn=250,
        )
        score = _fallback_heuristic(req)
        assert 0 <= score <= 1
        assert classify_risk(score) == "High"

    def test_medium_risk_module(self):
        req = DefectPredictionRequest(
            module_name="UserProfile",
            lines_of_code=2000,
            complexity_score=20,
            past_defects=5,
            code_churn=80,
        )
        score = _fallback_heuristic(req)
        assert 0 <= score <= 1


class TestPredictFunction:
    """Integration-level tests for the predict() function."""

    def test_returns_response_model(self):
        req = DefectPredictionRequest(
            module_name="TestModule",
            lines_of_code=1000,
            complexity_score=15,
            past_defects=3,
            code_churn=50,
        )
        result = predict(req)

        assert isinstance(result, DefectPredictionResponse)
        assert result.module_name == "TestModule"
        assert 0 <= result.defect_probability <= 1
        assert result.risk_level in {"Low", "Medium", "High"}

    def test_consistent_risk_and_probability(self):
        req = DefectPredictionRequest(
            module_name="BigModule",
            lines_of_code=5000,
            complexity_score=50,
            past_defects=20,
            code_churn=300,
        )
        result = predict(req)
        expected_risk = classify_risk(result.defect_probability)
        assert result.risk_level == expected_risk
