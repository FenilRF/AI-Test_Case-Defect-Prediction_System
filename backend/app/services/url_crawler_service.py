"""
URL Crawler Service
-----------------------
Crawls web URLs for design analysis:
  • Detects Figma vs normal web URLs
  • Extracts DOM structure (forms, inputs, buttons, etc.)
  • Captures screenshots per page
  • Crawls internal links (depth limit = 3)

Uses Playwright for headless browser automation when available,
falls back to requests + BeautifulSoup for basic extraction.
"""

import logging
import os
import re
import hashlib
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

# ── DOM component selectors ──────────────────────────────────
_COMPONENT_SELECTORS = {
    "forms": "form",
    "inputs": "input, textarea",
    "buttons": "button, [type='submit'], [type='button'], [role='button']",
    "dropdowns": "select, [role='combobox'], [role='listbox']",
    "tables": "table",
    "modals": "[role='dialog'], .modal, [class*='modal']",
    "navigation": "nav, [role='navigation']",
    "tabs": "[role='tablist'], [role='tab']",
    "tooltips": "[role='tooltip'], [data-tooltip], [title]",
    "alerts": "[role='alert'], .alert, [class*='alert'], [class*='toast']",
    "breadcrumbs": "[aria-label='breadcrumb'], .breadcrumb, [class*='breadcrumb']",
    "links": "a[href]",
    "images": "img",
    "checkboxes": "[type='checkbox']",
    "radio_buttons": "[type='radio']",
    "sliders": "[type='range'], [role='slider']",
    "cards": "[class*='card'], .card",
    "headers": "header, h1, h2, h3",
    "footers": "footer",
    "sidebars": "aside, [class*='sidebar'], [role='complementary']",
}


def _is_figma_url(url: str) -> bool:
    """Check if a URL is a Figma design link."""
    parsed = urlparse(url)
    return "figma.com" in parsed.hostname if parsed.hostname else False


def _is_same_domain(url: str, base_url: str) -> bool:
    """Check if url belongs to the same domain as base_url."""
    try:
        return urlparse(url).hostname == urlparse(base_url).hostname
    except Exception:
        return False


