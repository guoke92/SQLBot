"""StarRocks external catalog scope helpers and config normalization."""

from __future__ import annotations

from apps.datasource.models.datasource import CoreTable, DatasourceConf, table_identity_key
from apps.db.starrocks_catalog import (
    bare_table_name,
    connect_database_arg,
    qualified_table,
    resolve_sr_scope,
    show_full_columns_sql,
    show_tables_sql,
    split_legacy_database,
    sync_conf_scope,
)
from apps.protocol import get_protocol


def test_split_legacy_database() -> None:
    assert split_legacy_database("hive_emr.stg") == ("hive_emr", "stg")
    assert split_legacy_database("stg") is None
    assert split_legacy_database("a.b.c") is None


def test_resolve_splits_dotted_database_without_mutating_generic_conf() -> None:
    """Scope sync is SR-owned; bare DatasourceConf does not auto-mutate."""
    conf = DatasourceConf(
        host="h",
        port=9030,
        username="u",
        password="p",
        database="hive_emr.stg",
    )
    assert conf.catalog == ""
    assert conf.databases == []
    catalog, databases = resolve_sr_scope(conf)
    assert catalog == "hive_emr"
    assert databases == ["stg"]
    assert connect_database_arg(conf) is None

    sync_conf_scope(conf)
    assert conf.catalog == "hive_emr"
    assert conf.databases == ["stg"]
    assert conf.database == "stg"


def test_datasource_conf_multi_databases() -> None:
    conf = DatasourceConf(
        host="h",
        port=9030,
        username="u",
        password="p",
        catalog="hive_emr",
        databases=["stg", "ods"],
    )
    catalog, databases = resolve_sr_scope(conf)
    assert catalog == "hive_emr"
    assert databases == ["stg", "ods"]
    sync_conf_scope(conf)
    assert conf.database == "stg"
    assert connect_database_arg(conf) is None


def test_internal_starrocks_still_passes_database() -> None:
    conf = DatasourceConf(
        host="h",
        port=9030,
        username="u",
        password="p",
        database="analytics",
    )
    assert connect_database_arg(conf) == "analytics"
    sync_conf_scope(conf)
    assert conf.catalog == ""
    assert conf.databases == ["analytics"]
    assert connect_database_arg(conf) == "analytics"


def test_mysql_normalize_does_not_force_databases() -> None:
    proto = get_protocol("mysql")
    out = proto.normalize_configuration(
        {
            "host": "h",
            "port": 3306,
            "username": "u",
            "password": "p",
            "database": "app",
        }
    )
    assert out["database"] == "app"
    assert out.get("databases") in ([], None) or out["databases"] == []
    assert out.get("catalog", "") == ""


def test_qualified_sql_helpers() -> None:
    assert show_tables_sql("hive_emr", "stg") == "SHOW TABLES FROM `hive_emr`.`stg`"
    assert (
        show_full_columns_sql("hive_emr", "stg", "t1")
        == "SHOW FULL COLUMNS FROM `hive_emr`.`stg`.`t1`"
    )
    assert qualified_table("hive_emr", "stg", "t1") == "`hive_emr`.`stg`.`t1`"
    assert bare_table_name("`t1`") == "t1"
    from apps.db.starrocks_catalog import table_label

    assert table_label("hive_emr", "stg", "t1") == "hive_emr.stg.t1"
    assert table_label("", "stg", "t1") == "stg.t1"


def test_normalize_configuration_accepts_catalog_fields() -> None:
    proto = get_protocol("starrocks")
    out = proto.normalize_configuration(
        {
            "host": "emr-starrocks.example",
            "port": 9030,
            "username": "read_hive",
            "password": "secret",
            "catalog": "hive_emr",
            "databases": ["stg"],
        }
    )
    assert out["catalog"] == "hive_emr"
    assert out["databases"] == ["stg"]
    assert out["database"] == "stg"


def test_normalize_legacy_dotted_database() -> None:
    proto = get_protocol("starrocks")
    out = proto.normalize_configuration(
        {
            "host": "h",
            "port": 9030,
            "username": "u",
            "password": "p",
            "database": "hive_emr.stg",
        }
    )
    assert out["catalog"] == "hive_emr"
    assert out["databases"] == ["stg"]
    assert out["database"] == "stg"


def test_table_identity_key() -> None:
    a = CoreTable(table_name="orders", database_name="stg")
    b = CoreTable(table_name="orders", database_name="ods")
    assert table_identity_key(a) == ("stg", "orders")
    assert table_identity_key(b) == ("ods", "orders")
    assert table_identity_key(a) != table_identity_key(b)


def test_metadata_path_selection_helpers() -> None:
    """Document the catalog vs internal metadata branch predicate."""
    external = DatasourceConf(catalog="hive_emr", databases=["stg"], database="stg")
    catalog, databases = resolve_sr_scope(external)
    assert catalog and databases  # → SHOW TABLES path

    internal = DatasourceConf(database="analytics")
    catalog, databases = resolve_sr_scope(internal)
    assert not catalog and databases == ["analytics"]  # → information_schema path
