"""Internal accepted-step payload and legacy chart read projection.

``TurnAnswerV1`` in ``ChatRecord.answer`` is the only durable user-visible
answer. This module keeps the accepted-step structure used inside the quality
pipeline and derives old chart endpoint shapes at read time; the projection is
never a second persisted answer.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict, cast

from apps.conversation.outcome import RunOutcome, failed_outcome


class AnswerPresentationColumn(TypedDict):
    field: str
    label: str
    display: str


class AnswerPresentation(TypedDict):
    title: str
    columns: list[AnswerPresentationColumn]


class AnswerStep(TypedDict, total=False):
    sql: str
    brief: str
    presentation: AnswerPresentation
    chart: dict[str, Any] | None
    data: dict[str, Any]
    error: str
    failure: dict[str, Any]


class AnswerPayload(TypedDict):
    steps: list[AnswerStep]
    analysis: str
    outcome: RunOutcome


def build_answer_payload(
    steps: Sequence[Mapping[str, Any]],
    analysis: str,
    outcome: RunOutcome,
) -> AnswerPayload:
    """Project accepted internal query steps into the terminal answer shape."""
    answer_steps: list[AnswerStep] = []
    for step in steps:
        entry: AnswerStep = {
            "sql": str(step.get("format_statement") or step.get("sql") or ""),
            "brief": str(step.get("brief") or ""),
            "chart": (
                cast(dict[str, Any], step.get("chart"))
                if isinstance(step.get("chart"), dict)
                else None
            ),
        }
        presentation = step.get("presentation")
        if isinstance(presentation, Mapping):
            entry["presentation"] = cast(AnswerPresentation, dict(presentation))
        if step.get("error"):
            entry["error"] = str(step["error"])
            failure = step.get("failure")
            if isinstance(failure, dict):
                entry["failure"] = dict(failure)
        result = step.get("result")
        if isinstance(result, Mapping):
            entry["data"] = {
                "fields": list(result.get("fields") or []),
                "fields_info": result.get("fields_info"),
                "data": list(result.get("data") or []),
                "limit": result.get("limit"),
                "row_count": result.get("row_count"),
                "truncated": result.get("truncated"),
                "truncation_reason": result.get("truncation_reason"),
                "datasource": result.get("datasource"),
            }
        answer_steps.append(entry)
    return {
        "steps": answer_steps,
        "analysis": analysis or "",
        "outcome": outcome,
    }


def build_failed_answer_payload(error: BaseException | str) -> AnswerPayload:
    """Create the canonical terminal payload for failures before execution."""
    return build_answer_payload([], "", failed_outcome(error))


def project_turn_answer(value: Mapping[str, Any]) -> AnswerPayload:
    """Project durable TurnAnswerV1 for legacy chart-only read consumers.

    The projection is never persisted. ``ChatRecord.answer`` remains the sole
    terminal answer truth for normal conversation turns.
    """
    datasets = value.get("datasets") or value.get("source_datasets") or []
    steps: list[AnswerStep] = []
    failures: list[dict[str, Any]] = []
    for item in datasets:
        if not isinstance(item, Mapping):
            continue
        if item.get("status") == "failed":
            error = item.get("error") if isinstance(item.get("error"), Mapping) else {}
            failures.append(
                {
                    "kind": str(error.get("code") or "QUERY_FAILED"),
                    "message": str(error.get("message") or "Query failed"),
                    "retryable": bool(error.get("retryable")),
                }
            )
            continue
        entry: AnswerStep = {
            "sql": str(item.get("sql") or ""),
            "brief": str(item.get("title") or ""),
            "chart": (
                cast(dict[str, Any], item.get("chart"))
                if isinstance(item.get("chart"), dict)
                else None
            ),
            "data": {
                "fields": list(item.get("fields") or []),
                "data": list(item.get("rows") or []),
                "row_count": item.get("row_count"),
                "truncated": bool(item.get("truncated")),
            },
        }
        if isinstance(item.get("presentation"), Mapping):
            entry["presentation"] = cast(AnswerPresentation, dict(item["presentation"]))
        steps.append(entry)
    raw_status = str(value.get("status") or "failed")
    outcome_status = (
        "success"
        if raw_status == "succeeded"
        else "degraded"
        if raw_status == "degraded"
        else "failed"
    )
    outcome: RunOutcome = {
        "status": outcome_status,  # type: ignore[typeddict-item]
        "failures": failures,
        "successful_steps": len(steps),
        "total_steps": len(steps) + len(failures),
    }
    if isinstance(value.get("quality"), Mapping):
        outcome["quality"] = cast(Any, dict(value["quality"]))
    return {
        "steps": steps,
        "analysis": str(value.get("content") or ""),
        "outcome": outcome,
    }


def is_answer_payload(value: Any) -> bool:
    return bool(
        isinstance(value, Mapping)
        and isinstance(value.get("steps"), list)
        and isinstance(value.get("outcome"), Mapping)
    )


def get_answer_step_data(
    payload: Mapping[str, Any],
    step_index: int = 0,
) -> dict[str, Any]:
    """Select one result dataset from the canonical terminal answer."""
    if not is_answer_payload(payload):
        raise ValueError("Invalid NLQ answer payload")
    steps = payload.get("steps") or []
    if not steps:
        return {}
    index = step_index if 0 <= step_index < len(steps) else 0
    step = steps[index]
    data = step.get("data") if isinstance(step, Mapping) else None
    return dict(data) if isinstance(data, Mapping) else {}


def normalize_answer_payload(
    payload: Mapping[str, Any],
    *,
    normalize_data: Callable[[dict[str, Any]], dict[str, Any]],
) -> AnswerPayload:
    """Normalize step row values without changing the answer envelope."""
    if not is_answer_payload(payload):
        raise ValueError("Invalid NLQ answer payload")
    normalized = deepcopy(dict(payload))
    normalized_steps: list[AnswerStep] = []
    for raw_step in normalized.get("steps") or []:
        if not isinstance(raw_step, dict):
            raise ValueError("Invalid NLQ answer step")
        step = cast(AnswerStep, raw_step)
        raw_data = step.get("data")
        if isinstance(raw_data, dict):
            step["data"] = normalize_data(raw_data)
        normalized_steps.append(step)
    normalized["steps"] = normalized_steps
    normalized["analysis"] = str(normalized.get("analysis") or "")
    return cast(AnswerPayload, normalized)
