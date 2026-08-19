"""Knowledge providers with one structured recall contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlmodel import Session

from apps.knowledge.dictionary_recall import recall_dictionary
from apps.knowledge.models import KnowledgeBundle


@dataclass(frozen=True)
class KnowledgeRecallContext:
    question: str
    oid: int
    ds_id: int | None
    advanced_application_id: int | None = None


class KnowledgeProvider(Protocol):
    def recall(
        self,
        session: Session,
        context: KnowledgeRecallContext,
    ) -> KnowledgeBundle: ...


class DictionaryProvider:
    def recall(
        self,
        session: Session,
        context: KnowledgeRecallContext,
    ) -> KnowledgeBundle:
        if context.ds_id is None or context.advanced_application_id is not None:
            return KnowledgeBundle()
        return KnowledgeBundle(
            matches=recall_dictionary(
                session,
                question=context.question,
                oid=context.oid,
                ds_id=context.ds_id,
            )
        )


DEFAULT_KNOWLEDGE_PROVIDERS: tuple[KnowledgeProvider, ...] = (DictionaryProvider(),)
