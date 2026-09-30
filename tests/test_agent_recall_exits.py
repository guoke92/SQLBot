"""Empty-plane prepare, pin-only restore, and unified close (cards vs narration)."""

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
from apps.chat.agent.delivery import finalize_agent_turn_node  # noqa: E402
from apps.chat.agent.loop import (  # noqa: E402
    route_after_tools_execution,
)
from apps.chat.memory_slots import MemorySlots  # noqa: E402
from apps.chat.steps.recall_request import RecallRequest  # noqa: E402
from apps.chat.task.agent_prompt import (  # noqa: E402
    _SYSTEM_PROMPT_TEMPLATE,
    build_agent_system_prompt,
)
from apps.chat.agent.workspace import SqlWorkspace  # noqa: E402
from apps.chat.tools.registry import build_agent_tools  # noqa: E402


def _result_ds(
    *,
    dataset_id: str,
    sql: str,
    fields: list[str],
    rows: list[dict],
    row_count: int,
    title: str = "",
    required: bool = True,
    truncated: bool = False,
    limit: int | None = None,
):
    from types import SimpleNamespace

    return SimpleNamespace(
        dataset_id=dataset_id,
        status="succeeded",
        required=required,
        fields=fields,
        rows=rows,
        row_count=row_count,
        truncated=truncated,
        schema_snapshot={
            "sql": sql,
            "result_title": title,
            "chart_type": "table",
            "limit": limit,
        },
    )


def _delivered_workspace(sql: str, *, dataset_id: str, title: str = "") -> dict:
    ws = SqlWorkspace()
    item = ws.add_revision(
        sql, origin="model", status="executed", dataset_id=dataset_id, result_title=title
    )
    ws.mark_executed(
        item.rev, dataset_id=dataset_id, purpose="delivery", result_title=title
    )
    return ws.model_dump(mode="json")


