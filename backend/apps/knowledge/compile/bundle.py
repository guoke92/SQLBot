"""Compiled knowledge bundle — sole NLQ knowledge apply surface."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from apps.knowledge.models import KnowledgeMatch

ApplyAction = Literal["bind", "structural", "constrain", "exemplify", "clarify", "drop"]
CompileStage = Literal["assess", "generate", "repair"]


class ApplyHit(BaseModel):
    asset_kind: str
    asset_id: int | str | None = None
    lineage_id: str | None = None
    trust_tier: str | None = None
    apply: ApplyAction
    reason: str = ""
    meta: dict[str, Any] = Field(default_factory=dict)


class BoundCaliber(BaseModel):
    caliber_id: int
    lineage_id: str
    label: str
    fragment: dict[str, Any]
    field_targets: list[Any] = Field(default_factory=list)
    trust_tier: str = "certified"
    apply: Literal["bind"] = "bind"


class CompiledKnowledge(BaseModel):
    """Phase A fills legacy KnowledgeBundle fields for ground_entities compat."""

    stage: CompileStage = "assess"
    prompt_template: str = ""
    log_items: list[dict[str, Any]] = Field(default_factory=list)
    matches: list[KnowledgeMatch] = Field(default_factory=list)
    bound_calibers: list[BoundCaliber] = Field(default_factory=list)
    constraint_cards: list[dict[str, Any]] = Field(default_factory=list)
    examples: list[dict[str, Any]] = Field(default_factory=list)
    clarify_hints: list[str] = Field(default_factory=list)
    structural_ref: dict[str, Any] = Field(default_factory=dict)
    apply_log: list[ApplyHit] = Field(default_factory=list)

    def knowledge_apply_payload(self) -> list[dict[str, Any]]:
        return [hit.model_dump(mode="json") for hit in self.apply_log]
