"""The single contract validation entry point.

Every contract rule lives here exactly once and always yields
``ContractIssue``.  Callers decide how to consume the result — clarify, drop
the inference, retry generation — but they never re-implement a rule and never
invent a different consequence for it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from apps.chat.contract.issues import ContractIssue, IssueSeverity
from apps.chat.query_contract import (
    ContractRequirement,
    GroupRequirement,
    OutputRequirement,
    QueryContract,
    requirement_fields,
    requirement_resources,
)

_TABLE_HEADER_RE = re.compile(r"^#\s*Table:\s*([^,;\s]+)", re.MULTILINE)
_FIELD_LINE_RE = re.compile(r"^\s*\(([^:(),\s]+)\s*:", re.MULTILINE)
_LIST_SEPARATOR = ", "


def _parse_schema_catalog(schema_text: str) -> dict[str, set[str]]:
    """Parse the prompt schema block into a resource -> field-name catalog."""
    result: dict[str, set[str]] = {}
    matches = list(_TABLE_HEADER_RE.finditer(schema_text or ""))
    for index, match in enumerate(matches):
        table = match.group(1).strip().strip('`"[]').casefold()
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(schema_text)
        )
        block = schema_text[match.end() : end]
        fields = {
            field.group(1).strip().strip('`"[]').casefold()
            for field in _FIELD_LINE_RE.finditer(block)
        }
        result[table] = fields
        result.setdefault(table.rsplit(".", 1)[-1], fields)
    return result


def _severity_for(requirements: Iterable[ContractRequirement]) -> IssueSeverity:
    """Confirmed clauses block; pure inferences degrade to a stated assumption."""
    return (
        "blocking"
        if any(requirement.is_confirmed for requirement in requirements)
        else "advisory"
    )


def _resource_components(
    resources: set[str], requirements: Sequence[ContractRequirement]
) -> list[set[str]]:
    """Partition result resources by the relations that connect them.

    Ordering is stable so that the reported blame — and therefore the issue's
    severity — never depends on set iteration order.
    """
    from apps.chat.query_contract import RelationRequirement

    adjacency: dict[str, set[str]] = {resource: set() for resource in resources}
    for requirement in requirements:
        if not isinstance(requirement, RelationRequirement):
            continue
        for pair in requirement.pairs:
            left = pair.left.resource_name.casefold()
            right = pair.right.resource_name.casefold()
            if not left or not right or left == right:
                continue
            adjacency.setdefault(left, set()).add(right)
            adjacency.setdefault(right, set()).add(left)

    components: list[set[str]] = []
    seen: set[str] = set()
    for start in sorted(resources):
        if start in seen:
            continue
        pending = [start]
        reached: set[str] = set()
        while pending:
            current = pending.pop()
            if current in reached:
                continue
            reached.add(current)
            pending.extend(adjacency.get(current, set()) - reached)
        seen |= reached
        components.append(reached & resources)
    return components


def relation_coverage_issues(
    requirements: Sequence[ContractRequirement],
    *,
    additional_group_resources: Iterable[str] = (),
    additional_output_resources: Iterable[str] = (),
) -> list[ContractIssue]:
    """Report result grains that span business ranges with no stated mapping.

    Independent scalar outputs may still be emitted as separate plans.  Once a
    shared result grain exists, an output from another resource cannot be
    interpreted without both a physical relation and a business population.
    """
    group_resources = {
        resource
        for requirement in requirements
        if isinstance(requirement, GroupRequirement)
        for resource in requirement_resources(requirement)
    } | {resource.casefold() for resource in additional_group_resources if resource}
    output_resources = {
        resource
        for requirement in requirements
        if isinstance(requirement, OutputRequirement)
        for resource in requirement_resources(requirement)
    } | {resource.casefold() for resource in additional_output_resources if resource}
    result_resources = group_resources | output_resources
    if not group_resources or len(result_resources) <= 1:
        return []
    components = _resource_components(result_resources, requirements)
    if len(components) <= 1:
        return []

    grain_clauses = [
        requirement
        for requirement in requirements
        if isinstance(requirement, (GroupRequirement, OutputRequirement))
    ]
    per_component = [
        [
            requirement
            for requirement in grain_clauses
            if requirement_resources(requirement) & component
        ]
        for component in components
    ]
    anchored = [
        index
        for index, clauses in enumerate(per_component)
        if any(requirement.is_confirmed for requirement in clauses)
    ]
    if len(anchored) > 1:
        # The user confirmed clauses on both sides, so which entities to keep
        # is a business decision only they can make.
        return [
            ContractIssue(
                code="relation_coverage_missing",
                severity="blocking",
                slot_ids=tuple(requirement.slot_id for requirement in grain_clauses),
                resources=tuple(sorted(result_resources)),
            )
        ]
    keep = anchored[0] if anchored else 0
    stranded = [
        requirement
        for index, clauses in enumerate(per_component)
        if index != keep
        for requirement in clauses
    ]
    return [
        ContractIssue(
            code="relation_coverage_missing",
            severity=_severity_for(stranded),
            slot_ids=tuple(requirement.slot_id for requirement in stranded),
            resources=tuple(sorted(result_resources)),
        )
    ]


def field_reference_issues(
    requirements: Sequence[ContractRequirement],
    schema_text: str,
) -> list[ContractIssue]:
    """Report clauses pointing at fields the retrieved schema does not expose."""
    catalog = _parse_schema_catalog(schema_text)
    if not catalog:
        # Proceeding unverified is still the best available behaviour, but it
        # must be visible instead of silently skipped.
        return [ContractIssue(code="schema_catalog_unavailable", severity="advisory")]
    all_fields: set[str] = set().union(*catalog.values())
    issues: list[ContractIssue] = []
    for requirement in requirements:
        if isinstance(requirement, OutputRequirement) and requirement.operation in {
            "ratio",
            "difference",
        }:
            continue
        unknown: list[str] = []
        unretrieved: list[str] = []
        for field in requirement_fields(requirement):
            if field.resource:
                known_fields = catalog.get(
                    field.resource.casefold(),
                    catalog.get(field.resource_name.casefold()),
                )
                if known_fields is None:
                    # The resource was not part of this turn's retrieval, so
                    # the clause is unverifiable rather than wrong. Treating it
                    # as wrong would break every follow-up whose earlier table
                    # dropped out of the top-k schema.
                    unretrieved.append(field.identifier)
                    continue
                known = field.field.casefold() in known_fields
            else:
                known = field.field.casefold() in all_fields
            if not known:
                unknown.append(field.identifier)
        if unknown:
            issues.append(
                ContractIssue(
                    code="field_not_in_schema",
                    severity=_severity_for([requirement]),
                    slot_ids=(requirement.slot_id,),
                    params={
                        "label": requirement.label,
                        "fields": _LIST_SEPARATOR.join(dict.fromkeys(unknown)),
                    },
                )
            )
        if unretrieved:
            issues.append(
                ContractIssue(
                    code="resource_not_retrieved",
                    severity="advisory",
                    slot_ids=(requirement.slot_id,),
                    resources=tuple(
                        dict.fromkeys(
                            field.resource_name
                            for field in requirement_fields(requirement)
                            if field.resource_name
                        )
                    ),
                    params={"label": requirement.label},
                )
            )
    return issues


def validate_contract(
    contract: QueryContract,
    *,
    schema_text: str | None = None,
) -> list[ContractIssue]:
    """Return every expected issue of one frozen contract.

    ``schema_text`` is optional because field existence can only be judged
    against a retrieval that the caller may not have.
    """
    issues = list(relation_coverage_issues(contract.requirements))
    if schema_text is not None:
        issues.extend(field_reference_issues(contract.requirements, schema_text))
    return issues
