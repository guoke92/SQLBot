"""Protocol-neutral result presentation derived from validated contract facts."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import TypedDict

from apps.chat.query_intent import IntentRevision

_SCHEMA_FIELD_RE = re.compile(
    r"^\s*(?P<bare>[A-Za-z_]\w*:.*)\s*$",
    re.MULTILINE,
)


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
    """Return only unambiguous physical-field comments from prompt schema.

    label 取首个顶层逗号后的**第一段**（到下一个顶层逗号/结尾为止）——
    旧实现把整段 remainder（含 topk=...）当作 label，topk 段会混进前端
    列名；枚举内联后 topk 变长，污染可见。topk 属于值集信息，不属于列名。"""
    candidates: dict[str, set[str]] = {}
    for match in _SCHEMA_FIELD_RE.finditer(schema_text or ""):
        blob = str(match.group("bare") or "")
        name_part, separator, remainder = blob.partition(":")
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
                # label 只取首个顶层逗号后的**第一段**（到下一个顶层逗号/
                # 结尾为止），感知括号深度——comment 自身含括号内逗号时
                # （如 "主键(id, name)"）不被截断；后续段（topk=...）不进列名
                segment: list[str] = []
                inner = 0
                for ch in remainder[index + 1 :]:
                    if ch == "(":
                        inner += 1
                    elif ch == ")":
                        inner -= 1
                    elif ch == "," and inner == 0:
                        break
                    segment.append(ch)
                label = "".join(segment).strip()
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
    intent_revision: IntentRevision | None = None,
    projection_requirements: Mapping[str, Sequence[str]] | None = None,
    schema_text: str = "",
) -> ResultPresentation:
    """Build stable labels from projection lineage, contract and schema.

    Projection lineage is authoritative for SQL aliases. Exact contract
    bindings are the protocol-neutral fallback. Schema comments are used only
    when neither source can establish one unambiguous business meaning.
    """
    requirements = dict(intent_revision.item_catalog) if intent_revision else {}
    lineage = {
        _bare_identifier(field): tuple(keys)
        for field, keys in (projection_requirements or {}).items()
    }
    schema_labels = schema_field_labels(schema_text)

    columns: list[ResultColumnPresentation] = []
    for raw_field in fields:
        field = str(raw_field)
        normalized = _bare_identifier(field)
        contract_label = _unique_label(
            str(requirements[key].get("business_name") or "")
            for key in lineage.get(normalized, ())
            if key in requirements
        )
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
