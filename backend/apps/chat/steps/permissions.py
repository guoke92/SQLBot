"""Row-permission / assistant-dynamic SQL rewrite steps (domain atoms)."""

from __future__ import annotations

import json
import re
from typing import Any

import orjson
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum, SystemPromptMessage
from apps.chat.steps.observability import log_span
from apps.chat.steps.stream import process_stream
from apps.datasource.crud.permission import get_row_permission_filters
from apps.system.schemas.system_schema import AssistantOutDsSchema
from common.error import SingleMessageError
from common.utils.json_utils import extract_nested_json
from common.utils.utils import SQLBotLogUtil

# Prefix for assistant dynamic temp-table subqueries (sole definition).
DYNAMIC_SUBSQL_PREFIX = "select * from sqlbot_dynamic_temp_table_"


def generate_with_sub_sql(
    llm_service: Any,
    session: Session,  # noqa: ARG001 — 签名兼容(调用方协议统一)
    sql: str,
    sub_mappings: list,
) -> str:
    """Ask the model to fuse assistant sub-queries into a single executable SQL string."""
    sub_query = json.dumps(sub_mappings, ensure_ascii=False)
    llm_service.chat_question.sql = sql
    llm_service.chat_question.sub_query = sub_query
    dynamic_sql_msg: list[BaseMessage | dict[str, Any]] = [
        SystemPromptMessage(content=llm_service.chat_question.dynamic_sys_question()),
        HumanMessage(content=llm_service.chat_question.dynamic_user_question()),
    ]
    with log_span(
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_DYNAMIC_QUERY,
        record_id=llm_service.record.id,
        local_operation=False,
        graph_node="execute_queries",
        title_key="chat.log.GENERATE_DYNAMIC_QUERY",
    ) as span:
        full_thinking_text = ""
        full_dynamic_text = ""
        token_usage: dict[str, Any] = {}
        for chunk in process_stream(
            llm_service.llm.stream(dynamic_sql_msg), token_usage
        ):
            if chunk.get("content"):
                full_dynamic_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
        dynamic_sql_msg.append(AIMessage(full_dynamic_text))
        span.set_model_context(dynamic_sql_msg)
        span.set_usage(token_usage)
        span["reasoning_content"] = full_thinking_text
        span.set_summary("chat.audit.permission_query_ready")
    SQLBotLogUtil.info(full_dynamic_text)
    return full_dynamic_text


def generate_assistant_dynamic_sql(
    llm_service: Any, session: Session, sql: str, tables: list
) -> dict | None:
    """Collect assistant table SQL snippets and rewrite the main query when needed."""
    ds: AssistantOutDsSchema = llm_service.ds
    sub_query: list[dict[str, str]] = []
    result_dict: dict[str, str] = {}
    for table in ds.tables:
        if table.name in tables and table.sql:
            result_dict[table.name] = table.sql
            sub_query.append(
                {
                    "table": table.name,
                    "query": f"{DYNAMIC_SUBSQL_PREFIX}{table.name}",
                }
            )
    if not sub_query:
        return None
    temp_sql_text = generate_with_sub_sql(llm_service, session, sql, sub_query)
    result_dict["sqlbot_temp_sql_text"] = temp_sql_text
    return result_dict


def build_table_filter(
    llm_service: Any,
    session: Session,  # noqa: ARG001 — 签名兼容(调用方协议统一)
    sql: str,
    filters: list,
) -> str:
    """Stream a permission-rewritten SQL answer for the given filter list."""
    filter_json = json.dumps(filters, ensure_ascii=False)
    llm_service.chat_question.sql = sql
    llm_service.chat_question.filter = filter_json
    permission_sql_msg: list[BaseMessage | dict[str, Any]] = [
        SystemPromptMessage(content=llm_service.chat_question.filter_sys_question()),
        HumanMessage(content=llm_service.chat_question.filter_user_question()),
    ]
    with log_span(
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_QUERY_WITH_PERMISSIONS,
        record_id=llm_service.record.id,
        local_operation=False,
        graph_node="execute_queries",
        title_key="chat.log.GENERATE_QUERY_WITH_PERMISSIONS",
    ) as span:
        full_thinking_text = ""
        full_filter_text = ""
        token_usage: dict[str, Any] = {}
        for chunk in process_stream(
            llm_service.llm.stream(permission_sql_msg), token_usage
        ):
            if chunk.get("content"):
                full_filter_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
        permission_sql_msg.append(AIMessage(full_filter_text))
        span.set_model_context(permission_sql_msg)
        span.set_usage(token_usage)
        span["reasoning_content"] = full_thinking_text
        span.set_detail({"filter_count": len(filters)})
        span.set_summary("chat.audit.permission_query_ready")
    SQLBotLogUtil.info(full_filter_text)
    # 模板契约要求模型必须返回 {"success":true,"sql":"..."} JSON(旧
    # check_sql 语义,重构时丢失)。解析失败/嵌码围栏剥离/校验 success,
    # 拒绝把模型原文当 SQL 拼进执行计划。
    json_str = extract_nested_json(full_filter_text)
    if json_str is not None:
        try:
            data = orjson.loads(json_str)
        except Exception:
            data = None
        if (
            isinstance(data, dict)
            and data.get("success")
            and str(data.get("sql") or "").strip()
        ):
            return str(data["sql"]).strip()
        if isinstance(data, dict) and data.get("success") is False:
            raise SingleMessageError(str(data.get("message") or "行权限改写失败"))
    # 兼容模型无视模板直接返回裸 SQL 的历史形态:仅当文本看起来是
    # 单条 SQL(无花括号、以 SELECT/WITH 开头)才原样采用
    stripped = full_filter_text.strip().strip("`")
    if not stripped.startswith("{") and re.match(
        r"^(SELECT|WITH)\b", stripped, re.IGNORECASE
    ):
        return stripped
    raise SingleMessageError("行权限改写返回了无法解析的内容")


def generate_filter(
    llm_service: Any,
    session: Session,  # noqa: ARG001 — 签名兼容(调用方协议统一)
    sql: str,
    tables: list,
    *,
    resolved_filters: list[dict[str, Any]] | None = None,
) -> str | None:
    """Apply workspace row-permission filters when present."""
    filters = resolved_filters
    if filters is None:
        filters = get_row_permission_filters(
            session=session,
            current_user=llm_service.current_user,
            ds=llm_service.ds,
            tables=tables,
        )
    if not filters:
        return None
    return build_table_filter(llm_service, session, sql, filters)


def generate_assistant_filter(
    llm_service: Any, session: Session, sql: str, tables: list
) -> str | None:
    """Apply assistant-attached table rules when present."""
    ds: AssistantOutDsSchema = llm_service.ds
    filters = []
    for table in ds.tables:
        if table.name in tables and table.rule:
            filters.append({"table": table.name, "filter": table.rule})
    if not filters:
        return None
    return build_table_filter(llm_service, session, sql, filters)
