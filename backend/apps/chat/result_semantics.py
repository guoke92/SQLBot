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


def _axis_values(chart: Mapping[str, Any] | None, key: str) -> set[str]:
    axis = chart.get("axis") if isinstance(chart, Mapping) else None
    if not isinstance(axis, Mapping):
        return set()
    raw = axis.get(key)
    items = raw if isinstance(raw, list) else [raw]
    return {
        str(item.get("value"))
        for item in items
        if isinstance(item, Mapping) and item.get("value")
    }


def classify_field_roles(
    fields: Sequence[str],
    fields_info: Sequence[Mapping[str, Any]] | None,
    chart: Mapping[str, Any] | None,
) -> FieldRoles:
    """Prefer chart bindings; use conservative type/name fallback for tables."""
    known = {str(field) for field in fields}
    chart_metrics = _axis_values(chart, "y") & known
    chart_dimensions = (
        _axis_values(chart, "x") | _axis_values(chart, "series")
    ) & known
    if chart_metrics:
        return {
            "metrics": chart_metrics,
            "dimensions": known - chart_metrics,
        }

    numeric = {
        str(info.get("name"))
        for info in fields_info or []
        if info.get("name") and bool(info.get("is_numeric", False))
    } & known
    metrics: set[str] = set()
    for field in numeric:
        if _METRIC_HINT_RE.search(field):
            metrics.add(field)
        elif not _DIMENSION_HINT_RE.search(field):
            # With no chart semantics, retain the historical numeric fallback
            # only for fields that do not look like identifiers/time buckets.
            metrics.add(field)
    return {
        "metrics": metrics,
        "dimensions": (known - metrics) | chart_dimensions,
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
