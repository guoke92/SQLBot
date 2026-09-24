"""Nomination engine + value-index reverse lookup (no live datasource)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane  # noqa: E402
from apps.chat.steps.wiki_schema import parse_field_enum  # noqa: E402
from apps.datasource.instance_index.extractor import (  # noqa: E402
    collect_wiki_enum_payloads,
    payloads_to_models,
)
from apps.datasource.instance_index.nomination import (  # noqa: E402
    looks_like_opaque_instance_values,
    nominate_instance_column,
    skip_instance_column,
)
from apps.datasource.instance_index.service import (  # noqa: E402
    rank_value_hits,
    render_value_grounding,
)
from apps.datasource.models.value_index import CoreValueIndex  # noqa: E402
from apps.knowledge.wiki.recall import InMemoryWikiStore  # noqa: E402


def test_nomination_skips_audit_time_pk_pii() -> None:
    assert skip_instance_column("create_user") == "audit_user"
    assert skip_instance_column("update_time") == "temporal_name"
    assert skip_instance_column("id") == "surrogate_pk"
    assert skip_instance_column("org_id") == "surrogate_fk"
    assert skip_instance_column("mobile") == "pii"
    assert skip_instance_column("payload", mysql_type="json") == "temporal_or_blob_type"
    assert skip_instance_column("cust_name") == ""


def test_nomination_accepts_business_name_and_code() -> None:
    assert nominate_instance_column("cust_name")
    assert nominate_instance_column("company_name")
    assert nominate_instance_column("channel_code")
    assert nominate_instance_column("certification_no", comment="统一社会信用代码")
    assert nominate_instance_column("cust_status")
    assert not nominate_instance_column("create_time")
    assert not nominate_instance_column("ref_cust_id")
    from apps.datasource.instance_index.nomination import consider_instance_column

    assert consider_instance_column("solution_manager")
    assert not nominate_instance_column("solution_manager")
    assert not consider_instance_column("payload", mysql_type="json")
    assert not consider_instance_column("create_user")


def test_opaque_instance_values() -> None:
    assert looks_like_opaque_instance_values(
        [{"value": "550e8400-e29b-41d4-a716-446655440000"}]
    )
    assert looks_like_opaque_instance_values([{"value": "12345678901234567"}])
    assert not looks_like_opaque_instance_values(
        [{"value": "深圳市前海一方商业保理有限公司"}]
    )
    assert not looks_like_opaque_instance_values(
        [{"value": '["LiuNing","HaoDeSheng"]'}]
    )


def test_parse_field_enum_inline_dict_and_label_map() -> None:
    spec = parse_field_enum(
        {
            "name": "cust_build_type",
            "dict": ["AGW_BUILD", "PC_BUILD"],
            "label": {"AGW_BUILD": "平台录入", "PC_BUILD": "客户录入"},
        },
        table="cust_company_info",
    )
    assert spec.codes == ("AGW_BUILD", "PC_BUILD")
    assert spec.labels["AGW_BUILD"] == "平台录入"
    assert spec.owned_labels is True
    assert "AGW_BUILD" in spec.topk
    assert "平台录入" in spec.label_tail


def test_wiki_enum_payloads_and_question_match() -> None:
    store = InMemoryWikiStore.load(
        [
            (
                "---\npage_key: cust_company_info\ntype: table\ntitle: 企业\n"
                "status: published\n---\n\n"
                "```ground:table\n"
                "table: cust_company_info\n"
                "desc: 企业\n"
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
        ]
    )
    payloads = collect_wiki_enum_payloads(store, "cust_company_info")
    types = {item[2] for item in payloads}
    assert "enum_code" in types
    assert "enum_label" in types
    models = payloads_to_models(8, payloads)
    hits = rank_value_hits(models, "25年6月前平台录入企业")
    assert hits
    assert hits[0].table_name == "cust_company_info"
    assert hits[0].field_name == "cust_build_type"
    assert hits[0].val_type == "enum_label"
    text = render_value_grounding(hits)
    assert "平台录入" in text
    assert "cust_company_info.cust_build_type" in text
    assert "AGW_BUILD" in text
    assert "候选:" in text
    assert "匹配字段" not in text


def test_access_scope_filters_value_hits() -> None:
    rows = [
        CoreValueIndex(
            ds_id=1,
            table_name="secret_table",
            field_name="name",
            val_type="instance",
            raw_value="研发二部",
            normalized_value="研发二部",
        ),
        CoreValueIndex(
            ds_id=1,
            table_name="d_organization",
            field_name="org_name",
            val_type="instance",
            raw_value="研发二部",
            normalized_value="研发二部",
        ),
    ]
    hits = rank_value_hits(rows, "研发二部人数", allowed_tables={"d_organization"})
    assert [item.table_name for item in hits] == ["d_organization"]


def test_plane_does_not_render_value_grounding() -> None:
    plane = AgentKnowledgePlane(
        value_grounding='候选: "平台录入" → cust_company_info.cust_build_type（枚举值 AGW_BUILD）'
    )
    rendered = plane.render_system_sections()
    assert "<value_grounding>" not in rendered
    assert "cust_company_info.cust_build_type" not in rendered


def test_instance_extract_skips_when_protocol_unsupported() -> None:
    from apps.datasource.instance_index.extractor import collect_instance_payloads

    proto = SimpleNamespace(
        profile_field=lambda *args, **kwargs: SimpleNamespace(
            supported=False, top_values=[]
        )
    )
    ds = SimpleNamespace(id=1)
    table = SimpleNamespace(table_name="cust_company_info", database_name=None)
    field = SimpleNamespace(
        field_name="cust_name",
        field_type="varchar",
        field_comment="企业名称",
        custom_comment="企业名称",
    )
    assert collect_instance_payloads(proto, ds, table, [field], enum_fields=set()) == []


def test_value_anchor_prefers_enum_label_over_instance() -> None:
    rows = [
        CoreValueIndex(
            ds_id=1,
            table_name="cust_company_info",
            field_name="cust_build_type",
            val_type="instance",
            raw_value="平台录入",
            normalized_value="平台录入",
        ),
        CoreValueIndex(
            ds_id=1,
            table_name="cust_company_info",
            field_name="cust_build_type",
            val_type="enum_label",
            raw_value="平台录入",
            normalized_value="平台录入",
            extra={"code": "AGW_BUILD"},
        ),
    ]
    hits = rank_value_hits(rows, "平台录入企业")
    assert len(hits) == 1
    assert hits[0].val_type == "enum_label"
    assert (hits[0].extra or {}).get("code") == "AGW_BUILD"


def test_select_extract_scope_checked_or_all() -> None:
    from apps.datasource.instance_index.extractor import select_extract_scope

    mixed = [
        SimpleNamespace(checked=True, name="kept"),
        SimpleNamespace(checked=False, name="dropped"),
    ]
    assert [item.name for item in select_extract_scope(mixed)] == ["kept"]
    none_checked = [
        SimpleNamespace(checked=False, name="a"),
        SimpleNamespace(checked=False, name="b"),
    ]
    assert [item.name for item in select_extract_scope(none_checked)] == ["a", "b"]


def test_phrase_lookup_completes_instance_fragment() -> None:
    rows = [
        CoreValueIndex(
            ds_id=1,
            table_name="d_organization",
            field_name="org_name",
            val_type="instance",
            raw_value="研发二部",
            normalized_value="研发二部",
        )
    ]
    hits = rank_value_hits(rows, "二部", reverse=True)
    assert hits
    assert hits[0].raw_value == "研发二部"
    assert hits[0].table_name == "d_organization"
    assert hits[0].field_name == "org_name"


def test_lookup_values_skips_dates_not_dept_phrases() -> None:
    from apps.chat.tools.catalog_tools import _lookup_skip_reason

    assert _lookup_skip_reason("2024-06", closed=set())
    assert _lookup_skip_reason("25", closed=set())
    assert not _lookup_skip_reason("二部", closed=set())
    assert _lookup_skip_reason("平台录入", closed={"平台录入"})


def test_instance_cell_keeps_raw_and_tokens() -> None:
    from apps.datasource.instance_index.cells import (
        instance_cell_entries,
        tokenize_cell,
    )

    tokens = tokenize_cell('["LiuNing","HaoDeSheng"]')
    assert tokens == ["LiuNing", "HaoDeSheng"]
    entries = instance_cell_entries('["LiuNing","HaoDeSheng"]', count=3)
    values = {item[0] for item in entries}
    assert '["LiuNing","HaoDeSheng"]' in values
    assert "LiuNing" in values
    assert "HaoDeSheng" in values
    extras = {item[0]: item[1] or {} for item in entries}
    assert extras['["LiuNing","HaoDeSheng"]'].get("raw_cell") is True
    assert extras["LiuNing"].get("token_of") == '["LiuNing","HaoDeSheng"]'
    comma = instance_cell_entries("刘宁，郝德生")
    assert {item[0] for item in comma} >= {"刘宁，郝德生", "刘宁", "郝德生"}


def test_llm_pick_includes_solution_manager_json() -> None:
    from apps.datasource.instance_index.extractor import collect_instance_payloads

    proto = SimpleNamespace(
        profile_field=lambda *args, **kwargs: SimpleNamespace(
            supported=True,
            top_values=[{"value": '["LiuNing","HaoDeSheng"]', "count": 4}],
        )
    )
    ds = SimpleNamespace(id=1)
    table = SimpleNamespace(
        table_name="wechat_project_approval_apply", database_name=None
    )
    field = SimpleNamespace(
        field_name="solution_manager",
        field_type="varchar",
        field_comment="方案经理",
        custom_comment="方案经理",
    )

    def _picker(table_name: str, columns: list) -> set[str]:
        assert table_name == "wechat_project_approval_apply"
        names = {str(item.get("name")) for item in columns}
        assert "solution_manager" in names
        return {"solution_manager"}

    payloads = collect_instance_payloads(
        proto,
        ds,
        table,
        [field],
        enum_fields=set(),
        column_picker=_picker,
    )
    values = {item[3] for item in payloads}
    assert '["LiuNing","HaoDeSheng"]' in values
    assert "LiuNing" in values
    assert "HaoDeSheng" in values
    assert all(item[2] == "instance" for item in payloads)


def test_llm_pick_failure_keeps_sampled_columns() -> None:
    from apps.datasource.instance_index.extractor import collect_instance_payloads

    proto = SimpleNamespace(
        profile_field=lambda *args, **kwargs: SimpleNamespace(
            supported=True,
            top_values=[{"value": "刘宁", "count": 2}],
        )
    )
    field = SimpleNamespace(
        field_name="solution_manager",
        field_type="varchar",
        field_comment="方案经理",
        custom_comment="方案经理",
    )
    payloads = collect_instance_payloads(
        proto,
        SimpleNamespace(id=1),
        SimpleNamespace(table_name="wechat_project_approval_apply", database_name=None),
        [field],
        enum_fields=set(),
        column_picker=lambda _t, _c: (_ for _ in ()).throw(RuntimeError("llm down")),
    )
    assert any(item[3] == "刘宁" for item in payloads)


def test_column_picker_parses_include_json() -> None:
    from apps.datasource.instance_index.column_picker import pick_instance_columns

    columns = [
        {"name": "solution_manager", "comment": "方案经理", "samples": ["LiuNing"]},
        {"name": "remark", "comment": "备注", "samples": ["ok"]},
    ]
    picked = pick_instance_columns(
        "wechat_project_approval_apply",
        columns,
        invoke=lambda _prompt: '{"include": ["solution_manager"], "exclude": ["remark"]}',
    )
    assert picked == {"solution_manager"}


def test_person_merge_allows_user_and_wx_drops_id_conflict() -> None:
    from apps.datasource.instance_index.person_map import (
        PersonEvidence,
        extra_instance_hits_for_people,
        merge_person_records,
        person_records_to_payloads,
        synthetic_id_hits_for_people,
    )
    from apps.datasource.instance_index.service import LookupScope, person_display_name

    ok = merge_person_records(
        [
            PersonEvidence(
                table="tenant_project_approval",
                name_field="solution_manager_name",
                id_field="solution_manager_id",
                user_id="1834001",
                name_zh="刘宁",
            ),
            PersonEvidence(
                table="wechat_project_approval_apply",
                name_field="solution_manager",
                id_field="solution_manager_wxid",
                wx_id="wx-liuning",
                name_zh="刘宁",
                name_en_raw="LiuNing",
            ),
        ]
    )
    assert len(ok) == 1
    person = ok[0]
    assert person.user_id == "1834001"
    assert person.wx_id == "wx-liuning"
    assert person.name_zh == "刘宁"
    assert person.name_en_raw == "LiuNing"
    assert person.name_en_fold == "liuning"
    aliases = {item[3] for item in person_records_to_payloads(ok)}
    assert {"刘宁", "LiuNing", "liuning", "1834001", "wx-liuning"} <= aliases

    dropped = merge_person_records(
        [
            PersonEvidence(
                table="tenant_project_approval",
                name_field="solution_manager_name",
                id_field="solution_manager_id",
                user_id="111",
                name_zh="刘宁",
            ),
            PersonEvidence(
                table="tenant_project_approval",
                name_field="solution_manager_name",
                id_field="solution_manager_id",
                user_id="222",
                name_zh="刘宁",
            ),
        ]
    )
    assert dropped == []

    from apps.datasource.instance_index.service import ValueAnchor

    person_hit = ValueAnchor(
        table_name="__person__",
        field_name="identity",
        raw_value="LiuNing",
        val_type="person_alias",
        matched_text="liuning",
        extra=person.snapshot(),
    )
    instance_row = CoreValueIndex(
        ds_id=1,
        table_name="wechat_project_approval_apply",
        field_name="solution_manager",
        val_type="instance",
        raw_value="LiuNing",
        normalized_value="liuning",
        extra={"token_of": '["LiuNing","HaoDeSheng"]'},
    )
    expanded = extra_instance_hits_for_people([person_hit], [instance_row])
    assert expanded
    assert expanded[0].table_name == "wechat_project_approval_apply"
    assert expanded[0].field_name == "solution_manager"

    ids = synthetic_id_hits_for_people(
        [person_hit],
        LookupScope(
            tables=frozenset(),
            fields=frozenset({("tenant_project_approval", "solution_manager_id")}),
        ),
    )
    assert ids
    assert ids[0].raw_value == "1834001"
    assert person_display_name(ids[0]) == "刘宁"


def test_person_zip_skips_length_mismatch() -> None:
    from apps.datasource.instance_index.person_map import (
        PersonPairSpec,
        evidence_from_row,
    )

    spec = PersonPairSpec(
        table="tenant_project_approval",
        id_field="solution_manager_id",
        name_field="solution_manager_name",
        id_kind="user_id",
    )
    assert evidence_from_row(spec, '["1","2"]', '["刘宁"]') == []
    zipped = evidence_from_row(spec, '["1834001"]', '["刘宁"]')
    assert len(zipped) == 1
    assert zipped[0].user_id == "1834001"
    assert zipped[0].name_zh == "刘宁"
    en = evidence_from_row(spec, "1834001", "LiuNing")
    assert en[0].name_en_raw == "LiuNing"
    assert en[0].name_zh is None


def test_person_hub_merges_cust_person_info() -> None:
    from apps.datasource.instance_index.person_map import (
        PersonEvidence,
        collect_hub_evidence,
        merge_person_records,
    )

    proto = SimpleNamespace(
        sample_rows=lambda *args, **kwargs: [
            {"user_id": "1834001", "name": "刘宁", "en_name": "LiuNing", "id": "9"}
        ]
    )
    table = SimpleNamespace(table_name="cust_person_info", database_name=None)
    fields = [
        SimpleNamespace(field_name="user_id"),
        SimpleNamespace(field_name="name"),
        SimpleNamespace(field_name="en_name"),
        SimpleNamespace(field_name="id"),
    ]
    hub = collect_hub_evidence(proto, SimpleNamespace(id=1), table, fields)
    assert hub
    assert hub[0].user_id == "1834001"
    assert hub[0].name_zh == "刘宁"
    merged = merge_person_records(
        hub
        + [
            PersonEvidence(
                table="tenant_project_approval",
                name_field="solution_manager_name",
                id_field="solution_manager_id",
                user_id="1834001",
                name_zh="刘宁",
            )
        ]
    )
    assert len(merged) == 1
    assert merged[0].name_en_raw == "LiuNing"
    roles = {
        (a["table"], a["field"], a["value_role"]) for a in merged[0].anchored_fields
    }
    assert ("cust_person_info", "user_id", "id") in roles
    assert ("cust_person_info", "id", "hub_pk") in roles


def test_person_single_form_not_indexed() -> None:
    from apps.datasource.instance_index.person_map import (
        PersonEvidence,
        merge_person_records,
    )

    records = merge_person_records(
        [
            PersonEvidence(
                table="cust_company_info",
                name_field="legal_name",
                id_field="",
                name_zh="张三",
            )
        ]
    )
    assert records == []


def test_parse_lookup_scope_and_match_hint() -> None:
    from apps.datasource.instance_index.cells import infer_match_hint
    from apps.datasource.instance_index.service import (
        ValueAnchor,
        annotate_lookup_candidate,
        parse_lookup_scope,
    )

    parsed = parse_lookup_scope(
        [
            "wechat_project_approval_apply",
            "tenant_project_approval.solution_manager_name",
        ]
    )
    assert "wechat_project_approval_apply" in parsed.tables
    assert ("tenant_project_approval", "solution_manager_name") in parsed.fields
    assert parsed.allows("wechat_project_approval_apply", "solution_manager")
    assert not parsed.allows("cust_company_info", "legal_name")

    assert infer_match_hint('["LiuNing","HaoDeSheng"]') == "contains"
    assert infer_match_hint("刘宁", {"token_of": "刘宁，郝德生"}) == "contains"
    assert infer_match_hint("刘宁") == "eq"

    hit = ValueAnchor(
        table_name="wechat_project_approval_apply",
        field_name="solution_manager",
        raw_value='["LiuNing","HaoDeSheng"]',
        val_type="instance",
        matched_text="LiuNing",
        extra={"raw_cell": True},
    )
    item = annotate_lookup_candidate(hit, phrases=["刘宁"])
    assert item["match_hint"] == "contains"


def test_lookup_values_field_topk_and_scope(monkeypatch) -> None:
    from apps.chat.tools import catalog_tools as ct
    from apps.chat.tools.catalog_tools import lookup_values
    from apps.datasource.instance_index.service import ValueAnchor

    monkeypatch.setattr(ct, "load_plane", lambda: AgentKnowledgePlane())
    monkeypatch.setattr(ct, "save_plane", lambda _p: None)
    monkeypatch.setattr(
        ct, "_catalog_sources", lambda _svc: (InMemoryWikiStore.load([]), {}, [])
    )

    empty = lookup_values(SimpleNamespace(ds=SimpleNamespace(id=1)), [])
    assert empty["ok"] is False

    hits = [
        ValueAnchor(
            table_name="wechat_project_approval_apply",
            field_name="solution_manager",
            raw_value="LiuNing",
            val_type="instance",
            matched_text="liuning",
            extra={"token_of": '["LiuNing","HaoDeSheng"]'},
        )
    ]

    class _Session:
        def __enter__(self) -> object:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    monkeypatch.setattr("apps.conversation.session.session_scope", lambda: _Session())
    monkeypatch.setattr(
        "apps.datasource.instance_index.service.match_phrases",
        lambda *args, **kwargs: hits,
    )
    monkeypatch.setattr(
        "apps.datasource.instance_index.service.list_field_topk",
        lambda *args, **kwargs: hits,
    )
    monkeypatch.setattr("apps.protocol.get_protocol_for_ds", lambda _ds: None)

    phrased = lookup_values(
        SimpleNamespace(ds=SimpleNamespace(id=1)),
        ["刘宁"],
        scope=["wechat_project_approval_apply"],
    )
    assert phrased["ok"] is True
    data = phrased.get("data") or {}
    assert data.get("mode") == "phrases"
    assert (data.get("candidates") or [])[0]["match_hint"] == "contains"

    topk = lookup_values(
        SimpleNamespace(ds=SimpleNamespace(id=1)),
        [],
        scope=["wechat_project_approval_apply.solution_manager"],
    )
    assert topk["ok"] is True
    assert (topk.get("data") or {}).get("mode") == "field_topk"
