"""Unit tests for multi-database catalog field lookup used by validate_plan."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.datasource.models.datasource import (
    CoreTable,
    resolve_catalog_table,
    table_identity_key,
)


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


def test_resolve_catalog_table_prefers_database_then_unique_bare() -> None:
    stg = CoreTable(id=1, table_name="orders", database_name="stg")
    ods = CoreTable(id=2, table_name="orders", database_name="ods")
    users = CoreTable(id=3, table_name="users", database_name="stg")
    tables = [stg, ods, users]

    assert resolve_catalog_table(tables, "orders", database_name="ods") is ods
    assert resolve_catalog_table(tables, "orders", database_name=None) is None
    assert resolve_catalog_table(tables, "users", database_name=None) is users


def test_dictionary_fingerprint_includes_database_name() -> None:
    from apps.dictionary.catalog import schema_fingerprint

    field = type("F", (), {"field_name": "id", "field_type": "bigint"})()
    a = schema_fingerprint(CoreTable(table_name="orders", database_name="stg"), field)
    b = schema_fingerprint(CoreTable(table_name="orders", database_name="ods"), field)
    assert a != b


def test_starrocks_internal_stats_route_in_source() -> None:
    """Avoid importing catalog_stats (pulls db/pandas); lock the routing contract in source."""
    text = (_BACKEND / "apps/datasource/crud/catalog_stats.py").read_text(encoding="utf-8")
    assert "equals_ignore_case(t, \"doris\", \"starrocks\")" in text
    assert "skip catalog stats for external catalog" in text
    assert "return _mysql_stats(ds, tables)" in text
    # Internal path must not unconditionally return {} after the catalog check.
    doris_block = text.split('equals_ignore_case(t, "doris", "starrocks")', 1)[1].split(
        'equals_ignore_case(t, "mysql"', 1
    )[0]
    assert "return _mysql_stats" in doris_block
    assert doris_block.count("return {}") == 1  # external catalog only
