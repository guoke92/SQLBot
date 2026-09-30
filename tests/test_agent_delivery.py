"""Delivery predicate is workspace.delivered; routers read compute_verdict."""

from __future__ import annotations

from apps.chat.agent.close import has_turn_result
from apps.chat.agent.loop import route_after_agent_loop, route_after_tools_execution
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.tools.contract import Signals, ToolOutcome


def _delivered_state() -> dict:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT 1", status="executed", dataset_id="ds1")
    ws.mark_executed(item.rev, dataset_id="ds1", purpose="delivery")
    return {"sql_workspace": ws.model_dump(mode="json")}


def test_has_turn_result_from_workspace() -> None:
    assert has_turn_result(_delivered_state()) is True


def test_has_turn_result_ignores_probe_sql() -> None:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT 1", status="executed", dataset_id="probe")
    ws.mark_executed(item.rev, dataset_id="probe", purpose="probe")
    assert has_turn_result({"sql_workspace": ws.model_dump(mode="json")}) is False


def test_loop_error_routes_to_finalize_when_turn_has_result() -> None:
    state = {**_delivered_state(), "error": "llm down", "messages": []}
    assert route_after_agent_loop(state) == "finalize_turn"


def test_route_after_tools_reads_signals_interrupt() -> None:
    state = {
        "batch_signals": Signals(interrupt=True).model_dump(mode="json"),
        "tool_steps": [
            {
                "ok": True,
                "tool": "request_clarification",
                "outcome": ToolOutcome(
                    ok=True,
                    summary="card",
                    payload={},
                    signals=Signals(interrupt=True),
                ).model_dump(mode="json"),
            }
        ],
    }
    assert route_after_tools_execution(state) == "await_clarification"


def test_fail_and_finalize_are_the_same_close_turn() -> None:
    from apps.chat.agent import delivery

    assert delivery.fail_node is delivery.close_turn
    assert delivery.finalize_agent_turn_node is delivery.close_turn
