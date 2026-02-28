"""
Requirement Decomposer — Phase 1 + Phase 2
----------------------------------------------
Performs deep multi-module decomposition of requirement/design text.

Phase 1: Breaks input into 12 logical module categories
Phase 2: For each module, extracts explicit rules, implicit rules,
         boundary conditions, negative paths, and data dependencies.

This feeds into the enterprise test engine (Phase 3–5).
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════
# Module Category Definitions (Phase 1)
# ═══════════════════════════════════════════════════════

_MODULE_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "Core Functional": {
        "keywords": [
            "login", "logout", "register", "create", "read", "update",
            "delete", "submit", "upload", "download", "search", "filter",
            "sort", "send", "receive", "process", "view", "display",
            "list", "fetch", "retrieve", "approve", "reject", "cancel",
            "confirm", "subscribe", "unsubscribe", "transfer", "pay",
            "checkout", "order", "purchase", "refund", "reset", "change",
            "save", "edit", "modify", "add", "remove", "assign", "import",
            "export", "generate", "print", "share", "invite", "activate",
            "deactivate", "archive", "restore", "merge", "split", "clone",
        ],
        "phrases": [
            "user can", "system shall", "system should",
            "must be able to", "allow the user", "enable",
            "when the user", "upon clicking", "after submission",
            "on success", "on completion", "the system will",
        ],
    },
    "Business Rules": {
        "keywords": [
            "calculate", "compute", "discount", "tax", "shipping",
            "threshold", "limit", "quota", "policy", "rule",
            "condition", "criteria", "eligibility", "tier",
            "pricing", "rate", "commission", "fee", "penalty",
            "grace period", "expiry", "renewal", "escalation",
            "workflow", "approval chain", "escalation",
        ],
        "phrases": [
            "if the", "when the", "only if", "unless",
            "based on", "depending on", "according to",
            "must not exceed", "should be at least",
            "is calculated as", "percent of", "percentage",
            "business rule", "business logic",
        ],
    },
    "Validation Rules": {
        "keywords": [
            "required", "mandatory", "optional", "validate",
            "format", "pattern", "regex", "min", "max",
            "length", "size", "range", "alphanumeric",
            "numeric", "alphabetic", "unique", "distinct",
            "not null", "not empty", "non-empty", "email",
            "phone", "url", "date", "valid", "invalid",
        ],
        "phrases": [
            "must be", "should be", "cannot be",
            "must contain", "should not contain",
            "at least", "at most", "no more than",
            "between", "greater than", "less than",
            "format should be", "valid format",
            "email format", "phone format", "date format",
        ],
    },
    "Error Handling": {
        "keywords": [
            "error", "exception", "fail", "failure", "invalid",
            "reject", "deny", "timeout", "retry", "fallback",
            "rollback", "recovery", "crash", "corrupt",
            "unavailable", "interrupt", "abort", "terminate",
        ],
        "phrases": [
            "error message", "error handling", "in case of",
            "if the system fails", "when an error occurs",
            "should display error", "must show warning",
            "graceful degradation", "fail-safe", "fail-over",
            "should not crash", "handle gracefully",
        ],
    },
    "Edge Cases": {
        "keywords": [
            "concurrent", "simultaneous", "parallel", "race",
            "idempotent", "idempotency", "duplicate", "stale",
            "empty", "null", "zero", "overflow", "underflow",
            "unicode", "special character", "whitespace",
            "extreme", "boundary", "corner", "unusual",
        ],
        "phrases": [
            "at the same time", "multiple users",
            "rapid succession", "double click",
            "browser back button", "session expired",
            "network failure", "slow connection",
            "very large", "very small", "empty input",
        ],
    },
    "Security": {
        "keywords": [
            "security", "authentication", "authorization",
            "permission", "access", "privilege", "encrypt",
            "decrypt", "hash", "token", "jwt", "oauth",
            "password", "credential", "session", "csrf",
            "xss", "injection", "sanitize", "firewall",
            "ssl", "tls", "https", "certificate", "audit",
            "vulnerability", "threat", "exploit", "brute",
        ],
        "phrases": [
            "access control", "role-based", "sql injection",
            "cross-site scripting", "cross-site request",
            "data breach", "sensitive data", "personally identifiable",
            "two-factor", "multi-factor", "single sign-on",
            "session management", "token expiry",
            "unauthorized access", "privilege escalation",
        ],
    },
    "Performance": {
        "keywords": [
            "performance", "load", "stress", "scalability",
            "latency", "throughput", "response time",
            "concurrent", "capacity", "bottleneck",
            "cache", "optimize", "speed", "fast", "slow",
            "memory", "cpu", "bandwidth", "queue",
        ],
        "phrases": [
            "response time", "page load", "under load",
            "peak traffic", "concurrent users", "per second",
            "within seconds", "milliseconds", "real-time",
            "should not exceed", "performance degradation",
            "stress test", "load test", "benchmarking",
        ],
    },
    "Integration Points": {
        "keywords": [
            "api", "endpoint", "rest", "graphql", "grpc",
            "webhook", "callback", "external", "third-party",
            "integration", "connect", "sync", "database",
            "microservice", "service", "gateway", "proxy",
            "kafka", "rabbitmq", "redis", "smtp", "ftp",
            "sso", "ldap", "saml", "oauth", "socket",
        ],
        "phrases": [
            "api call", "api endpoint", "external service",
            "third-party integration", "data sync",
            "cross-service", "inter-service", "message queue",
            "event-driven", "webhook notification",
            "database connection", "service dependency",
        ],
    },
    "UI/UX Behaviors": {
        "keywords": [
            "button", "form", "input", "field", "dropdown",
            "modal", "dialog", "popup", "tooltip", "menu",
            "navigation", "tab", "sidebar", "header", "footer",
            "layout", "responsive", "mobile", "desktop",
            "scroll", "hover", "click", "drag", "animation",
            "notification", "toast", "alert", "badge", "spinner",
            "loading", "skeleton", "pagination", "table", "grid",
        ],
        "phrases": [
            "user interface", "user experience", "front-end",
            "should display", "should show", "should hide",
            "loading indicator", "success message",
            "error indication", "form submission",
            "field validation", "auto-complete",
            "responsive design", "cross-browser",
            "empty state", "placeholder text",
        ],
    },
    "State Transitions": {
        "keywords": [
            "status", "state", "transition", "lifecycle",
            "pending", "active", "inactive", "completed",
            "cancelled", "expired", "suspended", "approved",
            "rejected", "draft", "published", "archived",
            "open", "closed", "in progress", "resolved",
        ],
        "phrases": [
            "changes from", "transitions to", "moves to",
            "status change", "state machine", "workflow step",
            "when status is", "if state is", "lifecycle",
            "from pending to", "from draft to",
            "order status", "ticket status",
        ],
    },
    "Role-Based Access": {
        "keywords": [
            "role", "admin", "administrator", "user", "guest",
            "manager", "supervisor", "moderator", "editor",
            "viewer", "owner", "member", "subscriber",
            "operator", "analyst", "auditor", "tenant",
        ],
        "phrases": [
            "role-based", "access control", "permission level",
            "admin only", "restricted to", "visible only to",
            "based on role", "user role", "multi-tenant",
            "admin panel", "admin dashboard",
            "user permission", "privilege level",
        ],
    },
    "Data Handling": {
        "keywords": [
            "data", "record", "field", "column", "table",
            "schema", "migration", "backup", "restore",
            "import", "export", "csv", "json", "xml",
            "encode", "decode", "serialize", "deserialize",
            "encrypt", "decrypt", "mask", "sanitize",
            "transform", "convert", "format", "parse",
        ],
        "phrases": [
            "data integrity", "data validation",
            "data transformation", "data migration",
            "data export", "data import", "data retention",
            "data encryption", "data masking",
            "file format", "character encoding",
            "null handling", "default value",
        ],
    },
}


# ═══════════════════════════════════════════════════════
# Phase 1 — Full Input Analysis
# ═══════════════════════════════════════════════════════

def _detect_modules(text_lower: str) -> List[Dict[str, Any]]:
    """
    Scan the full text against all 12 module categories.
    Returns list of detected modules with their matched signals.
    """
    detected = []
    for category, signals in _MODULE_CATEGORIES.items():
        matched_keywords: List[str] = []
        matched_phrases: List[str] = []

        for kw in signals["keywords"]:
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, text_lower):
                matched_keywords.append(kw)

        for phrase in signals["phrases"]:
            if phrase in text_lower:
                matched_phrases.append(phrase)

        if matched_keywords or matched_phrases:
            relevance = len(matched_keywords) + len(matched_phrases) * 2
            detected.append({
                "category": category,
                "matched_keywords": matched_keywords,
                "matched_phrases": matched_phrases,
                "relevance_score": relevance,
            })

    # Sort by relevance
    detected.sort(key=lambda m: m["relevance_score"], reverse=True)
    return detected


# ═══════════════════════════════════════════════════════
# Phase 2 — Deep Requirement Decomposition
# ═══════════════════════════════════════════════════════

def _extract_explicit_rules(text_lower: str, category: str) -> List[str]:
    """Extract explicitly stated rules from text."""
    rules = []

    # Pattern: "must", "shall", "should", "will" + action
    must_patterns = re.findall(
        r"(?:the system |system |it |the user |users? )?(?:must|shall|should|will|can) ([^.;]{10,80})",
        text_lower,
    )
    for match in must_patterns[:15]:
        rules.append(f"System {match.strip()}")

    # Pattern: "if ... then ..." conditional rules
    if_patterns = re.findall(
        r"if ([^,]{5,60}),?\s*(?:then )?((?:the )?(?:system|it) [^.;]{5,80})",
        text_lower,
    )
    for condition, action in if_patterns[:10]:
        rules.append(f"When {condition.strip()}, {action.strip()}")

    # Pattern: "required", "mandatory" field rules
    req_patterns = re.findall(
        r"(\w[\w\s]{2,30}) (?:is |are )?(?:required|mandatory)",
        text_lower,
    )
    for field in req_patterns[:10]:
        rules.append(f"{field.strip().title()} is required")

    return rules[:20]


def _extract_implicit_rules(text_lower: str, category: str, keywords: List[str]) -> List[str]:
    """Infer hidden assumptions based on what's mentioned."""
    implicit = []

    if category == "Core Functional":
        if any(kw in text_lower for kw in ["create", "add", "register"]):
            implicit.append("Duplicate entries should be prevented")
            implicit.append("Created record should be immediately retrievable")
        if any(kw in text_lower for kw in ["delete", "remove"]):
            implicit.append("Deletion should require confirmation")
            implicit.append("Soft-delete may be preferred over hard-delete")
        if any(kw in text_lower for kw in ["update", "edit", "modify"]):
            implicit.append("Concurrent edits should be handled safely")
            implicit.append("Audit trail should record modifications")

    if category == "Validation Rules":
        if any(kw in text_lower for kw in ["email", "phone", "url"]):
            implicit.append("Input format should be validated both client-side and server-side")
        if any(kw in text_lower for kw in ["password"]):
            implicit.append("Password strength requirements should be enforced")
            implicit.append("Password should be stored hashed, never in plaintext")

    if category == "Security":
        implicit.append("Session timeout should be enforced")
        implicit.append("Failed login attempts should be tracked and limited")
        implicit.append("Sensitive data should be encrypted in transit and at rest")

    if category == "Integration Points":
        implicit.append("External service failures should be handled gracefully")
        implicit.append("API responses should be validated before processing")
        implicit.append("Retry mechanisms should be in place for transient failures")

    if category == "UI/UX Behaviors":
        if any(kw in text_lower for kw in ["form", "submit", "input"]):
            implicit.append("Form should prevent double-submission")
            implicit.append("Loading state should be shown during async operations")
        implicit.append("UI should handle slow network gracefully")

    if category == "Data Handling":
        implicit.append("Data consistency must be maintained across operations")
        implicit.append("Character encoding should support UTF-8")

    if category == "State Transitions":
        implicit.append("Invalid state transitions should be rejected")
        implicit.append("State changes should be logged for audit")

    return implicit


