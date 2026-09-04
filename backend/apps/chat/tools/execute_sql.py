"""Sandboxed SQL execution tool with permission rewrites and compact summaries."""

from __future__ import annotations

from typing import Any, Mapping
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult
from apps.datasource.access import AccessScope
from apps.protocol.base import QueryPlan


def execute_sql_sandbox(
    llm_service: Any,
    sql: str,
    *,
    access_scope: AccessScope | None = None,
    limit: int = 1000,
    sample_limit: int = 5,
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

        # 1. Parse into QueryPlan
        payload = {"sql": clean_sql}
        plan = proto.parse_candidate_payload(payload)
        if not plan.success:
            return failure_result(f"Invalid SQL payload: {plan.message}")

        # 2. Validate against allowed resources if available
        allowed_resources = getattr(access_scope, "resource_names", None) or getattr(llm_service, "table_name_list", None) or []
        if allowed_resources:
            plan = proto.validate_plan(ds, plan, allowed_resources)
            if not plan.success:
                return failure_result(f"SQL validation error: {plan.message}")

        # 3. Execute through protocol with row limit
        exec_limit = max(1, min(limit, 1000))
        qr = proto.execute(ds, plan, max_rows=exec_limit)
        
        rows = list(qr.data or [])
        fields = list(qr.fields or [])
        row_count = len(rows)

        # 4. Create lightweight summary for context window protection (max 3 rows for LLM message)
        sample_rows = rows[:min(sample_limit, 3)]
        
        # Column level brief stats
        col_stats: dict[str, Any] = {}
        for f in fields[:10]:
            vals = [r.get(f) for r in rows if isinstance(r, dict) and r.get(f) is not None]
            col_stats[f] = {
                "non_null_count": len(vals),
                "null_count": row_count - len(vals),
            }
            num_vals = [float(v) for v in vals if isinstance(v, (int, float))]
            if num_vals:
                col_stats[f]["min"] = min(num_vals)
                col_stats[f]["max"] = max(num_vals)
                col_stats[f]["sum"] = round(sum(num_vals), 2)

        return success_result(
            f"Query executed successfully, returned {row_count} rows.",
            data={
                "sql": plan.statement or clean_sql,
                "fields": fields,
                "total_rows": row_count,
                "sample_rows": sample_rows,
                "column_stats": col_stats,
                "full_rows": rows,  # Retained in execution state for finalize
            },
        )
    except Exception as exc:
        return failure_result(
            f"SQL Execution Error: {exc}",
            retryable=True,
        )
