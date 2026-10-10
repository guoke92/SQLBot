"""Wiki page catalog: workspace scope, missing pages, parsed contract fields."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import pytest  # noqa: E402

from apps.knowledge.api.wiki import catalog_http_error  # noqa: E402
from apps.knowledge.db_models import WikiPageRow  # noqa: E402
from apps.knowledge.wiki.browse import (  # noqa: E402
    CatalogNotFound,
    filter_page_catalog,
    get_page_detail,
    list_page_catalog,
    page_detail_payload,
)

_CONCEPT = """---
page_key: 平台录入
title: 平台录入
type: concept
status: draft
belong: concepts
domain: 企业建档
aliases: [PC端录入]
maps_to: cust_company_info.cust_build_type
field_targets: [cust_company_info.cust_build_type]
related: [cust_company_info]
anchors: [cust_company_info.cust_build_type]
sources: [test]
contract_version: "0.1"
---

平台录入对应 [[cust_company_info]] 的建档方式。

```ground:caliber
caliber: 平台录入
predicate: cust_build_type = PC_BUILD
```

---REVIEW: gap | 缺启用过滤---
默认统计是否含停用企业尚未写明。
---END REVIEW---
"""


def _row(body: str) -> WikiPageRow:
    now = datetime(2026, 10, 10, 8, 0, 0)
    return WikiPageRow(
        corpus_id=1,
        belong="concepts",
        page_key="平台录入",
        page_type="concept",
        title="平台录入",
        status="draft",
        aliases=["PC端录入"],
        anchors=["cust_company_info.cust_build_type"],
        body_md=body,
        content_sha="abc",
        create_time=now,
        update_time=now,
    )


def test_detail_restores_maps_to_ground_and_review() -> None:
    payload = page_detail_payload(
        _row(_CONCEPT),
        known_keys={"cust_company_info", "tables/cust_company_info"},
    )
    assert payload["parse_error"] is None
    assert payload["maps_to"] == "cust_company_info.cust_build_type"
    assert payload["ground"] == [{"kind": "caliber", "label": "平台录入"}]
    assert payload["reviews"][0]["title"] == "缺启用过滤"
    assert "停用企业" in payload["reviews"][0]["body"]
    assert payload["links"][0]["target"] == "cust_company_info"
    assert payload["body"].startswith("平台录入对应")
    assert "cust_build_type = PC_BUILD" in payload["body"]
    assert "缺启用过滤" in payload["body"]
    assert "```ground:" not in payload["body"]


def test_present_keeps_ground_content_for_every_page_kind() -> None:
    from apps.knowledge.wiki.present import present_page_body

    root = Path(__file__).resolve().parents[1] / "docs" / "wiki" / "v3"
    samples = {
        "dicts/argeement_migratory_record__agreement_type.md": "PrivacyPolicy",
        "dicts/ca_fee_company__pay_status.md": "未缴费",
        "tables/ca_fee_company.md": "统一社会信用代码",
        "processes/async_io_task__status.md": "RUNNING",
        "calibers/freeze_audit_record.md": "enable = 'Y'",
        "metrics/effective_company_count.md": "count_distinct",
        "rules/survey_answer_once_per_company.md": "write_constraint",
        "scenarios/ca_fee_pay.md": "ca_fee_order",
    }
    for rel, needle in samples.items():
        shown = present_page_body((root / rel).read_text(encoding="utf-8"))
        assert needle in shown, rel
        assert "```ground:" not in shown, rel
    joins = present_page_body((root / "tables/ca_fee_company.md").read_text(encoding="utf-8"))
    assert "cust_company_info.certification_no" in joins
    assert "ca_fee_company.certification_no" in joins


def test_other_workspace_corpus_is_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, int] = {}

    def _hidden(session: object, oid: int, corpus_key: str) -> None:
        seen["oid"] = oid
        assert corpus_key == "pplatform"
        return None

    monkeypatch.setattr("apps.knowledge.wiki.browse.get_corpus", _hidden)
    with pytest.raises(CatalogNotFound) as exc:
        list_page_catalog(None, oid=7, corpus_key="pplatform")  # type: ignore[arg-type]
    assert exc.value.kind == "corpus"
    assert seen["oid"] == 7
    error = catalog_http_error(exc.value)
    assert error.status_code == 404
    assert error.detail == "corpus not found"


def test_missing_page_is_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps.knowledge.wiki.browse.get_corpus",
        lambda session, oid, corpus_key: SimpleNamespace(id=3, corpus_key=corpus_key),
    )

    class _Result:
        def first(self) -> None:
            return None

    class _Session:
        def exec(self, statement: object) -> _Result:
            return _Result()

    with pytest.raises(CatalogNotFound) as exc:
        get_page_detail(
            _Session(),  # type: ignore[arg-type]
            oid=1,
            corpus_key="pplatform",
            belong="concepts",
            page_key="缺失",
        )
    assert exc.value.kind == "page"
    error = catalog_http_error(exc.value)
    assert error.status_code == 404
    assert error.detail == "page not found"


def test_catalog_filter_matches_alias_and_status() -> None:
    rows = [
        SimpleNamespace(
            belong="concepts",
            page_key="平台录入",
            title="平台录入",
            page_type="concept",
            status="draft",
            aliases=["PC端录入"],
        ),
        SimpleNamespace(
            belong="tables",
            page_key="cust_company_info",
            title="企业信息",
            page_type="table",
            status="published",
            aliases=["企业"],
        ),
    ]
    drafted = filter_page_catalog(rows, status="draft")
    assert [item["page_key"] for item in drafted["pages"]] == ["平台录入"]
    assert drafted["counts"] == [{"belong": "concepts", "count": 1}]
    aliased = filter_page_catalog(rows, q="pc端")
    assert [item["page_key"] for item in aliased["pages"]] == ["平台录入"]
    tables = filter_page_catalog(rows, belong="tables")
    assert [item["page_key"] for item in tables["pages"]] == ["cust_company_info"]
    assert {item["belong"] for item in tables["counts"]} == {"concepts", "tables"}
    linked = filter_page_catalog(
        [
            SimpleNamespace(
                belong="concepts",
                page_key="平台录入",
                title="平台录入",
                page_type="concept",
                status="draft",
                aliases=[],
                body_md="见 [[tables/cust_company_info]] 与 [[cust_company_info#概述]]。",
            )
        ]
    )
    assert linked["pages"][0]["links"] == ["tables/cust_company_info", "cust_company_info"]
