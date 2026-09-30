"""Session Memory Slots for persistent multi-turn context and caliber retention."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field

from apps.chat.caliber_surface import (
    ingest_confirmed_calibers,
    lift_confirmed_from_assumptions,
    project_query_assumptions,
)


class MemorySlots(BaseModel):
    """Structured slots maintained across turns in a conversation."""

    confirmed_calibers: dict[str, Any] = Field(
        default_factory=dict,
        description="Explicit user-confirmed metric or date calibers, e.g. {'amount': 'pay_amount', 'date': 'pay_time'}",
    )
    assumptions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Declared non-obvious filters or caliber choices awaiting/after user awareness",
    )
    excluded_filters: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Persistent negative constraints, e.g. [{'field': 'status', 'op': 'NOT IN', 'value': ['CANCELLED']}]",
    )
    current_rev: str = Field(
        default="",
        description="Current SqlWorkspace revision handle (rN).",
    )
    active_dataset_outline: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata outline of the latest result dataset (fields, row_count, sample).",
    )
    knowledge_refs: dict[str, Any] = Field(
        default_factory=dict,
        description="Referenced turn's knowledge working set, keys only: {'page_keys': [...], 'tables': [...]}",
    )
    prior_questions: list[str] = Field(
        default_factory=list,
        description="Questions of the referenced turns (oldest first) — retrieval context for follow-ups.",
    )


def answer_has_executable_sql(answer: Mapping[str, Any] | None) -> bool:
    if not isinstance(answer, Mapping):
        return False
    if str(answer.get("status") or "") != "succeeded":
        return False
    for item in answer.get("datasets") or []:
        if isinstance(item, Mapping) and str(item.get("sql") or "").strip():
            return True
    return False


def hydrate_memory_slots_from_referenced_turns(
    memory_slots: MemorySlots,
    referenced_turns: Sequence[Mapping[str, Any]],
) -> MemorySlots:
    """Restore baseline SQL and confirmed calibers from prior turn outlines."""
    if not referenced_turns:
        return memory_slots
    latest = referenced_turns[-1]
    if not memory_slots.current_rev:
        for ds in latest.get("datasets") or []:
            if not isinstance(ds, Mapping):
                continue
            rev = str(ds.get("rev") or "").strip()
            if rev:
                memory_slots.current_rev = rev
            outline_fields = list(ds.get("fields") or [])
            if outline_fields or ds.get("dataset_id"):
                memory_slots.active_dataset_outline = {
                    "dataset_id": ds.get("dataset_id"),
                    "fields": outline_fields,
                    "row_count": ds.get("row_count"),
                    "rev": rev,
                }
            if rev:
                break

    refs = latest.get("knowledge_refs")
    if not memory_slots.knowledge_refs and isinstance(refs, Mapping):
        memory_slots.knowledge_refs = {
            "page_keys": [str(k) for k in (refs.get("page_keys") or []) if str(k)],
            "tables": [str(t) for t in (refs.get("tables") or []) if str(t)],
        }
    if not memory_slots.prior_questions:
        memory_slots.prior_questions = [
            str(turn.get("question") or "").strip()
            for turn in referenced_turns
            if isinstance(turn, Mapping) and str(turn.get("question") or "").strip()
        ]

    raw_assumptions = latest.get("assumptions")
    if not memory_slots.assumptions and isinstance(raw_assumptions, list):
        memory_slots.assumptions = [
            dict(item) for item in raw_assumptions if isinstance(item, Mapping)
        ]

    if not memory_slots.confirmed_calibers:
        ingest_confirmed_calibers(
            memory_slots.confirmed_calibers,
            latest.get("confirmed_calibers"),
        )
        if not memory_slots.confirmed_calibers:
            memory_slots.assumptions = lift_confirmed_from_assumptions(
                memory_slots.confirmed_calibers,
                memory_slots.assumptions,
            )
        else:
            # Keep slot assumptions = undeclared only (single surface rule).
            memory_slots.assumptions = project_query_assumptions(
                {"assumptions": memory_slots.assumptions}
            )
    elif memory_slots.assumptions:
        memory_slots.assumptions = project_query_assumptions(
            {"assumptions": memory_slots.assumptions}
        )
    return memory_slots
