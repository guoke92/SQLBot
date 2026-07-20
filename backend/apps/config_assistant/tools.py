"""Config-assistant tools — thin wrappers over existing system metadata CRUD.

Security envelope:
- tools only touch SQLBot metadata (core_datasource / core_table / core_field)
- no ``execSql``, no customer-engine DML/DDL
- mutations require workspace admin (``isAdmin`` or ``weight != 0``)
- reads/mutations enforce oid ownership of the target datasource
- ``CAP_CONF_OWNED_RESOURCES`` branching lives inside existing CRUD
  (create_ds / update_ds / chooseTables); tools do not re-implement it
"""

from __future__ import annotations

import json
from typing import Any, List, Optional

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from apps.datasource.crud.datasource import (
    check_status,
    chooseTables,
    create_ds,
    get_ds,
    get_datasource_list,
    get_table_sample_data,
    getFields,
    getTables,
    update_ds,
)
from apps.datasource.crud.field import get_fields_by_table_id, update_field
from apps.datasource.crud.table import get_tables_by_ds_id, update_table
from apps.datasource.models.datasource import (
    CoreDatasource,
    CoreField,
    CoreTable,
    CreateDatasource,
    FieldObj,
)
from apps.datasource.utils.utils import aes_encrypt
from apps.conversation.async_util import run_coro_sync
from apps.conversation.session import session_scope
from apps.protocol import get_protocol_for_ds
from apps.protocol.base import CAP_SAMPLE_DATA
from common.utils.locale import I18n

_i18n = I18n()


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def _as_dict(model: Any) -> dict[str, Any]:
    if model is None:
        return {}
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if isinstance(model, dict):
        return model
    return dict(getattr(model, "__dict__", {}) or {})


def _public_ds(ds: CoreDatasource | None) -> dict[str, Any]:
    if ds is None:
        return {}
    data = _as_dict(ds)
    # conf is encrypted blob — never leak full credential material to the model
    conf = data.get("configuration")
    if conf:
        data["configuration"] = "<encrypted>"
        data["configuration_present"] = True
    else:
        data["configuration_present"] = False
    return data


def _require_ws_admin(user: Any) -> None:
    if getattr(user, "isAdmin", False):
        return
    if getattr(user, "weight", 0) == 0:
        raise PermissionError(
            "Only workspace admins can mutate datasource configuration"
        )


def _assert_ds_in_workspace(user: Any, ds: CoreDatasource | None) -> CoreDatasource:
    """Ensure ds exists and belongs to the caller's workspace (unless platform admin)."""
    if ds is None:
        raise ValueError("Datasource not found")
    user_oid = getattr(user, "oid", None)
    if (
        user_oid is not None
        and ds.oid is not None
        and int(ds.oid) != int(user_oid)
        and not getattr(user, "isAdmin", False)
    ):
        raise PermissionError(
            f"Datasource {ds.id} does not belong to current workspace"
        )
    return ds


def _assert_ds_writable(user: Any, ds: CoreDatasource | None) -> CoreDatasource:
    _require_ws_admin(user)
    return _assert_ds_in_workspace(user, ds)


def _maybe_encrypt_configuration(configuration: Optional[str]) -> Optional[str]:
    """Encrypt plaintext JSON conf; leave already-encrypted blobs untouched."""
    if configuration is None or configuration == "":
        return configuration
    try:
        json.loads(configuration)
    except Exception:
        # Not parseable JSON — treat as pre-encrypted storage form
        return configuration
    encrypted = aes_encrypt(configuration)
    if isinstance(encrypted, bytes):
        return encrypted.decode("utf-8")
    return str(encrypted)


def _trans_for(user: Any):
    lang = getattr(user, "language", None) or "zh-CN"
    return _i18n(lang=lang)


