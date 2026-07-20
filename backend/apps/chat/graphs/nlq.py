"""NLQ primary graph — sole path for generate-SQL → execute → chart.

Domain match steps are first-class graph nodes (compose chat.steps atoms).
SSE type strings stay frozen; runtime entry is only submit_graph("nlq").

Topology::

    prepare_record → ensure_datasource → match_terminology → match_training
        → match_custom_prompts → build_context → generate_sql
        → early_finish | execute → data_finish | generate_chart → complete
        any ↘ fail
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Literal, Optional

import orjson
import pandas as pd
from langgraph.graph import END, START, StateGraph
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum

from apps.chat.curd.chat import (
    end_log,
    format_json_data,
    get_chat_chart_data,
    rename_chat,
    save_re_exec,
    save_sql,
    start_log,
)
from apps.chat.models.chat_model import AxisObj, ChatFinishStep, OperationEnum, RenameChat
from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.steps.chart import generate_chart
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.datasource import select_datasource, validate_history_ds
from apps.chat.steps.messages import build_prompt_messages
from apps.chat.steps.permissions import (
    DYNAMIC_SUBSQL_PREFIX,
    generate_assistant_dynamic_sql,
    generate_filter,
)
from apps.chat.steps.persist import check_save_chart, check_save_sql, save_sql_data
from apps.chat.steps.sql import generate_sql
from apps.chat.steps.terminology import match_terminology
from apps.chat.steps.training import match_training
from apps.chat.task.llm import LLMService, request_picture
from apps.conversation.record import finish as record_finish
from apps.conversation.record import save_error as record_save_error
from apps.conversation.registry import register_graph
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.datasource.crud.permission import is_normal_user
from apps.datasource.models.datasource import CoreDatasource
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_ROW_PERMISSION
from common.error import SingleMessageError, SQLBotDBConnectionError, SQLBotDBError
from common.utils.data_format import DataFormat
from common.utils.utils import SQLBotLogUtil


class NlqState(RunState, total=False):
    llm_service: LLMService
    finish_step: ChatFinishStep
    return_img: bool
    json_result: Dict[str, Any]
    plan: Any
    sql: Optional[str]
    format_statement: Optional[str]
    chart_type: Optional[str]
    full_sql_text: str
    dynamic_sql_result: Any
    sqlbot_temp_sql_text: Optional[str]
    assistant_dynamic_sql: Optional[str]
    query_result: Dict[str, Any]
    chart: Dict[str, Any]


def _as_finish_step(value: Any) -> ChatFinishStep:
    if isinstance(value, ChatFinishStep):
        return value
    if isinstance(value, int):
        return ChatFinishStep(value)
    return ChatFinishStep.GENERATE_CHART


def _error_message(exc: BaseException) -> str:
    if isinstance(exc, SingleMessageError):
        return str(exc)
    if isinstance(exc, SQLBotDBConnectionError):
        return orjson.dumps({"message": str(exc), "type": "db-connection-err"}).decode()
    if isinstance(exc, SQLBotDBError):
        return orjson.dumps(
            {
                "message": "Query execution failed",
                "traceback": str(exc),
                "type": "exec-query-err",
            }
        ).decode()
    return orjson.dumps(
        {"message": str(exc), "traceback": traceback.format_exc(limit=1)}
    ).decode()


def _ds_scope(llm_service: LLMService) -> tuple[Optional[int], Optional[int]]:
    if not llm_service.ds:
        return None, None
    oid = llm_service.ds.oid if isinstance(llm_service.ds, CoreDatasource) else 1
    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    return oid, ds_id


def _fail(state: NlqState, record_id: Optional[int], exc: BaseException) -> NlqState:
    traceback.print_exc()
    error_msg = _error_message(exc)
    if record_id is not None:
        try:
            with session_scope() as session:
                record_save_error(session, record_id, error_msg)
        except Exception:
            traceback.print_exc()
    return {**state, "error": error_msg}


def prepare_record_node(state: NlqState) -> NlqState:
    """Emit SSE header only — no domain match (match runs after ds is sure)."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    record = llm_service.get_record()
    finish_step = _as_finish_step(state.get("finish_step"))
    return_img = bool(state.get("return_img", True))
    json_result: Dict[str, Any] = {"success": True}

    try:
        sink.event({"type": "id", "id": record.id})
        if record.regenerate_record_id:
            sink.event(
                {
                    "type": "regenerate_record_id",
                    "regenerate_record_id": record.regenerate_record_id,
                }
            )
        sink.event({"type": "question", "question": record.question})
        sink.record_header(
            record_id=record.id,
            question=record.question,
            prefix=llm_service.trans("i18n_chat.record_id_in_mcp"),
        )
        if sink.mode == "json":
            json_result["record_id"] = record.id

        return {
            **state,
            "graph_key": "nlq",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "finish_step": finish_step,
            "return_img": return_img,
            "json_result": json_result,
        }
    except Exception as e:
        return {
            **_fail(state, record.id, e),
            "graph_key": "nlq",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "finish_step": finish_step,
            "return_img": return_img,
            "json_result": json_result,
        }


