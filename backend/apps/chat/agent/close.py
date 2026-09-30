"""Single close-plane for a chat turn.

Delivery truth is ``SqlWorkspace.delivered``. Narration is the model's stop
text (``final_text``). Interrupt flags come from this-batch
``ToolOutcome.signals``. Graph routers read ``compute_verdict``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from apps.chat.agent.budget import budget_from_state
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.tools.contract import Signals, ToolOutcome, step_outcome

CloseKind = Literal["artifacts", "text", "empty", "error"]
VerdictPhase = Literal["after_loop", "after_tools"]


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    reason: str
    phase: VerdictPhase


def workspace_from_state(state: Mapping[str, Any]) -> SqlWorkspace:
    return SqlWorkspace.from_state(state)


def has_turn_result(
    state: Mapping[str, Any], messages: Sequence[Any] | None = None
) -> bool:
    """True when this turn sealed a delivery revision."""
    del messages
    return bool(workspace_from_state(state).delivered)


def batch_signals(state: Mapping[str, Any]) -> Signals:
    raw = state.get("batch_signals")
    if isinstance(raw, Mapping):
        try:
            return Signals.model_validate(raw)
        except Exception:
            pass
    acc = Signals()
    for step in state.get("tool_steps") or []:
        if not isinstance(step, Mapping) or step.get("superseded"):
            continue
        outcome = step_outcome(step)
        if outcome.signals.interrupt:
            acc = acc.model_copy(update={"interrupt": True})
        if outcome.signals.terminal:
            acc = acc.model_copy(
                update={
                    "terminal": True,
                    "dataset_id": outcome.signals.dataset_id or acc.dataset_id,
                }
            )
    return acc


def terminal_text(state: Mapping[str, Any]) -> str:
    for step in reversed(list(state.get("tool_steps") or [])):
        if not isinstance(step, Mapping) or step.get("superseded"):
            continue
        outcome = step_outcome(step)
        if not outcome.ok or not outcome.signals.terminal:
            continue
        payload = outcome.payload if isinstance(outcome.payload, Mapping) else {}
        text = str(payload.get("content") or "").strip()
        if text:
            return text
    return ""


def close_kind(state: Mapping[str, Any], *, has_cards: bool) -> CloseKind:
    """Classify how this turn should close. One function, four outcomes.

    Stop text is always a valid narration. Cards exist only when this turn
    sealed ``SqlWorkspace.delivered``. Relation / task_kind do not pick a
    second close protocol.
    """
    ws = workspace_from_state(state)
    if has_cards or ws.delivered:
        return "artifacts"
    if state.get("error"):
        return "error"
    text = str(state.get("final_text") or "").strip() or terminal_text(state)
    if text:
        return "text"
    return "empty"


def compute_verdict(state: Mapping[str, Any], *, phase: VerdictPhase) -> Verdict:
    """Single graph-router decision. YAML edges still name the actions."""
    ws = workspace_from_state(state)
    signals = batch_signals(state)
    budget = budget_from_state(state)
    if phase == "after_loop":
        if state.get("error"):
            if ws.delivered or state.get("analysis_incomplete"):
                return Verdict(
                    action="finalize_turn",
                    reason="salvage",
                    phase=phase,
                )
            return Verdict(action="fail", reason="error", phase=phase)
        if _pending_tool_calls(state):
            if budget.exhausted:
                return Verdict(
                    action="finalize_turn",
                    reason="budget_exhausted",
                    phase=phase,
                )
            return Verdict(action="execute_tools", reason="tool_calls", phase=phase)
        if state.get("loop_continue") and not budget.exhausted:
            return Verdict(action="agent_loop", reason="evidence_nudge", phase=phase)
        return Verdict(action="finalize_turn", reason="model_stop", phase=phase)
    if state.get("error"):
        return Verdict(action="fail", reason="tool_error", phase=phase)
    if signals.interrupt:
        return Verdict(action="await_clarification", reason="interrupt", phase=phase)
    if signals.terminal:
        return Verdict(action="finalize_turn", reason="text_exit", phase=phase)
    if budget.exhausted:
        return Verdict(action="finalize_turn", reason="budget_exhausted", phase=phase)
    return Verdict(action="agent_loop", reason="continue", phase=phase)


def apply_outcome_to_workspace(
    workspace: SqlWorkspace,
    *,
    name: str,
    args: Mapping[str, Any],
    outcome: ToolOutcome,
    ds_id: int | None = None,
    dialect: str | None = None,
) -> tuple[SqlWorkspace, ToolOutcome]:
    """Fold one chat-tool outcome into the SQL workspace. Tools stay ref-pure."""
    if not outcome.ok or outcome.signals.skipped:
        return workspace, outcome
    payload = outcome.payload if isinstance(outcome.payload, Mapping) else {}
    purpose = outcome.signals.purpose
    if name == "execute_sql_sandbox":
        sql = str(payload.get("sql") or "").strip()
        sql_ref = str(args.get("sql_ref") or "").strip()
        dataset_id = str(payload.get("dataset_id") or "") or None
        fields = [str(item) for item in (payload.get("fields") or [])]
        row_count = payload.get("row_count")
        if not isinstance(row_count, int):
            row_count = payload.get("total_rows")
        title = str(payload.get("result_title") or "")
        truncated = bool(payload.get("truncated"))
        raw_limit = payload.get("limit")
        if raw_limit is None and truncated:
            raw_limit = payload.get("row_count") or payload.get("total_rows")
        try:
            display_limit = int(raw_limit) if raw_limit is not None else None
        except (TypeError, ValueError):
            display_limit = None
        if not truncated:
            display_limit = None
        if sql_ref:
            existing = workspace.resolve(sql_ref)
            if existing is not None:
                marked = workspace.mark_executed(
                    existing.rev,
                    dataset_id=dataset_id,
                    row_count=row_count if isinstance(row_count, int) else None,
                    fields=fields,
                    result_title=title,
                    purpose=purpose,
                    truncated=truncated,
                    display_limit=display_limit,
                )
                if marked is not None:
                    outcome = outcome.model_copy(
                        update={
                            "signals": outcome.signals.model_copy(
                                update={
                                    "sql_rev": marked.rev,
                                    "dataset_id": marked.dataset_id,
                                }
                            )
                        }
                    )
                return workspace, outcome
        if sql:
            item = workspace.add_revision(
                sql,
                origin="model",
                status="executed",
                dataset_id=dataset_id,
                ds_id=ds_id,
                result_title=title,
                row_count=row_count if isinstance(row_count, int) else None,
                fields=fields,
                truncated=truncated,
                display_limit=display_limit,
                dialect=dialect,
            )
            marked = workspace.mark_executed(
                item.rev,
                dataset_id=dataset_id,
                row_count=row_count if isinstance(row_count, int) else None,
                fields=fields,
                result_title=title,
                purpose=purpose,
                truncated=truncated,
                display_limit=display_limit,
            )
            rev = marked.rev if marked is not None else item.rev
            outcome = outcome.model_copy(
                update={
                    "signals": outcome.signals.model_copy(
                        update={"sql_rev": rev, "dataset_id": dataset_id}
                    )
                }
            )
        return workspace, outcome
    if name == "patch_and_compile_sql":
        new_sql = str(payload.get("sql") or "").strip()
        if new_sql:
            item = workspace.apply_patch(
                str(args.get("sql_ref") or "active"),
                new_sql,
                ds_id=ds_id,
                dialect=dialect,
            )
            outcome = outcome.model_copy(
                update={
                    "signals": outcome.signals.model_copy(update={"sql_rev": item.rev})
                }
            )
        return workspace, outcome
    return workspace, outcome


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
