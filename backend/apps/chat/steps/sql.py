"""SQL generation stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator, Optional

import orjson
from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import end_log, save_sql_answer, start_log
from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import inject_span_meta
from apps.chat.steps.stream import process_stream


def generate_sql(
    llm_service: Any,
    session: Session,
    *,
    step_index: Optional[int] = None,
    gen_attempts: Optional[int] = None,
    graph_node: str = "generate_queries",
) -> Iterator[Dict[str, Any]]:
    """Append user prompt, stream SQL tokens, persist answer + log.

    Holds ChatLog on a local handle (not only ``current_logs[enum]``) so
    agentic multi-attempt generates do not clobber identity.
    """
    llm_service.sql_message.append(
        HumanMessage(
            llm_service.protocol.build_user_prompt(
                llm_service.chat_question,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                change_title=llm_service.change_title,
            )
        )
    )
    full_message = [
        {
            "type": msg.type,
            "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
            "content": msg.content,
        }
        for msg in llm_service.sql_message
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
    token_usage: Dict[str, Any] = {}
    try:
        for chunk in process_stream(llm_service.llm.stream(llm_service.sql_message), token_usage):
            if chunk.get("content"):
                full_sql_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
            yield chunk
    finally:
        llm_service.sql_message.append(AIMessage(full_sql_text))
        end_msgs = [
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in llm_service.sql_message
        ]
        end_msgs = inject_span_meta(
            end_msgs,
            graph_node=graph_node,
            step_index=step_index,
            gen_attempts=gen_attempts,
        )
        llm_service.current_logs[OperationEnum.GENERATE_QUERY] = end_log(
            session=session,
            log=log,
            full_message=end_msgs,
            reasoning_content=full_thinking_text,
            token_usage=token_usage,
        )
        llm_service.record = save_sql_answer(
            session=session,
            record_id=llm_service.record.id,
            answer=orjson.dumps({"content": full_sql_text}).decode(),
        )
