"""Classify query result fields by semantic role for quality assessment."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal, TypedDict

FieldRole = Literal["metric", "dimension"]


class FieldRoles(TypedDict):
    metrics: set[str]
    dimensions: set[str]


class ResultWindow(TypedDict):
    row_count: int
    limit: int | None
    truncated: bool
    truncation_reason: str | None


_METRIC_HINT_RE = re.compile(
    r"(?:^|_)(?:count|sum|total|amount|avg|average|mean|rate|ratio|"
    r"workload|duration|cost|price|score|quantity|qty)(?:$|_)|"
    r"(?:数量|总数|合计|金额|占比|比率|工时|工作量|均值|平均值|得分)$",
    re.IGNORECASE,
)
_DIMENSION_HINT_RE = re.compile(
    r"(?:^|_)(?:id|code|year|month|day|date|time|number|no|index)(?:$|_)|"
    r"(?:编号|编码|序号|年份|月份|日期|时间)$",
    re.IGNORECASE,
)


def classify_field_roles(
    fields: Sequence[str],
    fields_info: Sequence[Mapping[str, Any]] | None,
    role_hints: Mapping[str, FieldRole] | None = None,
) -> FieldRoles:
    """Classify result semantics, preferring confirmed contract roles."""
    known = {str(field) for field in fields}
    normalized_fields = {field.casefold(): field for field in known}
    explicit_roles = {
        normalized_fields[name.casefold()]: role
        for name, role in (role_hints or {}).items()
        if name.casefold() in normalized_fields
    }
    numeric = {
        str(info.get("name"))
        for info in fields_info or []
        if info.get("name") and bool(info.get("is_numeric", False))
    } & known
    metrics = {field for field, role in explicit_roles.items() if role == "metric"}
    for field in numeric:
        if field in explicit_roles:
            continue
        if _METRIC_HINT_RE.search(field):
            metrics.add(field)
        elif not _DIMENSION_HINT_RE.search(field):
            # With no chart semantics, retain the historical numeric fallback
            # only for fields that do not look like identifiers/time buckets.
            metrics.add(field)
    return {
        "metrics": metrics,
        "dimensions": known - metrics,
    }


def apply_display_window(
    rows: list[dict[str, Any]],
    *,
    row_limit: int | None,
) -> tuple[list[dict[str, Any]], ResultWindow]:
    """Apply a bounded result window without claiming an unknown total."""
    total = len(rows)
    limit = int(row_limit) if row_limit and row_limit > 0 else None
    # Exactly hitting the configured ceiling is conservatively presented as a
    # bounded result because the exact total is intentionally not queried.
    truncated = bool(limit is not None and total >= limit)
    displayed = rows[:limit] if truncated and limit is not None else rows
    return displayed, {
        "row_count": len(displayed),
        "limit": limit if truncated else None,
        "truncated": truncated,
        "truncation_reason": "query_limit" if truncated else None,
    }


def read_result_window(
    result: Mapping[str, Any],
    returned_rows: Sequence[Mapping[str, Any]],
) -> ResultWindow:
    """Read bounded result metadata without inferring an unknown total."""
    row_count = len(returned_rows)
    truncated = bool(result.get("truncated"))
    raw_limit = result.get("limit")
    limit = int(raw_limit) if raw_limit is not None else None
    reason = result.get("truncation_reason")
    if truncated and not reason and limit is not None:
        reason = "query_limit"
    return {
        "row_count": row_count,
        "limit": limit if truncated else None,
        "truncated": truncated,
        "truncation_reason": str(reason) if reason else None,
    }
