from __future__ import annotations

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