def ensure_datasource_node(state: NlqState) -> NlqState:
    """Select/validate datasource + connection. Does not run match_* (graph after)."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)

    with session_scope() as session:
        try:
            if not llm_service.ds:
                for chunk in select_datasource(llm_service, session):
                    sink.event(
                        {
                            "content": chunk.get("content"),
                            "reasoning_content": chunk.get("reasoning_content"),
                            "type": "datasource-result",
                        }
                    )
                sink.event(
                    {
                        "id": llm_service.ds.id,
                        "datasource_name": llm_service.ds.name,
                        "engine_type": getattr(llm_service.ds, "type", None),
                        "type": "datasource",
                    }
                )
            else:
                validate_history_ds(llm_service, session)

            connected = llm_service.protocol.check_connection(ds=llm_service.ds)
            if not connected:
                raise SQLBotDBConnectionError("Datasource connection failed")
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def match_terminology_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_terminology(llm_service, session, oid, ds_id)
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def match_training_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_training(llm_service, session, oid, ds_id)
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def match_custom_prompts_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_custom_prompts(
                llm_service, session, CustomPromptTypeEnum.GENERATE_SQL, oid, ds_id
            )
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def build_context_node(state: NlqState) -> NlqState:
    """Schema retrieval + SQL/chart prompt message assembly."""
    llm_service = state["llm_service"]
    with session_scope() as session:
        try:
            build_prompt_messages(llm_service, session)
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def generate_sql_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    with session_scope() as session:
        try:
            sql_res = generate_sql(llm_service, session)
            full_sql_text = ""
            for chunk in sql_res:
                full_sql_text += chunk.get("content") or ""
                sink.event(
                    {
                        "content": chunk.get("content"),
                        "reasoning_content": chunk.get("reasoning_content"),
                        "type": "sql-result",
                    }
                )
            sink.event({"type": "info", "msg": "sql generated"})
            SQLBotLogUtil.info(full_sql_text)

            plan: QueryPlan = llm_service.protocol.parse_llm_output(full_sql_text)
            if not plan.success:
                raise SingleMessageError(plan.message or "Failed to parse LLM output")

            plan = llm_service.protocol.validate_plan(
                llm_service.ds, plan, llm_service.table_name_list
            )
            if not plan.success:
                raise SingleMessageError(plan.message or "Query plan validation failed")

            chart_type = plan.chart_type

            if llm_service.change_title:
                llm_brief = plan.brief
                llm_brief_generated = bool(llm_brief)
                if llm_brief_generated or (
                    llm_service.chat_question.question
                    and llm_service.chat_question.question.strip() != ""
                ):
                    save_brief = (
                        llm_brief
                        if (llm_brief and llm_brief != "")
                        else llm_service.chat_question.question.strip()[:20]
                    )
                    brief = rename_chat(
                        session=session,
                        rename_object=RenameChat(
                            id=llm_service.get_record().chat_id,
                            brief=save_brief,
                            brief_generate=llm_brief_generated,
                        ),
                    )
                    sink.event({"type": "brief", "brief": brief})
                    if sink.mode == "json":
                        json_result["title"] = brief

            use_dynamic_ds: bool = bool(
                llm_service.current_assistant
                and llm_service.current_assistant.type in DYNAMIC_DS_TYPES
            )
            is_page_embedded: bool = bool(
                llm_service.current_assistant and llm_service.current_assistant.type == 4
            )
            dynamic_sql_result = None
            sqlbot_temp_sql_text = None
            assistant_dynamic_sql = None
            sql_operate = OperationEnum.GENERATE_QUERY
            sql = plan.payload.get("sql", plan.statement)

            if llm_service.protocol.supports(CAP_ROW_PERMISSION):
                if (
                    (not llm_service.current_assistant or is_page_embedded)
                    and is_normal_user(llm_service.current_user)
                ) or use_dynamic_ds:
                    sql_result = None

                    if use_dynamic_ds:
                        dynamic_sql_result = generate_assistant_dynamic_sql(
                            llm_service, session, sql, plan.resources
                        )
                        sqlbot_temp_sql_text = (
                            dynamic_sql_result.get("sqlbot_temp_sql_text")
                            if dynamic_sql_result
                            else None
                        )
                    else:
                        sql_result = generate_filter(llm_service, session, sql, plan.resources)

                    if sql_result:
                        SQLBotLogUtil.info(sql_result)
                        sql_operate = OperationEnum.GENERATE_QUERY_WITH_PERMISSIONS
                        sql = check_save_sql(
                            llm_service, session=session, res=sql_result, operate=sql_operate
                        )
                    elif dynamic_sql_result and sqlbot_temp_sql_text:
                        sql_operate = OperationEnum.GENERATE_DYNAMIC_QUERY
                        assistant_dynamic_sql = check_save_sql(
                            llm_service,
                            session=session,
                            res=sqlbot_temp_sql_text,
                            operate=sql_operate,
                        )
                    else:
                        sql = check_save_sql(
                            llm_service, session=session, res=full_sql_text, operate=sql_operate
                        )
                else:
                    sql = check_save_sql(
                        llm_service, session=session, res=full_sql_text, operate=sql_operate
                    )

                plan.payload["sql"] = sql

            SQLBotLogUtil.info("statement: " + plan.statement)

            format_statement = llm_service.protocol.format_statement_for_display(plan)
            llm_service.chat_question.sql = format_statement
            save_sql(session=session, sql=format_statement, record_id=llm_service.record.id)

            if sink.mode == "json":
                json_result["sql"] = format_statement

            sink.event(
                {
                    "content": format_statement,
                    "type": "sql",
                    "engine_type": getattr(llm_service.ds, "type", None),
                }
            )
            if sink.mode == "markdown":
                sink.text(f"```\n{format_statement}\n```\n\n")

            return {
                **state,
                "json_result": json_result,
                "plan": plan,
                "sql": sql,
                "format_statement": format_statement,
                "chart_type": chart_type,
                "full_sql_text": full_sql_text,
                "dynamic_sql_result": dynamic_sql_result,
                "sqlbot_temp_sql_text": sqlbot_temp_sql_text,
                "assistant_dynamic_sql": assistant_dynamic_sql,
                "record": llm_service.record,
            }
        except Exception as e:
            traceback.print_exc()
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {**state, "error": error_msg, "json_result": json_result}


def early_finish_node(state: NlqState) -> NlqState:
    """finish_step <= GENERATE_QUERY — emit finish / JSON, mark record done."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})

    sink.event({"type": "finish"})
    if sink.mode == "json":
        sink.json_result(json_result)

    with session_scope() as session:
        record_finish(session, llm_service.record.id)
    return {**state, "json_result": json_result}


