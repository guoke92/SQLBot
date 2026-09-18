"""Overlap merge, column skip, and dual-evidence LLM joins — no live database."""

from __future__ import annotations

from tools.wiki_extract.heuristics import compile_model
from tools.wiki_extract.join_policy import (
    child_endpoint_reason,
    decide_authenticity,
    merge_llm_authenticity,
)
from tools.wiki_extract.llm_refine import refine_model, replay_judgments
from tools.wiki_extract.overlap import (
    apply_overlap,
    skip_overlap_child,
    validate_proposed_join,
)
from tools.wiki_extract.tests.test_l0_compile import fixture_catalog, fixture_profile


def test_skip_generic_and_temporal_endpoints() -> None:
    assert skip_overlap_child("id", "bigint(20)") == "skipped_generic_column"
    assert skip_overlap_child("create_time", "datetime") == "skipped_generic_column"
    assert skip_overlap_child("update_time", "datetime") == "skipped_generic_column"
    assert skip_overlap_child("req_time", "datetime") == "skipped_generic_column"
    assert skip_overlap_child("signed_on", "date") == "skipped_temporal_type"
    assert skip_overlap_child("rule_info_id", "bigint(20)") == ""
    assert skip_overlap_child("fund_rule_code_ref", "varchar(32)") == ""
    assert skip_overlap_child("parent_id", "bigint(20)") == ""
    assert child_endpoint_reason("parent_id", "bigint(20)") == ""


def test_bigint_varchar_ref_types_compatible() -> None:
    from tools.wiki_extract.join_policy import types_compatible

    assert types_compatible("varchar(128)", "bigint(22)")
    assert types_compatible("bigint(22)", "varchar(64)")
    assert types_compatible("int", "varchar(32)")
    assert not types_compatible("datetime", "bigint(22)")
    assert not types_compatible("json", "varchar(32)")


def test_authenticity_thresholds() -> None:
    assert decide_authenticity(sample_size=80, forward=0.99).value == "likely"
    assert decide_authenticity(sample_size=80, forward=0.0).value == "unlikely"
    mid = decide_authenticity(sample_size=40, forward=0.55)
    assert mid.value == "unknown" and mid.deepen
    tiny = decide_authenticity(sample_size=2, forward=1.0, deepened=True)
    assert tiny.value == "unknown" and not tiny.deepen
    failed = decide_authenticity(sample_size=80, forward=None, query_ok=False)
    assert failed.value == "unknown"
    assert (
        decide_authenticity(
            sample_size=80, forward=0.97, reverse=0.05, deepened=True
        ).value
        == "likely"
    )
    assert (
        decide_authenticity(
            sample_size=80, forward=0.02, reverse=0.9, deepened=True
        ).value
        == "unknown"
    )


def test_llm_missing_vote_keeps_overlap() -> None:
    auth, extra = merge_llm_authenticity(
        current="likely",
        overlap_probed=True,
        overlap_auth="likely",
        llm_auth=None,
    )
    assert auth == "likely"
    assert extra == ""


def test_replay_without_join_vote_keeps_overlap_likely() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())
    apply_overlap(
        model,
        {
            "edges": [
                {
                    "left": "cust_company_info.id",
                    "right": "cust_account_info.cust_company_id",
                    "source": "name",
                    "overlap_ratio": 0.99,
                    "sample_size": 80,
                    "authenticity": "likely",
                }
            ]
        },
    )
    assert (
        model["tables"]["cust_account_info"]["relations"][0]["authenticity"] == "likely"
    )
    refined = replay_judgments(
        model,
        {
            "tables": {
                "cust_account_info": {"dicts": [], "clusters": [], "joins": []},
                "cust_company_info": {
                    "dicts": [{"column": "sign_status", "verdict": "instance"}],
                    "clusters": [],
                },
            }
        },
    )
    assert (
        refined["tables"]["cust_account_info"]["relations"][0]["authenticity"]
        == "likely"
    )


