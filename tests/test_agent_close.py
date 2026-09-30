"""Close-plane: one delivery bit, one assembler, four close kinds."""

from __future__ import annotations

from apps.chat.agent.close import (
    TurnDelivery,
    clear_interrupt,
    close_kind,
    compute_verdict,
    delivery_from_state,
    empty_delivery,
    has_turn_result,
    observe_delivery,
    stamp_delivery,
)
from apps.chat.agent.delivery import close_turn, fail_node, finalize_agent_turn_node
from apps.chat.agent.tools.effect import ToolSignals


def test_fail_and_finalize_are_close_turn() -> None:
    assert fail_node is close_turn
    assert finalize_agent_turn_node is close_turn


def test_sealed_bit_is_the_read_path() -> None:
    sealed = {
        "turn_delivery": TurnDelivery(has_artifacts=True, dataset_id="d1").model_dump(),
        "tool_steps": [],
    }
    assert has_turn_result(sealed) is True
    assert delivery_from_state(sealed).dataset_id == "d1"


def test_sealed_empty_does_not_rescan_steps() -> None:
    state = {
        "turn_delivery": empty_delivery(),
        "tool_steps": [
            {
                "ok": True,
                "tool": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {"sql": "SELECT 1", "dataset_id": "ds1", "required": True},
                },
            }
        ],
    }
    assert has_turn_result(state) is False


def test_observe_from_steps_when_unsealed() -> None:
    state = {
        "tool_steps": [
            {
                "ok": True,
                "tool": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {"sql": "SELECT 1", "dataset_id": "ds1", "required": True},
                },
            }
        ]
    }
    seen = observe_delivery(state)
    assert seen.has_artifacts is True
    assert seen.dataset_id == "ds1"


def test_stamp_is_monotonic() -> None:
    acc = TurnDelivery()
    acc = stamp_delivery(
        acc,
        result={"ok": True, "data": {"terminal_answer": True, "content": "能力说明"}},
        signals=ToolSignals(terminal_text=True),
    )
    acc = stamp_delivery(
        acc,
        result={"ok": True, "data": {"sql": "SELECT 1", "dataset_id": "d1"}},
        signals=ToolSignals(dataset_id="d1", required=True),
    )
    assert acc.has_artifacts is True
    assert acc.text_only is True
    assert acc.text == "能力说明"


def test_close_kind_four_outcomes() -> None:
    assert (
        close_kind(
            {
                "turn_delivery": TurnDelivery(has_artifacts=True).model_dump(),
                "error": "llm down",
            },
            has_cards=False,
        )
        == "artifacts"
    )
    assert (
        close_kind(
            {"turn_delivery": TurnDelivery(text_only=True, text="办不到").model_dump()},
            has_cards=False,
        )
        == "text"
    )
    assert (
        close_kind({"turn_route": {"task_kind": "query"}}, has_cards=False) == "empty"
    )
    assert close_kind({"error": "boom"}, has_cards=False) == "error"


def test_stamp_interrupt_is_clearable() -> None:
    acc = stamp_delivery(
        TurnDelivery(),
        result={"ok": True, "data": {"interrupt_required": True}},
        signals=ToolSignals(interrupt=True),
    )
    assert acc.interrupt is True
    assert clear_interrupt(acc).interrupt is False
    assert clear_interrupt(acc).has_artifacts is False


def test_compute_verdict_after_tools_reads_close_plane_not_step_scan() -> None:
    sealed = {
        "turn_delivery": TurnDelivery(interrupt=True).model_dump(),
        "tool_steps": [],
    }
    assert compute_verdict(sealed, phase="after_tools").action == "await_clarification"
    resumed = {
        "turn_delivery": TurnDelivery(interrupt=False, has_artifacts=True).model_dump(),
        "tool_steps": [
            {
                "ok": True,
                "superseded": True,
                "result": {"ok": True, "data": {"interrupt_required": True}},
            }
        ],
    }
    assert compute_verdict(resumed, phase="after_tools").action == "agent_loop"


def test_compute_verdict_after_loop_salvage_and_tool_calls() -> None:
    from langchain_core.messages import AIMessage

    assert (
        compute_verdict(
            {
                "error": "llm down",
                "turn_delivery": TurnDelivery(has_artifacts=True).model_dump(),
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
    exhausted = {
        **calling,
        "tool_rounds": 5,
        "tool_round_limit": 5,
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
            "data": {"sql": "SELECT 1", "required": True, "dataset_id": "x"},
        },
    )
    assert has_turn_result({"tool_steps": []}, [message]) is False
