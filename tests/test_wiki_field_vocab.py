"""Table-field vocab: cardinality / comments / identifier topk / dict bind."""

from __future__ import annotations

from apps.knowledge.wiki.field_vocab import (
    decide_field_vocab,
    is_identifier_column,
    parse_comment_labels,
)


def test_parse_comment_labels_yn_and_01() -> None:
    assert parse_comment_labels("本期续费待办是否已生成：Y 已生成 / N 未生成") == {
        "Y": "已生成",
        "N": "未生成",
    }
    assert parse_comment_labels("软删除：0 否 1 是") == {"0": "否", "1": "是"}
    assert parse_comment_labels("缴费状态：PAID 已缴费 / UNPAID 未缴费") == {
        "PAID": "已缴费",
        "UNPAID": "未缴费",
    }


def test_tenant_code_is_not_an_enum_dict() -> None:
    from apps.knowledge.wiki.field_vocab import looks_like_enum_dict, looks_like_vocab

    values = {"LN1": 10, "ISOLATE_TAG_boscebl": 3}
    assert looks_like_vocab(
        col="db_tenant_code", family="string", distinct=2, values=values
    )
    assert not looks_like_enum_dict(
        col="db_tenant_code", family="string", distinct=2, values=values
    )


def test_status_and_soft_delete_are_enum_dicts() -> None:
    from apps.knowledge.wiki.field_vocab import looks_like_enum_dict

    assert looks_like_enum_dict(
        col="status",
        family="string",
        distinct=3,
        values={"FAILED": 1, "RUNNING": 1, "SUCCESS": 1},
        desc="状态",
    )
    assert looks_like_enum_dict(
        col="is_deleted",
        family="string",
        distinct=2,
        values={"0": 10, "1": 1},
        desc="软删除：0 否 1 是",
    )
    assert not looks_like_enum_dict(
        col="default_menu_index",
        family="string",
        distinct=1,
        values={"1": 10},
        desc="默认菜单序号",
    )


def test_skip_identifier_topk() -> None:
    snow = {
        "1364399217692581890": 10,
        "1407266533295345665": 8,
    }
    assert is_identifier_column("create_by", desc="创建人id", values=snow)
    out = decide_field_vocab(
        col="create_by",
        phys="varchar(100)",
        family="string",
        desc="创建人id",
        stats={"distinct": 4, "values": snow},
        dict_page="",
        enum_values=set(),
    )
    assert out == {}


def test_undeclared_status_rejects_shared_enable() -> None:
    out = decide_field_vocab(
        col="status",
        phys="varchar(16)",
        family="string",
        desc="状态",
        stats={
            "distinct": 3,
            "values": {"FAILED": 1, "RUNNING": 2, "SUCCESS": 9},
        },
        dict_page="enable",
        enum_values={"Y", "N"},
    )
    assert out.get("topk") == "FAILED|RUNNING|SUCCESS"
    assert "dict" not in out


def test_undeclared_status_keeps_local_enum_pointer() -> None:
    out = decide_field_vocab(
        col="status",
        phys="varchar(16)",
        family="string",
        desc="状态",
        stats={
            "distinct": 3,
            "values": {"FAILED": 1, "RUNNING": 2, "SUCCESS": 9},
        },
        dict_page="enable",
        enum_values={"Y", "N"},
        fallback_dict="async_io_task__status",
    )
    assert out.get("dict") == "async_io_task__status"
    assert out.get("topk") == "FAILED|RUNNING|SUCCESS"


def test_field_labels_overlay_shared_enable() -> None:
    out = decide_field_vocab(
        col="renew_remind_sent",
        phys="varchar(2)",
        family="string",
        desc="本期续费待办是否已生成：Y 已生成 / N 未生成",
        stats={"distinct": 2, "values": {"N": 10, "Y": 20}},
        dict_page="enable",
        enum_values={"Y", "N"},
    )
    assert out.get("dict") == "enable"
    assert out["topk"] == "N|Y"
    assert "Y:已生成" in out["labels"]
    assert "N:未生成" in out["labels"]


def test_drop_enable_dict_on_temporal() -> None:
    out = decide_field_vocab(
        col="service_end",
        phys="date",
        family="temporal",
        desc="服务截止日",
        stats=None,
        dict_page="enable",
        enum_values={"Y", "N"},
    )
    assert out == {}


def test_keep_real_enum_when_values_overlap() -> None:
    out = decide_field_vocab(
        col="user_type",
        phys="varchar(32)",
        family="string",
        desc="联系人类型",
        stats={
            "distinct": 3,
            "values": {
                "accountAdmin": 100,
                "accountNormal": 20,
                "accountGuest": 5,
            },
        },
        dict_page="user_type",
        enum_values={"accountAdmin", "accountNormal", "accountGuest"},
    )
    assert out.get("dict") == "user_type"
    assert "accountAdmin" in out.get("topk", "")


def test_drop_dict_when_same_name_values_diverge() -> None:
    out = decide_field_vocab(
        col="cust_type",
        phys="varchar(8)",
        family="string",
        desc="类型",
        stats={"distinct": 4, "values": {"1": 10, "2": 8, "3": 3, "4": 1}},
        dict_page="cust_type",
        enum_values={"CORE", "SUPPLIER", "DEALER"},
    )
    assert "dict" not in out
    assert out.get("topk") == "1|2|3|4"


def test_diverged_values_fall_back_to_local_enum() -> None:
    out = decide_field_vocab(
        col="cust_type",
        phys="varchar(8)",
        family="string",
        desc="类型",
        stats={"distinct": 4, "values": {"1": 10, "2": 8, "3": 3, "4": 1}},
        dict_page="cust_type",
        enum_values={"CORE", "SUPPLIER", "DEALER"},
        fallback_dict="cust_user_rel__cust_type",
    )
    assert out.get("dict") == "cust_user_rel__cust_type"
    assert out.get("topk") == "1|2|3|4"


def test_quoted_topk_values_do_not_break_yaml_fence() -> None:
    from apps.knowledge.wiki.contract import parse_page
    from apps.knowledge.wiki.pipeline import merge_same_key_page

    baseline = """---
type: table
title: t
page_key: t
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

```ground:table
table: t
fields:
  - name: role_type
    type: string
    topk: "\\"CORE\\"|CORE|SUPPLIER"
```
"""
    semantic = """---
type: table
title: t
page_key: t
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

old
```ground:table
table: t
fields:
  - name: role_type
    dict: enable
    topk: CORE
```
"""
    page = parse_page(baseline, page_key="t", belong="tables")
    assert any(b.kind == "table" for b in page.ground_blocks)
    merged = merge_same_key_page(baseline, semantic)
    assert "dict: enable" not in merged
    assert "CORE" in merged


def test_schema_keeps_enum_pointer_and_field_labels() -> None:
    from types import SimpleNamespace

    from apps.chat.steps.wiki_schema import WikiSchemaRenderer

    table_page = SimpleNamespace(
        body="```ground:table\ntable: t\ndesc: 表\n"
        "fields:\n  - name: renew_remind_sent\n    type: string\n"
        "    phys: varchar(2)\n    desc: 本期续费待办是否已生成\n"
        '    dict: enable\n    topk: N|Y\n    labels: "Y:已生成|N:未生成"\n```\n',
        ground_blocks=[],
    )

    class _Store:
        pages = {"t": table_page}

    text = WikiSchemaRenderer(_Store(), {}).render(["t"])
    assert "labels=Y:已生成|N:未生成" in text
    assert "enum=enable" in text
