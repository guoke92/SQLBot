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
    inactive = raw.get("inactive") or {}
    if not isinstance(inactive, dict) or not all(
        isinstance(reason, str) for reason in inactive.values()
    ):
        raise ValueError("coverage `inactive` must be a table-name to reason mapping")
    unknown_inactive = set(inactive) - set(tables)
    if unknown_inactive:
        raise ValueError(
            f"coverage marks unknown tables inactive: {', '.join(sorted(unknown_inactive))}"
        )
    overlap = set(inactive) & set(excluded)
    if overlap:
        raise ValueError(
            "coverage tables cannot be both inactive and excluded: "
            f"{', '.join(sorted(overlap))}"
        )
    return {
        "repository": raw.get("repository", ""),
        "repository_revision": raw.get("repository_revision", ""),
        "tables": list(dict.fromkeys(tables)),
        "excluded": dict(excluded),
        "inactive": dict(inactive),
    }


def _is_inactive_registration(unit: KnowledgeUnitEntry) -> bool:
    """True when a unit is a pure dormant-registration (all datasets inactive)."""
    datasets = unit.content.datasets
    return bool(datasets) and all(dataset.inactive for dataset in datasets)


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
    inactive = set(coverage.get("inactive") or {})
    unit_tables = _dataset_tables(package)
    referenced = {name for names in unit_tables.values() for name in names}

    covered = sorted(referenced & tables)
    undeclared = sorted(referenced - tables)
    gaps = sorted(tables - referenced - excluded)

    flagged = {
        dataset.name.casefold(): dataset.inactive
        for unit in package.knowledge_units
        for dataset in unit.content.datasets
        if dataset.name.strip()
    }

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
    for table in sorted(inactive):
        if table.casefold() in flagged and not flagged[table.casefold()]:
            issues.append(
                {
                    "code": "INACTIVE_FLAG_MISSING",
                    "severity": "advisory",
                    "unit": None,
                    "message": (
                        f"coverage marks table {table!r} inactive but the declaring "
                        "dataset is not flagged inactive: true"
                    ),
                }
            )
    for name, is_inactive in flagged.items():
        if is_inactive and name not in inactive and name in {t.casefold() for t in tables}:
            issues.append(
                {
                    "code": "INACTIVE_FLAG_UNLISTED",
                    "severity": "advisory",
                    "unit": None,
                    "message": (
                        f"dataset {name!r} is flagged inactive: true but coverage.yaml "
                        "does not list it under inactive"
                    ),
                }
            )
    return (
        {
            "total": len(tables),
            "covered": covered,
            "excluded": dict(sorted(coverage["excluded"].items())),
            "inactive": sorted(inactive),
            "gaps": gaps,
            "undeclared": undeclared,
        },
        issues,
    )


def _referenced_field_keys(
    unit: KnowledgeUnitEntry,
    package_relationships: list[Any] | None = None,
) -> set[tuple[str, str]]:
    """Every (dataset_id, field_id) an edge source references.

    In-unit sources are concept/relationship/metric/caliber/rule targets and
    process data_effects. Package-scoped relationships contribute via
    physical endpoint matching (dataset name + field name, casefolded),
    because their endpoints are physical names by contract.
    """
    content = unit.content
    referenced: set[tuple[str, str]] = set()
    for concept in content.concepts:
        for target in concept.field_targets:
            referenced.add((target.dataset, target.field))
    for relationship in content.relationships:
        referenced.add((relationship.left.dataset, relationship.left.field))
        referenced.add((relationship.right.dataset, relationship.right.field))
    for metric in content.metrics:
        if metric.field is not None:
            referenced.add((metric.field.dataset, metric.field.field))
        for grain in metric.grain:
            referenced.add((grain.dataset, grain.field))
    for caliber in content.calibers:
        for target in caliber.field_targets:
            referenced.add((target.dataset, target.field))
    for rule in content.domain_rules:
        for target in rule.field_targets:
            referenced.add((target.dataset, target.field))
    for process in content.processes:
        for effect in process.data_effects:
            for field_name in effect.fields:
                referenced.add((effect.dataset, field_name))
    for relationship in package_relationships or []:
        endpoint_tables = {
            str(relationship.left_table).casefold(),
            str(relationship.right_table).casefold(),
        }
        endpoint_fields = {
            str(relationship.left_field).casefold(),
            str(relationship.right_field).casefold(),
        }
        for dataset in content.datasets:
            if dataset.name.casefold() not in endpoint_tables:
                continue
            for field in dataset.fields:
                if field.name.casefold() in endpoint_fields:
                    referenced.add((dataset.dataset_id, field.field_id))
    return referenced


