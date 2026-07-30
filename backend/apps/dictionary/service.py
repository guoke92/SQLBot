"""Dictionary configuration and snapshot publication services."""

from __future__ import annotations

import datetime
from collections.abc import Iterable, Sequence

from fastapi import HTTPException
from sqlalchemy import and_, delete
from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.dictionary.catalog import is_string_field_type, schema_fingerprint
from apps.dictionary.matching import normalize_dictionary_value
from apps.dictionary.models import (
    DictionaryConfigCreate,
    DictionaryConfigUpdate,
    DictionaryFieldConfig,
    DictionaryFieldOptionRead,
    DictionaryRefreshResult,
    DictionaryStatus,
    DictionaryValue,
)
from apps.protocol.base import CAP_DICTIONARY_VALUES
from apps.protocol.registry import get_protocol_for_ds


def _now() -> datetime.datetime:
    return datetime.datetime.now()


def reconcile_configs(
    session: Session,
    tables: Sequence[CoreTable],
) -> None:
    """Keep explicitly configured fields consistent with the current catalog."""
    table_ids = [table.id for table in tables if table.id is not None]
    if not table_ids:
        return
    fields = session.exec(
        select(CoreField).where(CoreField.table_id.in_(table_ids))
    ).all()
    fields_by_id = {field.id: field for field in fields}
    table_by_id = {table.id: table for table in tables}
    configs = session.exec(
        select(DictionaryFieldConfig).where(
            DictionaryFieldConfig.table_id.in_(table_ids)
        )
    ).all()
    now = _now()

    for config in configs:
        field = fields_by_id.get(config.field_id)
        if field is None:
            continue
        table = table_by_id.get(field.table_id)
        if table is None:
            continue
        fingerprint = schema_fingerprint(table, field)
        previous = (
            config.enabled,
            config.status,
            config.schema_fingerprint,
        )
        if not is_string_field_type(field.field_type or ""):
            config.enabled = False
            config.status = DictionaryStatus.DISABLED
        elif not config.enabled:
            config.status = DictionaryStatus.DISABLED
        elif config.schema_fingerprint != fingerprint:
            config.status = (
                DictionaryStatus.STALE
                if config.published_generation
                else DictionaryStatus.EMPTY
            )
        config.schema_fingerprint = fingerprint
        current = (
            config.enabled,
            config.status,
            config.schema_fingerprint,
        )
        if current != previous:
            config.revision = int(config.revision or 0) + 1
            config.update_time = now
            session.add(config)


