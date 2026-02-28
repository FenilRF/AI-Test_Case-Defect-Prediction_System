"""
Folder-Based Storage Service
-------------------------------
Creates per-requirement folders under ``test_cases/`` and persists:
  • requirement.txt
  • design.txt          (if design text provided)
  • test_cases.json
  • risk_analysis.json
  • exported_excel.xlsx  (on explicit Save-to-Excel)

Folder name format:  ``<module>_<timestamp>``
All names are sanitised to prevent path traversal.
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Base directory for all requirement folders (relative to backend root)
_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "test_cases",
)


def _sanitise_name(name: str) -> str:
    """
    Sanitise a string for safe use as a folder / file name.
    Removes path separators and special characters.
    """
    # Replace unsafe chars with underscore
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    # Collapse multiple underscores / spaces
    safe = re.sub(r"[_\s]+", "_", safe).strip("_. ")
    return safe[:80] or "Unnamed"


def get_base_dir() -> str:
    """Return the absolute path of the test_cases base directory."""
    return _BASE_DIR


def ensure_base_dir() -> None:
    """Create the test_cases base directory if it doesn't exist."""
    os.makedirs(_BASE_DIR, exist_ok=True)
    logger.info("Ensured base storage directory: %s", _BASE_DIR)


def create_requirement_folder(
    module_name: str,
    requirement_text: str,
    design_text: Optional[str] = None,
    test_cases: Optional[List[Dict[str, Any]]] = None,
    risk_analysis: Optional[Dict[str, Any]] = None,
    defect_prediction: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new folder for a requirement submission and save all artefacts.

    Parameters
    ----------
    module_name : str
        Detected module name (used in folder name).
    requirement_text : str
        Raw requirement text.
    design_text : str, optional
        Design document text.
    test_cases : list[dict], optional
        Generated test case dicts.
    risk_analysis : dict, optional
        Risk analysis report dict.

    Returns
    -------
    str
        Absolute path of the created folder.
    """
    ensure_base_dir()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    folder_name = f"REQ_{timestamp}_{_sanitise_name(module_name)}"
    folder_path = os.path.join(_BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    logger.info("Created requirement folder: %s", folder_path)

    # ── Save requirement.txt ────────────────────────────
    req_file = os.path.join(folder_path, "requirement.txt")
    with open(req_file, "w", encoding="utf-8") as f:
        f.write(requirement_text)
    logger.info("Saved requirement.txt → %s", req_file)

    # ── Save design.txt (if provided) ───────────────────
    if design_text and design_text.strip():
        design_file = os.path.join(folder_path, "design.txt")
        with open(design_file, "w", encoding="utf-8") as f:
            f.write(design_text)
        logger.info("Saved design.txt → %s", design_file)

    # ── Save test_cases.json ────────────────────────────
    if test_cases is not None:
        tc_file = os.path.join(folder_path, "test_cases.json")
        with open(tc_file, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, indent=2, default=str)
        logger.info("Saved test_cases.json (%d cases) → %s", len(test_cases), tc_file)

    # ── Save risk_analysis.json ─────────────────────────
    if risk_analysis is not None:
        risk_file = os.path.join(folder_path, "risk_analysis.json")
        with open(risk_file, "w", encoding="utf-8") as f:
            json.dump(risk_analysis, f, indent=2, default=str)
        logger.info("Saved risk_analysis.json → %s", risk_file)

    if defect_prediction is not None:
        pred_file = os.path.join(folder_path, "defect_prediction.json")
        with open(pred_file, "w", encoding="utf-8") as f:
            json.dump(defect_prediction, f, indent=2, default=str)
        logger.info("Saved defect_prediction.json → %s", pred_file)

    return folder_path


def save_excel_to_folder(folder_path: str, excel_bytes: bytes) -> str:
    """
    Save exported Excel bytes into an existing requirement folder.

    Parameters
    ----------
    folder_path : str
        Absolute path to the requirement folder.
    excel_bytes : bytes
        Excel workbook bytes.

    Returns
    -------
    str
        Absolute path to the saved Excel file.
    """
    excel_file = os.path.join(folder_path, "exported_excel.xlsx")
    with open(excel_file, "wb") as f:
        f.write(excel_bytes)
    logger.info("Saved exported_excel.xlsx → %s", excel_file)
    return excel_file


def create_design_folder(
    module_name: Optional[str] = "Unknown"
) -> str:
    """
    Create a standalone design folder per upload.
    Returns the absolute path to the design folder.
    """
    ensure_base_dir()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    folder_name = f"DESIGN_{timestamp}_{_sanitise_name(module_name)}"
    design_path = os.path.join(_BASE_DIR, folder_name)

    os.makedirs(design_path, exist_ok=True)
    logger.info("Created design folder: %s", design_path)
    return design_path


def save_design_links(design_folder: str, urls: list) -> str:
    """
    Save design URLs as ``design_links.txt`` in the design folder.

    Returns
    -------
    str
        Absolute path to the saved txt file.
    """
    links_file = os.path.join(design_folder, "design_links.txt")
    with open(links_file, "w", encoding="utf-8") as f:
        for url in urls:
            f.write(f"{url}\n")
    logger.info("Saved design_links.txt (%d URLs) → %s", len(urls), links_file)
    return links_file

