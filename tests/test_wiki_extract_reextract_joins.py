"""Unit tests for JOIN re-extraction (same-name nomination)."""

from __future__ import annotations

from pathlib import Path

from tools.wiki_extract.reextract_joins import (
    FieldInfo,
    propose_pairs,
)


def test_same_name_menu_id_nominated() -> None:
    fields = {
        "tenant_product_menu": [
            FieldInfo("tenant_product_menu", "id", joinable=False, drop_reason="generic"),
            FieldInfo(
                "tenant_product_menu",
                "menu_id",
                tags=["same_name_priority", "suffix_key"],
            ),
            FieldInfo(
                "tenant_product_menu",
                "product_code",
                tags=["same_name_priority", "suffix_key"],
            ),
        ],
        "tenant_product_menu_res": [
            FieldInfo(
                "tenant_product_menu_res", "id", joinable=False, drop_reason="generic"
            ),
            FieldInfo(
                "tenant_product_menu_res",
                "menu_id",
                tags=["same_name_priority", "suffix_key"],
            ),
            FieldInfo(
                "tenant_product_menu_res",
                "product_code",
                tags=["same_name_priority", "suffix_key"],
            ),
        ],
    }
    # Mark joinable
    for flist in fields.values():
        for f in flist:
            if f.column in {"menu_id", "product_code"}:
                f.joinable = True

    cands = propose_pairs(fields, removed=set(), existing=set())
    pairs = {(c.left, c.right) for c in cands}
    # either orientation after norm preference
    assert any(
        {a, b}
        == {
            "tenant_product_menu.menu_id",
            "tenant_product_menu_res.menu_id",
        }
        for a, b in pairs
    ), pairs
    # Must NOT nominate menu.id → res.menu_id
    assert ("tenant_product_menu.id", "tenant_product_menu_res.menu_id") not in pairs


def test_removed_pair_excluded(tmp_path: Path) -> None:
    fields = {
        "tenant_product_menu": [
            FieldInfo("tenant_product_menu", "menu_id", joinable=True, tags=["same_name_priority"]),
        ],
        "tenant_product_menu_res": [
            FieldInfo(
                "tenant_product_menu_res",
                "menu_id",
                joinable=True,
                tags=["same_name_priority"],
            ),
        ],
    }
    removed = {
        tuple(
            sorted(
                [
                    "tenant_product_menu.menu_id",
                    "tenant_product_menu_res.menu_id",
                ]
            )
        )
    }
    cands = propose_pairs(fields, removed=removed, existing=set())
    assert cands == []
