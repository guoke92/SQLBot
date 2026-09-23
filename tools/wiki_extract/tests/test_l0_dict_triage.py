"""Dictionary triage is dict_keep | dict_hold | drop only."""

from __future__ import annotations

from tools.wiki_extract.dict_triage import (
    DEST_DICT_HOLD,
    DEST_DICT_KEEP,
    DEST_DROP,
    apply_llm_triage,
    incomplete_binary_pair,
    mechanical_suggestion,
)
from tools.wiki_extract.heuristics import compile_model, parse_comment_fk
from tools.wiki_extract.llm_refine import refine_model
from tools.wiki_extract.tests.test_l0_compile import fixture_catalog, fixture_profile


def test_mechanical_satellite_product_code_not_dict() -> None:
    dest, reason = mechanical_suggestion(
        {
            "table": "tenant_product",
            "column": "platform_product_code",
            "comment": "平台产品业务码",
            "mysql_type": "varchar(32)",
            "values": {"ACFLOW": 10, "ORDER": 2},
            "looks_like_ids": False,
            "looks_like_enum": True,
        }
    )
    assert dest == DEST_DROP
    assert reason == "product_code_concept_not_dict"
    dest, reason = mechanical_suggestion(
        {
            "table": "platform_product",
            "column": "product_code",
            "comment": "产品业务码",
            "mysql_type": "varchar(32)",
            "values": {"ACFLOW": 1, "ORDER": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
        }
    )
    assert dest == DEST_DICT_KEEP


def test_mechanical_closed_code_enum_keep() -> None:
    dest, reason = mechanical_suggestion(
        {
            "column": "node_code",
            "comment": "节点编码字典",
            "mysql_type": "varchar(32)",
            "values": {"PROJECT_CONFIG": 1, "PROJECT_MANAGER": 1, "OTHER": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
        }
    )
    assert dest == DEST_DICT_KEEP
    assert reason in {"closed_code_enum", "comment_dict_hint"}


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


def test_mechanical_drops_ref_comment_fk_ordinal_biz_sample() -> None:
    assert (
        mechanical_suggestion(
            {
                "column": "ref_tenant_project_approval_flow_comment_approval",
                "comment": "关联项目审批",
                "values": {"23099f85ba3e478b95eeba5b4262de36": 1},
                "looks_like_ids": True,
                "looks_like_enum": False,
            }
        )[0]
        == DEST_DROP
    )
    dest, reason = mechanical_suggestion(
        {
            "column": "sp_no",
            "comment": "立项审批编号（wechat_project_approval_apply#sp_no）",
            "values": {"202604270003": 1, "MN-202606230165": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
            "looks_like_biz_sample": True,
            "comment_fk": [("wechat_project_approval_apply", "sp_no")],
        }
    )
    assert dest == DEST_DROP
    assert reason == "comment_fk"
    dest, reason = mechanical_suggestion(
        {
            "column": "node_order",
            "comment": "节点顺序",
            "values": {"1": 1, "2": 1, "3": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
            "looks_like_ordinals": True,
        }
    )
    assert dest == DEST_DROP
    assert reason == "ordinal"
    dest, reason = mechanical_suggestion(
        {
            "column": "auth_agreement",
            "comment": "授权书协议",
            "values": {"CT-202404081721209495040": 1, "DT_202503251071": 1},
            "looks_like_ids": False,
            "looks_like_enum": True,
            "looks_like_biz_sample": True,
        }
    )
    assert dest == DEST_DROP
    assert reason == "business_id_sample"


def test_incomplete_binary_pair() -> None:
    assert incomplete_binary_pair({"Y": 10}) == ("Y", "N")
    assert incomplete_binary_pair({"N": 3}) == ("N", "Y")
    assert incomplete_binary_pair({"0": 1}) == ("0", "1")
    assert incomplete_binary_pair({"1": 1}) == ("1", "0")
    assert incomplete_binary_pair({"Y": 1, "N": 1}) is None


def test_mechanical_binary_switch_incomplete_keep() -> None:
    dest, reason = mechanical_suggestion(
        {
            "column": "enable",
            "comment": "是否启用",
            "mysql_type": "varchar(1)",
            "values": {"Y": 100},
            "looks_like_ids": False,
            "looks_like_enum": True,
            "looks_like_binary_switch": True,
        }
    )
    assert dest == DEST_DICT_KEEP
    assert reason == "binary_switch_incomplete"


def test_ai_binary_fill_adds_missing_n() -> None:
    model = {
        "tables": {
            "t": {
                "fields": [
                    {"name": "enable", "description": "是否启用", "data_type": "string"}
                ]
            }
        },
        "dict_candidates": [
            {
                "table": "t",
                "column": "enable",
                "comment": "是否启用",
                "mysql_type": "varchar(1)",
                "distinct": 1,
                "values": {"Y": 10},
                "looks_like_enum": True,
                "looks_like_ids": False,
                "looks_like_binary_switch": True,
                "dest": DEST_DICT_KEEP,
                "dest_source": "mechanical",
            }
        ],
        "dicts": {},
    }

    def chat(system: str, user: str) -> dict:
        assert "二值" in system
        return {
            "column": "enable",
            "supplement": True,
            "add": "N",
            "reason": "enable 二值开关，测库缺 N",
        }

    stats: dict[str, int] = {}
    apply_llm_triage(model, {}, chat, stats)
    assert "N" in model["dict_candidates"][0]["values"]
    assert model["dict_candidates"][0]["binary_fill"]["add"] == "N"
    assert stats.get("dict_binary_fill") == 1
    assert "N" in model["dicts"]["t__enable"]["values"]
    assert model["tables"]["t"]["fields"][0]["dictionary"] == "t__enable"


def test_ai_binary_fill_can_refuse() -> None:
    model = {
        "tables": {
            "t": {
                "fields": [
                    {"name": "enable", "description": "是否启用", "data_type": "string"}
                ]
            }
        },
        "dict_candidates": [
            {
                "table": "t",
                "column": "enable",
                "comment": "是否启用",
                "mysql_type": "varchar(1)",
                "distinct": 1,
                "values": {"Y": 10},
                "looks_like_enum": True,
                "looks_like_ids": False,
                "looks_like_binary_switch": True,
                "dest": DEST_DICT_KEEP,
                "dest_source": "mechanical",
            }
        ],
        "dicts": {},
    }

    def chat(_system: str, _user: str) -> dict:
        return {
            "column": "enable",
            "supplement": False,
            "add": None,
            "reason": "业务侧永久只写 Y",
        }

    apply_llm_triage(model, {}, chat, {})
    assert list(model["dict_candidates"][0]["values"]) == ["Y"]


def test_hold_does_not_attach_table_dictionary() -> None:
    catalog = fixture_catalog()
    profile = fixture_profile()
    profile["tables"]["cust_company_info"]["column_stats"]["payload_kind"] = {
        "distinct": 2,
        "values": {"A": 1, "B": 1},
    }
    catalog["tables"]["cust_company_info"]["columns"]["payload_kind"] = {
        "type": "varchar(16)",
        "nullable": True,
        "comment": "",
        "pos": 99,
        "key": "",
        "extra": "",
        "default": None,
    }
    model = compile_model(catalog, profile)
    assert "cust_company_info__payload_kind" in model["dicts"]
    assert model["dicts"]["cust_company_info__payload_kind"]["triage"] == "hold"
    field = next(
        f
        for f in model["tables"]["cust_company_info"]["fields"]
        if f["name"] == "payload_kind"
    )
    assert "dictionary" not in field


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


def test_parse_comment_fk() -> None:
    assert parse_comment_fk(
        "流程配置编码（tenant_project_approval_flow_config#flow_code）"
    ) == [("tenant_project_approval_flow_config", "flow_code")]
    assert parse_comment_fk("立项审批编号（wechat_project_approval_apply#sp_no）") == [
        ("wechat_project_approval_apply", "sp_no")
    ]
    assert parse_comment_fk("普通注释无关联") == []


def test_comment_fk_nominates_relation() -> None:
    catalog = fixture_catalog()
    catalog["tables"]["tenant_project_approval_flow_config"] = {
        "comment": "流程配置",
        "rows_estimate": 10,
        "primary_key": ["id"],
        "columns": {
            "id": {
                "type": "bigint",
                "nullable": False,
                "comment": "",
                "pos": 1,
                "key": "PRI",
                "extra": "",
                "default": None,
            },
            "flow_code": {
                "type": "varchar(32)",
                "nullable": False,
                "comment": "流程编码",
                "pos": 2,
                "key": "",
                "extra": "",
                "default": None,
            },
        },
        "indexes": [],
    }
    catalog["tables"]["tenant_project_approval"] = {
        "comment": "审批",
        "rows_estimate": 10,
        "primary_key": ["id"],
        "columns": {
            "id": {
                "type": "bigint",
                "nullable": False,
                "comment": "",
                "pos": 1,
                "key": "PRI",
                "extra": "",
                "default": None,
            },
            "flow_code": {
                "type": "varchar(32)",
                "nullable": True,
                "comment": "流程配置编码（tenant_project_approval_flow_config#flow_code）",
                "pos": 2,
                "key": "",
                "extra": "",
                "default": None,
            },
        },
        "indexes": [],
    }
    model = compile_model(catalog, {"tables": {}})
    rels = model["tables"]["tenant_project_approval"]["relations"]
    assert any(
        r["left"] == "tenant_project_approval_flow_config.flow_code"
        and r["right"] == "tenant_project_approval.flow_code"
        and r["source"] == "comment_fk"
        for r in rels
    )


def test_target_key_prefers_same_name_code() -> None:
    from tools.wiki_extract.heuristics import _target_key

    peer = {"column_names": ["id", "code", "flow_code"], "primary_key": ["id"]}
    assert _target_key(peer, "flow_code") == "flow_code"
    assert _target_key(peer, "product_code") == "code"
    assert _target_key(peer, "company_id") == "id"


def test_pass2_only_dict_verdicts() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())

    def chat(system: str, user: str) -> dict:
        if "二值" in system:
            return {
                "column": "enable",
                "supplement": False,
                "add": None,
                "reason": "skip",
            }
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
