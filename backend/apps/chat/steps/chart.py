"""Chart generation stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, Optional

import orjson
from langchain_core.messages import AIMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import save_chart_answer
from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span
from apps.chat.steps.stream import process_stream


def generate_chart(
    llm_service: Any,
    session: Session,
    chart_type: Optional[str] = "",
    schema: Optional[str] = "",
    *,
    step_index: Optional[int] = None,
    unit_index: Optional[int] = None,
    graph_node: str = "generate_charts",
) -> Iterator[Dict[str, Any]]:
    """Append chart user prompt, stream tokens, persist answer + log."""
    user_prompt = llm_service.protocol.build_chart_user_prompt(
        llm_service.chat_question, chart_type, schema
    )
    llm_service.chart_message.append(HumanMessage(user_prompt))
    with log_span(
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_CHART,
        record_id=llm_service.record.id,
        local_operation=False,
        graph_node=graph_node,
        step_index=step_index,
        unit_index=unit_index,
        brief=str(chart_type or ""),
        title_key="chat.log.GENERATE_CHART",
    ) as span:
        full_thinking_text = ""
        full_chart_text = ""
        token_usage: Dict[str, Any] = {}
        for chunk in process_stream(
            llm_service.llm.stream(llm_service.chart_message), token_usage
        ):
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
        span.set_model_context(llm_service.chart_message)
        span.set_usage(token_usage)
        span["reasoning_content"] = full_thinking_text
        span.set_detail({"chart_type": chart_type or "", "chars": len(full_chart_text)})
        span.set_summary("chat.audit.chart_ready")
