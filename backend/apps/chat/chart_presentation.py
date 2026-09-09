"""Delivery chart selection: agent hint → heuristic gates → narrow LLM → table."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any, cast

import orjson
from langchain_core.messages import HumanMessage, SystemMessage

from apps.chat.presentation import ResultPresentation, chart_columns
from common.utils.utils import SQLBotLogUtil

LEGAL_CHART_TYPES = frozenset({"table", "line", "bar", "column", "pie"})

_NARROW_SYSTEM = (
    "You choose a chart config for SQL query results. "
    "Return ONLY compact JSON, no markdown. "
    "Allowed types: table, line, bar, column, pie. "
    "Entity lists / detail dumps → type table with columns only. "
    "Trends over time → line with axis.x (time) and axis.y (measure array). "
    "Category comparison → bar/column with axis.x and axis.y. "
    "Share of total → pie with axis.series (category) and axis.y (measure object). "
    "Every axis value must be an exact field name from the provided fields list."
)


def _table_chart(presentation: ResultPresentation) -> dict[str, Any]:
    return {
        "type": "table",
        "title": presentation["title"],
        "columns": chart_columns(presentation),
    }


def normalize_chart_type(raw: str | None) -> str:
    text = str(raw or "").strip().lower()
    return text if text in LEGAL_CHART_TYPES else ""


def _is_numeric(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int | float):
        return True
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if not text:
            return False
        try:
            float(text)
            return True
        except ValueError:
            return False
    return False


def _is_temporal(value: Any) -> bool:
    if isinstance(value, datetime | date):
        return True
    if not isinstance(value, str) or len(value) < 8:
        return False
    text = value.strip().replace("Z", "+00:00")
    try:
        datetime.fromisoformat(text[:32])
        return True
    except ValueError:
        return False


def _numeric_samples(values: Sequence[Any]) -> list[float]:
    out: list[float] = []
    for item in values:
        if isinstance(item, bool):
            continue
        if isinstance(item, int | float):
            out.append(float(item))
            continue
        if isinstance(item, str):
            text = item.strip().replace(",", "")
            if not text:
                continue
            try:
                out.append(float(text))
            except ValueError:
                continue
    return out


def looks_like_identifier(values: Sequence[Any]) -> bool:
    """True for PK/snowflake/credit-code style numbers — not chart measures."""
    nums = _numeric_samples(values)
    if len(nums) < 2:
        return False
    unique_ratio = len({round(item, 12) for item in nums}) / len(nums)
    if unique_ratio < 0.9:
        return False
    all_integral = all(abs(item - round(item)) < 1e-9 for item in nums)
    if not all_integral:
        return False
    if any(abs(item) >= 1e12 for item in nums):
        return True
    return len(nums) >= 3


def column_kinds(
    fields: Sequence[str], rows: Sequence[Mapping[str, Any]]
) -> tuple[list[str], list[str], list[str]]:
    """Classify columns into temporal / measure / categorical."""
    temporal: list[str] = []
    measures: list[str] = []
    categorical: list[str] = []
    sample = list(rows)[:40]
    for field in fields:
        values = [
            row.get(field)
            for row in sample
            if isinstance(row, Mapping) and row.get(field) is not None
        ]
        if not values:
            categorical.append(field)
            continue
        temporal_hits = sum(1 for item in values if _is_temporal(item))
        numeric_hits = sum(1 for item in values if _is_numeric(item))
        n = len(values)
        if temporal_hits >= max(1, n * 0.6):
            temporal.append(field)
        elif numeric_hits >= max(1, n * 0.6):
            if looks_like_identifier(values):
                categorical.append(field)
            else:
                measures.append(field)
        else:
            categorical.append(field)
    return temporal, measures, categorical


def _chart_axis(x_col: Mapping[str, Any], y_col: Mapping[str, Any]) -> dict[str, Any]:
    """Line/bar axis; y is a single binding (FE normalizes object|list)."""
    return {
        "x": {"name": x_col["name"], "value": x_col["value"]},
        "y": {"name": y_col["name"], "value": y_col["value"]},
    }


def validate_chart_type(
    chart_type: str,
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
) -> tuple[bool, str]:
    """Heuristic gates for a suggested chart type (no LLM)."""
    ct = normalize_chart_type(chart_type)
    if not ct:
        return False, "unknown_type"
    if ct == "table":
        return True, ""
    if not rows or len(fields) < 2:
        return False, "insufficient_shape"
    temporal, measures, categorical = column_kinds(fields, rows)
    if not measures:
        return False, "no_measure"
    if len(rows) < 2:
        return False, "too_few_rows"
    if ct == "line":
        if not temporal:
            return False, "line_needs_temporal"
        return True, ""
    if ct in {"bar", "column"}:
        if not (categorical or temporal):
            return False, "bar_needs_category"
        return True, ""
    if ct == "pie":
        if not categorical:
            return False, "pie_needs_category"
        if len(rows) > 30:
            return False, "pie_too_many_rows"
        return True, ""
    return False, "unsupported"


def _axis_field_values(chart: Mapping[str, Any]) -> list[str]:
    axis = chart.get("axis")
    if not isinstance(axis, Mapping):
        return []
    out: list[str] = []
    for key in ("x", "series"):
        item = axis.get(key)
        if isinstance(item, Mapping) and item.get("value") is not None:
            out.append(str(item["value"]))
    y_axis = axis.get("y")
    if isinstance(y_axis, list):
        for item in y_axis:
            if isinstance(item, Mapping) and item.get("value") is not None:
                out.append(str(item["value"]))
    elif isinstance(y_axis, Mapping) and y_axis.get("value") is not None:
        out.append(str(y_axis["value"]))
    multi = axis.get("multi-quota")
    if isinstance(multi, Mapping):
        raw = multi.get("value")
        if isinstance(raw, list):
            out.extend(str(v) for v in raw if v is not None)
        elif raw is not None:
            out.append(str(raw))
    return out


def validate_chart_bindings(
    chart: Mapping[str, Any],
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
) -> tuple[bool, str]:
    """Ensure chart type + axis bindings fit the result shape."""
    ct = normalize_chart_type(str(chart.get("type") or ""))
    if not ct:
        return False, "unknown_type"
    ok, reason = validate_chart_type(ct, fields, rows)
    if not ok:
        return False, reason
    if ct == "table":
        return True, ""
    field_set = {str(f) for f in fields}
    bound = _axis_field_values(chart)
    if not bound:
        return False, "missing_axis"
    missing = [name for name in bound if name not in field_set]
    if missing:
        return False, f"unknown_fields:{','.join(missing)}"
    return True, ""


def build_chart_for_type(
    chart_type: str,
    presentation: ResultPresentation,
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
    *,
    instance_id: int = 0,
) -> dict[str, Any]:
    """Deterministically build a chart for a validated type."""
    ct = normalize_chart_type(chart_type) or "table"
    if ct == "table":
        tbl = _table_chart(presentation)
        tbl["instance_id"] = instance_id
        return tbl

    cols = chart_columns(presentation)
    col_by_field = {str(col.get("value") or col.get("name")): col for col in cols}
    temporal, measures, categorical = column_kinds(fields, rows)
    y_field = measures[0]
    y_col = col_by_field.get(y_field) or cols[-1]

    if ct == "line":
        x_field = temporal[0]
        x_col = col_by_field.get(x_field) or cols[0]
        return {
            "type": "line",
            "title": presentation["title"],
            "columns": cols,
            "xAxis": x_col["value"],
            "yAxis": y_col["value"],
            "axis": _chart_axis(x_col, y_col),
            "config": {
                "xField": x_col["value"],
                "yField": y_col["value"],
                "smooth": True,
            },
            "instance_id": instance_id,
        }

    if ct == "pie":
        series_field = categorical[0]
        series_col = col_by_field.get(series_field) or cols[0]
        return {
            "type": "pie",
            "title": presentation["title"],
            "columns": cols,
            "axis": {
                "y": {"name": y_col["name"], "value": y_col["value"]},
                "series": {"name": series_col["name"], "value": series_col["value"]},
            },
            "instance_id": instance_id,
        }

    # bar / column
    x_field = (categorical or temporal)[0]
    x_col = col_by_field.get(x_field) or cols[0]
    return {
        "type": ct,
        "title": presentation["title"],
        "columns": cols,
        "xAxis": x_col["value"],
        "yAxis": y_col["value"],
        "axis": _chart_axis(x_col, y_col),
        "config": {
            "xField": x_col["value"],
            "yField": y_col["value"],
        },
        "instance_id": instance_id,
    }


def infer_chart_for_presentation(
    presentation: ResultPresentation,
    fields: list[str],
    rows: list[dict[str, Any]],
    *,
    instance_id: int = 0,
) -> dict[str, Any]:
    """Heuristic-only inference when the agent left no usable chart_type."""
    if not rows or len(fields) < 2:
        return build_chart_for_type(
            "table", presentation, fields, rows, instance_id=instance_id
        )
    temporal, measures, categorical = column_kinds(fields, rows)
    if temporal and measures and len(rows) > 1:
        return build_chart_for_type(
            "line", presentation, fields, rows, instance_id=instance_id
        )
    if measures and categorical and 1 < len(rows) <= 30:
        return build_chart_for_type(
            "bar", presentation, fields, rows, instance_id=instance_id
        )
    return build_chart_for_type(
        "table", presentation, fields, rows, instance_id=instance_id
    )


def _narrow_llm_chart(
    *,
    llm_service: Any,
    sql: str,
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
    suggested: str,
    presentation: ResultPresentation,
) -> dict[str, Any] | None:
    llm = getattr(llm_service, "llm", None)
    if llm is None or not hasattr(llm, "invoke"):
        return None
    from common.utils.json_utils import extract_nested_json

    sample = [
        {str(k): row.get(k) for k in fields}
        for row in list(rows)[:5]
        if isinstance(row, Mapping)
    ]
    user = (
        f"SQL:\n{sql or '(none)'}\n\n"
        f"Fields: {list(fields)}\n\n"
        f"Sample rows:\n{orjson.dumps(sample, option=orjson.OPT_INDENT_2).decode()}\n\n"
        f"Suggested type that failed gates: {suggested or '(none)'}\n"
        f"Title: {presentation.get('title') or ''}\n"
        "Return JSON chart config only."
    )
    try:
        response = llm.invoke(
            [SystemMessage(content=_NARROW_SYSTEM), HumanMessage(content=user)]
        )
        text = getattr(response, "content", None)
        if isinstance(text, list):
            text = "".join(
                str(part.get("text") if isinstance(part, Mapping) else part)
                for part in text
            )
        json_str = extract_nested_json(str(text or ""))
        if not json_str:
            return None
        data = orjson.loads(json_str)
        if not isinstance(data, dict):
            return None
        if str(data.get("type") or "") in {"", "error"}:
            return None
        chart = dict(data)
        chart["title"] = presentation["title"]
        chart["columns"] = chart_columns(presentation)
        return chart
    except Exception as exc:
        SQLBotLogUtil.warning("narrow chart LLM failed: %s", exc)
        return None


def resolve_delivery_chart(
    *,
    presentation: ResultPresentation,
    fields: list[str],
    rows: list[dict[str, Any]],
    suggested_type: str = "",
    sql: str = "",
    llm_service: Any = None,
    instance_id: int = 0,
) -> dict[str, Any]:
    """Agent hint → gates → narrow LLM → table."""
    suggested = normalize_chart_type(suggested_type)
    if suggested:
        ok, _reason = validate_chart_type(suggested, fields, rows)
        if ok:
            chart = build_chart_for_type(
                suggested, presentation, fields, rows, instance_id=instance_id
            )
            return chart

    if llm_service is not None and suggested and suggested != "table":
        llm_chart = _narrow_llm_chart(
            llm_service=llm_service,
            sql=sql,
            fields=fields,
            rows=rows,
            suggested=suggested,
            presentation=presentation,
        )
        if llm_chart is not None:
            ok, _reason = validate_chart_bindings(llm_chart, fields, rows)
            if ok:
                llm_chart["instance_id"] = instance_id
                return cast(dict[str, Any], llm_chart)

    if not suggested:
        # Legacy / missing hint: keep prior heuristic behavior.
        return infer_chart_for_presentation(
            presentation, fields, rows, instance_id=instance_id
        )

    return build_chart_for_type(
        "table", presentation, fields, rows, instance_id=instance_id
    )
