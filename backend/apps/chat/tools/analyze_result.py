"""Analyze-mode tools: compact stats from a workspace SQL without loading rows.

Preview rows in the model context are not the result set. These tools wrap an
already-executed revision and re-aggregate in the database.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.tools.contract import failure_outcome, signals_for_tool, success_outcome
from apps.chat.tools.execute_sql import execute_sql_sandbox
from apps.db.constant import DB

PROFILE_TOOL = "profile_sql_result"
AGGREGATE_TOOL = "aggregate_sql_result"
ANALYZE_SQL_TOOLS: frozenset[str] = frozenset({PROFILE_TOOL, AGGREGATE_TOOL})

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SOURCE_ALIAS = "_sqlbot_src"
_MAX_PROFILE_COLUMNS = 6
_MAX_DIMENSIONS = 3
_MAX_METRICS = 4
_BREAKDOWN_TOPK = 8
_AGGREGATE_LIMIT = 20

MetricFn = Literal["count", "sum", "avg", "min", "max"]


def quote_ident(name: str, dialect: str | None) -> str:
    db = DB.get_db(dialect, default_if_none=True)
    return f"{db.prefix}{name}{db.suffix}"


def wrap_source_sql(sql: str, alias: str = _SOURCE_ALIAS) -> str:
    body = str(sql or "").strip().rstrip(";").strip()
    return f"({body}) {alias}"


def resolve_field(name: str, fields: Sequence[str]) -> str | None:
    raw = str(name or "").strip()
    if not raw or not _IDENT_RE.match(raw):
        return None
    for field in fields:
        if str(field).strip() == raw:
            return str(field).strip()
    lowered = raw.lower()
    for field in fields:
        if str(field).strip().lower() == lowered:
            return str(field).strip()
    if fields:
        return None
    return raw


def pick_profile_columns(
    requested: Sequence[str] | None, fields: Sequence[str]
) -> list[str]:
    if requested:
        picked: list[str] = []
        for item in requested:
            resolved = resolve_field(str(item), fields)
            if resolved and resolved not in picked:
                picked.append(resolved)
            if len(picked) >= _MAX_PROFILE_COLUMNS:
                break
        return picked
    return [str(item).strip() for item in fields[:_MAX_PROFILE_COLUMNS] if str(item).strip()]


def build_profile_sql(
    source_sql: str, columns: Sequence[str], *, dialect: str | None
) -> str:
    src = wrap_source_sql(source_sql)
    parts = [f"COUNT(*) AS {quote_ident('row_count', dialect)}"]
    for index, column in enumerate(columns):
        qualified = f"{_SOURCE_ALIAS}.{quote_ident(column, dialect)}"
        parts.append(f"COUNT({qualified}) AS {quote_ident(f'nn_{index}', dialect)}")
        parts.append(f"MIN({qualified}) AS {quote_ident(f'min_{index}', dialect)}")
        parts.append(f"MAX({qualified}) AS {quote_ident(f'max_{index}', dialect)}")
    return f"SELECT {', '.join(parts)} FROM {src}"


def build_breakdown_sql(
    source_sql: str, column: str, *, dialect: str | None, topk: int = _BREAKDOWN_TOPK
) -> str:
    src = wrap_source_sql(source_sql)
    ident = quote_ident(column, dialect)
    n = max(1, min(int(topk), 20))
    return (
        f"SELECT {_SOURCE_ALIAS}.{ident} AS {quote_ident('value', dialect)}, "
        f"COUNT(*) AS {quote_ident('n', dialect)} "
        f"FROM {src} "
        f"GROUP BY {_SOURCE_ALIAS}.{ident} "
        f"ORDER BY {quote_ident('n', dialect)} DESC "
        f"LIMIT {n}"
    )


def build_aggregate_sql(
    source_sql: str,
    dimensions: Sequence[str],
    metrics: Sequence[Mapping[str, Any]],
    *,
    dialect: str | None,
    limit: int = _AGGREGATE_LIMIT,
) -> str:
    src = wrap_source_sql(source_sql)
    select_parts: list[str] = []
    group_parts: list[str] = []
    for column in dimensions:
        ident = quote_ident(column, dialect)
        select_parts.append(f"{_SOURCE_ALIAS}.{ident} AS {ident}")
        group_parts.append(f"{_SOURCE_ALIAS}.{ident}")
    for index, metric in enumerate(metrics):
        fn = str(metric.get("fn") or "count").strip().lower()
        alias = str(metric.get("alias") or f"m_{index}").strip() or f"m_{index}"
        if not _IDENT_RE.match(alias):
            alias = f"m_{index}"
        quoted_alias = quote_ident(alias, dialect)
        if fn == "count" and not str(metric.get("column") or "").strip():
            select_parts.append(f"COUNT(*) AS {quoted_alias}")
            continue
        column = str(metric.get("column") or "").strip()
        qualified = f"{_SOURCE_ALIAS}.{quote_ident(column, dialect)}"
        if fn == "sum":
            expr = f"SUM({qualified})"
        elif fn == "avg":
            expr = f"AVG({qualified})"
        elif fn == "min":
            expr = f"MIN({qualified})"
        elif fn == "max":
            expr = f"MAX({qualified})"
        else:
            expr = f"COUNT({qualified})"
        select_parts.append(f"{expr} AS {quoted_alias}")
    n = max(1, min(int(limit), 50))
    sql = f"SELECT {', '.join(select_parts)} FROM {src}"
    if group_parts:
        sql += f" GROUP BY {', '.join(group_parts)}"
    return f"{sql} LIMIT {n}"


def _dialect(llm_service: Any) -> str | None:
    ds = getattr(llm_service, "ds", None) or getattr(llm_service, "datasource", None)
    return str(getattr(ds, "type", None) or "") or None


def _run_probe(
    llm_service: Any,
    sql: str,
    *,
    access_scope: Any,
    limit: int,
    name: str,
) -> dict[str, Any]:
    result = execute_sql_sandbox(
        llm_service,
        sql,
        access_scope=access_scope,
        limit=limit,
        purpose="probe",
    )
    if not result.get("ok"):
        return failure_outcome(
            str(result.get("error") or result.get("summary") or "probe failed"),
            retryable=True,
            name=name,
            signals=signals_for_tool(name, purpose="probe"),
        )
    return result


def _payload(result: Mapping[str, Any]) -> Mapping[str, Any]:
    data = result.get("payload")
    return data if isinstance(data, Mapping) else {}


def _row_get(row: Mapping[str, Any], key: str) -> Any:
    if key in row:
        return row[key]
    lowered = key.lower()
    for name, value in row.items():
        if str(name).lower() == lowered:
            return value
    return None


def profile_sql_result(
    llm_service: Any,
    workspace: SqlWorkspace,
    *,
    access_scope: Any = None,
    sql_ref: str = "active",
    columns: Sequence[str] | None = None,
    breakdown: str = "",
    topk: int = _BREAKDOWN_TOPK,
) -> dict[str, Any]:
    """Profile an executed revision in the warehouse; return compact stats."""
    item = workspace.resolve(sql_ref)
    if item is None or not str(item.sql or "").strip():
        return failure_outcome(
            "sql_ref must resolve to an executed workspace revision",
            retryable=True,
            name=PROFILE_TOOL,
            signals=signals_for_tool(PROFILE_TOOL, purpose="probe"),
        )
    dialect = _dialect(llm_service)
    fields = [str(field).strip() for field in (item.fields or []) if str(field).strip()]
    picked = pick_profile_columns(columns, fields)
    sql = build_profile_sql(item.sql, picked, dialect=dialect)
    raw = _run_probe(
        llm_service, sql, access_scope=access_scope, limit=1, name=PROFILE_TOOL
    )
    if not raw.get("ok"):
        return raw
    row = (_payload(raw).get("preview_rows") or _payload(raw).get("sample_rows") or [{}])
    first = row[0] if row and isinstance(row[0], Mapping) else {}
    stats: list[dict[str, Any]] = []
    for index, column in enumerate(picked):
        stats.append(
            {
                "name": column,
                "non_null": _row_get(first, f"nn_{index}"),
                "min": _row_get(first, f"min_{index}"),
                "max": _row_get(first, f"max_{index}"),
            }
        )
    payload: dict[str, Any] = {
        "sql_ref": item.rev,
        "row_count": _row_get(first, "row_count") or item.row_count,
        "columns": stats,
    }
    focus = resolve_field(breakdown, fields) if str(breakdown or "").strip() else None
    if focus:
        br_sql = build_breakdown_sql(item.sql, focus, dialect=dialect, topk=topk)
        br_raw = _run_probe(
            llm_service,
            br_sql,
            access_scope=access_scope,
            limit=max(1, min(int(topk), 20)),
            name=PROFILE_TOOL,
        )
        if br_raw.get("ok"):
            br_rows = list(
                _payload(br_raw).get("preview_rows")
                or _payload(br_raw).get("sample_rows")
                or []
            )
            payload["breakdown"] = {
                "column": focus,
                "top": [
                    {
                        "value": _row_get(entry, "value"),
                        "n": _row_get(entry, "n"),
                    }
                    for entry in br_rows
                    if isinstance(entry, Mapping)
                ],
            }
        else:
            payload["breakdown_error"] = str(
                br_raw.get("error") or br_raw.get("summary") or "breakdown failed"
            )
    summary = f"Profiled {item.rev}: {payload.get('row_count')} rows"
    if focus and isinstance(payload.get("breakdown"), Mapping):
        summary += f"; breakdown on {focus}"
    return success_outcome(
        summary,
        payload=payload,
        signals=signals_for_tool(PROFILE_TOOL, purpose="probe"),
        name=PROFILE_TOOL,
    )


def aggregate_sql_result(
    llm_service: Any,
    workspace: SqlWorkspace,
    *,
    access_scope: Any = None,
    sql_ref: str = "active",
    dimensions: Sequence[str] | None = None,
    metrics: Sequence[Mapping[str, Any]] | None = None,
    limit: int = _AGGREGATE_LIMIT,
) -> dict[str, Any]:
    """GROUP BY an executed revision in the warehouse; return ≤20 compact rows."""
    item = workspace.resolve(sql_ref)
    if item is None or not str(item.sql or "").strip():
        return failure_outcome(
            "sql_ref must resolve to an executed workspace revision",
            retryable=True,
            name=AGGREGATE_TOOL,
            signals=signals_for_tool(AGGREGATE_TOOL, purpose="probe"),
        )
    fields = [str(field).strip() for field in (item.fields or []) if str(field).strip()]
    dims: list[str] = []
    for name in list(dimensions or [])[:_MAX_DIMENSIONS]:
        resolved = resolve_field(str(name), fields)
        if resolved is None:
            return failure_outcome(
                f"dimension {name!r} is not a column on {item.rev}",
                retryable=True,
                name=AGGREGATE_TOOL,
                signals=signals_for_tool(AGGREGATE_TOOL, purpose="probe"),
            )
        if resolved not in dims:
            dims.append(resolved)
    raw_metrics = list(metrics or [{"fn": "count"}])[:_MAX_METRICS]
    if not raw_metrics:
        raw_metrics = [{"fn": "count"}]
    compiled: list[dict[str, Any]] = []
    for index, metric in enumerate(raw_metrics):
        if not isinstance(metric, Mapping):
            continue
        fn = str(metric.get("fn") or "count").strip().lower()
        if fn not in {"count", "sum", "avg", "min", "max"}:
            return failure_outcome(
                f"unsupported metric fn {fn!r}",
                retryable=True,
                name=AGGREGATE_TOOL,
                signals=signals_for_tool(AGGREGATE_TOOL, purpose="probe"),
            )
        column = str(metric.get("column") or "").strip()
        if fn != "count" or column:
            resolved = resolve_field(column, fields)
            if resolved is None:
                return failure_outcome(
                    f"metric column {column!r} is not a column on {item.rev}",
                    retryable=True,
                    name=AGGREGATE_TOOL,
                    signals=signals_for_tool(AGGREGATE_TOOL, purpose="probe"),
                )
            column = resolved
        alias = str(metric.get("alias") or "").strip()
        if not alias:
            alias = "n" if fn == "count" and not column else f"{fn}_{column or index}"
        if not _IDENT_RE.match(alias):
            alias = f"m_{index}"
        compiled.append({"fn": fn, "column": column, "alias": alias})
    if not dims and not compiled:
        return failure_outcome(
            "aggregate_sql_result needs dimensions or metrics",
            retryable=True,
            name=AGGREGATE_TOOL,
            signals=signals_for_tool(AGGREGATE_TOOL, purpose="probe"),
        )
    dialect = _dialect(llm_service)
    sql = build_aggregate_sql(
        item.sql, dims, compiled, dialect=dialect, limit=limit
    )
    raw = _run_probe(
        llm_service,
        sql,
        access_scope=access_scope,
        limit=max(1, min(int(limit), 50)),
        name=AGGREGATE_TOOL,
    )
    if not raw.get("ok"):
        return raw
    data = _payload(raw)
    rows = list(data.get("preview_rows") or data.get("sample_rows") or [])
    return success_outcome(
        f"Aggregated {item.rev}: {len(rows)} groups",
        payload={
            "sql_ref": item.rev,
            "dimensions": dims,
            "metrics": compiled,
            "rows": rows,
            "row_count": data.get("row_count") or len(rows),
        },
        signals=signals_for_tool(AGGREGATE_TOOL, purpose="probe"),
        name=AGGREGATE_TOOL,
    )
