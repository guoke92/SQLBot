"""Unified recall result contract — one bundle for Agent and NLQ consumers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

TableSource = Literal["anchor", "table_page", "schema_vector"]
RecallBackend = Literal["wiki", "schema_vector", "none", "error"]


@dataclass(frozen=True)
class RecallBudget:
    """Single prompt-size budget. Prepare and search_wiki share one instance."""

    passages: int = 8
    prose_chars: int = 400
    max_tables: int = 4
    max_tables_total: int = 8
    schema_chars: int = 12000

    @classmethod
    def from_settings(cls) -> RecallBudget:
        from common.core.config import settings

        prose = int(getattr(settings, "KNOWLEDGE_WIKI_PROSE_CHARS", 0) or 0)
        return cls(
            passages=max(1, int(getattr(settings, "KNOWLEDGE_WIKI_RECALL_TOP_K", 8))),
            prose_chars=prose or 400,
            max_tables=max(
                1, int(getattr(settings, "KNOWLEDGE_WIKI_RECALL_MAX_TABLES", 4))
            ),
            max_tables_total=max(
                1, int(getattr(settings, "KNOWLEDGE_WIKI_RECALL_MAX_TABLES_TOTAL", 8))
            ),
            schema_chars=max(
                1, int(getattr(settings, "KNOWLEDGE_WIKI_RECALL_SCHEMA_CHARS", 12000))
            ),
        )


@dataclass(frozen=True)
class PassageHit:
    store_key: str
    page_key: str
    kind: str
    score: float
    vector: float
    lexical: float
    passed_gate: bool
    text: str
    title: str = ""
    source: str = ""


@dataclass(frozen=True)
class TableCandidate:
    name: str
    evidence: tuple[str, ...]
    score: float
    source: TableSource


@dataclass
class RecallBundle:
    """Sole recall output. Adapters keep Agent dict / WikiRecallResult stable."""

    backend: RecallBackend
    passages: tuple[PassageHit, ...] = ()
    tables: tuple[TableCandidate, ...] = ()
    schema_text: str = ""
    budget: RecallBudget = field(default_factory=RecallBudget)
    trace: dict[str, Any] = field(default_factory=dict)
    knowledge_text: str = ""
    page_keys: tuple[str, ...] = ()
    hits: tuple[dict[str, Any], ...] = ()
    store_source: str = ""
    corpus_id: int = 0
    generation: int = 0
    vector_chunks: int = 0
    vector_channel: bool = False
    elapsed_ms: int = 0
    embedding_built: bool = False
    schema_ready: bool = False
    schema_chars: int = 0
    hit_count: int = 0
    error: str | None = None
    gate_rejected: tuple[str, ...] = ()
    budget_cut: tuple[str, ...] = ()
    caliber_conflicts: tuple[dict[str, Any], ...] = ()

    def table_names(self) -> list[str]:
        return [item.name for item in self.tables]

    def table_evidence(self) -> dict[str, list[str]]:
        return {item.name: list(item.evidence) for item in self.tables}

    def to_agent_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "knowledge_text": self.knowledge_text,
            "tables": self.table_names(),
            "schema_text": self.schema_text,
            "backend": self.backend,
            "page_keys": list(self.page_keys),
            "hit_count": int(self.hit_count),
            "schema_ready": bool(self.schema_ready),
            "schema_chars": int(self.schema_chars or len(self.schema_text)),
            "store_source": self.store_source,
            "corpus_id": self.corpus_id,
            "generation": self.generation,
            "vector_chunks": self.vector_chunks,
            "vector_channel": self.vector_channel,
            "wiki_trace": dict(self.trace),
            "hits": list(self.hits)[:12],
            "elapsed_ms": self.elapsed_ms,
            "embedding_built": self.embedding_built,
            "gate_rejected": list(self.gate_rejected),
            "table_evidence": self.table_evidence(),
            "budget_cut": list(self.budget_cut),
            "caliber_conflicts": [dict(item) for item in self.caliber_conflicts],
        }
        if self.error:
            payload["error"] = self.error
        return payload

    def to_wiki_result(self) -> Any:
        from apps.chat.steps.wiki_recall import WikiRecallResult

        return WikiRecallResult(
            text=self.knowledge_text,
            hits=list(self.hits),
            page_keys=list(self.page_keys),
            elapsed_ms=self.elapsed_ms,
            embedding_built=self.embedding_built,
            passages={hit.page_key: hit.text for hit in self.passages if hit.text},
            trace=dict(self.trace),
            store_source=self.store_source,
            corpus_id=self.corpus_id,
            generation=self.generation,
            vector_chunks=self.vector_chunks,
            vector_channel=self.vector_channel,
        )
