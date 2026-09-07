from __future__ import annotations

from pathlib import Path

import pytest

from apps.knowledge.semantic.lint import lint_package, load_coverage
from apps.knowledge.semantic.schema import KnowledgePackageV2


def _package(
    *, metrics: int = 0, serialize: bool = False, repository_revision: str = ""
) -> KnowledgePackageV2:
    processes = [
        {
            "stage_id": "submitted",
            "name": "提交",
            "next_stages": ["approved"] if serialize else [],
        },
        {"stage_id": "approved", "name": "通过"},
    ]
    metrics_bucket = (
        [
            {
                "metric_id": "company-count",
                "name": "企业数",
                "aggregation": "COUNT_DISTINCT",
                "field": {"dataset": "company", "field": "id"},
            }
        ]
        if metrics
        else []
    )
    return KnowledgePackageV2.model_validate(
        {
            "schema_version": "2.0",
            "package": {
                "package_id": "qa-demo",
                "revision": 1,
                "title": "QA demo",
                "namespace": "demo",
                "repository_revision": repository_revision,
            },
            "sources": [{"source_id": "src", "kind": "source_code"}],
            "evidence": [
                {
                    "evidence_id": "ev-status",
                    "source_id": "src",
                    "evidence_kind": "code_path",
                }
            ],
            "knowledge_units": [
                {
                    "unit_id": "onboarding",
                    "revision": 1,
                    "title": "建档",
                    "domain": "enterprise",
                    "description": "企业建档过程。",
                    "content": {
                        "datasets": [
                            {
                                "dataset_id": "company",
                                "name": "cust_company_info",
                                "fields": [
                                    {
                                        "field_id": "id",
                                        "name": "id",
                                        "evidence_refs": ["ev-status"],
                                    }
                                ],
                            }
                        ],
                        "processes": processes,
                        "metrics": metrics_bucket,
                    },
                    "evidence_refs": ["ev-status"],
                }
            ],
        }
    )


def test_coverage_reports_gap_and_auto_covered() -> None:
    # 仓库根解析（pytest 从 backend/ 起跑时 cwd 不是 repo root）
    coverage_path = (
        Path(__file__).resolve().parents[1]
        / "docs/knowledge-extraction/pplatform-web/system-knowledge-v4/coverage.yaml"
    )
    coverage = load_coverage(coverage_path)
    package = _package()
    report = lint_package(package, coverage)
    assert report["coverage"]["total"] == 74
    assert "cust_company_info" in report["coverage"]["covered"]
    assert "cust_shareholder_info" in report["coverage"]["gaps"]
    codes = {issue["code"] for issue in report["issues"]}
    assert "COVERAGE_GAP" in codes


def test_metric_missing_is_advisory() -> None:
    report = lint_package(_package(metrics=0))
    assert any(
        issue["code"] == "METRIC_MISSING"
        for issue in report["issues"]
        if issue["unit"] == "onboarding"
    )
    clean = lint_package(_package(metrics=1))
    assert not any(issue["code"] == "METRIC_MISSING" for issue in clean["issues"])


def test_process_serialization_suppresses_dead_end_warning() -> None:
    unserialized = lint_package(_package(serialize=False))
    assert any(
        issue["code"] == "PROCESS_NOT_SERIALIZED" for issue in unserialized["issues"]
    )
    serialized = lint_package(_package(serialize=True))
    assert not any(
        issue["code"] == "PROCESS_NOT_SERIALIZED" for issue in serialized["issues"]
    )


def _package_inactive(
    *, inactive: bool = True, with_fields: bool = False
) -> KnowledgePackageV2:
    fields = (
        [{"field_id": "id", "name": "id", "evidence_refs": ["ev-schema"]}]
        if with_fields
        else []
    )
    # 纯 inactive 登记单元：六层全空（schema 放行）；活跃单元含 inactive 数据集时保留 processes
    processes = (
        []
        if inactive
        else [{"stage_id": "configure", "name": "配置", "next_stages": []}]
    )
    return KnowledgePackageV2.model_validate(
        {
            "schema_version": "2.0",
            "package": {
                "package_id": "inactive-demo",
                "revision": 1,
                "title": "inactive demo",
                "namespace": "demo",
            },
            "sources": [{"source_id": "src", "kind": "source_code"}],
            "evidence": [
                {
                    "evidence_id": "ev-schema",
                    "source_id": "src",
                    "evidence_kind": "database_schema",
                }
            ],
            "knowledge_units": [
                {
                    "unit_id": "funding-rule",
                    "revision": 1,
                    "title": "资金规则",
                    "domain": "funding",
                    "description": "资金规则。",
                    "content": {
                        "datasets": [
                            {
                                "dataset_id": "funding_party_rule_cfg",
                                "name": "funding_party_rule_cfg",
                                "inactive": inactive,
                                "fields": fields,
                                "evidence_refs": ["ev-schema"],
                            }
                        ],
                        "processes": processes,
                    },
                    "evidence_refs": ["ev-schema"],
                }
            ],
        }
    )


