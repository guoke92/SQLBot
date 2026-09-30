"""Mechanical field glosses, with an injected chat function."""

from __future__ import annotations

import yaml

from tools.wiki_extract.cli import main
from tools.wiki_extract.field_gloss import apply_llm_glosses, mechanical_gloss
from tools.wiki_extract.value_sketch import FieldSketch


def _sketch(**overrides: object) -> FieldSketch:
    data = {
        "fq": "cust_company_info.certification_no",
        "table": "cust_company_info",
        "column": "certification_no",
        "comment": "",
        "shape": {
            "len_mode": 18,
            "len_mode_ratio": 1.0,
            "numeric_ratio": 1.0,
            "common_prefix": "91",
        },
    }
    data.update(overrides)
    return FieldSketch(**data)  # type: ignore[arg-type]


def test_strong_comment_is_left_alone() -> None:
    assert mechanical_gloss(_sketch(comment="统一社会信用代码")) is None


def test_mechanical_gloss_uses_shape() -> None:
    gloss = mechanical_gloss(_sketch(), samples=["91310000"])
    assert gloss is not None
    assert gloss["trust"] == "proposed"
    assert gloss["source"] == "shape"
    assert "长度多为 18" in gloss["gloss"]
    assert "全是数字" in gloss["gloss"]
    assert "公共前缀 91" in gloss["gloss"]
    assert "91310000" in gloss["gloss"]


def test_llm_failure_keeps_mechanical_gloss() -> None:
    gloss = mechanical_gloss(_sketch())
    assert gloss is not None

    def _boom(_system: str, _user: str) -> dict[str, object]:
        raise RuntimeError("offline")

    kept = apply_llm_glosses(_boom, [gloss])
    assert kept[0]["gloss"] == gloss["gloss"]
    assert kept[0]["source"] == "shape"


def test_llm_rewrite_marks_source() -> None:
    gloss = mechanical_gloss(_sketch())
    assert gloss is not None

    def _chat(_system: str, _user: str) -> dict[str, object]:
        return {"items": [{"fq": gloss["fq"], "gloss": "统一社会信用代码，18 位数字。"}]}

    rewritten = apply_llm_glosses(_chat, [gloss])
    assert rewritten[0]["gloss"] == "统一社会信用代码，18 位数字。"
    assert rewritten[0]["source"] == "shape+llm"


def test_value_sketch_cli_writes_pairs_and_glosses(tmp_path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    catalog = {
        "tables": {
            "parent": {"columns": {"code": {"comment": "", "type": "varchar(8)"}}},
        }
    }
    profile = {
        "tables": {
            "parent": {
                "column_stats": {
                    "code": {"values": {"10000001": 3, "10000002": 1, "10000003": 1}}
                }
            }
        }
    }
    (raw / "catalog.yaml").write_text(
        yaml.safe_dump(catalog, allow_unicode=True), encoding="utf-8"
    )
    (raw / "profile.yaml").write_text(
        yaml.safe_dump(profile, allow_unicode=True), encoding="utf-8"
    )
    out = tmp_path / "value_sketch.yaml"
    assert main(["value-sketch", "--from-raw", str(raw), "--out", str(out)]) == 0
    report = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert report["fields"] == 1
    assert report["pairs"] == []
    assert report["glosses"][0]["fq"] == "parent.code"
    assert "长度多为" in report["glosses"][0]["gloss"]
