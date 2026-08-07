"""Shared ranking helpers for schema vector recall.

Table / DS recall is in-process cosine over stored JSON vectors (not
pgvector). Terminology and data-training use SQL thresholds; this module
gives schema recall the same *shape*: similarity floor + top-K, with a
deterministic fallback when vectors are missing or all scores are weak.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def select_by_similarity(
    candidates: list[T],
    *,
    score_of: Callable[[T], float],
    threshold: float,
    top_count: int,
    has_vector: Callable[[T], bool] | None = None,
) -> list[T]:
    """Rank ``candidates`` and keep those at/above ``threshold``.

    Rules:
    * Prefer items with a usable vector and ``score >= threshold``, top-K.
    * If none clear the floor but some have vectors, keep the single best
      (best-effort continuity for NLQ).
    * If no usable vectors exist, return the first ``top_count`` candidates
      in input order (stable catalog prefix — never dump the whole list).
    """
    limit = max(1, int(top_count))
    if not candidates:
        return []

    def _has_vector(item: T) -> bool:
        if has_vector is None:
            return True
        return bool(has_vector(item))

    scored = [item for item in candidates if _has_vector(item)]
    if not scored:
        return candidates[:limit]

    scored.sort(key=lambda item: float(score_of(item)), reverse=True)
    above = [
        item for item in scored if float(score_of(item)) >= float(threshold)
    ][:limit]
    if above:
        return above
    return scored[:1]