def _parse_table_models(tables: str) -> List[CoreTable]:
    raw = json.loads(tables)
    if not isinstance(raw, list):
        raise ValueError("tables must be a JSON array")
    out: List[CoreTable] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("each table entry must be an object")
        out.append(
            CoreTable(
                table_name=item.get("table_name") or item.get("tableName") or "",
                table_comment=item.get("table_comment") or item.get("tableComment") or "",
            )
        )
    return out


# ---- tool arg schemas -------------------------------------------------------


class EmptyArgs(BaseModel):
    pass


class DsIdArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")


class CreateDsArgs(BaseModel):
    name: str = Field(description="Datasource name")
    type: str = Field(
        description="Protocol type key, e.g. mysql/pg/excel/api (not display name)"
    )
    configuration: str = Field(
        description="Datasource configuration as a JSON string (plaintext; system encrypts)"
    )
    description: str = Field(default="", description="Optional description")
    tables: Optional[str] = Field(
        default=None,
        description=(
            "Optional JSON array of tables for initial selection, each item "
            '{"table_name": "...", "table_comment": "..."}. '
            "Ignored for conf-owned resource types which re-project from conf."
        ),
    )


class UpdateDsArgs(BaseModel):
    ds_id: int = Field(description="Datasource id to update")
    name: Optional[str] = Field(default=None, description="New name")
    description: Optional[str] = Field(default=None, description="New description")
    configuration: Optional[str] = Field(
        default=None,
        description="New configuration JSON string (plaintext; system encrypts)",
    )
    type: Optional[str] = Field(
        default=None, description="Protocol type key if changing type"
    )


class ChooseTablesArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")
    tables: str = Field(
        description=(
            'JSON array of tables involved in the operation, e.g. '
            '[{"table_name":"t1","table_comment":""},...]'
        )
    )
    mode: str = Field(
        default="add",
        description=(
            'Projection mode: "add" (default) merges tables into current selection; '
            '"remove" drops named tables from current selection; '
            '"set" replaces the entire selection with the input list. '
            'Never pass mode="set" with only newly added names — that deletes the rest.'
        ),
    )


class TableIdArgs(BaseModel):
    table_id: int = Field(description="CoreTable id in SQLBot metadata")


class CatalogFieldsArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")
    table_name: str = Field(description="Remote catalog table name")


class UpdateTableArgs(BaseModel):
    table_id: int = Field(description="CoreTable id")
    checked: Optional[bool] = Field(
        default=None, description="Whether the table is selected/enabled"
    )
    custom_comment: Optional[str] = Field(
        default=None, description="Custom comment stored in SQLBot"
    )


class UpdateFieldArgs(BaseModel):
    field_id: int = Field(description="CoreField id")
    checked: Optional[bool] = Field(
        default=None, description="Whether the field is selected/enabled"
    )
    custom_comment: Optional[str] = Field(
        default=None, description="Custom comment stored in SQLBot"
    )


class TableFieldsArgs(BaseModel):
    table_id: int = Field(description="CoreTable id")
    field_name: Optional[str] = Field(
        default=None, description="Optional field name filter"
    )


class SampleDataArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")
    table_name: str = Field(
        description=(
            "Already-projected table name (must exist as CoreTable under the "
            "datasource). Protocol-level sample only — not free SQL."
        )
    )


