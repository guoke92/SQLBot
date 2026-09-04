"""Result comparison tool for user challenge and caliber verification."""

from __future__ import annotations

from typing import Any, Mapping
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult


def compare_query_results(
    llm_service: Any,
    base_sql: str,
    new_sql: str,
    *,
    hypothesis: str = "",
    access_scope: Any = None,
) -> ToolResult:
    """Execute both base_sql and new_sql, compare their metrics and return differential analysis."""
    from apps.chat.tools.execute_sql import execute_sql_sandbox

    base_res = execute_sql_sandbox(llm_service, base_sql, access_scope=access_scope, limit=100)
    if not base_res["ok"]:
        return failure_result(f"Base query failed during comparison: {base_res['error']}", retryable=True)

    new_res = execute_sql_sandbox(llm_service, new_sql, access_scope=access_scope, limit=100)
    if not new_res["ok"]:
        return failure_result(f"New query failed during comparison: {new_res['error']}", retryable=True)

    base_data = base_res["data"] or {}
    new_data = new_res["data"] or {}

    base_rows = int(base_data.get("total_rows", 0))
    new_rows = int(new_data.get("total_rows", 0))
    row_diff = new_rows - base_rows

    # Compare shared numeric columns
    base_stats = base_data.get("column_stats") or {}
    new_stats = new_data.get("column_stats") or {}
    metric_diffs: dict[str, Any] = {}

    for col in set(base_stats).intersection(new_stats):
        b_sum = base_stats[col].get("sum")
        n_sum = new_stats[col].get("sum")
        if b_sum is not None and n_sum is not None:
            metric_diffs[col] = {
                "base_sum": b_sum,
                "new_sum": n_sum,
                "diff": round(n_sum - b_sum, 2),
                "ratio": round(n_sum / b_sum, 4) if b_sum != 0 else None,
            }

    diff_summary = (
        f"Comparison complete. Row count changed from {base_rows} to {new_rows} (diff: {row_diff:+d}). "
    )
    if metric_diffs:
        diff_summary += f"Metric differences: {metric_diffs}."
    if hypothesis:
        diff_summary += f" Hypothesis tested: {hypothesis}."

    return success_result(
        diff_summary,
        data={
            "hypothesis": hypothesis,
            "base": {
                "sql": base_sql,
                "row_count": base_rows,
                "sample_rows": base_data.get("sample_rows"),
            },
            "new": {
                "sql": new_sql,
                "row_count": new_rows,
                "sample_rows": new_data.get("sample_rows"),
            },
            "row_diff": row_diff,
            "metric_diffs": metric_diffs,
        },
    )
