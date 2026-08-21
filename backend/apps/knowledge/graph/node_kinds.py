"""Single registry for node-kind -> slot / bucket / id-field / text-field.

This is the one place that names a node kind's runtime slot, composition
bucket, unit-local id field, and indexable text fields.  Changing a name here
updates decompose, governance and recall together instead of drifting across
three hard-coded dicts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NodeKindSpec:
    slot: str
    id_field: str | None
    text_fields: tuple[str, ...]
    bucket: str | None = None


NODE_KINDS: dict[str, NodeKindSpec] = {
    "dataset": NodeKindSpec(
        slot="datasets", id_field="dataset_id", text_fields=("name", "description")
    ),
    "field": NodeKindSpec(
        slot="fields", id_field="field_id", text_fields=("name", "description")
    ),
    "concept": NodeKindSpec(
        slot="concepts",
        bucket="concepts",
        id_field="concept_id",
        text_fields=("name", "definition"),
    ),
    "stage": NodeKindSpec(
        slot="scenarios",
        bucket="processes",
        id_field="stage_id",
        text_fields=("name", "trigger", "description"),
    ),
    "caliber": NodeKindSpec(
        slot="calibers",
        bucket="calibers",
        id_field="caliber_id",
        text_fields=("label", "description"),
    ),
    "rule": NodeKindSpec(
        slot="rules",
        bucket="domain_rules",
        id_field="rule_id",
        text_fields=("label", "content"),
    ),
    "metric": NodeKindSpec(
        slot="metrics",
        bucket="metrics",
        id_field="metric_id",
        text_fields=("name", "description"),
    ),
    "pattern": NodeKindSpec(
        slot="verified_examples",
        bucket="verified_query_patterns",
        id_field="pattern_id",
        text_fields=("question",),
    ),
    "relation": NodeKindSpec(slot="relationships", id_field=None, text_fields=()),
}


def slot_for_kind(kind: str) -> str | None:
    entry = NODE_KINDS.get(kind)
    return entry.slot if entry is not None else None


def id_field_for_kind(kind: str) -> str | None:
    entry = NODE_KINDS.get(kind)
    return entry.id_field if entry is not None else None


def text_fields_for_kind(kind: str) -> tuple[str, ...]:
    entry = NODE_KINDS.get(kind)
    return entry.text_fields if entry is not None else ()


# bucket -> id-field, derived once and shared by decompose + governance.
BUCKET_ID_FIELDS: dict[str, str] = {}
for _spec in NODE_KINDS.values():
    if _spec.bucket is not None and _spec.id_field is not None:
        BUCKET_ID_FIELDS[_spec.bucket] = _spec.id_field
