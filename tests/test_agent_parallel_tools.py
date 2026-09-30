"""Knowledge tools in one model round dispatch in parallel and merge the plane."""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from apps.chat.agent.knowledge import load_plane, stage_plane
from apps.chat.agent.tools.runtime import execute_tools_node
from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.chat.tools.contract import success_outcome
from apps.conversation.runtime_context import (
    attach_runtime,
    detach_runtime,
    worker_scope,
)


def test_parallel_knowledge_tools_merge_plane(monkeypatch) -> None:
    run_id = "run-parallel-knowledge"
    seen: list[str] = []
    lock = threading.Lock()

    def _make_tool(name: str, table: str) -> MagicMock:
        tool = MagicMock()
        tool.name = name

        def _invoke(_args: object) -> dict[str, object]:
            with lock:
                seen.append(name)
            time.sleep(0.05)
            plane = load_plane()
            plane.tables = list(dict.fromkeys([*(plane.tables or []), table]))
            stage_plane(plane)
            return success_outcome(name, payload={"tables": [table]}, name=name)

        tool.invoke.side_effect = _invoke
        return tool

    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.open_process_span", lambda **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.attach_process_span", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.attach_running_tool_span",
        lambda **_k: None,
    )

    schema = _make_tool("get_table_schema", "t_schema")
    wiki = _make_tool("search_knowledge", "t_wiki")
    ai = AIMessage(
        content="",
        tool_calls=[
            {"id": "c1", "name": "get_table_schema", "args": {"tables": ["t_schema"]}},
            {"id": "c2", "name": "search_knowledge", "args": {"query": "口径"}},
        ],
    )
    state = {
        "run_id": run_id,
        "record_id": 1,
        "messages": [ai],
        "bound_tools": [schema, wiki],
        "sink": "json",
        "knowledge_plane": AgentKnowledgePlane().to_dump(),
        "tool_steps": [],
    }
    with worker_scope(run_id, "tok"):
        attach_runtime(run_id, knowledge_plane=AgentKnowledgePlane().to_dump())
        try:
            next_state = execute_tools_node(state)
        finally:
            detach_runtime(run_id)

    plane = AgentKnowledgePlane.from_dump(next_state.get("knowledge_plane"))
    assert set(plane.tables) >= {"t_schema", "t_wiki"}
    assert {step.get("tool") for step in next_state["tool_steps"]} == {
        "get_table_schema",
        "search_knowledge",
    }
    assert all(step.get("signals") for step in next_state["tool_steps"])


def test_exclusive_tool_in_batch_runs_serially(monkeypatch) -> None:
    run_id = "run-serial-exclusive"
    order: list[str] = []

    def _make_tool(name: str) -> MagicMock:
        tool = MagicMock()
        tool.name = name

        def _invoke(_args: object) -> dict[str, object]:
            order.append(f"{name}:start")
            time.sleep(0.02)
            order.append(f"{name}:end")
            return success_outcome(name, payload={}, name=name)

        tool.invoke.side_effect = _invoke
        return tool

    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.open_process_span", lambda **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.attach_process_span", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.attach_running_tool_span",
        lambda **_k: None,
    )

    schema = _make_tool("get_table_schema")
    sql = _make_tool("execute_sql_sandbox")
    ai = AIMessage(
        content="",
        tool_calls=[
            {"id": "c1", "name": "get_table_schema", "args": {}},
            {"id": "c2", "name": "execute_sql_sandbox", "args": {"sql": "SELECT 1"}},
        ],
    )
    state = {
        "run_id": run_id,
        "messages": [ai],
        "bound_tools": [schema, sql],
        "sink": "json",
        "tool_steps": [],
    }
    with worker_scope(run_id, "tok"):
        attach_runtime(run_id)
        try:
            execute_tools_node(state)
        finally:
            detach_runtime(run_id)
    assert order == [
        "get_table_schema:start",
        "get_table_schema:end",
        "execute_sql_sandbox:start",
        "execute_sql_sandbox:end",
    ]
