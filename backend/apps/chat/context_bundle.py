"""Partitioned, budgeted input contract shared by query/analysis/prediction."""

from __future__ import annotations

import hashlib
from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict

from apps.chat.turn_contracts import TurnRoute


class ContextSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    content: Any
    estimated_tokens: int = 0
    trusted: bool = False


def estimate_tokens(value: Any) -> int:
    """Cheap conservative estimator used only for context budgeting."""
    if value is None:
        return 0
    if not isinstance(value, str):
        value = orjson.dumps(value, default=str).decode()
    return max(1, len(value) // 3)


def context_fingerprint(parts: dict[str, Any]) -> str:
    return hashlib.sha256(
        orjson.dumps(parts, option=orjson.OPT_SORT_KEYS, default=str)
    ).hexdigest()


def budget_context_sections(
    sections: list[ContextSection], *, max_tokens: int
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    """Keep sections by caller priority; never truncate trusted user evidence."""
    used = 0
    kept: dict[str, Any] = {}
    truncated: list[dict[str, Any]] = []
    for section in sections:
        cost = section.estimated_tokens or estimate_tokens(section.content)
        if section.trusted or used + cost <= max_tokens:
            kept[section.name] = section.content
            used += cost
            continue
        truncated.append(
            {
                "section": section.name,
                "estimated_tokens": cost,
                "reason": "context_budget",
            }
        )
    return kept, tuple(truncated)


def choose_data_strategy(
    route: TurnRoute,
    *,
    referenced_datasets: tuple[dict[str, Any], ...],
    message_has_query_need: bool,
) -> Literal["direct_query", "existing_results", "derived_query", "unavailable"]:
    if route.task_kind == "query":
        return "direct_query"
    usable = [
        item
        for item in referenced_datasets
        if item.get("status") in {"succeeded", "degraded"}
    ]
    if route.task_kind == "analysis":
        if usable:
            return "existing_results"
        return "derived_query" if message_has_query_need else "unavailable"
    if route.task_kind == "prediction":
        time_series = [
            item
            for item in usable
            if item.get("has_time_field")
            and item.get("has_numeric_measure")
            and int(item.get("valid_points") or 0) >= 6
        ]
        if time_series:
            return "existing_results"
        return "derived_query"
    return "unavailable"
