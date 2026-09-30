"""Close-plane: workspace delivery, batch signals, single verdict."""

from __future__ import annotations

from apps.chat.agent.close import (
    close_kind,
    compute_verdict,
    has_turn_result,
    workspace_from_state,
)
from apps.chat.agent.delivery import close_turn, fail_node, finalize_agent_turn_node
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.tools.contract import Signals, ToolOutcome


def test_fail_and_finalize_are_close_turn() -> None:
    assert fail_node is close_turn
    assert finalize_agent_turn_node is close_turn


def test_has_turn_result_reads_workspace_delivered() -> None:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT 1", origin="model", status="executed", dataset_id="d1")
    ws.mark_executed(item.rev, dataset_id="d1", purpose="delivery")
    state = {"sql_workspace": ws.model_dump(mode="json")}
    assert has_turn_result(state) is True
    assert workspace_from_state(state).delivered == item.rev


def test_empty_workspace_is_not_delivered() -> None:
    assert has_turn_result({"sql_workspace": SqlWorkspace().model_dump(mode="json")}) is False
    assert has_turn_result({"tool_steps": []}) is False


def test_probe_revision_is_not_delivery() -> None:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT 1", origin="model", status="executed", dataset_id="p")
    ws.mark_executed(item.rev, dataset_id="p", purpose="probe")
    assert has_turn_result({"sql_workspace": ws.model_dump(mode="json")}) is False


def test_close_kind_four_outcomes() -> None:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT 1", status="executed", dataset_id="d1")
    ws.mark_executed(item.rev, dataset_id="d1", purpose="delivery")
    assert (
        close_kind(
            {"sql_workspace": ws.model_dump(mode="json"), "error": "llm down"},
            has_cards=False,
        )
        == "artifacts"
    )
    assert (
        close_kind(
            {
                "final_text": "办不到",
                "turn_route": {"task_kind": "query", "relation": "continue"},
            },
            has_cards=False,
        )
        == "text"
    )
    assert (
        close_kind(
            {
                "final_text": "我可以帮你查数。",
                "turn_route": {"task_kind": "query", "relation": "independent"},
            },
            has_cards=False,
        )
        == "text"
    )
    assert (
        close_kind({"turn_route": {"task_kind": "query"}}, has_cards=False) == "empty"
    )
    assert (
        close_kind({"turn_route": {"task_kind": "analysis"}}, has_cards=False) == "empty"
    )
    assert close_kind({"error": "boom"}, has_cards=False) == "error"


def test_compute_verdict_after_tools_reads_batch_signals() -> None:
    assert (
        compute_verdict(
            {"batch_signals": Signals(interrupt=True).model_dump(mode="json")},
            phase="after_tools",
        ).action
        == "await_clarification"
    )
    resumed = {
        "batch_signals": Signals().model_dump(mode="json"),
        "sql_workspace": SqlWorkspace().model_dump(mode="json"),
        "tool_steps": [
            {
                "ok": True,
                "superseded": True,
                "outcome": ToolOutcome(
                    ok=True,
                    summary="card",
                    payload={},
                    signals=Signals(interrupt=True),
                ).model_dump(mode="json"),
            }
        ],
    }
    assert compute_verdict(resumed, phase="after_tools").action == "agent_loop"


def test_compute_verdict_after_loop_salvage_and_tool_calls() -> None:
    from langchain_core.messages import AIMessage

    ws = SqlWorkspace()
    item = ws.add_revision("SELECT 1", status="executed", dataset_id="d1")
    ws.mark_executed(item.rev, dataset_id="d1", purpose="delivery")
    assert (
        compute_verdict(
            {
                "error": "llm down",
                "sql_workspace": ws.model_dump(mode="json"),
            },
            phase="after_loop",
        ).action
        == "finalize_turn"
    )
    assert compute_verdict({"error": "llm down"}, phase="after_loop").action == "fail"
    calling = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": "get_table_schema", "args": {}, "id": "c1"}],
            )
        ]
    }
    assert compute_verdict(calling, phase="after_loop").action == "execute_tools"
    from apps.chat.agent.budget import LoopBudget, BudgetSlot

    exhausted = {
        **calling,
        "loop_budget": LoopBudget(
            exec_rounds=BudgetSlot(used=5, max=5),
            knowledge_rounds=BudgetSlot(used=0, max=4),
            probe_calls=BudgetSlot(used=0, max=2),
            tool_calls=BudgetSlot(used=0, max=24),
            clarify_count=BudgetSlot(used=0, max=2),
            context_tokens=BudgetSlot(used=0, max=48000),
        ).model_dump(mode="json"),
    }
    assert compute_verdict(exhausted, phase="after_loop").action == "finalize_turn"


def test_compute_verdict_loop_continue_reenters_agent_loop() -> None:
    from langchain_core.messages import AIMessage

    from apps.chat.agent.loop import route_after_agent_loop

    state = {
        "loop_continue": True,
        "messages": [AIMessage(content="draft report")],
    }
    verdict = compute_verdict(state, phase="after_loop")
    assert verdict.action == "agent_loop"
    assert verdict.reason == "evidence_nudge"
    assert route_after_agent_loop(state) == "agent_loop"

    from apps.chat.agent.budget import BudgetSlot, LoopBudget

    exhausted = {
        **state,
        "loop_budget": LoopBudget(
            exec_rounds=BudgetSlot(used=8, max=8),
            knowledge_rounds=BudgetSlot(used=0, max=4),
            probe_calls=BudgetSlot(used=0, max=8),
            tool_calls=BudgetSlot(used=0, max=24),
            clarify_count=BudgetSlot(used=0, max=2),
            context_tokens=BudgetSlot(used=0, max=48000),
        ).model_dump(mode="json"),
    }
    assert compute_verdict(exhausted, phase="after_loop").action == "finalize_turn"


def test_messages_are_not_a_delivery_source() -> None:
    from langchain_core.messages import ToolMessage

    message = ToolMessage(
        content="ok",
        name="execute_sql_sandbox",
        tool_call_id="t1",
        artifact={
            "ok": True,
            "payload": {"sql": "SELECT 1", "dataset_id": "x"},
            "signals": Signals(purpose="delivery", dataset_id="x").model_dump(),
        },
    )
    assert has_turn_result({"tool_steps": []}, [message]) is False
