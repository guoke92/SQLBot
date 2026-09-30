"""Typed tool outcome: control-plane signals plus a data-plane payload.

Chat tools return ``ToolOutcome``. Control flags never live in ``payload``.
Host/config tools still return the generic ``ToolResult`` mapping.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from apps.chat.agent_config.defaults import DEFAULT_PARALLEL_SAFE
from apps.chat.agent_knowledge import KNOWLEDGE_TOOLS
from apps.conversation.outcome import classify_failure

Purpose = Literal["probe", "delivery"]


class Signals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interrupt: bool = False
    terminal: bool = False
    skipped: bool = False
    purpose: Purpose = "delivery"
    dataset_id: str | None = None
    sql_rev: str | None = None
    exclusive: bool = False
    parallel_safe: bool = False


class ToolOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    summary: str
    payload: Any = None
    signals: Signals = Field(default_factory=Signals)
    error: str | None = None
    failure: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


def signals_for_tool(name: str, **overrides: Any) -> Signals:
    tool = str(name or "")
    return Signals(
        exclusive=tool not in DEFAULT_PARALLEL_SAFE,
        parallel_safe=tool in DEFAULT_PARALLEL_SAFE or tool in KNOWLEDGE_TOOLS,
        **overrides,
    )


def success_outcome(
    summary: str,
    payload: Any = None,
    *,
    signals: Signals | None = None,
    name: str = "",
) -> dict[str, Any]:
    base = signals if signals is not None else signals_for_tool(name)
    return ToolOutcome(
        ok=True,
        summary=summary,
        payload=payload,
        signals=base,
        error=None,
        failure=None,
    ).as_dict()


def failure_outcome(
    error: str,
    *,
    failure: dict[str, Any] | None = None,
    payload: Any = None,
    signals: Signals | None = None,
    name: str = "",
    retryable: bool | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    info: dict[str, Any] = dict(failure or classify_failure(error))
    if retryable is not None:
        info = {**info, "retryable": bool(retryable)}
    base = signals if signals is not None else signals_for_tool(name)
    return ToolOutcome(
        ok=False,
        summary=summary or error,
        payload=payload,
        signals=base,
        error=error,
        failure=info,
    ).as_dict()


def skipped_outcome(summary: str, *, reason: str, name: str = "") -> dict[str, Any]:
    return ToolOutcome(
        ok=True,
        summary=summary,
        payload={"reason": reason},
        signals=signals_for_tool(name, skipped=True),
        error=None,
        failure=None,
    ).as_dict()


def parse_tool_outcome(raw: Any, *, name: str = "") -> ToolOutcome:
    """Accept a ``ToolOutcome`` mapping. Reject Host ``ToolResult`` envelopes."""
    if isinstance(raw, ToolOutcome):
        return raw
    if not isinstance(raw, Mapping):
        raise TypeError("Tool must return a ToolOutcome mapping")
    if "signals" not in raw or "payload" not in raw:
        raise TypeError(
            "ToolOutcome requires 'signals' and 'payload'; "
            "control flags must not live in a ToolResult.data bag"
        )
    outcome = ToolOutcome.model_validate(dict(raw))
    if not outcome.signals.exclusive and not outcome.signals.parallel_safe:
        filled = signals_for_tool(name)
        outcome = outcome.model_copy(
            update={
                "signals": outcome.signals.model_copy(
                    update={
                        "exclusive": filled.exclusive,
                        "parallel_safe": filled.parallel_safe,
                    }
                )
            }
        )
    return outcome


def outcome_payload(result: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Data plane of an Outcome, or Host ``data`` for generic tools."""
    if not isinstance(result, Mapping):
        return {}
    payload = result.get("payload")
    if isinstance(payload, Mapping):
        return payload
    data = result.get("data")
    if isinstance(data, Mapping):
        return data
    return {}


def step_outcome(step: Mapping[str, Any]) -> ToolOutcome:
    stored = step.get("outcome")
    if isinstance(stored, Mapping):
        try:
            return ToolOutcome.model_validate(stored)
        except Exception:
            pass
    result = step.get("result") if isinstance(step.get("result"), Mapping) else {}
    name = str(step.get("tool") or step.get("name") or "")
    if isinstance(result, Mapping) and "signals" in result:
        try:
            return parse_tool_outcome(result, name=name)
        except Exception:
            pass
    return ToolOutcome(
        ok=bool(step.get("ok")),
        summary=str(step.get("error") or ""),
        payload=None,
        signals=Signals(),
        error=str(step.get("error") or "") or None,
        failure=step.get("failure") if isinstance(step.get("failure"), Mapping) else None,
    )


def wrap_tool_result(raw: Mapping[str, Any], *, name: str) -> dict[str, Any]:
    """Lift a Host-style ToolResult into ToolOutcome at the chat registry boundary."""
    from apps.conversation.tooling import normalize_tool_result

    result = normalize_tool_result(raw)
    if result["ok"]:
        return success_outcome(
            result["summary"],
            payload=result["data"],
            name=name,
        )
    return failure_outcome(
        str(result["error"] or result["summary"]),
        failure=result["failure"],
        payload=result["data"],
        name=name,
        summary=result["summary"],
    )
