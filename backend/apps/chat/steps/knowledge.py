"""Compile the Query Agent knowledge bundle (units + dictionary bindings)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlmodel import Session

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span
from apps.chat.steps.scope import match_scope
from apps.datasource.access import AccessScope
from apps.knowledge.compile import (
    BusinessDataBundle,
    SeedPolicy,
    compile_business_data_bundle,
)
from apps.knowledge.models import KnowledgeMatch
from apps.knowledge.scope import scope_knowledge_matches


def _scope_dictionary_matches(
    access_scope: AccessScope | None,
    matches: list[KnowledgeMatch],
) -> list[KnowledgeMatch]:
    """Apply the same local table/column/row permission scope as schema recall."""
    if access_scope is None:
        return [match for match in matches if "entity_binding" not in match.usages]

    return scope_knowledge_matches(
        matches,
        allowed_targets=access_scope.allowed_targets,
        row_restricted_tables=access_scope.row_restricted_tables,
    )


def match_knowledge(
    llm_service: Any,
    session: Session,
    oid: int | None = None,
    ds_id: int | None = None,
    access_scope: AccessScope | None = None,
    *,
    stage: str = "assess",
    include_examples: bool = False,
    seed_revision_ids: Sequence[int] = (),
    seed_policy: SeedPolicy = "none",
) -> list[KnowledgeMatch]:
    """Compile knowledge for the turn; return matches for ground_entities compat."""
    with log_span(
        operate=OperationEnum.FILTER_TERMS,
        record_id=llm_service.record.id,
        local_operation=True,
        graph_node="retrieve_context",
        title_key="chat.log.FILTER_TERMS",
    ) as span:
        calculate_oid, calculate_ds_id, _assistant_id = match_scope(
            llm_service, oid, ds_id
        )
        compiled = compile_business_data_bundle(
            session,
            stage=stage,  # type: ignore[arg-type]
            question=llm_service.retrieval_question,
            oid=int(calculate_oid or 1),
            ds_id=calculate_ds_id,
            include_examples=include_examples or stage == "generate",
            seed_revision_ids=seed_revision_ids,
            seed_policy=seed_policy,
        )
        matches = _scope_dictionary_matches(access_scope, compiled.matches)
        compiled = compiled.model_copy(update={"matches": matches})
        # BusinessDataBundle is the sole business-knowledge input. Do not
        # render the same unit again through the legacy terminology channel.
        llm_service.chat_question.terminologies = ""
        llm_service.compiled_knowledge = compiled
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
        apply_payload = compiled.knowledge_apply_payload()
        span.set_detail(
            {
                "unit_count": len(compiled.matched_units),
                "matched_units": [
                    {
                        "unit_id": item.get("unit_id"),
                        "unit_key": item.get("unit_key"),
                        "title": item.get("title"),
                        "domain": item.get("domain"),
                        "revision": item.get("revision"),
                        "confidence": item.get("confidence"),
                    }
                    for item in compiled.matched_units
                ],
                "dictionary_count": len(matches),
                "matches": [*compiled.log_items, *dictionary_items],
                "knowledge_apply": apply_payload,
            }
        )
        span.set_summary(
            "chat.audit.knowledge_ready", count=len(compiled.matched_units)
        )
    return matches


def get_compiled_knowledge(llm_service: Any) -> BusinessDataBundle | None:
    compiled = getattr(llm_service, "compiled_knowledge", None)
    if isinstance(compiled, BusinessDataBundle):
        return compiled
    return None