def _extract_boundaries(text_lower: str, category: str, keywords: List[str]) -> List[str]:
    """Identify boundary conditions for the module."""
    boundaries = []

    # Numeric boundaries
    num_patterns = re.findall(
        r"(?:min(?:imum)?|max(?:imum)?|at least|at most|no more than|between)\s+(\d+)",
        text_lower,
    )
    for val in num_patterns[:5]:
        boundaries.append(f"Boundary at value {val}")
        boundaries.append(f"Just below {val}")
        boundaries.append(f"Just above {val}")

    # Length constraints
    len_patterns = re.findall(
        r"(\w+)\s+(?:length|size)\s+(?:of |is |= )?(\d+)",
        text_lower,
    )
    for field, length in len_patterns[:5]:
        boundaries.append(f"{field} at exactly {length} characters")
        boundaries.append(f"{field} at {int(length)-1} characters (one below)")
        boundaries.append(f"{field} at {int(length)+1} characters (one above)")

    # Generic boundaries per category
    if category == "Core Functional":
        boundaries.extend([
            "First record in the system",
            "Maximum number of records",
            "Empty dataset scenario",
        ])
    if category == "Validation Rules":
        boundaries.extend([
            "Field at minimum allowed length (1 char)",
            "Field at maximum allowed length",
            "Field exceeding max length by 1",
            "Field with exactly 0 characters (empty)",
        ])
    if category == "Performance":
        boundaries.extend([
            "System with 1 concurrent user",
            "System at maximum concurrent user limit",
            "System slightly over capacity",
        ])

    return boundaries


