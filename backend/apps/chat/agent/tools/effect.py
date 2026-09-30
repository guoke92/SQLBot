"""Typed control-plane signals extracted from tool results."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict

from apps.chat.agent_config.defaults import DEFAULT_PARALLEL_SAFE
from apps.chat.agent_knowledge import KNOWLEDGE_TOOLS


class ToolSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interrupt: bool = False
    terminal_text: bool = False
    dataset_id: str | None = None
    sql_ref: str | None = None
    exclusive: bool = False
    required: bool = True
    parallel_safe: bool = False


def signals_from_result(name: str, result: Mapping[str, Any]) -> ToolSignals:
    data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
    if not isinstance(data, Mapping):
        data = {}
    dataset_id = str(data.get("dataset_id") or "").strip() or None
    sql = str(data.get("sql") or "").strip()
    tool = str(name or "")
    return ToolSignals(
        interrupt=bool(
            data.get("interrupt_required") or data.get("clarification_card")
        ),
        terminal_text=bool(data.get("terminal_answer")),
        dataset_id=dataset_id,
        sql_ref=dataset_id or (sql or None),
        exclusive=tool not in DEFAULT_PARALLEL_SAFE,
        required=data.get("required") is not False,
        parallel_safe=tool in DEFAULT_PARALLEL_SAFE or tool in KNOWLEDGE_TOOLS,
    )


def step_signals(step: Mapping[str, Any]) -> ToolSignals:
    stored = step.get("signals")
    if isinstance(stored, Mapping):
        try:
            return ToolSignals.model_validate(stored)
        except Exception:
            pass
    result = step.get("result") if isinstance(step.get("result"), Mapping) else {}
    name = str(step.get("tool") or step.get("name") or "")
    return signals_from_result(name, result if isinstance(result, Mapping) else {})
