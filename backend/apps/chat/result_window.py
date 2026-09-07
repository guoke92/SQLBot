"""Result display-window helpers: SQL LIMIT, default ROW_LIMIT, soft truncation."""

from __future__ import annotations

from typing import Any

from apps.chat.plan_policy import ROW_LIMIT, ROW_LIMIT_MAX

try:
    from sqlglot import exp, parse_one
except Exception:  # pragma: no cover - sqlglot is a hard dependency in practice
    exp = None  # type: ignore[assignment]
    parse_one = None  # type: ignore[assignment]


def extract_sql_limit(sql: str, *, dialect: str | None = None) -> int | None:
    """Best-effort outer SELECT LIMIT extraction. Returns None when absent/unparseable."""
    text = (sql or "").strip().rstrip(";")
    if not text or parse_one is None:
        return None
    try:
        tree = parse_one(text, read=dialect or "mysql")
    except Exception:
        return None
    limit_node = tree.args.get("limit") if hasattr(tree, "args") else None
    if limit_node is None:
        return None
    try:
        if isinstance(limit_node, exp.Limit):
            expression = limit_node.expression
            if expression is None:
                return None
            value = expression.this if hasattr(expression, "this") else expression
            return int(str(value))
        return int(str(limit_node))
    except Exception:
        return None


def resolve_exec_row_limit(
    sql: str,
    *,
    tool_limit: int | None = None,
    default_limit: int = ROW_LIMIT,
    absolute_max: int = ROW_LIMIT_MAX,
    dialect: str | None = None,
) -> int:
    """Resolve the fetch/display window for one query.

    Prefer an explicit SQL ``LIMIT`` (user asked for N rows) over the tool/default
    window. Always clamp to ``[1, absolute_max]``.
    """
    sql_limit = extract_sql_limit(sql, dialect=dialect)
    if sql_limit is not None and sql_limit > 0:
        requested = sql_limit
    elif tool_limit is not None and int(tool_limit) > 0:
        requested = int(tool_limit)
    else:
        requested = int(default_limit)
    return max(1, min(int(requested), int(absolute_max)))


def apply_result_window(
    *,
    row_count: int,
    window_limit: int | None,
    truncated: bool = False,
) -> tuple[bool, int | None]:
    """Mark a result as a display window when it hits the applied limit.

    Fetching ``limit + 1`` cannot detect overflow when the SQL itself already
    contains ``LIMIT N``. Hitting exactly ``window_limit`` rows is treated as
    truncated for the UI tip 「仅展示前 N 条」.
    """
    if window_limit is None or int(window_limit) <= 0:
        return bool(truncated), None
    limit = int(window_limit)
    if truncated or int(row_count) >= limit:
        return True, limit
    return False, limit


def annotate_result_window(
    result: dict[str, Any],
    *,
    sql: str,
    tool_limit: int | None = None,
    default_limit: int = ROW_LIMIT,
    dialect: str | None = None,
) -> dict[str, Any]:
    """Mutate a protocol result dict with consistent truncated/limit metadata."""
    rows = result.get("data") if isinstance(result.get("data"), list) else []
    window = resolve_exec_row_limit(
        sql,
        tool_limit=tool_limit,
        default_limit=default_limit,
        dialect=dialect,
    )
    truncated, limit = apply_result_window(
        row_count=len(rows),
        window_limit=window,
        truncated=bool(result.get("truncated")),
    )
    if truncated and isinstance(rows, list) and len(rows) > window:
        result["data"] = rows[:window]
        rows = result["data"]
    result["truncated"] = truncated
    if truncated:
        result["limit"] = limit
        result["truncation_reason"] = result.get("truncation_reason") or "query_limit"
    else:
        result.pop("limit", None)
        result.pop("truncation_reason", None)
    result["row_count"] = (
        result.get("row_count")
        if result.get("row_count") is not None
        else len(rows)
    )
    return result