def _extract_negative_paths(text_lower: str, category: str, keywords: List[str]) -> List[str]:
    """Identify negative/error scenarios for the module."""
    negatives = []

    if category == "Core Functional":
        for kw in keywords[:5]:
            negatives.append(f"Attempt {kw} without required data")
            negatives.append(f"Attempt {kw} with invalid data")
            negatives.append(f"Attempt {kw} when system is in wrong state")

    if category == "Validation Rules":
        negatives.extend([
            "Submit form with all fields empty",
            "Submit with invalid email format",
            "Submit with SQL injection in text fields",
            "Submit with extremely long input",
            "Submit with special characters only",
        ])

    if category == "Security":
        negatives.extend([
            "Access resource without authentication",
            "Access resource with expired token",
            "Access resource with insufficient permissions",
            "Attempt brute-force login",
            "Submit malicious payload in request body",
        ])

    if category == "Integration Points":
        negatives.extend([
            "External service returns 500 error",
            "External service times out",
            "External service returns malformed response",
            "Database connection pool exhausted",
            "Network partition between services",
        ])

    if category == "Error Handling":
        negatives.extend([
            "System encounters unexpected null value",
            "System receives corrupted data",
            "System runs out of disk space",
            "Transaction fails mid-operation",
        ])

    if category == "State Transitions":
        negatives.extend([
            "Attempt to transition to invalid state",
            "Attempt to skip a required state",
            "Attempt to reverse a final state",
        ])

    if category == "Role-Based Access":
        negatives.extend([
            "Low-privilege user attempts admin action",
            "Guest user attempts authenticated action",
            "User attempts action on another user's resource",
        ])

    return negatives


