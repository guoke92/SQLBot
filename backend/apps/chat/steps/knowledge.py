"""Unified terminology and dictionary recall step."""

from __future__ import annotations

from typing import Any, Optional

from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.scope import match_scope
from apps.conversation.observability import end_log, start_log
from apps.datasource.access import AccessScope
from apps.knowledge.models import KnowledgeMatch
from apps.knowledge.scope import scope_knowledge_matches
from apps.knowledge.service import recall_knowledge


def _scope_dictionary_matches(
    access_scope: AccessScope | None,
    matches: list[KnowledgeMatch],
) -> list[KnowledgeMatch]:
    """Apply the same local table/column/row permission scope as schema recall."""
    if access_scope is None:
        return [
            match
            for match in matches
            if "entity_binding" not in match.usages
        ]

    return scope_knowledge_matches(
        matches,
        allowed_targets=access_scope.allowed_targets,
        row_restricted_tables=access_scope.row_restricted_tables,
    )


def match_knowledge(
    llm_service: Any,
    session: Session,
    oid: Optional[int] = None,
    ds_id: Optional[int] = None,
    access_scope: AccessScope | None = None,
) -> list[KnowledgeMatch]:
    llm_service.current_logs[OperationEnum.FILTER_TERMS] = start_log(
        session=session,
        operate=OperationEnum.FILTER_TERMS,
        record_id=llm_service.record.id,
        local_operation=True,
    )
    calculate_oid, calculate_ds_id, assistant_id = match_scope(llm_service, oid, ds_id)
    bundle = recall_knowledge(
        session,
        question=llm_service.retrieval_question,
        oid=int(calculate_oid or 1),
        ds_id=calculate_ds_id if assistant_id is None else None,
        advanced_application_id=assistant_id,
    )
    matches = bundle.matches
    matches = _scope_dictionary_matches(access_scope, matches)
    llm_service.chat_question.terminologies = bundle.prompt_template
    dictionary_items = [
        {
            "words": [match.canonical, *match.alternatives],
            "description": (
                f"{match.description} "
                f"({', '.join(f'{target.table_name}.{target.field_name}' for target in match.targets)})"
            ).strip(),
        }
        for match in matches
        if "entity_binding" in match.usages
    ]
    llm_service.current_logs[OperationEnum.FILTER_TERMS] = end_log(
        session=session,
        log=llm_service.current_logs[OperationEnum.FILTER_TERMS],
        full_message=[*bundle.log_items, *dictionary_items],
    )
    return matches
