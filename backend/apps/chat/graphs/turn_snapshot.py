"""ChatRecord answer projection committed by finalize_run."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any, Literal, cast

import orjson

from apps.conversation.outcome import RunOutcome, public_error_message
from common.utils.utils import SQLBotLogUtil


def record_snapshot_values(
    all_steps: list[dict[str, Any]],
    analysis_text: str = "",
    *,
    finish: bool = False,
    outcome: RunOutcome | None = None,
    public_error: str | None = None,
    llm_service: Any = None,
    failure_code: str | None = None,
    failure_retryable: bool = True,
    execution_mode: Literal["verified", "unverified", "agent"] = "verified",
    assumptions: list[dict[str, Any]] | None = None,
    confirmed_calibers: list[dict[str, Any]] | None = None,
    knowledge_refs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the ChatRecord projection committed by ``finalize_run``."""
    if outcome is None:
        raise ValueError("Terminal snapshot requires an outcome")
    published_outcome = outcome
    if public_error and outcome["status"] in {"failed", "limit_reached"}:
        try:
            parsed_public_error = orjson.loads(public_error)
            safe_message = str(parsed_public_error.get("message") or public_error)
        except (TypeError, ValueError):
            safe_message = public_error
        published_outcome = cast(RunOutcome, deepcopy(outcome))
        for failure in published_outcome.get("failures") or []:
            failure["message"] = safe_message
    error: str | None = None
    if finish and outcome and outcome["status"] in {"failed", "limit_reached"}:
        failures = outcome.get("failures") or []
        error = public_error or str(
            failures[0].get("message")
            if failures
            else "Conversation completed without a usable result"
        )

    answer_datasets: list[dict[str, Any]] = []
    for index, step in enumerate(all_steps):
        if step.get("error"):
            failure = dict(step.get("failure") or {})
            raw_public_error = public_error_message(
                str(step.get("error") or "Query failed")
            )
            try:
                parsed_public_error = orjson.loads(raw_public_error)
            except (TypeError, ValueError):
                parsed_public_error = {
                    "type": "QUERY_FAILED",
                    "message": raw_public_error,
                }
            answer_datasets.append(
                {
                    "dataset_id": str(step.get("dataset_id") or f"dataset_{index + 1}"),
                    "status": "failed",
                    "required": bool(step.get("required", True)),
                    "title": str(step.get("brief") or ""),
                    "sql": "",
                    "fields": [],
                    "rows": [],
                    "row_count": None,
                    "truncated": False,
                    "error": {
                        "code": str(
                            parsed_public_error.get("type")
                            or failure.get("kind")
                            or "QUERY_FAILED"
                        ).upper(),
                        "message": str(
                            parsed_public_error.get("message") or "Query failed"
                        ),
                        "retryable": bool(failure.get("retryable")),
                    },
                }
            )
            continue
        result = (
            step.get("result")
            if isinstance(step.get("result"), dict)
            else step.get("data")
            if isinstance(step.get("data"), dict)
            else {}
        )
        rows = list(result.get("preview_rows") or result.get("data") or [])
        preview = list(result.get("preview_rows") or rows[:3])
        existing_labels = result.get("value_labels")
        step_value_labels: dict[str, dict[str, str]] = (
            {
                str(field): {str(raw): str(label) for raw, label in mapping.items()}
                for field, mapping in existing_labels.items()
                if isinstance(mapping, Mapping)
            }
            if isinstance(existing_labels, Mapping)
            else {}
        )
        if not step_value_labels:
            try:
                from apps.chat.steps.enum_display import apply_wiki_enum_labels

                preview, step_value_labels = apply_wiki_enum_labels(
                    sql=str(step.get("format_statement") or step.get("sql") or ""),
                    fields=[str(f) for f in (result.get("fields") or [])],
                    rows=preview,
                    llm_service=llm_service,
                    tables=[
                        str(t) for t in (step.get("tables") or step.get("resources") or [])
                    ],
                )
            except Exception as _enum_exc:  # noqa: BLE001
                SQLBotLogUtil.warning("enum translate degraded: %s", _enum_exc)
        row_count = result.get("row_count")
        if row_count is None:
            row_count = len(result.get("data") or preview)
        answer_datasets.append(
            {
                "dataset_id": str(step.get("dataset_id") or f"dataset_{index + 1}"),
                "status": "degraded"
                if published_outcome.get("status") == "degraded"
                else "succeeded",
                "required": bool(step.get("required", True)),
                "title": str(step.get("brief") or ""),
                "sql": str(step.get("format_statement") or step.get("sql") or ""),
                "fields": list(result.get("fields") or []),
                "rows": [],
                "preview_rows": preview,
                "row_count": row_count,
                **({"value_labels": step_value_labels} if step_value_labels else {}),
                "truncated": bool(result.get("truncated")),
                "limit": result.get("limit"),
                "truncation_reason": result.get("truncation_reason"),
                "presentation": step.get("presentation"),
                "chart": step.get("chart"),
            }
        )
    answer_status = (
        "failed"
        if published_outcome.get("status") in {"failed", "limit_reached"}
        else "degraded"
        if published_outcome.get("status") == "degraded"
        else "succeeded"
    )
    answer_error: dict[str, Any] | None = None
    if error:
        try:
            parsed_error = orjson.loads(error)
        except (TypeError, ValueError):
            parsed_error = {"type": "QUERY_FAILED", "message": error}
        answer_error = {
            "code": str(
                failure_code or parsed_error.get("type") or "QUERY_FAILED"
            ).upper(),
            "message": str(parsed_error.get("message") or "Query failed"),
            "retryable": failure_retryable,
        }
    return {
        "terminal": finish,
        "error": error,
        "answer": {
            "kind": "query",
            "status": answer_status,
            "content": analysis_text,
            "execution_mode": execution_mode,
            "datasets": answer_datasets,
            "intent_summary": "",
            "source_record_ids": [],
            "confirmed_calibers": list(confirmed_calibers or []),
            "assumptions": list(assumptions or []),
            "knowledge_refs": dict(knowledge_refs) if knowledge_refs else None,
            "quality": published_outcome.get("quality"),
            "error": answer_error,
        },
    }
