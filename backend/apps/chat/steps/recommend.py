"""Recommend-questions stream step (domain atom; graph owns SSE)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Union

import orjson
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlmodel import Session

from apps.chat.curd.chat import end_log, get_old_questions, save_recommend_question_answer, start_log
from apps.chat.models.chat_model import OperationEnum, SystemPromptMessage
from apps.chat.steps.stream import process_stream


def generate_recommend_questions(
    llm_service: Any, session: Session
) -> Iterator[Dict[str, Any]]:
    """Stream recommended-question tokens; yield final list under key recommended_question."""
    if llm_service.ds and not llm_service.chat_question.db_schema:
        snapshot = llm_service.protocol.retrieve_schema(
            session=session,
            current_user=llm_service.current_user,
            ds=llm_service.ds,
            question=llm_service.chat_question.question,
            out_ds_instance=llm_service.out_ds_instance,
        )
        llm_service.chat_question.db_schema = snapshot.schema_text

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

    llm_service.current_logs[OperationEnum.GENERATE_RECOMMENDED_QUESTIONS] = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.GENERATE_RECOMMENDED_QUESTIONS,
        record_id=llm_service.record.id,
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in guess_msg
        ],
    )

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
    llm_service.current_logs[OperationEnum.GENERATE_RECOMMENDED_QUESTIONS] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.GENERATE_RECOMMENDED_QUESTIONS],
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in guess_msg
        ],
        reasoning_content=full_thinking_text,
        token_usage=token_usage,
    )
    llm_service.record = save_recommend_question_answer(
        session=session,
        record_id=llm_service.record.id,
        answer={"content": full_guess_text},
        articles_number=llm_service.articles_number,
    )
    yield {"recommended_question": llm_service.record.recommended_question}
