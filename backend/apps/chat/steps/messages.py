"""Retrieve schema and assemble chart messages as separate domain steps."""

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
from apps.chat.steps.history import (
    get_last_conversation_rounds,
    select_prompt_history,
)
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


def assemble_chart_messages(llm_service: Any) -> None:
    """Assemble chart history after the query specification is confirmed."""
    last_chart_messages = select_prompt_history(
        llm_service.generate_chart_logs,
        record_id=getattr(llm_service.record, "id", None),
    )

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
    if last_chart_messages:
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
