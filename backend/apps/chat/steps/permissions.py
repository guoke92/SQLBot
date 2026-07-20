"""Row-permission / assistant-dynamic SQL rewrite steps (domain atoms)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import end_log, start_log
from apps.chat.models.chat_model import OperationEnum, SystemPromptMessage
from apps.chat.steps.stream import process_stream
from apps.datasource.crud.permission import get_row_permission_filters
from apps.system.schemas.system_schema import AssistantOutDsSchema
from common.utils.utils import SQLBotLogUtil

# Prefix for assistant dynamic temp-table subqueries (sole definition).
DYNAMIC_SUBSQL_PREFIX = "select * from sqlbot_dynamic_temp_table_"


def generate_with_sub_sql(
    llm_service: Any, session: Session, sql: str, sub_mappings: list
) -> str:
    """Ask the model to fuse assistant sub-queries into a single executable SQL string."""
    sub_query = json.dumps(sub_mappings, ensure_ascii=False)
    llm_service.chat_question.sql = sql
    llm_service.chat_question.sub_query = sub_query
    dynamic_sql_msg: List[Union[BaseMessage, dict[str, Any]]] = [
        SystemPromptMessage(content=llm_service.chat_question.dynamic_sys_question()),
        HumanMessage(content=llm_service.chat_question.dynamic_user_question()),
    ]
    llm_service.current_logs[OperationEnum.GENERATE_DYNAMIC_QUERY] = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_DYNAMIC_QUERY,
        record_id=llm_service.record.id,
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in dynamic_sql_msg
        ],
    )
    full_thinking_text = ""
    full_dynamic_text = ""
    token_usage: Dict[str, Any] = {}
    for chunk in process_stream(llm_service.llm.stream(dynamic_sql_msg), token_usage):
        if chunk.get("content"):
            full_dynamic_text += chunk.get("content")
        if chunk.get("reasoning_content"):
            full_thinking_text += chunk.get("reasoning_content")

    dynamic_sql_msg.append(AIMessage(full_dynamic_text))
    llm_service.current_logs[OperationEnum.GENERATE_DYNAMIC_QUERY] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.GENERATE_DYNAMIC_QUERY],
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in dynamic_sql_msg
        ],
        reasoning_content=full_thinking_text,
        token_usage=token_usage,
    )
    SQLBotLogUtil.info(full_dynamic_text)
    return full_dynamic_text


def generate_assistant_dynamic_sql(
    llm_service: Any, session: Session, sql: str, tables: List
) -> Optional[dict]:
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
    llm_service: Any, session: Session, sql: str, filters: list
) -> str:
    """Stream a permission-rewritten SQL answer for the given filter list."""
    filter_json = json.dumps(filters, ensure_ascii=False)
    llm_service.chat_question.sql = sql
    llm_service.chat_question.filter = filter_json
    permission_sql_msg: List[Union[BaseMessage, dict[str, Any]]] = [
        SystemPromptMessage(content=llm_service.chat_question.filter_sys_question()),
        HumanMessage(content=llm_service.chat_question.filter_user_question()),
    ]
    llm_service.current_logs[OperationEnum.GENERATE_QUERY_WITH_PERMISSIONS] = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_QUERY_WITH_PERMISSIONS,
        record_id=llm_service.record.id,
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in permission_sql_msg
        ],
    )
    full_thinking_text = ""
    full_filter_text = ""
    token_usage: Dict[str, Any] = {}
    for chunk in process_stream(llm_service.llm.stream(permission_sql_msg), token_usage):
        if chunk.get("content"):
            full_filter_text += chunk.get("content")
        if chunk.get("reasoning_content"):
            full_thinking_text += chunk.get("reasoning_content")

    permission_sql_msg.append(AIMessage(full_filter_text))
    llm_service.current_logs[OperationEnum.GENERATE_QUERY_WITH_PERMISSIONS] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.GENERATE_QUERY_WITH_PERMISSIONS],
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in permission_sql_msg
        ],
        reasoning_content=full_thinking_text,
        token_usage=token_usage,
    )
    SQLBotLogUtil.info(full_filter_text)
    return full_filter_text


def generate_filter(
    llm_service: Any, session: Session, sql: str, tables: List
) -> Optional[str]:
    """Apply workspace row-permission filters when present."""
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
    llm_service: Any, session: Session, sql: str, tables: List
) -> Optional[str]:
    """Apply assistant-attached table rules when present."""
    ds: AssistantOutDsSchema = llm_service.ds
    filters = []
    for table in ds.tables:
        if table.name in tables and table.rule:
            filters.append({"table": table.name, "filter": table.rule})
    if not filters:
        return None
    return build_table_filter(llm_service, session, sql, filters)
