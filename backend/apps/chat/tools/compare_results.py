"""Compare two executed SqlWorkspace revisions. Does not re-run SQL."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apps.chat.agent.workspace import SqlRevision, SqlWorkspace
from apps.chat.tools.contract import failure_outcome, signals_for_tool, success_outcome

TOOL_NAME = "compare_results"


def _side(item: SqlRevision) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "rev": item.rev,
        "row_count": item.row_count,
        "truncated": bool(item.truncated),
        "fields": list(item.fields or []),
        "dataset_id": item.dataset_id,
        "result_title": item.result_title,
    }
    if item.truncated and item.display_limit is not None:
        payload["display_limit"] = item.display_limit
    return payload


def _count_line(item: SqlRevision) -> str:
    count = item.row_count
    if count is None:
        return f"{item.rev}: not executed"
    if item.truncated and item.display_limit is not None:
        return f"{item.rev}: {count} rows (truncated at {item.display_limit})"
    if item.truncated:
        return f"{item.rev}: {count} rows (truncated)"
    return f"{item.rev}: {count} rows"


def compare_query_results(
    workspace: SqlWorkspace,
    *,
    sql_ref: str = "active",
    new_ref: str,
    hypothesis: str = "",
) -> dict[str, Any]:
    """Diff two executed revisions. Row counts come from the workspace, not a new window."""
    base = workspace.resolve(sql_ref)
    new = workspace.resolve(new_ref)
    if base is None or new is None:
        return failure_outcome(
            "sql_ref and new_ref must resolve to workspace revisions; "
            "patch or execute first",
            retryable=True,
            name=TOOL_NAME,
            signals=signals_for_tool(TOOL_NAME, purpose="probe"),
        )
    if base.row_count is None or new.row_count is None:
        missing = [item.rev for item in (base, new) if item.row_count is None]
        return failure_outcome(
            "compare_results needs executed revisions with row_count; "
            f"execute {', '.join(missing)} first",
            retryable=True,
            name=TOOL_NAME,
            signals=signals_for_tool(TOOL_NAME, purpose="probe"),
        )

    row_diff = int(new.row_count) - int(base.row_count)
    summary = (
        "Comparison complete. "
        f"{_count_line(base)}. {_count_line(new)}. "
        f"row_diff: {row_diff:+d}."
    )
    if list(base.fields or []) != list(new.fields or []):
        summary += (
            f" fields {base.rev}={list(base.fields)} {new.rev}={list(new.fields)}."
        )
    if hypothesis:
        summary += f" Hypothesis tested: {hypothesis}."

    return success_outcome(
        summary,
        payload={
            "hypothesis": hypothesis,
            "base": _side(base),
            "new": _side(new),
            "row_diff": row_diff,
        },
        signals=signals_for_tool(TOOL_NAME, purpose="probe"),
        name=TOOL_NAME,
    )


def compare_from_state(
    state: Mapping[str, Any],
    *,
    sql_ref: str = "active",
    new_ref: str,
    hypothesis: str = "",
) -> dict[str, Any]:
    return compare_query_results(
        SqlWorkspace.from_state(state),
        sql_ref=sql_ref,
        new_ref=new_ref,
        hypothesis=hypothesis,
    )
