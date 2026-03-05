"""
Design Intelligence Engine — Master Orchestrator
----------------------------------------------------
Coordinates the full design analysis and test generation pipeline:

  1. Detect input type (URL / Document / Image)
  2. Route to appropriate source handler
  3. Send images/screenshots to Vision Analyzer
  4. Build unified UI Schema
  5. Run Flow Detection
  6. Run LLM Test Generation with Enterprise Quality Filter
  7. Return complete enterprise output
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from app.services.document_extractor_service import extract_from_document
from app.services.vision_analyzer_service import analyze_image, analyze_multiple_images
from app.services.ui_schema_builder import build_ui_schema
from app.services.flow_detection_engine import detect_flows
from app.services.llm_test_generator import generate_enterprise_tests

logger = logging.getLogger(__name__)

# File extension categories
_DOC_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".txt"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _classify_input_type(
    file_paths: List[str],
    urls: List[str],
    design_text: Optional[str],
) -> str:
    """Determine the primary input type."""
    if urls:
        return "url"
    if file_paths:
        exts = {os.path.splitext(f)[1].lower() for f in file_paths}
        if exts & _IMAGE_EXTENSIONS:
            return "image"
        if exts & _DOC_EXTENSIONS:
            return "document"
    if design_text:
        return "text"
    return "unknown"


async def analyze_design_intelligent(
    file_paths: List[str] = None,
    urls: List[str] = None,
    design_text: Optional[str] = None,
    output_dir: str = "",
) -> Dict[str, Any]:
    """
    Main entry point — Full design intelligence pipeline (async).

    Parameters
    ----------
    file_paths : list[str], optional
        Paths to uploaded files (documents or images).
    urls : list[str], optional
        Design URLs to crawl.
    design_text : str, optional
        Raw design text input.
    output_dir : str
        Directory for saving screenshots and artefacts.

    Returns
    -------
    dict
        {
            "source_type": str,
            "total_pages_analyzed": int,
            "total_ui_components_detected": int,
            "total_flows_detected": int,
            "total_test_cases_generated": int,
            "enterprise_coverage_percentage": float,
            "ui_schema": {...},
            "detected_flows": {...},
            "test_generation_result": {...},
            "analysis_summary": str,
        }
    """
    file_paths = file_paths or []
    urls = urls or []

    source_type = _classify_input_type(file_paths, urls, design_text)
    logger.info("=== Design Intelligence Engine Starting (source=%s) ===", source_type)

    dom_pages = []
    vision_results = []
    doc_extraction = None
    all_ui_keywords = []

    # ═════════════════════════════════════════════════════════
    # STEP 1: Source Handling
    # ═════════════════════════════════════════════════════════

    # ── URL Processing ────────────────────────────────────
    if urls:
        logger.info("Processing %d URL(s)...", len(urls))
        for url in urls:
            try:
                from app.services.url_crawler_service import crawl_url
                crawl_result = await crawl_url(url, output_dir, max_depth=3)
                crawl_pages = crawl_result.get("pages", [])
                dom_pages.extend(crawl_pages)

                # Send screenshots to Vision LLM
                for page in crawl_pages:
                    screenshot_path = page.get("screenshot_path")
                    if screenshot_path and os.path.exists(screenshot_path):
                        try:
                            vision_result = analyze_image(
                                screenshot_path,
                                additional_context=f"Page: {page.get('title', '')} at {page.get('url', '')}",
                            )
                            vision_results.append(vision_result)
                        except Exception as ve:
                            logger.warning("Vision analysis failed for %s: %s", screenshot_path, ve)

            except Exception as e:
                logger.warning("URL crawl failed for %s: %s", url, e)
                # Add minimal entry
                dom_pages.append({
                    "url": url,
                    "title": "URL provided (crawl failed)",
                    "dom_components": {},
                    "error": str(e),
                })

    # ── File Processing ───────────────────────────────────
    if file_paths:
        image_paths = []
        doc_paths = []

        for fp in file_paths:
            ext = os.path.splitext(fp)[1].lower()
            if ext in _IMAGE_EXTENSIONS:
                image_paths.append(fp)
            elif ext in _DOC_EXTENSIONS:
                doc_paths.append(fp)

        # Process images via Vision LLM
        if image_paths:
            logger.info("Processing %d image(s) via Vision LLM...", len(image_paths))
            for img_path in image_paths:
                try:
                    vision_result = analyze_image(img_path)
                    vision_results.append(vision_result)
                except Exception as e:
                    logger.warning("Image analysis failed for %s: %s", img_path, e)

        # Process documents
        if doc_paths:
            logger.info("Processing %d document(s)...", len(doc_paths))
            # Merge all document extractions
            all_pages_text = []
            all_doc_keywords = []
            all_doc_modules = []
            all_doc_flows = []

            for doc_path in doc_paths:
                try:
                    doc_result = extract_from_document(doc_path)
                    all_pages_text.extend(doc_result.get("pages_text", []))
                    all_doc_keywords.extend(doc_result.get("ui_keywords", []))
                    all_doc_modules.extend(doc_result.get("modules_detected", []))
                    all_doc_flows.extend(doc_result.get("flows", []))
                except Exception as e:
                    logger.warning("Document extraction failed for %s: %s", doc_path, e)

            doc_extraction = {
                "pages_text": all_pages_text,
                "total_pages": len(all_pages_text),
                "ui_keywords": sorted(set(all_doc_keywords)),
                "modules_detected": sorted(set(all_doc_modules)),
                "flows": all_doc_flows,
            }
            all_ui_keywords.extend(all_doc_keywords)

    # ── Text input Processing ─────────────────────────────
    if design_text and design_text.strip():
        logger.info("Processing raw design text (%d chars)...", len(design_text))
        # Treat as a lightweight document
        from app.services.document_extractor_service import (
            _detect_ui_keywords,
            _detect_modules,
            _detect_flows,
        )
        text_keywords = _detect_ui_keywords(design_text)
        text_modules = _detect_modules([design_text])
        text_flows = _detect_flows(text_keywords)

        if doc_extraction is None:
            doc_extraction = {
                "pages_text": [design_text],
                "total_pages": 1,
                "ui_keywords": text_keywords,
                "modules_detected": text_modules,
                "flows": text_flows,
            }
        else:
            doc_extraction["pages_text"].append(design_text)
            doc_extraction["ui_keywords"] = sorted(
                set(doc_extraction["ui_keywords"] + text_keywords)
            )
            doc_extraction["modules_detected"] = sorted(
                set(doc_extraction["modules_detected"] + text_modules)
            )
            doc_extraction["flows"].extend(text_flows)

        all_ui_keywords.extend(text_keywords)

    # ═════════════════════════════════════════════════════════
    # STEP 2: Build Unified UI Schema
    # ═════════════════════════════════════════════════════════
    logger.info("Building unified UI Schema...")
    ui_schema = build_ui_schema(
        dom_pages=dom_pages if dom_pages else None,
        vision_results=vision_results if vision_results else None,
        doc_extraction=doc_extraction,
    )

    # ═════════════════════════════════════════════════════════
    # STEP 3: Flow Detection
    # ═════════════════════════════════════════════════════════
    logger.info("Running flow detection...")
    detected_flows = detect_flows(
        ui_schema=ui_schema,
        ui_keywords=all_ui_keywords,
    )

    # Attach flows back to schema
    ui_schema_with_flows = build_ui_schema(
        dom_pages=dom_pages if dom_pages else None,
        vision_results=vision_results if vision_results else None,
        doc_extraction=doc_extraction,
        detected_flows=detected_flows.get("primary_flows", []),
    )

    # ═════════════════════════════════════════════════════════
    # STEP 4: Enterprise Test Generation via LLM
    # ═════════════════════════════════════════════════════════
    logger.info("Generating enterprise test cases via LLM...")
    try:
        test_result = generate_enterprise_tests(
            ui_schema=ui_schema_with_flows,
            detected_flows=detected_flows,
        )
    except Exception as e:
        logger.error("Enterprise test generation failed: %s", e)
        test_result = {
            "test_cases": [],
            "coverage": {
                "total_test_cases": 0,
                "enterprise_coverage_percentage": 0.0,
                "type_distribution": {},
                "module_distribution": {},
                "level_distribution": {},
                "missing_coverage": [],
            },
            "total_test_cases": 0,
            "modules_grouped": {},
            "error": str(e),
        }

    # ═════════════════════════════════════════════════════════
    # STEP 5: Build Final Output
    # ═════════════════════════════════════════════════════════
    total_pages = ui_schema_with_flows.get("total_pages", 0)
    total_components = ui_schema_with_flows.get("total_components", 0)
    total_flows = detected_flows.get("total_flows", 0)
    total_tests = test_result.get("total_test_cases", 0)
    coverage_pct = test_result.get("coverage", {}).get("enterprise_coverage_percentage", 0.0)

    # Summary
    summary_parts = [
        f"Analyzed {total_pages} page(s)",
        f"detected {total_components} UI component(s)",
        f"identified {total_flows} flow(s)",
        f"generated {total_tests} enterprise test case(s)",
        f"with {coverage_pct:.1f}% coverage",
    ]
    summary = ", ".join(summary_parts) + "."

    result = {
        "source_type": source_type,
        "total_pages_analyzed": total_pages,
        "total_ui_components_detected": total_components,
        "total_flows_detected": total_flows,
        "total_test_cases_generated": total_tests,
        "enterprise_coverage_percentage": coverage_pct,
        "ui_schema": ui_schema_with_flows,
        "detected_flows": detected_flows,
        "test_generation_result": test_result,
        "analysis_summary": summary,
    }

    # Save analysis to output dir
    if output_dir:
        try:
            analysis_file = os.path.join(output_dir, "intelligence_analysis.json")
            with open(analysis_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
            logger.info("Analysis saved to %s", analysis_file)
        except Exception as e:
            logger.warning("Could not save analysis JSON: %s", e)

    logger.info("=== Design Intelligence Engine Complete ===")
    logger.info("Summary: %s", summary)

    return result
