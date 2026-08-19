"""Compiled knowledge bundle — sole NLQ knowledge apply surface."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from apps.knowledge.models import KnowledgeMatch

ApplyAction = Literal["bind", "constrain", "exemplify", "drop", "reuse"]
CompileStage = Literal["assess", "generate"]


class ApplyHit(BaseModel):
    asset_kind: str
    asset_id: int | str | None = None
    lineage_id: str | None = None
    trust_tier: str | None = None
    apply: ApplyAction
    reason: str = ""
    meta: dict[str, Any] = Field(default_factory=dict)


class BusinessDataBundle(BaseModel):
    """Single runtime knowledge contract consumed by the Query Agent.

    Semantic slots expand from active knowledge-unit revisions. Dictionary
    matches stay on this object for entity binding; ``bound_resources`` is the
    schema projection, not a prompt slot.
    """

    matched_units: list[dict[str, Any]] = Field(default_factory=list)
    bound_resources: list[str] = Field(default_factory=list)
    concepts: list[dict[str, Any]] = Field(default_factory=list)
    scenarios: list[dict[str, Any]] = Field(default_factory=list)
    data_effects: list[dict[str, Any]] = Field(default_factory=list)
    datasets: list[dict[str, Any]] = Field(default_factory=list)
    fields: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    metrics: list[dict[str, Any]] = Field(default_factory=list)
    calibers: list[dict[str, Any]] = Field(default_factory=list)
    rules: list[dict[str, Any]] = Field(default_factory=list)
    verified_examples: list[dict[str, Any]] = Field(default_factory=list)
    ambiguities: list[dict[str, Any]] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

    stage: CompileStage = "assess"
    log_items: list[dict[str, Any]] = Field(default_factory=list)
    matches: list[KnowledgeMatch] = Field(default_factory=list)
    structural_ref: dict[str, Any] = Field(default_factory=dict)
    reuse: dict[str, Any] | None = None
    apply_log: list[ApplyHit] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.matched_units and not self.matches

    def knowledge_apply_payload(self) -> list[dict[str, Any]]:
        return [hit.model_dump(mode="json") for hit in self.apply_log]
