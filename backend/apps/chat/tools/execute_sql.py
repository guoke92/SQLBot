"""Sandboxed SQL execution tool with permission rewrites and compact summaries."""

from __future__ import annotations

from typing import Any

from apps.chat.plan_policy import ROW_LIMIT
from apps.chat.result_window import apply_result_window, resolve_exec_row_limit
from apps.chat.steps.enum_display import apply_wiki_enum_labels
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.process_timeline import (
    PREVIEW_ROW_LIMIT,
    new_dataset_id,
    preview_rows,
    upsert_result_dataset,
)
from apps.conversation.runtime_context import (
    current_tool_call_id,
    current_worker_identity,
)
from apps.conversation.tooling import ToolResult
from apps.datasource.access import AccessScope
from common.utils.utils import SQLBotLogUtil


def execute_sql_sandbox(
    llm_service: Any,
    sql: str,
    *,
    access_scope: AccessScope | None = None,
    limit: int = ROW_LIMIT,
    sample_limit: int = PREVIEW_ROW_LIMIT,
    plan_id: str | None = None,
    dataset_id: str | None = None,
) -> ToolResult:
    """Safely execute SQL with permission rewrites and token-safe output."""
    clean_sql = (sql or "").strip().rstrip(";")
    if not clean_sql:
        return failure_result("SQL query cannot be empty")

    try:
        proto = getattr(llm_service, "protocol", None)
        ds = getattr(llm_service, "ds", None) or getattr(llm_service, "datasource", None)
        if proto is None or ds is None:
            return failure_result("Datasource or protocol not configured on session")

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

        value_labels: dict[str, dict[str, str]] = {}
        try:
            rows, value_labels = apply_wiki_enum_labels(
                sql=statement,
                fields=fields,
                rows=rows,
                llm_service=llm_service,
            )
        except Exception as exc:
            SQLBotLogUtil.warning("enum label projection degraded: %s", exc)

        row_count = len(rows)
        samples = preview_rows(rows, limit=min(sample_limit, PREVIEW_ROW_LIMIT))

        col_stats: dict[str, Any] = {}
        for field_name in fields[:10]:
            vals = [
                row.get(field_name)
                for row in rows
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
                rows=rows,
                row_count=row_count,
                truncated=truncated,
                sql=statement,
                value_labels=value_labels,
                limit=display_limit if truncated else exec_limit,
            )

        return success_result(
            f"Query executed successfully, returned {row_count} rows.",
            data={
                "sql": statement,
                "fields": fields,
                "total_rows": row_count,
                "row_count": row_count,
                "truncated": truncated,
                "sample_rows": samples,
                "preview_rows": samples,
                "column_stats": col_stats,
                "dataset_id": resolved_dataset_id,
                "plan_id": resolved_plan_id,
                **({"limit": display_limit} if truncated and display_limit is not None else {}),
                **({"value_labels": value_labels} if value_labels else {}),
            },
        )
    except Exception as exc:
        return failure_result(
            f"SQL Execution Error: {exc}",
            retryable=True,
        )
