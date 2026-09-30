"""Explicit loop budget for the chat agent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from apps.chat.agent_knowledge import (
    EXECUTION_ROUND_LIMIT,
    KNOWLEDGE_ROUND_LIMIT,
    PROBE_SQL_LIMIT,
    UNCOUNTED_TOOLS,
    tool_calls_advance_round,
)


@dataclass(frozen=True)
class LoopBudget:
    execution_rounds: int
    execution_limit: int
    knowledge_rounds: int
    knowledge_limit: int
    probe_sql_calls: int
    probe_sql_limit: int
    stop_reason: str = ""

    @property
    def execution_exhausted(self) -> bool:
        return bool(self.stop_reason) or self.execution_rounds >= self.execution_limit

    @property
    def knowledge_exhausted(self) -> bool:
        return (
            self.knowledge_limit > 0 and self.knowledge_rounds >= self.knowledge_limit
        )

    @property
    def exhausted(self) -> bool:
        return self.execution_exhausted


def budget_from_state(state: Mapping[str, Any], *, config: Any = None) -> LoopBudget:
    execution_limit = int(state.get("tool_round_limit") or EXECUTION_ROUND_LIMIT)
    knowledge_limit = KNOWLEDGE_ROUND_LIMIT
    probe_limit = PROBE_SQL_LIMIT
    if config is not None and hasattr(config, "param"):
        execution_limit = int(
            config.param("execution_round_limit", execution_limit) or execution_limit
        )
        knowledge_limit = int(
            config.param("search_wiki_round_limit", knowledge_limit) or knowledge_limit
        )
        probe_limit = int(config.param("probe_sql_limit", probe_limit) or probe_limit)
    plane = (
        state.get("knowledge_plane")
        if isinstance(state.get("knowledge_plane"), Mapping)
        else {}
    )
    return LoopBudget(
        execution_rounds=int(state.get("tool_rounds") or 0),
        execution_limit=execution_limit,
        knowledge_rounds=int((plane or {}).get("knowledge_rounds") or 0),
        knowledge_limit=knowledge_limit,
        probe_sql_calls=int(state.get("probe_sql_calls") or 0),
        probe_sql_limit=probe_limit,
        stop_reason=str(state.get("tool_stop_reason") or ""),
    )


def calls_count_as_execution(calls: Sequence[Mapping[str, Any]]) -> bool:
    return tool_calls_advance_round(calls)


def is_uncounted_tool(name: str) -> bool:
    return str(name or "") in UNCOUNTED_TOOLS
