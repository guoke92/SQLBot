"""Chat-tool plaintext for the model. Host render stays generic."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.agent_knowledge import KNOWLEDGE_TOOLS
from apps.chat.tools.contract import outcome_payload

_SQL_PREVIEW_ROWS = 5


def render_tool_message(name: str, result: Mapping[str, Any]) -> str:
    """Compact observation for one chat tool. Control flags stay off this text."""
    if not result.get("ok"):
        err = str(result.get("error") or result.get("summary") or "failed").strip()
        return f"Failed: {err}"
    data = outcome_payload(result)
    summary = str(result.get("summary") or "").strip()
    if name == "get_table_schema":
        body = str(data.get("schema_text") or "").strip()
        if body and body not in summary:
            return f"{summary}\n\n{body}".strip() if summary else body
        return summary
    if name == "execute_sql_sandbox":
        return _render_sql_sandbox(summary, data)
    if name == "compare_results":
        return _render_compare_results(summary, data)
    if name in {"profile_sql_result", "aggregate_sql_result"}:
        return _render_analyze_result(name, summary, data)
    if name == "patch_and_compile_sql":
        sql = str(data.get("sql") or "").strip()
        rev = str(
            data.get("sql_rev") or (result.get("signals") or {}).get("sql_rev") or ""
        )
        bits = [summary] if summary else []
        if rev:
            bits.append(f"rev: {rev}")
        if sql:
            bits.append(sql)
        return "\n".join(bits).strip()
    if name in KNOWLEDGE_TOOLS:
        return summary
    return summary


def _render_sql_sandbox(summary: str, data: Mapping[str, Any]) -> str:
    lines = [summary] if summary else []
    sql = str(data.get("sql") or "").strip()
    if sql:
        lines.append("sql:")
        lines.append(sql)
    fields = data.get("fields") or []
    if isinstance(fields, Sequence) and not isinstance(fields, str | bytes):
        names = [str(item).strip() for item in fields if str(item).strip()]
        if names:
            lines.append("fields: " + ", ".join(names))
    if data.get("truncated"):
        lines.append("truncated: true")
    lines.extend(_render_page_stats(data.get("column_stats")))
    context = data.get("context_preview")
    if (
        isinstance(context, Sequence)
        and not isinstance(context, str | bytes)
        and context
    ):
        page = list(context)
        complete = _is_complete_page(page)
        if complete:
            noun = "row" if len(page) == 1 else "rows"
            lines.append(f"complete page ({len(page)} {noun}):")
        else:
            lines.append("preview (first / middle / last of this page):")
        rendered = _render_context_preview(page, limit=20 if complete else 5)
        if rendered:
            lines.append(rendered)
    else:
        rows = data.get("preview_rows") or data.get("sample_rows") or []
        preview = _format_preview_rows(rows) if isinstance(rows, Sequence) else ""
        if preview:
            lines.append("preview:")
            lines.append(preview)
    return "\n".join(lines).strip()


def _render_page_stats(stats: Any) -> list[str]:
    """Null and range counts for the returned page. Sums stay off this text."""
    if not isinstance(stats, Mapping) or not stats:
        return []
    lines = ["page_stats (returned page only):"]
    for name, raw in list(stats.items())[:16]:
        if not isinstance(raw, Mapping):
            continue
        bits = [str(name)]
        for key, label in (
            ("null_count", "null"),
            ("blank_count", "blank"),
            ("non_null_count", "non_null"),
            ("min", "min"),
            ("max", "max"),
        ):
            if key not in raw or raw[key] is None:
                continue
            if key == "blank_count" and not raw[key]:
                continue
            bits.append(f"{label}={raw[key]}")
        if len(bits) > 1:
            lines.append("  " + " ".join(bits))
    return lines if len(lines) > 1 else []


def _is_complete_page(rows: Sequence[Any]) -> bool:
    positions: list[int] = []
    for item in rows:
        if not isinstance(item, Mapping) or not isinstance(item.get("position"), int):
            return False
        positions.append(int(item["position"]))
    return bool(positions) and positions == list(range(1, len(positions) + 1))


def _render_context_preview(rows: Sequence[Any], *, limit: int = 5) -> str:
    lines: list[str] = []
    for item in list(rows)[:limit]:
        if not isinstance(item, Mapping):
            continue
        position = item.get("position")
        row = item.get("row")
        if position is None or not isinstance(row, Mapping):
            continue
        body = _format_preview_rows([row], limit=1)
        lines.append(f"  #{position} {body}")
    return "\n".join(lines)


def _render_compare_results(summary: str, data: Mapping[str, Any]) -> str:
    lines = [summary] if summary else []
    for side in ("base", "new"):
        side_data = data.get(side)
        if not isinstance(side_data, Mapping):
            continue
        rev = str(side_data.get("rev") or side).strip()
        count = side_data.get("row_count")
        bits = [f"{rev}: {count} rows" if count is not None else f"{rev}:"]
        if side_data.get("truncated"):
            limit = side_data.get("display_limit")
            bits.append(f"truncated at {limit}" if limit is not None else "truncated")
        fields = side_data.get("fields") or []
        if isinstance(fields, Sequence) and not isinstance(fields, str | bytes):
            names = [str(item).strip() for item in fields if str(item).strip()]
            if names:
                bits.append("fields=" + ",".join(names[:8]))
        lines.append(" · ".join(bits))
    return "\n".join(lines).strip()


def _render_analyze_result(name: str, summary: str, data: Mapping[str, Any]) -> str:
    lines = [summary] if summary else [name]
    ref = str(data.get("sql_ref") or "").strip()
    if ref:
        lines.append(f"sql_ref: {ref}")
    columns = data.get("columns")
    if isinstance(columns, Sequence) and not isinstance(columns, str | bytes):
        for column in columns[:8]:
            if not isinstance(column, Mapping):
                continue
            bits = [str(column.get("name") or "")]
            if column.get("non_null") is not None:
                bits.append(f"non_null={column.get('non_null')}")
            if column.get("min") is not None:
                bits.append(f"min={column.get('min')}")
            if column.get("max") is not None:
                bits.append(f"max={column.get('max')}")
            lines.append(" ".join(str(item) for item in bits if item))
    breakdown = data.get("breakdown")
    if isinstance(breakdown, Mapping):
        lines.append(f"breakdown {breakdown.get('column')}:")
        for entry in list(breakdown.get("top") or [])[:8]:
            if isinstance(entry, Mapping):
                lines.append(f"  {entry.get('value')}: {entry.get('n')}")
    rows = data.get("rows")
    if isinstance(rows, Sequence) and not isinstance(rows, str | bytes) and rows:
        preview = _format_preview_rows(rows, limit=12)
        if preview:
            lines.append("groups:")
            lines.append(preview)
    return "\n".join(lines).strip()


def _format_preview_rows(rows: Sequence[Any], *, limit: int = _SQL_PREVIEW_ROWS) -> str:
    lines: list[str] = []
    for row in list(rows)[:limit]:
        if isinstance(row, Mapping):
            parts = [f"{key}={value}" for key, value in row.items()]
            lines.append(" | ".join(parts))
        else:
            lines.append(str(row))
    return "\n".join(lines)
