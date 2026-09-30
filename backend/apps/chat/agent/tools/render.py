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
    rows = data.get("preview_rows") or data.get("sample_rows") or []
    preview = _format_preview_rows(rows) if isinstance(rows, Sequence) else ""
    if preview:
        lines.append("preview:")
        lines.append(preview)
    return "\n".join(lines).strip()


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


def _format_preview_rows(rows: Sequence[Any], *, limit: int = _SQL_PREVIEW_ROWS) -> str:
    lines: list[str] = []
    for row in list(rows)[:limit]:
        if isinstance(row, Mapping):
            parts = [f"{key}={value}" for key, value in row.items()]
            lines.append(" | ".join(parts))
        else:
            lines.append(str(row))
    return "\n".join(lines)
