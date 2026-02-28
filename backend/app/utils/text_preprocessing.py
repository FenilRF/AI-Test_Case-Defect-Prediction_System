"""
Text Preprocessing Utilities
------------------------------
Low-level NLP helpers used by the NLP service:
  • tokenisation
  • stop-word removal
  • lemmatisation (via NLTK)
"""

import re
import logging
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# ── One-time NLTK data download (safe to call multiple times) ──
_NLTK_PACKAGES = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]


def ensure_nltk_data() -> None:
    """Download required NLTK datasets if missing."""
    for pkg in _NLTK_PACKAGES:
        try:
            nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
        except LookupError:
            logger.info("Downloading NLTK package: %s", pkg)
            nltk.download(pkg, quiet=True)


ensure_nltk_data()

# ── Initialise tools ────────────────────────────────────────
_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """Lowercase, strip special chars, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Tokenise cleaned text into a word list."""
    return word_tokenize(clean_text(text))


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove English stop-words from a token list."""
    return [t for t in tokens if t not in _stop_words]


def lemmatize(tokens: List[str]) -> List[str]:
    """Lemmatise tokens to their dictionary root form."""
    return [_lemmatizer.lemmatize(t) for t in tokens]


def preprocess(text: str) -> List[str]:
    """Full pipeline: clean → tokenise → remove stop-words → lemmatise."""
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)
    return tokens
