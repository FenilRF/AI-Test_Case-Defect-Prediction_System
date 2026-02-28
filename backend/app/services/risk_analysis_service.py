"""
Multi-Layer Risk Analysis Service
------------------------------------
Analyses requirement / design text and produces a risk report across
six layers:
  • UI Level
  • API Level
  • Integration Level
  • Function Level
  • System Level
  • Non-functional Level

Each layer receives a risk score (0.0–1.0), risk level (Low/Medium/High),
and a list of identified risk signals.
"""

import logging
import re
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# ── Risk signal keyword sets per layer ────────────────────────

_LAYER_SIGNALS: Dict[str, Dict[str, List[str]]] = {
    "UI Level": {
        "keywords": [
            "form", "button", "input", "display", "page", "screen",
            "layout", "render", "view", "template", "css", "style",
            "responsive", "mobile", "browser", "dropdown", "modal",
            "navigation", "menu", "tab", "tooltip", "notification",
            "dashboard", "widget", "theme", "animation", "hover",
            "click", "drag", "scroll", "popup", "dialog", "checkbox",
            "radio", "slider", "upload", "download",
        ],
        "risk_phrases": [
            "complex ui", "dynamic rendering", "cross-browser",
            "responsive design", "accessibility", "user interaction",
            "drag and drop", "real-time update", "rich text editor",
        ],
    },
    "API Level": {
        "keywords": [
            "api", "endpoint", "rest", "graphql", "request", "response",
            "http", "get", "post", "put", "delete", "patch",
            "json", "xml", "payload", "header", "query", "parameter",
            "status code", "rate limit", "throttle", "webhook",
            "swagger", "openapi", "cors", "authentication token",
        ],
        "risk_phrases": [
            "api gateway", "rate limiting", "request validation",
            "response format", "api versioning", "breaking change",
            "third-party api", "external api", "api key",
        ],
    },
    "Integration Level": {
        "keywords": [
            "integration", "connect", "sync", "external", "third-party",
            "database", "queue", "message", "event", "kafka", "rabbitmq",
            "socket", "websocket", "grpc", "microservice", "service",
            "bridge", "adapter", "plugin", "middleware", "gateway",
            "data flow", "pipeline", "proxy", "load balancer",
        ],
        "risk_phrases": [
            "cross-service", "data consistency", "eventual consistency",
            "message queue", "event-driven", "service mesh",
            "circuit breaker", "retry logic", "fallback",
        ],
    },
    "Function Level": {
        "keywords": [
            "calculate", "validate", "process", "transform", "parse",
            "convert", "format", "logic", "algorithm", "rule",
            "condition", "if", "loop", "iterate", "recursive",
            "sort", "filter", "search", "match", "compare",
            "merge", "split", "aggregate", "compute", "check",
        ],
        "risk_phrases": [
            "complex logic", "business rule", "edge case",
            "error handling", "null check", "type conversion",
            "data transformation", "validation rule", "boundary condition",
        ],
    },
    "System Level": {
        "keywords": [
            "system", "server", "deploy", "infrastructure", "docker",
            "container", "kubernetes", "cluster", "monitor", "log",
            "config", "environment", "scheduler", "cron", "batch",
            "process", "thread", "memory", "cpu", "disk",
            "network", "firewall", "dns", "proxy", "backup",
        ],
        "risk_phrases": [
            "system failure", "resource exhaustion", "memory leak",
            "deadlock", "race condition", "high availability",
            "disaster recovery", "failover", "auto-scaling",
        ],
    },
    "Non-functional Level": {
        "keywords": [
            "performance", "security", "scalability", "reliability",
            "availability", "compliance", "audit", "encryption",
            "ssl", "tls", "certificate", "auth", "permission",
            "role", "access control", "privacy", "gdpr",
            "load", "stress", "latency", "throughput", "cache",
            "backup", "recovery", "resilience", "sla",
        ],
        "risk_phrases": [
            "sql injection", "xss", "csrf", "ddos", "brute force",
            "data breach", "sensitive data", "pii",
            "performance degradation", "response time",
            "concurrent users", "peak load",
        ],
    },
}


def _score_layer(text_lower: str, signals: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Score a single risk layer by counting keyword/phrase matches.
    
    Returns dict with: score (0.0-1.0), risk_level, found_signals
    """
    found: List[str] = []

    for kw in signals["keywords"]:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text_lower):
            found.append(kw)

    for phrase in signals["risk_phrases"]:
        if phrase in text_lower:
            found.append(f"⚠ {phrase}")

    # Calculate score:  keyword hits contribute linearly, risk phrases × 2
    keyword_hits = sum(1 for f in found if not f.startswith("⚠"))
    phrase_hits = sum(1 for f in found if f.startswith("⚠"))

    # Normalise to 0–1 range (cap at 10 signals for max)
    raw = (keyword_hits + phrase_hits * 2) / 10
    score = round(min(raw, 1.0), 4)

    if score >= 0.7:
        risk_level = "High"
    elif score >= 0.35:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "score": score,
        "risk_level": risk_level,
        "found_signals": found,
    }


def analyse_risk(
    requirement_text: str,
    design_text: str = "",
) -> Dict[str, Any]:
    """
    Perform multi-layer risk analysis on requirement + design text.

    Parameters
    ----------
    requirement_text : str
        The raw requirement text.
    design_text : str, optional
        The design document text (if provided).

    Returns
    -------
    dict
        {
            "layers": { "UI Level": {...}, "API Level": {...}, ... },
            "overall_score": float,
            "overall_risk_level": str,
            "summary": str,
        }
    """
    combined = f"{requirement_text} {design_text}".lower()
    logger.info("Running multi-layer risk analysis (%d chars)", len(combined))

    layers: Dict[str, Any] = {}
    scores: List[float] = []

    for layer_name, signals in _LAYER_SIGNALS.items():
        result = _score_layer(combined, signals)
        layers[layer_name] = result
        scores.append(result["score"])

    overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    if overall_score >= 0.6:
        overall_risk_level = "High"
    elif overall_score >= 0.3:
        overall_risk_level = "Medium"
    else:
        overall_risk_level = "Low"

    # Identify top-risk layers
    high_risk_layers = [name for name, data in layers.items() if data["risk_level"] == "High"]
    medium_risk_layers = [name for name, data in layers.items() if data["risk_level"] == "Medium"]

    summary_parts = []
    if high_risk_layers:
        summary_parts.append(f"High risk in: {', '.join(high_risk_layers)}.")
    if medium_risk_layers:
        summary_parts.append(f"Medium risk in: {', '.join(medium_risk_layers)}.")
    if not summary_parts:
        summary_parts.append("Overall risk is Low across all layers.")

    report = {
        "layers": layers,
        "overall_score": overall_score,
        "overall_risk_level": overall_risk_level,
        "summary": " ".join(summary_parts),
    }

    logger.info(
        "Risk analysis complete: overall=%.4f (%s)", overall_score, overall_risk_level
    )
    return report