def execute_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
    plan: QueryPlan = state["plan"]
    sql = state.get("sql")
    dynamic_sql_result = state.get("dynamic_sql_result")
    sqlbot_temp_sql_text = state.get("sqlbot_temp_sql_text")
    assistant_dynamic_sql = state.get("assistant_dynamic_sql")

    with session_scope() as session:
        try:
            real_execute_sql = sql
            if sqlbot_temp_sql_text and assistant_dynamic_sql:
                dynamic_sql_result = dict(dynamic_sql_result or {})
                dynamic_sql_result.pop("sqlbot_temp_sql_text", None)
                for origin_table, subsql in dynamic_sql_result.items():
                    assistant_dynamic_sql = assistant_dynamic_sql.replace(
                        f"{DYNAMIC_SUBSQL_PREFIX}{origin_table}",
                        subsql,
                    )
                real_execute_sql = assistant_dynamic_sql
                plan.payload["sql"] = real_execute_sql

            llm_service.current_logs[OperationEnum.EXECUTE_QUERY] = start_log(
                session=session,
                operate=OperationEnum.EXECUTE_QUERY,
                record_id=llm_service.record.id,
                local_operation=True,
            )
            qr = llm_service.protocol.execute(llm_service.ds, plan)
            result = qr.as_dict()
            if result.get("is_success") is False:
                code = result.get("code_value")
                msg = (
                    f"Query failed (code={code})" if code is not None else "Query failed"
                )
                raise SingleMessageError(msg)
            llm_service.current_logs[OperationEnum.EXECUTE_QUERY] = end_log(
                session=session,
                log=llm_service.current_logs[OperationEnum.EXECUTE_QUERY],
                full_message={
                    "statement": plan.statement,
                    "count": len(result.get("data")),
                },
            )

            _data = DataFormat.convert_large_numbers_in_object_array(result.get("data"))
            _data = DataFormat.normalize_qualified_sql_column_keys_in_object_array(_data)
            result["data"] = _data

            save_sql_data(llm_service, session=session, data_obj=result)
            re_exec_json = result.get("re_exec")
            if re_exec_json:
                save_re_exec(
                    session=session,
                    record_id=llm_service.record.id,
                    re_exec=orjson.dumps(re_exec_json).decode(),
                )
                sink.event({"content": re_exec_json, "type": "re_exec"})
            sink.event({"content": "execute-success", "type": "sql-data"})
            if sink.mode == "json":
                json_result["data"] = get_chat_chart_data(session, llm_service.record.id)

            return {
                **state,
                "json_result": json_result,
                "query_result": result,
                "plan": plan,
                "sql": real_execute_sql,
                "record": llm_service.record,
            }
        except Exception as e:
            traceback.print_exc()
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {**state, "error": error_msg, "json_result": json_result}


