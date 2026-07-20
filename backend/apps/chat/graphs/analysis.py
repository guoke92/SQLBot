"""Analysis follow-up graph — sole path for record analysis.

Control flow (not a wrapper over one imperative blob)::

    prepare → stream → complete
                 ↘ fail
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Literal, TypedDict

import orjson
from langgraph.graph import END, START, StateGraph

from apps.chat.curd.chat import save_analysis_predict_record
from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.analysis import generate_analysis
from apps.chat.task.llm import LLMService
from apps.conversation.record import finish as record_finish
from apps.conversation.record import save_error as record_save_error
from apps.conversation.registry import register_graph
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from common.error import SingleMessageError


class AnalysisState(RunState, total=False):
    llm_service: LLMService
    base_record: ChatRecord
    record: ChatRecord
    json_result: Dict[str, Any]


def _error_message(exc: BaseException) -> str:
    if isinstance(exc, SingleMessageError):
        return str(exc)
    return orjson.dumps(
        {"message": str(exc), "traceback": traceback.format_exc(limit=1)}
    ).decode()


def prepare_node(state: AnalysisState) -> AnalysisState:
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
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {
                **state,
                "error": error_msg,
                "full_text": full_text,
                "json_result": json_result,
            }


def complete_node(state: AnalysisState) -> AnalysisState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    full_text = state.get("full_text") or ""
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "info", "msg": "analysis generated"})
    sink.event({"type": "analysis_finish"})
    # MCP stream: historic trailing newlines after tokens
    sink.text("\n\n")

    with session_scope() as session:
        record_finish(session, llm_service.record.id)

    if sink.mode == "json":
        json_result["content"] = full_text
        sink.json_result(json_result)

    return {**state, "json_result": json_result, "record": llm_service.record}


def fail_node(state: AnalysisState) -> AnalysisState:
    sink = StreamSink.from_state(state)
    error_msg = state.get("error") or "unknown error"
    sink.error(error_msg)
    return state


def _route_after_stream(state: AnalysisState) -> Literal["complete", "fail"]:
    return "fail" if state.get("error") else "complete"


def build_analysis_graph(_ctx: Any = None, **_kwargs: Any):
    g = StateGraph(AnalysisState)
    g.add_node("prepare", prepare_node)
    g.add_node("stream", stream_node)
    g.add_node("complete", complete_node)
    g.add_node("fail", fail_node)
    g.add_edge(START, "prepare")
    g.add_edge("prepare", "stream")
    g.add_conditional_edges(
        "stream",
        _route_after_stream,
        {"complete": "complete", "fail": "fail"},
    )
    g.add_edge("complete", END)
    g.add_edge("fail", END)
    return g.compile()


register_graph("analysis", build_analysis_graph)
