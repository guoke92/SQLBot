"""Protocol-neutral result presentation derived from validated contract facts."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import TypedDict

from apps.chat.query_contract import QueryContract

_SCHEMA_FIELD_RE = re.compile(r"^\s*\((?P<body>.*)\),?\s*$", re.MULTILINE)


class ResultColumnPresentation(TypedDict):
    field: str
    label: str
    display: str


class ResultPresentation(TypedDict):
    title: str
    columns: list[ResultColumnPresentation]


def _bare_identifier(value: str) -> str:
    return value.rsplit(".", 1)[-1].strip().strip('`"[]').casefold()


def schema_field_labels(schema_text: str) -> dict[str, str]:
    """Return only unambiguous physical-field comments from prompt schema."""
    candidates: dict[str, set[str]] = {}
    for match in _SCHEMA_FIELD_RE.finditer(schema_text or ""):
        name_part, separator, remainder = str(match.group("body") or "").partition(":")
        if not separator:
            continue
        depth = 0
        label = ""
        for index, char in enumerate(remainder):
            if char == "(":
                depth += 1
            elif char == ")" and depth:
                depth -= 1
            elif char == "," and depth == 0:
                label = remainder[index + 1 :].strip()
                break
        name = _bare_identifier(name_part)
        if name and label:
            candidates.setdefault(name, set()).add(label)
    return {
        name: next(iter(labels))
        for name, labels in candidates.items()
        if len(labels) == 1
    }


def _unique_label(labels: Iterable[str]) -> str:
    values = {str(label).strip() for label in labels if str(label).strip()}
    return next(iter(values)) if len(values) == 1 else ""


def build_result_presentation(
    fields: Iterable[str],
    *,
    title: str = "",
    contract: QueryContract | None = None,
    projection_requirements: Mapping[str, Sequence[str]] | None = None,
    schema_text: str = "",
) -> ResultPresentation:
    """Build stable labels from projection lineage, contract and schema.

    Projection lineage is authoritative for SQL aliases. Exact contract
    bindings are the protocol-neutral fallback. Schema comments are used only
    when neither source can establish one unambiguous business meaning.
    """
    requirements = {
        requirement.key: requirement
        for requirement in (contract.requirements if contract else ())
    }
    lineage = {
        _bare_identifier(field): tuple(keys)
        for field, keys in (projection_requirements or {}).items()
    }
    exact_labels: dict[str, set[str]] = {}
    for requirement in requirements.values():
        for binding in requirement.bindings_for("group", "measure", "attribute"):
            exact_labels.setdefault(_bare_identifier(binding.identifier), set()).add(
                requirement.label
            )
    schema_labels = schema_field_labels(schema_text)

    columns: list[ResultColumnPresentation] = []
    for raw_field in fields:
        field = str(raw_field)
        normalized = _bare_identifier(field)
        contract_label = _unique_label(
            requirements[key].label
            for key in lineage.get(normalized, ())
            if key in requirements
        ) or _unique_label(exact_labels.get(normalized, ()))
        label = contract_label or schema_labels.get(normalized, "")
        display = (
            f"{label}({field})"
            if label and label.casefold() != field.casefold()
            else field
        )
        columns.append({"field": field, "label": label, "display": display})
    return {"title": title or "", "columns": columns}


def chart_columns(presentation: ResultPresentation) -> list[dict[str, str]]:
    """Adapt canonical presentation columns to the existing chart contract."""
    return [
        {"name": column["display"], "value": column["field"]}
        for column in presentation["columns"]
    ]