def data_finish_node(state: NlqState) -> NlqState:
    """finish_step <= QUERY_DATA — stop after execute (MCP markdown table)."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
    result = state.get("query_result") or {}
    _data = result.get("data")

    if sink.mode == "sse":
        sink.event({"type": "finish"})
    elif sink.mode == "markdown":
        _column_list = []
        for field in result.get("fields") or []:
            _column_list.append(AxisObj(name=field, value=field))

        md_data, _fields_list = DataFormat.convert_object_array_for_pandas(
            _column_list, result.get("data")
        )
        if not _data or not _fields_list:
            sink.text("The query returned no data.\n\n")
        else:
            df = pd.DataFrame(_data, columns=_fields_list)
            df_safe = DataFormat.safe_convert_to_string(df)
            sink.text(df_safe.to_markdown(index=False) + "\n\n")
    else:
        sink.json_result(json_result)

    with session_scope() as session:
        record_finish(session, llm_service.record.id)
    return {**state, "json_result": json_result}


def generate_chart_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
    plan: QueryPlan = state["plan"]
    result = state.get("query_result") or {}
    chart_type = state.get("chart_type")

    with session_scope() as session:
        try:
            # Bound-resource refetch only (plan.resources). Do not pass embedding= —
            # subset filters already skip ranking; settings own any residual gate.
            if llm_service.out_ds_instance:
                used_tables_schema, used_tables = llm_service.out_ds_instance.get_db_schema(
                    llm_service.ds.id,
                    llm_service.chat_question.question,
                    table_list=plan.resources,
                )
            else:
                chart_snapshot = llm_service.protocol.retrieve_schema(
                    session=session,
                    current_user=llm_service.current_user,
                    ds=llm_service.ds,
                    question=llm_service.chat_question.question,
                    resource_names=plan.resources or None,
                )
                used_tables_schema = chart_snapshot.schema_text
                used_tables = chart_snapshot.resource_names
            _ = used_tables

            _sample_md = DataFormat.rows_to_markdown_table(
                result.get("fields") or [],
                result.get("data") or [],
                max_rows=5,
                title="\n【Sample Data】(first 5 rows, for chart reference)",
            )
            if _sample_md:
                used_tables_schema = (used_tables_schema or "") + "\n" + _sample_md
            SQLBotLogUtil.info("used_tables_schema: \n" + used_tables_schema)

            chart_res = generate_chart(llm_service, session, chart_type, used_tables_schema)
            full_chart_text = ""
            for chunk in chart_res:
                full_chart_text += chunk.get("content") or ""
                sink.event(
                    {
                        "content": chunk.get("content"),
                        "reasoning_content": chunk.get("reasoning_content"),
                        "type": "chart-result",
                    }
                )
            sink.event({"type": "info", "msg": "chart generated"})

            SQLBotLogUtil.info(full_chart_text)
            chart = check_save_chart(
                llm_service,
                session=session,
                res=full_chart_text,
                fields=result.get("fields"),
            )
            SQLBotLogUtil.info(chart)

            if sink.mode == "json":
                json_result["chart"] = chart

            sink.event({"content": orjson.dumps(chart).decode(), "type": "chart"})
            if sink.mode == "markdown":
                md_data, _fields_list = DataFormat.convert_data_fields_for_pandas(
                    chart, result.get("fields"), result.get("data")
                )
                if not md_data or not _fields_list:
                    sink.text("The SQL execution result is empty.\n\n")
                else:
                    df = pd.DataFrame(md_data, columns=_fields_list)
                    df_safe = DataFormat.safe_convert_to_string(df)
                    sink.text(df_safe.to_markdown(index=False) + "\n\n")

            return {
                **state,
                "json_result": json_result,
                "chart": chart,
                "record": llm_service.record,
            }
        except Exception as e:
            traceback.print_exc()
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {**state, "error": error_msg, "json_result": json_result}


def complete_node(state: NlqState) -> NlqState:
    """After successful chart: finish SSE / optional MCP picture / JSON dump."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
    chart = state.get("chart") or {}
    result = state.get("query_result") or {}
    return_img = bool(state.get("return_img", True))

    if sink.mode == "sse":
        sink.event({"type": "finish"})
        with session_scope() as session:
            record_finish(session, llm_service.record.id)
        return {**state, "json_result": json_result, "record": llm_service.record}

    with session_scope() as session:
        try:
            if chart.get("type") != "table" and return_img:
                llm_service.current_logs[OperationEnum.GENERATE_PICTURE] = start_log(
                    session=session,
                    operate=OperationEnum.GENERATE_PICTURE,
                    record_id=llm_service.record.id,
                    local_operation=True,
                )
                image_url, error = request_picture(
                    llm_service.record.chat_id,
                    llm_service.record.id,
                    chart,
                    format_json_data(result),
                )
                SQLBotLogUtil.info(image_url)
                if sink.mode == "markdown":
                    sink.text(f'![{chart.get("type")}]({image_url})')
                else:
                    json_result["image_url"] = image_url
                if error is not None:
                    raise error

                llm_service.current_logs[OperationEnum.GENERATE_PICTURE] = end_log(
                    session=session,
                    log=llm_service.current_logs[OperationEnum.GENERATE_PICTURE],
                    full_message=image_url,
                )
        except Exception as e:
            if sink.mode == "markdown" and chart.get("type") != "table":
                sink.text("generate or fetch chart picture error.\n\n")
            error_msg = _error_message(e)
            try:
                record_save_error(session, llm_service.record.id, error_msg)
            except Exception:
                traceback.print_exc()
            return {**state, "json_result": json_result, "error": error_msg}

        record_finish(session, llm_service.record.id)

    if sink.mode == "json":
        sink.json_result(json_result)
    return {**state, "json_result": json_result, "record": llm_service.record}