def test_inactive_dataset_skips_orphan_and_flags_fields() -> None:
    clean = lint_package(_package_inactive(inactive=True, with_fields=False))
    clean_codes = {issue["code"] for issue in clean["issues"]}
    assert "FIELD_DECLARATION_ORPHAN" not in clean_codes
    assert "INACTIVE_DATASET_FIELDS" not in clean_codes

    with_fields = lint_package(_package_inactive(inactive=True, with_fields=True))
    with_fields_codes = {issue["code"] for issue in with_fields["issues"]}
    assert "INACTIVE_DATASET_FIELDS" in with_fields_codes
    assert "FIELD_DECLARATION_ORPHAN" not in with_fields_codes


def test_coverage_inactive_cross_check(tmp_path) -> None:
    cov = tmp_path / "coverage.yaml"
    cov.write_text(
        "tables:\n"
        "  - funding_party_rule_cfg\n"
        "inactive:\n"
        "  funding_party_rule_cfg: 无调用链\n",
        encoding="utf-8",
    )
    coverage = load_coverage(cov)
    assert "funding_party_rule_cfg" in coverage["inactive"]

    matched = lint_package(_package_inactive(inactive=True), coverage)
    matched_codes = {issue["code"] for issue in matched["issues"]}
    assert "INACTIVE_FLAG_MISSING" not in matched_codes
    assert "INACTIVE_FLAG_UNLISTED" not in matched_codes

    mismatched = lint_package(_package_inactive(inactive=False), coverage)
    mismatched_codes = {issue["code"] for issue in mismatched["issues"]}
    assert "INACTIVE_FLAG_MISSING" in mismatched_codes


