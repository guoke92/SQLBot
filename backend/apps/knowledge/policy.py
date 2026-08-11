"""Workspace KnowledgePolicy — separate from Catalog mining_policy."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CompileBudgets(BaseModel):
    generate_examples: int = 2
    repair_hints: int = 1


class KnowledgePolicy(BaseModel):
    reproduce_count_n: int = 3
    compile_budgets: CompileBudgets = Field(default_factory=CompileBudgets)
    reuse_enabled: bool = True
    reuse_similarity_threshold: float = 0.95


DEFAULT_KNOWLEDGE_POLICY = KnowledgePolicy()


def get_knowledge_policy(raw: dict[str, Any] | None = None) -> KnowledgePolicy:
    if not raw:
        return DEFAULT_KNOWLEDGE_POLICY.model_copy(deep=True)
    return KnowledgePolicy.model_validate(raw)
