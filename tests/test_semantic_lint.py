from __future__ import annotations

import pytest

from apps.knowledge.semantic.lint import lint_package, load_coverage
from apps.knowledge.semantic.schema import KnowledgePackageV2


def _package(*, metrics: int = 0, serialize: bool = False) -> KnowledgePackageV2:
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
    coverage = load_coverage(
        "docs/knowledge-extraction/pplatform-web/system-knowledge-v4/coverage.yaml"
    )
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


def _package_inactive(*, inactive: bool = True, with_fields: bool = False) -> KnowledgePackageV2:
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
        "tables:\n"
        "  - t1\n"
        "excluded:\n"
        "  t1: 纯技术\n"
        "inactive:\n"
        "  t1: 休眠\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_coverage(cov)
