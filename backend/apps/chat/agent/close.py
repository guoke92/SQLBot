"""Single close-plane for a chat turn.

Coding agents emit one ``result`` when the loop stops. Data agents emit one
``Answer`` from the artifact store plus closing text. This module is that
joint: a serializable delivery bit written by tools, and a single derivation
when the bit has not been sealed yet.

Loop / tools / fail / finalize only read ``TurnDelivery``. Graph routers only
read ``compute_verdict``. They do not each invent a success or interrupt
predicate.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from apps.chat.agent.budget import budget_from_state
from apps.chat.agent.tools.effect import step_signals
from apps.chat.delivery import select_delivery_datasets
from apps.conversation.process_timeline import load_result_datasets
from apps.conversation.session import session_scope

CloseKind = Literal["artifacts", "text", "empty", "error"]
VerdictPhase = Literal["after_loop", "after_tools"]


class TurnDelivery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_artifacts: bool = False
    dataset_id: str | None = None
    text_only: bool = False
    text: str = ""
    interrupt: bool = False


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    reason: str
    phase: VerdictPhase


def empty_delivery() -> dict[str, Any]:
    return TurnDelivery().model_dump()


def delivery_from_state(state: Mapping[str, Any]) -> TurnDelivery:
    """Read the sealed bit when present; otherwise derive once from evidence."""
    raw = state.get("turn_delivery")
    if isinstance(raw, Mapping):
        try:
            return TurnDelivery.model_validate(raw)
        except Exception:
            pass
    return observe_delivery(state)


def has_turn_result(
    state: Mapping[str, Any], messages: Sequence[Any] | None = None
) -> bool:
    """True when this turn sealed a required SQL delivery.

    ``messages`` is accepted for call-site compatibility and ignored: transcript
    scrape is not a delivery source.
    """
    del messages
    return delivery_from_state(state).has_artifacts


def stamp_delivery(
    current: TurnDelivery,
    *,
    result: Mapping[str, Any],
    signals: Any,
) -> TurnDelivery:
    """Fold one tool outcome into the close-plane.

    Artifact/text bits only turn on. ``interrupt`` also turns on here; resume
    uses ``clear_interrupt``.
    """
    data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
    if not isinstance(data, Mapping):
        data = {}
    has_artifacts = current.has_artifacts
    dataset_id = current.dataset_id
    if bool(getattr(signals, "required", True)) and (
        getattr(signals, "dataset_id", None) or _required_sql_payload(data)
    ):
        has_artifacts = True
        dataset_id = str(getattr(signals, "dataset_id", None) or dataset_id or "") or (
            current.dataset_id
        )
    text = current.text
    text_only = current.text_only
    if getattr(signals, "terminal_text", False):
        text_only = True
        content = str(data.get("content") or "").strip()
        if content:
            text = content
    interrupt = current.interrupt or bool(getattr(signals, "interrupt", False))
    return TurnDelivery(
        has_artifacts=has_artifacts,
        dataset_id=dataset_id,
        text_only=text_only,
        text=text,
        interrupt=interrupt,
    )


def clear_interrupt(current: TurnDelivery) -> TurnDelivery:
    """Resume from clarification: keep artifacts/text, drop the pause bit."""
    return current.model_copy(update={"interrupt": False})


def observe_delivery(state: Mapping[str, Any]) -> TurnDelivery:
    """Derive delivery from tool_steps and persisted datasets. No message scrape."""
    acc = TurnDelivery()
    for step in state.get("tool_steps") or []:
        if not isinstance(step, Mapping):
            continue
        result = step.get("result") if isinstance(step.get("result"), Mapping) else {}
        acc = stamp_delivery(acc, result=result, signals=step_signals(step))
    if acc.has_artifacts:
        return acc
    run_id = str(state.get("run_id") or "")
    if not run_id:
        return acc
    try:
        with session_scope() as session:
            rows = load_result_datasets(session, run_id)
        delivered = select_delivery_datasets(rows)
    except Exception:
        return acc
    if not delivered:
        return acc
    last = delivered[-1]
    return TurnDelivery(
        has_artifacts=True,
        dataset_id=str(getattr(last, "dataset_id", "") or "") or None,
        text_only=acc.text_only,
        text=acc.text,
        interrupt=acc.interrupt,
    )


def close_kind(state: Mapping[str, Any], *, has_cards: bool) -> CloseKind:
    """Classify how this turn should close. One function, four outcomes."""
    delivery = delivery_from_state(state)
    if has_cards or delivery.has_artifacts:
        return "artifacts"
    if delivery.text_only or delivery.text:
        return "text"
    if state.get("error"):
        return "error"
    route = (
        state.get("turn_route") if isinstance(state.get("turn_route"), Mapping) else {}
    )
    if str(route.get("task_kind") or "query") == "query":
        return "empty"
    if str(state.get("final_text") or "").strip():
        return "text"
    return "error"


def compute_verdict(state: Mapping[str, Any], *, phase: VerdictPhase) -> Verdict:
    """Single graph-router decision. YAML edges still name the actions."""
    delivery = delivery_from_state(state)
    if phase == "after_loop":
        if state.get("error"):
            if delivery.has_artifacts or state.get("analysis_incomplete"):
                return Verdict(
                    action="finalize_turn",
                    reason="salvage",
                    phase=phase,
                )
            return Verdict(action="fail", reason="error", phase=phase)
        if _pending_tool_calls(state):
            budget = budget_from_state(state)
            if budget.exhausted:
                return Verdict(
                    action="finalize_turn",
                    reason="budget_exhausted",
                    phase=phase,
                )
            return Verdict(action="execute_tools", reason="tool_calls", phase=phase)
        return Verdict(action="finalize_turn", reason="model_stop", phase=phase)
    if state.get("error"):
        return Verdict(action="fail", reason="tool_error", phase=phase)
    if delivery.interrupt:
        return Verdict(action="await_clarification", reason="interrupt", phase=phase)
    if delivery.text_only:
        return Verdict(action="finalize_turn", reason="text_exit", phase=phase)
    return Verdict(action="agent_loop", reason="continue", phase=phase)


def _pending_tool_calls(state: Mapping[str, Any]) -> bool:
    from langchain_core.messages import AIMessage

    from apps.conversation.messages import deserialize_messages

    raw = list(state.get("messages") or [])
    if not raw:
        return False
    last = raw[-1]
    if not isinstance(last, AIMessage):
        try:
            messages = deserialize_messages(raw)
        except Exception:
            return False
        last = messages[-1] if messages else None
    return bool(isinstance(last, AIMessage) and getattr(last, "tool_calls", None))


def _required_sql_payload(data: Mapping[str, Any] | Any) -> bool:
    if not isinstance(data, Mapping) or not data.get("sql"):
        return False
    return data.get("required") is not False
