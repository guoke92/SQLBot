"""StarRocks / Doris catalog + database scope helpers.

External catalogs (e.g. Hive via ``hive_emr.stg``) cannot be passed as a single
MySQL-protocol database name. Scope is always ``(catalog, databases)`` where
``catalog`` may be empty for internal / default_catalog tables.

Ownership:
- Config normalize (doris/starrocks only): ``sync_conf_scope`` via SqlProtocol
- Runtime resolve (all SR call sites): ``resolve_sr_scope`` / ``connect_database_arg``
- SQL identifiers: ``qualified_table`` / ``quote_ident`` / SHOW helpers
- Table identity in local catalog: ``apps.datasource.models.datasource.table_identity_key``
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from apps.datasource.models.datasource import DatasourceConf


def quote_ident(name: str) -> str:
    """Backtick-quote one StarRocks / MySQL identifier segment."""
    cleaned = (name or "").replace("`", "")
    return f"`{cleaned}`"


def split_legacy_database(value: str) -> tuple[str, str] | None:
    """Split ``catalog.database`` when it is a single-dot legacy database field.

    Returns ``(catalog, database)`` or ``None`` if the value is not a legacy pair.
    """
    raw = (value or "").strip()
    if not raw or raw.count(".") != 1:
        return None
    catalog, database = raw.split(".", 1)
    catalog = catalog.strip()
    database = database.strip()
    if not catalog or not database:
        return None
    if any(ch in catalog or ch in database for ch in ("`", "/", "\\", " ")):
        return None
    return catalog, database


def _normalize_databases(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        return parts
    if isinstance(raw, Sequence) and not isinstance(raw, (bytes, bytearray)):
        out: list[str] = []
        for item in raw:
            text = str(item or "").strip()
            if text and text not in out:
                out.append(text)
        return out
    text = str(raw).strip()
    return [text] if text else []


def resolve_sr_scope(conf: DatasourceConf | Any) -> tuple[str, list[str]]:
    """Return ``(catalog, databases)`` after applying legacy dotted-database split."""
    catalog = (getattr(conf, "catalog", None) or "").strip()
    databases = _normalize_databases(getattr(conf, "databases", None))
    database = (getattr(conf, "database", None) or "").strip()

    if not databases and database:
        legacy = split_legacy_database(database)
        if legacy is not None:
            legacy_catalog, legacy_db = legacy
            if not catalog:
                catalog = legacy_catalog
            databases = [legacy_db]
        else:
            databases = [database]

    return catalog, databases


def sync_conf_scope(conf: DatasourceConf | Any) -> Any:
    """Normalize catalog/databases/database fields in-place and return conf."""
    catalog, databases = resolve_sr_scope(conf)
    conf.catalog = catalog
    conf.databases = list(databases)
    if databases:
        conf.database = databases[0]
    elif getattr(conf, "database", None) and split_legacy_database(conf.database):
        conf.database = ""
    return conf


def connect_database_arg(conf: DatasourceConf | Any) -> str | None:
    """Value for pymysql ``db=`` — never a dotted ``catalog.database``."""
    catalog, databases = resolve_sr_scope(conf)
    if catalog:
        return None
    return databases[0] if databases else None


def bare_table_name(table_name: str | None) -> str:
    """Strip whitespace and backticks from a table identifier (no dotted parsing)."""
    return (table_name or "").strip().strip("`")


def table_label(catalog: str, database: str, table: str) -> str:
    """Unquoted dotted name for prompts / UI (same segments as ``qualified_table``)."""
    parts: list[str] = []
    if catalog:
        parts.append(catalog)
    if database:
        parts.append(database)
    if table:
        parts.append(table)
    return ".".join(parts)


def qualified_table(
    catalog: str,
    database: str,
    table: str,
    *,
    include_catalog: bool = True,
) -> str:
    """Build a quoted table reference."""
    parts: list[str] = []
    if include_catalog and catalog:
        parts.append(quote_ident(catalog))
    if database:
        parts.append(quote_ident(database))
    parts.append(quote_ident(table))
    return ".".join(parts)


def show_tables_sql(catalog: str, database: str) -> str:
    """SHOW TABLES for an external catalog database (not used for internal DBs)."""
    return f"SHOW TABLES FROM {quote_ident(catalog)}.{quote_ident(database)}"


def show_full_columns_sql(catalog: str, database: str, table: str) -> str:
    return f"SHOW FULL COLUMNS FROM {qualified_table(catalog, database, table)}"


def show_databases_sql(catalog: str) -> str:
    if catalog:
        return f"SHOW DATABASES FROM {quote_ident(catalog)}"
    return "SHOW DATABASES"


def set_catalog_sql(catalog: str) -> str:
    return f"SET CATALOG {quote_ident(catalog)}"


def use_database_sql(database: str) -> str:
    return f"USE {quote_ident(database)}"