async def _crawl_with_playwright(
    url: str,
    output_dir: str,
    max_depth: int = 3,
) -> List[Dict[str, Any]]:
    """
    Crawl a URL using Playwright headless browser.
    Extracts DOM components and captures screenshots.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("Playwright not installed, falling back to basic extraction")
        return _crawl_with_requests(url)

    pages_data = []
    visited: Set[str] = set()
    to_visit = [(url, 0)]  # (url, depth)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )

            while to_visit and len(visited) < 20:  # Cap at 20 pages
                current_url, depth = to_visit.pop(0)

                if current_url in visited:
                    continue
                visited.add(current_url)

                logger.info("Crawling page [depth=%d]: %s", depth, current_url)

                try:
                    page = await context.new_page()
                    await page.goto(current_url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(2000)  # Wait for dynamic content

                    # Capture screenshot
                    url_hash = hashlib.md5(current_url.encode()).hexdigest()[:8]
                    screenshot_name = f"screenshot_{url_hash}.png"
                    screenshot_path = os.path.join(output_dir, screenshot_name)
                    await page.screenshot(path=screenshot_path, full_page=True)
                    logger.info("Screenshot saved: %s", screenshot_path)

                    # Extract DOM components
                    components = await _extract_dom_components(page)

                    # Get page title
                    title = await page.title()

                    page_data = {
                        "url": current_url,
                        "title": title or "Untitled",
                        "depth": depth,
                        "screenshot_path": screenshot_path,
                        "dom_components": components,
                    }
                    pages_data.append(page_data)

                    # Find internal links for further crawling
                    if depth < max_depth:
                        links = await page.eval_on_selector_all(
                            "a[href]",
                            "elements => elements.map(e => e.href).filter(h => h && h.startsWith('http'))"
                        )
                        for link in links:
                            if _is_same_domain(link, url) and link not in visited:
                                # Skip anchor links, assets, etc.
                                parsed = urlparse(link)
                                if not any(parsed.path.endswith(ext) for ext in
                                           ['.pdf', '.png', '.jpg', '.css', '.js', '.zip', '.svg']):
                                    to_visit.append((link, depth + 1))

                    await page.close()

                except Exception as e:
                    logger.warning("Failed to crawl %s: %s", current_url, e)
                    continue

            await browser.close()

    except Exception as e:
        logger.error("Playwright crawling failed: %s", e)
        return _crawl_with_requests(url)

    return pages_data


async def _extract_dom_components(page) -> Dict[str, List[Dict]]:
    """Extract DOM components from a Playwright page."""
    components = {}

    for comp_type, selector in _COMPONENT_SELECTORS.items():
        try:
            elements = await page.query_selector_all(selector)
            items = []
            for el in elements[:50]:  # Cap per type
                try:
                    item = {
                        "tag": await el.evaluate("e => e.tagName.toLowerCase()"),
                        "type": comp_type,
                    }
                    # Get text content
                    text = await el.evaluate("e => e.textContent?.trim()?.substring(0, 200)")
                    if text:
                        item["text"] = text

                    # Get relevant attributes
                    for attr in ["id", "name", "class", "placeholder", "aria-label",
                                 "type", "role", "href", "value", "title", "alt"]:
                        val = await el.get_attribute(attr)
                        if val and val.strip():
                            item[attr] = val.strip()[:100]

                    items.append(item)
                except Exception:
                    continue

            if items:
                components[comp_type] = items

        except Exception:
            continue

    return components


def _crawl_with_requests(url: str) -> List[Dict[str, Any]]:
    """Fallback: extract components using requests + BeautifulSoup."""
    try:
        import httpx
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("httpx or beautifulsoup4 not installed for fallback crawl")
        return [{
            "url": url,
            "title": "URL provided",
            "depth": 0,
            "screenshot_path": None,
            "dom_components": {},
            "extraction_method": "none",
        }]

    try:
        response = httpx.get(url, follow_redirects=True, timeout=15.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        components = {}

        # Extract forms
        forms = []
        for form in soup.find_all("form"):
            form_data = {"tag": "form"}
            if form.get("id"):
                form_data["id"] = form["id"]
            if form.get("action"):
                form_data["action"] = form["action"]
            # Get child inputs
            fields = []
            for inp in form.find_all(["input", "select", "textarea"]):
                field = {
                    "tag": inp.name,
                    "type": inp.get("type", "text"),
                    "name": inp.get("name", ""),
                    "placeholder": inp.get("placeholder", ""),
                }
                label = inp.find_previous("label")
                if label:
                    field["label"] = label.get_text(strip=True)
                fields.append(field)
            form_data["fields"] = fields
            forms.append(form_data)
        if forms:
            components["forms"] = forms

        # Extract buttons
        buttons = []
        for btn in soup.find_all(["button", "input"]):
            if btn.name == "input" and btn.get("type") not in ("submit", "button"):
                continue
            buttons.append({
                "tag": btn.name,
                "text": btn.get_text(strip=True) or btn.get("value", ""),
                "type": btn.get("type", ""),
            })
        if buttons:
            components["buttons"] = buttons

        # Extract navigation
        navs = []
        for nav in soup.find_all("nav"):
            links = [a.get_text(strip=True) for a in nav.find_all("a") if a.get_text(strip=True)]
            navs.append({"tag": "nav", "items": links[:20]})
        if navs:
            components["navigation"] = navs

        # Extract tables
        tables = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            tables.append({"tag": "table", "headers": headers[:20]})
        if tables:
            components["tables"] = tables

        title = soup.title.string if soup.title else "Untitled"

        return [{
            "url": url,
            "title": title,
            "depth": 0,
            "screenshot_path": None,
            "dom_components": components,
            "extraction_method": "requests",
        }]

    except Exception as e:
        logger.error("Requests fallback crawl failed for %s: %s", url, e)
        return [{
            "url": url,
            "title": "URL provided (extraction failed)",
            "depth": 0,
            "screenshot_path": None,
            "dom_components": {},
            "extraction_method": "failed",
            "error": str(e),
        }]


async def crawl_url(
    url: str,
    output_dir: str,
    max_depth: int = 3,
) -> Dict[str, Any]:
    """
    Main entry point for URL crawling.

    Parameters
    ----------
    url : str
        The URL to crawl.
    output_dir : str
        Directory to save screenshots.
    max_depth : int
        Maximum crawl depth for internal links.

    Returns
    -------
    dict
        {
            "source_url": str,
            "is_figma": bool,
            "pages": [...],
            "total_pages": int,
        }
    """
    is_figma = _is_figma_url(url)

    logger.info("Starting URL crawl: %s (figma=%s, max_depth=%d)", url, is_figma, max_depth)

    os.makedirs(output_dir, exist_ok=True)

    pages = await _crawl_with_playwright(url, output_dir, max_depth)

    result = {
        "source_url": url,
        "is_figma": is_figma,
        "pages": pages,
        "total_pages": len(pages),
    }

    logger.info("URL crawl complete: %d pages extracted", len(pages))
    return result
