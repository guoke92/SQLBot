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
    intent_revision: dict[str, Any] = Field(default_factory=dict)
    outcome: str = ""
    quality: dict[str, Any] = Field(default_factory=dict)
    contract_status: str = ""
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
    intent_revision: dict[str, Any] | None,
    outcome: str,
    knowledge_apply: list[dict[str, Any]] | None = None,
    sql_list: list[str] | None = None,
    chat_id: int | None = None,
    assistant_id: int | None = None,
    entity_bindings: dict[str, Any] | None = None,
) -> TurnSnapshot:
    revision = intent_revision or {}
    return TurnSnapshot(
        record_id=record_id,
        chat_id=chat_id,
        ds_id=ds_id,
        oid=oid,
        assistant_id=assistant_id,
        original_question=question,
        planning_question=question,
        intent_revision=revision,
        outcome=outcome,
        contract_status="accepted" if revision.get("status") == "accepted" else "missing",
        knowledge_apply=list(knowledge_apply or []),
        sql_list=list(sql_list or []),
        entity_bindings=dict(entity_bindings or {}),
        clarification_answered=has_user_answer_requirements(revision),
    )


def has_user_answer_requirements(intent_revision: dict[str, Any]) -> bool:
    """True when an intent item cites immutable clarification evidence."""
    return any(
        any(str(ref).startswith("user:answer:") for ref in refs or [])
        for refs in (intent_revision.get("evidence_map") or {}).values()
    )
