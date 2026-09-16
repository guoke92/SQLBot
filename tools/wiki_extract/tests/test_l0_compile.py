"""L0 compile from fixture catalog — no live database."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.wiki_extract.cli import main
from tools.wiki_extract.emit import emit
from tools.wiki_extract.heuristics import compile_model


def _col(
    pos: int, mysql_type: str, comment: str = "", *, nullable: bool = True
) -> dict:
    return {
        "type": mysql_type,
        "nullable": nullable,
        "comment": comment,
        "pos": pos,
        "key": "",
        "extra": "",
        "default": None,
    }


def fixture_catalog() -> dict:
    return {
        "database": "lowcode_pplatform",
        "generated_at": "2026-09-15",
        "tables": {
            "cust_company_info": {
                "engine": "InnoDB",
                "comment": "企业主档",
                "rows_estimate": 100,
                "primary_key": ["id"],
                "indexes": [{"name": "PRIMARY", "unique": True, "columns": ["id"]}],
                "columns": {
                    "id": _col(1, "bigint(20)", "主键", nullable=False),
                    "code": _col(2, "varchar(64)", "编码"),
                    "name": _col(3, "varchar(128)", "企业名称"),
                    "enable": _col(4, "varchar(4)", "有效"),
                    "create_time": _col(5, "datetime", "创建时间"),
                    "update_time": _col(6, "datetime", "更新时间"),
                    "sign_status": _col(7, "varchar(32)", "签约状态"),
                    "create_by": _col(8, "varchar(64)", "创建人"),
                },
            },
            "cust_account_info": {
                "engine": "InnoDB",
                "comment": "企业银行账户",
                "rows_estimate": 50,
                "primary_key": ["id"],
                "indexes": [{"name": "PRIMARY", "unique": True, "columns": ["id"]}],
                "columns": {
                    "id": _col(1, "bigint(20)", "主键", nullable=False),
                    "enable": _col(2, "varchar(4)"),
                    "account_name": _col(3, "varchar(128)", "户名"),
                    "account_no": _col(4, "varchar(64)", "账号"),
                    "bank_name": _col(5, "varchar(128)", "开户行"),
                    "bank_code": _col(6, "varchar(32)", "行号"),
                    "bank_city": _col(7, "varchar(64)", "开户城市"),
                    "cust_company_id": _col(8, "bigint(20)", "企业"),
                },
            },
            "cust_company_detail": {
                "engine": "InnoDB",
                "comment": "企业明细",
                "rows_estimate": 100,
                "primary_key": ["id"],
                "indexes": [{"name": "PRIMARY", "unique": True, "columns": ["id"]}],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "cust_company_id": _col(2, "bigint(20)", "企业"),
                    "extra": _col(3, "varchar(64)"),
                },
            },
        },
    }


def fixture_profile() -> dict:
    return {
        "database": "lowcode_pplatform",
        "tables": {
            "cust_company_info": {
                "rows_estimate": 100,
                "column_stats": {
                    "sign_status": {
                        "distinct": 2,
                        "values": {"SIGNED": 80, "DRAFT": 20, "": 1},
                    },
                    "name": {
                        "distinct": 3,
                        "values": {"甲公司": 1, "乙公司": 1, "丙公司": 1},
                    },
                },
            }
        },
    }


def test_l0_compile_fixture(tmp_path: Path) -> None:
    out = tmp_path / "l0"
    catalog = fixture_catalog()
    model = compile_model(catalog, fixture_profile())
    stats = emit(model, out, catalog=catalog, profile=fixture_profile())

    assert stats["tables"] == 3
    company = (out / "tables" / "cust_company_info.md").read_text(encoding="utf-8")
    account = (out / "tables" / "cust_account_info.md").read_text(encoding="utf-8")
    detail = (out / "tables" / "cust_company_detail.md").read_text(encoding="utf-8")

    assert "status: draft" in company
    assert "status: published" not in company
    for col in (
        "id",
        "code",
        "name",
        "enable",
        "create_time",
        "update_time",
        "sign_status",
        "create_by",
    ):
        assert f"name: {col}" in company

    assert "key: common" in company
    assert "include: always" in company
    assert "scenes:" not in company
    assert "label:" not in (
        out / "enums" / "cust_company_info::sign_status.md"
    ).read_text(encoding="utf-8")
    enum_page = (out / "enums" / "cust_company_info::sign_status.md").read_text(
        encoding="utf-8"
    )
    assert "SIGNED" in enum_page
    assert "平台录入" not in enum_page
    assert "status: draft" in enum_page
    assert "page_key: cust_company_info::sign_status" in enum_page
    assert "cust_company_info.sign_status" in enum_page  # physical field
    assert "cust_company_info_sign_status" not in enum_page
    assert "[[tables/cust_company_info]]" in enum_page
    assert "? ''" not in enum_page
    assert "trust: proposed" in enum_page
    assert "ambiguous:" not in enum_page

    assert "trust: proposed" in account
    assert "cust_company_id" in account
    assert "cust_company_info.id" in account
    assert "type: EQUI_JOIN" in account
    assert "cardinality: one_to_many" in account
    assert "left: cust_company_info.id" in account
    assert "right: cust_account_info.cust_company_id" in account
    assert "[[tables/cust_company_info]]" in account
    assert "[[tables/cust_account_info]]" in company
    assert "[[tables/cust_company_detail]]" in company
    assert "[[enums/cust_company_info::sign_status]]" in company
    assert "related:" in account
    assert "related:" in company

    assert "cust_company_info.id" in detail
    assert "cust_company_id" in detail

    assert "key: bank" in account
    assert "bank_name" in account

    value_index = yaml.safe_load((out / "value_index.yaml").read_text(encoding="utf-8"))
    names = [
        entry
        for entry in value_index["entries"]
        if entry["table"] == "cust_company_info" and entry["column"] == "name"
    ]
    assert names
    assert any(item["value"] == "甲公司" for item in names[0]["values"])

    reviews = yaml.safe_load((out / ".runs" / "l0" / "reviews.yaml").read_text())
    assert reviews["items"]
    assert all(item["status"] == "open" for item in reviews["items"])
    assert any(item["kind"] == "unverified_join" for item in reviews["items"])
    assert not any("#grain" in item["claim_path"] for item in reviews["items"])
    assert not any("#clusters." in item["claim_path"] for item in reviews["items"])
    assert not any(
        item["kind"] == "unanchored" and item["claim_path"].startswith("enums/")
        for item in reviews["items"]
    )

    assert (out / "_log.md").exists()
    assert (out / "_index.md").exists()
    assert (out / "_raw" / "catalog.yaml").exists()


def test_code_join_uses_code_not_id() -> None:
    catalog = {
        "database": "lowcode_pplatform",
        "tables": {
            "bank": {
                "comment": "银行",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "code": _col(2, "varchar(32)"),
                    "name": _col(3, "varchar(64)"),
                },
            },
            "cust_account_info": {
                "comment": "账户",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "bank_code": _col(2, "varchar(32)"),
                    "account_name": _col(3, "varchar(64)"),
                },
            },
        },
    }
    model = compile_model(catalog, {"tables": {}})
    rels = model["tables"]["cust_account_info"]["relations"]
    assert len(rels) == 1
    assert rels[0]["left"] == "bank.code"
    assert rels[0]["right"] == "cust_account_info.bank_code"
    assert rels[0]["trust"] == "proposed"
    assert rels[0]["authenticity"] == "unknown"
    assert rels[0]["source"] == "name"
    assert rels[0]["name_evidence"]["match"] in {"exact_table", "stem_info"}
    assert rels[0]["overlap"] == {"probed": False}
    anchors = model["tables"]["cust_account_info"]["name_anchors"]
    assert "bank_code" not in anchors
    assert not any("bank.id" in (r["left"] + r["right"]) for r in rels)
    names_as_join = [
        r
        for r in rels
        if r["right"].endswith(".account_name") or r["left"].endswith(".name")
    ]
    assert names_as_join == []


def test_missing_pk_is_review_not_invented() -> None:
    catalog = {
        "database": "db",
        "tables": {
            "no_pk": {
                "comment": "无主键",
                "primary_key": [],
                "indexes": [],
                "columns": {"name": _col(1, "varchar(32)")},
            }
        },
    }
    model = compile_model(catalog, {"tables": {}})
    assert model["tables"]["no_pk"]["primary_key"] == []
    assert any(
        item["kind"] == "missing" and "primary_key" in item["claim_path"]
        for item in model["reviews"]
    )


def test_cli_compile_from_raw(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "catalog.yaml").write_text(
        yaml.safe_dump(fixture_catalog(), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    (raw / "profile.yaml").write_text(
        yaml.safe_dump(fixture_profile(), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    out = tmp_path / "l0"
    assert (
        main(["compile", "--from-raw", str(raw), "--out", str(out), "--skip-llm"]) == 0
    )
    assert (out / "tables" / "cust_company_info.md").exists()
    assert not (tmp_path / "wiki-pages").exists()


def test_emit_refuses_old_corpus(tmp_path: Path) -> None:
    catalog = fixture_catalog()
    model = compile_model(catalog, {"tables": {}})
    banned = tmp_path / "wiki-pages"
    banned.mkdir()
    with pytest.raises(ValueError, match="wiki corpus"):
        emit(model, banned)

    db_dir = tmp_path / "db"
    db_dir.mkdir()
    with pytest.raises(ValueError, match="db substrate"):
        emit(model, db_dir)


def test_comment_labels_and_invented_dropped() -> None:
    catalog = {
        "database": "db",
        "tables": {
            "cust_group_rel": {
                "comment": "集团关系",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "status": _col(
                        2,
                        "varchar(32)",
                        "状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED",
                    ),
                    "enable": _col(3, "varchar(4)", "enable"),
                    "root_flag": _col(4, "varchar(4)", "是否集团企业 Y:是 N:不是"),
                },
            }
        },
    }
    profile = {
        "tables": {
            "cust_group_rel": {
                "column_stats": {
                    "status": {
                        "distinct": 3,
                        "values": {"EFFECTIVE": 2, "INEFFECTIVE": 1, "REJECTED": 1},
                    },
                    "enable": {"distinct": 2, "values": {"Y": 3, "N": 1}},
                    "root_flag": {"distinct": 2, "values": {"Y": 2, "N": 1}},
                }
            }
        }
    }
    model = compile_model(catalog, profile)
    status = model["enums"]["cust_group_rel::status"]["values"]
    assert status["EFFECTIVE"]["label"] == "已生效"
    assert status["EFFECTIVE"]["trust"] == "proposed"
    enable = model["enums"]["cust_group_rel::enable"]["values"]
    assert "label" not in enable["Y"]
    flags = model["enums"]["cust_group_rel::root_flag"]["values"]
    assert flags["Y"]["label"] == "是"
    assert flags["N"]["label"] == "不是"


def test_dual_identity_edges_all_kept() -> None:
    catalog = {
        "database": "db",
        "tables": {
            "cust_company_info": {
                "comment": "企业",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "code": _col(2, "varchar(32)"),
                    "name": _col(3, "varchar(64)", "名称"),
                },
            },
            "cust_person_info": {
                "comment": "联系人",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "ref_cust_company_info": _col(2, "varchar(64)", "所属企业"),
                    "cust_company_id": _col(3, "bigint(20)", "企业id"),
                    "name": _col(4, "varchar(64)", "姓名"),
                },
            },
        },
    }
    model = compile_model(catalog, {"tables": {}})
    rights = {r["right"] for r in model["tables"]["cust_person_info"]["relations"]}
    assert rights == {
        "cust_person_info.ref_cust_company_info",
        "cust_person_info.cust_company_id",
    }
    assert all(
        r["trust"] == "proposed" and "primary" not in r
        for r in model["tables"]["cust_person_info"]["relations"]
    )
    join_reviews = [i for i in model["reviews"] if i["kind"] == "unverified_join"]
    assert len(join_reviews) == 2


def test_family_abbreviated_fk_and_long_ref() -> None:
    catalog = {
        "database": "db",
        "tables": {
            "funding_rule_info": {
                "comment": "规则主表",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "code": _col(2, "varchar(32)"),
                    "product_code": _col(3, "varchar(32)"),
                },
            },
            "funding_rule_detail": {
                "comment": "规则明细",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "rule_info_id": _col(2, "bigint(20)", "规则主表"),
                    "product_code": _col(3, "varchar(32)"),
                },
            },
            "ca_fee_company": {
                "comment": "缴费企业",
                "primary_key": ["id"],
                "columns": {"id": _col(1, "bigint(20)", nullable=False)},
            },
            "ca_fee_order": {
                "comment": "缴费订单",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "company_id": _col(2, "bigint(20)"),
                },
            },
            "cust_company_info": {
                "comment": "企业",
                "primary_key": ["id"],
                "columns": {"id": _col(1, "bigint(20)", nullable=False)},
            },
            "cust_head_company_info": {
                "comment": "总公司",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "code": _col(2, "varchar(64)"),
                },
            },
            "cust_survey_answer": {
                "comment": "问卷答案",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "company_id": _col(2, "bigint(20)"),
                },
            },
            "cust_customized_product": {
                "comment": "快捷入口",
                "primary_key": ["id"],
                "columns": {
                    "id": _col(1, "bigint(20)", nullable=False),
                    "ref_cust_customized_product_cust_company_info": _col(
                        2, "varchar(64)"
                    ),
                    "product_code": _col(3, "varchar(32)"),
                },
            },
        },
    }
    model = compile_model(catalog, {"tables": {}})
    detail = model["tables"]["funding_rule_detail"]["relations"]
    assert any(
        r["left"] == "funding_rule_info.id" and r["right"].endswith(".rule_info_id")
        for r in detail
    )
    assert not any(r["right"].endswith(".product_code") for r in detail)
    fee = model["tables"]["ca_fee_order"]["relations"]
    assert fee[0]["left"] == "ca_fee_company.id"
    assert not any("cust_company_info" in r["left"] for r in fee)
    survey = model["tables"]["cust_survey_answer"]["relations"]
    assert survey[0]["left"] == "cust_company_info.id"
    custom = model["tables"]["cust_customized_product"]["relations"]
    assert any(
        r["left"] == "cust_company_info.id"
        and r["right"].endswith("ref_cust_customized_product_cust_company_info")
        for r in custom
    )
    assert not any(r["right"].endswith(".product_code") for r in custom)
