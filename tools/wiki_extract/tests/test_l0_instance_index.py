"""Instance index is independent of dict_triage and has no distinct<=32 cap."""

from __future__ import annotations

from tools.wiki_extract.heuristics import compile_model
from tools.wiki_extract.instance_index import (
    nominate_instance_column,
    skip_instance_column,
)
from tools.wiki_extract.tests.test_l0_compile import fixture_catalog, fixture_profile


def test_skip_audit_and_secrets() -> None:
    assert skip_instance_column("create_by") == "audit_user"
    assert skip_instance_column("update_time", mysql_type="datetime") == "temporal_name"
    assert skip_instance_column("id") == "surrogate_pk"
    assert skip_instance_column("login_pwd", comment="密码") == "secret"
    assert skip_instance_column("name") == ""


def test_nominate_credit_and_name() -> None:
    assert nominate_instance_column(
        "certification_no", comment="统一信用代码", mysql_type="varchar(32)"
    )
    assert nominate_instance_column("name", name_anchors=["name"])
    assert nominate_instance_column("app_tenant_code")
    assert not nominate_instance_column("create_by")
    assert not nominate_instance_column("login_pwd", comment="密码")


def test_high_cardinality_credit_enters_instance_index() -> None:
    catalog = fixture_catalog()
    catalog["tables"]["cust_company_info"]["columns"]["certification_no"] = {
        "type": "varchar(32)",
        "nullable": True,
        "comment": "统一信用代码",
        "pos": 30,
        "key": "",
        "extra": "",
        "default": None,
    }
    profile = fixture_profile()
    profile_instance = {
        "tables": {
            "cust_company_info": {
                "column_stats": {
                    "certification_no": {
                        "top_values": [
                            {"value": "91120104503856003W", "count": 40001},
                            {"value": "92522327MA6FLC7H2N", "count": 30},
                        ]
                    }
                }
            }
        }
    }
    model = compile_model(catalog, profile, profile_instance=profile_instance)
    indexed = {
        (e["table"], e["column"]): e for e in (model.get("instance_index") or [])
    }
    entry = indexed[("cust_company_info", "certification_no")]
    assert entry["values"][0]["value"] == "91120104503856003W"
    assert entry["values"][0]["count"] == 40001
    assert "cust_company_info__certification_no" not in (model.get("dicts") or {})


def test_audit_columns_never_indexed() -> None:
    catalog = fixture_catalog()
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["create_by"] = {
        "distinct": 3,
        "values": {"1": 1, "2": 1, "3": 1},
    }
    model = compile_model(catalog, profile)
    indexed = {(e["table"], e["column"]) for e in model["instance_index"]}
    assert ("cust_company_info", "create_by") not in indexed
    assert ("cust_company_info", "create_time") not in indexed
    assert ("cust_company_info", "id") not in indexed


def test_name_and_status_can_coexist_with_dict() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())
    indexed = {(e["table"], e["column"]) for e in model["instance_index"]}
    assert ("cust_company_info", "name") in indexed
    assert "cust_company_info__sign_status" in model["dicts"]
    # complementary: status may also appear in instance_index
    assert ("cust_company_info", "create_by") not in indexed


def test_skip_pii_fk_and_opaque_values() -> None:
    assert skip_instance_column("login_name") == "pii"
    assert skip_instance_column("email") == "pii"
    assert skip_instance_column("company_id") == "surrogate_fk"
    assert not nominate_instance_column("company_id")
    catalog = fixture_catalog()
    catalog["tables"]["cust_company_info"]["columns"]["trace_code"] = {
        "type": "varchar(64)",
        "nullable": True,
        "comment": "追踪码",
        "pos": 40,
        "key": "",
        "extra": "",
        "default": None,
    }
    catalog["tables"]["cust_company_info"]["columns"]["ext_json"] = {
        "type": "varchar(512)",
        "nullable": True,
        "comment": "扩展",
        "pos": 41,
        "key": "",
        "extra": "",
        "default": None,
    }
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["trace_code"] = {
        "distinct": 2,
        "values": {
            "550e8400-e29b-41d4-a716-446655440000": 1,
            "123e4567-e89b-12d3-a456-426614174000": 1,
        },
    }
    profile["tables"]["cust_company_info"]["column_stats"]["ext_json"] = {
        "distinct": 1,
        "values": {'[{"k":1}]': 1},
    }
    model = compile_model(catalog, profile)
    indexed = {(e["table"], e["column"]) for e in model["instance_index"]}
    assert ("cust_company_info", "trace_code") not in indexed
    assert ("cust_company_info", "ext_json") not in indexed
    assert ("cust_company_info", "company_id") not in indexed
