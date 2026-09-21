"""Sandboxed SQL execution tool with permission rewrites and compact summaries."""

from __future__ import annotations

import re
from typing import Any

from apps.chat.agent_knowledge import PROBE_SQL_LIMIT, AgentKnowledgePlane
from apps.chat.chart_presentation import LEGAL_CHART_TYPES, normalize_chart_type
from apps.chat.plan_policy import ROW_LIMIT
from apps.chat.result_window import apply_result_window, resolve_exec_row_limit
from apps.chat.steps.enum_display import (
    apply_wiki_enum_labels,
    is_wiki_enum_discovery_sql,
)
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.process_timeline import (
    PREVIEW_ROW_LIMIT,
    new_dataset_id,
    preview_rows,
    upsert_result_dataset,
)
from apps.conversation.runtime_context import (
    attach_runtime,
    current_tool_call_id,
    current_worker_identity,
    peek_runtime,
)
from apps.conversation.tooling import ToolResult
from apps.datasource.access import AccessScope
from common.utils.utils import SQLBotLogUtil

_CATALOG_NAME_RE = re.compile(
    r"\b(?:information_schema|pg_catalog)\b",
    re.IGNORECASE,
)
_CATALOG_COMMANDS = frozenset({"SHOW", "DESCRIBE", "DESC", "EXPLAIN"})


def is_catalog_probe_sql(sql: str) -> bool:
    """True for information_schema / pg_catalog / SHOW COLUMNS style probes."""
    text = (sql or "").strip()
    if not text:
        return False
    if _CATALOG_NAME_RE.search(text):
        return True
    first = text.split(None, 1)[0].upper() if text else ""
    return first in _CATALOG_COMMANDS


def _runtime_snapshot() -> dict[str, Any]:
    run_id, _token = current_worker_identity()
    if not run_id:
        return {}
    return peek_runtime(run_id) or {}


def _schema_ready() -> bool | None:
    """Session plane gate. None = no agent plane attached (standalone SQL tests)."""
    snap = _runtime_snapshot()
    if "knowledge_plane" not in snap:
        return None
    plane = AgentKnowledgePlane.from_dump(snap.get("knowledge_plane"))
    return bool(plane.schema_ready)


def _reject_enum_discovery(sql: str, llm_service: Any) -> ToolResult | None:
    ds = getattr(llm_service, "ds", None) or getattr(llm_service, "datasource", None)
    ds_id = getattr(ds, "id", None)
    if ds_id is None:
        return None
    try:
        from apps.chat.steps.wiki_recall import wiki_enum_carriers
        from apps.db.db import get_sqlglot_dialect

        carriers = wiki_enum_carriers(ds_id=int(ds_id))
        dialect = get_sqlglot_dialect(getattr(ds, "type", None) or "mysql")
    except Exception:
        return None
    if not is_wiki_enum_discovery_sql(sql, carriers, dialect=str(dialect or "mysql")):
        return None
    return failure_result(
        "Wiki enum pages already define these field values. Do not SELECT "
        "DISTINCT Wiki enum columns to discover codes. Use get_dict_values "
        "or labels= on the schema field.",
        retryable=False,
    )


def _with_probe_note(message: str, note: str | None) -> str:
    if not note:
        return message
    return f"{message} {note}"


def _consume_probe_budget(required: bool) -> str | None:
    """Soft probe budget: always allow execution; return advisory when exhausted.

    Hard-rejecting the N+1 probe wastes an already-written SQL and surfaces a
    fake "execution failed" in the timeline. The budget is an agent steering
    signal — keep counting, still run, and append guidance into the tool result.
    """
    if required is not False:
        return None
    used = int(_runtime_snapshot().get("probe_sql_calls") or 0)
    run_id, _token = current_worker_identity()
    if run_id:
        attach_runtime(run_id, probe_sql_calls=used + 1)
    # ``used`` is the count *before* this call; after attach it is used+1.
    after = used + 1
    if after < PROBE_SQL_LIMIT:
        return None
    return (
        "[probe_budget] 探查已执行。若数据形态已经够用，下一次 execute_sql_sandbox "
        "请用 required=true 交付；口径仍不清则 request_clarification。"
        "不要继续用探查摸字段/枚举。必要的形态验证仍可再探查。"
    )