def _lint_unit(
    unit: KnowledgeUnitEntry,
    package_relationships: list[Any] | None = None,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    content = unit.content

    for concept in content.concepts:
        if not concept.field_targets:
            issues.append(
                {
                    "code": "CONCEPT_UNANCHORED",
                    "severity": "advisory",
                    "unit": unit.unit_id,
                    "message": (
                        f"concept {concept.concept_id} ({concept.name}) has no "
                        "field_targets; anchor it to a declared field so the "
                        "concept_of edge can be generated"
                    ),
                }
            )

    for link in unit.unit_links:
        if not link.evidence_refs:
            issues.append(
                {
                    "code": "UNIT_LINK_UNJUSTIFIED",
                    "severity": "advisory",
                    "unit": unit.unit_id,
                    "message": (
                        f"unit link {link.kind} -> {link.target_unit} has no "
                        "evidence_refs; cross-scenario links require call-chain "
                        "evidence"
                    ),
                }
            )

    referenced_fields = _referenced_field_keys(unit, package_relationships)
    for dataset in content.datasets:
        if dataset.inactive:
            if dataset.fields:
                issues.append(
                    {
                        "code": "INACTIVE_DATASET_FIELDS",
                        "severity": "advisory",
                        "unit": unit.unit_id,
                        "message": (
                            f"inactive dataset {dataset.dataset_id} ({dataset.name}) "
                            "declares fields; dormant tables are table-level only "
                            "(fields: []) — fields stay in the catalog"
                        ),
                    }
                )
            continue
        for field in dataset.fields:
            if (dataset.dataset_id, field.field_id) not in referenced_fields:
                issues.append(
                    {
                        "code": "FIELD_DECLARATION_ORPHAN",
                        "severity": "advisory",
                        "unit": unit.unit_id,
                        "message": (
                            f"declared field {dataset.dataset_id}.{field.field_id} "
                            "is not referenced by any concept/process/relationship/"
                            "caliber/rule/metric; either reference it or drop the "
                            "declaration (declaration-as-edge discipline)"
                        ),
                    }
                )

    if not content.metrics and not _is_inactive_registration(unit):
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


def _lint_package_relationships(
    package: KnowledgePackageV2,
) -> list[dict[str, Any]]:
    """Advisory checks for package-scoped physical relations.

    v4 evidence shows relations legitimately reference endpoints no unit
    declares (minimal field declaration), so closure is advisory here;
    physical existence is enforced at bind time against the live catalog.
    """
    issues: list[dict[str, Any]] = []
    declared_tables: dict[str, set[str]] = {}
    for unit in package.knowledge_units:
        for dataset in unit.content.datasets:
            names = declared_tables.setdefault(dataset.name.casefold(), set())
            names.update(field.name.casefold() for field in dataset.fields)
    for relationship in package.relationships:
        title = f"{relationship.left_table}.{relationship.left_field} -> "
        title += f"{relationship.right_table}.{relationship.right_field}"
        if not relationship.evidence:
            issues.append(
                {
                    "code": "RELATION_UNJUSTIFIED",
                    "severity": "advisory",
                    "unit": None,
                    "message": f"package relationship {title} has no evidence",
                }
            )
        for side, table, field_name in (
            ("left", relationship.left_table, relationship.left_field),
            ("right", relationship.right_table, relationship.right_field),
        ):
            declared = declared_tables.get(table.casefold())
            if declared is None:
                issues.append(
                    {
                        "code": "RELATION_UNDECLARED_ENDPOINT",
                        "severity": "advisory",
                        "unit": None,
                        "message": (
                            f"package relationship {side} table {table!r} is not "
                            "declared by any unit; it will bind as a stub node"
                        ),
                    }
                )
            elif field_name.casefold() not in declared:
                issues.append(
                    {
                        "code": "RELATION_UNDECLARED_ENDPOINT",
                        "severity": "advisory",
                        "unit": None,
                        "message": (
                            f"package relationship {side} field "
                            f"{table}.{field_name} is not declared by any unit; "
                            "it will bind as a stub node"
                        ),
                    }
                )
    return issues


_STRICT_BLOCKING_CODES = {"CONCEPT_UNANCHORED", "FAKE_EXECUTED"}


def lint_package(
    package: KnowledgePackageV2,
    coverage: dict[str, Any] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Return a structured QA report for a validated package.

    When ``strict`` is true, CONCEPT_UNANCHORED and FAKE_EXECUTED are promoted
    from advisory to blocking, so a new extraction fails until every concept
    is anchored and no pattern fakes an execution.
    """
    coverage_report: dict[str, Any] = {}
    issues: list[dict[str, Any]] = []
    if coverage is not None:
        coverage_report, coverage_issues = _lint_coverage(package, coverage)
        issues.extend(coverage_issues)
    issues.extend(_lint_package_relationships(package))

    used_evidence: set[str] = set()
    for unit in package.knowledge_units:
        used_evidence.update(collect_evidence_refs(unit))
        issues.extend(_lint_unit(unit, package.relationships))
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

    if strict:
        for issue in issues:
            if issue["code"] in _STRICT_BLOCKING_CODES:
                issue["severity"] = "blocking"
    blocking = sum(1 for issue in issues if issue["severity"] == "blocking")
    advisory = len(issues) - blocking
    return {
        "coverage": coverage_report,
        "issues": issues,
        "summary": {"blocking": blocking, "advisory": advisory},
    }
