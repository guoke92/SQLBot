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
    specification: dict[str, Any] = Field(default_factory=dict)
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
    specification: dict[str, Any] | None,
    outcome: str,
    knowledge_apply: list[dict[str, Any]] | None = None,
    sql_list: list[str] | None = None,
    chat_id: int | None = None,
    assistant_id: int | None = None,
    entity_bindings: dict[str, Any] | None = None,
) -> TurnSnapshot:
    spec = specification or {}
    return TurnSnapshot(
        record_id=record_id,
        chat_id=chat_id,
        ds_id=ds_id,
        oid=oid,
        assistant_id=assistant_id,
        original_question=question,
        planning_question=question,
        specification=spec,
        outcome=outcome,
        contract_status="ready" if spec else "missing",
        knowledge_apply=list(knowledge_apply or []),
        sql_list=list(sql_list or []),
        entity_bindings=dict(entity_bindings or {}),
        clarification_answered=has_user_answer_requirements(spec),
    )


def specification_requirements(specification: dict[str, Any]) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for key in (
        "projections",
        "outputs",
        "predicates",
        "group_by",
        "time_windows",
        "order_by",
        "business_relations",
    ):
        requirements.extend(
            item for item in specification.get(key) or [] if isinstance(item, dict)
        )
    return requirements


def has_user_answer_requirements(specification: dict[str, Any]) -> bool:
    """True when any requirement cites immutable clarification evidence."""
    requirements = specification_requirements(specification)
    for req in requirements:
        if not isinstance(req, dict):
            continue
        refs = req.get("evidence_refs") or []
        if any(str(r).startswith("user:answer:") for r in refs):
            return True
    return False
