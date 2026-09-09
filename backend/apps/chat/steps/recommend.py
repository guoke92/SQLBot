"""Recommend-questions stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Union

import orjson
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import get_old_questions, save_recommend_question_answer
from apps.chat.models.chat_model import OperationEnum, SystemPromptMessage
from apps.chat.steps.observability import log_span
from apps.chat.steps.stream import process_stream


def _recalled_schema_text(llm_service: Any) -> str:
    """Reuse the turn's knowledge-plane schema. Never dump the full catalog."""
    existing = str(getattr(llm_service.chat_question, "db_schema", "") or "").strip()
    if existing:
        return existing
    record = getattr(llm_service, "record", None)
    run_id = str(getattr(record, "active_run_id", "") or "")
    if not run_id:
        return ""
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.conversation.runtime_context import peek_runtime

    snap = peek_runtime(run_id) or {}
    plane = AgentKnowledgePlane.from_dump(snap.get("knowledge_plane"))
    return "\n".join(
        plane.schema_by_table[name]
        for name in plane.tables
        if plane.schema_by_table.get(name)
    ).strip()


def generate_recommend_questions(
    llm_service: Any, session: Session
) -> Iterator[Dict[str, Any]]:
    """Stream recommended-question tokens; yield final list under key recommended_question."""
    recalled = _recalled_schema_text(llm_service)
    if recalled:
        llm_service.chat_question.db_schema = recalled

    guess_msg: List[Union[BaseMessage, dict[str, Any]]] = [
        SystemPromptMessage(
            content=llm_service.chat_question.guess_sys_question(llm_service.articles_number)
        )
    ]
    old_questions = list(
        map(lambda q: q.strip(), get_old_questions(session, llm_service.record.datasource))
    )
    guess_msg.append(
        HumanMessage(
            content=llm_service.chat_question.guess_user_question(
                orjson.dumps(old_questions).decode()
            )
        )
    )

    with log_span(
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_RECOMMENDED_QUESTIONS,
        record_id=llm_service.record.id,
        local_operation=False,
        graph_node="generate",
        title_key="chat.log.GENERATE_RECOMMENDED_QUESTIONS",
    ) as span:
        full_thinking_text = ""
        full_guess_text = ""
        token_usage: Dict[str, Any] = {}
        for chunk in process_stream(llm_service.llm.stream(guess_msg), token_usage):
            if chunk.get("content"):
                full_guess_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
            yield chunk
        guess_msg.append(AIMessage(full_guess_text))
        span.set_model_context(guess_msg)
        span.set_usage(token_usage)
        span["reasoning_content"] = full_thinking_text
        span.set_summary("chat.audit.response_ready")
    llm_service.record = save_recommend_question_answer(
        session=session,
        record_id=llm_service.record.id,
        answer={"content": full_guess_text},
        articles_number=llm_service.articles_number,
    )
    yield {"recommended_question": llm_service.record.recommended_question}
