"""MinHash location, sentinels, and shape hints. No live database."""

from __future__ import annotations

from tools.wiki_extract.validate_joins import _usable_predicate
from tools.wiki_extract.value_sketch import (
    FieldSketch,
    field_shape,
    is_sentinel,
    locate_overlaps,
    minhash_sketch,
    resemblance,
    shape_transform_hint,
    sketches_from_profile,
    sql_sentinel_exclusions,
    summarize_value_counts,
)


def _field(
    table: str,
    column: str,
    values: list[str],
    *,
    comment: str = "",
    mysql_type: str = "varchar(32)",
) -> FieldSketch:
    summary = summarize_value_counts({value: 1 for value in values})
    packed = summary["minhash"]
    return FieldSketch(
        fq=f"{table}.{column}",
        table=table,
        column=column,
        comment=comment,
        mysql_type=mysql_type,
        shape=summary["shape"],
        sentinels=list(summary["sentinels"]),
        minhash=list(packed["values"]),
        basis=packed["basis"],
    )


def test_identical_sets_resemble_and_sentinels_drop_out() -> None:
    plain = minhash_sketch(["ABC", "DEF"])
    with_placeholder = minhash_sketch(["ABC", "DEF", "123-456-7890", "无"])
    assert resemblance(plain, with_placeholder) == 1.0
    assert is_sentinel("0") is False
    assert is_sentinel("000000") is True
    clause = sql_sentinel_exclusions("a", "`code`")
    assert "'0'" not in clause
    assert "'123-456-7890'" in clause
    clause = _usable_predicate("a", "code")
    assert "NOT IN" in clause
    assert "'0'" not in clause


def test_zero_stays_in_the_sketch() -> None:
    with_zero = minhash_sketch(["0", "A"])
    without_zero = minhash_sketch(["A"])
    assert resemblance(with_zero, without_zero) < 1.0


def test_transform_hint_for_one_extra_prefix_digit() -> None:
    short = field_shape(["1234567890123", "2234567890123", "3234567890123"])
    long = field_shape(["11234567890123", "12234567890123", "13234567890123"])
    assert shape_transform_hint(short, long) == "prefix:1"


def test_name_keeps_sparse_fk_and_ref_only_when_it_points() -> None:
    parent = _field("tenant_project", "id", ["1", "2", "3"], comment="项目主键")
    sparse = _field("project_file_info", "project_id", ["999"])
    ref_hit = _field("cust_auth_application_config", "ref_cust_company_info", ["888"])
    company = _field("cust_company_info", "id", ["1"])
    noise = _field("cust_company_info", "name", ["甲"])
    unrelated_ref = _field("notes", "ref_other_thing", ["ZZZ"])

    located = locate_overlaps(
        [parent, sparse, ref_hit, company, noise, unrelated_ref],
        min_resemblance=0.8,
    )
    kept = {(row["left"], row["right"], row["kept_by"]) for row in located["pairs"]}
    assert (
        "project_file_info.project_id",
        "tenant_project.id",
        "name",
    ) in kept or (
        "tenant_project.id",
        "project_file_info.project_id",
        "name",
    ) in kept
    assert any(
        {left, right} == {"cust_auth_application_config.ref_cust_company_info", "cust_company_info.id"}
        for left, right, _by in kept
    )
    assert not any("ref_other_thing" in left or "ref_other_thing" in right for left, right, _by in kept)
    assert not any(row[0].endswith(".name") and "ref_cust_company_info" in row[1] for row in kept)
    assert not any(row[1].endswith(".name") and "ref_cust_company_info" in row[0] for row in kept)


def test_comment_borrow_requires_high_resemblance_and_a_real_comment() -> None:
    parent = _field("hub", "product_code", ["P1", "P2"], comment="产品编码")
    child = _field("role", "product_code", ["P1", "P2"], comment="编码")
    weak = _field("other", "product_code", ["P1", "P2"], comment="")
    located = locate_overlaps([parent, child, weak], min_resemblance=0.2)
    targets = {row["target"]: row for row in located["imputations"]}
    assert targets["role.product_code"]["from"] == "hub.product_code"
    assert targets["role.product_code"]["trust"] == "proposed"
    assert targets["other.product_code"]["comment"] == "产品编码"
    assert all(row["target"] != "hub.product_code" for row in located["imputations"])


def test_incompatible_types_are_not_paired() -> None:
    left = _field("a", "status", ["1", "2"], mysql_type="int")
    right = _field("b", "status", ["1", "2"], mysql_type="varchar(8)")
    located = locate_overlaps([left, right], min_resemblance=0.0)
    assert located["pairs"] == []


def test_sketches_from_profile_prefers_distinct_counts() -> None:
    catalog = {
        "tables": {
            "parent": {"columns": {"code": {"comment": "渠道", "type": "varchar(16)"}}},
            "child": {"columns": {"code": {"comment": "", "type": "varchar(16)"}}},
        }
    }
    profile = {
        "tables": {
            "parent": {"column_stats": {"code": {"values": {"SSO": 4, "APP": 1}}}},
        }
    }
    instance = {
        "tables": {
            "parent": {
                "column_stats": {
                    "code": {"top_values": [{"value": "ONLY_TOP", "count": 9}]}
                }
            },
            "child": {
                "column_stats": {
                    "code": {"top_values": [{"value": "SSO", "count": 2}, {"value": "APP", "count": 1}]}
                }
            },
        }
    }
    sketches = {item.fq: item for item in sketches_from_profile(catalog, profile, instance)}
    assert sketches["parent.code"].minhash == minhash_sketch(["SSO", "APP"])
    assert sketches["parent.code"].basis == "profile"
    assert sketches["child.code"].basis == "top_values"
    located = locate_overlaps(list(sketches.values()), min_resemblance=0.2)
    assert located["pairs"][0]["resemblance"] == 1.0
    assert sketches["parent.code"].comment == "渠道"
    summary = summarize_value_counts({"N/A": 9, "SSO": 1})
    assert summary["sentinels"] == ["N/A"]
    assert summary["shape"]["n"] == 1
