"""Predict follow-up stream + parse helpers (domain atoms; graph owns SSE)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Union

import orjson
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum
from sqlmodel import Session

from apps.chat.curd.chat import (
    end_log,
    get_chat_chart_data,
    save_predict_answer,
    save_predict_data,
    start_log,
)
from apps.chat.models.chat_model import OperationEnum, SystemPromptMessage
from apps.chat.steps.chart_fields import get_fields_from_chart
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.stream import process_stream
from apps.datasource.models.datasource import CoreDatasource
from common.utils.utils import extract_nested_json


def generate_predict(llm_service: Any, session: Session) -> Iterator[Dict[str, Any]]:
    """Stream predict tokens; persist answer + op log on completion."""
    fields = get_fields_from_chart(llm_service, session)
    llm_service.chat_question.fields = orjson.dumps(fields).decode()
    data = get_chat_chart_data(session, llm_service.record.id)
    llm_service.chat_question.data = orjson.dumps(data.get("data")).decode()

    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    match_custom_prompts(
        llm_service, session, CustomPromptTypeEnum.PREDICT_DATA, llm_service.oid, ds_id
    )

    predict_msg: List[Union[BaseMessage, dict[str, Any]]] = [
        SystemPromptMessage(content=llm_service.chat_question.predict_sys_question()),
        HumanMessage(content=llm_service.chat_question.predict_user_question()),
    ]

    llm_service.current_logs[OperationEnum.PREDICT_DATA] = start_log(
        session=session,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        operate=OperationEnum.PREDICT_DATA,
        record_id=llm_service.record.id,
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in predict_msg
        ],
    )

    full_thinking_text = ""
    full_predict_text = ""
    token_usage: Dict[str, Any] = {}
    for chunk in process_stream(llm_service.llm.stream(predict_msg), token_usage):
        if chunk.get("content"):
            full_predict_text += chunk.get("content")
        if chunk.get("reasoning_content"):
            full_thinking_text += chunk.get("reasoning_content")
        yield chunk

    predict_msg.append(AIMessage(full_predict_text))
    llm_service.record = save_predict_answer(
        session=session,
        record_id=llm_service.record.id,
        answer=orjson.dumps({"content": full_predict_text}).decode(),
    )
    llm_service.current_logs[OperationEnum.PREDICT_DATA] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.PREDICT_DATA],
        full_message=[
            {
                "type": msg.type,
                "sqlbot_system": getattr(msg, "sqlbot_system", False) is True,
                "content": msg.content,
            }
            for msg in predict_msg
        ],
        reasoning_content=full_thinking_text,
        token_usage=token_usage,
    )


def check_save_predict_data(llm_service: Any, session: Session, res: str) -> bool:
    """Parse nested JSON body from predict answer and persist expect/actual rows."""
    json_str = extract_nested_json(res) or ""
    save_predict_data(session=session, record_id=llm_service.record.id, data=json_str)
    return json_str != ""
