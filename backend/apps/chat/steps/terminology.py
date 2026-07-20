"""Match terminology templates for the current question (domain step)."""

from __future__ import annotations

from typing import Any, Optional

from sqlmodel import Session

from apps.chat.curd.chat import end_log, start_log
from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.scope import match_scope
from apps.terminology.curd.terminology import get_terminology_template


def match_terminology(
    llm_service: Any,
    session: Session,
    oid: Optional[int] = None,
    ds_id: Optional[int] = None,
) -> list[Any]:
    """Fill ``chat_question.terminologies``; return raw term list for logging."""
    llm_service.current_logs[OperationEnum.FILTER_TERMS] = start_log(
        session=session,
        operate=OperationEnum.FILTER_TERMS,
        record_id=llm_service.record.id,
        local_operation=True,
    )
    calculate_oid, calculate_ds_id, assistant_id = match_scope(llm_service, oid, ds_id)
    if assistant_id is not None:
        llm_service.chat_question.terminologies, term_list = get_terminology_template(
            session,
            llm_service.chat_question.question,
            calculate_oid,
            None,
            assistant_id,
        )
    else:
        llm_service.chat_question.terminologies, term_list = get_terminology_template(
            session,
            llm_service.chat_question.question,
            calculate_oid,
            calculate_ds_id,
        )
    llm_service.current_logs[OperationEnum.FILTER_TERMS] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.FILTER_TERMS],
        full_message=term_list,
    )
    return term_list
