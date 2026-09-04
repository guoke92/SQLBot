"""Base definitions and contract for agent deterministic tools."""

from __future__ import annotations

from typing import Any, Mapping
from apps.conversation.tooling import FailureInfo, ToolResult, tool_failure, tool_success, classify_failure


def success_result(summary: str, data: Any = None) -> ToolResult:
    return tool_success(summary, data=data)


def failure_result(
    error: str,
    *,
    failure: FailureInfo | None = None,
    summary: str | None = None,
    data: Any = None,
    retryable: bool | None = None,
) -> ToolResult:
    if failure is None:
        failure = classify_failure(error)
        if retryable is not None:
            failure = {**failure, "retryable": bool(retryable)}
    elif retryable is not None:
        failure = {**failure, "retryable": bool(retryable)}
    return tool_failure(summary or error, error, data=data, failure=failure)
