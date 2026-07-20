"""Chart generation stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, Optional

import orjson
from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import end_log, save_chart_answer, start_log
from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.stream import process_stream


def generate_chart(
    llm_service: Any,
    session: Session,
    chart_type: Optional[str] = "",
    schema: Optional[str] = "",
) -> Iterator[Dict[str, Any]]:
    """Append chart user prompt, stream tokens, persist answer + log."""
    user_prompt = llm_service.protocol.build_chart_user_prompt(
        llm_service.chat_question, chart_type, schema
    )
    llm_service.chart_message.append(HumanMessage(user_prompt))
    llm_service.current_logs[OperationEnum.GENERATE_CHART] = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_CHART,
        record_id=llm_service.record.id,
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in llm_service.chart_message
        ],
    )
    full_thinking_text = ""
    full_chart_text = ""
    token_usage: Dict[str, Any] = {}
    for chunk in process_stream(llm_service.llm.stream(llm_service.chart_message), token_usage):
        if chunk.get("content"):
            full_chart_text += chunk.get("content")
        if chunk.get("reasoning_content"):
            full_thinking_text += chunk.get("reasoning_content")
        yield chunk

    llm_service.chart_message.append(AIMessage(full_chart_text))
    llm_service.record = save_chart_answer(
        session=session,
        record_id=llm_service.record.id,
        answer=orjson.dumps({"content": full_chart_text}).decode(),
    )
    llm_service.current_logs[OperationEnum.GENERATE_CHART] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.GENERATE_CHART],
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in llm_service.chart_message
        ],
        reasoning_content=full_thinking_text,
        token_usage=token_usage,
    )
