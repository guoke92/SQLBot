"""Repo-map outline + orthogonal catalog tools (schema/relations/knowledge/dict)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane, KNOWLEDGE_TOOLS  # noqa: E402
from apps.chat.steps.schema_outline import render_schema_outline  # noqa: E402
from apps.chat.task.agent_prompt import _SYSTEM_PROMPT_TEMPLATE  # noqa: E402
from apps.chat.tools.catalog_tools import (  # noqa: E402
    MAX_TABLES_PER_CALL,
    classify_relations,
    filter_knowledge_passages,
    knowledge_budget_result,
    parse_relation_edges,
    render_tables_schema,
    strip_relation_lines,
)
from apps.chat.tools.registry import build_agent_tools  # noqa: E402
from apps.knowledge.wiki.recall import InMemoryWikiStore, recall  # noqa: E402


def _page(
    *,
    key: str,
    title: str,
    page_type: str,
    body: str,
    aliases: list[str] | None = None,
) -> str:
    alias_line = ""
    if aliases:
        alias_line = "aliases: [" + ", ".join(aliases) + "]\n"
    return (
        f"---\npage_key: {key}\ntype: {page_type}\ntitle: {title}\n"
        f"status: published\n{alias_line}---\n\n{body}\n"
    )


def _table_body(
    table: str,
    desc: str,
    fields: list[tuple[str, str, str]],
    *,
    relations: str = "",
) -> str:
    lines = [
        "```ground:table",
        f"table: {table}",
        f"desc: {desc}",
        "fields:",
    ]
    for name, phys, comment in fields:
        lines.append(f"  - name: {name}")
        lines.append(f"    phys: {phys}")
        lines.append(f"    desc: {comment}")
    lines.append("```")
    if relations:
        lines.append("")
        lines.append("## 关联表")
        lines.append(relations)
    return "\n".join(lines)


def _wide_project_store() -> InMemoryWikiStore:
    project_fields = [
        ("id", "bigint", "主键"),
        ("name", "varchar", "项目名称"),
        ("city", "varchar", "城市"),
        ("industry", "varchar", "行业"),
        ("status", "varchar", "状态"),
        ("owner", "varchar", "运营对接人"),
        ("approve_no", "varchar", "企微审批编号"),
        ("tenant_id", "bigint", "租户ID"),
    ]
    project_fields.extend(
        (f"col_{index}", "varchar", f"导出列{index}") for index in range(26)
    )
    return InMemoryWikiStore.load(
        [
            _page(
                key="tenant_project",
                title="租户项目基础信息表",
                page_type="table",
                body=_table_body(
                    "tenant_project",
                    "租户项目基础信息表",
                    project_fields,
                    relations=(
                        "- [[wec_project_operation_rel]]："
                        "tenant_project.id → wec_project_operation_rel.project_id"
                        "（write-flow:Op.java，confirmed）"
                    ),
                ),
            ),
            _page(
                key="wec_project_operation_rel",
                title="项目运营关系",
                page_type="table",
                body=_table_body(
                    "wec_project_operation_rel",
                    "项目运营关系",
                    [
                        ("id", "bigint", "主键"),
                        ("project_id", "bigint", "项目ID"),
                        ("op_user", "varchar", "运营人"),
                    ],
                ),
            ),
            _page(
                key="ca_fee_company",
                title="CA费用企业",
                page_type="table",
                body=_table_body(
                    "ca_fee_company",
                    "CA费用企业",
                    [("id", "bigint", "主键"), ("fee", "decimal", "费用")],
                ),
            ),
        ]
    )


def _company_person_store() -> InMemoryWikiStore:
    identify_dict = (
        "```ground:dict\n"
        "dict: identify_style\n"
        "values:\n"
        "  LICENSE:\n"
        "    label: 营业执照认证\n"
        "  BANK:\n"
        "    label: 对公打款认证\n"
        "```\n"
    )
    build_dict = (
        "```ground:dict\n"
        "dict: cust_build_type\n"
        "values:\n"
        "  1:\n"
        "    label: 平台录入\n"
        "  2:\n"
        "    label: 接口同步\n"
        "```\n"
    )
    company_fields = [
        ("id", "bigint", "主键"),
        ("code", "varchar", "企业编码"),
        ("name", "varchar", "企业名称"),
        ("identify_style", "varchar", "认证方式"),
        ("cust_build_type", "varchar", "建档类型"),
    ]
    person_fields = [
        ("id", "bigint", "主键"),
        ("name", "varchar", "联系人姓名"),
        ("ref_cust_company_info", "varchar", "所属企业"),
    ]
    return InMemoryWikiStore.load(
        [
            _page(
                key="cust_company_info",
                title="客户企业主档案",
                page_type="table",
                aliases=["企业"],
                body=_table_body(
                    "cust_company_info",
                    "客户企业主档案",
                    company_fields,
                    relations=(
                        "- [[cust_person_info]]："
                        "cust_person_info.ref_cust_company_info → cust_company_info.code"
                        "（write-flow:Person.java，confirmed）"
                    ),
                ),
            ),
            _page(
                key="cust_person_info",
                title="客户联系人信息",
                page_type="table",
                aliases=["联系人"],
                body=_table_body(
                    "cust_person_info",
                    "客户联系人信息",
                    person_fields,
                    relations=(
                        "- [[cust_company_info]]："
                        "cust_person_info.ref_cust_company_info → cust_company_info.code"
                        "（write-flow:Person.java，confirmed）"
                    ),
                ),
            ),
            _page(
                key="identify_style",
                title="认证方式",
                page_type="concept",
                aliases=["认证方式"],
                body="# 认证方式\n企业认证渠道，落在 cust_company_info.identify_style。\n",
            ),
            _page(
                key="cust_build_type",
                title="建档类型",
                page_type="caliber",
                aliases=["平台录入"],
                body="# 建档类型\n「平台录入」是建档类型取值，不是认证方式。\n",
            ),
            _page(
                key="identify_style_dict",
                title="认证方式字典",
                page_type="dict",
                body=identify_dict,
            ),
            _page(
                key="cust_build_type_dict",
                title="建档类型字典",
                page_type="dict",
                body=build_dict,
            ),
            _page(
                key="export_task_rule",
                title="导出任务规则",
                page_type="rule",
                body="# 导出任务\n操作手册，不得选表。\n",
            ),
        ]
    )


def test_schema_outline_lists_tables_without_ddl() -> None:
    store = _wide_project_store()
    text = render_schema_outline(store=store)
    assert text.startswith("<schema_outline>")
    assert "tenant_project: 租户项目基础信息表" in text
    assert "项目名称" in text
    assert "ca_fee_company" in text
    assert "phys:" not in text
    assert "bigint" not in text


def test_wide_export_schema_is_single_table_no_hops() -> None:
    store = _wide_project_store()
    schema = render_tables_schema(["tenant_project"], store=store)
    assert "tenant_project" in schema
    assert "项目名称" in schema
    assert "导出列0" in schema
    assert "关联:" not in schema
    assert "wec_project_operation_rel" not in schema


def test_relations_require_two_tables_and_keep_direct_edge() -> None:
    store = _company_person_store()
    raw = render_tables_schema(
        ["cust_company_info", "cust_person_info"], store=store
    )
    # relations are stripped from schema helper; parse from full renderer
    from apps.knowledge.recall_kernel.render import render_schema

    full = render_schema(
        ["cust_company_info", "cust_person_info"],
        store=store,
        project_relations=False,
    )
    grouped = classify_relations(
        ["cust_company_info", "cust_person_info"],
        parse_relation_edges(full),
    )
    assert grouped["direct"]
    assert any(
        item["left_table"] == "cust_person_info"
        and item["right_table"] == "cust_company_info"
        for item in grouped["direct"]
    )
    assert raw  # schema helper still returns fields
    assert "关联:" not in raw


def test_knowledge_filters_rules_and_keeps_caliber() -> None:
    store = _company_person_store()
    passages = recall("认证方式 平台录入", store, top_k=8, mode="business")
    kept = filter_knowledge_passages(passages, store)
    types = {
        store.pages[str(item.store_key)].type
        for item in kept
        if str(item.store_key) in store.pages
    }
    assert "rule" not in types
    assert types & {"concept", "caliber"}
    keys = {str(item.page_key) for item in kept}
    assert "export_task_rule" not in keys


def test_strip_relation_lines_and_budget_gate() -> None:
    text = "## 项目 (tenant_project)\nname:varchar, 项目名称\n关联: a.b → c.d (c)"
    assert "关联:" not in strip_relation_lines(text)
    plane = AgentKnowledgePlane(knowledge_rounds=2)
    blocked = knowledge_budget_result(plane)
    assert blocked is not None
    assert blocked["ok"] is False


def test_agent_tools_are_orthogonal_not_search_wiki() -> None:
    tools = build_agent_tools(SimpleNamespace(ds=None, datasource=None))
    names = {tool.name for tool in tools}
    assert "search_wiki" not in names
    assert KNOWLEDGE_TOOLS <= names
    assert "execute_sql_sandbox" in names


def test_prompt_guardrails_name_the_four_tools() -> None:
    assert "get_table_schema" in _SYSTEM_PROMPT_TEMPLATE
    assert "get_table_relations" in _SYSTEM_PROMPT_TEMPLATE
    assert "search_knowledge" in _SYSTEM_PROMPT_TEMPLATE
    assert "get_dict_values" in _SYSTEM_PROMPT_TEMPLATE
    assert "schema_outline" in _SYSTEM_PROMPT_TEMPLATE
    assert "单表禁用" in _SYSTEM_PROMPT_TEMPLATE
    assert "快速通道" in _SYSTEM_PROMPT_TEMPLATE
    assert "search_wiki" not in _SYSTEM_PROMPT_TEMPLATE
    assert "focus=all" not in _SYSTEM_PROMPT_TEMPLATE


def test_plane_renders_outline_and_full_opened_table() -> None:
    plane = AgentKnowledgePlane(schema_outline="<schema_outline>\n- tenant_project: 项目\n</schema_outline>")
    plane.merge_recall(
        {
            "schema_text": (
                "## 项目 (tenant_project)\n"
                "name:varchar, 项目名称\n"
                "city:varchar, 城市\n"
                "关联: tenant_project.id → wec_project_operation_rel.project_id (运营) （对端未入选）"
            ),
            "tables": ["tenant_project"],
        }
    )
    rendered = plane.render_system_sections()
    assert "<schema_outline>" in rendered
    assert "项目名称" in rendered
    assert "对端未入选" not in rendered


def test_max_tables_cap_constant() -> None:
    assert MAX_TABLES_PER_CALL == 3
