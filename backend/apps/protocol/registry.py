"""Type -> protocol registry.

Persistent identity is only `CoreDatasource.type` (mysql, pg, api, ...).
Dialect details stay inside SqlProtocol. No family layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set, Type

from apps.protocol.base import BaseProtocol


ProtocolFactory = Callable[[str], BaseProtocol]


@dataclass(frozen=True)
class ConnectorSpec:
    """Registration metadata for one datasource type key."""

    type_key: str
    display_name: str
    protocol_factory: ProtocolFactory
    # Optional UI grouping only — never used for runtime branching.
    category: str = "database"
    capabilities: Set[str] = field(default_factory=set)
    # SQL-only: template / quote helpers (ignored by non-SQL).
    quote_prefix: str = '"'
    quote_suffix: str = '"'
    template_name: str = ""
    sqlglot_dialect: Optional[str] = None
    illegal_params: tuple[str, ...] = ()


_REGISTRY: Dict[str, ConnectorSpec] = {}
_BOOTSTRAPPED = False


def register_type(spec: ConnectorSpec) -> ConnectorSpec:
    key = spec.type_key.lower()
    _REGISTRY[key] = spec
    return spec


def get_spec(type_key: str) -> ConnectorSpec:
    _ensure_bootstrap()
    key = (type_key or "").lower()
    if key not in _REGISTRY:
        raise ValueError(f"Unsupported datasource type: {type_key}")
    return _REGISTRY[key]


def get_protocol(type_key: str) -> BaseProtocol:
    spec = get_spec(type_key)
    protocol = spec.protocol_factory(spec.type_key)
    protocol.type_key = spec.type_key
    protocol.capabilities = set(spec.capabilities)
    return protocol


def get_protocol_for_ds(ds: Any) -> BaseProtocol:
    type_key = getattr(ds, "type", None)
    if not type_key:
        raise ValueError("Datasource has no type")
    return get_protocol(str(type_key))


def list_types(category: Optional[str] = None) -> list[ConnectorSpec]:
    _ensure_bootstrap()
    specs = list(_REGISTRY.values())
    if category:
        specs = [s for s in specs if s.category == category]
    return specs


def _sql_factory(type_key: str) -> BaseProtocol:
    from apps.protocol.sql.protocol import SqlProtocol

    return SqlProtocol(type_key)


def _rest_factory(type_key: str) -> BaseProtocol:
    from apps.protocol.rest.protocol import RestProtocol

    return RestProtocol(type_key)


def _ensure_bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    bootstrap_default_types()
    _BOOTSTRAPPED = True


def bootstrap_default_types() -> None:
    """Register built-in SQL types + api. Idempotent."""
    from apps.protocol.base import (
        CAP_CONF_OWNED_RESOURCES,
        CAP_OPENAPI_IMPORT,
        CAP_ROW_PERMISSION,
        CAP_SAMPLE_DATA,
        CAP_SQL_DIALECT,
        CAP_TABLE_RELATION,
    )

    sql_caps = {CAP_SQL_DIALECT, CAP_ROW_PERMISSION, CAP_SAMPLE_DATA, CAP_TABLE_RELATION}

    sql_types = [
        # type_key, display, template, prefix, suffix, sqlglot, illegal, category
        ("excel", "Excel/CSV", "PostgreSQL", '"', '"', None, (), "file"),
        ("redshift", "AWS Redshift", "AWS_Redshift", '"', '"', None, (), "database"),
        ("ck", "ClickHouse", "ClickHouse", '"', '"', None, (), "database"),
        ("dm", "达梦", "DM", '"', '"', None, (), "database"),
        ("doris", "Apache Doris", "Doris", "`", "`", "mysql", (), "database"),
        ("es", "Elasticsearch", "Elasticsearch", '"', '"', None, (), "database"),
        ("kingbase", "Kingbase", "Kingbase", '"', '"', None, (), "database"),
        ("sqlServer", "Microsoft SQL Server", "Microsoft_SQL_Server", "[", "]", "tsql", (), "database"),
        ("mysql", "MySQL", "MySQL", "`", "`", "mysql", ("local_infile",), "database"),
        ("oracle", "Oracle", "Oracle", '"', '"', None, (), "database"),
        ("pg", "PostgreSQL", "PostgreSQL", '"', '"', None, (), "database"),
        ("starrocks", "StarRocks", "StarRocks", "`", "`", "mysql", (), "database"),
        ("hive", "Apache Hive", "Hive", "`", "`", "hive", (), "database"),
    ]

    for type_key, display, template, prefix, suffix, dialect, illegal, category in sql_types:
        register_type(
            ConnectorSpec(
                type_key=type_key,
                display_name=display,
                protocol_factory=_sql_factory,
                category=category,
                capabilities=set(sql_caps),
                quote_prefix=prefix,
                quote_suffix=suffix,
                template_name=template,
                sqlglot_dialect=dialect,
                illegal_params=illegal,
            )
        )

    register_type(
        ConnectorSpec(
            type_key="api",
            display_name="API",
            protocol_factory=_rest_factory,
            category="api",
            capabilities={CAP_OPENAPI_IMPORT, CAP_CONF_OWNED_RESOURCES},
            template_name="API",
        )
    )


# Convenience re-export type for static checkers
ProtocolClass = Type[BaseProtocol]
