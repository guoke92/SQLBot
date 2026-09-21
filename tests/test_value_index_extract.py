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


def test_opaque_instance_values() -> None:
    assert looks_like_opaque_instance_values(
        [{"value": "550e8400-e29b-41d4-a716-446655440000"}]
    )
    assert looks_like_opaque_instance_values([{"value": "12345678901234567"}])
    assert not looks_like_opaque_instance_values(
        [{"value": "深圳市前海一方商业保理有限公司"}]
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
