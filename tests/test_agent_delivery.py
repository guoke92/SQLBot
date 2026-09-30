"""Delivery predicate is the single source of 'this turn has a publishable SQL'."""

from __future__ import annotations

from apps.chat.agent.delivery import has_turn_result
from apps.chat.agent.loop import route_after_agent_loop, route_after_tools_execution


def test_has_turn_result_from_required_sql_step() -> None:
    state = {
        "tool_steps": [
            {
                "ok": True,
                "tool": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {
                        "sql": "SELECT 1",
                        "dataset_id": "ds1",
                        "required": True,
                    },
                },
            }
        ]
    }
    assert has_turn_result(state) is True


def test_has_turn_result_ignores_probe_sql() -> None:
    state = {
        "tool_steps": [
            {
                "ok": True,
                "tool": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {
                        "sql": "SELECT 1",
                        "dataset_id": "probe",
                        "required": False,
                    },
                },
            }
        ]
    }
    assert has_turn_result(state) is False


def test_loop_error_routes_to_finalize_when_turn_has_result() -> None:
    state = {
        "error": "llm down",
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
        "messages": [],
    }
    assert route_after_agent_loop(state) == "finalize_turn"


def test_route_after_tools_reads_signals_interrupt() -> None:
    state = {
        "tool_steps": [
            {
                "ok": True,
                "tool": "request_clarification",
                "signals": {
                    "interrupt": True,
                    "terminal_text": False,
                    "dataset_id": None,
                    "sql_ref": None,
                    "exclusive": True,
                    "required": True,
                    "parallel_safe": False,
                },
                "result": {"ok": True, "data": {}},
            }
        ]
    }
    assert route_after_tools_execution(state) == "await_clarification"


def test_fail_and_finalize_are_the_same_close_turn() -> None:
    from apps.chat.agent import delivery

    assert delivery.fail_node is delivery.close_turn
    assert delivery.finalize_agent_turn_node is delivery.close_turn
