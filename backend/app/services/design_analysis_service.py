"""
Design Analysis Service
--------------------------
Performs lightweight analysis on uploaded design documents
to extract architecture-level insights:
  • Module count
  • Integration count
  • UI vs API vs System classification

Results feed into multi-level test generation and
design-based defect prediction.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Keyword banks for classification ─────────────────────────

_UI_KEYWORDS = [
    "form", "button", "input", "screen", "page", "layout", "view",
    "template", "modal", "dialog", "menu", "navigation", "tab",
    "sidebar", "header", "footer", "card", "grid", "table",
    "dropdown", "select", "checkbox", "radio", "slider",
    "tooltip", "notification", "toast", "popup", "banner",
    "responsive", "mobile", "desktop", "tablet", "css",
    "style", "theme", "color", "font", "icon", "image",
    "animation", "hover", "click", "scroll", "drag", "drop",
    "widget", "dashboard", "chart", "graph", "panel",
    "wireframe", "mockup", "prototype", "figma", "sketch",
]

_API_KEYWORDS = [
    "api", "endpoint", "rest", "graphql", "grpc", "http",
    "get", "post", "put", "delete", "patch",
    "json", "xml", "payload", "header", "query", "param",
    "request", "response", "status", "token", "jwt",
    "oauth", "bearer", "cors", "webhook", "swagger",
    "openapi", "rate limit", "throttle", "middleware",
    "controller", "route", "handler", "service layer",
    "serialization", "deserialization", "dto",
]

_SYSTEM_KEYWORDS = [
    "server", "deploy", "docker", "kubernetes", "container",
    "database", "schema", "migration", "model", "orm",
    "queue", "kafka", "rabbitmq", "redis", "cache",
    "scheduler", "cron", "batch", "worker", "thread",
    "process", "memory", "cpu", "disk", "storage",
    "monitor", "log", "alert", "metric", "health check",
    "load balancer", "proxy", "cdn", "dns", "ssl", "tls",
    "firewall", "backup", "recovery", "replication",
    "microservice", "cluster", "node", "instance",
    "ci/cd", "pipeline", "build", "artifact", "config",
    "environment", "staging", "production",
]

_INTEGRATION_KEYWORDS = [
    "integration", "connect", "sync", "bridge", "adapter",
    "plugin", "extension", "gateway", "proxy", "federation",
    "data flow", "pipeline", "etl", "import", "export",
    "third-party", "external", "partner", "vendor",
    "sso", "ldap", "saml", "smtp", "ftp", "sftp",
    "websocket", "socket", "event", "pub/sub", "stream",
    "message", "notification", "callback", "hook",
]

_MODULE_KEYWORDS = [
    "module", "component", "service", "feature", "section",
    "page", "screen", "panel", "dashboard", "form",
    "login", "register", "auth", "profile", "settings",
    "payment", "checkout", "cart", "product", "catalog",
    "report", "analytics", "admin", "user", "role",
    "notification", "search", "filter", "upload", "download",
]


def _count_keyword_matches(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in the text."""
    count = 0
    for kw in keywords:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text):
            count += 1
    return count


def _extract_modules(text: str) -> List[str]:
    """Try to extract module names from design text."""
    modules = set()

    for kw in _MODULE_KEYWORDS:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text):
            modules.add(kw.title())

    # Also look for capitalized multi-word module patterns
    # e.g., "User Management", "Payment Processing"
    cap_pattern = r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+"
    cap_matches = re.findall(cap_pattern, text) if any(c.isupper() for c in text) else []
    for m in cap_matches[:10]:  # cap at 10
        if len(m) > 3 and len(m) < 50:
            modules.add(m)

    return sorted(modules)[:20]  # cap at 20


def _extract_integrations(text: str) -> List[str]:
    """Identify integration points from design text."""
    found = []
    for kw in _INTEGRATION_KEYWORDS:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text):
            found.append(kw)
    return found


def analyse_design(
    combined_text: str,
    file_names: Optional[List[str]] = None,
    urls: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Perform lightweight design analysis on extracted text content.

    Parameters
    ----------
    combined_text : str
        Concatenated text extracted from all uploaded files.
    file_names : list[str], optional
        Names of uploaded files (for context).
    urls : list[str], optional
        Design URLs provided.

    Returns
    -------
    dict
        {
            "modules": [...],
            "module_count": int,
            "integrations": [...],
            "integration_count": int,
            "classification": {
                "ui_score": int,
                "api_score": int,
                "system_score": int,
                "primary_type": str,
            },
            "design_sources": {
                "files": [...],
                "urls": [...],
            },
            "summary": str,
        }
    """
    text_lower = combined_text.lower()
    logger.info("Analysing design document (%d chars)", len(combined_text))

    # ── Module extraction ─────────────────────────────────
    modules = _extract_modules(text_lower)
    module_count = max(len(modules), 1)

    # ── Integration identification ────────────────────────
    integrations = _extract_integrations(text_lower)
    integration_count = len(integrations)

    # ── UI vs API vs System classification ────────────────
    ui_score = _count_keyword_matches(text_lower, _UI_KEYWORDS)
    api_score = _count_keyword_matches(text_lower, _API_KEYWORDS)
    system_score = _count_keyword_matches(text_lower, _SYSTEM_KEYWORDS)

    total = ui_score + api_score + system_score
    if total == 0:
        primary_type = "General"
    elif ui_score >= api_score and ui_score >= system_score:
        primary_type = "UI-Focused"
    elif api_score >= ui_score and api_score >= system_score:
        primary_type = "API-Focused"
    else:
        primary_type = "System-Focused"

    # ── Summary ───────────────────────────────────────────
    summary_parts = [
        f"Design contains {module_count} identified module(s).",
    ]
    if integration_count > 0:
        summary_parts.append(f"{integration_count} integration point(s) detected.")
    summary_parts.append(f"Primary classification: {primary_type}.")
    if file_names:
        summary_parts.append(f"Analysed from {len(file_names)} uploaded file(s).")
    if urls:
        summary_parts.append(f"{len(urls)} design URL(s) linked.")

    report = {
        "modules": modules,
        "module_count": module_count,
        "integrations": integrations,
        "integration_count": integration_count,
        "classification": {
            "ui_score": ui_score,
            "api_score": api_score,
            "system_score": system_score,
            "primary_type": primary_type,
        },
        "design_sources": {
            "files": file_names or [],
            "urls": urls or [],
        },
        "summary": " ".join(summary_parts),
    }

    logger.info(
        "Design analysis: modules=%d, integrations=%d, type=%s",
        module_count, integration_count, primary_type,
    )
    return report
