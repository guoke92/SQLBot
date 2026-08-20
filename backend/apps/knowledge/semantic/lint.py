"""Extraction QA for KnowledgePackage 2.0.

This is a review aid, not a second schema or a runtime gate. It reuses the
sole semantic contract (:class:`KnowledgePackageV2`) and adds completeness /
quality checks the structural validator deliberately does not enforce, because
a package can be structurally valid while still covering only a fraction of
the source system or carrying no reusable measures.

The only extra authoring input is an optional ``coverage.yaml`` inventory that
lists every physical table in scope. Coverage is computed (not declared) by
matching each unit's ``dataset.name`` against that inventory, so a table can
never drift into "covered" without actually appearing in a unit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apps.knowledge.semantic.schema import (
    KnowledgePackageV2,
    KnowledgeUnitEntry,
    collect_evidence_refs,
)

_COVERAGE_NAMES = {"coverage.yaml", "coverage.yml"}

_EXECUTED_STATUSES = {"executed", "passed"}
_EXECUTION_PROOF_KEYS = {"execution_proof", "executed_at", "result", "rows"}


def load_coverage(path: str | Path) -> dict[str, Any]:
    """Load a coverage inventory from disk and normalize it.

    Accepted shape::

        schema_version: '1.0'
        repository: pplatform-web
        repository_revision: ee434954e
        tables:
          - cust_company_info
          - cust_build_record
        excluded:
          argeement_migratory_record: 迁移日志，无问数场景
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("coverage manifest root must be an object")
    tables = raw.get("tables")
    if not isinstance(tables, list) or not all(
        isinstance(name, str) and name.strip() for name in tables
    ):
        raise ValueError("coverage `tables` must be a non-empty list of table names")
    excluded = raw.get("excluded") or {}
    if not isinstance(excluded, dict) or not all(
        isinstance(reason, str) for reason in excluded.values()
    ):
        raise ValueError("coverage `excluded` must be a table-name to reason mapping")
    unknown = set(excluded) - set(tables)
    if unknown:
        raise ValueError(
            f"coverage excludes unknown tables: {', '.join(sorted(unknown))}"
        )
    return {
        "repository": raw.get("repository", ""),
        "repository_revision": raw.get("repository_revision", ""),
        "tables": list(dict.fromkeys(tables)),
        "excluded": dict(excluded),
    }


def _dataset_tables(package: KnowledgePackageV2) -> dict[str, set[str]]:
    """Map every unit to the physical table names it declares as datasets."""
    result: dict[str, set[str]] = {}
    for unit in package.knowledge_units:
        names = {
            dataset.name for dataset in unit.content.datasets if dataset.name.strip()
        }
        result[unit.unit_id] = names
    return result


def _lint_coverage(
    package: KnowledgePackageV2, coverage: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    tables = set(coverage["tables"])
    excluded = set(coverage["excluded"])
    unit_tables = _dataset_tables(package)
    referenced = {name for names in unit_tables.values() for name in names}

    covered = sorted(referenced & tables)
    undeclared = sorted(referenced - tables)
    gaps = sorted(tables - referenced - excluded)

    issues: list[dict[str, Any]] = []
    for table in gaps:
        issues.append(
            {
                "code": "COVERAGE_GAP",
                "severity": "blocking",
                "unit": None,
                "message": f"physical table {table!r} has no covering knowledge unit",
            }
        )
    for table in undeclared:
        owners = sorted(
            unit_id for unit_id, names in unit_tables.items() if table in names
        )
        issues.append(
            {
                "code": "UNDECLARED_DATASET",
                "severity": "advisory",
                "unit": owners[0] if len(owners) == 1 else None,
                "message": (
                    f"unit dataset {table!r} is not in the coverage inventory; "
                    f"update coverage.yaml or fix the table name ({', '.join(owners)})"
                ),
            }
        )
    return (
        {
            "total": len(tables),
            "covered": covered,
            "excluded": dict(sorted(coverage["excluded"].items())),
            "gaps": gaps,
            "undeclared": undeclared,
        },
        issues,
    )


def _lint_unit(unit: KnowledgeUnitEntry) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    content = unit.content

    if not content.metrics:
        issues.append(
            {
                "code": "METRIC_MISSING",
                "severity": "advisory",
                "unit": unit.unit_id,
                "message": (
                    "no reusable metrics; extract aggregation + grain so questions "
                    "like 'X 有多少' map to a measure instead of a one-off query"
                ),
            }
        )

    for relation in content.relationships:
        if not relation.evidence_refs:
            issues.append(
                {
                    "code": "RELATION_UNJUSTIFIED",
                    "severity": "advisory",
                    "unit": unit.unit_id,
                    "message": (
                        f"relationship {relation.relationship_id} "
                        f"({relation.left.dataset}.{relation.left.field} -> "
                        f"{relation.right.dataset}.{relation.right.field}) has no evidence"
                    ),
                }
            )

    stages = {stage.stage_id for stage in content.processes}
    if len(stages) > 1 and not any(stage.next_stages for stage in content.processes):
        issues.append(
            {
                "code": "PROCESS_NOT_SERIALIZED",
                "severity": "advisory",
                "unit": unit.unit_id,
                "message": (
                    "process has multiple stages but no next_stages chain; "
                    "verify whether stages are sequential or independent"
                ),
            }
        )
    for stage in content.processes:
        unknown = sorted(set(stage.next_stages) - stages)
        if unknown:
            issues.append(
                {
                    "code": "PROCESS_NOT_SERIALIZED",
                    "severity": "advisory",
                    "unit": unit.unit_id,
                    "message": (
                        f"stage {stage.stage_id} references unknown next_stages: "
                        f"{', '.join(unknown)}"
                    ),
                }
            )

    for pattern in content.verified_query_patterns:
        verification = pattern.verification or {}
        status = verification.get("status")
        if status in _EXECUTED_STATUSES and not any(
            verification.get(key) for key in _EXECUTION_PROOF_KEYS
        ):
            issues.append(
                {
                    "code": "FAKE_EXECUTED",
                    "severity": "advisory",
                    "unit": unit.unit_id,
                    "message": (
                        f"pattern {pattern.pattern_id} claims {status!r} without "
                        "execution proof (execution_proof/executed_at/result/rows)"
                    ),
                }
            )

    return issues


def lint_package(
    package: KnowledgePackageV2,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured QA report for a validated package."""
    coverage_report: dict[str, Any] = {}
    issues: list[dict[str, Any]] = []
    if coverage is not None:
        coverage_report, coverage_issues = _lint_coverage(package, coverage)
        issues.extend(coverage_issues)

    used_evidence: set[str] = set()
    for unit in package.knowledge_units:
        used_evidence.update(collect_evidence_refs(unit))
        issues.extend(_lint_unit(unit))
    for evidence in package.evidence:
        if evidence.evidence_id not in used_evidence:
            issues.append(
                {
                    "code": "DOC_UNDERUSED",
                    "severity": "advisory",
                    "unit": None,
                    "message": (
                        f"evidence {evidence.evidence_id} is not cited by any unit"
                    ),
                }
            )

    blocking = sum(1 for issue in issues if issue["severity"] == "blocking")
    advisory = len(issues) - blocking
    return {
        "coverage": coverage_report,
        "issues": issues,
        "summary": {"blocking": blocking, "advisory": advisory},
    }
