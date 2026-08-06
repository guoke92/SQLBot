"""Unit tests for multi-database catalog field lookup used by validate_plan."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.datasource.models.datasource import CoreTable, table_identity_key


def _lookup_fields(
    fields_by_key: dict[tuple[str, str], set[str]],
    table_name: str,
    database_name: str | None,
) -> tuple[str, str] | None:
    """Mirror SqlProtocol.validate_plan identity resolution."""
    db = (database_name or "").strip()
    if db:
        key = (db, table_name)
        return key if key in fields_by_key else None
    matches = [k for k in fields_by_key if k[1] == table_name]
    if len(matches) == 1:
        return matches[0]
    return None


def test_same_table_name_in_two_databases_stays_separate() -> None:
    stg = CoreTable(table_name="orders", database_name="stg")
    ods = CoreTable(table_name="orders", database_name="ods")
    fields_by_key = {
        table_identity_key(stg): {"stg_only", "id"},
        table_identity_key(ods): {"ods_only", "id"},
    }

    stg_key = _lookup_fields(fields_by_key, "orders", "stg")
    ods_key = _lookup_fields(fields_by_key, "orders", "ods")
    assert stg_key == ("stg", "orders")
    assert ods_key == ("ods", "orders")
    assert "stg_only" in fields_by_key[stg_key]
    assert "stg_only" not in fields_by_key[ods_key]


def test_ambiguous_bare_name_skips_lookup() -> None:
    fields_by_key = {
        ("stg", "orders"): {"a"},
        ("ods", "orders"): {"b"},
    }
    assert _lookup_fields(fields_by_key, "orders", None) is None


def test_unique_bare_name_resolves_without_database() -> None:
    fields_by_key = {("stg", "orders"): {"a"}}
    assert _lookup_fields(fields_by_key, "orders", None) == ("stg", "orders")
