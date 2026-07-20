"""Predict follow-up graph — sole path for record data prediction.

Control flow::

    prepare → stream → parse → success|failed → complete
                        ↘ fail
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Literal, TypedDict

import orjson
import pandas as pd
from langgraph.graph import END, START, StateGraph

from apps.chat.curd.chat import (
    format_json_data,
    get_chat_chart_config,
    get_chat_chart_data,
    get_chat_predict_data,
    save_analysis_predict_record,
)
from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.predict import check_save_predict_data, generate_predict
from apps.chat.task.llm import LLMService, request_picture
from apps.conversation.record import finish as record_finish
from apps.conversation.record import save_error as record_save_error
from apps.conversation.registry import register_graph
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from common.error import SingleMessageError
from common.utils.data_format import DataFormat
from common.utils.utils import SQLBotLogUtil


class PredictState(RunState, total=False):
    llm_service: LLMService
    base_record: ChatRecord
    record: ChatRecord
    json_result: Dict[str, Any]
    has_data: bool
    outcome: Literal["success", "failed"]


def _error_message(exc: BaseException) -> str:
    if isinstance(exc, SingleMessageError):
        return str(exc)
    return orjson.dumps(
        {"message": str(exc), "traceback": traceback.format_exc(limit=1)}
    ).decode()


def prepare_node(state: PredictState) -> PredictState:
    base = state["base_record"]
    if not base.chart:
        raise SingleMessageError(
            f"Chat record with id {base.id} has not generated chart, do not support to analyze it"
        )
    with session_scope() as session:
        record = save_analysis_predict_record(session, base, "predict")
    state["llm_service"].set_record(record)
    return {
        **state,
        "record": record,
        "record_id": record.id,
        "base_record_id": base.id,
        "graph_key": "predict",
        "mode": "follow_up",
        "json_result": {"success": True, "record_id": record.id},
        "full_text": "",
    }


def stream_node(state: PredictState) -> PredictState:
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
            for chunk in generate_predict(llm_service, session):
                full_text += chunk.get("content") or ""
                sink.token(
                    content=chunk.get("content"),
                    reasoning_content=chunk.get("reasoning_content"),
                    event_type="predict-result",
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


def parse_node(state: PredictState) -> PredictState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    full_text = state.get("full_text") or ""

    sink.event({"type": "info", "msg": "predict generated"})

    with session_scope() as session:
        try:
            has_data = check_save_predict_data(llm_service, session=session, res=full_text)
            return {**state, "has_data": has_data, "outcome": "success" if has_data else "failed"}
        except Exception as e:
            traceback.print_exc()
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {**state, "error": error_msg}


def success_node(state: PredictState) -> PredictState:
    """MCP table/chart rendering when prediction produced data; SSE: predict-success."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "predict-success"})

    if sink.mode == "sse":
        return {**state, "json_result": json_result}

    # markdown / json: attach data (+ optional SSR picture for non-table charts)
    with session_scope() as session:
        chart = get_chat_chart_config(session, llm_service.record.id)
        origin_data = get_chat_chart_data(session, llm_service.record.id)
        predict_data = get_chat_predict_data(session, llm_service.record.id)

        if sink.mode == "markdown":
            md_data, fields_list = DataFormat.convert_data_fields_for_pandas(
                chart, origin_data.get("fields"), predict_data
            )
            if not md_data or not fields_list:
                sink.text("Predict data result is empty.\n\n")
            else:
                df = pd.DataFrame(md_data, columns=fields_list)
                df_safe = DataFormat.safe_convert_to_string(df)
                sink.text(df_safe.to_markdown(index=False) + "\n\n")
        else:
            json_result["origin_data"] = origin_data
            json_result["predict_data"] = predict_data

        try:
            if chart.get("type") != "table":
                data = get_chat_chart_data(session, llm_service.record.id)
                data["data"] = data.get("data") + predict_data
                image_url, error = request_picture(
                    llm_service.record.chat_id,
                    llm_service.record.id,
                    chart,
                    format_json_data(data),
                )
                SQLBotLogUtil.info(image_url)
                if sink.mode == "markdown":
                    sink.text(f'![{chart.get("type")}]({image_url})')
                else:
                    json_result["image_url"] = image_url
                if error is not None:
                    raise error
        except Exception as e:
            # Historic: emit partial picture-error note then fail the run (no finish).
            if sink.mode == "markdown" and chart.get("type") != "table":
                sink.text("generate or fetch chart picture error.\n\n")
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {**state, "json_result": json_result, "error": error_msg}

    return {**state, "json_result": json_result}


def failed_node(state: PredictState) -> PredictState:
    sink = StreamSink.from_state(state)
    full_text = state.get("full_text") or ""
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "predict-failed"})
    if sink.mode == "markdown":
        sink.text(full_text + "\n\n")
    if sink.mode == "json":
        json_result["success"] = False
        json_result["message"] = full_text
    return {**state, "json_result": json_result}


def complete_node(state: PredictState) -> PredictState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "predict_finish"})
    with session_scope() as session:
        record_finish(session, llm_service.record.id)
    if sink.mode == "json":
        sink.json_result(json_result)
    return {**state, "json_result": json_result, "record": llm_service.record}


def fail_node(state: PredictState) -> PredictState:
    sink = StreamSink.from_state(state)
    sink.error(state.get("error") or "unknown error")
    return state


def _route_after_stream(state: PredictState) -> Literal["parse", "fail"]:
    return "fail" if state.get("error") else "parse"


def _route_after_parse(state: PredictState) -> Literal["success", "failed", "fail"]:
    if state.get("error"):
        return "fail"
    return "success" if state.get("has_data") else "failed"


def build_predict_graph(_ctx: Any = None, **_kwargs: Any):
    g = StateGraph(PredictState)
    g.add_node("prepare", prepare_node)
    g.add_node("stream", stream_node)
    g.add_node("parse", parse_node)
    g.add_node("success", success_node)
    g.add_node("failed", failed_node)
    g.add_node("complete", complete_node)
    g.add_node("fail", fail_node)

    g.add_edge(START, "prepare")
    g.add_edge("prepare", "stream")
    g.add_conditional_edges(
        "stream",
        _route_after_stream,
        {"parse": "parse", "fail": "fail"},
    )
    g.add_conditional_edges(
        "parse",
        _route_after_parse,
        {"success": "success", "failed": "failed", "fail": "fail"},
    )
    g.add_conditional_edges(
        "success",
        lambda s: "fail" if s.get("error") else "complete",
        {"complete": "complete", "fail": "fail"},
    )
    g.add_edge("failed", "complete")
    g.add_edge("complete", END)
    g.add_edge("fail", END)
    return g.compile()


register_graph("predict", build_predict_graph)
