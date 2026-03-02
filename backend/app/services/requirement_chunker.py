"""
Requirement Chunker Service
------------------------------
Splits large requirement documents into semantic chunks
for complete analysis. Merges parsed results from all chunks.
"""

import logging
import re
from typing import List

from app.schemas.schemas import ParsedRequirement

logger = logging.getLogger(__name__)

# Maximum characters per chunk — tuned for NLP keyword extraction
_MAX_CHUNK_SIZE = 2000


def chunk_requirement(text: str, max_chunk_size: int = _MAX_CHUNK_SIZE) -> List[str]:
    """
    Split a large requirement document into semantic chunks.

    Strategy:
    1. Split by double newline (paragraph boundaries)
    2. If any paragraph exceeds max_chunk_size, split by sentence
    3. Merge small consecutive paragraphs into a single chunk

    Returns list of text chunks, each ≤ max_chunk_size characters.
    """
    if len(text) <= max_chunk_size:
        return [text]

    # Step 1: Split by paragraph boundaries
    paragraphs = re.split(r"\n\s*\n", text.strip())

    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If single paragraph exceeds limit, split by sentences
        if len(para) > max_chunk_size:
            # Flush current chunk first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            sentences = re.split(r"(?<=[.!?])\s+", para)
            sentence_chunk = ""
            for sentence in sentences:
                if len(sentence_chunk) + len(sentence) + 1 > max_chunk_size:
                    if sentence_chunk:
                        chunks.append(sentence_chunk.strip())
                    sentence_chunk = sentence
                else:
                    sentence_chunk = (sentence_chunk + " " + sentence).strip()
            if sentence_chunk:
                chunks.append(sentence_chunk.strip())
            continue

        # Merge small paragraphs
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            current_chunk = (current_chunk + "\n\n" + para).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para

    # Flush final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    logger.info("Chunked requirement (%d chars) into %d chunks", len(text), len(chunks))
    return chunks


def merge_parsed_results(results: List[ParsedRequirement]) -> ParsedRequirement:
    """
    Merge ParsedRequirement objects from multiple chunks.

    - Union of all actions, fields and validations (deduplicated)
    - Module name: most frequently detected module, or first if tied
    """
    if len(results) == 1:
        return results[0]

    all_actions = []
    all_fields = []
    all_validations = []
    module_counts: dict = {}

    for pr in results:
        all_actions.extend(pr.actions)
        all_fields.extend(pr.fields)
        all_validations.extend(pr.validations)
        module_counts[pr.module] = module_counts.get(pr.module, 0) + 1

    # Pick the most common module
    best_module = max(module_counts, key=module_counts.get) if module_counts else "General"

    merged = ParsedRequirement(
        module=best_module,
        actions=sorted(set(all_actions)),
        fields=sorted(set(all_fields)),
        validations=sorted(set(all_validations)),
    )

    logger.info(
        "Merged %d chunk results: module=%s, actions=%d, fields=%d, validations=%d",
        len(results), merged.module, len(merged.actions), len(merged.fields), len(merged.validations),
    )
    return merged