def test_continue_prompt_keeps_baseline_not_restored_wiki() -> None:
    slots = MemorySlots(
        knowledge_refs={
            "page_keys": ["dicts/identify_style"],
            "tables": ["cust_company_info"],
        },
        current_rev="r1",
    )
    plane = AgentKnowledgePlane(
        schema_outline="<schema_outline>\n- cust_company_info: 企业\n</schema_outline>"
    )
    prompt = build_agent_system_prompt(
        memory_slots=slots.model_dump(),
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
    assert "complete_without_sql" not in prompt
    assert "停手即终答" in prompt


def test_text_close_is_not_a_tool() -> None:
    tools = build_agent_tools(MagicMock(), access_scope=None)
    names = {item.name for item in tools}
    assert "complete_without_sql" not in names
    assert "execute_sql_sandbox" in names
    assert "request_clarification" in names


def test_compare_results_is_not_a_close_exit() -> None:
    from apps.chat.tools.contract import Signals, ToolOutcome

    steps = [
        {
            "ok": True,
            "name": "compare_results",
            "outcome": ToolOutcome(
                ok=True,
                summary="diff",
                payload={"row_count_a": 3, "row_count_b": 5},
                signals=Signals(),
            ).model_dump(mode="json"),
        }
    ]
    assert route_after_tools_execution({"tool_steps": steps}) == "agent_loop"


def test_finalize_text_exit_uses_final_text(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    content = "我可以帮你查询企业认证、协议签署等相关数据。"
    out = finalize_agent_turn_node(
        {
            "run_id": "text_exit_run",
            "record_id": 1,
            "final_text": content,
            "turn_route": {"task_kind": "query", "relation": "continue"},
            "tool_steps": [],
        }
    )
    assert out.get("error") is None
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert ans["content"] == content
    assert ans["datasets"] == []
    quality = (out.get("outcome") or {}).get("quality") or {}
    assert quality.get("grade") != "unreliable"


def test_text_close_writes_empty_knowledge_refs(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    content = "我可以帮你查询企业认证、协议签署等相关数据。"
    out = finalize_agent_turn_node(
        {
            "run_id": "capability_qa",
            "record_id": 3,
            "final_text": content,
            "turn_route": {"task_kind": "query", "relation": "continue"},
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

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [
            _result_ds(
                dataset_id="ds1",
                sql="SELECT id, name FROM tenant_project",
                fields=["id", "name"],
                rows=[{"id": 1, "name": "p"}],
                row_count=1,
                title="项目清单",
            )
        ],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "sql_refs",
            "record_id": 4,
            "final_text": "项目清单如下。",
            "turn_route": {"task_kind": "query"},
            "sql_workspace": _delivered_workspace(
                "SELECT id, name FROM tenant_project",
                dataset_id="ds1",
                title="项目清单",
            ),
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
        }
    )
    refs = out["terminal_answer"]["knowledge_refs"]
    assert refs["tables"] == ["tenant_project"]
    assert "tenant_setting_config" not in refs["tables"]
    assert "tables/tenant_project" in refs["page_keys"]
    assert "dicts/status" in refs["page_keys"]
    assert "rules/excel-import" not in refs["page_keys"]


def test_text_close_pins_knowledge_refs_from_workspace_sql(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    ws = SqlWorkspace()
    ws.inherit_dataset(
        {
            "sql": "SELECT code FROM cust_company_info LIMIT 1000",
            "dataset_id": "ds1",
            "rev": "r1",
            "fields": ["code"],
            "row_count": 1000,
            "truncated": True,
            "limit": 1000,
        }
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "continue_attr",
            "record_id": 861,
            "final_text": "行数差来自展示截断，不是口径不同。",
            "turn_route": {"task_kind": "query", "relation": "continue"},
            "sql_workspace": ws.model_dump(mode="json"),
            "knowledge_plane": {
                "tables": ["cust_company_info", "cust_account_info"],
                "page_keys": [
                    "tables/cust_company_info",
                    "tables/cust_account_info",
                ],
                "schema_by_table": {
                    "cust_company_info": "## 企业 (cust_company_info)\nid:int",
                    "cust_account_info": "## 账户 (cust_account_info)\nid:int",
                },
            },
        }
    )
    refs = out["terminal_answer"]["knowledge_refs"]
    assert refs["tables"] == ["cust_company_info"]
    assert "cust_account_info" not in refs["tables"]


def test_close_pins_workspace_tables_when_plane_empty(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    ws = SqlWorkspace()
    ws.inherit_dataset(
        {
            "sql": "SELECT code FROM cust_company_info",
            "dataset_id": "ds1",
            "rev": "r1",
        }
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "empty_plane",
            "record_id": 862,
            "final_text": "沿用上轮 SQL。",
            "turn_route": {"task_kind": "query", "relation": "continue"},
            "sql_workspace": ws.model_dump(mode="json"),
        }
    )
    refs = out["terminal_answer"]["knowledge_refs"]
    assert "cust_company_info" in list((refs or {}).get("tables") or [])


def test_sql_delivery_wins_over_text_exit(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [
            _result_ds(
                dataset_id="ds1",
                sql="SELECT code FROM t",
                fields=["code"],
                rows=[{"code": "c1"}],
                row_count=1,
                title="企业清单",
            )
        ],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "sql_wins",
            "record_id": 2,
            "final_text": "口径：启用企业。",
            "turn_route": {"task_kind": "query"},
            "sql_workspace": _delivered_workspace(
                "SELECT code FROM t", dataset_id="ds1", title="企业清单"
            ),
        }
    )
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert [item["title"] for item in ans["datasets"]] == ["企业清单"]
    assert "口径：启用企业。" in ans["content"]


def test_independent_text_close_uses_final_text(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )
    content = "我能帮你查数、对比和解释口径。直接说要看哪一类数据即可。"
    out = finalize_agent_turn_node(
        {
            "run_id": "capability",
            "record_id": 875,
            "final_text": content,
            "turn_route": {"task_kind": "query", "relation": "independent"},
            "tool_steps": [],
        }
    )
    assert out.get("error") is None
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert ans["content"] == content
    assert ans["datasets"] == []


def test_empty_stop_without_delivery_still_fails(monkeypatch) -> None:
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        "apps.chat.graphs.turn_failure.persist_query_terminal_failure",
        lambda payload, **_k: payload.get("outcome")
        or {"status": "failed", "failures": []},
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "empty_stop",
            "turn_route": {"task_kind": "query", "relation": "independent"},
            "tool_steps": [],
        }
    )
    assert out["outcome"]["status"] == "failed"


def test_prompt_names_unified_close_and_empty_start() -> None:
    assert "首次召回是起点" not in _SYSTEM_PROMPT_TEMPLATE
    assert "complete_without_sql" not in _SYSTEM_PROMPT_TEMPLATE
    assert "execute_sql_sandbox(purpose=delivery)" in _SYSTEM_PROMPT_TEMPLATE
    assert "停手即终答" in _SYSTEM_PROMPT_TEMPLATE
    assert "schema_outline" in _SYSTEM_PROMPT_TEMPLATE
    assert "get_table_schema" in _SYSTEM_PROMPT_TEMPLATE


def test_chat_yaml_execute_tools_can_finalize() -> None:
    text = (_BACKEND / "graphs" / "current" / "chat.yaml").read_text(encoding="utf-8")
    execute_block = text.split("- from: execute_tools", 1)[1].split("- from:", 1)[0]
    assert "finalize_turn: finalize_turn" in execute_block
    assert "await_clarification: await_clarification" in execute_block
