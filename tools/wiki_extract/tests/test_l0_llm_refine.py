"""LLM refine applies keep/hold/drop without live LLM."""

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
    assert "cust_company_info__sign_status" in model["dicts"]
    assert (
        "cust_company_info_enable" not in model["dicts"]
    )  # enable not in fixture profile

    def chat(_system: str, user: str) -> dict:
        if "cust_company_info" in user and "sign_status" in user:
            return {
                "dicts": [
                    {
                        "column": "sign_status",
                        "verdict": "keep",
                        "reason": "closed status codes",
                    }
                ],
                "clusters": [
                    {
                        "key": "common",
                        "title": "通用（主键/审计/租户）",
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
                "dicts": [],
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
                "joins": [
                    {
                        "right": "cust_account_info.cust_company_id",
                        "authenticity": "unlikely",
                        "note": "name-only guess",
                    }
                ],
            }
        return {
            "dicts": [],
            "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
            "similar_fields": [],
        }

    refined = refine_model(model, chat, workers=1)
    assert "cust_company_info__sign_status" in refined["dicts"]
    company = refined["tables"]["cust_company_info"]
    assert "clusters" not in company
    name_field = next(f for f in company["fields"] if f["name"] == "name")
    assert "cluster" not in name_field
    assert company["similar_fields"]
    notes = [item["note"] for item in refined["reviews"]]
    assert any("similar" in n or "名称" in n for n in notes)
    assert all("#grain" not in item["claim_path"] for item in refined["reviews"])
    rels = refined["tables"]["cust_account_info"]["relations"]
    assert len(rels) == 1
    assert rels[0]["authenticity"] == "unlikely"
    assert rels[0]["trust"] == "proposed"
    assert any(
        item["kind"] == "unverified_join" and "authenticity=unlikely" in item["note"]
        for item in refined["reviews"]
    )
    # invented columns must not appear
    assert all(f["name"] != "ghost" for f in company["fields"])


def test_llm_hold_keeps_uncertain_enum() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())

    def chat(system: str, user: str) -> dict:
        if "复核" in system:
            return {
                "column": "sign_status",
                "verdict": "dict_hold",
                "reason": "测库样本偏少，语义像状态码但未闭合",
            }
        if "cust_company_info" in user:
            return {
                "dicts": [
                    {
                        "column": "sign_status",
                        "verdict": "hold",
                        "reason": "测库样本偏少，语义像状态码但未闭合",
                    }
                ],
                "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
                "similar_fields": [],
            }
        return {
            "dicts": [],
            "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
            "similar_fields": [],
        }

    refined = refine_model(model, chat, workers=1)
    enum = refined["dicts"]["cust_company_info__sign_status"]
    assert enum["triage"] == "hold"
    assert enum["needs_review"] is True
    assert refined["llm_stats"]["dict_hold"] >= 1


def test_auto_reject_audit_not_value_index() -> None:
    catalog = fixture_catalog()
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["create_by"] = {
        "distinct": 3,
        "values": {"1": 1, "2": 1, "3": 1},
    }
    profile["tables"]["cust_company_info"]["column_stats"]["create_time"] = {
        "distinct": 2,
        "values": {"2024-01-01 00:00:00": 1, "2024-01-02 00:00:00": 1},
    }
    profile["tables"]["cust_company_info"]["column_stats"]["id"] = {
        "distinct": 3,
        "values": {"1001": 1, "1002": 1, "1003": 1},
    }
    model = compile_model(catalog, profile)
    assert "cust_company_info__create_by" not in model["dicts"]
    indexed = {(e["table"], e["column"]) for e in model["instance_index"]}
    assert ("cust_company_info", "create_by") not in indexed
    assert ("cust_company_info", "create_time") not in indexed
    assert ("cust_company_info", "id") not in indexed

    def chat(_s: str, _u: str) -> dict:
        return {"dicts": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    assert "cust_company_info__create_by" not in refined["dicts"]
    indexed = {(e["table"], e["column"]) for e in refined["instance_index"]}
    assert ("cust_company_info", "create_by") not in indexed
    assert ("cust_company_info", "create_time") not in indexed
    assert ("cust_company_info", "id") not in indexed


def test_llm_label_gate_drops_invention() -> None:
    catalog = fixture_catalog()
    catalog["tables"]["cust_company_info"]["columns"]["enable"]["comment"] = "enable"
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["enable"] = {
        "distinct": 2,
        "values": {"Y": 10, "N": 2},
    }
    model = compile_model(catalog, profile)

    def chat(_s: str, user: str) -> dict:
        if "cust_company_info" in user:
            return {
                "dicts": [
                    {
                        "column": "enable",
                        "verdict": "keep",
                        "labels": {"Y": "启用", "N": "停用"},
                    },
                    {"column": "sign_status", "verdict": "keep"},
                ],
                "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
                "similar_fields": [],
            }
        return {"dicts": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    enable_vals = refined["dicts"]["cust_company_info__enable"]["values"]
    assert "label" not in enable_vals["Y"]
    assert "label" not in enable_vals["N"]


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
    assert "cust_company_info__login_pwd" not in model["dicts"]
    indexed = {(e["table"], e["column"]) for e in model["instance_index"]}
    assert ("cust_company_info", "app_tenant_code") in indexed
    assert ("cust_company_info", "login_pwd") not in indexed

    def chat(_s: str, _u: str) -> dict:
        return {"dicts": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    assert "cust_company_info__login_pwd" not in refined["dicts"]
    indexed = {(e["table"], e["column"]) for e in refined["instance_index"]}
    assert ("cust_company_info", "app_tenant_code") in indexed
    assert ("cust_company_info", "login_pwd") not in indexed


def test_skip_audit_similar_reviews() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())

    def chat(_s: str, user: str) -> dict:
        if "cust_company_info" in user:
            return {
                "dicts": [{"column": "sign_status", "verdict": "keep"}],
                "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
                "similar_fields": [
                    {"fields": ["create_by", "update_by"], "note": "audit pair"}
                ],
            }
        return {"dicts": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    assert not any("#similar_fields." in i["claim_path"] for i in refined["reviews"])


def test_omitted_enum_keeps_mechanical_enum() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())

    def chat(_s: str, user: str) -> dict:
        return {"dicts": [], "clusters": [], "similar_fields": []}

    refined = refine_model(model, chat, workers=1)
    enum = refined["dicts"]["cust_company_info__sign_status"]
    assert enum["triage"] == "keep"