def test_coverage_inactive_excluded_overlap_rejected(tmp_path) -> None:
    cov = tmp_path / "coverage.yaml"
    cov.write_text(
        "tables:\n  - t1\nexcluded:\n  t1: 纯技术\ninactive:\n  t1: 休眠\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_coverage(cov)


def _rel_package(*, cross_unit: bool) -> KnowledgePackageV2:
    def ds(dataset_id: str, name: str, field_id: str) -> dict:
        return {
            "dataset_id": dataset_id,
            "name": name,
            "fields": [
                {"field_id": field_id, "name": field_id, "evidence_refs": ["ev"]}
            ],
        }

    if cross_unit:
        units = [
            {
                "unit_id": "u1",
                "revision": 1,
                "title": "单元一",
                "domain": "d",
                "description": "d",
                "content": {
                    "datasets": [ds("a", "table_a", "id")],
                    "metrics": [
                        {
                            "metric_id": "m1",
                            "name": "计数",
                            "aggregation": "COUNT",
                            "field": {"dataset": "a", "field": "id"},
                        }
                    ],
                },
                "evidence_refs": ["ev"],
            },
            {
                "unit_id": "u2",
                "revision": 1,
                "title": "单元二",
                "domain": "d",
                "description": "d",
                "content": {
                    "datasets": [ds("b", "table_b", "fk")],
                    "metrics": [
                        {
                            "metric_id": "m2",
                            "name": "计数",
                            "aggregation": "COUNT",
                            "field": {"dataset": "b", "field": "fk"},
                        }
                    ],
                },
                "evidence_refs": ["ev"],
            },
        ]
    else:
        units = [
            {
                "unit_id": "u1",
                "revision": 1,
                "title": "单单元",
                "domain": "d",
                "description": "d",
                "content": {
                    "datasets": [ds("a", "table_a", "id"), ds("b", "table_b", "fk")],
                    "metrics": [
                        {
                            "metric_id": "m1",
                            "name": "计数",
                            "aggregation": "COUNT",
                            "field": {"dataset": "a", "field": "id"},
                        }
                    ],
                },
                "evidence_refs": ["ev"],
            }
        ]
    return KnowledgePackageV2.model_validate(
        {
            "schema_version": "2.0",
            "package": {
                "package_id": "rel-demo",
                "revision": 1,
                "title": "rel demo",
                "namespace": "demo",
            },
            "sources": [{"source_id": "src", "kind": "source_code"}],
            "evidence": [
                {"evidence_id": "ev", "source_id": "src", "evidence_kind": "code_path"}
            ],
            "relationships": [
                {
                    "left_table": "table_b",
                    "left_field": "fk",
                    "right_table": "table_a",
                    "right_field": "id",
                    "evidence": "write-flow:X.java:1",
                }
            ],
            "knowledge_units": units,
        }
    )


def test_package_relationship_same_unit_is_flagged() -> None:
    report = lint_package(_rel_package(cross_unit=False))
    assert any(
        issue["code"] == "RELATION_SHOULD_BE_IN_UNIT" for issue in report["issues"]
    )


def test_package_relationship_cross_unit_is_ok() -> None:
    report = lint_package(_rel_package(cross_unit=True))
    assert not any(
        issue["code"] == "RELATION_SHOULD_BE_IN_UNIT" for issue in report["issues"]
    )


def test_baseline_missing_is_advisory() -> None:
    report = lint_package(_package(metrics=1))
    assert any(issue["code"] == "BASELINE_MISSING" for issue in report["issues"])


def test_baseline_present_no_warning() -> None:
    report = lint_package(_package(metrics=1, repository_revision="abc123"))
    assert not any(issue["code"] == "BASELINE_MISSING" for issue in report["issues"])


# ── package.domains 契约：域校准入包 + 域漂移 lint ─────────────────────────────


def _package_with_domains(domains: list[dict], unit_domains: list[str]):
    from apps.knowledge.semantic.lint import lint_package
    from apps.knowledge.semantic.schema import (
        KnowledgePackageV2,
        PackageDomain,
    )

    units = []
    for i, domain in enumerate(unit_domains):
        units.append(
            {
                "unit_id": f"u{i}",
                "title": f"单元{i}",
                "domain": domain,
                "description": "d",
                "content": {
                    "datasets": [{"dataset_id": f"d{i}", "name": f"t{i}"}],
                    "processes": [
                        {
                            "process_id": f"p{i}",
                            "name": f"流程{i}",
                            "stage_id": "s1",
                            "data_effects": [{"operation": "read", "dataset": f"d{i}"}],
                        }
                    ],
                },
            }
        )
    package = KnowledgePackageV2.model_validate(
        {
            "package": {
                "package_id": "p",
                "title": "t",
                "namespace": "n",
                "repository": "r",
                "repository_revision": "abc123",
                "domains": [PackageDomain.model_validate(d) for d in domains],
            },
            "sources": [],
            "evidence": [],
            "knowledge_units": units,
        }
    )
    return lint_package(package)


def test_package_domains_schema_validation() -> None:
    from pydantic import ValidationError

    from apps.knowledge.semantic.schema import PackageDomain

    ok = PackageDomain(name="企业入驻", calibration="added")
    assert ok.calibration == "added"
    split = PackageDomain(
        name="认证管理",
        calibration="split_from",
        split_from="客户管理",
        renamed_from="认证",
    )
    assert split.renamed_from == "认证"

    with pytest.raises(ValidationError):
        PackageDomain(name="x", calibration="split_from")  # 缺父域
    with pytest.raises(ValidationError):
        PackageDomain(name="x", calibration="added", split_from="y")  # split_from 互斥
    with pytest.raises(ValidationError):
        PackageDomain(name="  ")  # 空域名


def test_lint_domain_undeclared_flags_taxonomy_drift() -> None:
    report = _package_with_domains(
        domains=[{"name": "企业入驻", "calibration": "added"}],
        unit_domains=["企业入驻", "未声明域"],
    )
    codes = [(i["code"], i.get("unit")) for i in report["issues"]]
    assert ("DOMAIN_UNDECLARED", "u1") in codes
    assert ("DOMAIN_UNDECLARED", "u0") not in codes


def test_lint_doc_only_domain_with_units_contradicted() -> None:
    report = _package_with_domains(
        domains=[{"name": "死域", "calibration": "doc_only"}],
        unit_domains=["死域"],
    )
    codes = [i["code"] for i in report["issues"]]
    assert "DOMAIN_DOC_ONLY_HAS_UNITS" in codes


def test_lint_domains_clean_when_consistent() -> None:
    report = _package_with_domains(
        domains=[
            {"name": "企业入驻"},
            {"name": "认证管理", "calibration": "split_from", "split_from": "客户管理"},
        ],
        unit_domains=["企业入驻", "认证管理"],
    )
    codes = [i["code"] for i in report["issues"]]
    assert "DOMAIN_UNDECLARED" not in codes
    assert "DOMAIN_DOC_ONLY_HAS_UNITS" not in codes


def test_lint_no_domains_field_is_backward_compatible() -> None:
    """旧包无 package.domains → 域 lint 静默跳过（advisory 不阻断存量）。"""
    report = _package_with_domains(domains=[], unit_domains=["任意域"])
    codes = [i["code"] for i in report["issues"]]
    assert "DOMAIN_UNDECLARED" not in codes
