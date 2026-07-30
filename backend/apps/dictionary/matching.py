"""Datasource-neutral normalization and match-span helpers."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


def normalize_dictionary_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").strip().lower()
    return re.sub(r"\s+", " ", normalized)


def best_matching_span(question: str, value: str, *, min_length: int = 3) -> str:
    """Return the longest common Unicode span for a fuzzy dictionary hit."""
    normalized_question = normalize_dictionary_value(question)
    normalized_value = normalize_dictionary_value(value)
    if normalized_value in normalized_question:
        return normalized_value
    match = SequenceMatcher(
        None,
        normalized_question,
        normalized_value,
        autojunk=False,
    ).find_longest_match()
    if match.size < min_length:
        return ""
    return normalized_question[match.a : match.a + match.size]
