"""
Test Case Generation Engine
------------------------------
Generates comprehensive test cases from a ParsedRequirement:
  • Positive     — happy-path scenarios
  • Negative     — invalid / missing data
  • Boundary     — min/max limits
  • Edge         — unusual but valid conditions
  • Security     — basic SQL injection & XSS probes

Each test case includes: test_id, module_name, scenario,
test_type, expected_result, priority.
"""

import logging
from typing import List, Dict, Any

from app.schemas.schemas import ParsedRequirement

logger = logging.getLogger(__name__)


def _priority_for(test_type: str) -> str:
    """Assign default priority based on test type."""
    mapping = {
        "positive": "P2",
        "negative": "P1",
        "boundary": "P2",
        "edge": "P3",
        "security": "P1",
    }
    return mapping.get(test_type, "P3")


# ── Multi-Level Test Classification ──────────────────────────
# Classifies each test case into: Unit, Integration, System, UAT

_INTEGRATION_KEYWORDS = {
    "concurrent", "idempotency", "duplicate", "api", "service",
    "database", "connect", "integration", "endpoint", "request",
    "response", "session", "authentication", "authorisation",
    "authorization", "token", "middleware",
}

_SYSTEM_KEYWORDS = {
    "security", "injection", "xss", "permission", "role",
    "performance", "load", "stress", "timeout", "crash",
    "recovery", "backup", "ssl", "https", "encrypt",
}

_UAT_KEYWORDS = {
    "user", "workflow", "end-to-end", "acceptance", "scenario",
    "business", "requirement", "valid inputs", "all valid",
}


def _classify_test_level(test_type: str, scenario: str) -> str:
    """
    Classify a test case into one of four levels:
      Unit         — isolated field-level validations
      Integration  — cross-component / API-level interactions
      System       — security, performance, system-wide checks
      UAT          — end-to-end user acceptance scenarios
    """
    scenario_lower = scenario.lower()

    # Security tests are always system-level
    if test_type == "security":
        return "System"

    # Check for system-level keywords
    if any(kw in scenario_lower for kw in _SYSTEM_KEYWORDS):
        return "System"

    # Check for integration-level keywords
    if any(kw in scenario_lower for kw in _INTEGRATION_KEYWORDS):
        return "Integration"

    # Positive tests with "all valid inputs" are UAT-level
    if test_type == "positive" and any(kw in scenario_lower for kw in _UAT_KEYWORDS):
        return "UAT"

    # Edge cases involving concurrency / idempotency → Integration
    if test_type == "edge":
        return "Integration"

    # Default: field-level validations are Unit tests
    return "Unit"


def _generate_positive_cases(parsed: ParsedRequirement) -> List[Dict[str, Any]]:
    """Happy-path test cases for every action × field combination."""
    cases: List[Dict[str, Any]] = []
    for action in parsed.actions:
        for field in parsed.fields:
            cases.append({
                "module_name": parsed.module,
                "scenario": f"Verify that {action} succeeds with valid {field}",
                "test_type": "positive",
                "expected_result": f"{action.capitalize()} operation completes successfully with valid {field}",
                "priority": _priority_for("positive"),
            })
        # General positive case per action
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify {action} operation with all valid inputs",
            "test_type": "positive",
            "expected_result": f"{action.capitalize()} completes and returns success response",
            "priority": _priority_for("positive"),
        })
    return cases


def _generate_negative_cases(parsed: ParsedRequirement) -> List[Dict[str, Any]]:
    """Test cases for missing, empty, and invalid inputs."""
    cases: List[Dict[str, Any]] = []
    for field in parsed.fields:
        # Missing field
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify error when {field} is missing",
            "test_type": "negative",
            "expected_result": f"System returns validation error indicating {field} is required",
            "priority": _priority_for("negative"),
        })
        # Empty field
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify error when {field} is empty",
            "test_type": "negative",
            "expected_result": f"System rejects empty {field} with appropriate error message",
            "priority": _priority_for("negative"),
        })
        # Invalid format
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify error when {field} has invalid format",
            "test_type": "negative",
            "expected_result": f"System rejects invalid {field} format and shows format hint",
            "priority": _priority_for("negative"),
        })
    return cases


