"""Downstream analysis/prediction agent nodes."""

from __future__ import annotations

from typing import Any, Literal

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    _TEMPORAL_RE,
    NlqState,
    _fail,
    _llm_service,
)
from apps.chat.models.chat_model import (
    OperationEnum,
)
from apps.chat.steps.observability import log_span
from apps.chat.steps.turn_agents import run_turn_agent
from apps.conversation.outcome import (
    successful_outcome,
)

# monkeypatch-surface imports: tests setattr these names on submodules
from apps.conversation.run_service import finalize_run  # noqa: F401
from apps.conversation.runtime_context import attach_runtime  # noqa: F401
from apps.conversation.session import session_scope  # noqa: F401
from apps.conversation.sink import StreamSink
from common.error import SingleMessageError


def analysis_agent_node(state: NlqState) -> NlqState:
    return _run_downstream_agent(state, task_kind="analysis")


def prediction_agent_node(state: NlqState) -> NlqState:
    return _run_downstream_agent(state, task_kind="prediction")


def _run_downstream_agent(
    state: NlqState, *, task_kind: Literal["analysis", "prediction"]
) -> NlqState:
    llm_service = _llm_service(state)
    candidate_steps = list((state.get("accepted_candidate") or {}).get("steps") or [])
    required_failures = [
        item
        for item in candidate_steps
        if isinstance(item, dict)
        and bool(item.get("required", True))
        and bool(item.get("error"))
    ]
    if required_failures:
        return _fail(
            state,
            state.get("record_id"),
            SingleMessageError(
                f"{task_kind} was not started because a required source dataset failed"
            ),
        )
    datasets = _turn_source_datasets(state)
    if not datasets:
        return _fail(
            state,
            state.get("record_id"),
            SingleMessageError(f"{task_kind} requires a usable result dataset"),
        )
    if task_kind == "prediction" and not any(
        item.get("has_time_field")
        and item.get("has_numeric_measure")
        and int(item.get("valid_points") or 0) >= 6
        for item in datasets
    ):
        return _fail(
            state,
            state.get("record_id"),
            SingleMessageError(
                "Prediction requires a time series with at least 6 valid points"
            ),
        )
    sink = StreamSink.from_state(state)
    operate = (
        OperationEnum.ANALYSIS
        if task_kind == "analysis"
        else OperationEnum.PREDICT_DATA
    )
    try:
        with log_span(
            operate=operate,
            record_id=llm_service.record.id,
            ai_modal_id=llm_service.chat_question.ai_modal_id,
            ai_modal_name=llm_service.chat_question.ai_modal_name,
            local_operation=False,
            graph_node=f"{task_kind}_agent",
            title_key=(
                "chat.log.ANALYSIS"
                if task_kind == "analysis"
                else "chat.log.PREDICT_DATA"
            ),
        ) as span:
            result = run_turn_agent(
                llm_service,
                task_kind=task_kind,
                question=str(llm_service.record.question or ""),
                datasets=datasets,
                on_stream=lambda chunk: sink.token(
                    content="",
                    reasoning_content=chunk.get("reasoning_content") or "",
                    event_type=f"{task_kind}-reasoning",
                ),
            )
            span.set_usage(result.usage)
            span["reasoning_content"] = result.reasoning
            span.set_model_context(result.model_messages)
            span.set_detail(
                {
                    "dataset_ids": [item.get("dataset_id") for item in datasets],
                    "chars": len(result.content),
                    "forecast_rows": len(result.forecast_rows),
                }
            )
            span.set_summary("chat.audit.response_ready")
        source_records = tuple(
            dict.fromkeys(
                int(item.get("source_record_id"))
                for item in datasets
                if item.get("source_record_id")
            )
        )
        if task_kind == "analysis":
            answer = {
                "kind": "analysis",
                "content": result.content,
                "dataset_ids": [str(item.get("dataset_id") or "") for item in datasets],
                "source_datasets": datasets,
                "source_record_ids": list(source_records),
                "assumptions": [],
                "quality": (state.get("outcome") or {}).get("quality"),
            }
            status = "succeeded"
        else:
            status = "succeeded" if result.forecast_rows else "degraded"
            answer = {
                "kind": "prediction",
                "content": result.content,
                "dataset_id": str(datasets[0].get("dataset_id") or ""),
                "forecast_rows": result.forecast_rows,
                "source_datasets": datasets,
                "source_record_ids": list(source_records),
                "assumptions": [],
                "quality": (state.get("outcome") or {}).get("quality"),
            }
        return {
            **state,
            "terminal_answer": answer,
            "analysis_text": result.content,
            "outcome": (
                successful_outcome()
                if status == "succeeded"
                else {**successful_outcome(), "status": "degraded"}
            ),
        }
    except Exception as exc:
        return _fail(state, state.get("record_id"), exc)


def _turn_source_datasets(state: NlqState) -> list[dict[str, Any]]:
    existing = [
        dict(item)
        for item in state.get("source_datasets") or []
        if isinstance(item, dict) and item.get("status") in {"succeeded", "degraded"}
    ]
    if existing:
        return existing
    candidate = dict(state.get("accepted_candidate") or {})
    datasets: list[dict[str, Any]] = []
    for index, step in enumerate(candidate.get("steps") or []):
        if not isinstance(step, dict) or step.get("error"):
            continue
        result = step.get("result") if isinstance(step.get("result"), dict) else {}
        datasets.append(
            _dataset_capabilities(
                {
                    "dataset_id": str(step.get("dataset_id") or f"dataset_{index + 1}"),
                    "status": "degraded"
                    if (state.get("outcome") or {}).get("status") == "degraded"
                    else "succeeded",
                    "required": bool(step.get("required", True)),
                    "title": str(step.get("brief") or ""),
                    "sql": str(step.get("format_statement") or step.get("sql") or ""),
                    "fields": list(result.get("fields") or []),
                    "rows": list(result.get("data") or []),
                    "row_count": int(
                        result.get("row_count") or len(result.get("data") or [])
                    ),
                    "truncated": bool(result.get("truncated")),
                    "limit": result.get("limit"),
                    "truncation_reason": result.get("truncation_reason"),
                    "presentation": step.get("presentation"),
                    "chart": step.get("chart"),
                }
            )
        )
    return datasets


def _dataset_capabilities(dataset: dict[str, Any]) -> dict[str, Any]:
    rows = [item for item in dataset.get("rows") or [] if isinstance(item, dict)]
    fields = [str(item) for item in dataset.get("fields") or []]
    temporal = False
    numeric = False
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        if not values:
            continue
        if any(
            isinstance(value, int | float) and not isinstance(value, bool)
            for value in values
        ):
            numeric = True
        if any(_TEMPORAL_RE.match(str(value).strip()) for value in values):
            temporal = True
    return {
        **dataset,
        "has_time_field": temporal,
        "has_numeric_measure": numeric,
        "valid_points": len(rows),
    }
