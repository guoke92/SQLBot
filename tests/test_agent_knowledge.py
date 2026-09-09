"""AgentKnowledgePlane SSOT: merge, stubs, clarify budget, required-only delivery."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import (  # noqa: E402
    PROBE_SQL_LIMIT,
    AgentKnowledgePlane,
    strip_search_wiki_payload,
)
from apps.chat.graphs.nodes.agent_clarify import (  # noqa: E402
    await_agent_clarification_node,
)
from apps.chat.graphs.nodes.agent_finalize import (  # noqa: E402
    select_delivery_datasets,
)
from apps.chat.graphs.nodes.unified_agent import (  # noqa: E402
    _agent_has_sql_result,
)
from apps.chat.task.agent_prompt import build_agent_system_prompt  # noqa: E402
from apps.chat.tools.execute_sql import execute_sql_sandbox  # noqa: E402
from apps.conversation.messages import deserialize_messages  # noqa: E402
from apps.conversation.runtime_context import (  # noqa: E402
    attach_runtime,
    detach_runtime,
    worker_scope,
)
from apps.conversation.tooling import execute_tools_node  # noqa: E402


def test_plane_same_table_merge_does_not_grow() -> None:
    plane = AgentKnowledgePlane()
    blob = "## 任务 (d_task)\n(id:int, 主键)\n(name:text, 名称)"
    payload = {
        "knowledge_text": "任务表口径",
        "schema_text": blob,
        "tables": ["d_task"],
        "page_keys": ["d_task"],
        "backend": "wiki",
    }
    first_delta = plane.merge_recall(payload)
    first = plane.render_system_sections()
    second_delta = plane.merge_recall(payload)
    second = plane.render_system_sections()
    assert first_delta.unchanged is False
    assert second_delta.unchanged is True
    assert plane.has_new_coverage(second_delta) is False
    assert len(second) == len(first)
    assert second.count("# Table: d_task") == 0
    assert second.count("## 任务 (d_task)") == 1
    assert "<wiki_knowledge>" in first
    assert "<schema_catalog>" in first
    wiki_body = first.split("<wiki_knowledge>", 1)[1].split("</wiki_knowledge>", 1)[0]
    assert "# Table: d_task" not in wiki_body


def test_search_wiki_stub_and_unchanged_stop(monkeypatch) -> None:
    from apps.chat.tools import wiki_search as ws

    payload = {
        "knowledge_text": "# d_task\n任务表",
        "schema_text": "## 任务 (d_task)\n(id:int, 主键)\n(name:text, 名称)",
        "tables": ["d_task"],
        "page_keys": ["d_task"],
        "backend": "wiki",
        "hit_count": 1,
    }
    monkeypatch.setattr(ws, "retrieve_wiki_context", lambda *_a, **_k: payload)
    run_id = "wiki-stub"
    attach_runtime(run_id, knowledge_plane=AgentKnowledgePlane().to_dump())
    llm = SimpleNamespace(ds=SimpleNamespace(id=1))
    try:
        with worker_scope(run_id, "tok"):
            first = ws.search_wiki_knowledge(llm, "task")
            second = ws.search_wiki_knowledge(llm, "task")
    finally:
        detach_runtime(run_id)
    assert first["ok"] is True
    assert "knowledge_text" not in first["data"]
    assert "schema_text" not in first["data"]
    assert first["data"]["added_tables"] == ["d_task"]
    assert first["data"]["stop_search"] is False
    assert second["data"]["unchanged"] is True
    assert second["data"]["stop_search"] is True
    assert second["data"]["recall_status"] == "stagnant"


def test_execute_tools_strips_search_wiki_full_text(monkeypatch) -> None:
    fake_tool = MagicMock()
    fake_tool.name = "search_wiki"
    fake_tool.invoke.return_value = {
        "ok": True,
        "summary": "merged",
        "data": {
            "knowledge_text": "FULL_WIKI_BODY",
            "schema_text": "# Table: t1\nFULL_SCHEMA",
            "added_tables": ["t1"],
            "added_pages": ["p1"],
            "schema_ready": True,
            "stop_search": False,
            "recall_status": "hit",
            "unchanged": False,
            "backend": "wiki",
            "tables": ["t1"],
            "page_keys": ["p1"],
        },
        "error": None,
        "failure": None,
    }
    monkeypatch.setattr(
        "apps.conversation.tooling.open_process_span", lambda **_k: None
    )
    monkeypatch.setattr(
        "apps.conversation.tooling.attach_process_span", lambda *_a, **_k: None
    )
    state = {
        "run_id": "strip-wiki",
        "record_id": 1,
        "sink": "json",
        "messages": [
            SystemMessage(content="sys"),
            HumanMessage(content="q"),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "c1",
                        "name": "search_wiki",
                        "args": {"query": "t1"},
                    }
                ],
            ),
        ],
        "bound_tools": [fake_tool],
        "knowledge_plane": {},
        "memory_slots": {},
    }
    out = execute_tools_node(state)
    tool_payload = str(out["messages"][-1])
    assert "FULL_WIKI_BODY" not in tool_payload
    assert "FULL_SCHEMA" not in tool_payload
    data = out["tool_steps"][0]["result"]["data"]
    assert "knowledge_text" not in data
    assert data["added_tables"] == ["t1"]


def test_strip_search_wiki_payload_drops_full_text() -> None:
    cleaned = strip_search_wiki_payload(
        {
            "knowledge_text": "nope",
            "schema_text": "nope",
            "added_tables": ["t"],
            "schema_ready": True,
            "stop_search": True,
            "recall_status": "stagnant",
            "unchanged": True,
        }
    )
    assert "knowledge_text" not in cleaned
    assert cleaned["stop_search"] is True


def test_clarify_resume_resets_tool_rounds_and_refreshes_system(monkeypatch) -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "knowledge_text": "口径正文",
            "schema_text": "## 表 (t1)\n(id:int, 主键)",
            "tables": ["t1"],
            "page_keys": ["p1"],
        }
    )

    @contextmanager
    def _scope():
        yield MagicMock()

    pending = SimpleNamespace(interrupt_id="i1", version=1, status="answered")
    dummy_span = MagicMock()
    dummy_span.id = 1
    monkeypatch.setattr("apps.chat.graphs.nodes.agent_clarify.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.create_interrupt",
        lambda *_a, **_k: pending,
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.attach_running_clarification_span",
        lambda **_k: dummy_span,
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.open_process_span",
        lambda **_k: dummy_span,
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.interrupt",
        lambda _public: [{"question_id": "caliber", "option_id": "opt_a"}],
    )

    state = {
        "run_id": "run-clarify",
        "record_id": 9,
        "sink": "json",
        "tool_rounds": 5,
        "tool_stop_reason": "Tool calling budget reached",
        "knowledge_plane": plane.to_dump(),
        "memory_slots": {},
        "messages": [
            SystemMessage(content=build_agent_system_prompt(knowledge_plane=plane)),
            HumanMessage(content="查一下"),
        ],
        "tool_steps": [
            {
                "ok": True,
                "result": {
                    "data": {
                        "clarification_card": {
                            "questions": [
                                {
                                    "question_id": "caliber",
                                    "question": "用哪个口径？",
                                    "options": [
                                        {
                                            "option_id": "opt_a",
                                            "label": "确认口径X",
                                            "description": "用户确认的口径",
                                            "fields": [
                                                {"table": "t1", "field": "amount"}
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                    }
                },
            }
        ],
    }
    out = await_agent_clarification_node(state)
    assert out["tool_rounds"] == 0
    assert out["tool_stop_reason"] == ""
    confirmed = (out["memory_slots"] or {}).get("confirmed_calibers") or {}
    assert "caliber" in confirmed
    system = deserialize_messages(out["messages"])[0]
    text = str(system.content)
    assert "确认口径X" in text
    assert "confirmed_calibers" in text
    assert "<schema_catalog>" in text


def test_select_delivery_datasets_required_only() -> None:
    probe = SimpleNamespace(
        dataset_id="p", required=False, status="succeeded", row_count=3
    )
    required = SimpleNamespace(
        dataset_id="a", required=True, status="succeeded", row_count=10
    )
    assert select_delivery_datasets([probe]) == []
    picked = select_delivery_datasets([probe, required])
    assert [item.dataset_id for item in picked] == ["a"]


def test_agent_has_sql_result_ignores_probes() -> None:
    probe_only = {
        "tool_steps": [
            {
                "ok": True,
                "result": {"data": {"sql": "SELECT 1", "required": False}},
            }
        ]
    }
    required = {
        "tool_steps": [
            {
                "ok": True,
                "result": {"data": {"sql": "SELECT 1", "required": True}},
            }
        ]
    }
    assert _agent_has_sql_result(probe_only, []) is False
    assert _agent_has_sql_result(required, []) is True


def test_clarify_only_calls_do_not_count_as_work_rounds() -> None:
    from apps.chat.graphs.nodes.unified_agent import _clarify_only_tool_calls

    assert _clarify_only_tool_calls(
        [{"name": "request_clarification", "id": "1", "args": {}}]
    )
    assert not _clarify_only_tool_calls(
        [
            {"name": "request_clarification"},
            {"name": "search_wiki"},
        ]
    )
    assert not _clarify_only_tool_calls([])


def test_wiki_header_uses_physical_table_name() -> None:
    plane = AgentKnowledgePlane()
    delta = plane.merge_recall(
        {
            "knowledge_text": "口径",
            "schema_text": "## 客户信息 (cust_company_info)\n(id:bigint, 主键)\n(name:varchar, 名称)",
            "tables": ["cust_company_info"],
            "page_keys": ["cust_company_info"],
        }
    )
    assert delta.added_tables == ["cust_company_info"]
    assert plane.tables == ["cust_company_info"]
    assert "cust_company_info" in plane.schema_by_table
    assert "客户信息" not in plane.schema_by_table
    assert plane.schema_ready is True


def test_tables_without_field_rows_are_not_schema_ready() -> None:
    plane = AgentKnowledgePlane()
    delta = plane.merge_recall(
        {
            "knowledge_text": "只有口径散文",
            "schema_text": "",
            "tables": ["cust_company_info"],
            "page_keys": ["identify_style"],
        }
    )
    assert delta.added_pages == ["identify_style"]
    assert plane.tables == []
    assert plane.schema_ready is False
    rendered = plane.render_system_sections()
    assert "<wiki_schema_gap>" in rendered
    assert "</schema_catalog>" not in rendered


def test_wiki_page_key_overwrite_does_not_append() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "knowledge_text": "第一版口径",
            "schema_text": "",
            "page_keys": ["identify_style"],
        }
    )
    plane.merge_recall(
        {
            "knowledge_text": "第二版口径",
            "schema_text": "",
            "page_keys": ["identify_style"],
        }
    )
    rendered = plane.render_system_sections()
    assert rendered.count("第一版口径") == 0
    assert rendered.count("第二版口径") == 1


def test_execute_sql_blocked_when_session_schema_missing() -> None:
    run_id = "schema-missing"
    attach_runtime(run_id, knowledge_plane=AgentKnowledgePlane().to_dump())
    llm = SimpleNamespace()
    try:
        with worker_scope(run_id, "tok"):
            blocked = execute_sql_sandbox(
                llm, "SELECT * FROM cust_company_info LIMIT 1"
            )
    finally:
        detach_runtime(run_id)
    assert blocked["ok"] is False
    assert blocked["failure"]["retryable"] is False
    assert "schema" in (blocked.get("error") or "").lower() or "Wiki" in (
        blocked.get("error") or ""
    )


def test_probe_sql_limit_rejects_third_call() -> None:
    run_id = "probe-limit"
    attach_runtime(run_id, probe_sql_calls=PROBE_SQL_LIMIT)
    llm = SimpleNamespace()
    try:
        with worker_scope(run_id, "tok"):
            blocked = execute_sql_sandbox(llm, "SELECT 1", required=False)
    finally:
        detach_runtime(run_id)
    assert blocked["ok"] is False
    assert str(PROBE_SQL_LIMIT) in (blocked.get("error") or "")
    assert blocked["failure"]["retryable"] is False