def fail_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    error_msg = state.get("error") or "unknown error"
    sink.error(error_msg)
    try:
        with session_scope() as session:
            record_finish(session, llm_service.record.id)
    except Exception:
        traceback.print_exc()
    return state


def _ok_or_fail(next_name: str):
    def _route(state: NlqState) -> Literal:  # type: ignore[type-arg]
        return "fail" if state.get("error") else next_name

    return _route


def _route_after_sql(state: NlqState) -> Literal["early_finish", "execute", "fail"]:
    if state.get("error"):
        return "fail"
    finish_step = _as_finish_step(state.get("finish_step"))
    if finish_step.value <= ChatFinishStep.GENERATE_QUERY.value:
        return "early_finish"
    return "execute"


def _route_after_execute(state: NlqState) -> Literal["data_finish", "generate_chart", "fail"]:
    if state.get("error"):
        return "fail"
    finish_step = _as_finish_step(state.get("finish_step"))
    if finish_step.value <= ChatFinishStep.QUERY_DATA.value:
        return "data_finish"
    return "generate_chart"


def _route_after_chart(state: NlqState) -> Literal["complete", "fail"]:
    return "fail" if state.get("error") else "complete"


def _route_after_complete(state: NlqState) -> Literal["fail", "__end__"]:
    return "fail" if state.get("error") else "__end__"


