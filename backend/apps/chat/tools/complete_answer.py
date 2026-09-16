"""Explicit no-SQL terminal-answer tool for the unified agent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.tools.base import failure_result, success_result
from apps.conversation.runtime_context import current_worker_identity, peek_runtime
from apps.conversation.tooling import ToolResult

TOOL_NAME = "complete_without_sql"


def _sql_already_delivered() -> bool:
    run_id, _token = current_worker_identity()
    if not run_id:
        return False
    snap = peek_runtime(run_id) or {}
    return bool(snap.get("sql_delivered"))


def complete_without_sql(content: str) -> ToolResult:
    """Record a user-facing answer that does not deliver SQL."""
    if _sql_already_delivered():
        return failure_result(
            "SQL already delivered; do not call complete_without_sql. "
            "Close with a §6 caliber summary only.",
            retryable=False,
        )
    text = str(content or "").strip()
    if not text:
        return failure_result(
            "complete_without_sql requires non-empty content",
            retryable=True,
        )
    return success_result(
        "Terminal answer recorded without SQL.",
        data={"terminal_answer": True, "content": text},
    )


def terminal_text_from_steps(tool_steps: Sequence[Any] | None) -> str:
    """Latest successful complete_without_sql content, or empty."""
    for step in reversed(list(tool_steps or [])):
        if not isinstance(step, Mapping) or not step.get("ok"):
            continue
        name = str(step.get("tool") or step.get("name") or "")
        if name != TOOL_NAME:
            continue
        result = step.get("result") if isinstance(step.get("result"), Mapping) else {}
        data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
        if data.get("terminal_answer"):
            return str(data.get("content") or "").strip()
    return ""


def has_terminal_text_answer(tool_steps: Sequence[Any] | None) -> bool:
    return bool(terminal_text_from_steps(tool_steps))
