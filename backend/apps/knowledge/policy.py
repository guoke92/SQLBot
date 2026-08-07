"""Workspace KnowledgePolicy — separate from Catalog mining_policy."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CompileBudgets(BaseModel):
    assess_constrain_cards: int = 6
    generate_examples: int = 2
    generate_constrain_cards: int = 4
    repair_hints: int = 1


class KnowledgePolicy(BaseModel):
    """Defaults match the locked plan; missing workspace config uses these."""

    caliber_bind_requires: Literal["certified", "trusted"] = "certified"
    caliber_auto_trusted: bool = True
    example_auto_publish: bool = False
    reproduce_count_n: int = 3
    promotion_window_days: int = 90
    allow_user_certify: bool = False
    assess_constrain_uncertified_caliber: bool = False
    applied_lineage_full: bool = False
    compile_budgets: CompileBudgets = Field(default_factory=CompileBudgets)


DEFAULT_KNOWLEDGE_POLICY = KnowledgePolicy()


def get_knowledge_policy(raw: dict[str, Any] | None = None) -> KnowledgePolicy:
    """Parse policy from workspace settings JSON; never read mining_policy."""
    if not raw:
        return DEFAULT_KNOWLEDGE_POLICY.model_copy(deep=True)
    return KnowledgePolicy.model_validate(raw)
