"""SQL generation stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator

import orjson
from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import end_log, save_sql_answer, start_log
from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.stream import process_stream


def generate_sql(llm_service: Any, session: Session) -> Iterator[Dict[str, Any]]:
    """Append user prompt, stream SQL tokens, persist answer + log."""
    llm_service.sql_message.append(
        HumanMessage(
            llm_service.protocol.build_user_prompt(
                llm_service.chat_question,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                change_title=llm_service.change_title,
            )
        )
    )
    llm_service.current_logs[OperationEnum.GENERATE_QUERY] = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_QUERY,
        record_id=llm_service.record.id,
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in llm_service.sql_message
        ],
    )
    full_thinking_text = ""
    full_sql_text = ""
    token_usage: Dict[str, Any] = {}
    for chunk in process_stream(llm_service.llm.stream(llm_service.sql_message), token_usage):
        if chunk.get("content"):
            full_sql_text += chunk.get("content")
        if chunk.get("reasoning_content"):
            full_thinking_text += chunk.get("reasoning_content")
        yield chunk

    llm_service.sql_message.append(AIMessage(full_sql_text))
    llm_service.current_logs[OperationEnum.GENERATE_QUERY] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.GENERATE_QUERY],
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in llm_service.sql_message
        ],
        reasoning_content=full_thinking_text,
        token_usage=token_usage,
    )
    llm_service.record = save_sql_answer(
        session=session,
        record_id=llm_service.record.id,
        answer=orjson.dumps({"content": full_sql_text}).decode(),
    )
