"""Explicit six-slot loop budget. All counters update in Product execute_tools."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from apps.chat.agent_knowledge import (
    EXECUTION_ROUND_LIMIT,
    KNOWLEDGE_ROUND_LIMIT,
    PROBE_SQL_LIMIT,
    UNCOUNTED_TOOLS,
    tool_calls_advance_round,
)

TOOL_CALL_LIMIT = 24
CLARIFY_LIMIT = 2
CONTEXT_TOKEN_LIMIT = 48000


class BudgetSlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    used: int = 0
    max: int = 0

    @property
    def remaining(self) -> int:
        if self.max <= 0:
            return 0
        return max(0, self.max - self.used)

    @property
    def exhausted(self) -> bool:
        return self.max > 0 and self.used >= self.max


class LoopBudget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exec_rounds: BudgetSlot = Field(default_factory=BudgetSlot)
    knowledge_rounds: BudgetSlot = Field(default_factory=BudgetSlot)
    probe_calls: BudgetSlot = Field(default_factory=BudgetSlot)
    tool_calls: BudgetSlot = Field(default_factory=BudgetSlot)
    clarify_count: BudgetSlot = Field(default_factory=BudgetSlot)
    context_tokens: BudgetSlot = Field(default_factory=BudgetSlot)
    stop_reason: str = ""

    @property
    def execution_exhausted(self) -> bool:
        return bool(self.stop_reason) or self.exec_rounds.exhausted

    @property
    def knowledge_exhausted(self) -> bool:
        return self.knowledge_rounds.exhausted

    @property
    def probe_exhausted(self) -> bool:
        return self.probe_calls.exhausted

    @property
    def clarify_exhausted(self) -> bool:
        return self.clarify_count.exhausted

    @property
    def exhausted(self) -> bool:
        return (
            bool(self.stop_reason)
            or self.exec_rounds.exhausted
            or self.tool_calls.exhausted
            or self.context_tokens.exhausted
        )

    def render_brief(self) -> str:
        parts = [
            f"exec {self.exec_rounds.used}/{self.exec_rounds.max}",
            f"knowledge {self.knowledge_rounds.used}/{self.knowledge_rounds.max}",
            f"probe {self.probe_calls.used}/{self.probe_calls.max}",
            f"tools {self.tool_calls.used}/{self.tool_calls.max}",
            f"clarify {self.clarify_count.used}/{self.clarify_count.max}",
        ]
        if self.exhausted:
            parts.append("工具已关闭，请基于已有信息作答")
        return "预算：" + " · ".join(parts)


def _slot(used: int, maximum: int) -> BudgetSlot:
    return BudgetSlot(used=max(0, int(used)), max=max(0, int(maximum)))


def _apply_overrides(
    budget: LoopBudget, overrides: Mapping[str, int] | None
) -> LoopBudget:
    if not overrides:
        return budget
    mapping = {
        "execution_round_limit": budget.exec_rounds,
        "probe_sql_limit": budget.probe_calls,
        "search_wiki_round_limit": budget.knowledge_rounds,
        "tool_call_limit": budget.tool_calls,
        "clarify_limit": budget.clarify_count,
        "context_token_limit": budget.context_tokens,
    }
    for key, slot in mapping.items():
        if key in overrides:
            slot.max = max(0, int(overrides[key]))
    return budget


def empty_budget(
    *, config: Any = None, overrides: Mapping[str, int] | None = None
) -> LoopBudget:
    return _apply_overrides(_limits(LoopBudget(), config=config), overrides)


def _limits(budget: LoopBudget, *, config: Any = None) -> LoopBudget:
    exec_max = EXECUTION_ROUND_LIMIT
    knowledge_max = KNOWLEDGE_ROUND_LIMIT
    probe_max = PROBE_SQL_LIMIT
    tool_max = TOOL_CALL_LIMIT
    clarify_max = CLARIFY_LIMIT
    token_max = CONTEXT_TOKEN_LIMIT
    if config is not None and hasattr(config, "param"):
        exec_max = int(config.param("execution_round_limit", exec_max) or exec_max)
        knowledge_max = int(
            config.param("search_wiki_round_limit", knowledge_max) or knowledge_max
        )
        probe_max = int(config.param("probe_sql_limit", probe_max) or probe_max)
        tool_max = int(config.param("tool_call_limit", tool_max) or tool_max)
        clarify_max = int(config.param("clarify_limit", clarify_max) or clarify_max)
        token_max = int(
            config.param("context_token_limit", token_max) or token_max
        )
    budget.exec_rounds.max = exec_max
    budget.knowledge_rounds.max = knowledge_max
    budget.probe_calls.max = probe_max
    budget.tool_calls.max = tool_max
    budget.clarify_count.max = clarify_max
    budget.context_tokens.max = token_max
    return budget


def budget_from_state(state: Mapping[str, Any], *, config: Any = None) -> LoopBudget:
    raw_overrides = state.get("loop_param_overrides")
    overrides = raw_overrides if isinstance(raw_overrides, Mapping) else None
    raw = state.get("loop_budget")
    if isinstance(raw, Mapping):
        try:
            budget = LoopBudget.model_validate(raw)
            budget = _limits(budget, config=config)
            if state.get("tool_stop_reason") and not budget.stop_reason:
                budget.stop_reason = str(state.get("tool_stop_reason") or "")
            return _apply_overrides(budget, overrides)
        except Exception:
            pass
    plane = (
        state.get("knowledge_plane")
        if isinstance(state.get("knowledge_plane"), Mapping)
        else {}
    )
    budget = LoopBudget(
        exec_rounds=_slot(int(state.get("tool_rounds") or 0), EXECUTION_ROUND_LIMIT),
        knowledge_rounds=_slot(
            int((plane or {}).get("knowledge_rounds") or 0), KNOWLEDGE_ROUND_LIMIT
        ),
        probe_calls=_slot(0, PROBE_SQL_LIMIT),
        tool_calls=_slot(0, TOOL_CALL_LIMIT),
        clarify_count=_slot(0, CLARIFY_LIMIT),
        context_tokens=_slot(
            int(state.get("context_tokens") or 0), CONTEXT_TOKEN_LIMIT
        ),
        stop_reason=str(state.get("tool_stop_reason") or ""),
    )
    return _apply_overrides(_limits(budget, config=config), overrides)


def calls_count_as_execution(calls: Sequence[Mapping[str, Any]]) -> bool:
    return tool_calls_advance_round(calls)


def is_uncounted_tool(name: str) -> bool:
    return str(name or "") in UNCOUNTED_TOOLS
