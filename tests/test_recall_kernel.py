"""Unified recall kernel: gate, alias channel, table resolver, coverage policy."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane  # noqa: E402
from apps.knowledge.recall_kernel.tables import (  # noqa: E402
    cut_relative_tail,
    resolve_schema_vector_tables,
    resolve_wiki_tables,
    trim_schema_chars,
)
from apps.knowledge.recall_kernel.types import RecallBudget, TableCandidate  # noqa: E402
from apps.knowledge.wiki.recall import InMemoryWikiStore, recall  # noqa: E402


def _page(
    *,
    key: str,
    title: str,
    page_type: str,
    body: str,
    aliases: list[str] | None = None,
    anchors: tuple[str, ...] = (),
) -> str:
    alias_line = ""
    if aliases:
        joined = ", ".join(aliases)
        alias_line = f"aliases: [{joined}]\n"
    anchor_line = ""
    if anchors:
        anchor_line = "anchors:\n" + "".join(f"  - {item}\n" for item in anchors)
    return (
        f"---\npage_key: {key}\ntype: {page_type}\ntitle: {title}\n"
        f"status: published\n{alias_line}{anchor_line}---\n\n{body}\n"
    )


def test_table_pages_do_not_occupy_semantic_window() -> None:
    store = InMemoryWikiStore.load(
        [
            _page(
                key="authenticated-company",
                title="认证成功企业",
                page_type="caliber",
                aliases=["认证成功企业"],
                anchors=("cust_company_info",),
                body="认证成功企业口径：建档成功且认证通过。",
            ),
            _page(
                key="cust_company_info",
                title="企业表",
                page_type="table",
                body="```ground:table\ntable: cust_company_info\ndesc: 企业\nfields:\n  - name: id\n    phys: bigint\n    desc: 主键\n```\n",
            ),
            _page(
                key="noise_table",
                title="运营配置",
                page_type="table",
                body="```ground:table\ntable: tenant_setting_config\ndesc: 配置\nfields:\n  - name: id\n    phys: bigint\n    desc: 主键\n```\n",
            ),
        ]
    )
    passages = recall("认证成功企业清单", store, top_k=5, mode="business")
    kinds = {store.pages[p.store_key].type for p in passages}
    assert "table" not in kinds
    assert any(p.page_key == "authenticated-company" for p in passages)


def test_alias_is_rrf_channel_not_absolute_bonus() -> None:
    store = InMemoryWikiStore.load(
        [
            _page(
                key="authenticated-company",
                title="认证成功企业",
                page_type="caliber",
                body="认证成功企业口径正文。",
            ),
            _page(
                key="identify-style",
                title="认证方式",
                page_type="concept",
                aliases=["认证方式"],
                body="认证方式枚举页。",
            ),
        ]
    )
    passages = recall("认证成功企业的认证方式", store, top_k=5, mode="business")
    keys = [p.page_key for p in passages]
    assert "authenticated-company" in keys
    # alias 命中不应把口径页挤出窗口
    assert keys.index("authenticated-company") <= 1 or "identify-style" in keys


def test_quality_gate_rejects_weak_pages() -> None:
    store = InMemoryWikiStore.load(
        [
            _page(
                key="unrelated",
                title="无关规则",
                page_type="rule",
                body="完全无关的水电煤缴费说明。",
            ),
            _page(
                key="hit",
                title="认证成功企业",
                page_type="caliber",
                aliases=["认证成功企业"],
                body="认证成功企业口径。",
            ),
        ]
    )
    trace: dict = {}
    passages = recall("认证成功企业", store, top_k=8, mode="business", trace_out=trace)
    assert any(p.page_key == "hit" for p in passages)
    rejected = set(trace.get("gate_rejected") or [])
    assert any("unrelated" in key for key in rejected) or all(
        p.page_key != "unrelated" for p in passages
    )


def test_table_resolver_ranks_by_evidence() -> None:
    class _Page:
        def __init__(self, **kwargs: object) -> None:
            self.anchors = kwargs.get("anchors", ())
            self.field_targets = kwargs.get("field_targets", ())
            self.maps_to = kwargs.get("maps_to", "")
            self.page_key = kwargs.get("page_key", "")
            self.type = kwargs.get("type", "caliber")

    class _Store:
        def __init__(self) -> None:
            self.pages = {
                "caliber/a": _Page(anchors=("t_main",), page_key="a"),
                "caliber/b": _Page(anchors=("t_main", "t_side"), page_key="b"),
                "tables/t_main": _Page(page_key="t_main", type="table"),
                "tables/t_side": _Page(page_key="t_side", type="table"),
                "tables/t_noise": _Page(page_key="t_noise", type="table"),
            }

        def get_page(self, key: str):
            return self.pages.get(key)

        def has_table(self, table: str) -> bool:
            return f"tables/{table}" in self.pages or table in {
                "t_main",
                "t_side",
                "t_noise",
            }

    store = _Store()
    kept, cut = resolve_wiki_tables(
        store,
        page_keys=["caliber/a", "caliber/b"],
        table_pages=["tables/t_noise"],
        scores={"caliber/a": 0.9, "caliber/b": 0.8, "tables/t_noise": 0.1},
        budget=RecallBudget(max_tables=2),
    )
    names = [item.name for item in kept]
    assert names[0] == "t_main"
    assert "t_side" in names
    assert "t_noise" not in names
    assert "t_noise" not in cut


def test_table_page_joins_only_when_query_names_it() -> None:
    class _Page:
        def __init__(self, **kwargs: object) -> None:
            self.anchors = kwargs.get("anchors", ())
            self.field_targets = kwargs.get("field_targets", ())
            self.maps_to = kwargs.get("maps_to", "")
            self.page_key = kwargs.get("page_key", "")
            self.type = kwargs.get("type", "table")
            self.title = kwargs.get("title", "")
            self.aliases = kwargs.get("aliases", ())
            self.ground_blocks = ()

    class _Store:
        def __init__(self) -> None:
            self.pages = {
                "tables/t_noise": _Page(
                    page_key="t_noise", type="table", title="噪音表"
                ),
            }

        def get_page(self, key: str):
            return self.pages.get(key)

        def has_table(self, table: str) -> bool:
            return table == "t_noise"

    store = _Store()
    silent, _cut = resolve_wiki_tables(
        store,
        page_keys=[],
        table_pages=["tables/t_noise"],
        budget=RecallBudget(max_tables=4),
        query="认证方式是平台录入的企业清单",
    )
    assert silent == []
    named, _cut = resolve_wiki_tables(
        store,
        page_keys=[],
        table_pages=["tables/t_noise"],
        budget=RecallBudget(max_tables=4),
        query="t_noise 有多少行",
    )
    assert [item.name for item in named] == ["t_noise"]


def test_rule_pages_do_not_enter_semantic_window() -> None:
    store = InMemoryWikiStore.load(
        [
            _page(
                key="excel-import-rule",
                title="项目运营配置导入规则",
                page_type="rule",
                anchors=("t_noise",),
                body="项目名称 城市 行业 状态 创建时间 租户 负责人 " * 10,
            ),
            _page(
                key="project-caliber",
                title="项目清单",
                page_type="caliber",
                aliases=["项目清单"],
                anchors=("t_main",),
                body="项目清单口径：按项目主档统计。",
            ),
            _page(
                key="t_main",
                title="项目表",
                page_type="table",
                body="```ground:table\ntable: t_main\ndesc: 项目\nfields:\n  - name: name\n    phys: varchar\n    desc: 项目名称\n```\n",
            ),
            _page(
                key="t_noise",
                title="配置表",
                page_type="table",
                body="```ground:table\ntable: t_noise\ndesc: 配置\nfields:\n  - name: cfg_key\n    phys: varchar\n    desc: 配置项\n```\n",
            ),
        ]
    )
    passages = recall("项目名称 城市 行业 状态", store, top_k=8, mode="business")
    kinds = {store.pages[p.store_key].type for p in passages}
    assert "rule" not in kinds
    kept, _cut = resolve_wiki_tables(
        store,
        page_keys=[p.store_key for p in passages] + ["rules/excel-import-rule"],
        extra_keys=["rules/excel-import-rule"],
        budget=RecallBudget(max_tables=4),
    )
    assert "t_noise" not in [item.name for item in kept]


def test_resolve_wiki_tables_ignores_rule_page_anchors() -> None:
    class _Page:
        def __init__(self, **kwargs: object) -> None:
            self.anchors = kwargs.get("anchors", ())
            self.field_targets = kwargs.get("field_targets", ())
            self.maps_to = kwargs.get("maps_to", "")
            self.page_key = kwargs.get("page_key", "")
            self.type = kwargs.get("type", "caliber")

    class _Store:
        def __init__(self) -> None:
            self.pages = {
                "rules/excel": _Page(
                    anchors=("t_noise",), page_key="excel", type="rule"
                ),
                "calibers/main": _Page(anchors=("t_main",), page_key="main"),
                "tables/t_main": _Page(page_key="t_main", type="table"),
                "tables/t_noise": _Page(page_key="t_noise", type="table"),
            }

        def get_page(self, key: str):
            return self.pages.get(key)

        def has_table(self, table: str) -> bool:
            return table in {"t_main", "t_noise"}

    kept, _cut = resolve_wiki_tables(
        _Store(),
        page_keys=["rules/excel", "calibers/main"],
        scores={"rules/excel": 0.99, "calibers/main": 0.4},
        budget=RecallBudget(max_tables=4),
    )
    names = [item.name for item in kept]
    assert "t_main" in names
    assert "t_noise" not in names


def test_schema_vector_candidates_preserve_field_boost() -> None:
    scored = [
        {"kind": "table", "table_name": "d_qa_case", "score": 0.31},
        {"kind": "field", "table_name": "d_organization", "score": 0.62},
        {
            "kind": "relation",
            "table_name": "d_task",
            "peer_table": "d_project",
            "score": 0.55,
        },
    ]
    candidates = resolve_schema_vector_tables(scored, table_limit=4)
    names = [item.name for item in candidates]
    assert names[0] == "d_organization"
    assert all(item.source == "schema_vector" for item in candidates)
    assert all(item.evidence == ("schema_vector",) for item in candidates)


def test_expand_schema_working_set_keeps_seeds_and_admits_peers() -> None:
    from apps.knowledge.recall_kernel.tables import expand_schema_working_set

    seeds = [
        TableCandidate("d_task", ("schema_vector",), 0.5, "schema_vector"),
        TableCandidate("d_project", ("schema_vector",), 0.48, "schema_vector"),
        TableCandidate("d_story", ("schema_vector",), 0.45, "schema_vector"),
        TableCandidate("d_qa_bug", ("schema_vector",), 0.44, "schema_vector"),
    ]
    expanded = expand_schema_working_set(
        seeds,
        edges=[
            ("d_project", "d_organization"),
            ("d_task", "d_user"),
            ("d_story", "d_sprint"),
        ],
        scores={"d_organization": 0.31, "d_user": 0.12, "d_sprint": 0.2},
        total_limit=8,
    )
    names = [item.name for item in expanded]
    assert names[:4] == ["d_task", "d_project", "d_story", "d_qa_bug"]
    assert "d_organization" in names
    assert names.index("d_organization") < names.index("d_user")
    org = next(item for item in expanded if item.name == "d_organization")
    assert org.source == "schema_expand"
    assert org.evidence == ("schema_expand",)


def test_cut_relative_tail_keeps_join_cluster_and_drops_cliff() -> None:
    cluster = [
        TableCandidate("tenant_project", ("p1",), 2.0, "anchor"),
        TableCandidate("tenant_project_approval", ("p2",), 1.8, "anchor"),
    ]
    kept, cut = cut_relative_tail(cluster, cap=8)
    assert [item.name for item in kept] == [
        "tenant_project",
        "tenant_project_approval",
    ]
    assert cut == []

    mixed = [
        TableCandidate("tenant_project", ("p1", "p2"), 8.0, "anchor"),
        TableCandidate("share_cfg", ("p3",), 0.4, "anchor"),
    ]
    kept, cut = cut_relative_tail(mixed, cap=8)
    assert [item.name for item in kept] == ["tenant_project"]
    assert cut == ["share_cfg"]


def test_trim_schema_chars_drops_least_evidenced() -> None:
    tables = [
        TableCandidate("a", ("p1", "p2"), 2.0, "anchor"),
        TableCandidate("b", ("p1",), 1.0, "anchor"),
    ]
    bodies = {
        "a": "## A (a)\n" + "id:int, x\n" * 2,
        "b": "## B (b)\n" + "id:int, y\n" * 40,
    }
    kept, cut = trim_schema_chars(tables, bodies, schema_chars=80)
    assert [item.name for item in kept] == ["a"]
    assert cut == ["b"]


def test_coverage_policy_stops_unevidenced_tables() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane()
    first = {
        "knowledge_text": "",
        "schema_text": "## 任务 (d_task)\nid:int, 主键",
        "tables": ["d_task"],
        "page_keys": [],
        "backend": "schema_vector",
        "table_evidence": {"d_task": []},
    }
    plane, policy, delta = apply_wiki_search_policy(first, plane)
    assert delta.added_tables == ["d_task"]
    assert policy["recall_status"] == "hit"
    assert policy["stop_search"] is False

    second = {
        "knowledge_text": "",
        "schema_text": "## 噪音 (noise_table)\nid:int, 主键",
        "tables": ["noise_table"],
        "page_keys": [],
        "backend": "schema_vector",
        "table_evidence": {"noise_table": []},
    }
    plane, policy, delta = apply_wiki_search_policy(second, plane)
    assert "noise_table" not in plane.tables
    assert policy["stop_search"] is True
    assert policy["recall_status"] == "diminishing_returns"


def test_coverage_policy_keeps_evidenced_schema_expand() -> None:
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane()
    plane, _policy, _delta = apply_wiki_search_policy(
        {
            "knowledge_text": "",
            "schema_text": "## 任务 (d_task)\nid:int, 主键",
            "tables": ["d_task"],
            "page_keys": [],
            "backend": "schema_vector",
            "table_evidence": {"d_task": ["schema_vector"]},
        },
        plane,
    )
    plane, policy, delta = apply_wiki_search_policy(
        {
            "knowledge_text": "",
            "schema_text": (
                "## 任务 (d_task)\nid:int, 主键\n## 机构 (d_organization)\nid:int, 主键"
            ),
            "tables": ["d_task", "d_organization"],
            "page_keys": [],
            "backend": "schema_vector",
            "table_evidence": {
                "d_task": ["schema_vector"],
                "d_organization": ["schema_expand"],
            },
        },
        plane,
    )
    assert "d_organization" in plane.tables
    assert delta.added_tables == ["d_organization"]
    assert policy["recall_status"] == "hit"
    assert policy["stop_search"] is False


def test_bundle_payload_round_trip() -> None:
    from apps.knowledge.recall_kernel.types import RecallBundle

    bundle = RecallBundle(
        backend="wiki",
        knowledge_text="口径",
        schema_text="## 企业 (cust_company_info)\nid:bigint, 主键",
        page_keys=("calibers/authenticated-company",),
        tables=(
            TableCandidate(
                "cust_company_info",
                ("calibers/authenticated-company",),
                1.0,
                "anchor",
            ),
        ),
        hit_count=1,
        store_source="db",
        gate_rejected=("tables/noise",),
        budget_cut=("t_extra",),
    )
    payload = bundle.to_agent_payload()
    assert payload["tables"] == ["cust_company_info"]
    assert payload["table_evidence"]["cust_company_info"] == [
        "calibers/authenticated-company"
    ]
    assert payload["gate_rejected"] == ["tables/noise"]
    assert payload["budget_cut"] == ["t_extra"]
    plane = AgentKnowledgePlane()
    delta = plane.merge_recall(payload)
    assert delta.added_tables == ["cust_company_info"]
    assert plane.schema_catalog_text().startswith("## 企业")


def _conflict_store() -> InMemoryWikiStore:
    return InMemoryWikiStore.load(
        [
            (
                "---\ntype: table\ntitle: 企业\npage_key: cust_company_info\n"
                "status: published\n---\n\n"
                "```ground:table\ntable: cust_company_info\nfields:\n"
                "  - name: identify_style\n  - name: cust_build_type\n```\n"
            ),
            (
                "---\ntype: concept\ntitle: 认证方式\n"
                "page_key: concept_identify_style\nstatus: published\n"
                'maps_to: "cust_company_info.identify_style"\n'
                "field_targets: [cust_company_info.identify_style]\n"
                "adjudication: boundary\nalso_confused_with: [cust_build_status]\n"
                "---\n\n认证方式表示认证产品模式。\n"
            ),
            (
                "---\ntype: dict\ntitle: identify_style\n"
                "page_key: identify_style\nstatus: published\n---\n\n"
                "```ground:dict\ndict: identify_style\n"
                "fields: [cust_company_info.identify_style]\nvalues:\n"
                "  INVITE:\n    label: 邀请认证\n"
                "  INVITE_AGW:\n    label: 邀请认证-内管录入\n"
                "  SIMPLE:\n    label: 简易认证\n"
                "  SELF:\n    label: 自主认证\n```\n"
            ),
            (
                "---\ntype: dict\ntitle: cust_build_type\n"
                "page_key: cust_build_type\nstatus: published\n---\n\n"
                "```ground:dict\ndict: cust_build_type\n"
                "fields: [cust_company_info.cust_build_type]\nvalues:\n"
                "  AGW_BUILD:\n    label: 平台录入\n"
                "  PC_BUILD:\n    label: 客户录入\n```\n"
            ),
        ]
    )


def test_attribution_conflict_is_query_conditioned() -> None:
    from apps.knowledge.recall_kernel.conflicts import detect_caliber_conflicts

    store = _conflict_store()
    conflicts = detect_caliber_conflicts(
        store, "提取25年6月之前认证方式是平台录入 建档的企业清单"
    )
    assert len(conflicts) == 1
    fields = {(opt["table"], opt["field"]) for opt in conflicts[0].candidates}
    assert fields == {
        ("cust_company_info", "identify_style"),
        ("cust_company_info", "cust_build_type"),
    }
    sayings = {opt["saying"] for opt in conflicts[0].candidates}
    assert "平台录入" in sayings
    assert "认证方式" in sayings
    identify = next(
        opt for opt in conflicts[0].candidates if opt["field"] == "identify_style"
    )
    assert any(
        item.get("label") == "邀请认证-内管录入"
        for item in identify.get("enum_values") or []
    )
    evidence = conflicts[0].to_evidence()
    assert "question" not in evidence
    assert "options" not in evidence
    assert evidence["kind"] == "attribution"
    independent = detect_caliber_conflicts(store, "查询企业名称和认证方式")
    assert independent == ()


def test_value_hits_complete_attribution_without_dict_page() -> None:
    """Value-index label can supply the value side when wiki dict is absent."""
    from apps.datasource.instance_index.service import ValueAnchor
    from apps.knowledge.recall_kernel.conflicts import detect_caliber_conflicts
    from apps.knowledge.wiki.recall import InMemoryWikiStore

    store = InMemoryWikiStore.load(
        [
            (
                "---\ntype: table\ntitle: 企业\npage_key: cust_company_info\n"
                "status: published\n---\n\n"
                "```ground:table\ntable: cust_company_info\nfields:\n"
                "  - name: identify_style\n    desc: 认证方式\n"
                "    dict: [INVITE_AGW, INVITE]\n"
                "  - name: cust_build_type\n    desc: 录入方式\n"
                "    dict: [AGW_BUILD, PC_BUILD]\n```\n"
            ),
        ]
    )
    query = "提取25年6月之前认证方式是平台录入 建档的企业清单"
    # Dimension from field desc alone is not enough without a value binding.
    assert detect_caliber_conflicts(store, query) == ()
    hits = [
        ValueAnchor(
            table_name="cust_company_info",
            field_name="cust_build_type",
            raw_value="平台录入",
            val_type="enum_label",
            matched_text="平台录入",
            extra={"code": "AGW_BUILD"},
        )
    ]
    conflicts = detect_caliber_conflicts(store, query, value_hits=hits)
    assert len(conflicts) == 1
    assert conflicts[0].kind == "attribution"
    fields = {(opt["table"], opt["field"]) for opt in conflicts[0].candidates}
    assert fields == {
        ("cust_company_info", "identify_style"),
        ("cust_company_info", "cust_build_type"),
    }
    build = next(
        opt for opt in conflicts[0].candidates if opt["field"] == "cust_build_type"
    )
    assert build["value"] == "AGW_BUILD"
    assert build["value_label"] == "平台录入"


def test_table_field_desc_and_dict_label_attribution() -> None:
    """Field desc (dimension) + dict label (value) without a concept page."""
    from apps.knowledge.recall_kernel.conflicts import detect_caliber_conflicts
    from apps.knowledge.wiki.recall import InMemoryWikiStore

    store = InMemoryWikiStore.load(
        [
            (
                "---\ntype: table\ntitle: 企业\npage_key: cust_company_info\n"
                "status: published\n---\n\n"
                "```ground:table\ntable: cust_company_info\nfields:\n"
                "  - name: identify_style\n    desc: 认证方式\n"
                "    dict: [INVITE_AGW, INVITE]\n"
                "  - name: cust_build_type\n    desc: 录入方式\n"
                "    dict: [AGW_BUILD, PC_BUILD]\n```\n"
            ),
            (
                "---\ntype: dict\ntitle: cust_build_type\n"
                "page_key: cust_build_type\nstatus: published\n---\n\n"
                "```ground:dict\ndict: cust_build_type\n"
                "fields: [cust_company_info.cust_build_type]\nvalues:\n"
                "  AGW_BUILD:\n    label: 平台录入\n"
                "  PC_BUILD:\n    label: 客户录入\n```\n"
            ),
        ]
    )
    conflicts = detect_caliber_conflicts(
        store, "提取25年6月之前认证方式是平台录入 建档的企业清单"
    )
    assert len(conflicts) == 1
    assert conflicts[0].kind == "attribution"
    fields = {(opt["table"], opt["field"]) for opt in conflicts[0].candidates}
    assert fields == {
        ("cust_company_info", "identify_style"),
        ("cust_company_info", "cust_build_type"),
    }


def test_value_hit_alone_is_not_a_conflict() -> None:
    """A lone value-index hit is evidence, not an automatic conflict."""
    from apps.datasource.instance_index.service import ValueAnchor
    from apps.knowledge.recall_kernel.conflicts import detect_caliber_conflicts

    hits = [
        ValueAnchor(
            table_name="cust_company_info",
            field_name="cust_build_type",
            raw_value="平台录入",
            val_type="enum_label",
            matched_text="平台录入",
            extra={"code": "AGW_BUILD"},
        )
    ]
    assert (
        detect_caliber_conflicts(
            None, "平台录入建档的企业清单", value_hits=hits
        )
        == ()
    )


def test_pin_keys_keep_conflict_pages_in_window() -> None:
    pages = [
        _page(
            key=f"rule-{index}",
            title=f"企业规则{index}",
            page_type="rule",
            body=f"企业清单通用规则{index}。",
        )
        for index in range(8)
    ]
    pages.append(
        _page(
            key="cust_build_type",
            title="录入方式",
            page_type="dict",
            body="平台录入枚举。",
        )
    )
    store = InMemoryWikiStore.load(pages)
    pin = "dicts/cust_build_type"
    unpinned = recall("企业清单", store, top_k=8, mode="business")
    assert all(p.page_key != "cust_build_type" for p in unpinned)
    pinned = recall("企业清单", store, top_k=8, mode="business", pin_keys=[pin])
    assert any(p.page_key == "cust_build_type" for p in pinned)
    assert len(pinned) <= 8
