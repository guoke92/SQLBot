"""Empty-plane prepare, pin-only restore, and complete_without_sql exits."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane  # noqa: E402
from apps.chat.graphs.nodes.agent_finalize import finalize_agent_turn_node  # noqa: E402
from apps.chat.graphs.nodes.unified_agent import (  # noqa: E402
    route_after_tools_execution,
)
from apps.chat.memory_slots import MemorySlots  # noqa: E402
from apps.chat.steps.recall_request import RecallRequest  # noqa: E402
from apps.chat.task.agent_prompt import (  # noqa: E402
    _SYSTEM_PROMPT_TEMPLATE,
    build_agent_system_prompt,
)
from apps.chat.tools.complete_answer import complete_without_sql  # noqa: E402
from apps.chat.tools.registry import CompleteWithoutSqlInput, build_agent_tools  # noqa: E402


def test_continue_prompt_keeps_baseline_not_restored_wiki() -> None:
    slots = MemorySlots(
        knowledge_refs={
            "page_keys": ["dicts/identify_style"],
            "tables": ["cust_company_info"],
        },
        active_baseline_sql=(
            "SELECT cust_name FROM cust_company_info WHERE enable='Y'"
        ),
    )
    plane = AgentKnowledgePlane(
        schema_outline="<schema_outline>\n- cust_company_info: 企业\n</schema_outline>"
    )
    prompt = build_agent_system_prompt(
        memory_slots=slots.model_dump(),
        change_baseline=slots.extract_change_baseline(),
        knowledge_plane=plane,
    )
    assert "<schema_outline>" in prompt
    assert "cust_company_info" in prompt
    assert "<wiki_knowledge>" not in prompt
    assert "<schema_catalog>" not in prompt
    assert "<change_baseline>" not in prompt
    assert "<memory_slots>" not in prompt
    assert "cust_name FROM cust_company_info" not in prompt


def test_independent_prompt_has_no_pin_restore() -> None:
    prompt = build_agent_system_prompt(
        knowledge_plane=AgentKnowledgePlane(
            schema_outline="<schema_outline>\n- t: 表\n</schema_outline>"
        )
    )
    assert "<schema_outline>" in prompt
    assert "<wiki_knowledge>" not in prompt
    assert "restore_wiki" not in prompt


def test_pin_only_retrieve_skips_vector_query(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    called = {"n": 0}

    def _boom(*_a: object, **_k: object) -> None:
        called["n"] += 1
        raise AssertionError("wiki_recall must not run on pin-only rehydrate")

    monkeypatch.setattr(wr, "wiki_recall", _boom)
    monkeypatch.setattr(wr, "has_wiki_bound_corpus", lambda ds_id=None: True)
    monkeypatch.setattr(wr, "_store", lambda ds_id=None: SimpleNamespace(pages={}))
    monkeypatch.setattr(wr, "datasource_databases", lambda ds: ["db"])
    llm = SimpleNamespace(ds=SimpleNamespace(id=1, type="mysql"))
    out = wr.retrieve_wiki_context(
        llm,
        RecallRequest.rehydrate(
            pin_tables=["cust_company_info"],
            pin_pages=["tables/cust_company_info"],
            question="再加上城市",
        ),
    )
    assert called["n"] == 0
    assert "再加上城市" not in str(out.get("query") or "")


def test_empty_plane_system_prompt_has_no_wiki_or_schema() -> None:
    prompt = build_agent_system_prompt(knowledge_plane=AgentKnowledgePlane())
    assert "<wiki_knowledge>" not in prompt
    assert "<schema_catalog>" not in prompt
    assert "complete_without_sql" in prompt


def test_complete_without_sql_tool_schema_and_payload() -> None:
    args = CompleteWithoutSqlInput.model_validate({"content": "我可以查询企业数据。"})
    res = complete_without_sql(args.content)
    assert res["ok"] is True
    assert res["data"]["terminal_answer"] is True
    assert res["data"]["content"] == "我可以查询企业数据。"
    empty = complete_without_sql("  ")
    assert empty["ok"] is False
    tools = build_agent_tools(MagicMock(), access_scope=None)
    assert any(item.name == "complete_without_sql" for item in tools)


def test_complete_without_sql_rejected_after_delivery(monkeypatch) -> None:
    from apps.conversation.runtime_context import attach_runtime

    attach_runtime("run-sql", sql_delivered=True)
    monkeypatch.setattr(
        "apps.chat.tools.complete_answer.current_worker_identity",
        lambda: ("run-sql", None),
    )
    res = complete_without_sql("忽略这条说明")
    assert res["ok"] is False
    assert "SQL already delivered" in str(res.get("error") or "")


def test_route_complete_without_sql_goes_to_finalize() -> None:
    steps = [
        {
            "ok": True,
            "name": "complete_without_sql",
            "result": {
                "ok": True,
                "data": {"terminal_answer": True, "content": "能力说明"},
            },
        }
    ]
    assert route_after_tools_execution({"tool_steps": steps}) == "finalize_turn"


def test_finalize_text_exit_uses_tool_content(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.graphs.nodes.agent_finalize.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.finalize_run",
        lambda *_a, **_k: None,
    )
    content = "我可以帮你查询企业认证、协议签署等相关数据。"
    out = finalize_agent_turn_node(
        {
            "run_id": "text_exit_run",
            "record_id": 1,
            "final_text": "这段裸文本不该成为终答",
            "turn_route": {"task_kind": "query"},
            "tool_steps": [
                {
                    "ok": True,
                    "name": "complete_without_sql",
                    "result": {
                        "ok": True,
                        "data": {"terminal_answer": True, "content": content},
                    },
                }
            ],
        }
    )
    assert out.get("error") is None
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert ans["content"] == content
    assert ans["datasets"] == []
    quality = (out.get("outcome") or {}).get("quality") or {}
    assert quality.get("grade") != "unreliable"


def test_complete_without_sql_writes_empty_knowledge_refs(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.graphs.nodes.agent_finalize.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.finalize_run",
        lambda *_a, **_k: None,
    )
    content = "我可以帮你查询企业认证、协议签署等相关数据。"
    out = finalize_agent_turn_node(
        {
            "run_id": "capability_qa",
            "record_id": 3,
            "final_text": "这段裸文本不该成为终答",
            "turn_route": {"task_kind": "query"},
            "knowledge_plane": {
                "tables": ["cust_company_info", "cust_account_info"],
                "page_keys": [
                    "tables/cust_company_info",
                    "rules/batch-delete-avoid-deadlock",
                ],
                "schema_by_table": {
                    "cust_company_info": "## 企业 (cust_company_info)\nid:int, 主键",
                    "cust_account_info": "## 账户 (cust_account_info)\nid:int, 主键",
                },
            },
            "tool_steps": [
                {
                    "ok": True,
                    "name": "complete_without_sql",
                    "result": {
                        "ok": True,
                        "data": {"terminal_answer": True, "content": content},
                    },
                }
            ],
        }
    )
    assert out.get("error") is None
    assert out["terminal_answer"]["knowledge_refs"] == {
        "page_keys": [],
        "tables": [],
    }


def test_sql_delivery_scopes_knowledge_refs_to_used_tables(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.graphs.nodes.agent_finalize.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.finalize_run",
        lambda *_a, **_k: None,
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "sql_refs",
            "record_id": 4,
            "final_text": "项目清单如下。",
            "turn_route": {"task_kind": "query"},
            "knowledge_plane": {
                "tables": ["tenant_project", "tenant_setting_config"],
                "page_keys": [
                    "tables/tenant_project",
                    "tables/tenant_setting_config",
                    "dicts/status",
                    "rules/excel-import",
                ],
                "schema_by_table": {
                    "tenant_project": "## 项目 (tenant_project)\nid:int, 主键",
                    "tenant_setting_config": (
                        "## 配置 (tenant_setting_config)\nid:int, 主键"
                    ),
                },
            },
            "tool_steps": [
                {
                    "ok": True,
                    "name": "execute_sql_sandbox",
                    "result": {
                        "ok": True,
                        "data": {
                            "sql": "SELECT id, name FROM tenant_project",
                            "fields": ["id", "name"],
                            "preview_rows": [{"id": 1, "name": "p"}],
                            "row_count": 1,
                            "required": True,
                            "result_title": "项目清单",
                        },
                    },
                }
            ],
        }
    )
    refs = out["terminal_answer"]["knowledge_refs"]
    assert refs["tables"] == ["tenant_project"]
    assert "tenant_setting_config" not in refs["tables"]
    assert "tables/tenant_project" in refs["page_keys"]
    assert "dicts/status" in refs["page_keys"]
    assert "rules/excel-import" not in refs["page_keys"]


def test_sql_delivery_wins_over_text_exit(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.graphs.nodes.agent_finalize.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.finalize_run",
        lambda *_a, **_k: None,
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "sql_wins",
            "record_id": 2,
            "final_text": "口径：启用企业。",
            "turn_route": {"task_kind": "query"},
            "tool_steps": [
                {
                    "ok": True,
                    "name": "execute_sql_sandbox",
                    "result": {
                        "ok": True,
                        "data": {
                            "sql": "SELECT code FROM t",
                            "fields": ["code"],
                            "preview_rows": [{"code": "c1"}],
                            "row_count": 1,
                            "required": True,
                            "result_title": "企业清单",
                        },
                    },
                },
                {
                    "ok": True,
                    "name": "complete_without_sql",
                    "result": {
                        "ok": True,
                        "data": {
                            "terminal_answer": True,
                            "content": "不该覆盖数据集",
                        },
                    },
                },
            ],
        }
    )
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert [item["title"] for item in ans["datasets"]] == ["企业清单"]
    assert "不该覆盖数据集" not in ans["content"]


def test_bare_text_without_exit_still_fails(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.graphs.nodes.agent_finalize.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_finalize.load_result_datasets",
        lambda *_a, **_k: [],
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "bare_text",
            "final_text": "我可以帮你查数，但这次没跑 SQL。",
            "turn_route": {"task_kind": "query"},
            "tool_steps": [],
        }
    )
    assert out["outcome"]["status"] == "failed"
    assert "我可以帮你查数" not in out["final_text"]


def test_prompt_names_two_exits_and_empty_start() -> None:
    assert "首次召回是起点" not in _SYSTEM_PROMPT_TEMPLATE
    assert "complete_without_sql" in _SYSTEM_PROMPT_TEMPLATE
    assert "execute_sql_sandbox(required=true)" in _SYSTEM_PROMPT_TEMPLATE
    assert "终答只有两条路" in _SYSTEM_PROMPT_TEMPLATE
    assert "schema_outline" in _SYSTEM_PROMPT_TEMPLATE
    assert "get_table_schema" in _SYSTEM_PROMPT_TEMPLATE


def test_chat_yaml_execute_tools_can_finalize() -> None:
    text = (_BACKEND / "graphs" / "current" / "chat.yaml").read_text(encoding="utf-8")
    execute_block = text.split("- from: execute_tools", 1)[1].split("- from:", 1)[0]
    assert "finalize_turn: finalize_turn" in execute_block
    assert "await_clarification: await_clarification" in execute_block
