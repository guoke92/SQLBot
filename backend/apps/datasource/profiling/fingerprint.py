"""Schema fingerprints for profiling invalidation."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any


def table_schema_fingerprint(table: Any, fields: Sequence[Any]) -> str:
    """Hash structural identity of a local catalog table (names/types only)."""
    parts = [
        str(getattr(table, "database_name", None) or ""),
        str(getattr(table, "table_name", None) or ""),
    ]
    for field in sorted(
        fields,
        key=lambda item: (
            int(getattr(item, "field_index", 0) or 0),
            str(getattr(item, "field_name", "") or ""),
        ),
    ):
        parts.append(str(getattr(field, "field_name", None) or ""))
        parts.append(str(getattr(field, "field_type", None) or ""))
    raw = "\x1f".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def content_fingerprint(text: str) -> str:
    """SHA-256 of embedding / prompt source text."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def format_profile_field_bits(
    *,
    null_rate: float | None = None,
    distinct_ratio: float | None = None,
    min_value: Any = None,
    max_value: Any = None,
    top_values: list[Any] | None = None,
    include_topk: bool = False,
    topk_limit: int = 3,
) -> list[str]:
    """Compact profile fragments for PROMPT schema lines (READY only)."""
    bits: list[str] = []
    if null_rate is not None:
        try:
            bits.append(f"null={float(null_rate):.2f}")
        except (TypeError, ValueError):
            pass
    ndv: float | None = None
    if distinct_ratio is not None:
        try:
            ndv = float(distinct_ratio)
            bits.append(f"ndv={ndv:.2f}")
        except (TypeError, ValueError):
            pass
    if min_value is not None or max_value is not None:
        bits.append(f"range=[{min_value},{max_value}]")
    if include_topk and top_values and (ndv is None or ndv <= 0.05):
        values: list[str] = []
        for item in top_values[: max(0, int(topk_limit))]:
            if isinstance(item, dict):
                raw = item.get("value")
            else:
                raw = item
            if raw is None:
                continue
            text = str(raw).strip()
            if not text:
                continue
            values.append(text[:32])
        if values:
            bits.append("topk=" + "|".join(values))
    return bits
