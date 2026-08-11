"""Match data-training via Knowledge Compile Exemplify (single channel)."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.scope import match_scope
from apps.conversation.observability import end_log, start_log
from apps.data_training.curd.data_training import to_xml_string
from apps.knowledge.compile import compile_knowledge_for_turn
from apps.knowledge.policy import get_knowledge_policy
from apps.template.generate_chart.generator import get_base_data_training_template


def match_training(
    llm_service: Any,
    session: Session,
    oid: int | None = None,
    ds_id: int | None = None,
) -> list[Any]:
    """Fill ``chat_question.data_training`` through Compile only (no fallback)."""
    llm_service.current_logs[OperationEnum.FILTER_QUERY_EXAMPLE] = start_log(
        session=session,
        operate=OperationEnum.FILTER_QUERY_EXAMPLE,
        record_id=llm_service.record.id,
        local_operation=True,
    )
    calculate_oid, calculate_ds_id, assistant_id = match_scope(llm_service, oid, ds_id)
    training_type = getattr(llm_service.protocol, "training_type", "sql")
    policy = get_knowledge_policy()

    compiled = compile_knowledge_for_turn(
        session,
        stage="generate",
        question=llm_service.retrieval_question,
        oid=int(calculate_oid or 1),
        ds_id=calculate_ds_id if assistant_id is None else None,
        advanced_application_id=assistant_id,
        include_matches=False,
        include_calibers=False,
        include_examples=True,
        training_type=training_type,
        policy=policy,
    )
    example_list = list(compiled.examples or [])
    rows = [
        {
            "id": ex.get("id"),
            "question": ex.get("question"),
            "description": ex.get("sql"),
        }
        for ex in example_list
    ]
    if rows:
        data_training = to_xml_string(rows)
        llm_service.chat_question.data_training = (
            get_base_data_training_template().format(data_training=data_training)
        )
    else:
        llm_service.chat_question.data_training = ""

    prior = getattr(llm_service, "compiled_knowledge", None)
    if prior is not None and hasattr(prior, "apply_log"):
        llm_service.compiled_knowledge = prior.model_copy(
            update={
                "examples": compiled.examples,
                "reuse": compiled.reuse,
                "apply_log": list(prior.apply_log) + list(compiled.apply_log),
            }
        )
    else:
        llm_service.compiled_knowledge = compiled

    llm_service.current_logs[OperationEnum.FILTER_QUERY_EXAMPLE] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.FILTER_QUERY_EXAMPLE],
        full_message=rows,
    )
    return rows
