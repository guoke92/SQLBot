"""Durable, replayable input boundary for semantic planning.

LangGraph checkpoints contain IDs and orchestration state only.  Retrieval
results live on the request-local ``LLMService`` while a process is alive, so
resuming the checkpoint immediately before ``plan_query`` used to silently
plan with an empty schema.  This snapshot is the single persisted projection
of those inputs; it is not a second semantic contract.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import and_, select

from apps.knowledge.compile import CompiledKnowledge


class PlanningContextSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    schema_text: str
    resources: list[str] = Field(default_factory=list)
    sample_data: str = ""
    terminology: str = ""
    query_examples: str = ""
    custom_rules: str = ""
    entity_bindings: dict[str, Any] = Field(default_factory=dict)
    temporal_parse: dict[str, Any] = Field(default_factory=dict)
    compiled_knowledge: dict[str, Any] = Field(default_factory=dict)
    fingerprint: str = ""

    @property
    def usable(self) -> bool:
        # Every protocol planner needs a concrete schema/API catalog.  An
        # empty resource list alone is not decisive (some protocols expose a
        # schema without table names), but an empty schema never is usable.
        return bool(self.schema_text.strip())


def capture_planning_context(
    llm_service: Any,
    *,
    entity_bindings: dict[str, Any],
    temporal_parse: dict[str, Any],
) -> PlanningContextSnapshot:
    question = llm_service.chat_question
    compiled = getattr(llm_service, "compiled_knowledge", None)
    compiled_payload: dict[str, Any] = {}
    if isinstance(compiled, CompiledKnowledge):
        # Persist only what plan_query / replan hydrate need. Embedding matches
        # and prompt log_items are request-local; clarification reuses bindings.
        full = compiled.model_dump(mode="json")
        for key in (
            "stage",
            "prompt_template",
            "bound_calibers",
            "constraints",
            "examples",
            "reuse",
            "apply_log",
            "structural_ref",
        ):
            if key in full:
                compiled_payload[key] = full[key]
    payload: dict[str, Any] = {
        "version": 1,
        "schema_text": str(question.db_schema or ""),
        "resources": [str(item) for item in (llm_service.table_name_list or [])],
        "sample_data": str(question.sample_data or ""),
        "terminology": str(question.terminologies or ""),
        "query_examples": str(question.data_training or ""),
        "custom_rules": str(question.custom_prompt or ""),
        "entity_bindings": dict(entity_bindings or {}),
        "temporal_parse": dict(temporal_parse or {}),
        "compiled_knowledge": compiled_payload,
    }
    fingerprint_material = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)
    payload["fingerprint"] = hashlib.sha256(fingerprint_material).hexdigest()
    return PlanningContextSnapshot.model_validate(payload)


def restore_planning_context(
    llm_service: Any,
    payload: dict[str, Any],
) -> PlanningContextSnapshot:
    snapshot = PlanningContextSnapshot.model_validate(payload)
    if not snapshot.usable:
        raise ValueError("Persisted planning context does not contain a usable schema")
    question = llm_service.chat_question
    question.db_schema = snapshot.schema_text
    question.sample_data = snapshot.sample_data
    question.terminologies = snapshot.terminology
    question.data_training = snapshot.query_examples
    question.custom_prompt = snapshot.custom_rules
    llm_service.table_name_list = list(snapshot.resources)
    if snapshot.compiled_knowledge:
        llm_service.compiled_knowledge = CompiledKnowledge.model_validate(
            snapshot.compiled_knowledge
        )
    return snapshot


@dataclass(frozen=True)
class ChatPlanningMemory:
    """Prior turns in the same chat that the current planner must inherit."""

    turns: list[dict[str, Any]]
    previous_specification: dict[str, Any] | None
    resolved_business_axes: frozenset[str]


def load_chat_planning_memory(
    session: Any,
    *,
    chat_id: int,
    current_record_id: int | None,
    limit: int = 5,
) -> ChatPlanningMemory:
    """Load recent NLQ turns so a new run continues the same conversation."""
    from apps.chat.models.chat_model import ChatRecord
    from apps.conversation.models import ConversationRun, NlqRun
    from apps.conversation.run_service import active_evidence

    filters = [
        ChatRecord.chat_id == chat_id,
        ChatRecord.analysis_record_id.is_(None),
        ChatRecord.predict_record_id.is_(None),
    ]
    if current_record_id is not None:
        filters.append(ChatRecord.id != current_record_id)
    records = list(
        session.execute(
            select(ChatRecord)
            .where(and_(*filters))
            .order_by(ChatRecord.id.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    records.reverse()
    turns: list[dict[str, Any]] = []
    previous_specification: dict[str, Any] | None = None
    resolved_axes: set[str] = set()
    for record in records:
        if getattr(record, "first_chat", False):
            continue
        question = str(record.question or "").strip()
        if not question:
            continue
        run = session.execute(
            select(ConversationRun).where(
                ConversationRun.chat_record_id == record.id
            )
        ).scalars().first()
        nlq = session.get(NlqRun, run.run_id) if run is not None else None
        spec = None
        if nlq is not None and nlq.specifications:
            spec = nlq.specifications[-1]
            if isinstance(spec, dict):
                previous_specification = spec
        clarifications: list[dict[str, Any]] = []
        if run is not None:
            for event in active_evidence(session, run.run_id):
                if event.kind not in {
                    "clarification_option",
                    "clarification_custom",
                    "user_correction",
                }:
                    continue
                structured = dict(event.structured_value or {})
                axis = str(structured.get("business_axis") or "").strip()
                if axis:
                    resolved_axes.add(axis)
                clarifications.append(
                    {
                        "business_axis": axis,
                        "content": event.content,
                        "resolution": structured.get("resolution"),
                    }
                )
        turns.append(
            {
                "question": question,
                "status": getattr(run, "status", None),
                "clarifications": clarifications,
                "has_specification": spec is not None,
            }
        )
    return ChatPlanningMemory(
        turns=turns,
        previous_specification=previous_specification,
        resolved_business_axes=frozenset(resolved_axes),
    )