# ═══════════════════════════════════════════════════════
# Main Decomposition Entry Point
# ═══════════════════════════════════════════════════════

def decompose_requirement(
    requirement_text: str,
    design_text: Optional[str] = None,
    design_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Full Phase 1 + Phase 2 decomposition.

    Parameters
    ----------
    requirement_text : str
        Raw requirement text.
    design_text : str, optional
        Design document text.
    design_analysis : dict, optional
        Output from design_analysis_service.analyse_design().

    Returns
    -------
    dict
        {
            "modules": [ { category, matched_keywords, rules, implicit_rules,
                           boundaries, negative_paths, relevance_score } ],
            "total_modules": int,
            "design_integration": dict or None,
            "ambiguity_warnings": [str],
        }
    """
    combined = requirement_text
    if design_text:
        combined = f"{requirement_text}\n{design_text}"
    text_lower = combined.lower()

    logger.info("Phase 1: Detecting modules in %d chars of input", len(combined))

    # ── Phase 1: Detect modules ───────────────────────────
    raw_modules = _detect_modules(text_lower)

    # Always include Core Functional if nothing else
    if not raw_modules:
        raw_modules = [{
            "category": "Core Functional",
            "matched_keywords": ["process"],
            "matched_phrases": [],
            "relevance_score": 1,
        }]

    logger.info("Phase 1 complete: %d modules detected", len(raw_modules))

    # ── Phase 2: Deep decomposition per module ────────────
    decomposed_modules = []
    for mod in raw_modules:
        cat = mod["category"]
        kws = mod["matched_keywords"]

        explicit_rules = _extract_explicit_rules(text_lower, cat)
        implicit_rules = _extract_implicit_rules(text_lower, cat, kws)
        boundaries = _extract_boundaries(text_lower, cat, kws)
        negative_paths = _extract_negative_paths(text_lower, cat, kws)

        decomposed_modules.append({
            "category": cat,
            "matched_keywords": kws,
            "matched_phrases": mod["matched_phrases"],
            "relevance_score": mod["relevance_score"],
            "explicit_rules": explicit_rules,
            "implicit_rules": implicit_rules,
            "boundaries": boundaries,
            "negative_paths": negative_paths,
        })

    logger.info("Phase 2 complete: %d modules fully decomposed", len(decomposed_modules))

    # ── Integrate design analysis (if available) ──────────
    design_integration = None
    if design_analysis:
        design_modules = design_analysis.get("modules", [])
        design_integrations = design_analysis.get("integrations", [])
        classification = design_analysis.get("classification", {})

        design_integration = {
            "design_modules": design_modules,
            "design_integrations": design_integrations,
            "primary_type": classification.get("primary_type", "General"),
            "ui_score": classification.get("ui_score", 0),
            "api_score": classification.get("api_score", 0),
            "system_score": classification.get("system_score", 0),
        }

    # ── Ambiguity warnings ────────────────────────────────
    warnings = _detect_ambiguities(text_lower, decomposed_modules)

    return {
        "modules": decomposed_modules,
        "total_modules": len(decomposed_modules),
        "design_integration": design_integration,
        "ambiguity_warnings": warnings,
    }


def _detect_ambiguities(text_lower: str, modules: List[Dict]) -> List[str]:
    """Detect potential ambiguities in the requirement text."""
    warnings = []

    # Vague language
    vague_terms = ["appropriate", "suitable", "proper", "adequate", "reasonable",
                   "significant", "sufficient", "as needed", "etc", "and so on"]
    for term in vague_terms:
        if term in text_lower:
            warnings.append(f"Vague term detected: '{term}' — may need clarification")

    # Missing module categories
    detected_cats = {m["category"] for m in modules}
    if "Security" not in detected_cats:
        warnings.append("No security requirements detected — consider adding security rules")
    if "Error Handling" not in detected_cats:
        warnings.append("No error handling requirements detected — consider defining error behavior")
    if "Performance" not in detected_cats:
        warnings.append("No performance requirements detected — consider defining SLAs")

    # Conflicting rules
    if "must" in text_lower and "optional" in text_lower:
        warnings.append("Both mandatory and optional constraints detected — verify field requirements")

    # Short input
    if len(text_lower) < 100:
        warnings.append("Requirement text is very short — may lack sufficient detail for exhaustive coverage")

    return warnings
