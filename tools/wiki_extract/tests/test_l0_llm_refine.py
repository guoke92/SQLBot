"""LLM refine applies keep/instance/reject and semantic clusters without live LLM."""

from __future__ import annotations

from tools.wiki_extract.heuristics import compile_model
from tools.wiki_extract.llm_client import parse_json_object
from tools.wiki_extract.llm_refine import refine_model
from tools.wiki_extract.tests.test_l0_compile import fixture_catalog, fixture_profile


def test_parse_json_object_strips_fence() -> None:
    data = parse_json_object('```json\n{"table": "t"}\n```')
    assert data["table"] == "t"


def test_refine_filters_enums_and_regroups() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())
    assert "cust_company_info_sign_status" in model["enums"]
    assert (
        "cust_company_info_enable" not in model["enums"]
    )  # enable not in fixture profile

    def chat(_system: str, user: str) -> dict:
        if "cust_company_info" in user and "sign_status" in user:
            return {
                "enums": [
                    {
                        "column": "sign_status",
                        "verdict": "keep",
                        "reason": "closed status codes",
                    }
                ],
                "clusters": [
                    {
                        "key": "common",
                        "title": "通用",
                        "include": "always",
                        "fields": [
                            "id",
                            "enable",
                            "create_time",
                            "update_time",
                            "create_by",
                            "code",
                        ],
                    },
                    {
                        "key": "identity",
                        "title": "主档身份",
                        "fields": ["name", "code"],
                    },
                ],
                "similar_fields": [
                    {"fields": ["name", "code"], "note": "名称与编码都可指代企业"}
                ],
            }
        if "cust_account_info" in user:
            return {
                "enums": [],
                "clusters": [
                    {
                        "key": "common",
                        "include": "always",
                        "fields": ["id", "enable"],
                    },
                    {
                        "key": "bank",
                        "title": "银行账户",
                        "fields": ["bank_name", "bank_code", "bank_city", "account_no"],
                    },
                ],
                "similar_fields": [],
            }
        return {
            "enums": [],
            "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
            "similar_fields": [],
        }

    refined = refine_model(model, chat, workers=1)
    assert "cust_company_info_sign_status" in refined["enums"]
    company = refined["tables"]["cust_company_info"]
    keys = [c["key"] for c in company["clusters"]]
    assert keys[0] == "common"
    assert "identity" in keys
    name_field = next(f for f in company["fields"] if f["name"] == "name")
    assert name_field["cluster"] == "identity"
    assert company["similar_fields"]
    notes = [item["note"] for item in refined["reviews"]]
    assert any("similar" in n or "名称" in n for n in notes)
    # invented columns must not appear
    assert all(f["name"] != "ghost" for f in company["fields"])


def test_auto_instance_tenant_and_reject_pwd() -> None:
    catalog = fixture_catalog()
    catalog["tables"]["cust_company_info"]["columns"]["app_tenant_code"] = {
        "type": "varchar(32)",
        "nullable": True,
        "comment": "租户",
        "pos": 20,
        "key": "",
        "extra": "",
        "default": None,
    }
    catalog["tables"]["cust_company_info"]["columns"]["login_pwd"] = {
        "type": "varchar(32)",
        "nullable": True,
        "comment": "密码",
        "pos": 21,
        "key": "",
        "extra": "",
        "default": None,
    }
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["app_tenant_code"] = {
        "distinct": 2,
        "values": {"base": 1, "QA2": 1},
    }
    profile["tables"]["cust_company_info"]["column_stats"]["login_pwd"] = {
        "distinct": 2,
        "values": {"Aa11111.": 1, "lls16888": 1},
    }
    model = compile_model(catalog, profile)
    assert "cust_company_info_app_tenant_code" in model["enums"]
    assert "cust_company_info_login_pwd" in model["enums"]

    def chat(_s: str, _u: str) -> dict:
        return {"enums": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    assert "cust_company_info_app_tenant_code" not in refined["enums"]
    assert "cust_company_info_login_pwd" not in refined["enums"]
    indexed = {(e["table"], e["column"]) for e in refined["value_index"]}
    assert ("cust_company_info", "app_tenant_code") in indexed
    assert ("cust_company_info", "login_pwd") not in indexed


def test_omitted_enum_defaults_to_instance() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())

    def chat(_s: str, user: str) -> dict:
        return {"enums": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    assert "cust_company_info_sign_status" not in refined["enums"]
    indexed = {(e["table"], e["column"]) for e in refined["value_index"]}
    assert ("cust_company_info", "sign_status") in indexed
