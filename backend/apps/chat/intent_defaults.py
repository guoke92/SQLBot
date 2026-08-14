"""Typed, certified business defaults applied before plan validation.

Defaults are reusable business clauses, not user evidence and not physical
field mappings. They may fill a missing clause, but an explicit clause with
the same business name always wins.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from apps.chat.query_intent import (
    IntentDataset,
    IntentFilter,
    IntentGrouping,
    IntentOrder,
    IntentOutput,
    IntentTime,
    QueryIntent,
)


class IntentDefaultItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset_subject: str
    kind: Literal["output", "group", "filter", "time", "order"]
    value: dict[str, Any]


class IntentDefaultFragment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[1] = 1
    intent_defaults: tuple[IntentDefaultItem, ...] = Field(min_length=1)


_ITEM_ADAPTERS = {
    "output": TypeAdapter(IntentOutput),
    "group": TypeAdapter(IntentGrouping),
    "filter": TypeAdapter(IntentFilter),
    "time": TypeAdapter(IntentTime),
    "order": TypeAdapter(IntentOrder),
}


def parse_intent_default_fragment(fragment: dict[str, Any]) -> IntentDefaultFragment:
    parsed = IntentDefaultFragment.model_validate(fragment)
    for item in parsed.intent_defaults:
        _ITEM_ADAPTERS[item.kind].validate_python(item.value)
    return parsed


def apply_intent_defaults(
    intent: QueryIntent,
    fragments: list[dict[str, Any]],
) -> tuple[QueryIntent, list[int]]:
    """Fill absent clauses deterministically; never replace an intent clause."""
    datasets = list(intent.datasets)
    applied_assets: list[int] = []
    for wrapped in fragments:
        asset_id = int(wrapped.get("asset_id") or 0)
        fragment = parse_intent_default_fragment(dict(wrapped.get("fragment") or {}))
        fragment_applied = False
        for default in fragment.intent_defaults:
            for index, dataset in enumerate(datasets):
                if (
                    default.dataset_subject.strip().casefold()
                    != dataset.subject.casefold()
                ):
                    continue
                updated, applied = _apply_item(dataset, default)
                if applied:
                    datasets[index] = updated
                    fragment_applied = True
        if fragment_applied and asset_id:
            applied_assets.append(asset_id)
    return intent.model_copy(update={"datasets": tuple(datasets)}), applied_assets


def _apply_item(
    dataset: IntentDataset,
    default: IntentDefaultItem,
) -> tuple[IntentDataset, bool]:
    value = _ITEM_ADAPTERS[default.kind].validate_python(default.value)
    if default.kind == "time":
        if dataset.time is not None:
            return dataset, False
        return dataset.model_copy(update={"time": value}), True
    attr = {
        "output": "outputs",
        "group": "groupings",
        "filter": "filters",
        "order": "ordering",
    }[default.kind]
    existing = tuple(getattr(dataset, attr))
    business_name = str(getattr(value, "business_name", "")).casefold()
    if any(
        str(getattr(item, "business_name", "")).casefold() == business_name
        for item in existing
    ):
        return dataset, False
    return dataset.model_copy(update={attr: (*existing, value)}), True
