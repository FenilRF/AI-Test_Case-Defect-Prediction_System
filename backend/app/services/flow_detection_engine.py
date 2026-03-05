"""
Flow Detection Engine
------------------------
Auto-detects user flows from UI structure:
  • Primary flows (Registration → Login → Dashboard, etc.)
  • Alternate flows (Validation errors, Cancel, Timeout)
  • Cross-flow enterprise cases
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ── Primary flow templates ───────────────────────────────────
_PRIMARY_FLOW_TEMPLATES = [
    {
        "name": "Registration → Login → Dashboard",
        "trigger_keywords": ["register", "signup", "sign up", "login", "sign in", "dashboard"],
        "min_match": 2,
        "steps": [
            "User navigates to registration page",
            "User fills registration form with valid data",
            "System validates and creates account",
            "User redirected to login page",
            "User enters credentials",
            "System authenticates and redirects to dashboard",
        ],
        "type": "authentication",
    },
    {
        "name": "Add → Edit → Delete (CRUD)",
        "trigger_keywords": ["add", "create", "edit", "update", "delete", "remove", "save"],
        "min_match": 2,
        "steps": [
            "User creates a new record",
            "System saves and displays confirmation",
            "User edits the record",
            "System saves changes",
            "User deletes the record",
            "System removes and confirms deletion",
        ],
        "type": "crud",
    },
    {
        "name": "Search → Filter → Export",
        "trigger_keywords": ["search", "filter", "sort", "export", "download"],
        "min_match": 2,
        "steps": [
            "User enters search criteria",
            "System displays results",
            "User applies filters",
            "System refines results",
            "User exports filtered data",
        ],
        "type": "data_management",
    },
    {
        "name": "Form Submission → Validation → Confirmation",
        "trigger_keywords": ["form", "input", "submit", "validate", "confirmation", "save"],
        "min_match": 2,
        "steps": [
            "User opens form",
            "User fills required fields",
            "System validates input in real-time",
            "User submits form",
            "System processes and shows confirmation",
        ],
        "type": "form_workflow",
    },
    {
        "name": "File Upload → Preview → Process",
        "trigger_keywords": ["upload", "file", "image", "preview", "process", "download"],
        "min_match": 2,
        "steps": [
            "User selects file(s) for upload",
            "System validates file type and size",
            "User previews uploaded content",
            "System processes the file",
            "User can download or manage uploaded files",
        ],
        "type": "file_management",
    },
    {
        "name": "Shopping → Cart → Checkout → Payment",
        "trigger_keywords": ["product", "cart", "checkout", "payment", "order", "buy"],
        "min_match": 2,
        "steps": [
            "User browses products",
            "User adds item to cart",
            "User proceeds to checkout",
            "User enters payment information",
            "System processes payment and confirms order",
        ],
        "type": "ecommerce",
    },
    {
        "name": "Profile → Settings → Password",
        "trigger_keywords": ["profile", "settings", "account", "password", "preferences"],
        "min_match": 2,
        "steps": [
            "User navigates to profile page",
            "User updates profile information",
            "User changes settings/preferences",
            "User updates password",
            "System saves all changes",
        ],
        "type": "user_management",
    },
    {
        "name": "Dashboard → Report → Analytics",
        "trigger_keywords": ["dashboard", "report", "analytics", "chart", "graph", "statistics"],
        "min_match": 2,
        "steps": [
            "User views dashboard overview",
            "User selects date range or filters",
            "System displays charts and metrics",
            "User generates detailed report",
            "User exports report data",
        ],
        "type": "reporting",
    },
    {
        "name": "Notification → Action → Resolution",
        "trigger_keywords": ["notification", "alert", "message", "inbox", "approve", "reject"],
        "min_match": 2,
        "steps": [
            "System generates notification",
            "User views notification",
            "User takes action (approve/reject/dismiss)",
            "System updates status",
        ],
        "type": "notification_workflow",
    },
]

# ── Alternate flow templates ─────────────────────────────────
_ALTERNATE_FLOW_TEMPLATES = [
    {
        "name": "Validation Error Recovery",
        "description": "User submits form with invalid data, sees error, corrects, and resubmits",
        "type": "error_recovery",
    },
    {
        "name": "Cancel Action Mid-Flow",
        "description": "User starts a multi-step process, cancels midway, data is preserved or discarded",
        "type": "cancellation",
    },
    {
        "name": "Session Timeout",
        "description": "User session expires during form filling or navigation, forced re-login",
        "type": "timeout",
    },
    {
        "name": "Network Failure & Retry",
        "description": "Network drops during submission, user retries after reconnection",
        "type": "network_failure",
    },
    {
        "name": "Browser Back/Forward Navigation",
        "description": "User uses browser back/forward buttons during multi-step flow",
        "type": "browser_navigation",
    },
    {
        "name": "Concurrent Session Conflict",
        "description": "Same user logged in from multiple tabs/devices causes data conflict",
        "type": "concurrent_session",
    },
    {
        "name": "Permission Denied Mid-Flow",
        "description": "User loses permissions during a workflow (role changed, token expired)",
        "type": "permission_change",
    },
    {
        "name": "Double Submission Prevention",
        "description": "User double-clicks submit or refreshes during processing",
        "type": "double_submit",
    },
]


def detect_flows(
    ui_schema: Dict[str, Any],
    ui_keywords: List[str] = None,
) -> Dict[str, Any]:
    """
    Detect primary, alternate, and cross-flow patterns from UI schema.

    Parameters
    ----------
    ui_schema : dict
        The unified UI schema from ui_schema_builder.
    ui_keywords : list[str], optional
        Additional UI keywords detected from documents.

    Returns
    -------
    dict
        {
            "primary_flows": [...],
            "alternate_flows": [...],
            "cross_flows": [...],
            "total_flows": int,
        }
    """
    # Collect all keywords from UI schema
    all_keywords = set(ui_keywords or [])

    for module in ui_schema.get("modules", []):
        module_name = module.get("module_name", "").lower()
        all_keywords.update(module_name.split())

        for comp in module.get("ui_components", []):
            label = (comp.get("label") or comp.get("text") or "").lower()
            comp_type = (comp.get("type") or "").lower()
            all_keywords.update(label.split())
            all_keywords.add(comp_type)

        for flow in module.get("flows", []):
            flow_name = flow.get("name", "").lower()
            all_keywords.update(flow_name.split())

    all_keywords = {kw.strip() for kw in all_keywords if kw.strip() and len(kw.strip()) > 2}

    logger.info("Flow detection using %d keywords", len(all_keywords))

    # ── Detect primary flows ─────────────────────────────
    primary_flows = []
    for template in _PRIMARY_FLOW_TEMPLATES:
        trigger_set = set(template["trigger_keywords"])
        overlap = all_keywords & trigger_set
        if len(overlap) >= template["min_match"]:
            primary_flows.append({
                "name": template["name"],
                "type": template["type"],
                "matched_keywords": sorted(overlap),
                "match_strength": len(overlap) / len(trigger_set),
                "steps": template["steps"],
            })

    # Sort by match strength (strongest first)
    primary_flows.sort(key=lambda f: f["match_strength"], reverse=True)

    # ── Include all alternate flows ──────────────────────
    alternate_flows = []
    for alt in _ALTERNATE_FLOW_TEMPLATES:
        alternate_flows.append({
            "name": alt["name"],
            "type": alt["type"],
            "description": alt["description"],
        })

    # ── Generate cross-flow patterns ─────────────────────
    cross_flows = _generate_cross_flows(primary_flows)

    total = len(primary_flows) + len(alternate_flows) + len(cross_flows)

    logger.info(
        "Flow detection complete: primary=%d, alternate=%d, cross=%d",
        len(primary_flows), len(alternate_flows), len(cross_flows),
    )

    return {
        "primary_flows": primary_flows,
        "alternate_flows": alternate_flows,
        "cross_flows": cross_flows,
        "total_flows": total,
    }


def _generate_cross_flows(primary_flows: List[Dict]) -> List[Dict]:
    """Generate cross-flow test scenarios from pairs of primary flows."""
    cross_flows = []

    if len(primary_flows) < 2:
        return cross_flows

    for i, flow_a in enumerate(primary_flows):
        for flow_b in primary_flows[i + 1:]:
            cross_flow = {
                "name": f"{flow_a['name']} ↔ {flow_b['name']}",
                "flow_a": flow_a["name"],
                "flow_b": flow_b["name"],
                "type": "cross_module",
                "scenarios": [
                    f"Complete {flow_a['name']} then immediately start {flow_b['name']}",
                    f"Interrupt {flow_a['name']} with action from {flow_b['name']}",
                    f"Verify data consistency between {flow_a['name']} and {flow_b['name']}",
                ],
            }
            cross_flows.append(cross_flow)

    return cross_flows[:10]  # Cap at 10 cross-flows
