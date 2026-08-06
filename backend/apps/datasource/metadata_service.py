"""Application services for datasource metadata configuration."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlmodel import Session

from apps.datasource.crud.datasource import chooseTables, get_ds
from apps.datasource.crud.table import get_tables_by_ds_id
from apps.datasource.models.datasource import CoreField, CoreTable, TableObj, table_identity_key
from common.utils.embedding_threads import (
    run_save_ds_embeddings,
    run_save_table_embeddings,
)


def update_table_projection(
    session: Session,
    *,
    trans: Any,
    ds_id: int,
    tables: Sequence[CoreTable],
    mode: str,
) -> list[CoreTable]:
    """Apply add/remove/set semantics, then use the canonical full-set sync."""
    normalized = mode.strip().lower()
    if normalized not in {"add", "remove", "set"}:
        raise ValueError('mode must be "add", "remove", or "set"')
    if get_ds(session, ds_id) is None:
        raise ValueError("Datasource not found")

    current = get_tables_by_ds_id(session, ds_id)
    if normalized == "set":
        full = list(tables)
    elif normalized == "add":
        by_key = {
            table_identity_key(table): CoreTable(
                table_name=str(table.table_name).strip(),
                database_name=getattr(table, "database_name", None) or None,
                table_comment=table.table_comment or table.custom_comment or "",
            )
            for table in current
            if str(table.table_name or "").strip()
        }
        for table in tables:
            name = str(table.table_name or "").strip()
            if not name:
                continue
            key = table_identity_key(table)
            existing = by_key.get(key)
            by_key[key] = CoreTable(
                table_name=name,
                database_name=getattr(table, "database_name", None)
                or (existing.database_name if existing is not None else None),
                table_comment=table.table_comment
                or (existing.table_comment if existing is not None else "")
                or "",
            )
        full = list(by_key.values())
    else:
        removed = {
            table_identity_key(table)
            for table in tables
            if str(table.table_name or "").strip()
        }
        full = [
            CoreTable(
                table_name=table.table_name,
                database_name=getattr(table, "database_name", None) or None,
                table_comment=table.table_comment or table.custom_comment or "",
            )
            for table in current
            if table_identity_key(table) not in removed
        ]

    chooseTables(session, trans, ds_id, full)
    return get_tables_by_ds_id(session, ds_id)


def update_table_metadata(
    session: Session,
    *,
    table_id: int,
    checked: bool | None = None,
    custom_comment: str | None = None,
) -> CoreTable:
    """Update table metadata through the canonical embedding-aware write path."""
    table = session.get(CoreTable, table_id)
    if table is None:
        raise ValueError(f"Table {table_id} not found")
    if checked is not None:
        table.checked = checked
    if custom_comment is not None:
        table.custom_comment = custom_comment
    session.add(table)
    session.commit()
    run_save_table_embeddings([table_id])
    run_save_ds_embeddings([int(table.ds_id)])
    refreshed = session.get(CoreTable, table_id)
    if refreshed is None:  # pragma: no cover - guarded by the initial lookup
        raise RuntimeError(f"Table {table_id} disappeared after update")
    return refreshed


def update_field_metadata(
    session: Session,
    *,
    field_id: int,
    checked: bool | None = None,
    custom_comment: str | None = None,
) -> CoreField:
    """Update field metadata through the canonical embedding-aware write path."""
    field = session.get(CoreField, field_id)
    if field is None:
        raise ValueError(f"Field {field_id} not found")
    if checked is not None:
        field.checked = checked
    if custom_comment is not None:
        field.custom_comment = custom_comment
    session.add(field)
    session.commit()
    run_save_table_embeddings([int(field.table_id)])
    run_save_ds_embeddings([int(field.ds_id)])
    refreshed = session.get(CoreField, field_id)
    if refreshed is None:  # pragma: no cover - guarded by the initial lookup
        raise RuntimeError(f"Field {field_id} disappeared after update")
    return refreshed


def update_table_and_fields_metadata(session: Session, data: TableObj) -> None:
    """Persist a table and its field comments with one embedding refresh."""
    if data.table is None or data.table.id is None:
        raise ValueError("Table metadata is required")
    table = session.get(CoreTable, int(data.table.id))
    if table is None:
        raise ValueError(f"Table {data.table.id} not found")

    fields: list[tuple[CoreField, CoreField]] = []
    for incoming in data.fields:
        if incoming.id is None:
            raise ValueError("Field metadata id is required")
        field = session.get(CoreField, int(incoming.id))
        if (
            field is None
            or int(field.table_id) != int(table.id)
            or int(field.ds_id) != int(table.ds_id)
        ):
            raise ValueError(f"Field {incoming.id} does not belong to table {table.id}")
        fields.append((field, incoming))

    table.checked = data.table.checked
    table.custom_comment = data.table.custom_comment
    session.add(table)
    for field, incoming in fields:
        field.checked = incoming.checked
        field.custom_comment = incoming.custom_comment
        session.add(field)
    session.commit()
    run_save_table_embeddings([int(table.id)])
    run_save_ds_embeddings([int(table.ds_id)])
