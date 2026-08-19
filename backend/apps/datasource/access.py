"""Request-scoped datasource access context.

The access scope is resolved once after datasource selection and reused by
knowledge recall, schema rendering, validation, and row-permission rewriting.
It is an application DTO: names and permission tuples only, never ORM instances.
Schema rendering reloads tables in the current Session.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import orjson
from sqlmodel import Session


@dataclass(frozen=True)
class AccessScope:
    resource_names: tuple[str, ...] = ()
    allowed_targets: frozenset[tuple[int, int]] = frozenset()
    row_filters: tuple[dict[str, Any], ...] = ()
    row_restricted_tables: frozenset[str] = frozenset()

    def filters_for(self, resource_names: list[str]) -> list[dict[str, Any]]:
        allowed = set(resource_names)
        return [item for item in self.row_filters if item.get("table") in allowed]


def project_schema_resources(
    resource_names: Sequence[str] | None,
    access_scope: AccessScope | None,
) -> list[str] | None:
    """Return an exact schema projection, or None to rank inside the fence.

    ``resource_names`` is a chosen subset (knowledge binding or a prior plan).
    ``access_scope`` only intersects; it is never itself a projection.
    An empty list means 'nothing visible', not 'fall back to the catalog'.
    """
    if resource_names is None:
        return None
    names = [str(name).strip() for name in resource_names if str(name).strip()]
    if access_scope is None:
        return names
    allowed = set(access_scope.resource_names)
    return [name for name in names if name in allowed]


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
    from apps.datasource.crud.datasource import get_table_obj_by_ds
    from apps.datasource.crud.permission import (
        get_row_permission_filters,
        is_normal_user,
    )
    from apps.datasource.models.datasource import CoreDatasource

    if not isinstance(ds, CoreDatasource):
        return None

    table_objects = tuple(
        get_table_obj_by_ds(
            session=session,
            current_user=current_user,
            ds=ds,
        )
    )
    resource_names = tuple(obj.table.table_name for obj in table_objects)
    allowed_targets = frozenset(
        (int(obj.table.id), int(field.id))
        for obj in table_objects
        for field in (obj.fields or [])
        if obj.table.id is not None and field.id is not None
    )
    row_filters: tuple[dict[str, Any], ...] = ()
    if is_normal_user(current_user) and resource_names:
        row_filters = tuple(
            get_row_permission_filters(
                session=session,
                current_user=current_user,
                ds=ds,
                tables=list(resource_names),
            )
            or []
        )
    return AccessScope(
        resource_names=resource_names,
        allowed_targets=allowed_targets,
        row_filters=row_filters,
        row_restricted_tables=frozenset(
            str(item["table"]) for item in row_filters if item.get("table")
        ),
    )
