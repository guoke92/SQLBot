"""Dictionary triage is dict_keep | dict_hold | drop only."""

from __future__ import annotations

from tools.wiki_extract.dict_triage import (
    DEST_DICT_HOLD,
    DEST_DICT_KEEP,
    DEST_DROP,
    mechanical_suggestion,
)
from tools.wiki_extract.heuristics import compile_model
from tools.wiki_extract.llm_refine import refine_model
from tools.wiki_extract.tests.test_l0_compile import fixture_catalog, fixture_profile


def test_mechanical_status_dict_keep() -> None:
    dest, _reason = mechanical_suggestion(
        {
            "column": "sign_status",
            "comment": "签约状态",
            "mysql_type": "varchar(32)",
            "values": {"SIGNED": 1, "DRAFT": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
        }
    )
    assert dest == DEST_DICT_KEEP


def test_mechanical_audit_time_id_drop() -> None:
    assert (
        mechanical_suggestion({"column": "create_by", "values": {"1": 1}})[0]
        == DEST_DROP
    )
    assert (
        mechanical_suggestion(
            {
                "column": "signed_on",
                "mysql_type": "datetime",
                "values": {"2024-01-01": 1},
            }
        )[0]
        == DEST_DROP
    )
    assert (
        mechanical_suggestion({"column": "id", "values": {"1": 1, "2": 1}})[0]
        == DEST_DROP
    )


def test_mechanical_credit_code_drops_from_dict() -> None:
    dest, reason = mechanical_suggestion(
        {
            "column": "credit_code",
            "comment": "统一社会信用代码",
            "mysql_type": "varchar(32)",
            "values": {"911100001234567890": 1, "911100001234567891": 1},
            "looks_like_ids": True,
            "looks_like_enum": False,
        }
    )
    assert dest == DEST_DROP
    assert reason == "snowflake_or_long_id"


def test_mechanical_codeish_unnamed_is_hold() -> None:
    dest, _reason = mechanical_suggestion(
        {
            "column": "payload_kind",
            "comment": "",
            "mysql_type": "varchar(16)",
            "values": {"A": 1, "B": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
        }
    )
    assert dest == DEST_DICT_HOLD


def test_mechanical_tenant_and_json_drop() -> None:
    dest, reason = mechanical_suggestion(
        {
            "column": "db_tenant_code",
            "comment": "租户",
            "mysql_type": "varchar(32)",
            "values": {"T1": 10},
            "looks_like_ids": False,
            "looks_like_enum": True,
        }
    )
    assert dest == DEST_DROP
    assert reason == "tenant"
    dest, reason = mechanical_suggestion(
        {
            "column": "ext_json",
            "comment": "",
            "mysql_type": "varchar(512)",
            "values": {'[{"k":1}]': 1, '{"a":2}': 1},
            "looks_like_ids": False,
            "looks_like_enum": False,
        }
    )
    assert dest == DEST_DROP
    assert reason == "json_payload"


def test_drop_clears_field_dictionary() -> None:
    catalog = fixture_catalog()
    catalog["tables"]["cust_company_info"]["columns"]["db_tenant_code"] = {
        "type": "varchar(32)",
        "nullable": True,
        "comment": "租户",
        "pos": 31,
        "key": "",
        "extra": "",
        "default": None,
    }
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["db_tenant_code"] = {
        "distinct": 1,
        "values": {"T1": 10},
    }
    model = compile_model(catalog, profile)
    assert "cust_company_info__db_tenant_code" not in model["dicts"]
    fields = model["tables"]["cust_company_info"]["fields"]
    tenant = next(f for f in fields if f["name"] == "db_tenant_code")
    assert "dictionary" not in tenant


def test_compile_credit_code_not_a_dict_page() -> None:
    catalog = fixture_catalog()
    catalog["tables"]["cust_company_info"]["columns"]["credit_code"] = {
        "type": "varchar(32)",
        "nullable": True,
        "comment": "统一社会信用代码",
        "pos": 30,
        "key": "",
        "extra": "",
        "default": None,
    }
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["credit_code"] = {
        "distinct": 2,
        "values": {"911100001234567890": 1, "911100001234567891": 1},
    }
    model = compile_model(catalog, profile)
    assert "cust_company_info__credit_code" not in model["dicts"]


def test_pass2_only_dict_verdicts() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())

    def chat(system: str, user: str) -> dict:
        if "复核" in system:
            return {
                "column": "sign_status",
                "verdict": "dict_keep",
                "reason": "closed status",
            }
        if "cust_company_info" in user:
            return {
                "dicts": [
                    {
                        "column": "sign_status",
                        "verdict": "drop",
                        "reason": "disagree with mechanical",
                    }
                ],
                "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
            }
        return {
            "dicts": [],
            "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
        }

    refined = refine_model(model, chat, workers=1)
    cand = next(
        c
        for c in refined["dict_candidates"]
        if c["table"] == "cust_company_info" and c["column"] == "sign_status"
    )
    assert cand["llm_dest"] == DEST_DROP
    assert cand["mechanical_dest"] == DEST_DICT_KEEP
    assert cand["dest"] == DEST_DICT_KEEP
    assert cand["dest_source"] == "pass2"
    assert "value_index" not in str(cand.get("dest"))
    assert "cust_company_info__sign_status" in refined["dicts"]
