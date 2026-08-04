"""Predict node implementations for the predict graph."""

from __future__ import annotations

import traceback
from typing import Any, Dict, Literal, cast

import pandas as pd

from apps.chat.curd.chat import (
    get_chat_chart_config,
    get_chat_chart_data,
    get_chat_predict_data,
    save_analysis_predict_record,
)
from apps.chat.models.chat_model import ChatRecord
from apps.chat.result_data import format_json_data
from apps.chat.steps.predict import check_save_predict_data, generate_predict
from apps.chat.task.llm import LLMService, request_picture
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
from common.utils.data_format import DataFormat
from common.utils.utils import SQLBotLogUtil


class PredictState(RunState, total=False):
    llm_service: LLMService
    base_record: ChatRecord
    record: ChatRecord
    json_result: Dict[str, Any]
    has_data: bool


def prepare_node(state: PredictState) -> PredictState:
    try:
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
            "outcome": running_outcome(),
        }
    except Exception as exc:
        return {
            **state,
            "error": format_error_message(exc),
            "outcome": failed_outcome(exc),
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
            error_msg = format_error_message(e)
            return {
                **state,
                "error": error_msg,
                "full_text": full_text,
                "json_result": json_result,
                "outcome": failed_outcome(e),
            }


def parse_node(state: PredictState) -> PredictState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    full_text = state.get("full_text") or ""

    sink.event({"type": "info", "msg": "predict generated"})

    with session_scope() as session:
        try:
            has_data = check_save_predict_data(llm_service, session=session, res=full_text)
            outcome = (
                successful_outcome()
                if has_data
                else failed_outcome(
                    full_text or "Prediction did not produce data",
                    kind="validation",
                )
            )
            return {**state, "has_data": has_data, "outcome": outcome}
        except Exception as e:
            traceback.print_exc()
            error_msg = format_error_message(e)
            return {**state, "error": error_msg, "outcome": failed_outcome(e)}


def success_node(state: PredictState) -> PredictState:
    """MCP table/chart rendering when prediction produced data; SSE: predict-success."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "predict-success"})

    if sink.mode == "sse":
        return {**state, "json_result": json_result}

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
            if sink.mode == "markdown" and chart.get("type") != "table":
                sink.text("generate or fetch chart picture error.\n\n")
            error_msg = format_error_message(e)
            return {
                **state,
                "json_result": json_result,
                "error": error_msg,
                "outcome": failed_outcome(e),
            }

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
        persist_snapshot(session, llm_service.record.id, terminal=True)
    if sink.mode == "json":
        sink.json_result(json_result)
    return {
        **state,
        "json_result": json_result,
        "record": llm_service.record,
        "outcome": state.get("outcome") or successful_outcome(),
    }


def fail_node(state: PredictState) -> PredictState:
    return cast(PredictState, fail_turn_node(state))


# ── Routers ──────────────────────────────────────────────────────────────────


def route_after_stream(state: PredictState) -> Literal["parse", "fail"]:
    return "fail" if state.get("error") else "parse"


def route_after_prepare(state: PredictState) -> Literal["stream", "fail"]:
    return "fail" if state.get("error") else "stream"


def route_after_parse(state: PredictState) -> Literal["success", "failed", "fail"]:
    if state.get("error"):
        return "fail"
    return "success" if state.get("has_data") else "failed"


def route_after_success(state: PredictState) -> Literal["complete", "fail"]:
    return "fail" if state.get("error") else "complete"
