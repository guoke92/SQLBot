"""Build core_value_index rows from wiki field enums and sampled instance columns."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeVar

from sqlalchemy import delete
from sqlmodel import Session, select

from apps.chat.steps.wiki_schema import field_enum_rows, parse_field_enum
from apps.datasource.instance_index.cells import instance_cell_entries
from apps.datasource.instance_index.column_picker import pick_instance_columns
from apps.datasource.instance_index.nomination import (
    INSTANCE_TOP_K,
    consider_instance_column,
    looks_like_opaque_instance_values,
    whitelist_instance_column,
)
from apps.datasource.instance_index.person_map import (
    VAL_PERSON_ALIAS,
    collect_person_evidence,
    merge_person_records,
    person_records_to_payloads,
)
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.models.value_index import CoreValueIndex
from apps.dictionary.matching import normalize_dictionary_value
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

VAL_ENUM_CODE = "enum_code"
VAL_ENUM_LABEL = "enum_label"
VAL_INSTANCE = "instance"
_MIN_VALUE_LENGTH = 2

Payload = tuple[str, str, str, str, dict[str, Any] | None]
T = TypeVar("T")


def _norm(value: str) -> str:
    return normalize_dictionary_value(value)


def _row(
    *,
    ds_id: int,
    table_name: str,
    field_name: str,
    val_type: str,
    raw: str,
    extra: dict[str, Any] | None = None,
) -> CoreValueIndex | None:
    text = str(raw or "").strip()
    normalized = _norm(text)
    if len(normalized) < _MIN_VALUE_LENGTH:
        return None
    table = str(table_name or "")[:128]
    field = str(field_name or "")[:128]
    if not table or not field:
        return None
    return CoreValueIndex(
        ds_id=ds_id,
        table_name=table,
        field_name=field,
        val_type=val_type,
        raw_value=text[:2000],
        normalized_value=normalized[:2000],
        extra=extra,
    )


def select_extract_scope(items: Sequence[T], *, attr: str = "checked") -> list[T]:
    """Online: keep checked items. Offline (none checked): keep all."""
    rows = list(items)
    if any(bool(getattr(item, attr, True)) for item in rows):
        return [item for item in rows if bool(getattr(item, attr, True))]
    return rows


def wiki_table_scope(store: Any, table_name: str) -> tuple[set[str], list[str]]:
    """Field names + name_anchors from the bound wiki table page."""
    from apps.knowledge.wiki.contract import compact_block

    fields: set[str] = set()
    anchors: list[str] = []
    getter = getattr(store, "get_page", None)
    page = None
    if callable(getter):
        page = getter(f"tables/{table_name}") or getter(table_name)
    if page is None:
        return fields, anchors
    for block in getattr(page, "ground_blocks", ()) or ():
        if getattr(block, "kind", "") != "table":
            continue
        data = compact_block(getattr(block, "data", {}) or {})
        for entry in data.get("fields") or []:
            if isinstance(entry, Mapping):
                name = str(entry.get("name") or "").strip()
                if name:
                    fields.add(name)
        raw_anchors = data.get("name_anchors") or []
        if isinstance(raw_anchors, str):
            raw_anchors = [
                part.strip() for part in raw_anchors.split(",") if part.strip()
            ]
        for item in raw_anchors:
            text = str(item).strip()
            if text:
                anchors.append(text)
        break
    return fields, anchors


def collect_wiki_enum_payloads(store: Any, table_name: str) -> list[Payload]:
    """Return (table, field, val_type, raw, extra) tuples from wiki field enums."""
    from apps.knowledge.wiki.contract import compact_block

    payloads: list[Payload] = []
    getter = getattr(store, "get_page", None)
    page = None
    if callable(getter):
        page = getter(f"tables/{table_name}") or getter(table_name)
    if page is None:
        return payloads
    for block in getattr(page, "ground_blocks", ()) or ():
        if getattr(block, "kind", "") != "table":
            continue
        data = compact_block(getattr(block, "data", {}) or {})
        for entry in data.get("fields") or []:
            if not isinstance(entry, Mapping):
                continue
            field_name = str(entry.get("name") or "").strip()
            if not field_name:
                continue
            spec = parse_field_enum(entry, table=table_name)
            for item in field_enum_rows(spec):
                code = str(item.get("value") or "").strip()
                label = str(item.get("label") or "").strip()
                if code:
                    payloads.append(
                        (table_name, field_name, VAL_ENUM_CODE, code, {"code": code})
                    )
                if label and _norm(label) != _norm(code):
                    payloads.append(
                        (
                            table_name,
                            field_name,
                            VAL_ENUM_LABEL,
                            label,
                            {"code": code} if code else None,
                        )
                    )
    return payloads


def collect_dict_page_payloads(store: Any, table_name: str) -> list[Payload]:
    """Map dict pages that declare ``fields: [table.column]`` onto this table."""
    payloads: list[Payload] = []
    prefix = f"{table_name}."
    for page in (getattr(store, "pages", {}) or {}).values():
        if str(getattr(page, "type", "") or "") != "dict":
            continue
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") != "dict":
                continue
            data = getattr(block, "data", {}) or {}
            targets = data.get("fields") or []
            values = data.get("values") or {}
            if not isinstance(values, Mapping):
                continue
            field_names: list[str] = []
            for target in targets:
                text = str(target or "").strip()
                if text.startswith(prefix):
                    field_names.append(text.split(".", 1)[1])
            page_key = str(getattr(page, "page_key", "") or "")
            if not field_names and page_key.startswith(f"{table_name}__"):
                field_names.append(page_key.split("__", 1)[1])
            for field_name in field_names:
                for value, meta in values.items():
                    code = str(value).strip()
                    label = ""
                    if isinstance(meta, Mapping):
                        label = str(meta.get("label") or "").strip()
                    elif meta is not None:
                        label = str(meta).strip()
                    if code:
                        payloads.append(
                            (
                                table_name,
                                field_name,
                                VAL_ENUM_CODE,
                                code,
                                {"code": code},
                            )
                        )
                    if label and _norm(label) != _norm(code):
                        payloads.append(
                            (
                                table_name,
                                field_name,
                                VAL_ENUM_LABEL,
                                label,
                                {"code": code} if code else None,
                            )
                        )
            break
    return payloads


def collect_instance_payloads(
    proto: Any,
    ds: CoreDatasource,
    table: CoreTable,
    fields: Sequence[CoreField],
    *,
    enum_fields: set[str] | None = None,  # noqa: ARG001 — kept; enums may be indexed
    wiki_fields: set[str] | None = None,  # noqa: ARG001 — checked CoreField is source
    name_anchors: Sequence[str] | None = None,
    column_picker: Callable[[str, list[dict[str, Any]]], set[str] | None] | None = None,
) -> list[Payload]:
    """Hard-skip + topK sample; LLM (or nominate whitelist) picks columns.

    Multi-value cells keep the original string and split tokens. Picker failure
    keeps every sampled column — never falls back to the old nominate-only set.
    """
    top_k = int(
        getattr(settings, "VALUE_INDEX_INSTANCE_TOP_K", INSTANCE_TOP_K)
        or INSTANCE_TOP_K
    )
    cap = int(getattr(settings, "VALUE_INDEX_TABLE_INSTANCE_CAP", 2000) or 2000)
    table_name = str(table.table_name or "")
    anchors = [str(item) for item in (name_anchors or []) if str(item).strip()]
    sampled: list[tuple[str, str, list[tuple[str, int]], dict[str, Any]]] = []
    for field in fields:
        name = str(field.field_name or "").strip()
        if not name:
            continue
        comment = str(field.custom_comment or field.field_comment or "")
        mysql_type = str(field.field_type or "")
        if not consider_instance_column(
            name,
            comment=comment,
            mysql_type=mysql_type,
            name_anchors=anchors,
        ):
            continue
        try:
            result = proto.profile_field(
                ds,
                resource=table_name,
                field=name,
                field_type=mysql_type,
                database_name=getattr(table, "database_name", None),
                top_k=top_k,
            )
        except Exception as exc:
            SQLBotLogUtil.warning(
                "value-index profile %s.%s failed: %s", table_name, name, exc
            )
            continue
        if result is None or not getattr(result, "supported", True):
            continue
        raw_values = list(getattr(result, "top_values", None) or [])
        if looks_like_opaque_instance_values(raw_values):
            continue
        values: list[tuple[str, int]] = []
        for item in raw_values:
            if isinstance(item, dict):
                value = str(item.get("value") or "").strip()
                count = int(item.get("count") or 0)
            else:
                value = str(item or "").strip()
                count = 0
            if value:
                values.append((value, count))
            if len(values) >= top_k:
                break
        if not values:
            continue
        sampled.append(
            (
                name,
                comment,
                values,
                {
                    "whitelisted": whitelist_instance_column(
                        name, comment=comment, name_anchors=anchors
                    )
                },
            )
        )
    if not sampled:
        return []
    picker_input = [
        {
            "name": name,
            "comment": comment,
            "samples": [value for value, _count in values[:8]],
        }
        for name, comment, values, meta in sampled
        if not meta["whitelisted"]
    ]
    include: set[str] | None
    if not picker_input:
        include = {name for name, _c, _v, _m in sampled}
    else:
        picker = column_picker or pick_instance_columns
        try:
            include = picker(table_name, picker_input)
        except Exception as exc:
            SQLBotLogUtil.warning(
                "value-index column pick %s failed: %s", table_name, exc
            )
            include = None
        if include is None:
            include = {name for name, _c, _v, _m in sampled}
        else:
            include = set(include) | {
                name for name, _c, _v, meta in sampled if meta["whitelisted"]
            }
    payloads: list[Payload] = []
    instance_count = 0
    for name, _comment, values, _meta in sampled:
        if name not in include:
            continue
        for value, count in values:
            if instance_count >= cap:
                return payloads
            for cell, extra in instance_cell_entries(value, count=count):
                if instance_count >= cap:
                    return payloads
                payloads.append((table_name, name, VAL_INSTANCE, cell, extra))
                instance_count += 1
    return payloads


def rebuild_person_index(
    session: Session,
    *,
    ds: CoreDatasource,
    tables: Sequence[CoreTable],
    proto: Any,
) -> int:
    """Replace ds-level person_alias rows from paired id/name samples."""
    evidence = []
    for table in tables:
        all_fields = session.exec(
            select(CoreField).where(CoreField.table_id == table.id)
        ).all()
        try:
            evidence.extend(collect_person_evidence(proto, ds, table, all_fields))
        except Exception as exc:
            SQLBotLogUtil.warning(
                "person-map extract %s failed: %s",
                getattr(table, "table_name", table.id),
                exc,
            )
    records = merge_person_records(evidence)
    payloads = person_records_to_payloads(records)
    models = payloads_to_models(int(ds.id), payloads)
    session.execute(
        delete(CoreValueIndex).where(
            CoreValueIndex.ds_id == int(ds.id),
            CoreValueIndex.val_type == VAL_PERSON_ALIAS,
        )
    )
    for item in models:
        session.add(item)
    return len(models)


def payloads_to_models(ds_id: int, payloads: Sequence[Payload]) -> list[CoreValueIndex]:
    models: list[CoreValueIndex] = []
    seen: set[tuple[str, str, str, str]] = set()
    for table_name, field_name, val_type, raw, extra in payloads:
        item = _row(
            ds_id=ds_id,
            table_name=table_name,
            field_name=field_name,
            val_type=val_type,
            raw=raw,
            extra=extra,
        )
        if item is None:
            continue
        key = (item.table_name, item.field_name, item.val_type, item.normalized_value)
        if key in seen:
            continue
        seen.add(key)
        models.append(item)
    return models


def extract_table(
    session: Session,
    *,
    ds: CoreDatasource,
    table: CoreTable,
    store: Any = None,
    proto: Any = None,
) -> int:
    """Replace one table's value-index rows. Returns inserted count."""
    from apps.protocol import get_protocol_for_ds

    ds_id = int(ds.id)
    table_name = str(table.table_name or "")
    all_fields = session.exec(
        select(CoreField).where(CoreField.table_id == table.id)
    ).all()
    fields = select_extract_scope(all_fields)
    payloads: list[Payload] = []
    wiki_fields: set[str] = set()
    name_anchors: list[str] = []
    if store is not None:
        payloads.extend(collect_wiki_enum_payloads(store, table_name))
        payloads.extend(collect_dict_page_payloads(store, table_name))
        wiki_fields, name_anchors = wiki_table_scope(store, table_name)
    enum_fields = {
        item[1] for item in payloads if item[2] in {VAL_ENUM_CODE, VAL_ENUM_LABEL}
    }
    protocol = proto or get_protocol_for_ds(ds)
    try:
        payloads.extend(
            collect_instance_payloads(
                protocol,
                ds,
                table,
                fields,
                enum_fields=enum_fields,
                wiki_fields=wiki_fields or None,
                name_anchors=name_anchors,
            )
        )
    except Exception as exc:
        SQLBotLogUtil.warning(
            "value-index instance extract %s failed: %s", table_name, exc
        )
    models = payloads_to_models(ds_id, payloads)
    session.execute(
        delete(CoreValueIndex).where(
            CoreValueIndex.ds_id == ds_id,
            CoreValueIndex.table_name == table_name,
        )
    )
    for item in models:
        session.add(item)
    return len(models)
