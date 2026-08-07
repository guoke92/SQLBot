"""Heuristic value scoring for semantic mining follow-ups."""

from __future__ import annotations

from typing import Any


def is_high_value_table(table: Any, *, field_count: int = 0) -> bool:
    """Cheap gate: large or richly-described tables get semantic follow-up."""
    rows = getattr(table, "approx_rows", None)
    try:
        row_n = int(rows) if rows is not None else 0
    except (TypeError, ValueError):
        row_n = 0
    comment = (
        getattr(table, "custom_comment", None)
        or getattr(table, "table_comment", None)
        or ""
    ).strip()
    if row_n >= 10_000:
        return True
    if field_count >= 12:
        return True
    if comment and row_n >= 100:
        return True
    return False
