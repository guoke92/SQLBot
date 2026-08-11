"""Single validation entry point for QuerySpecification."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict

from apps.chat.query_specification import QuerySpecification, requirement_fields

_TABLE_RE = re.compile(r"^#\s*Table:\s*([^,;\s]+)", re.MULTILINE)
_FIELD_RE = re.compile(r"^\s*\(([^:(),\s]+)\s*:", re.MULTILINE)


class SpecificationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    code: str
    severity: Literal["blocking", "advisory"]
    requirement_ids: tuple[str, ...] = ()
    detail: str = ""
    fields: tuple[str, ...] = ()


def _schema_catalog(schema_text: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    matches = list(_TABLE_RE.finditer(schema_text or ""))
    for index, match in enumerate(matches):
        table = match.group(1).strip().strip('`"[]').casefold()
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(schema_text)
        )
        fields = {
            item.group(1).strip().strip('`"[]').casefold()
            for item in _FIELD_RE.finditer(schema_text[match.end() : end])
        }
        result[table] = fields
        result.setdefault(table.rsplit(".", 1)[-1], fields)
    return result


def validate_specification(
    specification: QuerySpecification,
    *,
    schema_text: str = "",
    available_evidence_refs: set[str] | None = None,
) -> list[SpecificationIssue]:
    issues: list[SpecificationIssue] = []
    if available_evidence_refs is not None:
        referenced = set(specification.evidence_refs)
        for requirement in specification.requirements:
            referenced.update(requirement.evidence_refs)
        for assumption in specification.assumptions:
            referenced.update(assumption.evidence_refs)
        unknown_refs = referenced - available_evidence_refs
        if unknown_refs:
            issues.append(
                SpecificationIssue(
                    code="unknown_evidence_reference",
                    severity="blocking",
                    detail="Specification cites evidence outside the immutable ledger",
                    fields=tuple(sorted(unknown_refs)),
                )
            )
    catalog = _schema_catalog(schema_text)
    if not catalog:
        issues.append(
            SpecificationIssue(
                code="schema_catalog_unavailable",
                severity="advisory",
                detail="Retrieved schema cannot be structurally verified",
            )
        )
    else:
        all_fields = set().union(*catalog.values()) if catalog else set()
        for requirement in specification.requirements:
            unknown: list[str] = []
            for field in requirement_fields(requirement):
                if field.semantic_ref and not field.field:
                    continue
                if field.resource:
                    table_fields = catalog.get(
                        field.resource.casefold()
                    ) or catalog.get(field.resource_name.casefold())
                    if table_fields is None:
                        unknown.append(field.identifier)
                    elif field.field.casefold() not in table_fields:
                        unknown.append(field.identifier)
                elif field.field.casefold() not in all_fields:
                    unknown.append(field.identifier)
            if unknown:
                issues.append(
                    SpecificationIssue(
                        code="field_not_in_schema",
                        # A physical identifier is either present or invented;
                        # uncertain mappings must remain semantic_ref until the
                        # planner can ground them or ask a business question.
                        severity="blocking",
                        requirement_ids=(requirement.requirement_id,),
                        fields=tuple(dict.fromkeys(unknown)),
                    )
                )

    if specification.limit is not None and specification.limit <= 0:
        issues.append(SpecificationIssue(code="invalid_limit", severity="blocking"))
    return issues


def blocking_issues(issues: list[SpecificationIssue]) -> list[SpecificationIssue]:
    return [issue for issue in issues if issue.severity == "blocking"]


def validate_specification_transition(
    previous: QuerySpecification | None,
    current: QuerySpecification,
    *,
    active_evidence_refs: set[str],
) -> list[SpecificationIssue]:
    """Protect still-effective user-confirmed clauses across revisions.

    Stable requirement IDs encode clause semantics. A newer revision may
    replace model inferences freely, but it cannot silently remove or rewrite
    a user clause while the cited user evidence remains effective. A genuine
    correction first supersedes that evidence in the ledger.
    """
    if previous is None:
        return []
    current_ids = set(current.by_requirement_id())
    issues: list[SpecificationIssue] = []
    for requirement in previous.requirements:
        cited_user_evidence = {
            ref
            for ref in requirement.evidence_refs
            if ref == "user:question" or ref.startswith("user:answer:")
        }
        if not (cited_user_evidence & active_evidence_refs):
            continue
        if requirement.requirement_id not in current_ids:
            issues.append(
                SpecificationIssue(
                    code="confirmed_requirement_changed_without_correction",
                    severity="blocking",
                    requirement_ids=(requirement.requirement_id,),
                    detail=requirement.business_label,
                )
            )
    return issues
