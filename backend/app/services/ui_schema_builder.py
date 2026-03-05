"""
UI Schema Builder
--------------------
Merges outputs from DOM extraction, Vision analysis, and Document extraction
into a unified structured UI Schema.

Performs:
  • Component deduplication (>85% name/type similarity)
  • Module grouping
  • Validation detection from field context
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _normalize_component_name(name: str) -> str:
    """Normalize a component name for dedup comparison."""
    return re.sub(r"\s+", " ", name.lower().strip())


def _similarity_score(a: str, b: str) -> float:
    """Simple token-overlap similarity between two strings."""
    if not a or not b:
        return 0.0
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union) if union else 0.0


def _deduplicate_components(components: List[Dict]) -> List[Dict]:
    """Remove components with >85% similarity."""
    if not components:
        return []

    unique = []
    seen_keys = set()

    for comp in components:
        # Create a fingerprint from type + label
        label = _normalize_component_name(comp.get("label", comp.get("text", "")))
        comp_type = comp.get("type", "unknown")
        key = f"{comp_type}:{label}"

        # Check similarity against existing
        is_duplicate = False
        for seen in seen_keys:
            if _similarity_score(key, seen) > 0.85:
                is_duplicate = True
                break

        if not is_duplicate:
            seen_keys.add(key)
            unique.append(comp)

    removed = len(components) - len(unique)
    if removed > 0:
        logger.info("Deduplication removed %d duplicate components", removed)

    return unique


def _extract_validations_from_components(components: List[Dict]) -> List[str]:
    """Infer potential validations from component properties."""
    validations = set()

    for comp in components:
        label = (comp.get("label") or comp.get("text") or "").lower()
        comp_type = (comp.get("type") or "").lower()
        placeholder = (comp.get("placeholder") or comp.get("properties", {}).get("placeholder", "")).lower()
        validation_hint = comp.get("properties", {}).get("validation_hint", "")

        if validation_hint:
            validations.add(validation_hint)

        # Infer from component labels
        if "email" in label:
            validations.add("Email format validation required")
        if "password" in label:
            validations.add("Password strength validation required")
            validations.add("Password minimum length check")
        if "phone" in label or "mobile" in label:
            validations.add("Phone number format validation")
        if "date" in label or comp_type == "date_picker":
            validations.add("Date format and range validation")
        if "amount" in label or "price" in label or "cost" in label:
            validations.add("Numeric value and range validation")
        if "url" in label or "link" in label:
            validations.add("URL format validation")
        if "file" in label or comp_type == "file_upload":
            validations.add("File type and size validation")

        # Check for required hints
        required = comp.get("properties", {}).get("required", False)
        if required:
            validations.add(f"Required field: {label}")

        # Placeholder hints
        if "required" in placeholder:
            validations.add(f"Required field: {label}")
        if "format" in placeholder:
            validations.add(f"Format validation for: {label}")

    return sorted(validations)


def _group_into_modules(
    components: List[Dict],
    modules_from_doc: List[str],
    modules_from_vision: List[str],
    pages: List[Dict],
) -> List[Dict[str, Any]]:
    """Group components into modules."""
    # Determine module names
    all_module_names = set()
    for m in modules_from_doc:
        all_module_names.add(m)
    for m in modules_from_vision:
        all_module_names.add(m)

    # If no modules detected, infer from pages or use "Main"
    if not all_module_names:
        for page in pages:
            title = page.get("title", "")
            if title and title != "Untitled" and title != "Unknown Page":
                all_module_names.add(title)

    if not all_module_names:
        all_module_names.add("Main Module")

    module_names = sorted(all_module_names)

    # Group components by module (try matching by section/source)
    modules = []
    assigned = set()

    for mod_name in module_names:
        mod_name_lower = mod_name.lower()
        mod_components = []

        for i, comp in enumerate(components):
            if i in assigned:
                continue
            # Match by section, source, or label content
            section = (comp.get("section") or comp.get("source") or "").lower()
            label = (comp.get("label") or comp.get("text") or "").lower()

            if (mod_name_lower in section or
                mod_name_lower in label or
                any(word in section for word in mod_name_lower.split())):
                mod_components.append(comp)
                assigned.add(i)

        # Get pages for this module
        mod_pages = []
        for page in pages:
            page_title = (page.get("title") or "").lower()
            if mod_name_lower in page_title or any(word in page_title for word in mod_name_lower.split()):
                mod_pages.append(page.get("url") or page.get("title", ""))

        if not mod_pages:
            mod_pages = [page.get("url") or page.get("title", "") for page in pages[:1]]

        modules.append({
            "module_name": mod_name,
            "pages": mod_pages,
            "ui_components": mod_components,
            "flows": [],
            "validations_detected": _extract_validations_from_components(mod_components),
        })

    # Assign remaining unassigned components to the first module
    remaining = [components[i] for i in range(len(components)) if i not in assigned]
    if remaining and modules:
        modules[0]["ui_components"].extend(remaining)
        # Re-extract validations for the first module
        modules[0]["validations_detected"] = _extract_validations_from_components(
            modules[0]["ui_components"]
        )

    return modules


def build_ui_schema(
    dom_pages: Optional[List[Dict]] = None,
    vision_results: Optional[List[Dict]] = None,
    doc_extraction: Optional[Dict] = None,
    detected_flows: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Build a unified UI Schema from all source outputs.

    Parameters
    ----------
    dom_pages : list[dict], optional
        Pages from URL crawler with DOM components.
    vision_results : list[dict], optional
        Results from vision analyzer.
    doc_extraction : dict, optional
        Result from document extractor.
    detected_flows : list[dict], optional
        Detected user flows.

    Returns
    -------
    dict
        {
            "modules": [...],
            "total_components": int,
            "total_pages": int,
            "total_modules": int,
        }
    """
    all_components = []
    all_pages = []
    modules_from_doc = []
    modules_from_vision = []

    # ── Collect from DOM pages ────────────────────────────
    if dom_pages:
        for page in dom_pages:
            all_pages.append({
                "title": page.get("title", "Untitled"),
                "url": page.get("url", ""),
            })
            dom_comps = page.get("dom_components", {})
            for comp_type, items in dom_comps.items():
                for item in items:
                    item["source"] = "dom"
                    item["source_page"] = page.get("url", "")
                    if "type" not in item:
                        item["type"] = comp_type
                    all_components.append(item)

    # ── Collect from Vision results ───────────────────────
    if vision_results:
        for vision in vision_results:
            page_title = vision.get("page_title", "Vision Analysis")
            modules_from_vision.append(page_title)

            for comp in vision.get("components", []):
                comp["source"] = "vision"
                comp["source_page"] = vision.get("source", "")
                all_components.append(comp)

            if not all_pages or all(p.get("url") for p in all_pages):
                all_pages.append({
                    "title": page_title,
                    "url": vision.get("source", ""),
                })

    # ── Collect from Document extraction ──────────────────
    if doc_extraction:
        modules_from_doc = doc_extraction.get("modules_detected", [])

        for kw in doc_extraction.get("ui_keywords", []):
            all_components.append({
                "type": "keyword_detected",
                "label": kw,
                "source": "document",
            })

        for i, page_text in enumerate(doc_extraction.get("pages_text", [])[:10]):
            all_pages.append({
                "title": f"Document Section {i + 1}",
                "url": "",
                "text_preview": page_text[:200],
            })

    # ── Deduplicate components ────────────────────────────
    unique_components = _deduplicate_components(all_components)

    # ── Group into modules ────────────────────────────────
    modules = _group_into_modules(
        components=unique_components,
        modules_from_doc=modules_from_doc,
        modules_from_vision=modules_from_vision,
        pages=all_pages,
    )

    # ── Attach flows to modules ───────────────────────────
    if detected_flows:
        for flow in detected_flows:
            # Try to match flow to a module by keywords
            matched = False
            for mod in modules:
                mod_name_lower = mod["module_name"].lower()
                flow_name_lower = flow.get("name", "").lower()
                if any(word in mod_name_lower for word in flow_name_lower.split()):
                    mod["flows"].append(flow)
                    matched = True
                    break
            if not matched and modules:
                modules[0]["flows"].append(flow)

    # ── Build final schema ────────────────────────────────
    total_components = sum(len(m["ui_components"]) for m in modules)

    schema = {
        "modules": modules,
        "total_components": total_components,
        "total_pages": len(all_pages),
        "total_modules": len(modules),
    }

    logger.info(
        "UI Schema built: modules=%d, components=%d, pages=%d",
        schema["total_modules"], schema["total_components"], schema["total_pages"],
    )

    return schema
