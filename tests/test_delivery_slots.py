"""Delivery-slot projection: same card replaces, distinct cards stay."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.delivery import delivery_slot_key, select_delivery_datasets
from apps.chat.graphs.nodes.agent_finalize import (
    select_delivery_datasets as reexported,
)


def _ds(**kwargs: object) -> SimpleNamespace:
    payload = {
        "dataset_id": "x",
        "required": True,
        "status": "succeeded",
        "row_count": 1,
        "fields": [],
        "schema_snapshot": {},
    }
    payload.update(kwargs)
    return SimpleNamespace(**payload)


def test_finalize_reexports_delivery_select() -> None:
    assert reexported is select_delivery_datasets


def test_probes_and_failures_never_publish() -> None:
    probe = _ds(dataset_id="p", required=False, row_count=9)
    failed = _ds(dataset_id="f", status="failed", row_count=4)
    ok = _ds(dataset_id="a", row_count=3)
    assert select_delivery_datasets([probe, failed, ok]) == [ok]
    assert select_delivery_datasets([probe]) == []


def test_same_title_later_success_replaces() -> None:
    first = _ds(
        dataset_id="a",
        schema_snapshot={"result_title": "  结果卡  "},
        row_count=1000,
    )
    second = _ds(
        dataset_id="b",
        schema_snapshot={"result_title": "结果卡"},
        row_count=1000,
    )
    assert delivery_slot_key(first) == delivery_slot_key(second)
    picked = select_delivery_datasets([first, second])
    assert [item.dataset_id for item in picked] == ["b"]


def test_distinct_titles_all_stay_in_first_seen_order() -> None:
    left = _ds(dataset_id="a", schema_snapshot={"result_title": "卡甲"}, row_count=10)
    right = _ds(dataset_id="b", schema_snapshot={"result_title": "卡乙"}, row_count=8)
    picked = select_delivery_datasets([left, right])
    assert [item.dataset_id for item in picked] == ["a", "b"]


def test_untitled_same_fields_replace() -> None:
    first = _ds(dataset_id="a", fields=["id", "name"], row_count=10)
    second = _ds(dataset_id="b", fields=["name", "id"], row_count=8)
    picked = select_delivery_datasets([first, second])
    assert [item.dataset_id for item in picked] == ["b"]


def test_untitled_different_fields_are_distinct_slots() -> None:
    first = _ds(dataset_id="a", fields=["id"], row_count=10)
    second = _ds(dataset_id="b", fields=["city"], row_count=8)
    picked = select_delivery_datasets([first, second])
    assert [item.dataset_id for item in picked] == ["a", "b"]


def test_untitled_empty_fields_share_one_slot() -> None:
    first = _ds(dataset_id="a", fields=[], row_count=10)
    second = _ds(dataset_id="b", fields=[], row_count=8)
    picked = select_delivery_datasets([first, second])
    assert [item.dataset_id for item in picked] == ["b"]


def test_zero_row_revision_can_replace_populated_slot() -> None:
    first = _ds(
        dataset_id="a",
        schema_snapshot={"result_title": "卡"},
        row_count=12,
    )
    empty = _ds(
        dataset_id="b",
        schema_snapshot={"result_title": "卡"},
        row_count=0,
        rows=[],
    )
    picked = select_delivery_datasets([first, empty])
    assert [item.dataset_id for item in picked] == ["b"]