def _generate_boundary_cases(parsed: ParsedRequirement) -> List[Dict[str, Any]]:
    """Boundary value analysis for fields with length / size constraints."""
    cases: List[Dict[str, Any]] = []
    for field in parsed.fields:
        cases.extend([
            {
                "module_name": parsed.module,
                "scenario": f"Verify {field} at minimum allowed length (1 character)",
                "test_type": "boundary",
                "expected_result": f"System accepts {field} at minimum boundary",
                "priority": _priority_for("boundary"),
            },
            {
                "module_name": parsed.module,
                "scenario": f"Verify {field} at maximum allowed length",
                "test_type": "boundary",
                "expected_result": f"System accepts {field} at maximum boundary",
                "priority": _priority_for("boundary"),
            },
            {
                "module_name": parsed.module,
                "scenario": f"Verify {field} exceeding maximum allowed length",
                "test_type": "boundary",
                "expected_result": f"System rejects {field} exceeding maximum length with error",
                "priority": _priority_for("boundary"),
            },
        ])
    return cases


def _generate_edge_cases(parsed: ParsedRequirement) -> List[Dict[str, Any]]:
    """Edge / corner cases — unusual but technically valid inputs."""
    cases: List[Dict[str, Any]] = []
    for field in parsed.fields:
        cases.extend([
            {
                "module_name": parsed.module,
                "scenario": f"Verify {field} with only whitespace characters",
                "test_type": "edge",
                "expected_result": f"System trims whitespace and validates {field} correctly",
                "priority": _priority_for("edge"),
            },
            {
                "module_name": parsed.module,
                "scenario": f"Verify {field} with Unicode / special characters",
                "test_type": "edge",
                "expected_result": f"System handles Unicode in {field} without crashing",
                "priority": _priority_for("edge"),
            },
        ])

    for action in parsed.actions:
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify duplicate {action} request handling (idempotency)",
            "test_type": "edge",
            "expected_result": f"System handles duplicate {action} gracefully without data corruption",
            "priority": _priority_for("edge"),
        })
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify {action} under concurrent access",
            "test_type": "edge",
            "expected_result": f"System maintains data integrity during concurrent {action} operations",
            "priority": _priority_for("edge"),
        })
    return cases


def _generate_security_cases(parsed: ParsedRequirement) -> List[Dict[str, Any]]:
    """Basic security test cases — SQL injection & XSS probes."""
    cases: List[Dict[str, Any]] = []
    for field in parsed.fields:
        cases.extend([
            {
                "module_name": parsed.module,
                "scenario": f"Verify SQL injection attempt in {field} — input: ' OR '1'='1",
                "test_type": "security",
                "expected_result": f"System sanitises input and rejects SQL injection in {field}",
                "priority": _priority_for("security"),
            },
            {
                "module_name": parsed.module,
                "scenario": f"Verify XSS attempt in {field} — input: <script>alert('xss')</script>",
                "test_type": "security",
                "expected_result": f"System sanitises HTML/JS and prevents XSS via {field}",
                "priority": _priority_for("security"),
            },
        ])

    for action in parsed.actions:
        cases.append({
            "module_name": parsed.module,
            "scenario": f"Verify {action} is not accessible without authentication",
            "test_type": "security",
            "expected_result": f"System returns 401/403 for unauthenticated {action} attempt",
            "priority": _priority_for("security"),
        })
    return cases


def generate_test_cases(parsed: ParsedRequirement) -> List[Dict[str, Any]]:
    """
    Master generator — orchestrates all sub-generators and assigns sequential IDs.

    Parameters
    ----------
    parsed : ParsedRequirement
        Structured requirement from the NLP service.

    Returns
    -------
    list[dict]
        Complete list of test cases ready for DB insertion.
    """
    logger.info("Generating test cases for module: %s", parsed.module)

    all_cases: List[Dict[str, Any]] = []
    all_cases.extend(_generate_positive_cases(parsed))
    all_cases.extend(_generate_negative_cases(parsed))
    all_cases.extend(_generate_boundary_cases(parsed))
    all_cases.extend(_generate_edge_cases(parsed))
    all_cases.extend(_generate_security_cases(parsed))

    # Assign sequential test IDs and classify test level
    for idx, case in enumerate(all_cases, start=1):
        case["test_id"] = idx
        case["test_level"] = _classify_test_level(case["test_type"], case["scenario"])

    logger.info("Generated %d test cases for module '%s'", len(all_cases), parsed.module)
    return all_cases

