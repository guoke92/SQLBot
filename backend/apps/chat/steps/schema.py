"""Match / retrieve table schema for the current datasource (domain step).

Table vector recall is not a request-level flag and not stored on ``LLMService``.
Callers must not pass ``embedding=`` here. Protocol defaults ``embedding=True``;
``get_table_schema`` ranks tables only when ``settings.TABLE_EMBEDDING_ENABLED``.
Assistant out-DS schema paths do not run table embedding (name filter only).
"""

from __future__ import annotations

from typing import Any, List, Sequence

from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span
from apps.datasource.access import AccessScope


def match_table_schema(
    llm_service: Any,
    session: Session,
    *,
    required_resource_names: Sequence[str] = (),
    access_scope: AccessScope | None = None,
) -> List[Any]:
    """Retrieve schema via protocol; set ``db_schema`` / ``sample_data`` on question.

    Does not pass ``embedding`` — protocol default + ``TABLE_EMBEDDING_ENABLED``
    own ranking. Returns resource (table) names chosen for the prompt.
    """
    with log_span(
        operate=OperationEnum.CHOOSE_TABLE,
        record_id=llm_service.record.id,
        local_operation=True,
        phase="prepare",
        graph_node="retrieve_context",
        title_key="chat.log.CHOOSE_TABLE",
    ) as span:
        snapshot = llm_service.protocol.retrieve_schema(
            session=session,
            current_user=llm_service.current_user,
            ds=llm_service.ds,
            question=llm_service.retrieval_question,
            out_ds_instance=llm_service.out_ds_instance,
            required_resource_names=required_resource_names,
            access_scope=access_scope,
        )
        llm_service.chat_question.db_schema = snapshot.schema_text
        tables = snapshot.resource_names
        llm_service.chat_question.sample_data = snapshot.sample_data
        span.set_detail(
            {
                "resource_count": len(tables),
                "resources": list(tables),
                "schema": snapshot.schema_text,
                "access_scope_applied": access_scope is not None,
            }
        )
        span.set_summary("chat.audit.schema_ready", count=len(tables))
    return tables
