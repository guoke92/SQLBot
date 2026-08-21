"""Analysis follow-up stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Union

import orjson
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum
from sqlmodel import Session

from apps.chat.curd.chat import get_chat_chart_data, save_analysis_answer
from apps.chat.models.chat_model import OperationEnum, SystemPromptMessage
from apps.chat.steps.chart_fields import get_fields_from_chart
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.knowledge import match_knowledge
from apps.chat.steps.observability import log_span
from apps.chat.steps.stream import process_stream
from apps.datasource.models.datasource import CoreDatasource


def generate_analysis(llm_service: Any, session: Session) -> Iterator[Dict[str, Any]]:
    """Stream analysis tokens; persist answer + op log on completion."""
    fields = get_fields_from_chart(llm_service, session)
    llm_service.chat_question.fields = orjson.dumps(fields).decode()
    data = get_chat_chart_data(session, llm_service.record.id)
    llm_service.chat_question.data = orjson.dumps(data.get("data")).decode()

    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    match_knowledge(llm_service, session, llm_service.oid, ds_id)
    match_custom_prompts(
        llm_service, session, CustomPromptTypeEnum.ANALYSIS, llm_service.oid, ds_id
    )

    analysis_msg: List[Union[BaseMessage, dict[str, Any]]] = [
        SystemPromptMessage(content=llm_service.chat_question.analysis_sys_question()),
        HumanMessage(content=llm_service.chat_question.analysis_user_question()),
    ]

    with log_span(
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.ANALYSIS,
        record_id=llm_service.record.id,
        local_operation=False,
        graph_node="stream",
        title_key="chat.log.ANALYSIS",
    ) as span:
        full_thinking_text = ""
        full_analysis_text = ""
        token_usage: Dict[str, Any] = {}
        for chunk in process_stream(llm_service.llm.stream(analysis_msg), token_usage):
            if chunk.get("content"):
                full_analysis_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
            yield chunk
        analysis_msg.append(AIMessage(full_analysis_text))
        span.set_model_context(analysis_msg)
        span.set_usage(token_usage)
        span["reasoning_content"] = full_thinking_text
        span.set_detail({"chars": len(full_analysis_text)})
        span.set_summary("chat.audit.response_ready")
    llm_service.record = save_analysis_answer(
        session=session,
        record_id=llm_service.record.id,
        answer=orjson.dumps({"content": full_analysis_text}).decode(),
    )
