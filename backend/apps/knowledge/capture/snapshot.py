"""TurnSnapshot assembled at NLQ terminal success for async capture."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TurnSnapshot(BaseModel):
    record_id: int
    chat_id: int | None = None
    ds_id: int | None = None
    oid: int = 1
    assistant_id: int | None = None
    original_question: str = ""
    planning_question: str = ""
    risk_assessment: dict[str, Any] = Field(default_factory=dict)
    semantic_review: dict[str, Any] = Field(default_factory=dict)
    plan_facts: list[dict[str, Any]] = Field(default_factory=list)
    clarification_resolutions: list[dict[str, Any]] = Field(default_factory=list)
    outcome: str = ""
    quality: dict[str, Any] = Field(default_factory=dict)
    validation_status: str = ""
    knowledge_apply: list[dict[str, Any]] = Field(default_factory=list)
    sql_list: list[str] = Field(default_factory=list)
    entity_bindings: dict[str, Any] = Field(default_factory=dict)
    clarification_answered: bool = False


def build_turn_snapshot(
    *,
    record_id: int,
    oid: int,
    ds_id: int | None,
    question: str,
    risk_assessment: dict[str, Any] | None,
    semantic_review: dict[str, Any] | None,
    plan_facts: list[dict[str, Any]] | None,
    clarification_resolutions: list[dict[str, Any]] | None,
    outcome: str,
    knowledge_apply: list[dict[str, Any]] | None = None,
    sql_list: list[str] | None = None,
    chat_id: int | None = None,
    assistant_id: int | None = None,
    entity_bindings: dict[str, Any] | None = None,
) -> TurnSnapshot:
    risk = dict(risk_assessment or {})
    review = dict(semantic_review or {})
    return TurnSnapshot(
        record_id=record_id,
        chat_id=chat_id,
        ds_id=ds_id,
        oid=oid,
        assistant_id=assistant_id,
        original_question=question,
        planning_question=question,
        risk_assessment=risk,
        semantic_review=review,
        plan_facts=list(plan_facts or []),
        clarification_resolutions=list(clarification_resolutions or []),
        outcome=outcome,
        validation_status=(
            "verified"
            if risk.get("level") == "low" or review.get("verdict") == "pass"
            else "unverified"
        ),
        knowledge_apply=list(knowledge_apply or []),
        sql_list=list(sql_list or []),
        entity_bindings=dict(entity_bindings or {}),
        clarification_answered=bool(clarification_resolutions),
    )
