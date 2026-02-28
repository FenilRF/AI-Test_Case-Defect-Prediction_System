"""
NLP Service — Requirement Analysis Engine
--------------------------------------------
Parses raw requirement text to extract:
  • Module name  (first capitalised noun phrase or fallback)
  • Actions      (verbs like login, register, create, update, delete)
  • Fields       (domain entities like email, password, amount, id, name …)
  • Validations  (constraints like required, max length, format, unique …)

Uses keyword-matching heuristics boosted by NLTK preprocessing.
"""

import re
import logging
from typing import List

from app.utils.text_preprocessing import preprocess, clean_text
from app.schemas.schemas import ParsedRequirement

logger = logging.getLogger(__name__)

# ── Keyword dictionaries ────────────────────────────────────
ACTION_KEYWORDS: List[str] = [
    "login", "logout", "register", "signup", "sign up", "sign in",
    "create", "read", "update", "delete", "remove", "edit", "modify",
    "submit", "upload", "download", "search", "filter", "sort",
    "validate", "verify", "authenticate", "authorise", "authorize",
    "reset", "change", "view", "display", "list", "fetch", "retrieve",
    "send", "receive", "process", "calculate", "transfer", "pay",
    "approve", "reject", "cancel", "confirm", "subscribe", "unsubscribe",
]

FIELD_KEYWORDS: List[str] = [
    "email", "password", "username", "name", "first name", "last name",
    "phone", "phone number", "mobile", "address", "city", "state",
    "country", "zip", "zipcode", "zip code", "postal code",
    "amount", "price", "cost", "balance", "quantity", "total",
    "id", "user id", "order id", "product id", "transaction id",
    "date", "time", "datetime", "dob", "date of birth",
    "description", "title", "comment", "message", "note",
    "file", "image", "photo", "document", "attachment",
    "role", "permission", "status", "type", "category", "tag",
    "token", "otp", "code", "pin", "cvv", "card number",
    "account", "account number", "iban", "routing number",
]

VALIDATION_KEYWORDS: List[str] = [
    "required", "mandatory", "optional",
    "min length", "max length", "minimum", "maximum",
    "format", "regex", "pattern",
    "unique", "distinct",
    "valid", "invalid", "alphanumeric", "numeric", "alphabetic",
    "positive", "negative", "non-negative",
    "range", "between", "greater than", "less than",
    "not null", "not empty", "non-empty",
    "email format", "url format", "date format",
    "special characters", "uppercase", "lowercase",
    "must contain", "should not contain",
    "length", "size", "limit",
    "encrypted", "hashed", "masked",
]

# ── Module name heuristics ──────────────────────────────────
MODULE_KEYWORDS: dict[str, str] = {
    "login": "Login",
    "logout": "Login",
    "sign in": "Login",
    "sign up": "Registration",
    "signup": "Registration",
    "register": "Registration",
    "registration": "Registration",
    "password": "Authentication",
    "reset password": "Authentication",
    "change password": "Authentication",
    "payment": "Payment",
    "pay": "Payment",
    "transfer": "Payment",
    "transaction": "Payment",
    "checkout": "Payment",
    "cart": "Shopping Cart",
    "order": "Order Management",
    "product": "Product Management",
    "search": "Search",
    "profile": "User Profile",
    "dashboard": "Dashboard",
    "report": "Reporting",
    "notification": "Notifications",
    "setting": "Settings",
    "upload": "File Management",
    "download": "File Management",
}


def _extract_module(text_lower: str) -> str:
    """Infer the most likely module name from the requirement text."""
    for keyword, module in MODULE_KEYWORDS.items():
        if keyword in text_lower:
            return module
    # Fallback: use first capitalized word group from original text
    match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text_lower.title())
    return match.group(0) if match else "General"


def _find_matches(text_lower: str, keyword_list: List[str]) -> List[str]:
    """Return all keywords found (as whole words / phrases) in the text."""
    found: List[str] = []
    for kw in keyword_list:
        # Use word-boundary regex so 'id' doesn't match inside 'valid'
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text_lower):
            found.append(kw)
    return sorted(set(found))


def parse_requirement(text: str) -> ParsedRequirement:
    """
    Main entry point — analyse raw requirement text and return structured output.

    Parameters
    ----------
    text : str
        Free-form requirement description.

    Returns
    -------
    ParsedRequirement
        Structured JSON-serialisable object.
    """
    text_lower = clean_text(text)
    logger.info("Parsing requirement: %s…", text_lower[:80])

    module = _extract_module(text_lower)
    actions = _find_matches(text_lower, ACTION_KEYWORDS)
    fields = _find_matches(text_lower, FIELD_KEYWORDS)
    validations = _find_matches(text_lower, VALIDATION_KEYWORDS)

    # Ensure at least one entry per category for downstream generation
    if not actions:
        actions = ["process"]
    if not fields:
        fields = ["data"]
    if not validations:
        validations = ["required"]

    parsed = ParsedRequirement(
        module=module,
        actions=actions,
        fields=fields,
        validations=validations,
    )
    logger.debug("Parsed result: %s", parsed.model_dump_json())
    return parsed
