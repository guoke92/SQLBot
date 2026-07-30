from __future__ import annotations

from sqlmodel import Session

from apps.knowledge.models import KnowledgeBundle
from apps.knowledge.providers import (
    DEFAULT_KNOWLEDGE_PROVIDERS,
    KnowledgeProvider,
    KnowledgeRecallContext,
)


def recall_knowledge(
    session: Session,
    *,
    question: str,
    oid: int,
    ds_id: int | None,
    advanced_application_id: int | None = None,
    providers: tuple[KnowledgeProvider, ...] = DEFAULT_KNOWLEDGE_PROVIDERS,
) -> KnowledgeBundle:
    """Recall all providers while preserving provider-specific quotas."""
    context = KnowledgeRecallContext(
        question=question,
        oid=oid,
        ds_id=ds_id,
        advanced_application_id=advanced_application_id,
    )
    bundles = [provider.recall(session, context) for provider in providers]
    return KnowledgeBundle(
        prompt_template=next(
            (
                bundle.prompt_template
                for bundle in bundles
                if bundle.prompt_template
            ),
            "",
        ),
        log_items=[
            item
            for bundle in bundles
            for item in bundle.log_items
        ],
        matches=[
            match
            for bundle in bundles
            for match in bundle.matches
        ],
    )
