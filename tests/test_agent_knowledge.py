"""AgentKnowledgePlane SSOT: merge, stubs, clarify budget, required-only delivery."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import (  # noqa: E402
    PROBE_SQL_LIMIT,
    AgentKnowledgePlane,
    MergeDelta,
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
    peek_runtime,
    worker_scope,
)
from apps.conversation.tooling import execute_tools_node  # noqa: E402


def test_plane_same_table_merge_does_not_grow() -> None:
    plane = AgentKnowledgePlane()
    blob = "## 任务 (d_task)\nid:int, 主键\nname:text, 名称"
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
    assert "<wiki_knowledge>" not in first
    assert "<schema_catalog>" not in first
    assert "任务表口径" not in first
    assert "## 任务 (d_task)" in plane.schema_catalog_text()


def test_search_wiki_stub_and_unchanged_stop(monkeypatch) -> None:
    from apps.chat.tools import wiki_search as ws

    payload = {
        "knowledge_text": "# d_task\n任务表",
        "schema_text": "## 任务 (d_task)\nid:int, 主键\nname:text, 名称",
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
    assert first["data"]["hit_count"] == 1
    assert first["data"]["stop_search"] is False
    assert second["data"]["unchanged"] is True
    assert second["data"]["stop_search"] is True
    assert second["data"]["recall_status"] == "diminishing_returns"


def test_execute_tools_keeps_schema_text_for_catalog_tool(monkeypatch) -> None:
    fake_tool = MagicMock()
    fake_tool.name = "get_table_schema"
    fake_tool.invoke.return_value = {
        "ok": True,
        "summary": "opened",
        "data": {
            "schema_text": "# Table: t1\nFULL_SCHEMA",
            "added_tables": ["t1"],
            "tables": ["t1"],
            "schema_ready": True,
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
        "run_id": "keep-schema",
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
                        "name": "get_table_schema",
                        "args": {"tables": ["t1"]},
                    }
                ],
            ),
        ],
        "bound_tools": [fake_tool],
        "knowledge_plane": {},
        "memory_slots": {},
    }
    out = execute_tools_node(state)
    data = out["tool_steps"][0]["result"]["data"]
    assert data["schema_text"] == "# Table: t1\nFULL_SCHEMA"
    assert data["added_tables"] == ["t1"]
    assert out.get("tool_stop_reason") in {"", None}
    plane = AgentKnowledgePlane.from_dump(out.get("knowledge_plane"))
    assert plane.knowledge_rounds == 1
    tool_message = next(
        message
        for message in deserialize_messages(out["messages"])
        if isinstance(message, ToolMessage)
    )
    content = str(tool_message.content)
    assert "\\n" not in content
    assert "# Table: t1" in content
    assert "FULL_SCHEMA" in content.splitlines()
    assert '"ok"' not in content
    assert "schema_text" not in content


def test_execute_tools_does_not_lock_on_stop_search(monkeypatch) -> None:
    fake_tool = MagicMock()
    fake_tool.name = "get_table_schema"
    fake_tool.invoke.return_value = {
        "ok": True,
        "summary": "stagnant",
        "data": {
            "added_tables": [],
            "added_pages": [],
            "schema_ready": True,
            "stop_search": True,
            "recall_status": "stagnant",
            "unchanged": True,
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
        "run_id": "no-lock-search",
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
                        "name": "get_table_schema",
                        "args": {"tables": ["t1"]},
                    }
                ],
            ),
        ],
        "bound_tools": [fake_tool],
        "knowledge_plane": {},
        "memory_slots": {},
    }
    out = execute_tools_node(state)
    assert out.get("tool_stop_reason") in {"", None}
    assert out["tool_steps"][0]["result"]["data"]["stop_search"] is True


def test_search_wiki_timeline_summary_uses_recall_count() -> None:
    from apps.conversation.tooling import _knowledge_tool_close

    key, params = _knowledge_tool_close(
        "search_knowledge",
        {"ok": True, "data": {"hit_count": 4, "page_keys": ["a", "b", "c", "d"]}},
    )
    assert key == "chat.summary.wiki_prepared"
    assert params == {"count": 4}
    failed_key, _failed = _knowledge_tool_close(
        "get_table_schema", {"ok": False, "data": {}}
    )
    assert failed_key == "chat.summary.tool_failed"
    ok_key, ok_params = _knowledge_tool_close(
        "execute_sql_sandbox", {"ok": True, "data": {}}
    )
    assert ok_key == "chat.summary.tool_ok"
    assert ok_params == {"tool": "execute_sql_sandbox"}
    skip_key, skip_params = _knowledge_tool_close(
        "search_knowledge",
        {"ok": True, "data": {"skipped": "knowledge_budget"}},
    )
    assert skip_key == "chat.summary.tool_skipped"
    assert skip_params == {"tool": "search_knowledge"}


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
            "schema_text": "## 表 (t1)\nid:int, 主键",
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
        "apps.chat.graphs.nodes.agent_clarify.ensure_clarification_span",
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
    messages = deserialize_messages(out["messages"])
    system = messages[0]
    text = str(system.content)
    assert "<schema_catalog>" not in text
    assert "<memory_slots>" not in text
    human_text = "\n".join(
        str(item.content)
        for item in messages
        if str(getattr(item, "type", "")) == "human"
    )
    assert "确认口径X" in human_text
    assert "用户已完成澄清" in human_text


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


def test_agent_has_sql_result_ignores_prior_turn_transcript() -> None:
    """Continue turns preload prior execute_sql ToolMessages; they must not count."""
    prior = ToolMessage(
        content="Query executed successfully",
        name="execute_sql_sandbox",
        tool_call_id="prior-1",
        artifact={
            "ok": True,
            "data": {"sql": "SELECT 1 AS prior", "required": True, "row_count": 1},
        },
    )
    human = HumanMessage(content="哪些企业运营人员为空")
    state = {"turn_message_start": 1, "tool_steps": []}
    assert _agent_has_sql_result(state, [prior, human]) is False

    current = ToolMessage(
        content="Query executed successfully",
        name="execute_sql_sandbox",
        tool_call_id="cur-1",
        artifact={
            "ok": True,
            "data": {"sql": "SELECT 2 AS cur", "required": True, "row_count": 1},
        },
    )
    assert (
        _agent_has_sql_result(
            state,
            [prior, human, AIMessage(content="", tool_calls=[]), current],
        )
        is True
    )


def test_self_budgeted_tool_calls_do_not_advance_execution_rounds() -> None:
    """Categorical budgets: clarification and search_wiki have their own limits,
    so a round made only of them must not consume the execution round budget."""
    from apps.chat.agent_knowledge import tool_calls_advance_round

    assert not tool_calls_advance_round(
        [{"name": "request_clarification", "id": "1", "args": {}}]
    )
    assert not tool_calls_advance_round(
        [{"name": "request_clarification"}, {"name": "get_table_schema"}]
    )
    assert not tool_calls_advance_round(
        [{"name": "complete_without_sql"}, {"name": "search_knowledge"}]
    )
    assert tool_calls_advance_round(
        [{"name": "get_table_schema"}, {"name": "execute_sql_sandbox"}]
    )
    assert not tool_calls_advance_round([])


def test_wiki_header_uses_physical_table_name() -> None:
    plane = AgentKnowledgePlane()
    delta = plane.merge_recall(
        {
            "knowledge_text": "口径",
            "schema_text": "## 客户信息 (cust_company_info)\nid:bigint, 主键\nname:varchar, 名称",
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
    assert "<wiki_knowledge>" not in rendered
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
    assert plane.wiki_passages.get("identify_style") == "第二版口径"
    rendered = plane.render_system_sections()
    assert "第一版口径" not in rendered
    assert "第二版口径" not in rendered


def test_execute_sql_does_not_gate_on_schema_ready() -> None:
    """Once SQL is generated, plane.schema_ready must not block execution."""
    run_id = "schema-ready-not-gate"
    attach_runtime(run_id, knowledge_plane=AgentKnowledgePlane().to_dump())
    llm = SimpleNamespace()
    try:
        with worker_scope(run_id, "tok"):
            result = execute_sql_sandbox(
                llm, "SELECT * FROM cust_company_info LIMIT 1"
            )
    finally:
        detach_runtime(run_id)
    assert result["ok"] is False
    err = result.get("error") or ""
    assert "Wiki did not provide" not in err
    assert "Datasource or protocol" in err


def test_probe_sql_limit_soft_warns_instead_of_blocking() -> None:
    """Over-budget probes still need a protocol/ds to run; budget note alone.

    When schema/runtime cannot execute, the soft budget must not invent a
    hard probe-limit failure — that was the chat-245 timeline false failure.
    """
    run_id = "probe-limit"
    attach_runtime(run_id, probe_sql_calls=PROBE_SQL_LIMIT)
    llm = SimpleNamespace()
    try:
        with worker_scope(run_id, "tok"):
            blocked = execute_sql_sandbox(llm, "SELECT 1", required=False)
    finally:
        detach_runtime(run_id)
    assert blocked["ok"] is False
    err = blocked.get("error") or ""
    assert "Probe SQL limit" not in err
    assert "Datasource or protocol" in err
    assert "probe_budget" in err
    assert "上限" not in err


def test_display_sql_uses_protocol_formatter() -> None:
    from apps.chat.tools.execute_sql import _display_sql

    plan = SimpleNamespace(
        payload={"sql": "SELECT 1\nFROM t"}, statement="SELECT 1 FROM t"
    )

    class _Proto:
        def format_statement_for_display(self, p):  # noqa: ANN001
            return "SELECT 1\nFROM t"

    assert "\n" in _display_sql(_Proto(), plan, plan.statement)
    assert _display_sql(SimpleNamespace(), plan, "fallback") == "fallback"


def test_consume_probe_budget_advises_without_blocking() -> None:
    from apps.chat.tools.execute_sql import _consume_probe_budget

    run_id = "probe-soft"
    attach_runtime(run_id, probe_sql_calls=0)
    try:
        with worker_scope(run_id, "tok"):
            assert _consume_probe_budget(True) is None
            assert _consume_probe_budget(False) is None  # 1/2
            note = _consume_probe_budget(False)  # 2/2
            assert note and "probe_budget" in note and "探查已执行" in note
            assert "上限" not in note
            over = _consume_probe_budget(False)  # 3rd still allowed
            assert over and "probe_budget" in over
            assert "上限" not in over
            assert "必要的形态验证仍可再探查" in over
    finally:
        detach_runtime(run_id)


def test_kernel_conflicts_are_evidence_not_auto_cards() -> None:
    plane = AgentKnowledgePlane()
    evidence = [
        {
            "conflict_id": (
                "caliber:cust_company_info.cust_build_type|"
                "cust_company_info.identify_style"
            ),
            "kind": "attribution",
            "phrase": "认证方式是平台录入",
            "candidates": [
                {
                    "saying": "认证方式",
                    "table": "cust_company_info",
                    "field": "identify_style",
                    "value": "",
                    "value_label": "",
                    "enum_values": [
                        {"value": "INVITE_AGW", "label": "邀请认证-内管录入"}
                    ],
                },
                {
                    "saying": "平台录入",
                    "table": "cust_company_info",
                    "field": "cust_build_type",
                    "value": "AGW_BUILD",
                    "value_label": "平台录入",
                    "enum_values": [{"value": "AGW_BUILD", "label": "平台录入"}],
                },
            ],
        }
    ]
    plane.adopt_conflicts(evidence)
    assert plane.caliber_conflicts
    rendered = plane.render_system_sections()
    assert "<caliber_conflicts>" not in rendered
    assert "question_id" not in rendered
    plane.drop_resolved_conflicts(
        {
            evidence[0]["conflict_id"]: {
                "fields": [{"table": "cust_company_info", "name": "cust_build_type"}]
            }
        }
    )
    assert plane.caliber_conflicts == []


def test_wiki_enum_discovery_sql_rejects_distinct_only() -> None:
    from apps.chat.steps.enum_display import is_wiki_enum_discovery_sql

    carriers = {
        "identify_style",
        "cust_build_type",
        "cust_company_info.identify_style",
        "cust_company_info.cust_build_type",
    }
    assert is_wiki_enum_discovery_sql(
        "SELECT DISTINCT identify_style FROM cust_company_info",
        carriers,
    )
    assert is_wiki_enum_discovery_sql(
        "SELECT DISTINCT identify_style, cust_build_type FROM cust_company_info",
        carriers,
    )
    # Distribution analytics stay allowed — not a dictionary dump.
    assert not is_wiki_enum_discovery_sql(
        "SELECT identify_style, cust_build_type, COUNT(*) AS cnt "
        "FROM cust_company_info GROUP BY identify_style, cust_build_type",
        carriers,
    )
    assert not is_wiki_enum_discovery_sql(
        "SELECT identify_style, COUNT(*) AS cnt FROM cust_company_info "
        "WHERE create_time < '2025-06-01' GROUP BY identify_style",
        carriers,
    )
    assert not is_wiki_enum_discovery_sql(
        "SELECT code, name FROM cust_company_info WHERE identify_style = 'INVITE_AGW'",
        carriers,
    )


def test_plane_does_not_drop_tables_for_count_budget() -> None:
    plane = AgentKnowledgePlane()
    for index in range(10):
        name = f"t_{index}"
        plane.merge_recall(
            {
                "schema_text": f"## x ({name})\nid:int, 主键",
                "tables": [name],
            }
        )
    policy = plane.apply_search_policy(
        MergeDelta(
            added_tables=["t_9"],
            unchanged=False,
            schema_ready=True,
        )
    )
    assert plane.tables == [f"t_{index}" for index in range(10)]
    assert len(plane.schema_by_table) == 10
    assert policy["recall_status"] != "budget_exhausted"


def test_exclude_knowledge_hides_from_prompt_and_blocks_remerge() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "schema_text": (
                "## 主档 (cust_company_info)\nid:int, 主键\n"
                "## 噪声 (cust_change_cfg)\nid:int, 主键"
            ),
            "tables": ["cust_company_info", "cust_change_cfg"],
            "page_keys": ["concepts/menuKey"],
            "wiki_passages": {"concepts/menuKey": "# 菜单\nmenuKey 说明"},
            "query": "已缴费企业管理员",
        }
    )
    dropped = plane.exclude_knowledge(["cust_change_cfg", "concepts/menuKey"])
    assert dropped["tables"] == ["cust_change_cfg"]
    assert "concepts/menuKey" in dropped["pages"]
    rendered = plane.render_system_sections()
    catalog = plane.schema_catalog_text()
    assert "cust_company_info" in catalog
    assert "## 噪声" not in catalog
    assert "# 菜单" not in rendered
    assert "<knowledge_index>" not in rendered
    assert "cust_change_cfg" in plane.excluded
    assert plane.tables == ["cust_company_info"]

    plane.merge_recall(
        {
            "schema_text": "## 噪声 (cust_change_cfg)\nid:int, 主键",
            "tables": ["cust_change_cfg"],
            "query": "已缴费企业管理员",
        }
    )
    assert "cust_change_cfg" not in plane.tables
    assert "## 噪声" not in plane.schema_catalog_text()

    plane.merge_recall(
        {
            "schema_text": "## 噪声 (cust_change_cfg)\nid:int, 主键",
            "tables": ["cust_change_cfg"],
            "query": "cust_change_cfg 变更配置",
        }
    )
    assert "cust_change_cfg" in plane.tables
    assert "## 噪声" in plane.schema_catalog_text()


def test_search_wiki_drop_only_skips_retrieve(monkeypatch) -> None:
    from apps.chat.tools import wiki_search as ws

    def _boom(*_a, **_k):  # noqa: ANN002
        raise AssertionError("drop-only must not retrieve")

    monkeypatch.setattr(ws, "retrieve_wiki_context", _boom)
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "schema_text": (
                "## 主档 (cust_company_info)\nid:int, 主键\n"
                "## 噪声 (cust_change_cfg)\nid:int, 主键"
            ),
            "tables": ["cust_company_info", "cust_change_cfg"],
        }
    )
    run_id = "wiki-drop-only"
    attach_runtime(run_id, knowledge_plane=plane.to_dump())
    llm = SimpleNamespace(ds=SimpleNamespace(id=1))
    try:
        with worker_scope(run_id, "tok"):
            result = ws.search_wiki_knowledge(llm, "", drop=["cust_change_cfg"])
            snap = peek_runtime(run_id)
    finally:
        detach_runtime(run_id)
    assert result["ok"] is True
    assert result["data"]["recall_status"] == "dropped"
    assert result["data"]["dropped_tables"] == ["cust_change_cfg"]
    assert result["data"]["tables"] == ["cust_company_info"]
    assert "cust_change_cfg" in result["data"]["excluded"]
    restored = AgentKnowledgePlane.from_dump((snap or {}).get("knowledge_plane"))
    assert restored.tables == ["cust_company_info"]
    assert restored.search_rounds == 0
