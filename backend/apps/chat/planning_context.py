"""Durable, replayable input boundary for semantic planning.

LangGraph checkpoints contain IDs and orchestration state only.  Retrieval
results live on the request-local ``LLMService`` while a process is alive, so
resuming the checkpoint immediately before ``plan_query`` used to silently
plan with an empty schema.  This snapshot is the single persisted projection
of those inputs; it is not a second semantic contract.
"""

from __future__ import annotations

import hashlib
from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field

from apps.chat.context_bundle import ContextSection, budget_context_sections
from apps.knowledge.compile import CompiledKnowledge

_PLANNER_CONTEXT_BUDGET = 24_000


class PlanningContextSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[2] = 2
    schema_text: str
    resources: list[str] = Field(default_factory=list)
    sample_data: str = ""
    terminology: str = ""
    query_examples: str = ""
    custom_rules: str = ""
    entity_bindings: dict[str, Any] = Field(default_factory=dict)
    temporal_parse: dict[str, Any] = Field(default_factory=dict)
    compiled_knowledge: dict[str, Any] = Field(default_factory=dict)
    schema_fingerprint: str = ""
    truncation: list[dict[str, Any]] = Field(default_factory=list)
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
    sections, truncation = budget_context_sections(
        [
            ContextSection(
                name="schema_text", content=str(question.db_schema or ""), trusted=True
            ),
            ContextSection(name="compiled_knowledge", content=compiled_payload),
            ContextSection(
                name="custom_rules", content=str(question.custom_prompt or "")
            ),
            ContextSection(
                name="terminology", content=str(question.terminologies or "")
            ),
            ContextSection(
                name="query_examples", content=str(question.data_training or "")
            ),
            ContextSection(name="sample_data", content=str(question.sample_data or "")),
        ],
        max_tokens=_PLANNER_CONTEXT_BUDGET,
    )
    payload: dict[str, Any] = {
        "version": 2,
        "schema_text": sections.get("schema_text", ""),
        "resources": [str(item) for item in (llm_service.table_name_list or [])],
        "sample_data": sections.get("sample_data", ""),
        "terminology": sections.get("terminology", ""),
        "query_examples": sections.get("query_examples", ""),
        "custom_rules": sections.get("custom_rules", ""),
        "entity_bindings": dict(entity_bindings or {}),
        "temporal_parse": dict(temporal_parse or {}),
        "compiled_knowledge": sections.get("compiled_knowledge", {}),
        "truncation": list(truncation),
    }
    schema_material = orjson.dumps(
        {
            "schema_text": payload["schema_text"],
            "resources": payload["resources"],
        },
        option=orjson.OPT_SORT_KEYS,
    )
    payload["schema_fingerprint"] = hashlib.sha256(schema_material).hexdigest()
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