def build_nlq_graph(_ctx: Any = None, **_kwargs: Any):
    g = StateGraph(NlqState)
    g.add_node("prepare_record", prepare_record_node)
    g.add_node("ensure_datasource", ensure_datasource_node)
    g.add_node("match_terminology", match_terminology_node)
    g.add_node("match_training", match_training_node)
    g.add_node("match_custom_prompts", match_custom_prompts_node)
    g.add_node("build_context", build_context_node)
    g.add_node("generate_sql", generate_sql_node)
    g.add_node("early_finish", early_finish_node)
    g.add_node("execute", execute_node)
    g.add_node("data_finish", data_finish_node)
    g.add_node("generate_chart", generate_chart_node)
    g.add_node("complete", complete_node)
    g.add_node("fail", fail_node)

    g.add_edge(START, "prepare_record")
    g.add_conditional_edges(
        "prepare_record",
        _ok_or_fail("ensure_datasource"),
        {"ensure_datasource": "ensure_datasource", "fail": "fail"},
    )
    g.add_conditional_edges(
        "ensure_datasource",
        _ok_or_fail("match_terminology"),
        {"match_terminology": "match_terminology", "fail": "fail"},
    )
    g.add_conditional_edges(
        "match_terminology",
        _ok_or_fail("match_training"),
        {"match_training": "match_training", "fail": "fail"},
    )
    g.add_conditional_edges(
        "match_training",
        _ok_or_fail("match_custom_prompts"),
        {"match_custom_prompts": "match_custom_prompts", "fail": "fail"},
    )
    g.add_conditional_edges(
        "match_custom_prompts",
        _ok_or_fail("build_context"),
        {"build_context": "build_context", "fail": "fail"},
    )
    g.add_conditional_edges(
        "build_context",
        _ok_or_fail("generate_sql"),
        {"generate_sql": "generate_sql", "fail": "fail"},
    )
    g.add_conditional_edges(
        "generate_sql",
        _route_after_sql,
        {"early_finish": "early_finish", "execute": "execute", "fail": "fail"},
    )
    g.add_edge("early_finish", END)
    g.add_conditional_edges(
        "execute",
        _route_after_execute,
        {"data_finish": "data_finish", "generate_chart": "generate_chart", "fail": "fail"},
    )
    g.add_edge("data_finish", END)
    g.add_conditional_edges(
        "generate_chart",
        _route_after_chart,
        {"complete": "complete", "fail": "fail"},
    )
    g.add_conditional_edges(
        "complete",
        _route_after_complete,
        {"fail": "fail", "__end__": END},
    )
    g.add_edge("fail", END)
    return g.compile()


register_graph("nlq", build_nlq_graph)
