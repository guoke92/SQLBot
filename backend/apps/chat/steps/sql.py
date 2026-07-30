"""SQL generation stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Any

import orjson
from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import inject_span_meta
from apps.chat.steps.stream import process_stream
from apps.conversation.observability import end_log, start_log, trigger_log_error
from apps.conversation.record import persist_snapshot


def generate_sql(
    llm_service: Any,
    session: Session,
    *,
    step_index: int | None = None,
    gen_attempts: int | None = None,
    graph_node: str = "generate_queries",
) -> Iterator[dict[str, Any]]:
    """Stream one SQL attempt from an immutable base-message snapshot.

    Holds ChatLog on a local handle (not only ``current_logs[enum]``) so
    agentic multi-attempt generates do not clobber identity.
    """
    attempt_messages = [
        *llm_service.sql_message,
        HumanMessage(
            llm_service.protocol.build_user_prompt(
                llm_service.chat_question,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                change_title=llm_service.change_title,
            )
        ),
    ]
    full_message = [
        {
            "type": msg.type,
            "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
            "content": msg.content,
        }
        for msg in attempt_messages
    ]
    full_message = inject_span_meta(
        full_message,
        graph_node=graph_node,
        step_index=step_index,
        gen_attempts=gen_attempts,
    )
    log = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_QUERY,
        record_id=llm_service.record.id,
        full_message=full_message,
    )
    # Keep last-handle for legacy check_sql paths that still key by enum.
    llm_service.current_logs[OperationEnum.GENERATE_QUERY] = log

    full_thinking_text = ""
    full_sql_text = ""
    token_usage: dict[str, Any] = {}
    completed = False
    try:
        for chunk in process_stream(
            llm_service.llm.stream(attempt_messages), token_usage
        ):
            if chunk.get("content"):
                full_sql_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
            yield chunk
        completed = True
    finally:
        messages_for_log = [*attempt_messages, AIMessage(full_sql_text)]
        end_msgs = [
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in messages_for_log
        ]
        end_msgs = inject_span_meta(
            end_msgs,
            graph_node=graph_node,
            step_index=step_index,
            gen_attempts=gen_attempts,
        )
        if not completed:
            trigger_log_error(session, log)
        llm_service.current_logs[OperationEnum.GENERATE_QUERY] = end_log(
            session=session,
            log=log,
            full_message=end_msgs,
            reasoning_content=full_thinking_text,
            token_usage=token_usage,
        )
        if completed:
            persist_snapshot(
                session=session,
                record_id=llm_service.record.id,
                sql_answer=orjson.dumps({"content": full_sql_text}).decode(),
            )
