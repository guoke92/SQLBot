"""Agent prompt compact: wiki prose, per-page plane, schema projection."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane  # noqa: E402
from apps.chat.steps.wiki_schema import (  # noqa: E402
    OMITTED_FIELDS_PREFIX,
    RELATION_PEER_MISSING,
    WikiSchemaRenderer,
    collect_schema_evidence,
    compact_field_type,
    filter_schema_relations,
    parse_field_line,
    project_schema,
    relation_source_tag,
    relevant_fields,
)
from apps.chat.task.agent_prompt import _SYSTEM_PROMPT_TEMPLATE  # noqa: E402


def _ns_page(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def test_plane_per_page_merge_does_not_duplicate_wiki() -> None:
    plane = AgentKnowledgePlane()
    page_a = "# 口径A\n谓词 A"
    page_b = "# 口径B\n谓词 B"
    page_c = "# 口径C\n谓词 C"
    plane.merge_recall(
        {
            "knowledge_text": f"{page_a}\n\n{page_b}",
            "page_keys": ["a", "b"],
        }
    )
    plane.merge_recall(
        {
            "knowledge_text": f"{page_b}\n\n{page_c}",
            "page_keys": ["b", "c"],
        }
    )
    rendered = plane.render_system_sections()
    assert rendered.count("# 口径A") == 1
    assert rendered.count("# 口径B") == 1
    assert rendered.count("# 口径C") == 1
    assert list(plane.wiki_passages) == ["a", "b", "c"]


def test_plane_wiki_passages_upsert_beats_blob() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "wiki_passages": {"enums/pay_status": "# 缴费\nPAID = 已缴费"},
            "page_keys": ["enums/pay_status"],
            "knowledge_text": "# 缴费\nPAID = 已缴费\n\n# 缴费\nPAID = 已缴费",
        }
    )
    rendered = plane.render_system_sections()
    assert rendered.count("# 缴费") == 1
    assert "enums/pay_status" in plane.wiki_passages


def test_search_policy_strips_noise_table_without_new_pages() -> None:
    """Table gating lives in the kernel + search policy, not in the plane merge:
    a follow-up search that brings no new page may not smuggle unevidenced tables."""
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "schema_text": "## 企业 (cust_company_info)\nid:int, 主键",
            "tables": ["cust_company_info"],
            "page_keys": ["calibers/paid"],
            "wiki_passages": {"calibers/paid": "# 已缴费\n谓词"},
            "backend": "wiki",
        }
    )
    plane, policy, delta = apply_wiki_search_policy(
        {
            "schema_text": (
                "## 企业 (cust_company_info)\nid:int, 主键\n"
                "## 噪声 (cust_change_cfg)\nid:int, 主键"
            ),
            "tables": ["cust_company_info", "cust_change_cfg"],
            "table_evidence": {"cust_company_info": ["calibers/paid"]},
            "page_keys": ["calibers/paid"],
            "backend": "wiki",
        },
        plane,
    )
    assert plane.tables == ["cust_company_info"]
    assert "cust_change_cfg" not in plane.schema_by_table
    assert delta.unchanged
    assert policy["stop_search"]


def _identify_style_conflict() -> dict[str, object]:
    return {
        "conflict_id": "caliber:identify_style|cust_build_type",
        "kind": "attribution",
        "phrase": "认证方式",
        "candidates": [
            {
                "saying": "认证方式",
                "table": "cust_company_info",
                "field": "identify_style",
                "value": "INVITE_AGW",
                "value_label": "邀请认证-内管录入",
                "enum_values": [{"value": "INVITE_AGW", "label": "邀请认证-内管录入"}],
            }
        ],
    }


def test_conflicts_omit_nested_enum_only_when_enum_page_text_present() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "schema_text": (
                "## 企业 (cust_company_info)\n"
                "identify_style:varchar(32), 认证方式, topk=INVITE_AGW, enum=identify_style"
            ),
            "tables": ["cust_company_info"],
            "page_keys": ["enums/identify_style"],
            "wiki_passages": {
                "enums/identify_style": "# 认证方式\nINVITE_AGW: 邀请认证"
            },
        }
    )
    plane.adopt_conflicts([_identify_style_conflict()])
    rendered = plane.render_system_sections()
    assert "identify_style" in rendered
    assert "INVITE_AGW" in rendered
    assert "enum_values" not in rendered
    # The catalog swaps topk for the enum pointer once the page text is present.
    assert "topk=" not in plane.schema_catalog_text()
    assert "enum=identify_style" in plane.schema_catalog_text()


def test_conflicts_keep_nested_enum_when_only_concept_page_present() -> None:
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "schema_text": (
                "## 企业 (cust_company_info)\n"
                "identify_style:varchar(32), 认证方式, topk=INVITE_AGW, enum=identify_style"
            ),
            "tables": ["cust_company_info"],
            "page_keys": ["concepts/identify_style"],
            "wiki_passages": {"concepts/identify_style": "# 认证方式概念\n说明"},
        }
    )
    plane.adopt_conflicts([_identify_style_conflict()])
    rendered = plane.render_system_sections()
    assert "enum_values" in rendered
    assert "topk=INVITE_AGW" in plane.schema_catalog_text()


def test_soft_filter_rule_is_in_agent_prompt() -> None:
    assert "软过滤" in _SYSTEM_PROMPT_TEMPLATE
    assert "enable='Y'" in _SYSTEM_PROMPT_TEMPLATE
    assert "仅启用 / 含停用" in _SYSTEM_PROMPT_TEMPLATE


def test_agent_prompt_prefers_sql_accuracy_and_llm_drop() -> None:
    assert "生成准确的业务 SQL" in _SYSTEM_PROMPT_TEMPLATE
    assert "search_wiki` 的 `drop`" in _SYSTEM_PROMPT_TEMPLATE
    assert "不会因长度上限删除已入选的表" in _SYSTEM_PROMPT_TEMPLATE


def _wide_table_page(*, dict_key: str = "pay_status") -> SimpleNamespace:
    field_yaml = [
        "  - name: id\n    phys: bigint\n    desc: 主键",
        "  - name: pay_status\n    phys: varchar(16)\n    desc: 缴费状态\n"
        f"    dict: {dict_key}\n    topk: PAID|UNPAID",
        "  - name: enable\n    phys: char(1)\n    desc: 是否启用",
        "  - name: cust_id\n    phys: bigint\n    desc: 客户",
    ]
    field_yaml.extend(
        f"  - name: addr_{index}\n    phys: varchar(128)\n    desc: 开票地址{index}"
        for index in range(42)
    )
    body = (
        "```ground:table\ntable: cust_company_info\ndesc: 企业\nfields:\n"
        + "\n".join(field_yaml)
        + "\n```\n\n## 关联表\n\n"
        "- [[cust_person_info]]：cust_company_info.cust_id → cust_person_info.id"
        "（write-flow:Foo，confirmed）\n"
        "- [[ghost]]：cust_company_info.id → ghost.id（ref-convention，suggested）\n"
    )
    return _ns_page(body=body, ground_blocks=[], type="table")


def _pay_status_store() -> object:
    enum_page = _ns_page(
        type="enum",
        ground_blocks=[
            SimpleNamespace(
                kind="enum",
                data={
                    "enum": "pay_status",
                    "values": {
                        "PAID": {"label": "已缴费"},
                        "UNPAID": {"label": "未缴费"},
                    },
                },
            )
        ],
    )

    class _Store:
        pages = {
            "cust_company_info": _wide_table_page(),
            "pay_status": enum_page,
        }

    return _Store()


def test_compact_field_type_strips_display_width_keeps_scale_and_temporal() -> None:
    assert compact_field_type("varchar(128)") == "varchar"
    assert compact_field_type("bigint(20)") == "bigint"
    assert compact_field_type("char(1)") == "char"
    assert compact_field_type("int(11)") == "int"
    assert compact_field_type("datetime(6)") == "datetime"
    assert compact_field_type("decimal(18,2)") == "decimal(18,2)"
    assert compact_field_type("date") == "date"
    parsed = parse_field_line(
        "status:varchar(64), 联系人账号状态, topk=ADD|EFFECT, "
        "labels=ADD:未生效|EFFECT:已生效, enum=cust_status"
    )
    assert parsed is not None
    assert parsed.topk == "ADD|EFFECT"
    assert parsed.labels == "ADD:未生效|EFFECT:已生效"
    assert "(" not in parsed.render()
    assert parse_field_line("(id:bigint(20), 主键)") is None
    from apps.chat.presentation import schema_field_labels

    labeled = schema_field_labels(
        "## 表 (t)\n"
        "status:varchar, 联系人账号状态, topk=ADD|EFFECT, "
        "labels=ADD:未生效|EFFECT:已生效, enum=cust_status\n"
    )
    assert labeled.get("status") == "联系人账号状态"


def test_relation_source_tag_keeps_kind_drops_trust_label() -> None:
    assert relation_source_tag("write-flow:Foo.java，confirmed") == "write-flow"
    assert relation_source_tag("ref-convention，suggested") == "ref-convention"
    assert relation_source_tag("java-eq:Bar.java，suggested") == "java-eq"
    assert relation_source_tag("suggested") == ""
    assert relation_source_tag("confirmed") == ""


def test_renderer_is_full_and_relations_are_tagged() -> None:
    raw = WikiSchemaRenderer(_pay_status_store(), {}).render(["cust_company_info"])
    assert "id:bigint, 主键" in raw
    assert (
        "pay_status:varchar, 缴费状态, topk=PAID|UNPAID, "
        "labels=PAID:已缴费|UNPAID:未缴费, enum=pay_status"
    ) in raw
    assert "enable:char, 是否启用" in raw
    assert "addr_0" in raw and "addr_41" in raw  # renderer never drops fields
    person_rel = (
        "关联: cust_company_info.cust_id → cust_person_info.id (cust_person_info) [write-flow]"
    )
    ghost_rel = "关联: cust_company_info.id → ghost.id (ghost) [ref-convention]"
    assert person_rel in raw
    assert ghost_rel in raw
    text = filter_schema_relations(
        raw, peer_tables=["cust_company_info", "cust_person_info"]
    )
    assert person_rel in text
    assert "ghost" not in text


def test_projection_never_folds_and_strips_enum_values_when_page_present() -> None:
    raw = WikiSchemaRenderer(_pay_status_store(), {}).render(["cust_company_info"])
    fitted = project_schema(
        raw,
        budget_chars=600,
        queries=["CA 已缴费企业管理员"],
        present_pages=["enums/pay_status"],
    )
    assert "addr_41" in fitted.text and OMITTED_FIELDS_PREFIX not in fitted.text
    assert "topk=" not in fitted.text
    assert "labels=PAID:已缴费|UNPAID:未缴费" in fitted.text
    assert "enum=pay_status" in fitted.text
    assert fitted.enum_stripped == {"cust_company_info": ["pay_status"]}
    assert fitted.omitted == {}
    kept = project_schema(
        raw,
        budget_chars=600,
        queries=["CA 已缴费企业管理员"],
        keep_fields={"cust_company_info": {"pay_status"}},
        present_pages=["concepts/pay_status"],
    )
    assert (
        "pay_status:varchar, 缴费状态, topk=PAID|UNPAID, "
        "labels=PAID:已缴费|UNPAID:未缴费, enum=pay_status"
    ) in kept.text
    assert "id:bigint, 主键" in kept.text
    assert "addr_0:varchar, 开票地址0" in kept.text
    text = filter_schema_relations(kept.text, peer_tables=["cust_company_info"])
    assert "cust_person_info.id (cust_person_info) [write-flow]（对端未入选）" in text


def test_projection_keeps_all_fields_relevance_is_type_driven() -> None:
    schema = (
        "## 订单 (ord)\n"
        "id:bigint, 主键\n"
        "create_time:datetime, 创建时间\n"
        "amount:decimal(18,2), 金额\n"
        "business_province:varchar(64), 经营省份\n"
        "legal_name:varchar(64), 法人姓名\n"
        "memo:varchar(255), 备注\n"
        "remark2:varchar(255), 备注二\n"
    )
    projected = project_schema(schema, budget_chars=120, queries=["按省份统计法人"])
    assert "memo:varchar, 备注" in projected.text
    assert "remark2:varchar, 备注二" in projected.text
    assert projected.omitted == {}
    rel = relevant_fields(schema, queries=["按省份统计法人"])
    assert "business_province" in rel["ord"]  # 省份 ⊂ 经营省份
    assert "legal_name" in rel["ord"]  # 法人 ⊂ 法人姓名
    assert "memo" not in rel["ord"]
    assert "create_time" in rel["ord"]
    assert "amount" in rel["ord"]


def test_plane_projection_is_monotonic_across_rounds() -> None:
    raw = WikiSchemaRenderer(_pay_status_store(), {}).render(["cust_company_info"])
    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "schema_text": raw,
            "tables": ["cust_company_info"],
            "query": "CA 已缴费企业",
            "evidence_fields": {"cust_company_info": ["pay_status"]},
        }
    )
    first = plane.schema_catalog_text()
    delta = plane.merge_recall(
        {
            "schema_text": raw,
            "tables": ["cust_company_info"],
            "query": "第二轮补检索",
            "evidence_fields": {"cust_company_info": ["addr_1"]},
        }
    )
    second = plane.schema_catalog_text()
    first_full = {line for line in first.splitlines() if parse_field_line(line)}
    second_full = {line for line in second.splitlines() if parse_field_line(line)}
    assert first_full <= second_full
    assert delta.added_fields == {"cust_company_info": ["addr_1"]}
    assert not delta.unchanged
    assert plane.keep_fields == {"cust_company_info": ["pay_status", "addr_1"]}
    assert plane.knowledge_refs() == {"page_keys": [], "tables": ["cust_company_info"]}


def test_collect_schema_evidence_from_targets_and_caliber() -> None:
    caliber = _ns_page(
        field_targets=("cust_company_info.pay_status",),
        maps_to="cust_company_info.user_type",
        ground_blocks=[
            SimpleNamespace(
                kind="caliber",
                data={"predicate": "cust_company_info.enable = 'Y'"},
            )
        ],
    )

    class _Store:
        pages = {"calibers/paid": caliber}

        def get_page(self, key: str) -> object | None:
            return self.pages.get(key)

    evidence = collect_schema_evidence(
        _Store(),
        page_keys=["calibers/paid"],
        tables=["cust_company_info"],
    )
    assert evidence["cust_company_info"] == {"pay_status", "user_type", "enable"}


def test_dict_topk_kept_when_enum_page_not_in_prompt() -> None:
    enum_page = _ns_page(
        type="enum",
        ground_blocks=[
            SimpleNamespace(
                kind="enum",
                data={
                    "enum": "state",
                    "values": {"A": {"label": "甲类"}, "B": {"label": "乙类"}},
                },
            )
        ],
    )
    table_page = _ns_page(
        type="table",
        body=(
            "```ground:table\ntable: t\ndesc: 表\nfields:\n"
            "  - name: state\n    phys: varchar(64)\n    desc: 状态\n"
            "    dict: state\n    topk: A|B\n```\n"
        ),
        ground_blocks=[],
    )

    class _Store:
        pages = {"state": enum_page, "t": table_page}

    text = WikiSchemaRenderer(_Store(), {}).render(["t"])
    assert (
        "state:varchar, 状态, topk=A|B, labels=A:甲类|B:乙类, enum=state"
    ) in text
    # Projection with the enum page absent keeps topk+labels; present →
    # drop topk (values live on the enum page) but keep labels + enum pointer.
    kept = project_schema(text, present_pages=["t"]).text
    assert "topk=A|B" in kept and "labels=A:甲类|B:乙类" in kept
    stripped = project_schema(text, present_pages=["enums/state"]).text
    assert "topk=" not in stripped
    assert "labels=A:甲类|B:乙类" in stripped
    assert "enum=state" in stripped


def test_plane_relations_refresh_when_peer_table_arrives() -> None:
    """关联投影看 plane 累计表：后到的对端表要让已有 blob 上的 JOIN 现出来。"""
    company = (
        "## 企业 (cust_company_info)\n"
        "id:bigint, 主键\n"
        "code:varchar, 编码\n"
        "关联: cust_company_info.code → "
        "cust_person_info.ref_cust_company_info (cust_person_info)\n"
        "关联: cust_company_info.id → ghost.id (ghost)\n"
    )
    person = (
        "## 联系人 (cust_person_info)\n"
        "id:bigint, 主键\n"
        "ref_cust_company_info:varchar, 关联企业\n"
        "关联: cust_person_info.ref_cust_company_info → "
        "cust_company_info.code (cust_company_info)\n"
    )
    plane = AgentKnowledgePlane()
    plane.merge_recall({"schema_text": company, "tables": ["cust_company_info"]})
    first = plane.schema_catalog_text()
    assert "ghost" not in first
    assert "cust_person_info" not in first
    plane.merge_recall({"schema_text": person, "tables": ["cust_person_info"]})
    catalog = plane.schema_catalog_text()
    assert (
        "关联: cust_company_info.code → "
        "cust_person_info.ref_cust_company_info (cust_person_info)"
    ) in catalog
    assert (
        "关联: cust_person_info.ref_cust_company_info → "
        "cust_company_info.code (cust_company_info)"
    ) in catalog
    assert "ghost" not in catalog
    assert RELATION_PEER_MISSING not in catalog


def test_fk_relation_kept_when_peer_not_in_plane() -> None:
    person = (
        "## 联系人 (cust_person_info)\n"
        "id:bigint, 主键\n"
        "ref_cust_company_info:varchar, 关联企业\n"
        "关联: cust_person_info.ref_cust_company_info → "
        "cust_company_info.code (cust_company_info)\n"
    )
    plane = AgentKnowledgePlane()
    plane.merge_recall({"schema_text": person, "tables": ["cust_person_info"]})
    catalog = plane.schema_catalog_text()
    assert "ref_cust_company_info → cust_company_info.code" in catalog
    assert RELATION_PEER_MISSING in catalog
