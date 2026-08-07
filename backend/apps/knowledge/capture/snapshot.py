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
    intent_context: dict[str, Any] = Field(default_factory=dict)
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
    intent_context: dict[str, Any] | None,
    outcome: str,
    knowledge_apply: list[dict[str, Any]] | None = None,
    sql_list: list[str] | None = None,
    chat_id: int | None = None,
    assistant_id: int | None = None,
    entity_bindings: dict[str, Any] | None = None,
) -> TurnSnapshot:
    ctx = intent_context or {}
    return TurnSnapshot(
        record_id=record_id,
        chat_id=chat_id,
        ds_id=ds_id,
        oid=oid,
        assistant_id=assistant_id,
        original_question=question,
        planning_question=question,
        intent_context=ctx,
        outcome=outcome,
        contract_status=str(ctx.get("status") or ""),
        knowledge_apply=list(knowledge_apply or []),
        sql_list=list(sql_list or []),
        entity_bindings=dict(entity_bindings or {}),
        clarification_answered=has_user_answer_slots(ctx),
    )


def has_user_answer_slots(intent_context: dict[str, Any]) -> bool:
    """True when any contract requirement cites user:answer:* evidence."""
    contract = intent_context.get("contract") or {}
    requirements = contract.get("requirements") or []
    for req in requirements:
        if not isinstance(req, dict):
            continue
        refs = req.get("evidence_refs") or []
        if any(str(r).startswith("user:answer:") for r in refs):
            return True
    answers = intent_context.get("answers") or []
    return bool(answers)
