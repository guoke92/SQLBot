"""Analysis node implementations for the analysis graph."""

from __future__ import annotations

import traceback
from typing import Any, Dict, Literal, cast

from apps.chat.curd.chat import save_analysis_predict_record
from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.analysis import generate_analysis
from apps.chat.task.llm import LLMService
from apps.conversation.outcome import (
    failed_outcome,
    format_error_message,
    running_outcome,
    successful_outcome,
)
from apps.conversation.record import persist_snapshot
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.conversation.turn import fail_node as fail_turn_node
from common.error import SingleMessageError


class AnalysisState(RunState, total=False):
    llm_service: LLMService
    base_record: ChatRecord
    record: ChatRecord
    json_result: Dict[str, Any]


def prepare_node(state: AnalysisState) -> AnalysisState:
    try:
        base = state["base_record"]
        if not base.chart:
            raise SingleMessageError(
                f"Chat record with id {base.id} has not generated chart, do not support to analyze it"
            )
        with session_scope() as session:
            record = save_analysis_predict_record(session, base, "analysis")
        state["llm_service"].set_record(record)
        return {
            **state,
            "record": record,
            "record_id": record.id,
            "base_record_id": base.id,
            "graph_key": "analysis",
            "mode": "follow_up",
            "json_result": {"success": True, "record_id": record.id},
            "full_text": "",
            "outcome": running_outcome(),
        }
    except Exception as exc:
        return {
            **state,
            "error": format_error_message(exc),
            "outcome": failed_outcome(exc),
        }


def stream_node(state: AnalysisState) -> AnalysisState:
    llm_service = state["llm_service"]
    record = state["record"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
    full_text = ""

    sink.event({"type": "id", "id": record.id})
    sink.record_header(
        record_id=record.id,
        question=record.question,
        prefix=llm_service.trans("i18n_chat.record_id_in_mcp"),
    )
    if sink.mode == "json":
        json_result["record_id"] = record.id

    with session_scope() as session:
        try:
            for chunk in generate_analysis(llm_service, session):
                full_text += chunk.get("content") or ""
                sink.token(
                    content=chunk.get("content"),
                    reasoning_content=chunk.get("reasoning_content"),
                    event_type="analysis-result",
                )
            return {
                **state,
                "full_text": full_text,
                "json_result": json_result,
                "record": llm_service.record,
            }
        except Exception as e:
            traceback.print_exc()
            error_msg = format_error_message(e)
            return {
                **state,
                "error": error_msg,
                "full_text": full_text,
                "json_result": json_result,
                "outcome": failed_outcome(e),
            }


def complete_node(state: AnalysisState) -> AnalysisState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    full_text = state.get("full_text") or ""
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "info", "msg": "analysis generated"})
    sink.event({"type": "analysis_finish"})
    sink.text("\n\n")

    with session_scope() as session:
        persist_snapshot(session, llm_service.record.id, terminal=True)

    if sink.mode == "json":
        json_result["content"] = full_text
        sink.json_result(json_result)

    return {
        **state,
        "json_result": json_result,
        "record": llm_service.record,
        "outcome": successful_outcome(),
    }


def fail_node(state: AnalysisState) -> AnalysisState:
    return cast(AnalysisState, fail_turn_node(state))


def route_after_stream(state: AnalysisState) -> Literal["complete", "fail"]:
    return "fail" if state.get("error") else "complete"


def route_after_prepare(state: AnalysisState) -> Literal["stream", "fail"]:
    return "fail" if state.get("error") else "stream"
