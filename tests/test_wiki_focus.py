"""Focused recall: single search_wiki focus enum, local lookup, admit, GC."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane  # noqa: E402
from apps.chat.steps.recall_request import RecallRequest  # noqa: E402
from apps.chat.steps.wiki_focus import (  # noqa: E402
    LOOKUP_FOUND_LIMIT,
    catalog_rank_tables,
    coverage_pin_tables,
    expanded_tables,
    infer_focus,
    is_binding_page,
    lookup_payload,
    normalize_focus,
)
from apps.chat.tools.registry import GetTableSchemaInput  # noqa: E402
from apps.conversation.runtime_context import (  # noqa: E402
    attach_runtime,
    detach_runtime,
    peek_runtime,
    worker_scope,
)
from apps.conversation.tooling import _knowledge_tool_close, execute_tools_node  # noqa: E402

_PROJECT_SCHEMA = """## 项目 (tenant_project)
id:int, 主键
name:varchar, 项目名称
city:varchar, 城市
industry:varchar, 行业
status:varchar, 状态, dict=status, labels=0:待生效|1:已生效
created_at:datetime, 创建时间
tenant_id:int, 租户
关联: tenant_project.tenant_id → tenant.id
"""

_NOISE_SCHEMA = """## 租户配置 (tenant_setting_config)
id:int, 主键
cfg_key:varchar, 配置项
cfg_value:varchar, 配置值
"""


def _ready_plane() -> AgentKnowledgePlane:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "query": "项目清单",
            "schema_text": _PROJECT_SCHEMA,
            "tables": ["tenant_project"],
            "page_keys": ["tables/tenant_project", "dicts/status"],
            "wiki_passages": {
                "tables/tenant_project": "# 项目主档\n项目表",
                "dicts/status": "# 状态\n0 待生效",
            },
            "backend": "wiki",
        }
    )
    return plane


def test_focus_contract_defaults_to_all() -> None:
    assert RecallRequest.simple("项目").focus == "all"
    parsed = GetTableSchemaInput(tables=["tenant_project"])
    assert parsed.tables == ["tenant_project"]
    assert normalize_focus("") == "all"
    assert normalize_focus("none") == "all"
    assert normalize_focus("fine") == "field"
    assert normalize_focus("dict") == "dict"


def test_infer_focus_upgrades_exact_column_not_sentences() -> None:
    plane = _ready_plane()
    assert infer_focus("tenant_project.status", plane, declared="all") == "field"
    assert infer_focus("项目名称", plane, declared="all") == "field"
    assert infer_focus("status", plane, declared="all") == "field"
    assert infer_focus("查已生效状态的项目清单导出", plane, declared="all") == "all"
    assert infer_focus("status", plane, declared="dict") == "dict"


def test_infer_focus_upgrades_space_separated_field_list() -> None:
    plane = _ready_plane()
    assert (
        infer_focus(
            "name city industry status created_at tenant_id",
            plane,
            declared="all",
        )
        == "field"
    )
    assert infer_focus("是否生产数据", plane, declared="all") == "all"


def test_infer_focus_keeps_all_when_query_names_a_page() -> None:
    plane = _ready_plane()
    assert (
        infer_focus(
            "rules/excel-import-operation-config-rule 项目运营配置",
            plane,
            declared="all",
        )
        == "all"
    )
    assert (
        infer_focus(
            "excel-import-operation-config-rule 项目名称 city",
            plane,
            declared="all",
        )
        == "all"
    )


def test_field_lookup_lights_keep_fields_without_prose() -> None:
    from apps.chat.tools import wiki_search as ws

    plane = _ready_plane()
    payload = lookup_payload(plane, "项目名称", focus="field")
    assert payload["knowledge_text"] == ""
    assert payload["schema_text"] == ""
    assert payload["page_keys"] == []
    assert payload["focus_facts"]["found"]
    assert payload["evidence_fields"]["tenant_project"] == ["name"]

    run_id = "focus-field"
    attach_runtime(run_id, knowledge_plane=plane.to_dump())
    try:
        with worker_scope(run_id, "tok"):
            out = ws.search_wiki_knowledge(
                SimpleNamespace(ds=SimpleNamespace(id=1)),
                "项目名称",
                focus="field",
            )
        saved = AgentKnowledgePlane.from_dump(
            (peek_runtime(run_id) or {}).get("knowledge_plane")
        )
    finally:
        detach_runtime(run_id)
    assert out["ok"] is True
    assert out["data"]["focus"] == "field"
    assert out["data"]["backend"] == "lookup"
    assert "knowledge_text" not in out["data"]
    assert out["data"]["recall_status"] == "hit"
    assert "name" in (saved.keep_fields.get("tenant_project") or [])
    assert "未注入 Wiki 正文" in out["summary"]


def test_enum_lookup_returns_physical_mapping() -> None:
    plane = _ready_plane()
    payload = lookup_payload(plane, "status", focus="dict")
    found = payload["focus_facts"]["found"]
    assert found
    assert found[0]["enums"] == {"0": "待生效", "1": "已生效"}
    assert payload["knowledge_text"] == ""


def test_field_lookup_not_found_soft_guides() -> None:
    from apps.chat.tools import wiki_search as ws

    plane = _ready_plane()
    run_id = "focus-missing"
    attach_runtime(run_id, knowledge_plane=plane.to_dump())
    try:
        with worker_scope(run_id, "tok"):
            out = ws.search_wiki_knowledge(
                SimpleNamespace(ds=SimpleNamespace(id=1)),
                "custom_ext_col",
                focus="field",
            )
    finally:
        detach_runtime(run_id)
    assert out["data"]["recall_status"] == "not_found"
    assert out["data"]["stop_search"] is True
    assert "请勿反复搜索" in out["summary"]
    assert out["data"]["focus"] == "field"


def test_focus_all_rules_only_is_diminishing_not_hit() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = _ready_plane()
    _plane, policy, delta = apply_wiki_search_policy(
        {
            "knowledge_text": "# Excel 导入规则\n很长的散文",
            "schema_text": "",
            "tables": [],
            "page_keys": ["rules/excel-import"],
            "wiki_passages": {"rules/excel-import": "# Excel\n散文污染"},
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert is_binding_page("rules/excel-import", plane.tables) is False
    assert "rules/excel-import" not in plane.page_keys
    assert policy["recall_status"] == "diminishing_returns"
    assert policy["stop_search"] is True
    assert delta.added_tables == []
    assert "excel-import" not in plane.wiki_passages


def test_focus_all_new_table_still_hits_after_diminishing() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = _ready_plane()
    plane, policy, _delta = apply_wiki_search_policy(
        {
            "knowledge_text": "# 规则",
            "schema_text": "",
            "tables": [],
            "page_keys": ["rules/noise"],
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert policy["recall_status"] == "diminishing_returns"
    plane, policy, delta = apply_wiki_search_policy(
        {
            "knowledge_text": "",
            "schema_text": "## 租户 (tenant)\nid:int, 主键",
            "tables": ["tenant"],
            "page_keys": ["tables/tenant"],
            "table_evidence": {"tenant": ["tables/tenant"]},
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert delta.added_tables == ["tenant"]
    assert policy["recall_status"] == "hit"
    assert policy["stop_search"] is False


def test_local_lookup_does_not_consume_search_round() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = _ready_plane()
    before = plane.search_rounds
    payload = lookup_payload(plane, "city", focus="field")
    apply_wiki_search_policy(payload, plane, focus="field")
    assert plane.search_rounds == before


def test_coverage_pin_tables_prefers_wide_export_table() -> None:
    fields = [
        {"name": "name", "comment": "项目名称"},
        {"name": "city", "comment": "城市"},
        {"name": "industry", "comment": "行业"},
        {"name": "status", "comment": "状态"},
        {"name": "created_at", "comment": "创建时间"},
        {"name": "tenant_id", "comment": "租户"},
        {"name": "owner", "comment": "负责人"},
    ]
    winner = SimpleNamespace(
        page_key="tables/tenant_project",
        title="项目",
        body="项目主档",
        ground_blocks=[
            SimpleNamespace(
                kind="table",
                data={"table": "tenant_project", "fields": fields},
            )
        ],
    )
    noise = SimpleNamespace(
        page_key="tables/tenant_setting_config",
        title="租户配置",
        body="配置项",
        ground_blocks=[
            SimpleNamespace(
                kind="table",
                data={
                    "table": "tenant_setting_config",
                    "fields": [{"name": "cfg_key", "comment": "配置项"}],
                },
            )
        ],
    )
    pages = {
        "tables/tenant_project": winner,
        "tables/tenant_setting_config": noise,
    }
    store = SimpleNamespace(
        table_index={key: key for key in pages},
        get_page=lambda key: pages.get(key),
    )
    query = "项目名称,城市,行业,状态,创建时间,租户,负责人"
    assert coverage_pin_tables(query, store) == ("tenant_project",)
    ranked = catalog_rank_tables(query, store, cap=4)
    assert [item.name for item in ranked] == ["tenant_project"]


def test_working_set_folds_low_coverage_noise_instead_of_evicting() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "query": "项目名称,城市,行业,状态,创建时间,租户,负责人",
            "schema_text": _PROJECT_SCHEMA + "\n" + _NOISE_SCHEMA,
            "tables": ["tenant_setting_config", "tenant_project"],
            "page_keys": [
                "tables/tenant_project",
                "tables/tenant_setting_config",
                "rules/excel-tenant_setting_config",
            ],
            "wiki_passages": {
                "tables/tenant_project": "# 项目",
                "tables/tenant_setting_config": "# 配置",
                "rules/excel-tenant_setting_config": "# Excel 导入规则",
            },
            "evidence_fields": {
                "tenant_project": [
                    "name",
                    "city",
                    "industry",
                    "status",
                    "created_at",
                    "tenant_id",
                ]
            },
            "backend": "wiki",
        }
    )
    kept = expanded_tables(plane)
    assert "tenant_project" in kept
    catalog = plane.schema_catalog_text()
    assert "tenant_project" in catalog
    # Opened tables are fully expanded; folding is no longer a recall policy.
    assert "cfg_key" in catalog
    index = plane.render_system_sections()
    assert "folded:" not in index
    assert "tenant_setting_config" in index


def test_expanded_tables_uses_human_question_not_later_tool_query() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "question": "查询多租户联系人超过五个的企业信息",
            "query": "查询多租户联系人超过五个的企业信息",
            "schema_text": (
                "## 企业 (cust_company_info)\n"
                "cust_name:varchar, 企业名称\n"
                "code:varchar, 企业编码\n"
                "关联: cust_company_info.code → cust_person_info.ref_cust_company_info\n"
                "## 联系人 (cust_person_info)\n"
                "user_name:varchar, 联系人姓名\n"
                "ref_cust_company_info:varchar, 企业编码\n"
                "关联: cust_person_info.ref_cust_company_info → cust_company_info.code\n"
            ),
            "tables": ["cust_company_info", "cust_person_info"],
            "evidence_fields": {"cust_company_info": ["cust_name", "code"]},
            "backend": "wiki",
        }
    )
    plane.queries.append("企业客户 cust_company_info")
    kept = expanded_tables(plane)
    assert "cust_company_info" in kept
    assert "cust_person_info" in kept


def test_field_lookup_caps_found_rows() -> None:
    plane = _ready_plane()
    payload = lookup_payload(
        plane,
        "name city industry status created_at tenant_id id",
        focus="field",
    )
    assert len(payload["focus_facts"]["found"]) <= LOOKUP_FOUND_LIMIT


def test_relation_lookup_checks_join_edge() -> None:
    plane = _ready_plane()
    plane.merge_recall(
        {
            "schema_text": _PROJECT_SCHEMA
            + "\n## 租户 (tenant)\nid:int, 主键\nname:varchar, 名称",
            "tables": ["tenant_project", "tenant"],
            "backend": "wiki",
        }
    )
    hit = lookup_payload(plane, "tenant_project tenant", focus="relation")
    assert hit["focus_facts"]["found"]
    assert hit["knowledge_text"] == ""
    miss = lookup_payload(plane, "tenant_project ghost_table", focus="relation")
    assert miss["focus_facts"]["found"] == []
    assert miss["focus_facts"]["missing"]


def test_timeline_lookup_uses_wiki_lookup_key() -> None:
    key, params = _knowledge_tool_close(
        "get_table_schema",
        {
            "ok": True,
            "data": {
                "tables": ["tenant_project"],
                "added_tables": ["tenant_project"],
            },
        },
    )
    assert key == "chat.summary.schema_loaded"
    assert params == {"count": 1}
    knowledge_key, knowledge_params = _knowledge_tool_close(
        "search_knowledge",
        {"ok": True, "data": {"hit_count": 3, "page_keys": ["a", "b", "c"]}},
    )
    assert knowledge_key == "chat.summary.wiki_prepared"
    assert knowledge_params == {"count": 3}


def test_stop_search_does_not_lock_execute_tools(monkeypatch) -> None:
    fake_tool = MagicMock()
    fake_tool.name = "get_table_schema"
    fake_tool.invoke.return_value = {
        "ok": True,
        "summary": "diminishing",
        "data": {
            "stop_search": True,
            "recall_status": "diminishing_returns",
            "focus": "all",
            "unchanged": True,
            "schema_ready": True,
            "hit_count": 0,
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
        "run_id": "focus-no-lock",
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
                        "args": {"tables": ["tenant_project"]},
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
    assert out["tool_steps"][0]["ok"] is True


_APPROVAL_SCHEMA = """## 项目审批 (tenant_project_approval)
id:int, 主键
project_id:int, 项目
status:varchar, 审批状态
关联: tenant_project_approval.project_id → tenant_project.id
"""


def test_first_search_rejects_rules_pages_on_empty_plane() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane()
    plane, policy, _delta = apply_wiki_search_policy(
        {
            "knowledge_text": "# Excel 导入规则\n很长的散文",
            "schema_text": _PROJECT_SCHEMA,
            "tables": ["tenant_project"],
            "page_keys": ["tables/tenant_project", "rules/excel-import"],
            "wiki_passages": {
                "tables/tenant_project": "# 项目主档",
                "rules/excel-import": "# Excel 导入规则\n散文污染",
            },
            "table_evidence": {"tenant_project": ["tables/tenant_project"]},
            "query": "导出项目名称城市行业",
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert "tenant_project" in plane.tables
    assert "rules/excel-import" not in plane.page_keys
    assert "rules/excel-import" not in plane.wiki_passages
    assert "rules/excel-import" in policy["rejected_pages"]
    sections = plane.render_system_sections()
    assert "散文污染" not in sections
    assert policy["recall_status"] == "hit"


def test_join_partners_admit_together_on_first_search() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane()
    plane, policy, delta = apply_wiki_search_policy(
        {
            "schema_text": _PROJECT_SCHEMA + "\n" + _APPROVAL_SCHEMA,
            "tables": ["tenant_project", "tenant_project_approval"],
            "page_keys": [
                "tables/tenant_project",
                "tables/tenant_project_approval",
            ],
            "table_evidence": {
                "tenant_project": ["tables/tenant_project"],
                "tenant_project_approval": ["tables/tenant_project_approval"],
            },
            "table_scores": {
                "tenant_project": 1.2,
                "tenant_project_approval": 1.0,
            },
            "query": "项目审批状态",
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert "tenant_project" in plane.tables
    assert "tenant_project_approval" in plane.tables
    assert delta.added_tables == ["tenant_project", "tenant_project_approval"]
    assert policy["recall_status"] == "hit"
    assert policy["rejected_tables"] == []


def test_coverage_cliff_rejects_share_table_named_pin_restores() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = _ready_plane()
    plane.merge_recall(
        {
            "query": "项目名称,城市,行业,状态,创建时间,租户,负责人",
            "evidence_fields": {
                "tenant_project": [
                    "name",
                    "city",
                    "industry",
                    "status",
                    "created_at",
                    "tenant_id",
                ]
            },
        }
    )
    plane, policy, _delta = apply_wiki_search_policy(
        {
            "schema_text": _PROJECT_SCHEMA + "\n" + _NOISE_SCHEMA,
            "tables": ["tenant_project", "tenant_setting_config"],
            "page_keys": ["tables/tenant_setting_config"],
            "table_evidence": {
                "tenant_project": ["tables/tenant_project"],
                "tenant_setting_config": ["tables/tenant_setting_config"],
            },
            "query": "项目名称,城市,行业,状态,创建时间,租户",
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert "tenant_setting_config" not in plane.tables
    assert "tenant_setting_config" in policy["rejected_tables"]
    assert policy["recall_status"] == "diminishing_returns"

    plane, policy, delta = apply_wiki_search_policy(
        {
            "schema_text": _NOISE_SCHEMA,
            "tables": ["tenant_setting_config"],
            "page_keys": ["tables/tenant_setting_config"],
            "wiki_passages": {"tables/tenant_setting_config": "# 配置"},
            "table_evidence": {
                "tenant_setting_config": ["tables/tenant_setting_config"]
            },
            "query": "tenant_setting_config",
            "backend": "wiki",
        },
        plane,
        focus="all",
    )
    assert "tenant_setting_config" in plane.tables
    assert delta.added_tables == ["tenant_setting_config"]
    assert policy["recall_status"] == "hit"


def test_search_wiki_stub_hides_peripheral_rejected_and_caps_lookup() -> None:
    from apps.chat.agent_knowledge import MergeDelta, search_wiki_stub

    plane = AgentKnowledgePlane()
    stub = search_wiki_stub(
        delta=MergeDelta(),
        policy={
            "schema_ready": True,
            "stop_search": False,
            "recall_status": "hit",
            "rejected_pages": ["rules/excel-import", "dicts/status"],
            "rejected_tables": ["tenant_setting_config"],
            "focus_facts": {
                "kind": "field",
                "found": [
                    {"table": "tenant_project", "field": f"c{i}"} for i in range(20)
                ],
            },
        },
        plane=plane,
        backend="lookup",
        hit_count=20,
    )
    assert "rules/excel-import" not in stub["rejected_pages"]
    assert "dicts/status" in stub["rejected_pages"]
    assert stub["rejected_tables"] == ["tenant_setting_config"]
    assert len(stub["focus_facts"]["found"]) == LOOKUP_FOUND_LIMIT
