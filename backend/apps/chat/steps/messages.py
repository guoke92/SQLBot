"""Retrieve schema and assemble SQL/chart messages as separate domain steps."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from apps.chat.models.chat_model import (
    AIPromptMessage,
    HumanPromptMessage,
    SystemPromptMessage,
)
from apps.chat.steps.history import get_last_conversation_rounds
from apps.chat.steps.schema import match_table_schema
from apps.datasource.access import AccessScope


def retrieve_prompt_schema(
    llm_service: Any,
    session: Session,
    *,
    required_resource_names: Sequence[str] = (),
    access_scope: AccessScope | None = None,
) -> list[Any]:
    """Retrieve the permission-scoped schema needed by intent and SQL planning."""
    llm_service.table_name_list = match_table_schema(
        llm_service,
        session,
        required_resource_names=required_resource_names,
        access_scope=access_scope,
    )
    return llm_service.table_name_list


def assemble_prompt_messages(llm_service: Any) -> None:
    """Assemble SQL/chart messages after semantic intent is confirmed."""

    last_sql_messages: list[dict[str, Any]] = (
        llm_service.generate_sql_logs[-1].messages
        if len(llm_service.generate_sql_logs) > 0
        else []
    )
    if llm_service.chat_question.regenerate_record_id:
        _temp_log = next(
            filter(
                lambda obj: obj.pid == llm_service.chat_question.regenerate_record_id,
                llm_service.generate_sql_logs,
            ),
            None,
        )
        last_sql_messages = _temp_log.messages if _temp_log else []

    last_sql_messages = [
        obj for obj in last_sql_messages if obj.get("sqlbot_system") is not True
    ]

    count_limit = llm_service.base_message_round_count_limit

    llm_service.sql_message = []
    llm_service.chat_question._ds_type = llm_service.ds.type
    _system_templates = llm_service.protocol.build_prompt_bundle(
        llm_service.chat_question, enable_query_limit=llm_service.enable_sql_row_limit
    ).as_dict()
    llm_service.sql_message.append(
        SystemPromptMessage(content=_system_templates["system"])
    )
    llm_service.sql_message.append(
        HumanPromptMessage(content=_system_templates["rules"])
    )
    llm_service.sql_message.append(
        AIPromptMessage(content=_system_templates["ack_rules"])
    )
    llm_service.sql_message.append(
        HumanPromptMessage(content=_system_templates["schema"])
    )
    llm_service.sql_message.append(
        AIPromptMessage(content=_system_templates["ack_schema"])
    )
    if _system_templates.get("custom_prompt"):
        llm_service.sql_message.append(
            HumanPromptMessage(content=_system_templates["custom_prompt"])
        )
        llm_service.sql_message.append(
            AIPromptMessage(content=_system_templates["ack_custom_prompt"])
        )
    if _system_templates.get("terminologies"):
        llm_service.sql_message.append(
            HumanPromptMessage(content=_system_templates["terminologies"])
        )
        llm_service.sql_message.append(
            AIPromptMessage(content=_system_templates["ack_terminologies"])
        )
    if _system_templates.get("data_training"):
        llm_service.sql_message.append(
            HumanPromptMessage(content=_system_templates["data_training"])
        )
        llm_service.sql_message.append(
            AIPromptMessage(content=_system_templates["ack_data_training"])
        )

    if last_sql_messages is not None and len(last_sql_messages) > 0:
        last_rounds = get_last_conversation_rounds(
            last_sql_messages, rounds=count_limit
        )
        for _msg_dict in last_rounds:
            if _msg_dict.get("type") == "human":
                llm_service.sql_message.append(
                    HumanMessage(content=_msg_dict.get("content"))
                )
            elif _msg_dict.get("type") == "ai":
                llm_service.sql_message.append(
                    AIMessage(content=_msg_dict.get("content"))
                )

    last_chart_messages: list[dict[str, Any]] = (
        llm_service.generate_chart_logs[-1].messages
        if len(llm_service.generate_chart_logs) > 0
        else []
    )
    if llm_service.chat_question.regenerate_record_id:
        _temp_log = next(
            filter(
                lambda obj: obj.pid == llm_service.chat_question.regenerate_record_id,
                llm_service.generate_chart_logs,
            ),
            None,
        )
        last_chart_messages = _temp_log.messages if _temp_log else []

    last_chart_messages = [
        obj for obj in last_chart_messages if obj.get("sqlbot_system") is not True
    ]

    count_chart_limit = llm_service.base_message_round_count_limit

    llm_service.chart_message = []
    _chart_bundle = llm_service.protocol.build_chart_system_prompt(
        llm_service.chat_question
    )
    llm_service.chart_message.append(
        SystemPromptMessage(content=_chart_bundle["system"])
    )
    llm_service.chart_message.append(HumanPromptMessage(content=_chart_bundle["rules"]))
    llm_service.chart_message.append(AIPromptMessage(content=_chart_bundle["ack"]))
    if last_chart_messages is not None and len(last_chart_messages) > 0:
        last_rounds = get_last_conversation_rounds(
            last_chart_messages, rounds=count_chart_limit
        )
        for _msg_dict in last_rounds:
            if _msg_dict.get("type") == "human":
                llm_service.chart_message.append(
                    HumanMessage(content=_msg_dict.get("content"))
                )
            elif _msg_dict.get("type") == "ai":
                llm_service.chart_message.append(
                    AIMessage(content=_msg_dict.get("content"))
                )