def create_manual_config(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    data: DictionaryConfigCreate,
) -> DictionaryFieldConfig:
    field = session.get(CoreField, data.field_id)
    if field is None or field.ds_id != ds_id:
        raise HTTPException(status_code=404, detail="Datasource field not found")
    if not is_string_field_type(field.field_type or ""):
        raise HTTPException(
            status_code=400,
            detail="Only string fields can be configured as dictionary fields",
        )
    table = session.get(CoreTable, field.table_id)
    ds = session.get(CoreDatasource, ds_id)
    if (
        table is None
        or table.id is None
        or field.id is None
        or ds is None
        or int(ds.oid or 1) != int(oid)
    ):
        raise HTTPException(status_code=404, detail="Datasource field not found")
    protocol = get_protocol_for_ds(ds)
    if not protocol.supports(CAP_DICTIONARY_VALUES):
        raise HTTPException(
            status_code=400, detail="Datasource does not support dictionary values"
        )
    existing = session.exec(
        select(DictionaryFieldConfig).where(
            and_(
                DictionaryFieldConfig.oid == oid,
                DictionaryFieldConfig.ds_id == ds_id,
                DictionaryFieldConfig.field_id == data.field_id,
            )
        )
    ).first()
    now = _now()
    if existing is not None:
        existing.enabled = data.enabled
        existing.max_values = data.max_values
        existing.schema_fingerprint = schema_fingerprint(table, field)
        existing.status = (
            DictionaryStatus.DISABLED
            if not data.enabled
            else DictionaryStatus.STALE
            if existing.published_generation
            else DictionaryStatus.EMPTY
        )
        existing.revision = int(existing.revision or 0) + 1
        existing.update_time = now
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    config = DictionaryFieldConfig(
        oid=oid,
        ds_id=ds_id,
        table_id=int(table.id),
        field_id=int(field.id),
        enabled=data.enabled,
        max_values=data.max_values,
        schema_fingerprint=schema_fingerprint(table, field),
        status=DictionaryStatus.EMPTY if data.enabled else DictionaryStatus.DISABLED,
        published_generation=0,
        revision=0,
        value_count=0,
        create_time=now,
        update_time=now,
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


def update_config(
    session: Session,
    *,
    oid: int,
    config_id: int,
    data: DictionaryConfigUpdate,
) -> DictionaryFieldConfig:
    config = session.get(DictionaryFieldConfig, config_id)
    if config is None or config.oid != oid:
        raise HTTPException(status_code=404, detail="Dictionary config not found")
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(config, key, value)
    if not config.enabled:
        config.status = DictionaryStatus.DISABLED
    elif "max_values" in updates and config.published_generation:
        config.status = DictionaryStatus.STALE
    elif config.status == DictionaryStatus.DISABLED:
        config.status = (
            DictionaryStatus.STALE
            if config.published_generation
            else DictionaryStatus.EMPTY
        )
    if updates:
        config.revision = int(config.revision or 0) + 1
        config.update_time = _now()
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


def list_field_options(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    table_id: int | None = None,
) -> list[DictionaryFieldOptionRead]:
    ds = session.get(CoreDatasource, ds_id)
    if ds is None or int(ds.oid or 1) != oid:
        raise HTTPException(status_code=404, detail="Datasource not found")
    if not get_protocol_for_ds(ds).supports(CAP_DICTIONARY_VALUES):
        return []
    statement = (
        select(CoreTable, CoreField)
        .join(CoreField, CoreField.table_id == CoreTable.id)
        .where(CoreTable.ds_id == ds_id)
        .order_by(CoreTable.table_name, CoreField.field_index)
    )
    if table_id is not None:
        statement = statement.where(CoreTable.id == table_id)
    rows = session.exec(statement).all()
    eligible = [
        (table, field)
        for table, field in rows
        if is_string_field_type(field.field_type or "")
    ]
    field_ids = [int(field.id) for _, field in eligible if field.id is not None]
    configs = (
        session.exec(
            select(DictionaryFieldConfig).where(
                and_(
                    DictionaryFieldConfig.oid == oid,
                    DictionaryFieldConfig.ds_id == ds_id,
                    DictionaryFieldConfig.field_id.in_(field_ids),
                )
            )
        ).all()
        if field_ids
        else []
    )
    by_field = {config.field_id: config for config in configs}
    result: list[DictionaryFieldOptionRead] = []
    for table, field in eligible:
        if table.id is None or field.id is None:
            continue
        config = by_field.get(field.id)
        state = (
            config.model_dump()
            if config is not None
            else {
                "id": None,
                "ds_id": ds_id,
                "table_id": int(table.id),
                "field_id": int(field.id),
                "enabled": False,
                "max_values": 500,
                "status": DictionaryStatus.DISABLED,
                "published_generation": 0,
                "value_count": 0,
                "last_synced_at": None,
                "last_error": None,
            }
        )
        result.append(
            DictionaryFieldOptionRead.model_validate(
                {
                    **state,
                    "configured": config is not None,
                    "table_name": table.table_name,
                    "table_comment": table.custom_comment or table.table_comment,
                    "field_name": field.field_name,
                    "field_type": field.field_type,
                    "field_comment": field.custom_comment or field.field_comment,
                }
            )
        )
    return result


def get_field_option(
    session: Session,
    *,
    oid: int,
    config_id: int,
) -> DictionaryFieldOptionRead:
    row = session.exec(
        select(DictionaryFieldConfig, CoreTable, CoreField)
        .join(CoreTable, CoreTable.id == DictionaryFieldConfig.table_id)
        .join(CoreField, CoreField.id == DictionaryFieldConfig.field_id)
        .where(
            and_(
                DictionaryFieldConfig.id == config_id,
                DictionaryFieldConfig.oid == oid,
            )
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Dictionary config not found")
    config, table, field = row
    return DictionaryFieldOptionRead.model_validate(
        {
            **config.model_dump(),
            "configured": True,
            "table_name": table.table_name,
            "table_comment": table.custom_comment or table.table_comment,
            "field_name": field.field_name,
            "field_type": field.field_type,
            "field_comment": field.custom_comment or field.field_comment,
        }
    )


def refresh_config(
    session: Session,
    *,
    oid: int,
    config_id: int,
) -> DictionaryFieldConfig:
    """Extract externally, then atomically publish a new local generation."""
    config = session.get(DictionaryFieldConfig, config_id)
    if config is None or config.oid != oid:
        raise HTTPException(status_code=404, detail="Dictionary config not found")
    if not config.enabled:
        raise HTTPException(status_code=400, detail="Dictionary config is disabled")
    ds = session.get(CoreDatasource, config.ds_id)
    table = session.get(CoreTable, config.table_id)
    field = session.get(CoreField, config.field_id)
    if ds is None or table is None or field is None:
        raise HTTPException(
            status_code=409, detail="Dictionary catalog target no longer exists"
        )
    fingerprint = schema_fingerprint(table, field)
    if fingerprint != config.schema_fingerprint:
        config.schema_fingerprint = fingerprint
        config.status = (
            DictionaryStatus.STALE
            if config.published_generation
            else DictionaryStatus.EMPTY
        )
        config.revision = int(config.revision or 0) + 1
        config.update_time = _now()
        session.add(config)
        session.commit()

    protocol = get_protocol_for_ds(ds)
    if not protocol.supports(CAP_DICTIONARY_VALUES):
        raise HTTPException(
            status_code=400, detail="Datasource does not support dictionary values"
        )

    resource_name = table.table_name
    field_name = field.field_name
    max_values = config.max_values
    start_revision = int(config.revision or 0)
    # End the catalog-read transaction before the potentially slow remote
    # DISTINCT query. The detached datasource is a fully-loaded connection DTO.
    session.expunge(ds)
    session.rollback()
    try:
        extracted = protocol.extract_dictionary_values(
            ds,
            resource=resource_name,
            field=field_name,
            limit=max_values,
        )
        if extracted.truncated:
            raise ValueError(
                f"Distinct values exceed configured maximum ({max_values}); "
                "increase the limit or disable this dictionary field"
            )
        normalized: dict[str, str] = {}
        for value in extracted.values:
            key = normalize_dictionary_value(value)
            if key:
                normalized.setdefault(key, value.strip())
        # Serialize only the short local publication phase. The remote query
        # above never holds an AI智能问数 database lock.
        config = session.exec(
            select(DictionaryFieldConfig)
            .where(DictionaryFieldConfig.id == config_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).one()
        if not config.enabled:
            raise ValueError("Dictionary config was disabled during refresh")
        if config.schema_fingerprint != fingerprint:
            raise ValueError(
                "Dictionary field schema changed during refresh; retry with the latest catalog"
            )
        if int(config.revision or 0) != start_revision:
            raise ValueError(
                "Dictionary config changed during refresh; retry with the latest config"
            )
        generation = int(config.published_generation or 0) + 1
        now = _now()
        for key, value in normalized.items():
            session.add(
                DictionaryValue(
                    config_id=int(config.id),
                    value=value,
                    normalized_value=key,
                    generation=generation,
                    create_time=now,
                )
            )
        session.flush()
        session.exec(
            delete(DictionaryValue).where(
                and_(
                    DictionaryValue.config_id == config.id,
                    DictionaryValue.generation != generation,
                )
            )
        )
        config.published_generation = generation
        config.revision = start_revision + 1
        config.value_count = len(normalized)
        config.status = DictionaryStatus.READY
        config.last_synced_at = now
        config.last_error = None
        config.update_time = now
        session.add(config)
        session.commit()
        session.refresh(config)
        return config
    except Exception as exc:
        session.rollback()
        current = session.get(DictionaryFieldConfig, config_id)
        if (
            current is not None
            and int(current.revision or 0) == start_revision
        ):
            current.status = (
                DictionaryStatus.DISABLED
                if not current.enabled
                else DictionaryStatus.STALE
                if current.published_generation
                else DictionaryStatus.EMPTY
            )
            current.last_error = str(exc)[:2000]
            current.revision = start_revision + 1
            current.update_time = _now()
            session.add(current)
            session.commit()
        raise


def refresh_configs(
    session: Session,
    *,
    oid: int,
    config_ids: Iterable[int],
) -> list[DictionaryRefreshResult]:
    results: list[DictionaryRefreshResult] = []
    for config_id in dict.fromkeys(config_ids):
        try:
            config = refresh_config(session, oid=oid, config_id=int(config_id))
            results.append(
                DictionaryRefreshResult(
                    id=int(config.id),
                    status=config.status,
                    value_count=config.value_count,
                )
            )
        except Exception as exc:
            current = session.get(DictionaryFieldConfig, int(config_id))
            results.append(
                DictionaryRefreshResult(
                    id=int(config_id),
                    status=(
                        current.status
                        if current is not None
                        else DictionaryStatus.EMPTY
                    ),
                    value_count=current.value_count if current is not None else 0,
                    error=str(exc),
                )
            )
    return results
