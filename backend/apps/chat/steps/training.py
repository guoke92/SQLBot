"""Match data-training / query-example templates (domain step)."""

from __future__ import annotations

from typing import Any, Optional

from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.scope import match_scope
from apps.conversation.observability import end_log, start_log
from apps.data_training.curd.data_training import get_training_template


def match_training(
    llm_service: Any,
    session: Session,
    oid: Optional[int] = None,
    ds_id: Optional[int] = None,
) -> list[Any]:
    """Fill ``chat_question.data_training``; return example list for logging."""
    llm_service.current_logs[OperationEnum.FILTER_QUERY_EXAMPLE] = start_log(
        session=session,
        operate=OperationEnum.FILTER_QUERY_EXAMPLE,
        record_id=llm_service.record.id,
        local_operation=True,
    )
    calculate_oid, calculate_ds_id, assistant_id = match_scope(llm_service, oid, ds_id)
    training_type = getattr(llm_service.protocol, "training_type", "sql")
    if assistant_id is not None:
        llm_service.chat_question.data_training, example_list = get_training_template(
            session,
            llm_service.retrieval_question,
            calculate_oid,
            None,
            assistant_id,
            training_type=training_type,
        )
    else:
        llm_service.chat_question.data_training, example_list = get_training_template(
            session,
            llm_service.retrieval_question,
            calculate_oid,
            calculate_ds_id,
            training_type=training_type,
        )
    llm_service.current_logs[OperationEnum.FILTER_QUERY_EXAMPLE] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.FILTER_QUERY_EXAMPLE],
        full_message=example_list,
    )
    return example_list
