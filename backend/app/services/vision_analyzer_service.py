"""
Vision Analyzer Service
--------------------------
Analyzes UI screenshots / images via Groq Llama 4 Scout (Vision LLM).

Extracts:
  • Form sections & field labels
  • Buttons & interactive elements
  • Navigation areas, tabs, breadcrumbs
  • Cards, tables, alerts
  • Layout zones (header, footer, sidebar, main content)
"""

import logging
import os
from typing import Any, Dict, List, Union

from app.services.groq_client import call_vision_llm

logger = logging.getLogger(__name__)

_VISION_SYSTEM_PROMPT = """You are an expert UI/UX analyst. Analyze the provided UI screenshot and extract ALL visible components into a structured JSON format.

You MUST return a valid JSON object with this exact structure:
{
  "page_title": "detected page title or description",
  "layout_zones": [
    {
      "zone": "header|sidebar|main_content|footer|modal|drawer",
      "description": "brief description of what this zone contains"
    }
  ],
  "components": [
    {
      "type": "form|button|input|dropdown|table|card|modal|navigation|tab|breadcrumb|alert|toast|tooltip|checkbox|radio|toggle|slider|date_picker|file_upload|search_bar|pagination|badge|chip|avatar|icon|progress_bar|stepper|accordion|carousel|chart|menu|link|image|video|text_block|divider|footer|header|sidebar",
      "label": "visible label text or aria-label",
      "section": "which layout zone or section this belongs to",
      "properties": {
        "placeholder": "placeholder text if visible",
        "required": true,
        "disabled": false,
        "validation_hint": "any visible validation messages"
      }
    }
  ],
  "navigation": [
    {
      "type": "navbar|sidebar|breadcrumb|tabs|footer_links",
      "items": ["item1", "item2", "..."]
    }
  ],
  "detected_validations": [
    "email format required",
    "password minimum 8 characters",
    "..."
  ],
  "detected_states": [
    "login form - empty state",
    "error state visible",
    "..."
  ]
}

Be thorough. Extract EVERY visible UI element. Include labels, placeholders, button text, navigation items, and any validation messages visible on screen."""


_VISION_USER_PROMPT = """Analyze this UI screenshot completely. Extract:
1. ALL form fields with their labels and types
2. ALL buttons with their text
3. ALL navigation elements (menus, tabs, breadcrumbs)
4. ALL tables with column headers
5. ALL cards/panels with content descriptions
6. ALL alerts, toasts, error messages
7. Layout structure (header, sidebar, main, footer)
8. Any visible validation rules or constraints
9. Interactive elements (dropdowns, checkboxes, toggles)
10. Any visible state information (loading, error, success)

Return the complete JSON analysis."""


def analyze_image(
    image_path: str,
    additional_context: str = "",
) -> Dict[str, Any]:
    """
    Analyze a single image file using the Vision LLM.

    Parameters
    ----------
    image_path : str
        Absolute path to the image file (PNG, JPG).
    additional_context : str
        Optional additional context about the image.

    Returns
    -------
    dict
        Structured UI analysis with components, layout, navigation, etc.
    """
    if not os.path.exists(image_path):
        logger.error("Image file not found: %s", image_path)
        return _empty_analysis(f"File not found: {image_path}")

    logger.info("Analyzing image via Vision LLM: %s", image_path)

    user_prompt = _VISION_USER_PROMPT
    if additional_context:
        user_prompt += f"\n\nAdditional context: {additional_context}"

    try:
        result = call_vision_llm(
            system_prompt=_VISION_SYSTEM_PROMPT,
            image_source=image_path,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=4096,
            expect_json=True,
        )

        # Validate and normalize the response
        if isinstance(result, dict):
            return _normalize_vision_result(result, image_path)
        else:
            logger.warning("Vision LLM returned non-dict result")
            return _empty_analysis("Vision analysis returned unexpected format")

    except Exception as e:
        logger.error("Vision analysis failed for %s: %s", image_path, e)
        return _empty_analysis(f"Vision analysis error: {str(e)}")


def analyze_image_bytes(
    image_bytes: bytes,
    image_name: str = "screenshot",
    additional_context: str = "",
) -> Dict[str, Any]:
    """
    Analyze image from raw bytes (e.g., Playwright screenshot).

    Parameters
    ----------
    image_bytes : bytes
        Raw image bytes.
    image_name : str
        Descriptive name for logging.
    additional_context : str
        Optional context.

    Returns
    -------
    dict
        Structured UI analysis.
    """
    logger.info("Analyzing image bytes via Vision LLM: %s (%d bytes)", image_name, len(image_bytes))

    user_prompt = _VISION_USER_PROMPT
    if additional_context:
        user_prompt += f"\n\nAdditional context: {additional_context}"

    try:
        result = call_vision_llm(
            system_prompt=_VISION_SYSTEM_PROMPT,
            image_source=image_bytes,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=4096,
            expect_json=True,
        )

        if isinstance(result, dict):
            return _normalize_vision_result(result, image_name)
        else:
            return _empty_analysis("Vision analysis returned unexpected format")

    except Exception as e:
        logger.error("Vision analysis failed for %s: %s", image_name, e)
        return _empty_analysis(f"Vision analysis error: {str(e)}")


def analyze_multiple_images(
    image_paths: List[str],
) -> List[Dict[str, Any]]:
    """Analyze multiple images sequentially."""
    results = []
    for path in image_paths:
        result = analyze_image(path)
        results.append(result)
    return results


def _normalize_vision_result(result: Dict, source: str) -> Dict[str, Any]:
    """Ensure all expected keys exist in the vision result."""
    normalized = {
        "source": source,
        "page_title": result.get("page_title", "Unknown Page"),
        "layout_zones": result.get("layout_zones", []),
        "components": result.get("components", []),
        "navigation": result.get("navigation", []),
        "detected_validations": result.get("detected_validations", []),
        "detected_states": result.get("detected_states", []),
        "total_components": len(result.get("components", [])),
    }
    return normalized


def _empty_analysis(reason: str) -> Dict[str, Any]:
    """Return an empty analysis structure with an error reason."""
    return {
        "source": "error",
        "page_title": "Analysis Failed",
        "layout_zones": [],
        "components": [],
        "navigation": [],
        "detected_validations": [],
        "detected_states": [],
        "total_components": 0,
        "error": reason,
    }
