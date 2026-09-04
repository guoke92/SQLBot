"""Session Memory Slots for persistent multi-turn context and caliber retention."""

from __future__ import annotations

from typing import Any, Mapping
from pydantic import BaseModel, Field


class MemorySlots(BaseModel):
    """Structured slots maintained across turns in a conversation."""

    confirmed_calibers: dict[str, Any] = Field(
        default_factory=dict,
        description="Explicit user-confirmed metric or date calibers, e.g. {'amount': 'pay_amount', 'date': 'pay_time'}",
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