def test_apply_overlap_rechecks_name_edge_and_adds_likely() -> None:
    catalog = {
        "database": "db",
        "tables": {
            "funding_rule_info": {
                "comment": "规则主表",
                "primary_key": ["id"],
                "columns": {
                    "id": {
                        "type": "bigint(20)",
                        "nullable": False,
                        "comment": "",
                        "pos": 1,
                        "key": "PRI",
                        "extra": "",
                        "default": None,
                    },
                    "code": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "",
                        "pos": 2,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "create_time": {
                        "type": "datetime",
                        "nullable": True,
                        "comment": "",
                        "pos": 3,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                },
            },
            "funding_rule_detail": {
                "comment": "规则明细",
                "primary_key": ["id"],
                "columns": {
                    "id": {
                        "type": "bigint(20)",
                        "nullable": False,
                        "comment": "",
                        "pos": 1,
                        "key": "PRI",
                        "extra": "",
                        "default": None,
                    },
                    "rule_info_id": {
                        "type": "bigint(20)",
                        "nullable": True,
                        "comment": "规则主表",
                        "pos": 2,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "fund_rule_code_ref": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "规则编码",
                        "pos": 3,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "product_code": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "",
                        "pos": 4,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "create_time": {
                        "type": "datetime",
                        "nullable": True,
                        "comment": "",
                        "pos": 5,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                },
            },
        },
    }
    model = compile_model(catalog, {"tables": {}})
    detail = model["tables"]["funding_rule_detail"]["relations"]
    assert any(r["right"].endswith(".rule_info_id") for r in detail)
    assert all(r["type"] == "EQUI_JOIN" for r in detail)

    packed = {
        "edges": [
            {
                "left": "funding_rule_info.id",
                "right": "funding_rule_detail.rule_info_id",
                "source": "name",
                "name_match": "family_suffix",
                "sample_size": 180,
                "overlap_ratio": 0.99,
                "overlap_ratio_reverse": 0.12,
                "deepened": False,
                "miss": 1,
                "authenticity": "likely",
                "evidence": "database_profile:db.funding_rule_detail.rule_info_id",
            },
            {
                "left": "funding_rule_info.code",
                "right": "funding_rule_detail.fund_rule_code_ref",
                "source": "overlap",
                "name_match": "none",
                "sample_size": 40,
                "overlap_ratio": 0.97,
                "overlap_ratio_reverse": 0.4,
                "deepened": True,
                "miss": 1,
                "authenticity": "likely",
                "evidence": "database_profile:db.funding_rule_detail.fund_rule_code_ref",
            },
            {
                "left": "funding_rule_info.code",
                "right": "funding_rule_detail.product_code",
                "source": "overlap",
                "authenticity": "likely",
                "overlap_ratio": 0.99,
                "sample_size": 20,
            },
        ],
        "unresolved_probes": [
            {
                "left": "funding_rule_info.id",
                "right": "funding_rule_detail.fund_rule_code_ref",
                "overlap_ratio": 0.01,
                "sample_size": 40,
                "authenticity": "unlikely",
            }
        ],
        "skipped_columns": ["funding_rule_detail.create_time"],
    }
    apply_overlap(model, packed)
    rels = model["tables"]["funding_rule_detail"]["relations"]
    by_right = {r["right"]: r for r in rels}
    named = by_right["funding_rule_detail.rule_info_id"]
    assert named["authenticity"] == "likely"
    assert named["overlap"]["probed"] is True
    assert named["overlap"]["ratio"] == 0.99
    assert named["name_evidence"]["match"] == "family_suffix"
    added = by_right["funding_rule_detail.fund_rule_code_ref"]
    assert added["source"] == "overlap"
    assert added["overlap"]["deepened"] is True
    assert added["overlap"]["authenticity"] == "likely"
    assert added["authenticity"] == "unknown"
    assert added["preview_block"] == "overlap_unsemantic"
    code_edge = by_right["funding_rule_detail.product_code"]
    assert code_edge["type"] == "EQUI_JOIN"
    assert code_edge["join_role"] == "business_code"
    assert code_edge["priority"] == "secondary"
    assert code_edge["authenticity"] == "unknown"
    assert named["join_role"] == "identity"
    assert named["priority"] == "primary"
    assert named["authenticity"] == "likely"
    assert not any(r["type"] == "CONTAINS" for r in rels)


def test_controversial_fixture_keeps_unknown_and_deepened() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())
    packed = {
        "edges": [
            {
                "left": "cust_company_info.id",
                "right": "cust_account_info.cust_company_id",
                "source": "name",
                "sample_size": 50,
                "overlap_ratio": 0.55,
                "overlap_ratio_reverse": 0.2,
                "deepened": True,
                "miss": 22,
                "authenticity": "unknown",
            }
        ]
    }
    apply_overlap(model, packed)
    rel = model["tables"]["cust_account_info"]["relations"][0]
    assert rel["authenticity"] == "unknown"
    assert rel["overlap"]["deepened"] is True
    assert rel["overlap"]["ratio_reverse"] == 0.2


def test_llm_payload_carries_name_and_overlap() -> None:
    model = compile_model(fixture_catalog(), fixture_profile())
    apply_overlap(
        model,
        {
            "edges": [
                {
                    "left": "cust_company_info.id",
                    "right": "cust_account_info.cust_company_id",
                    "source": "name",
                    "overlap_ratio": 0.99,
                    "overlap_ratio_reverse": 0.1,
                    "sample_size": 80,
                    "deepened": False,
                    "miss": 0,
                    "authenticity": "likely",
                }
            ]
        },
    )
    seen: list[str] = []

    def chat(_system: str, user: str) -> dict:
        seen.append(user)
        if "cust_account_info" in user:
            assert "name_evidence" in user
            assert '"probed": true' in user or '"probed": True' in user
            assert "ratio_reverse" in user
            assert "unresolved_join_window" in user
            return {
                "dicts": [],
                "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
                "joins": [
                    {
                        "right": "cust_account_info.cust_company_id",
                        "authenticity": "unlikely",
                        "note": "disagree",
                    }
                ],
                "propose_joins": [],
            }
        return {
            "dicts": [],
            "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
        }

    refined = refine_model(model, chat, workers=1)
    rel = refined["tables"]["cust_account_info"]["relations"][0]
    assert rel["authenticity"] == "likely"
    assert rel["llm_authenticity"] == "unlikely"
    assert rel["trust"] == "proposed"
    assert any("name_evidence" in blob for blob in seen)


def test_propose_joins_window_and_hard_reject() -> None:
    catalog = {
        "database": "db",
        "tables": {
            "funding_rule_info": {
                "comment": "规则主表",
                "primary_key": ["id"],
                "columns": {
                    "id": {
                        "type": "bigint(20)",
                        "nullable": False,
                        "comment": "",
                        "pos": 1,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "code": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "",
                        "pos": 2,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "product_code": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "",
                        "pos": 3,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                },
            },
            "funding_rule_detail": {
                "comment": "规则明细",
                "primary_key": ["id"],
                "columns": {
                    "id": {
                        "type": "bigint(20)",
                        "nullable": False,
                        "comment": "",
                        "pos": 1,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "rule_info_id": {
                        "type": "bigint(20)",
                        "nullable": True,
                        "comment": "规则主表",
                        "pos": 2,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "fund_rule_code_ref": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "规则编码",
                        "pos": 3,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                    "product_code": {
                        "type": "varchar(32)",
                        "nullable": True,
                        "comment": "",
                        "pos": 4,
                        "key": "",
                        "extra": "",
                        "default": None,
                    },
                },
            },
        },
    }
    model = compile_model(catalog, {"tables": {}})
    assert (
        validate_proposed_join(
            model,
            "ghost.id",
            "funding_rule_detail.fund_rule_code_ref",
            window_lefts={"funding_rule_info.code"},
        )
        == "unknown_table"
    )
    assert (
        validate_proposed_join(
            model,
            "funding_rule_info.product_code",
            "funding_rule_detail.product_code",
            window_lefts={"funding_rule_info.product_code"},
        )
        == ""
    )

    def chat(_s: str, user: str) -> dict:
        if "funding_rule_detail" not in user:
            return {
                "dicts": [],
                "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
            }
        assert "unresolved_join_window" in user
        return {
            "dicts": [],
            "clusters": [{"key": "common", "include": "always", "fields": ["id"]}],
            "joins": [],
            "propose_joins": [
                {
                    "left": "funding_rule_info.code",
                    "right": "funding_rule_detail.fund_rule_code_ref",
                    "verdict": "accept",
                    "note": "code ref",
                },
                {
                    "left": "nope_table.id",
                    "right": "funding_rule_detail.fund_rule_code_ref",
                    "verdict": "accept",
                    "note": "invented",
                },
                {
                    "left": "funding_rule_info.product_code",
                    "right": "funding_rule_detail.product_code",
                    "verdict": "accept",
                    "note": "copy",
                },
            ],
        }

    refined = refine_model(model, chat, workers=1)
    rels = refined["tables"]["funding_rule_detail"]["relations"]
    rights = {r["right"]: r for r in rels}
    assert "funding_rule_detail.fund_rule_code_ref" in rights
    code_edge = rights["funding_rule_detail.product_code"]
    assert code_edge["left"] == "funding_rule_info.product_code"
    assert code_edge["join_role"] == "business_code"
    assert code_edge["priority"] == "secondary"
    assert any(
        r["join_role"] == "identity" and r["priority"] == "primary" for r in rels
    )
    assert all(r["left"] != "nope_table.id" for r in rels)
    assert all(r["type"] == "EQUI_JOIN" for r in rels)


def test_merge_llm_cannot_mint_likely_without_semantic() -> None:
    auth, extra = merge_llm_authenticity(
        current="unknown",
        overlap_probed=True,
        overlap_auth="likely",
        llm_auth="likely",
        semantic=False,
    )
    assert auth == "unknown"
    assert "semantic" in extra
    auth, extra = merge_llm_authenticity(
        current="unknown",
        overlap_probed=True,
        overlap_auth="likely",
        llm_auth="unlikely",
        semantic=False,
    )
    assert auth == "unknown"


def test_cap_inclusion_ratio_never_exceeds_one() -> None:
    from tools.wiki_extract.overlap import cap_inclusion

    hit, ratio = cap_inclusion(80, 40)
    assert hit == 40
    assert ratio == 1.0
    hit, ratio = cap_inclusion(0, 10)
    assert hit == 0
    assert ratio == 0.0
    hit, ratio = cap_inclusion(5, 0)
    assert hit == 0
    assert ratio is None