def _display_sql(proto: Any, plan: Any, fallback: str) -> str:
    """User-facing SQL via the protocol display formatter (pretty / original).

    Execution may rewrite quotes via sqlglot into a single line; UI and
    result_dataset must not inherit that flattened form.
    """
    fmt = getattr(proto, "format_statement_for_display", None)
    if callable(fmt):
        try:
            text = str(fmt(plan) or "").strip()
            if text:
                return text
        except Exception as exc:
            SQLBotLogUtil.warning("format_statement_for_display failed: %s", exc)
    return fallback


def execute_sql_sandbox(
    llm_service: Any,
    sql: str,
    *,
    access_scope: AccessScope | None = None,
    limit: int = ROW_LIMIT,
    sample_limit: int = PREVIEW_ROW_LIMIT,
    plan_id: str | None = None,
    dataset_id: str | None = None,
    required: bool = True,
    result_title: str = "",
    chart_type: str = "",
) -> ToolResult:
    """Safely execute SQL with permission rewrites and token-safe output.

    JOIN edges from wiki relations are advisory; this sandbox does not reject
    queries whose tables are missing from the known relation graph.
    """
    clean_sql = (sql or "").strip().rstrip(";")
    if not clean_sql:
        return failure_result("SQL query cannot be empty")

    delivery = required is not False
    resolved_chart = ""
    if delivery:
        resolved_chart = normalize_chart_type(chart_type)
        if chart_type and not resolved_chart:
            return failure_result(
                "Invalid chart_type. Use one of: "
                + ", ".join(sorted(LEGAL_CHART_TYPES)),
                retryable=True,
            )
        if not resolved_chart:
            # Missing hint defaults to table so a silent omit still delivers.
            resolved_chart = "table"

    if is_catalog_probe_sql(clean_sql):
        return failure_result(
            "Catalog probes are not allowed (information_schema / pg_catalog / "
            "SHOW COLUMNS / DESCRIBE). Table structure must come from Wiki or "
            "the schema context already in the prompt.",
            retryable=False,
        )

    enum_block = _reject_enum_discovery(clean_sql, llm_service)
    if enum_block is not None:
        return enum_block

    probe_note = _consume_probe_budget(required)

    if _schema_ready() is False:
        return failure_result(
            _with_probe_note(
                "Wiki did not provide table/enum schema. Do not guess columns or "
                "query information_schema. Stop and tell the user the knowledge "
                "base cannot answer this yet.",
                probe_note,
            ),
            retryable=False,
        )

    try:
        proto = getattr(llm_service, "protocol", None)
        ds = getattr(llm_service, "ds", None) or getattr(
            llm_service, "datasource", None
        )
        if proto is None or ds is None:
            return failure_result(
                _with_probe_note(
                    "Datasource or protocol not configured on session",
                    probe_note,
                )
            )

        payload = {"sql": clean_sql}
        plan = proto.parse_candidate_payload(payload)
        if not plan.success:
            return failure_result(f"Invalid SQL payload: {plan.message}")

        allowed_resources = (
            getattr(access_scope, "resource_names", None)
            or getattr(llm_service, "table_name_list", None)
            or []
        )
        if allowed_resources:
            plan = proto.validate_plan(ds, plan, allowed_resources)
            if not plan.success:
                return failure_result(f"SQL validation error: {plan.message}")

        dialect_raw = getattr(ds, "type", None) or getattr(proto, "type_key", None)
        dialect = dialect_raw if isinstance(dialect_raw, str) else None
        statement = plan.statement or clean_sql
        display_sql = _display_sql(proto, plan, clean_sql or statement)
        exec_limit = resolve_exec_row_limit(
            statement,
            tool_limit=limit,
            dialect=dialect,
        )
        # Protocol/exec_sql already fetches limit+1 to detect hard overflow.
        qr = proto.execute(ds, plan, max_rows=exec_limit)
        fetched = [row for row in list(qr.data or []) if isinstance(row, dict)]
        truncated, display_limit = apply_result_window(
            row_count=len(fetched),
            window_limit=exec_limit,
            truncated=bool(getattr(qr, "truncated", False)),
        )
        rows = fetched[:exec_limit]
        fields = [str(item) for item in (qr.fields or [])]
        # Agent always sees raw codes. Enum labels are a delivery/UI projection
        # only — labeling probe samples (e.g. PAID→已缴费) made models write
        # Chinese literals into WHERE and return empty sets (chat 247).
        raw_rows = [dict(row) for row in rows if isinstance(row, dict)]
        value_labels: dict[str, dict[str, str]] = {}
        store_rows = raw_rows
        if delivery:
            try:
                store_rows, value_labels = apply_wiki_enum_labels(
                    sql=statement,
                    fields=fields,
                    rows=raw_rows,
                    llm_service=llm_service,
                )
            except Exception as exc:
                SQLBotLogUtil.warning("enum label projection degraded: %s", exc)
                store_rows = raw_rows
                value_labels = {}

        row_count = len(raw_rows)
        samples = preview_rows(raw_rows, limit=min(sample_limit, PREVIEW_ROW_LIMIT))

        col_stats: dict[str, Any] = {}
        for field_name in fields[:10]:
            vals = [
                row.get(field_name)
                for row in raw_rows
                if isinstance(row, dict) and row.get(field_name) is not None
            ]
            stats: dict[str, Any] = {
                "non_null_count": len(vals),
                "null_count": row_count - len(vals),
            }
            num_vals = [
                float(v)
                for v in vals
                if isinstance(v, int | float) and not isinstance(v, bool)
            ]
            if num_vals:
                stats["min"] = min(num_vals)
                stats["max"] = max(num_vals)
                stats["sum"] = round(sum(num_vals), 2)
            col_stats[field_name] = stats

        resolved_dataset_id = dataset_id or new_dataset_id()
        resolved_plan_id = plan_id or current_tool_call_id() or resolved_dataset_id
        run_id, _token = current_worker_identity()
        if run_id:
            upsert_result_dataset(
                run_id=run_id,
                dataset_id=resolved_dataset_id,
                plan_id=resolved_plan_id,
                fields=fields,
                rows=store_rows,
                row_count=row_count,
                truncated=truncated,
                sql=display_sql,
                value_labels=value_labels,
                limit=display_limit if truncated else exec_limit,
                required=required,
                result_title=result_title,
                chart_type=resolved_chart,
            )
            if delivery:
                attach_runtime(run_id, sql_delivered=True)

        title = str(result_title or "").strip()
        summary = _with_probe_note(
            f"Query executed successfully, returned {row_count} rows.",
            probe_note,
        )
        return success_result(
            summary,
            data={
                "sql": display_sql,
                "fields": fields,
                "total_rows": row_count,
                "row_count": row_count,
                "truncated": truncated,
                "sample_rows": samples,
                "preview_rows": samples,
                "column_stats": col_stats,
                "dataset_id": resolved_dataset_id,
                "plan_id": resolved_plan_id,
                "required": bool(required),
                **({"probe_note": probe_note} if probe_note else {}),
                **({"chart_type": resolved_chart} if resolved_chart else {}),
                **({"result_title": title} if title else {}),
                **(
                    {"limit": display_limit}
                    if truncated and display_limit is not None
                    else {}
                ),
                **({"value_labels": value_labels} if value_labels else {}),
            },
        )
    except Exception as exc:
        return failure_result(
            _with_probe_note(f"SQL Execution Error: {exc}", probe_note),
            retryable=True,
        )
