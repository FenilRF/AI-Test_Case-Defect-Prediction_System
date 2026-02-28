"""
Unit Tests — Test Case Generator
-----------------------------------
Tests for the test case generation engine:
  • Generates all 5 types of test cases
  • Each test case has required fields
  • Correct module name propagation
  • Sequential ID assignment
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.test_case_generator import generate_test_cases
from app.schemas.schemas import ParsedRequirement


@pytest.fixture
def sample_parsed():
    """Sample ParsedRequirement for testing."""
    return ParsedRequirement(
        module="Login",
        actions=["login"],
        fields=["email", "password"],
        validations=["required", "format"],
    )


@pytest.fixture
def complex_parsed():
    """ParsedRequirement with multiple actions and fields."""
    return ParsedRequirement(
        module="Order Management",
        actions=["create", "update", "delete"],
        fields=["order id", "amount", "status"],
        validations=["required", "positive", "unique"],
    )


class TestGenerateTestCases:

    def test_returns_list(self, sample_parsed):
        """Should return a non-empty list of test cases."""
        result = generate_test_cases(sample_parsed)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_all_types_present(self, sample_parsed):
        """All 5 test types should be present in the output."""
        result = generate_test_cases(sample_parsed)
        types = {tc["test_type"] for tc in result}
        expected_types = {"positive", "negative", "boundary", "edge", "security"}
        assert expected_types == types

    def test_required_fields(self, sample_parsed):
        """Each test case must have all required fields."""
        result = generate_test_cases(sample_parsed)
        required_keys = {"test_id", "module_name", "scenario", "test_type", "expected_result", "priority"}

        for tc in result:
            assert required_keys.issubset(tc.keys()), f"Missing keys in test case: {required_keys - tc.keys()}"

    def test_sequential_ids(self, sample_parsed):
        """Test IDs should be sequential starting from 1."""
        result = generate_test_cases(sample_parsed)
        ids = [tc["test_id"] for tc in result]
        assert ids == list(range(1, len(result) + 1))

    def test_module_name_propagation(self, sample_parsed):
        """All test cases should use the module name from the parsed requirement."""
        result = generate_test_cases(sample_parsed)
        for tc in result:
            assert tc["module_name"] == "Login"

    def test_priority_values(self, sample_parsed):
        """Priorities should be one of P1, P2, P3."""
        result = generate_test_cases(sample_parsed)
        valid_priorities = {"P1", "P2", "P3"}
        for tc in result:
            assert tc["priority"] in valid_priorities

    def test_positive_cases_generated(self, sample_parsed):
        """Should generate positive test cases for action+field combinations."""
        result = generate_test_cases(sample_parsed)
        positive = [tc for tc in result if tc["test_type"] == "positive"]
        assert len(positive) >= 2  # at least one per field + general

    def test_negative_cases_generated(self, sample_parsed):
        """Should generate negative test cases (missing, empty, invalid) per field."""
        result = generate_test_cases(sample_parsed)
        negative = [tc for tc in result if tc["test_type"] == "negative"]
        # 3 negative cases per field (missing, empty, invalid format)
        assert len(negative) >= len(sample_parsed.fields) * 3

    def test_security_cases_generated(self, sample_parsed):
        """Should generate SQL injection and XSS test cases per field."""
        result = generate_test_cases(sample_parsed)
        security = [tc for tc in result if tc["test_type"] == "security"]
        assert len(security) >= len(sample_parsed.fields) * 2  # SQLi + XSS per field

    def test_complex_requirement(self, complex_parsed):
        """Complex requirement should generate more test cases."""
        result = generate_test_cases(complex_parsed)
        assert len(result) > 20  # multiple actions × fields

    def test_scenario_not_empty(self, sample_parsed):
        """No test case should have an empty scenario."""
        result = generate_test_cases(sample_parsed)
        for tc in result:
            assert len(tc["scenario"]) > 0
            assert len(tc["expected_result"]) > 0
