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
    extra_front: str = "",
) -> str:
    alias_line = ""
    if aliases:
        alias_line = "aliases: [" + ", ".join(aliases) + "]\n"
    return (
        f"---\npage_key: {key}\ntype: {page_type}\ntitle: {title}\n"
        f"status: published\n{alias_line}{extra_front}---\n\n{body}\n"
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
                extra_front=(
                    "maps_to: cust_company_info.identify_style\n"
                    "field_targets: [cust_company_info.identify_style]\n"
                    "also_confused_with: [cust_build_type]\n"
                    "adjudication: boundary\n"
                ),
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
            _page(
                key="company_build",
                title="企业建档",
                page_type="scenario",
                aliases=["企业建档"],
                body=(
                    "# 企业建档\n"
                    "```ground:scenario\n"
                    "scenario: company_build\n"
                    "hubs:\n"
                    "- table: cust_company_info\n"
                    "  role: master\n"
                    "shared:\n"
                    "- table: cust_person_info\n"
                    "  role: admin_person\n"
                    "```\n"
                ),
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
    raw = render_tables_schema(["cust_company_info", "cust_person_info"], store=store)
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

    scenario_passages = recall("企业建档", store, top_k=8, mode="business")
    scenario_kept = filter_knowledge_passages(scenario_passages, store)
    scenario_types = {
        store.pages[str(item.store_key)].type
        for item in scenario_kept
        if str(item.store_key) in store.pages
    }
    assert "scenario" in scenario_types


def test_strip_relation_lines_and_budget_gate() -> None:
    text = "## 项目 (tenant_project)\nname:varchar, 项目名称\n关联: a.b → c.d (c)"
    assert "关联:" not in strip_relation_lines(text)
    from apps.chat.tools import catalog_tools as ct

    assert not hasattr(ct, "knowledge_budget_result")
    plane = AgentKnowledgePlane(knowledge_rounds=8)
    assert int(plane.knowledge_rounds) == 8


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
    assert "lookup_values" in _SYSTEM_PROMPT_TEMPLATE
    assert "get_dict_values" in _SYSTEM_PROMPT_TEMPLATE
    assert "schema_outline" in _SYSTEM_PROMPT_TEMPLATE
    assert "单表禁用" in _SYSTEM_PROMPT_TEMPLATE
    assert "单表直查" in _SYSTEM_PROMPT_TEMPLATE
    assert "lookup_values" in _SYSTEM_PROMPT_TEMPLATE
    assert "match_hint=contains" in _SYSTEM_PROMPT_TEMPLATE
    assert "display_name" in _SYSTEM_PROMPT_TEMPLATE
    assert "focus=all" not in _SYSTEM_PROMPT_TEMPLATE
    assert "value_grounding" not in _SYSTEM_PROMPT_TEMPLATE
    assert "caliber_conflicts" not in _SYSTEM_PROMPT_TEMPLATE
    assert "硬预算" not in _SYSTEM_PROMPT_TEMPLATE
    assert "轮次建议" not in _SYSTEM_PROMPT_TEMPLATE
    assert "按需调用" in _SYSTEM_PROMPT_TEMPLATE
    assert "全对话最多" not in _SYSTEM_PROMPT_TEMPLATE


def test_plane_renders_outline_and_full_opened_table() -> None:
    plane = AgentKnowledgePlane(
        schema_outline="<schema_outline>\n- tenant_project: 项目\n</schema_outline>"
    )
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
    assert "项目名称" not in rendered
    assert "tenant_project" in plane.schema_catalog_text()
    assert "项目名称" in plane.schema_catalog_text()
    assert "对端未入选" not in plane.schema_catalog_text()


def test_max_tables_cap_constant() -> None:
    assert MAX_TABLES_PER_CALL == 3


def test_inline_dict_and_label_render_on_schema() -> None:
    body = (
        "```ground:table\n"
        "table: cust_company_info\n"
        "desc: 客户企业主档案\n"
        "fields:\n"
        "  - name: cust_build_type\n"
        "    phys: varchar\n"
        "    desc: 建档类型\n"
        "    dict: [AGW_BUILD, PC_BUILD]\n"
        "    label:\n"
        "      AGW_BUILD: 平台录入\n"
        "      PC_BUILD: 客户录入\n"
        "```\n"
    )
    store = InMemoryWikiStore.load(
        [
            _page(
                key="cust_company_info",
                title="客户企业主档案",
                page_type="table",
                body=body,
            )
        ]
    )
    schema = render_tables_schema(["cust_company_info"], store=store)
    assert "topk=AGW_BUILD|PC_BUILD" in schema
    assert "labels=" in schema
    assert "平台录入" in schema
    assert "AGW_BUILD" in schema


def test_get_dict_values_resolves_unprefixed_and_inline(monkeypatch) -> None:
    from apps.chat.tools import catalog_tools as ct
    from apps.chat.tools.catalog_tools import get_dict_values

    store = _company_person_store()
    plane = AgentKnowledgePlane()
    monkeypatch.setattr(ct, "load_plane", lambda: plane)
    monkeypatch.setattr(ct, "save_plane", lambda _p: None)
    monkeypatch.setattr(ct, "_catalog_sources", lambda _svc: (store, {}, []))
    monkeypatch.setattr(ct, "_value_index_field_values", lambda *_a, **_k: [])

    result = get_dict_values(SimpleNamespace(ds=None), dict_name="cust_build_type")
    assert result["ok"] is True
    values = (result.get("data") or {}).get("values") or []
    labels = {item["label"] for item in values}
    assert "平台录入" in labels

    inline_body = (
        "```ground:table\n"
        "table: cust_company_info\n"
        "desc: 客户企业\n"
        "fields:\n"
        "  - name: cust_build_type\n"
        "    phys: varchar\n"
        "    desc: 建档类型\n"
        "    dict: [AGW_BUILD, PC_BUILD]\n"
        "    label:\n"
        "      AGW_BUILD: 平台录入\n"
        "      PC_BUILD: 客户录入\n"
        "```\n"
    )
    inline_store = InMemoryWikiStore.load(
        [
            _page(
                key="cust_company_info",
                title="客户企业",
                page_type="table",
                body=inline_body,
            )
        ]
    )
    monkeypatch.setattr(ct, "_catalog_sources", lambda _svc: (inline_store, {}, []))
    inline = get_dict_values(
        SimpleNamespace(ds=None),
        table="cust_company_info",
        field="cust_build_type",
    )
    assert inline["ok"] is True
    inline_values = (inline.get("data") or {}).get("values") or []
    assert any(item["value"] == "AGW_BUILD" for item in inline_values)
    assert any(item["label"] == "平台录入" for item in inline_values)


def test_catalog_summary_not_recalled_in_search_knowledge() -> None:
    summary_page = _page(
        key="catalog_summary",
        title="全库表骨架",
        page_type="concept",
        body="# 全库表骨架\n\n- tenant_project: 项目运营配置(渠道, 对接人)\n- cust_company_info: 企业主表\n",
        aliases=["Catalog Summary", "表目录", "库表一览"],
    )
    caliber_page = _page(
        key="agw_build",
        title="平台录入",
        page_type="caliber",
        body="# 平台录入\n「平台录入」是建档类型取值。\n",
        aliases=["平台录入"],
    )
    store = InMemoryWikiStore.load([summary_page, caliber_page])
    passages = recall("平台录入 库表一览", store, top_k=8, mode="business")
    keys = {p.page_key for p in passages}
    assert "catalog_summary" not in keys
    assert "agw_build" in keys
    from apps.knowledge.wiki.contract import parse_page

    parsed = parse_page(summary_page)
    assert parsed.page_key == "catalog_summary"
    assert parsed.recall is False


def test_render_schema_outline_prefers_db_catalog_summary() -> None:
    summary_page = _page(
        key="catalog_summary",
        title="全库表骨架",
        page_type="concept",
        body=(
            "# 全库表骨架\n\n"
            "## project\n"
            "- tenant_project: 租户项目全量运营配置(项目ID, 渠道码, 运营对接人A/B)\n"
            "- secret_table: 机密表\n"
        ),
    )
    store = InMemoryWikiStore.load([summary_page])
    text = render_schema_outline(store=store)
    assert "<schema_outline>" in text
    assert "tenant_project: 租户项目全量运营配置(项目ID, 渠道码, 运营对接人A/B)" in text
    assert "secret_table" in text

    scoped_text = render_schema_outline(
        store=store,
        access_scope=SimpleNamespace(resource_names=("tenant_project",)),
    )
    assert "tenant_project" in scoped_text
    assert "secret_table" in scoped_text


def test_render_schema_outline_keeps_comment_and_catalog_blurb() -> None:
    from apps.chat.steps.schema_outline import (
        merge_comment_and_blurb,
        parse_catalog_table_lines,
    )

    assert (
        merge_comment_and_blurb("企业立项申请表", "企业立项申请表") == "企业立项申请表"
    )
    merged = merge_comment_and_blurb(
        "企业立项申请表",
        "[核心主档大宽表] 企微立项审批流申请(企微审批号sp_no)",
    )
    assert merged.startswith("企业立项申请表")
    assert "企微立项审批流申请" in merged

    summary_page = _page(
        key="catalog_summary",
        title="全库表骨架",
        page_type="concept",
        body=(
            "# 全库表骨架\n\n"
            "- wechat_project_approval_apply: [核心主档大宽表] "
            "企微立项审批流申请(企微审批号sp_no)\n"
            "- wec_project_cust_operation_rel: 微企链企业运营对接(关联ID)\n"
        ),
    )
    table_page = _page(
        key="wechat_project_approval_apply",
        title="企业立项申请表",
        page_type="table",
        body=_table_body(
            "wechat_project_approval_apply",
            "企业立项申请表",
            [("sp_no", "varchar", "企微审批编号")],
        ),
    )
    store = InMemoryWikiStore.load([summary_page, table_page])
    text = render_schema_outline(store=store)
    apply_line = next(
        line
        for line in text.splitlines()
        if line.startswith("- wechat_project_approval_apply:")
    )
    assert "企业立项申请表" in apply_line
    assert "企微立项审批流申请" in apply_line
    assert "wec_project_cust_operation_rel" in text
    parsed = parse_catalog_table_lines(
        "- wechat_project_approval_apply: 企微立项审批流申请(sp_no)\n"
    )
    assert parsed["wechat_project_approval_apply"] == "企微立项审批流申请(sp_no)"


def test_catalog_summary_keeps_official_comment_for_wechat_apply() -> None:
    text = (
        Path(__file__).resolve().parents[1] / "docs/wiki/v3/concepts/catalog_summary.md"
    ).read_text(encoding="utf-8")
    apply_line = next(
        line
        for line in text.splitlines()
        if line.startswith("- wechat_project_approval_apply:")
    )
    assert "企业立项申请表" in apply_line
    assert "企微立项审批流申请" in apply_line
    for table in (
        "tenant_product_client",
        "tenant_product_site",
        "sys_cust_org",
        "sys_cust_org_rel",
        "sys_cust_org_user_rel",
        "argeement_migratory_record_bak",
    ):
        assert f"- {table}:" in text


def test_search_knowledge_returns_structured_hits(monkeypatch) -> None:
    from apps.chat.tools import catalog_tools as ct
    from apps.chat.tools.catalog_tools import search_knowledge
    from apps.knowledge.wiki.hit import project_knowledge_hit

    store = _company_person_store()
    page = store.get_page("identify_style")
    assert page is not None
    hit = project_knowledge_hit(page)
    assert hit["maps_to"] == "cust_company_info.identify_style"
    assert hit["adjudication"] == "boundary"

    plane = AgentKnowledgePlane()
    monkeypatch.setattr(ct, "load_plane", lambda: plane)
    monkeypatch.setattr(ct, "save_plane", lambda _p: None)
    monkeypatch.setattr(ct, "_catalog_sources", lambda _svc: (store, {}, []))

    result = search_knowledge(SimpleNamespace(ds=None), "认证方式 平台录入")
    assert result["ok"] is True
    hits = (result.get("data") or {}).get("hits") or []
    keys = {item["page_key"] for item in hits}
    assert "catalog_summary" not in keys
    types = {item["type"] for item in hits}
    assert "scenario" in types or "concept" in types or "caliber" in types
    identify = next(
        (item for item in hits if item["page_key"] == "identify_style"), None
    )
    if identify is not None:
        assert identify["maps_to"] == "cust_company_info.identify_style"
        assert identify["adjudication"] == "boundary"
    scenario = next(
        (item for item in hits if item["page_key"] == "company_build"), None
    )
    if scenario is not None:
        assert scenario["hubs"]


def test_relations_empty_graph_does_not_forbid_join() -> None:
    from apps.chat.tools.catalog_tools import classify_relations, parse_relation_edges

    grouped = classify_relations(["alpha", "beta"], parse_relation_edges(""))
    assert grouped["direct"] == []
    # Tool summary is assembled in get_table_relations; the data contract stays
    # advisory — empty graph is not a hard JOIN stop.
    assert "bridges" in grouped


def test_relation_edges_include_trust() -> None:
    from apps.chat.tools.catalog_tools import relation_edges_from_store

    store = InMemoryWikiStore.load(
        [
            _page(
                key="cust_account_info",
                title="银行账户",
                page_type="table",
                body=(
                    "```ground:table\n"
                    "table: cust_account_info\n"
                    "desc: 账户\n"
                    "fields:\n"
                    "  - name: ref_cust_company_info\n"
                    "    phys: varchar\n"
                    "    desc: 企业编码\n"
                    "```\n"
                    "```ground:relation\n"
                    "type: EQUI_JOIN\n"
                    "left: cust_company_info.code\n"
                    "right: cust_account_info.ref_cust_company_info\n"
                    "trust: confirmed\n"
                    "```\n"
                ),
            )
        ]
    )
    edges = relation_edges_from_store(store, ["cust_account_info", "cust_company_info"])
    assert edges
    assert edges[0]["trust"] == "confirmed"
    assert "禁止 JOIN" not in edges[0]["line"]


def test_lookup_values_skips_closed_concept_alias(monkeypatch) -> None:
    from apps.chat.tools import catalog_tools as ct
    from apps.chat.tools.catalog_tools import lookup_values

    store = InMemoryWikiStore.load(
        [
            _page(
                key="agw_build",
                title="平台录入",
                page_type="caliber",
                body="# 平台录入\n建档类型取值。\n",
                aliases=["平台录入"],
            )
        ]
    )
    monkeypatch.setattr(ct, "load_plane", lambda: AgentKnowledgePlane())
    monkeypatch.setattr(ct, "save_plane", lambda _p: None)
    monkeypatch.setattr(ct, "_catalog_sources", lambda _svc: (store, {}, []))
    result = lookup_values(SimpleNamespace(ds=SimpleNamespace(id=1)), ["平台录入"])
    assert result["ok"] is False
    assert "概念" in str(result.get("error") or result.get("summary") or "")


def test_search_knowledge_page_keys_are_store_keys(monkeypatch) -> None:
    from apps.chat.tools import catalog_tools as ct
    from apps.chat.tools.catalog_tools import search_knowledge

    store = _company_person_store()
    plane = AgentKnowledgePlane()
    monkeypatch.setattr(ct, "load_plane", lambda: plane)
    monkeypatch.setattr(ct, "save_plane", lambda _p: None)
    monkeypatch.setattr(ct, "_catalog_sources", lambda _svc: (store, {}, []))
    result = search_knowledge(SimpleNamespace(ds=None), "认证方式")
    keys = (result.get("data") or {}).get("page_keys") or []
    assert keys
    assert all("/" in str(key) for key in keys)


def test_default_wiki_pages_parse() -> None:
    from apps.knowledge.wiki.contract import parse_page
    from apps.knowledge.wiki.default_corpus import (
        render_default_catalog_summary,
        render_default_table_page,
    )

    field = SimpleNamespace(
        field_name="name",
        field_type="varchar",
        custom_comment="名称",
        field_comment="",
    )
    table_md = render_default_table_page(
        table_name="tenant_project",
        title="项目",
        database="app",
        fields=[field],
        today="2026-09-20",
    )
    page = parse_page(table_md, belong="tables")
    assert page.page_key == "tenant_project"
    assert page.recall is True
    summary = render_default_catalog_summary(
        [("tenant_project", "项目", ["name"])],
        database="app",
        today="2026-09-20",
    )
    concept = parse_page(summary, belong="concepts")
    assert concept.page_key == "catalog_summary"
    assert concept.recall is False
