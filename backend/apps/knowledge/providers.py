"""Knowledge providers with one structured recall contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlmodel import Session

from apps.knowledge.dictionary_recall import recall_dictionary
from apps.knowledge.models import KnowledgeBundle, KnowledgeMatch
from apps.terminology.curd.terminology import get_terminology_template


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


class TerminologyProvider:
    def recall(
        self,
        session: Session,
        context: KnowledgeRecallContext,
    ) -> KnowledgeBundle:
        template, terms = get_terminology_template(
            session,
            context.question,
            context.oid,
            context.ds_id,
            context.advanced_application_id,
        )
        matches = [
            KnowledgeMatch(
                source="terminology",
                usages=["prompt"],
                query=context.question,
                canonical=(term.get("words") or [""])[0],
                alternatives=list((term.get("words") or [])[1:]),
                description=term.get("description") or "",
                match_type=(
                    "exact"
                    if any(
                        str(word).lower() in context.question.lower()
                        for word in term.get("words") or []
                    )
                    else "semantic"
                ),
                score=float(term.get("score") or 0.0),
            )
            for term in terms
            if term.get("words")
        ]
        return KnowledgeBundle(
            prompt_template=template,
            log_items=terms,
            matches=matches,
        )


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


DEFAULT_KNOWLEDGE_PROVIDERS: tuple[KnowledgeProvider, ...] = (
    TerminologyProvider(),
    DictionaryProvider(),
)
