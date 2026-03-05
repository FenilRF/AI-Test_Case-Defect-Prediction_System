"""
Groq LLM Client
------------------
Reusable wrapper for Groq API calls:
  • Text LLM   → gpt-oss-120b
  • Vision LLM  → Llama 4 Scout

Handles JSON parsing, retries, and chunked payloads.
"""

import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.config import get_settings

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY_BASE = 2  # exponential backoff base (seconds)


def _get_groq_client():
    """Lazily create and return a Groq client."""
    try:
        from groq import Groq
    except ImportError:
        raise ImportError(
            "groq package is not installed. Run: pip install groq>=0.12.0"
        )

    settings = get_settings()
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is not set. Add a valid key to backend/.env"
        )
    return Groq(api_key=settings.GROQ_API_KEY)


def _parse_json_from_response(text: str) -> Union[Dict, List]:
    """Extract JSON from an LLM response that may contain markdown fences."""
    # Try direct parse first
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding first { or [ and matching to last } or ]
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue

    logger.warning("Could not parse JSON from LLM response: %s...", text[:200])
    return {"raw_text": text}


def call_text_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 8192,
    expect_json: bool = True,
) -> Union[Dict, List, str]:
    """
    Call Groq text model (gpt-oss-120b).

    Parameters
    ----------
    system_prompt : str
        System-level instructions.
    user_prompt : str
        User content / data to process.
    temperature : float
        Sampling temperature (lower = more deterministic).
    max_tokens : int
        Maximum response tokens.
    expect_json : bool
        If True, parse the response as JSON.

    Returns
    -------
    dict | list | str
        Parsed JSON or raw text.
    """
    settings = get_settings()
    client = _get_groq_client()
    model = settings.GROQ_TEXT_MODEL

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            logger.info(
                "Groq text call attempt %d/%d (model=%s, prompt_len=%d)",
                attempt, _MAX_RETRIES, model, len(user_prompt),
            )
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            logger.info("Groq text response received (%d chars)", len(content))

            if expect_json:
                return _parse_json_from_response(content)
            return content

        except Exception as e:
            logger.warning("Groq text call attempt %d failed: %s", attempt, e)
            if attempt < _MAX_RETRIES:
                delay = _RETRY_DELAY_BASE ** attempt
                logger.info("Retrying in %ds...", delay)
                time.sleep(delay)
            else:
                logger.error("All Groq text call attempts exhausted.")
                raise


def call_vision_llm(
    system_prompt: str,
    image_source: Union[str, bytes],
    user_prompt: str = "Analyze this UI screenshot and extract all components.",
    temperature: float = 0.2,
    max_tokens: int = 4096,
    expect_json: bool = True,
) -> Union[Dict, List, str]:
    """
    Call Groq vision model (Llama 4 Scout) with an image.

    Parameters
    ----------
    system_prompt : str
        System instructions for the vision analysis.
    image_source : str | bytes
        File path (str) or raw image bytes.
    user_prompt : str
        Text to accompany the image.
    temperature : float
        Sampling temperature.
    max_tokens : int
        Max response tokens.
    expect_json : bool
        If True, parse response as JSON.

    Returns
    -------
    dict | list | str
        Parsed JSON or raw text.
    """
    settings = get_settings()
    client = _get_groq_client()
    model = settings.GROQ_VISION_MODEL

    # Convert image to base64
    if isinstance(image_source, str):
        path = Path(image_source)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_source}")
        image_bytes = path.read_bytes()
        # Detect MIME type
        suffix = path.suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        mime_type = mime_map.get(suffix, "image/png")
    elif isinstance(image_source, bytes):
        image_bytes = image_source
        mime_type = "image/png"
    else:
        raise TypeError("image_source must be a file path (str) or bytes")

    b64_data = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_data}"

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            logger.info(
                "Groq vision call attempt %d/%d (model=%s, img_size=%d bytes)",
                attempt, _MAX_RETRIES, model, len(image_bytes),
            )
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            },
                        ],
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            logger.info("Groq vision response received (%d chars)", len(content))

            if expect_json:
                return _parse_json_from_response(content)
            return content

        except Exception as e:
            logger.warning("Groq vision call attempt %d failed: %s", attempt, e)
            if attempt < _MAX_RETRIES:
                delay = _RETRY_DELAY_BASE ** attempt
                logger.info("Retrying in %ds...", delay)
                time.sleep(delay)
            else:
                logger.error("All Groq vision call attempts exhausted.")
                raise


def call_text_llm_chunked(
    system_prompt: str,
    chunks: List[str],
    temperature: float = 0.3,
    max_tokens: int = 8192,
) -> List[Union[Dict, List]]:
    """
    Process multiple text chunks through the text LLM in sequence.
    Used for performance control when >20 pages are detected.

    Returns a list of parsed results, one per chunk.
    """
    results = []
    for i, chunk in enumerate(chunks, 1):
        logger.info("Processing chunk %d/%d (%d chars)", i, len(chunks), len(chunk))
        result = call_text_llm(
            system_prompt=system_prompt,
            user_prompt=chunk,
            temperature=temperature,
            max_tokens=max_tokens,
            expect_json=True,
        )
        results.append(result)
    return results
