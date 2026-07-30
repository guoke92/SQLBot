"""Shared terminal-state and failure semantics for conversation graphs.

Graph nodes may retain human-readable ``error`` text for display, but routing
and API success flags must use this structured contract instead of parsing
localized exception messages in multiple scenarios.
"""

from __future__ import annotations

import json
import traceback
from typing import Any, Literal, NotRequired, TypedDict

import orjson

from common.error import SingleMessageError, SQLBotDBConnectionError, SQLBotDBError

RunStatus = Literal[
    "running",
    "awaiting_input",
    "blocked",
    "success",
    "degraded",
    "failed",
    "limit_reached",
]
FailureKind = Literal[
    "unknown_identifier",
    "syntax",
    "timeout",
    "connection",
    "permission",
    "validation",
    "execution",
    "internal",
    "limit_reached",
    "empty_response",
]


class FailureInfo(TypedDict, total=False):
    kind: FailureKind
    message: str
    retryable: bool
    step_index: int


class ResultQuality(TypedDict):
    status: Literal["complete", "partial"]
    truncated: bool
    returned_rows: int


class RunOutcome(TypedDict):
    status: RunStatus
    failures: list[FailureInfo]
    successful_steps: int
    total_steps: int
    quality: NotRequired[ResultQuality]


_RETRYABLE_KINDS: frozenset[FailureKind] = frozenset(
    {"unknown_identifier", "syntax", "timeout", "validation"}
)


def _plain_message(error: BaseException | str) -> str:
    raw = str(error)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return str(parsed.get("message") or parsed.get("traceback") or raw)
    except (TypeError, ValueError):
        pass
    return raw


def format_error_message(error: BaseException) -> str:
    """Serialize one user-facing error envelope at graph boundaries."""
    if isinstance(error, SingleMessageError):
        return str(error)
    if isinstance(error, SQLBotDBConnectionError):
        return orjson.dumps(
            {"message": str(error), "type": "db-connection-err"}
        ).decode()
    if isinstance(error, SQLBotDBError):
        return orjson.dumps(
            {
                "message": "Query execution failed",
                "traceback": str(error),
                "type": "exec-query-err",
            }
        ).decode()
    return orjson.dumps(
        {"message": str(error), "traceback": traceback.format_exc(limit=1)}
    ).decode()


def classify_failure(
    error: BaseException | str,
    *,
    step_index: int | None = None,
    default_kind: FailureKind = "execution",
) -> FailureInfo:
    """Classify once at the error boundary; downstream control uses ``kind``."""
    message = _plain_message(error)
    normalized = message.lower()
    class_name = (
        error.__class__.__name__.lower() if isinstance(error, BaseException) else ""
    )

    if any(
        marker in normalized
        for marker in (
            "unknown column",
            "unknown identifier",
            "column does not exist",
            "字段不存在",
            "列不存在",
        )
    ):
        kind: FailureKind = "unknown_identifier"
    elif any(marker in normalized for marker in ("syntax error", "语法错误")):
        kind = "syntax"
    elif "timeout" in normalized or "timed out" in normalized or "超时" in normalized:
        kind = "timeout"
    elif (
        "connection" in class_name
        or "connecterror" in class_name
        or any(
            marker in normalized
            for marker in (
                "connection refused",
                "connection error",
                "could not connect",
                "连接失败",
            )
        )
    ):
        kind = "connection"
    elif any(
        marker in normalized
        for marker in (
            "permission denied",
            "not authorized",
            "forbidden",
            "无权限",
            "权限不足",
        )
    ):
        kind = "permission"
    elif any(
        marker in normalized
        for marker in (
            "validation",
            "invalid query",
            "only columns from the provided schema",
            "校验失败",
        )
    ):
        kind = "validation"
    elif default_kind == "internal":
        kind = "internal"
    else:
        kind = default_kind

    failure: FailureInfo = {
        "kind": kind,
        "message": message,
        "retryable": kind in _RETRYABLE_KINDS,
    }
    if step_index is not None:
        failure["step_index"] = step_index
    return failure


def running_outcome() -> RunOutcome:
    return {
        "status": "running",
        "failures": [],
        "successful_steps": 0,
        "total_steps": 0,
    }


def successful_outcome(
    *,
    successful_steps: int = 1,
    total_steps: int | None = None,
) -> RunOutcome:
    total = successful_steps if total_steps is None else total_steps
    return {
        "status": "success",
        "failures": [],
        "successful_steps": successful_steps,
        "total_steps": total,
    }


def awaiting_input_outcome() -> RunOutcome:
    return {
        "status": "awaiting_input",
        "failures": [],
        "successful_steps": 0,
        "total_steps": 0,
    }


def blocked_outcome(message: str) -> RunOutcome:
    return {
        "status": "blocked",
        "failures": [
            {
                "kind": "validation",
                "message": message,
                "retryable": False,
            }
        ],
        "successful_steps": 0,
        "total_steps": 0,
    }


def failed_outcome(
    error: BaseException | str,
    *,
    kind: FailureKind = "internal",
) -> RunOutcome:
    failure = classify_failure(error, default_kind=kind)
    if kind == "limit_reached":
        failure["kind"] = "limit_reached"
        failure["retryable"] = False
    return {
        "status": "limit_reached" if kind == "limit_reached" else "failed",
        "failures": [failure],
        "successful_steps": 0,
        "total_steps": 0,
    }


def outcome_from_steps(
    steps: list[dict[str, Any]],
    *,
    planned_count: int = 0,
) -> RunOutcome:
    """Derive one authoritative outcome from materialized step results."""
    failures: list[FailureInfo] = []
    successful = 0
    for index, step in enumerate(steps):
        if step.get("error"):
            raw_failure = step.get("failure")
            if isinstance(raw_failure, dict) and raw_failure.get("kind"):
                failure = FailureInfo(**raw_failure)
                failure.setdefault("step_index", index)
            else:
                failure = classify_failure(str(step["error"]), step_index=index)
            failures.append(failure)
        else:
            successful += 1

    total = len(steps)
    if total == 0 and planned_count > 0:
        return {
            "status": "success",
            "failures": [],
            "successful_steps": planned_count,
            "total_steps": planned_count,
        }
    if failures and not successful:
        status: RunStatus = "failed"
    elif failures:
        status = "degraded"
    elif total:
        status = "success"
    else:
        status = "failed"
        failures = [
            classify_failure(
                "Conversation completed without a result",
                default_kind="internal",
            )
        ]
    return {
        "status": status,
        "failures": failures,
        "successful_steps": successful,
        "total_steps": total,
    }


def outcome_allows_retry(outcome: RunOutcome) -> bool:
    failures = outcome.get("failures") or []
    return bool(failures) and all(bool(item.get("retryable")) for item in failures)


def outcome_is_success(outcome: RunOutcome) -> bool:
    return outcome.get("status") in {
        "awaiting_input",
        "success",
        "degraded",
    }
