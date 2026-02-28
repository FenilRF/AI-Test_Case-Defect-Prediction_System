"""
Unit Tests — API Integration Tests
--------------------------------------
Tests for FastAPI endpoints via TestClient.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


class TestHealthEndpoints:
    """Health check endpoint tests."""

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200


class TestRequirementsAPI:
    """Requirement CRUD endpoint tests."""

    def test_create_requirement(self, client):
        response = client.post("/api/requirements", json={"text": "Users should be able to login with email and password."})
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Users should be able to login with email and password."
        assert "id" in data

    def test_list_requirements(self, client):
        client.post("/api/requirements", json={"text": "Test requirement 1"})
        client.post("/api/requirements", json={"text": "Test requirement 2"})
        response = client.get("/api/requirements")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_requirement_not_found(self, client):
        response = client.get("/api/requirements/999")
        assert response.status_code == 404


class TestTestCaseGeneration:
    """Test case generation endpoint tests."""

    def test_generate_testcases(self, client):
        response = client.post("/api/generate-testcases", json={
            "requirement_text": "Users should be able to login with email and password. Email must be in valid format and password is required."
        })
        assert response.status_code == 200
        data = response.json()
        assert "requirement_id" in data
        assert "parsed" in data
        assert "test_cases" in data
        assert len(data["test_cases"]) > 0

    def test_generated_testcases_have_types(self, client):
        response = client.post("/api/generate-testcases", json={
            "requirement_text": "The system shall allow users to register with name, email, and password. All fields are required."
        })
        data = response.json()
        types = {tc["test_type"] for tc in data["test_cases"]}
        assert "positive" in types
        assert "negative" in types
        assert "security" in types

    def test_list_test_cases(self, client):
        # Generate first
        client.post("/api/generate-testcases", json={
            "requirement_text": "Login with email and password."
        })
        response = client.get("/api/test-cases")
        assert response.status_code == 200
        assert len(response.json()) > 0


class TestDefectPredictionAPI:
    """Defect prediction endpoint tests."""

    def test_predict_defect(self, client):
        response = client.post("/api/predict-defect", json={
            "module_name": "Payment",
            "lines_of_code": 4200,
            "complexity_score": 42.0,
            "past_defects": 18,
            "code_churn": 250,
        })
        assert response.status_code == 200
        data = response.json()
        assert "defect_probability" in data
        assert "risk_level" in data
        assert data["module_name"] == "Payment"

    def test_prediction_stored(self, client):
        client.post("/api/predict-defect", json={
            "module_name": "Auth",
            "lines_of_code": 3000,
            "complexity_score": 30.0,
            "past_defects": 10,
            "code_churn": 150,
        })
        response = client.get("/api/predictions")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestDashboardAPI:
    """Dashboard stats endpoint tests."""

    def test_dashboard_stats(self, client):
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requirements" in data
        assert "total_test_cases" in data
        assert "total_predictions" in data


class TestExportEndpoints:
    """CSV and JSON export endpoint tests."""

    def test_export_csv(self, client):
        # Generate some test cases first
        client.post("/api/generate-testcases", json={
            "requirement_text": "Login with email and password."
        })
        response = client.get("/api/test-cases/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    def test_export_json(self, client):
        client.post("/api/generate-testcases", json={
            "requirement_text": "Login with email and password."
        })
        response = client.get("/api/test-cases/export/json")
        assert response.status_code == 200
        data = response.json()
        assert "test_cases" in data
