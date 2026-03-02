"""
Duplicate Detector Service
----------------------------
Checks new test cases against existing ones using TF-IDF cosine similarity.
Rejects or flags cases with >85% similarity to prevent repetition.
"""

import logging
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> List[str]:
    """Simple whitespace + lowercased tokenizer."""
    return re.findall(r"\b[a-z]+\b", text.lower())


def _build_vocab(documents: List[List[str]]) -> Dict[str, int]:
    """Build vocabulary mapping from tokenized documents."""
    vocab: Dict[str, int] = {}
    idx = 0
    for tokens in documents:
        for token in tokens:
            if token not in vocab:
                vocab[token] = idx
                idx += 1
    return vocab


def _tf_vector(tokens: List[str], vocab: Dict[str, int]) -> List[float]:
    """Build TF vector for a document."""
    vec = [0.0] * len(vocab)
    for token in tokens:
        if token in vocab:
            vec[vocab[token]] += 1.0
    # Normalize
    total = sum(vec)
    if total > 0:
        vec = [v / total for v in vec]
    return vec


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def check_duplicate(
    new_case: Dict[str, Any],
    existing_cases: List[Dict[str, Any]],
    threshold: float = 0.85,
) -> Tuple[float, bool]:
    """
    Check if a new test case is a duplicate of any existing case.

    Returns (highest_similarity_score, is_duplicate).
    """
    if not existing_cases:
        return 0.0, False

    new_tokens = _tokenize(new_case.get("scenario", ""))
    existing_tokens = [_tokenize(ec.get("scenario", "")) for ec in existing_cases]

    all_docs = [new_tokens] + existing_tokens
    vocab = _build_vocab(all_docs)

    if not vocab:
        return 0.0, False

    new_vec = _tf_vector(new_tokens, vocab)
    max_sim = 0.0

    for et in existing_tokens:
        existing_vec = _tf_vector(et, vocab)
        sim = _cosine_similarity(new_vec, existing_vec)
        if sim > max_sim:
            max_sim = sim

    return round(max_sim, 4), max_sim > threshold


def deduplicate_batch(
    test_cases: List[Dict[str, Any]],
    threshold: float = 0.85,
) -> List[Dict[str, Any]]:
    """
    Remove near-duplicate test cases from a batch.
    Keeps the first occurrence, rejects subsequent duplicates.
    Attaches duplicate_score to each surviving case.
    """
    unique: List[Dict[str, Any]] = []
    rejected = 0

    for tc in test_cases:
        score, is_dup = check_duplicate(tc, unique, threshold)
        tc["duplicate_score"] = score
        if is_dup:
            rejected += 1
            logger.debug("Rejected duplicate (sim=%.2f): %s", score, tc.get("scenario", "")[:60])
        else:
            unique.append(tc)

    logger.info(
        "Dedup: %d input → %d unique, %d rejected (threshold=%.2f)",
        len(test_cases), len(unique), rejected, threshold,
    )
    return unique
