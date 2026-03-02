"""
Complexity Scorer Service
---------------------------
Assigns a complexity score (1–5) to each test case based on:
  1 → Basic validation (single field, positive test)
  2 → Field-level negative (missing/invalid single field)
  3 → Multi-step flow (state transition, workflow)
  4 → Integration flow (API + DB, cross-module)
  5 → Edge + system interaction (concurrency, security, performance)
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Keyword → minimum complexity
_LEVEL_5_KEYWORDS = {
    "concurrent", "race condition", "deadlock", "performance", "load",
    "stress", "injection", "xss", "csrf", "encryption", "ssl",
    "system crash", "recovery", "data corruption", "memory leak",
}

_LEVEL_4_KEYWORDS = {
    "integration", "api", "database", "cross-module", "service",
    "external", "third-party", "authentication", "authorization",
    "token", "session", "middleware", "retry", "timeout",
    "webhook", "gateway", "queue", "kafka", "redis",
}

_LEVEL_3_KEYWORDS = {
    "workflow", "state transition", "multi-step", "end-to-end",
    "status change", "approval", "rejection", "lifecycle",
    "sequence", "chain", "pipeline", "batch", "process flow",
    "role-based", "permission", "admin", "user journey",
}


def score_complexity(test_case: Dict[str, Any]) -> int:
    """
    Compute complexity score (1–5) for a test case.

    Uses test_type, scenario text, and test_level as signals.
    """
    scenario_lower = test_case.get("scenario", "").lower()
    test_type = test_case.get("test_type", "").lower()
    test_level = test_case.get("test_level", "Unit").lower()

    # Start with base score from test_type
    if test_type == "security":
        score = 4
    elif test_type == "edge":
        score = 3
    elif test_type == "boundary":
        score = 2
    elif test_type == "negative":
        score = 2
    else:
        score = 1  # positive

    # Elevate based on keyword detection
    if any(kw in scenario_lower for kw in _LEVEL_5_KEYWORDS):
        score = max(score, 5)
    elif any(kw in scenario_lower for kw in _LEVEL_4_KEYWORDS):
        score = max(score, 4)
    elif any(kw in scenario_lower for kw in _LEVEL_3_KEYWORDS):
        score = max(score, 3)

    # Elevate based on test_level
    level_boost = {
        "unit": 0,
        "integration": 1,
        "system": 2,
        "uat": 1,
    }
    score = min(score + level_boost.get(test_level, 0), 5)

    return score


def score_batch(test_cases: list) -> list:
    """Score all test cases in a batch and attach complexity_score field."""
    for tc in test_cases:
        tc["complexity_score"] = score_complexity(tc)
    logger.info("Scored %d test cases for complexity", len(test_cases))
    return test_cases
