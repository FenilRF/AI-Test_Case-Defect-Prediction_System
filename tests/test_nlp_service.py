"""
Unit Tests — NLP Service
--------------------------
Tests for the requirement parsing engine:
  • Module name extraction
  • Action detection
  • Field detection
  • Validation keyword detection
  • Edge cases (empty/minimal input)
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.nlp_service import parse_requirement
from app.schemas.schemas import ParsedRequirement


class TestParseRequirement:
    """Suite for parse_requirement()."""

    def test_login_requirement(self):
        """Login requirement should detect Login module, login action, email & password fields."""
        text = "The system shall allow users to login using their email and password."
        result = parse_requirement(text)

        assert isinstance(result, ParsedRequirement)
        assert result.module == "Login"
        assert "login" in result.actions
        assert "email" in result.fields
        assert "password" in result.fields

    def test_registration_requirement(self):
        """Registration text should detect related module and fields."""
        text = "Users should be able to register by providing name, email, and phone number. All fields are required."
        result = parse_requirement(text)

        assert result.module == "Registration"
        assert "register" in result.actions
        assert "email" in result.fields
        assert "name" in result.fields
        assert "required" in result.validations

    def test_payment_requirement(self):
        """Payment requirement should detect Payment module and amount field."""
        text = "The payment module should allow users to transfer an amount from their account."
        result = parse_requirement(text)

        assert result.module == "Payment"
        assert "transfer" in result.actions
        assert "amount" in result.fields

    def test_validations_detected(self):
        """Validation keywords should be extracted correctly."""
        text = "Email must be in valid format. Password is required with minimum length of 8 characters."
        result = parse_requirement(text)

        assert "required" in result.validations
        assert "format" in result.validations

    def test_multiple_actions(self):
        """Multiple actions in one requirement should all be detected."""
        text = "Administrators can create, update, and delete products."
        result = parse_requirement(text)

        assert "create" in result.actions
        assert "update" in result.actions
        assert "delete" in result.actions

    def test_minimal_input(self):
        """Even minimal text should return valid parsed result with defaults."""
        text = "something simple"
        result = parse_requirement(text)

        assert isinstance(result, ParsedRequirement)
        assert len(result.actions) > 0  # should have fallback
        assert len(result.fields) > 0   # should have fallback

    def test_search_module(self):
        """Search-related text should map to Search module."""
        text = "Users should be able to search for products by name."
        result = parse_requirement(text)

        assert result.module == "Search"
        assert "search" in result.actions

    def test_security_keywords(self):
        """Requirement with upload/file keywords should detect File Management."""
        text = "The system should allow users to upload documents and images."
        result = parse_requirement(text)

        assert result.module == "File Management"
        assert "upload" in result.actions
