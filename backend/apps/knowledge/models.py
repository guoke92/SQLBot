from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

KnowledgeUsage = Literal["prompt", "entity_binding"]


class FieldTarget(BaseModel):
    ds_id: int
    table_id: int
    table_name: str
    field_id: int
    field_name: str


class KnowledgeMatch(BaseModel):
    source: Literal["terminology", "dictionary"]
    usages: list[KnowledgeUsage]
    query: str
    canonical: str
    alternatives: list[str] = Field(default_factory=list)
    description: str = ""
    match_type: Literal["exact", "suffix", "contains", "semantic"]
    score: float
    targets: list[FieldTarget] = Field(default_factory=list)


class KnowledgeBundle(BaseModel):
    prompt_template: str = ""
    log_items: list[dict[str, Any]] = Field(default_factory=list)
    matches: list[KnowledgeMatch] = Field(default_factory=list)
