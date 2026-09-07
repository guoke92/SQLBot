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
    active_baseline_sql: str = Field(
        default="",
        description="Latest successfully executed SQL query statement.",
    )
    active_dataset_outline: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata outline of the latest result dataset (fields, row_count, sample).",
    )

    def extract_change_baseline(self) -> dict[str, Any]:
        """Compact baseline for incremental patching in the current turn."""
        if not self.active_baseline_sql:
            return {}
        return {
            "sql": self.active_baseline_sql,
            "outline": self.active_dataset_outline,
            "confirmed_calibers": self.confirmed_calibers,
            "excluded_filters": self.excluded_filters,
        }

    def update_from_execution(
        self,
        *,
        executed_sql: str,
        fields: list[str],
        row_count: int,
        sample_rows: list[dict[str, Any]] | None = None,
    ) -> None:
        if executed_sql:
            self.active_baseline_sql = executed_sql
            self.active_dataset_outline = {
                "fields": fields,
                "row_count": row_count,
                "sample_rows": (sample_rows or [])[:3],
            }


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
    if not memory_slots.active_baseline_sql:
        for ds in latest.get("datasets") or []:
            if not isinstance(ds, Mapping):
                continue
            sql = str(ds.get("sql") or "").strip()
            if not sql:
                continue
            memory_slots.active_baseline_sql = sql
            memory_slots.active_dataset_outline = {
                "fields": list(ds.get("fields") or []),
                "row_count": ds.get("row_count"),
            }
            break

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
