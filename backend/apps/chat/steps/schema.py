"""Match / retrieve table schema for the current datasource (domain step).

Table vector recall is not a request-level flag and not stored on ``LLMService``.
Callers must not pass ``embedding=`` here. Protocol defaults ``embedding=True``;
``get_table_schema`` ranks tables only when ``settings.TABLE_EMBEDDING_ENABLED``.
Assistant out-DS schema paths do not run table embedding (name filter only).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span
from apps.datasource.access import AccessScope


def match_table_schema(
    llm_service: Any,
    session: Session,
    *,
    resource_names: Sequence[str] | None = None,
    required_resource_names: Sequence[str] = (),
    access_scope: AccessScope | None = None,
    graph_node: str = "retrieve_context",
    brief: str = "",
    audit: bool = True,
    table_limit: int | None = None,
) -> list[Any]:
    """Retrieve schema via protocol; set ``db_schema`` / ``sample_data`` on question.

    ``resource_names`` is an exact projection (binding or prior plan).
    Does not pass ``embedding`` — protocol default + ``TABLE_EMBEDDING_ENABLED``
    own ranking. Returns resource (table) names chosen for the prompt.
    ``table_limit`` caps the ranked working set (required tables always kept) —
    wiki-led selection passes closure count + supplement budget.
    Execution-time refresh keeps the same retrieve but must not emit another
    user-visible ``CHOOSE_TABLE`` span.
    """

    def _retrieve() -> list[Any]:
        snapshot = llm_service.protocol.retrieve_schema(
            session=session,
            current_user=llm_service.current_user,
            ds=llm_service.ds,
            question=llm_service.retrieval_question,
            out_ds_instance=llm_service.out_ds_instance,
            resource_names=resource_names,
            required_resource_names=required_resource_names,
            access_scope=access_scope,
            table_limit=table_limit,
        )
        llm_service.chat_question.db_schema = snapshot.schema_text
        tables = list(snapshot.resource_names)
        llm_service.chat_question.sample_data = snapshot.sample_data
        llm_service.table_name_list = tables
        return tables

    if not audit:
        return _retrieve()

    with log_span(
        operate=OperationEnum.CHOOSE_TABLE,
        record_id=llm_service.record.id,
        local_operation=True,
        graph_node=graph_node,
        brief=brief,
        title_key="chat.log.CHOOSE_TABLE",
    ) as span:
        tables = _retrieve()
        # schema 全文不再入 detail（52KB 级转义串不可读且快照已有同份数据）
        span.set_detail(
            {
                "resource_count": len(tables),
                "resources": list(tables),
                "schema_chars": len(llm_service.chat_question.db_schema or ""),
                "access_scope_applied": access_scope is not None,
            }
        )
        span.set_summary("chat.audit.schema_ready", count=len(tables))
    return tables
