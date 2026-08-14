"""Request-scoped datasource access context.

The access scope is resolved once after datasource selection and reused by
knowledge recall, schema rendering, validation, and row-permission rewriting.
It is an application DTO, not a second permission implementation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import orjson
from sqlmodel import Session

from apps.datasource.crud.datasource import get_table_obj_by_ds
from apps.datasource.crud.permission import get_row_permission_filters, is_normal_user
from apps.datasource.models.datasource import CoreDatasource


@dataclass(frozen=True)
class AccessScope:
    table_objects: tuple[Any, ...] = ()
    allowed_targets: frozenset[tuple[int, int]] = frozenset()
    row_filters: tuple[dict[str, Any], ...] = ()
    row_restricted_tables: frozenset[str] = frozenset()

    @property
    def resource_names(self) -> tuple[str, ...]:
        return tuple(obj.table.table_name for obj in self.table_objects)

    def filters_for(self, resource_names: list[str]) -> list[dict[str, Any]]:
        allowed = set(resource_names)
        return [item for item in self.row_filters if item.get("table") in allowed]


def access_scope_fingerprint(scope: AccessScope | None) -> str:
    """Content identity used to fence persisted result replay."""
    if scope is None:
        return hashlib.sha256(b"external-or-unscoped").hexdigest()
    material = {
        "resources": sorted(scope.resource_names),
        "allowed_targets": sorted([list(item) for item in scope.allowed_targets]),
        "row_filters": list(scope.row_filters),
        "row_restricted_tables": sorted(scope.row_restricted_tables),
    }
    return hashlib.sha256(
        orjson.dumps(material, option=orjson.OPT_SORT_KEYS, default=str)
    ).hexdigest()


def resolve_access_scope(
    session: Session,
    *,
    current_user: Any,
    ds: Any,
) -> AccessScope | None:
    """Resolve local catalog visibility and row filters for one chat request."""
    if not isinstance(ds, CoreDatasource):
        return None

    table_objects = tuple(
        get_table_obj_by_ds(
            session=session,
            current_user=current_user,
            ds=ds,
        )
    )
    allowed_targets = frozenset(
        (int(obj.table.id), int(field.id))
        for obj in table_objects
        for field in (obj.fields or [])
        if obj.table.id is not None and field.id is not None
    )
    row_filters: tuple[dict[str, Any], ...] = ()
    if is_normal_user(current_user) and table_objects:
        row_filters = tuple(
            get_row_permission_filters(
                session=session,
                current_user=current_user,
                ds=ds,
                tables=[obj.table.table_name for obj in table_objects],
            )
            or []
        )
    return AccessScope(
        table_objects=table_objects,
        allowed_targets=allowed_targets,
        row_filters=row_filters,
        row_restricted_tables=frozenset(
            str(item["table"]) for item in row_filters if item.get("table")
        ),
    )