def build_tools(user: Any) -> List[BaseTool]:
    """Build the tool set closed over the current user identity."""

    def list_datasources() -> str:
        with session_scope() as session:
            rows = get_datasource_list(session, user)
            return _json_dumps([_public_ds(ds) for ds in rows])

    def get_datasource(ds_id: int) -> str:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            return _json_dumps(_public_ds(ds))

    def create_datasource(
        name: str,
        type: str,
        configuration: str,
        description: str = "",
        tables: Optional[str] = None,
    ) -> str:
        _require_ws_admin(user)
        conf = _maybe_encrypt_configuration(configuration) or ""
        table_models: List[CoreTable] = _parse_table_models(tables) if tables else []
        create_obj = CreateDatasource(
            name=name,
            type=type,
            description=description or "",
            configuration=conf,
            tables=table_models,
        )
        with session_scope() as session:
            ds = run_coro_sync(create_ds(session, _trans_for(user), user, create_obj))
            return _json_dumps(_public_ds(ds))

    def update_datasource(
        ds_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        configuration: Optional[str] = None,
        type: Optional[str] = None,
    ) -> str:
        with session_scope() as session:
            existing = get_ds(session, ds_id)
            _assert_ds_writable(user, existing)
            payload = existing.model_dump()
            if name is not None:
                payload["name"] = name
            if description is not None:
                payload["description"] = description
            if type is not None:
                payload["type"] = type
            if configuration is not None:
                payload["configuration"] = _maybe_encrypt_configuration(configuration)
            ds_obj = CoreDatasource(**payload)
            updated = update_ds(session, _trans_for(user), user, ds_obj)
            return _json_dumps(_public_ds(updated))

    def check_datasource(ds_id: int) -> str:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"ok": False, "error": str(e)})
            ok = check_status(session, _trans_for(user), ds, is_raise=False)
            return _json_dumps({"ok": bool(ok), "ds_id": ds_id})

    def list_catalog_tables(ds_id: int) -> str:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            tables = getTables(session, ds_id)
            return _json_dumps(
                [
                    {
                        "tableName": getattr(t, "tableName", None),
                        "tableComment": getattr(t, "tableComment", None),
                    }
                    for t in tables
                ]
            )

    def list_selected_tables(ds_id: int) -> str:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            tables = get_tables_by_ds_id(session, ds_id)
            return _json_dumps([_as_dict(t) for t in tables])

    def choose_tables(ds_id: int, tables: str, mode: str = "add") -> str:
        """Project tables into SQLBot metadata.

        Always ends in a full-set write via existing ``chooseTables``/``sync_table``.
        ``mode`` controls how the input list is combined with the current selection
        so the model can safely append without wiping other projections.
        """
        normalized = (mode or "add").strip().lower()
        if normalized not in {"add", "remove", "set"}:
            return _json_dumps(
                {
                    "error": (
                        f'Invalid mode {mode!r}; expected "add", "remove", or "set"'
                    )
                }
            )
        input_models = _parse_table_models(tables)
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_writable(user, ds)
            current = get_tables_by_ds_id(session, ds_id)
            # Build the full projection set; CRUD always syncs as full replace.
            if normalized == "set":
                full = input_models
            elif normalized == "add":
                by_name: dict[str, CoreTable] = {}
                for t in current:
                    name = (t.table_name or "").strip()
                    if name:
                        by_name[name] = CoreTable(
                            table_name=name,
                            table_comment=t.table_comment or t.custom_comment or "",
                        )
                for t in input_models:
                    name = (t.table_name or "").strip()
                    if not name:
                        continue
                    # New names win for comment; existing keep previous unless provided.
                    comment = t.table_comment or ""
                    if name in by_name and not comment:
                        comment = by_name[name].table_comment or ""
                    by_name[name] = CoreTable(table_name=name, table_comment=comment)
                full = list(by_name.values())
            else:  # remove
                drop = {
                    (t.table_name or "").strip()
                    for t in input_models
                    if (t.table_name or "").strip()
                }
                full = [
                    CoreTable(
                        table_name=t.table_name,
                        table_comment=t.table_comment or t.custom_comment or "",
                    )
                    for t in current
                    if (t.table_name or "").strip() not in drop
                ]
            chooseTables(session, _trans_for(user), ds_id, full)
            selected = get_tables_by_ds_id(session, ds_id)
            return _json_dumps(
                {
                    "message": f"tables synchronized (mode={normalized})",
                    "mode": normalized,
                    "input_count": len(input_models),
                    "selected_count": len(selected),
                    "selected": [_as_dict(t) for t in selected],
                }
            )

    def list_catalog_fields(ds_id: int, table_name: str) -> str:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            fields = getFields(session, ds_id, table_name)
            return _json_dumps(
                [
                    {
                        "fieldName": getattr(f, "fieldName", None),
                        "fieldType": getattr(f, "fieldType", None),
                        "fieldComment": getattr(f, "fieldComment", None),
                    }
                    for f in fields
                ]
            )

    def list_table_fields(table_id: int, field_name: Optional[str] = None) -> str:
        with session_scope() as session:
            item = session.get(CoreTable, table_id)
            if item is None:
                return _json_dumps({"error": f"Table {table_id} not found"})
            ds = get_ds(session, item.ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            field = FieldObj(fieldName=field_name) if field_name else FieldObj(fieldName=None)
            fields = get_fields_by_table_id(session, table_id, field)
            return _json_dumps([_as_dict(f) for f in fields])

    def update_table_meta(
        table_id: int,
        checked: Optional[bool] = None,
        custom_comment: Optional[str] = None,
    ) -> str:
        with session_scope() as session:
            item = session.get(CoreTable, table_id)
            if item is None:
                return _json_dumps({"error": f"Table {table_id} not found"})
            ds = get_ds(session, item.ds_id)
            try:
                _assert_ds_writable(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            if checked is not None:
                item.checked = checked
            if custom_comment is not None:
                item.custom_comment = custom_comment
            update_table(session, item)
            refreshed = session.get(CoreTable, table_id)
            return _json_dumps(_as_dict(refreshed))

    def update_field_meta(
        field_id: int,
        checked: Optional[bool] = None,
        custom_comment: Optional[str] = None,
    ) -> str:
        with session_scope() as session:
            item = session.get(CoreField, field_id)
            if item is None:
                return _json_dumps({"error": f"Field {field_id} not found"})
            ds = get_ds(session, item.ds_id)
            try:
                _assert_ds_writable(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})
            if checked is not None:
                item.checked = checked
            if custom_comment is not None:
                item.custom_comment = custom_comment
            update_field(session, item)
            refreshed = session.get(CoreField, field_id)
            return _json_dumps(_as_dict(refreshed))

    def get_sample_data(ds_id: int, table_name: str) -> str:
        """Protocol-level sample preview for an already-projected table.

        Uses ``get_table_sample_data`` → ``proto.preview`` (CAP_SAMPLE_DATA),
        limited to 3 rows × 10 fields. Not business SQL execution.
        """
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            try:
                _assert_ds_in_workspace(user, ds)
            except (ValueError, PermissionError) as e:
                return _json_dumps({"error": str(e)})

            proto = get_protocol_for_ds(ds)
            if not proto.supports(CAP_SAMPLE_DATA):
                return _json_dumps(
                    {
                        "error": (
                            f"Datasource type '{getattr(ds, 'type', None)}' does not "
                            "support sample_data preview (CAP_SAMPLE_DATA)"
                        )
                    }
                )

            tables = get_tables_by_ds_id(session, ds_id)
            match = next(
                (
                    t
                    for t in tables
                    if (t.table_name or "") == table_name
                    or (getattr(t, "table_name", None) or "").lower()
                    == table_name.lower()
                ),
                None,
            )
            if match is None:
                return _json_dumps(
                    {
                        "error": (
                            f"Table '{table_name}' is not projected into SQLBot "
                            "metadata for this datasource. "
                            "Use choose_tables mode=add first, or list_selected_tables."
                        )
                    }
                )

            fields = get_fields_by_table_id(session, match.id, FieldObj(fieldName=None))
            if not fields:
                return _json_dumps(
                    {
                        "error": (
                            f"No fields stored for projected table '{table_name}' "
                            f"(table_id={match.id})"
                        )
                    }
                )

            field_names = [f.field_name for f in fields[:10] if getattr(f, "field_name", None)]
            sample_text = get_table_sample_data(ds, match.table_name or table_name, fields)
            if not sample_text:
                return _json_dumps(
                    {
                        "error": (
                            f"Preview returned no rows for '{table_name}' "
                            "(empty table or protocol preview failure)"
                        ),
                        "ds_id": ds_id,
                        "table_name": match.table_name or table_name,
                        "fields": field_names,
                        "sample_data": [],
                        "row_count": 0,
                    }
                )

            try:
                sample_rows = json.loads(sample_text)
            except Exception:
                sample_rows = sample_text
            row_count = len(sample_rows) if isinstance(sample_rows, list) else None
            return _json_dumps(
                {
                    "ds_id": ds_id,
                    "table_name": match.table_name or table_name,
                    "fields": field_names,
                    "sample_data": sample_rows,
                    "row_count": row_count,
                    "note": (
                        "protocol preview, max 3 rows × 10 fields; "
                        "not a business query or chart pipeline"
                    ),
                }
            )

    return [
        StructuredTool.from_function(
            func=list_datasources,
            name="list_datasources",
            description="List datasources in the current workspace (credentials redacted).",
            args_schema=EmptyArgs,
        ),
        StructuredTool.from_function(
            func=get_datasource,
            name="get_datasource",
            description="Get one datasource by id (credentials redacted).",
            args_schema=DsIdArgs,
        ),
        StructuredTool.from_function(
            func=create_datasource,
            name="create_datasource",
            description=(
                "Create a datasource. configuration is plaintext JSON; system encrypts. "
                "Requires workspace admin."
            ),
            args_schema=CreateDsArgs,
        ),
        StructuredTool.from_function(
            func=update_datasource,
            name="update_datasource",
            description=(
                "Update datasource name/description/configuration/type. "
                "Conf-owned resources re-project tables from conf. Requires ws admin."
            ),
            args_schema=UpdateDsArgs,
        ),
        StructuredTool.from_function(
            func=check_datasource,
            name="check_datasource",
            description="Check datasource connection status.",
            args_schema=DsIdArgs,
        ),
        StructuredTool.from_function(
            func=list_catalog_tables,
            name="list_catalog_tables",
            description="Read-only: list remote catalog tables for a datasource.",
            args_schema=DsIdArgs,
        ),
        StructuredTool.from_function(
            func=list_selected_tables,
            name="list_selected_tables",
            description="List tables currently projected into SQLBot metadata for a datasource.",
            args_schema=DsIdArgs,
        ),
        StructuredTool.from_function(
            func=choose_tables,
            name="choose_tables",
            description=(
                "Update SQL-type datasource table projection. "
                'mode="add" (default) merges tables into current selection; '
                'mode="remove" drops named tables; '
                'mode="set" fully replaces selection with the input list. '
                "Conf-owned types re-project from conf instead. Requires ws admin."
            ),
            args_schema=ChooseTablesArgs,
        ),
        StructuredTool.from_function(
            func=list_catalog_fields,
            name="list_catalog_fields",
            description="Read-only: list remote catalog fields for a table name.",
            args_schema=CatalogFieldsArgs,
        ),
        StructuredTool.from_function(
            func=list_table_fields,
            name="list_table_fields",
            description="List fields stored in SQLBot metadata for a CoreTable id.",
            args_schema=TableFieldsArgs,
        ),
        StructuredTool.from_function(
            func=update_table_meta,
            name="update_table_meta",
            description="Update checked / custom_comment on a CoreTable. Requires ws admin.",
            args_schema=UpdateTableArgs,
        ),
        StructuredTool.from_function(
            func=update_field_meta,
            name="update_field_meta",
            description="Update checked / custom_comment on a CoreField. Requires ws admin.",
            args_schema=UpdateFieldArgs,
        ),
        StructuredTool.from_function(
            func=get_sample_data,
            name="get_sample_data",
            description=(
                "Protocol-level sample preview (max 3 rows x 10 fields) for an already "
                "projected table via CAP_SAMPLE_DATA. Not free SQL and not a chart pipeline. "
                "Use to validate projection; chart analysis belongs in the main NLQ chat."
            ),
            args_schema=SampleDataArgs,
        ),
    ]
