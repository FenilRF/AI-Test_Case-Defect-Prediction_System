"""
Enterprise Test Engine — Phase 3 + Phase 4 + Phase 5
--------------------------------------------------------
Phase 3: Exhaustive test scenario generation (13 categories)
Phase 4: Duplicate elimination
Phase 5: Coverage validation

Generates enterprise-grade test suites with NO LIMIT on count.
Optimises for 100% logical coverage, not brevity.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from app.services.requirement_decomposer import decompose_requirement

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════
# Priority Assignment
# ═══════════════════════════════════════════════════════

_PRIORITY_MAP = {
    "positive": "P2",
    "negative": "P1",
    "edge_case": "P3",
    "boundary_value": "P2",
    "security": "P1",
    "role_based": "P1",
    "state_transition": "P2",
    "api_ui_consistency": "P2",
    "integration_failure": "P1",
    "performance_stress": "P3",
    "data_corruption": "P1",
    "concurrency": "P2",
    "workflow_interruption": "P3",
}


def _priority_for(category: str) -> str:
    return _PRIORITY_MAP.get(category, "P3")


# ═══════════════════════════════════════════════════════
# Test Level Classification
# ═══════════════════════════════════════════════════════

_LEVEL_KEYWORDS = {
    "System": {
        "security", "injection", "xss", "csrf", "ssl", "tls", "encrypt",
        "permission", "privilege", "performance", "load", "stress",
        "throughput", "latency", "crash", "recovery", "backup",
        "vulnerability", "brute force", "ddos",
    },
    "Integration": {
        "api", "endpoint", "service", "database", "connect", "external",
        "third-party", "webhook", "integration", "timeout", "retry",
        "queue", "kafka", "redis", "socket", "concurrent",
        "idempotent", "race condition", "message", "sync",
    },
    "UAT": {
        "user workflow", "end-to-end", "acceptance", "business",
        "complete flow", "all valid", "full scenario",
        "user journey", "happy path",
    },
}


def _classify_level(test_type: str, scenario: str) -> str:
    scenario_lower = scenario.lower()
    if test_type in ("security", "performance_stress"):
        return "System"
    for level, keywords in _LEVEL_KEYWORDS.items():
        if any(kw in scenario_lower for kw in keywords):
            return level
    if test_type in ("integration_failure", "concurrency", "api_ui_consistency"):
        return "Integration"
    if test_type == "positive" and "all valid" in scenario_lower:
        return "UAT"
    return "Unit"


# ═══════════════════════════════════════════════════════
# Phase 3 — Scenario Generators (13 Categories)
# ═══════════════════════════════════════════════════════

def _gen_positive(module: Dict, module_name: str) -> List[Dict]:
    """Happy-path scenarios for every keyword."""
    cases = []
    keywords = module.get("matched_keywords", [])
    for kw in keywords:
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify {kw} operation succeeds with all valid inputs",
            "test_type": "positive",
            "expected_result": f"{kw.capitalize()} completes successfully and returns correct response",
        })
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify {kw} result is correctly persisted and retrievable",
            "test_type": "positive",
            "expected_result": f"Data from {kw} operation is stored and can be fetched accurately",
        })

    # Explicit rule scenarios
    for rule in module.get("explicit_rules", [])[:10]:
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify: {rule}",
            "test_type": "positive",
            "expected_result": f"System behaves as specified: {rule}",
        })
    return cases


def _gen_negative(module: Dict, module_name: str) -> List[Dict]:
    """Invalid, missing, rejected input scenarios."""
    cases = []
    keywords = module.get("matched_keywords", [])
    for kw in keywords[:8]:
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify {kw} fails when required fields are missing",
            "test_type": "negative",
            "expected_result": f"System returns validation error for missing fields during {kw}",
        })
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify {kw} rejects invalid data format",
            "test_type": "negative",
            "expected_result": f"System returns format error and does not process invalid {kw} request",
        })
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify {kw} returns appropriate error for unauthorized request",
            "test_type": "negative",
            "expected_result": f"System returns 401/403 for unauthorized {kw} attempt",
        })

    for neg in module.get("negative_paths", []):
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify: {neg}",
            "test_type": "negative",
            "expected_result": f"System handles gracefully: {neg}",
        })
    return cases


def _gen_edge_cases(module: Dict, module_name: str) -> List[Dict]:
    """Unusual but valid inputs."""
    cases = []
    keywords = module.get("matched_keywords", [])
    edge_inputs = [
        ("only whitespace characters", "trims whitespace or rejects empty input"),
        ("Unicode / non-ASCII characters", "handles Unicode without corruption"),
        ("extremely long input (10,000+ chars)", "rejects or truncates safely"),
        ("HTML/script tags in text fields", "sanitises and prevents rendering"),
        ("leading and trailing spaces", "trims and processes correctly"),
        ("null bytes in string input", "rejects or sanitises null bytes"),
        ("emoji characters in text fields", "handles emoji without crash or corruption"),
    ]
    for kw in keywords[:5]:
        for input_desc, expected in edge_inputs:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} with {input_desc}",
                "test_type": "edge_case",
                "expected_result": f"System {expected} during {kw}",
            })
    return cases


def _gen_boundary_value(module: Dict, module_name: str) -> List[Dict]:
    """Min/max/off-by-one boundary tests."""
    cases = []
    keywords = module.get("matched_keywords", [])
    boundaries = module.get("boundaries", [])

    for boundary in boundaries:
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify behavior at boundary: {boundary}",
            "test_type": "boundary_value",
            "expected_result": f"System correctly handles {boundary}",
        })

    for kw in keywords[:5]:
        cases.extend([
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} with minimum allowed input length (1 char)",
                "test_type": "boundary_value",
                "expected_result": f"System accepts minimum boundary for {kw}",
            },
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} with maximum allowed input length",
                "test_type": "boundary_value",
                "expected_result": f"System accepts maximum boundary for {kw}",
            },
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} with input exceeding maximum length by 1",
                "test_type": "boundary_value",
                "expected_result": f"System rejects over-maximum boundary for {kw}",
            },
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} with zero-length / empty input",
                "test_type": "boundary_value",
                "expected_result": f"System rejects empty input for {kw} with clear error",
            },
        ])
    return cases


def _gen_security(module: Dict, module_name: str) -> List[Dict]:
    """SQL injection, XSS, CSRF, auth bypass tests."""
    cases = []
    keywords = module.get("matched_keywords", [])
    security_vectors = [
        ("SQL injection via ' OR '1'='1", "sanitises SQL injection and returns error"),
        ("XSS via <script>alert('xss')</script>", "escapes HTML/JS and prevents XSS execution"),
        ("command injection via ; rm -rf /", "sanitises shell commands and rejects"),
        ("path traversal via ../../etc/passwd", "blocks path traversal attempts"),
        ("CSRF attack without valid token", "rejects request missing CSRF protection"),
        ("authentication bypass with forged JWT", "rejects invalid/forged authentication tokens"),
        ("privilege escalation to admin role", "denies escalation and logs the attempt"),
        ("brute-force with 100+ rapid requests", "rate-limits and blocks after threshold"),
    ]
    for kw in keywords[:4]:
        for attack, expected in security_vectors:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} is protected against {attack}",
                "test_type": "security",
                "expected_result": f"System {expected} on {kw}",
            })

    # Auth scenarios for all keywords
    for kw in keywords[:6]:
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify {kw} requires valid authentication",
            "test_type": "security",
            "expected_result": f"System returns 401 for unauthenticated {kw} request",
        })
    return cases


def _gen_role_based(module: Dict, module_name: str) -> List[Dict]:
    """Admin vs user vs guest permission tests."""
    cases = []
    keywords = module.get("matched_keywords", [])
    roles = ["admin", "authenticated user", "guest/anonymous user", "read-only user", "manager"]

    for kw in keywords[:5]:
        for role in roles:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} access as {role}",
                "test_type": "role_based",
                "expected_result": f"System enforces correct permissions for {role} attempting {kw}",
            })

    # Cross-role scenarios
    cases.append({
        "module_name": module_name,
        "scenario": "Verify user cannot access admin-only resources",
        "test_type": "role_based",
        "expected_result": "System returns 403 Forbidden for non-admin users",
    })
    cases.append({
        "module_name": module_name,
        "scenario": "Verify user cannot modify another user's data",
        "test_type": "role_based",
        "expected_result": "System prevents cross-user data modification with appropriate error",
    })
    return cases


def _gen_state_transition(module: Dict, module_name: str) -> List[Dict]:
    """Status lifecycle and workflow interrupts."""
    cases = []
    keywords = module.get("matched_keywords", [])

    state_pairs = [
        ("draft", "published"), ("pending", "approved"), ("pending", "rejected"),
        ("active", "inactive"), ("active", "suspended"), ("open", "closed"),
        ("in progress", "completed"), ("completed", "archived"),
    ]
    for from_state, to_state in state_pairs:
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify transition from '{from_state}' to '{to_state}' is allowed",
            "test_type": "state_transition",
            "expected_result": f"System transitions record from {from_state} to {to_state} and updates timestamp",
        })
        cases.append({
            "module_name": module_name,
            "scenario": f"Verify reverse transition from '{to_state}' back to '{from_state}' is handled",
            "test_type": "state_transition",
            "expected_result": f"System either allows reverse or rejects with clear error message",
        })

    # Invalid transitions
    cases.append({
        "module_name": module_name,
        "scenario": "Verify skipping required intermediate states is rejected",
        "test_type": "state_transition",
        "expected_result": "System rejects invalid state skip and shows required workflow path",
    })
    cases.append({
        "module_name": module_name,
        "scenario": "Verify modifying a record in final/archived state is prevented",
        "test_type": "state_transition",
        "expected_result": "System returns error when trying to modify finalised record",
    })
    return cases


def _gen_api_ui_consistency(module: Dict, module_name: str) -> List[Dict]:
    """Frontend should match backend validation."""
    cases = []
    keywords = module.get("matched_keywords", [])

    for kw in keywords[:5]:
        cases.extend([
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} frontend validation matches backend validation",
                "test_type": "api_ui_consistency",
                "expected_result": f"Both frontend and backend reject same invalid inputs for {kw}",
            },
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} API error messages match UI error displays",
                "test_type": "api_ui_consistency",
                "expected_result": f"Error messages are consistent between API response and UI rendering for {kw}",
            },
            {
                "module_name": module_name,
                "scenario": f"Verify {kw} API response data is correctly rendered in UI",
                "test_type": "api_ui_consistency",
                "expected_result": f"UI displays all fields from {kw} API response accurately",
            },
        ])
    return cases


def _gen_integration_failure(module: Dict, module_name: str) -> List[Dict]:
    """External service errors, timeouts, retries."""
    cases = []
    keywords = module.get("matched_keywords", [])

    failure_modes = [
        ("service returns HTTP 500", "shows user-friendly error and logs server error"),
        ("service times out after 30s", "shows timeout message and allows retry"),
        ("service returns malformed JSON", "handles parse error without crashing"),
        ("database connection is lost", "returns service-unavailable and queues retry"),
        ("service returns HTTP 429 (rate limited)", "backs off and retries after delay"),
        ("DNS resolution fails", "shows network error and suggests retry"),
        ("SSL certificate is expired", "rejects connection securely and alerts admin"),
    ]
    for kw in keywords[:4]:
        for failure, expected in failure_modes:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} behavior when {failure}",
                "test_type": "integration_failure",
                "expected_result": f"System {expected} during {kw}",
            })
    return cases


def _gen_performance_stress(module: Dict, module_name: str) -> List[Dict]:
    """Load, concurrency, rate limiting tests."""
    cases = []
    keywords = module.get("matched_keywords", [])

    perf_scenarios = [
        ("100 concurrent users", "handles load without degradation"),
        ("1000 requests per second", "rate-limits or throttles gracefully"),
        ("response within 2 seconds under normal load", "meets response SLA"),
        ("with 10MB payload", "processes or rejects large payloads correctly"),
        ("during peak database load", "maintains data consistency and acceptable speed"),
        ("with cache miss on all requests", "serves requests from DB without crashing"),
    ]
    for kw in keywords[:3]:
        for scenario, expected in perf_scenarios:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} performance with {scenario}",
                "test_type": "performance_stress",
                "expected_result": f"System {expected} for {kw}",
            })
    return cases


def _gen_data_corruption(module: Dict, module_name: str) -> List[Dict]:
    """Partial saves, encoding, null propagation."""
    cases = []
    keywords = module.get("matched_keywords", [])

    corruption_scenarios = [
        ("partial save due to mid-operation failure", "rolls back partial data and maintains consistency"),
        ("null value propagation through data pipeline", "handles null safely without NullPointerException"),
        ("character encoding mismatch (UTF-8 vs Latin-1)", "preserves data integrity with correct encoding"),
        ("concurrent write to same record", "prevents data loss via locking or versioning"),
        ("transaction fails after partial commit", "rolls back entire transaction atomically"),
        ("data truncation during insert", "rejects or warns about data exceeding column width"),
    ]
    for kw in keywords[:4]:
        for scenario, expected in corruption_scenarios:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} handles {scenario}",
                "test_type": "data_corruption",
                "expected_result": f"System {expected} for {kw}",
            })
    return cases


def _gen_concurrency(module: Dict, module_name: str) -> List[Dict]:
    """Race conditions, deadlocks, stale reads."""
    cases = []
    keywords = module.get("matched_keywords", [])

    concurrency_scenarios = [
        ("two users modify same record simultaneously", "detects conflict and one update is rejected or merged"),
        ("read occurs during active write transaction", "returns consistent data (no dirty reads)"),
        ("delete and update on same record at same time", "one operation succeeds and the other gets conflict error"),
        ("rapid sequential requests from same user", "processes in order without duplication"),
        ("optimistic locking violation", "detects version mismatch and prompts user to refresh"),
    ]
    for kw in keywords[:4]:
        for scenario, expected in concurrency_scenarios:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw}: {scenario}",
                "test_type": "concurrency",
                "expected_result": f"System {expected} during concurrent {kw}",
            })
    return cases


def _gen_workflow_interruption(module: Dict, module_name: str) -> List[Dict]:
    """Session expiry, network loss, browser close, etc."""
    cases = []
    keywords = module.get("matched_keywords", [])

    interruptions = [
        ("session expires mid-operation", "saves progress or prompts re-authentication"),
        ("network connection drops during submission", "queues or allows retry after reconnection"),
        ("browser is closed during multi-step form", "preserves completed steps on return"),
        ("user navigates away before save", "shows unsaved-changes warning dialog"),
        ("server restart during long-running operation", "resumes or rolls back gracefully"),
        ("user double-clicks submit button", "prevents duplicate submission"),
    ]
    for kw in keywords[:4]:
        for interruption, expected in interruptions:
            cases.append({
                "module_name": module_name,
                "scenario": f"Verify {kw} when {interruption}",
                "test_type": "workflow_interruption",
                "expected_result": f"System {expected} during {kw}",
            })
    return cases


# ═══════════════════════════════════════════════════════
# Phase 4 — Duplicate Elimination
# ═══════════════════════════════════════════════════════

def _deduplicate(cases: List[Dict]) -> List[Dict]:
    """Remove duplicate and near-duplicate test cases."""
    seen_keys = set()
    unique_cases = []

    for case in cases:
        # Normalize scenario text for comparison
        normalized = re.sub(r"\s+", " ", case["scenario"].lower().strip())
        # Create dedup key from type + first 120 chars of normalized scenario
        key = f"{case['test_type']}::{normalized[:120]}"

        if key not in seen_keys:
            seen_keys.add(key)
            unique_cases.append(case)

    removed = len(cases) - len(unique_cases)
    if removed > 0:
        logger.info("Phase 4: Removed %d duplicate test cases", removed)

    return unique_cases


# ═══════════════════════════════════════════════════════
# Phase 5 — Coverage Validation
# ═══════════════════════════════════════════════════════

def _validate_coverage(
    decomposition: Dict,
    test_cases: List[Dict],
) -> Dict[str, Any]:
    """Compute coverage metrics and confidence score."""
    modules = decomposition.get("modules", [])
    warnings = decomposition.get("ambiguity_warnings", [])

    # Count categories covered by test cases
    type_counts: Dict[str, int] = {}
    for tc in test_cases:
        t = tc["test_type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    total_categories = 13
    covered_categories = len(type_counts)

    # Coverage per module
    module_names = {m["category"] for m in modules}
    tc_modules = {tc["module_name"] for tc in test_cases}

    # Confidence calculation
    #  - Each covered category adds ~7 points (max 91)
    #  - Module depth adds up to 9 points
    #  - Ambiguity warnings reduce confidence
    base_score = (covered_categories / total_categories) * 91
    module_depth = min(len(modules) / 12.0, 1.0) * 9
    ambiguity_penalty = min(len(warnings) * 3, 15)

    confidence = max(10, min(100, round(base_score + module_depth - ambiguity_penalty)))

    return {
        "total_modules_detected": len(modules),
        "module_categories": [m["category"] for m in modules],
        "total_scenarios_generated": len(test_cases),
        "scenarios_by_type": type_counts,
        "coverage_confidence_score": confidence,
        "ambiguity_warnings": warnings,
    }


# ═══════════════════════════════════════════════════════
# Master Orchestrator
# ═══════════════════════════════════════════════════════

def generate_enterprise_test_cases(
    requirement_text: str,
    design_text: Optional[str] = None,
    design_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Full 5-phase enterprise test generation pipeline.

    Returns
    -------
    dict
        {
            "decomposition": {...},
            "test_cases": [{...}],
            "coverage": {...},
        }
    """
    logger.info("=== Enterprise Test Engine — Starting 5-Phase Pipeline ===")

    # ── Phase 1+2: Decompose ──────────────────────────────
    decomposition = decompose_requirement(
        requirement_text=requirement_text,
        design_text=design_text,
        design_analysis=design_analysis,
    )

    logger.info("Phases 1-2 complete: %d modules decomposed", decomposition["total_modules"])

    # ── Phase 3: Generate ─────────────────────────────────
    all_cases: List[Dict[str, Any]] = []

    generators = [
        _gen_positive,
        _gen_negative,
        _gen_edge_cases,
        _gen_boundary_value,
        _gen_security,
        _gen_role_based,
        _gen_state_transition,
        _gen_api_ui_consistency,
        _gen_integration_failure,
        _gen_performance_stress,
        _gen_data_corruption,
        _gen_concurrency,
        _gen_workflow_interruption,
    ]

    for module in decomposition["modules"]:
        module_name = module["category"]
        for gen_func in generators:
            cases = gen_func(module, module_name)
            all_cases.extend(cases)

    logger.info("Phase 3 complete: %d raw test cases generated", len(all_cases))

    # ── Phase 4: Deduplicate ──────────────────────────────
    unique_cases = _deduplicate(all_cases)
    logger.info("Phase 4 complete: %d unique test cases after deduplication", len(unique_cases))

    # ── Assign IDs, priorities, levels ────────────────────
    for idx, case in enumerate(unique_cases, start=1):
        case["test_id"] = idx
        case["priority"] = _priority_for(case["test_type"])
        case["test_level"] = _classify_level(case["test_type"], case["scenario"])

    # ── Phase 5: Coverage validation ──────────────────────
    coverage = _validate_coverage(decomposition, unique_cases)
    logger.info(
        "Phase 5 complete: confidence=%d%%, modules=%d, scenarios=%d",
        coverage["coverage_confidence_score"],
        coverage["total_modules_detected"],
        coverage["total_scenarios_generated"],
    )

    logger.info("=== Enterprise Test Engine — Pipeline Complete ===")

    return {
        "decomposition": decomposition,
        "test_cases": unique_cases,
        "coverage": coverage,
    }
