"""Durable, replayable input boundary for semantic planning.

LangGraph checkpoints contain IDs and orchestration state only.  Retrieval
results live on the request-local ``LLMService`` while a process is alive, so
resuming the checkpoint immediately before ``plan_query`` used to silently
plan with an empty schema.  This snapshot is the single persisted projection
of those inputs; it is not a second semantic contract.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field

from apps.chat.context_bundle import ContextSection, budget_context_sections
from apps.knowledge.compile import BusinessDataBundle, knowledge_prompt_payload

_PLANNER_CONTEXT_BUDGET = 24_000
_KNOWLEDGE_FLOOR_KEYS = (
    "matched_units",
    "concepts",
    "datasets",
    "fields",
    "relationships",
    "metrics",
    "calibers",
    "rules",
    "verified_examples",
    "conflicts",
)
_KNOWLEDGE_PROCESS_KEYS = ("processes", "data_effects", "assumptions")


def _split_knowledge_payload(
    compact: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    floor = {
        key: compact[key] for key in _KNOWLEDGE_FLOOR_KEYS if compact.get(key)
    }
    process = {
        key: compact[key] for key in _KNOWLEDGE_PROCESS_KEYS if compact.get(key)
    }
    leftover = {
        key: value
        for key, value in compact.items()
        if key not in _KNOWLEDGE_FLOOR_KEYS and key not in _KNOWLEDGE_PROCESS_KEYS
    }
    floor.update(leftover)
    return floor, process


def _bundle_from_prompt_payload(payload: dict[str, Any]) -> BusinessDataBundle:
    data = dict(payload)
    if "processes" in data and "scenarios" not in data:
        data["scenarios"] = data.pop("processes")
    if "conflicts" in data and "ambiguities" not in data:
        data["ambiguities"] = data.pop("conflicts")
    return BusinessDataBundle.model_validate(data)


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
    process_payload: dict[str, Any] = {}
    if isinstance(compiled, BusinessDataBundle):
        compiled_payload, process_payload = _split_knowledge_payload(
            knowledge_prompt_payload(compiled)
        )
    sections, truncation = budget_context_sections(
        [
            ContextSection(
                name="schema_text", content=str(question.db_schema or ""), trusted=True
            ),
            ContextSection(
                name="compiled_knowledge",
                content=compiled_payload,
                trusted=True,
            ),
            ContextSection(name="compiled_knowledge_process", content=process_payload),
            ContextSection(
                name="custom_rules", content=str(question.custom_prompt or "")
            ),
            ContextSection(name="sample_data", content=str(question.sample_data or "")),
        ],
        max_tokens=_PLANNER_CONTEXT_BUDGET,
    )
    knowledge = dict(sections.get("compiled_knowledge") or {})
    knowledge.update(sections.get("compiled_knowledge_process") or {})
    payload: dict[str, Any] = {
        "version": 2,
        "schema_text": sections.get("schema_text", ""),
        "resources": [str(item) for item in (llm_service.table_name_list or [])],
        "sample_data": sections.get("sample_data", ""),
        "terminology": "",
        "query_examples": "",
        "custom_rules": sections.get("custom_rules", ""),
        "entity_bindings": dict(entity_bindings or {}),
        "temporal_parse": dict(temporal_parse or {}),
        "compiled_knowledge": knowledge,
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


def execution_schema_resources(
    snapshot_resources: Sequence[str],
    plans: Sequence[Mapping[str, Any]],
) -> list[str] | None:
    """Exact schema projection for execute-time refresh.

    Planning already chose the visible tables. Execute re-reads that set plus
    any extra tables named by the plans. A subset of the planned schema is not
    drift. ``None`` ranks inside the fence; it is not a catalog dump.
    """
    names: list[str] = []
    for value in snapshot_resources:
        name = str(value).strip()
        if name and name not in names:
            names.append(name)
    for plan in plans:
        for table in plan.get("tables") or []:
            name = str(table).strip()
            if name and name not in names:
                names.append(name)
    return names or None


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
        llm_service.compiled_knowledge = _bundle_from_prompt_payload(
            snapshot.compiled_knowledge
        )
    return snapshot
