"""Config-assistant tools — thin wrappers over existing system metadata CRUD.

Security envelope:
- tools only touch AI智能问数 metadata (core_datasource / core_table / core_field)
- no ``execSql``, no customer-engine DML/DDL
- mutations require workspace admin (``isAdmin`` or ``weight != 0``)
- reads/mutations enforce oid ownership of the target datasource
- ``CAP_CONF_OWNED_RESOURCES`` branching lives inside existing CRUD
  (create_ds / update_ds / metadata service); tools do not re-implement it
"""

from __future__ import annotations

import json
from typing import Any, List, Optional

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from apps.datasource.crud.datasource import (
    check_status,
    create_ds,
    get_ds,
    get_datasource_list,
    get_table_sample_data,
    getFields,
    getTables,
    update_ds,
)
from apps.datasource.crud.field import get_fields_by_table_id
from apps.datasource.crud.table import get_tables_by_ds_id
from apps.datasource.metadata_service import (
    update_field_metadata,
    update_table_metadata,
    update_table_projection,
)
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
from apps.conversation.tooling import ToolResult, tool_success
from apps.config_assistant.tools.common import (
    require_datasource_scope,
    require_workspace_admin as _require_ws_admin,
    translator_for as _trans_for,
)
from apps.protocol import get_protocol, get_protocol_for_ds
from apps.protocol.base import CAP_SAMPLE_DATA
from common.core.branding import APP_DISPLAY_NAME


def _public_ds(ds: CoreDatasource | None) -> dict[str, Any]:
    if ds is None:
        return {}
    return {
        "id": ds.id,
        "name": ds.name,
        "description": ds.description,
        "type": ds.type,
        "type_name": ds.type_name,
        "status": ds.status,
        "table_count": ds.num,
        "recommended_config": ds.recommended_config,
        "configuration_present": bool(ds.configuration),
    }


def _public_table(table: CoreTable) -> dict[str, Any]:
    return {
        "id": table.id,
        "ds_id": table.ds_id,
        "checked": table.checked,
        "table_name": table.table_name,
        "database_name": getattr(table, "database_name", None),
        "table_comment": table.table_comment,
        "custom_comment": table.custom_comment,
        "approx_rows": table.approx_rows,
        "data_bytes": table.data_bytes,
        "index_summary": table.index_summary,
        "stats_updated_at": table.stats_updated_at,
    }


def _public_field(field: CoreField) -> dict[str, Any]:
    return {
        "id": field.id,
        "ds_id": field.ds_id,
        "table_id": field.table_id,
        "checked": field.checked,
        "field_name": field.field_name,
        "field_type": field.field_type,
        "field_comment": field.field_comment,
        "custom_comment": field.custom_comment,
        "field_index": field.field_index,
    }


def _assert_ds_in_workspace(user: Any, ds: CoreDatasource | None) -> CoreDatasource:
    return require_datasource_scope(user, ds)


def _assert_ds_writable(user: Any, ds: CoreDatasource | None) -> CoreDatasource:
    return require_datasource_scope(user, ds, writable=True)


def _encrypt_configuration(configuration: dict[str, Any]) -> str:
    encrypted = aes_encrypt(json.dumps(configuration, ensure_ascii=False))
    if isinstance(encrypted, bytes):
        return encrypted.decode("utf-8")
    return str(encrypted)


def _normalize_configuration(
    datasource_type: str,
    configuration: dict[str, Any],
) -> dict[str, Any]:
    return get_protocol(datasource_type).normalize_configuration(configuration)


def _parse_table_models(tables: list[Any]) -> List[CoreTable]:
    out: List[CoreTable] = []
    for item in tables:
        raw = item.model_dump() if hasattr(item, "model_dump") else item
        if not isinstance(raw, dict):
            raise ValueError("each table entry must be an object")
        out.append(
            CoreTable(
                table_name=raw.get("table_name") or "",
                table_comment=raw.get("table_comment") or "",
                database_name=raw.get("database_name") or None,
            )
        )
    return out


# ---- tool arg schemas -------------------------------------------------------


class EmptyArgs(BaseModel):
    pass


class DsIdArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")


class TableSelection(BaseModel):
    table_name: str
    table_comment: str = ""
    database_name: Optional[str] = Field(
        default=None,
        description="Logical database under the datasource/catalog (required for multi-DB StarRocks)",
    )


class CreateDsArgs(BaseModel):
    name: str = Field(description="Datasource name")
    type: str = Field(
        description="Protocol type key, e.g. mysql/pg/excel/api/starrocks (not display name)"
    )
    configuration: dict[str, Any] = Field(
        description=(
            "Plain JSON object using the datasource protocol's canonical fields. "
            "SQL connections use username (never user), password, host, port, "
            "database and optional dbSchema/extraJdbc/timeout/ssl. "
            "For StarRocks/Doris external catalogs also set catalog (e.g. hive_emr) "
            "and databases (list of DB names under that catalog). Never put "
            "catalog.database into the single database field."
        )
    )
    description: str = Field(default="", description="Optional description")
    tables: Optional[list[TableSelection]] = Field(
        default=None,
        description="Optional initial table selection",
    )


class UpdateDsArgs(BaseModel):
    ds_id: int = Field(description="Datasource id to update")
    name: Optional[str] = Field(default=None, description="New name")
    description: Optional[str] = Field(default=None, description="New description")
    configuration: Optional[dict[str, Any]] = Field(
        default=None,
        description=(
            "New plaintext configuration using canonical protocol fields; "
            "SQL connections use username, never user"
        ),
    )
    type: Optional[str] = Field(
        default=None, description="Protocol type key if changing type"
    )


class ChooseTablesArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")
    tables: list[TableSelection]
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
    table_id: int = Field(description=f"CoreTable id in {APP_DISPLAY_NAME} metadata")


class CatalogFieldsArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")
    table_name: str = Field(description="Remote catalog table name")
    database_name: Optional[str] = Field(
        default=None,
        description="Logical database name when the datasource spans multiple databases",
    )


class UpdateTableArgs(BaseModel):
    table_id: int = Field(description="CoreTable id")
    checked: Optional[bool] = Field(
        default=None, description="Whether the table is selected/enabled"
    )
    custom_comment: Optional[str] = Field(
        default=None, description=f"Custom comment stored in {APP_DISPLAY_NAME}"
    )


class UpdateFieldArgs(BaseModel):
    field_id: int = Field(description="CoreField id")
    checked: Optional[bool] = Field(
        default=None, description="Whether the field is selected/enabled"
    )
    custom_comment: Optional[str] = Field(
        default=None, description=f"Custom comment stored in {APP_DISPLAY_NAME}"
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
    database_name: Optional[str] = Field(
        default=None,
        description="Logical database name when multiple databases are projected",
    )


def build_metadata_tools(user: Any) -> List[BaseTool]:
    """Build datasource, table and field metadata tools."""

    def list_datasources() -> ToolResult:
        with session_scope() as session:
            rows = get_datasource_list(session, user)
            data = [_public_ds(ds) for ds in rows]
            return tool_success(f"Found {len(data)} datasources", data)

    def get_datasource(ds_id: int) -> ToolResult:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)
            return tool_success("Datasource loaded", _public_ds(ds))

    def create_datasource(
        name: str,
        type: str,
        configuration: dict[str, Any],
        description: str = "",
        tables: Optional[list[TableSelection]] = None,
    ) -> ToolResult:
        _require_ws_admin(user)
        conf = _encrypt_configuration(_normalize_configuration(type, configuration))
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
            return tool_success("Datasource created", _public_ds(ds))

    def update_datasource(
        ds_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        type: Optional[str] = None,
    ) -> ToolResult:
        with session_scope() as session:
            existing = get_ds(session, ds_id)
            _assert_ds_writable(user, existing)
            if name is not None:
                existing.name = name
            if description is not None:
                existing.description = description
            if type is not None:
                existing.type = type
            if configuration is not None:
                existing.configuration = _encrypt_configuration(
                    _normalize_configuration(existing.type, configuration)
                )
            updated = update_ds(session, _trans_for(user), user, existing)
            return tool_success("Datasource updated", _public_ds(updated))

    def check_datasource(ds_id: int) -> ToolResult:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)
            ok = check_status(session, _trans_for(user), ds, is_raise=False)
            if not ok:
                raise ValueError(f"Datasource {ds_id} connection check failed")
            return tool_success("Datasource connection succeeded", {"ds_id": ds_id})

    def list_catalog_tables(ds_id: int) -> ToolResult:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)
            tables = getTables(session, ds_id)
            data = [
                {
                    "table_name": getattr(t, "tableName", None),
                    "table_comment": getattr(t, "tableComment", None),
                    "database_name": getattr(t, "databaseName", None) or "",
                }
                for t in tables
            ]
            return tool_success(
                f"Found {len(data)} catalog tables",
                data,
            )

    def list_databases(ds_id: int) -> ToolResult:
        with session_scope() as session:
            from apps.db.db import get_schema

            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)
            try:
                databases = get_schema(ds)
            except Exception as exc:
                raise ValueError(f"Failed to list databases: {exc}") from exc
            return tool_success(
                f"Found {len(databases)} databases",
                {"ds_id": ds_id, "databases": databases},
            )

    def list_selected_tables(ds_id: int) -> ToolResult:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)
            tables = get_tables_by_ds_id(session, ds_id)
            data = [_public_table(table) for table in tables]
            return tool_success(f"Found {len(data)} selected tables", data)

    def choose_tables(
        ds_id: int,
        tables: list[TableSelection],
        mode: str = "add",
    ) -> ToolResult:
        """Project tables into AI智能问数 metadata.

        Always ends in the datasource domain's canonical full-set sync.
        ``mode`` controls how the input list is combined with the current selection
        so the model can safely append without wiping other projections.
        """
        normalized = (mode or "add").strip().lower()
        input_models = _parse_table_models(tables)
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_writable(user, ds)
            selected = update_table_projection(
                session,
                trans=_trans_for(user),
                ds_id=ds_id,
                tables=input_models,
                mode=normalized,
            )
            return tool_success(
                f"Tables synchronized (mode={normalized})",
                {
                    "mode": normalized,
                    "input_count": len(input_models),
                    "selected_count": len(selected),
                    "selected": [_public_table(table) for table in selected],
                },
            )

    def list_catalog_fields(
        ds_id: int,
        table_name: str,
        database_name: Optional[str] = None,
    ) -> ToolResult:
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)
            fields = getFields(session, ds_id, table_name, database_name=database_name)
            data = [
                {
                    "field_name": getattr(f, "fieldName", None),
                    "field_type": getattr(f, "fieldType", None),
                    "field_comment": getattr(f, "fieldComment", None),
                }
                for f in fields
            ]
            return tool_success(
                f"Found {len(data)} catalog fields",
                data,
            )

    def list_table_fields(
        table_id: int,
        field_name: Optional[str] = None,
    ) -> ToolResult:
        with session_scope() as session:
            item = session.get(CoreTable, table_id)
            if item is None:
                raise ValueError(f"Table {table_id} not found")
            ds = get_ds(session, item.ds_id)
            _assert_ds_in_workspace(user, ds)
            field = FieldObj(fieldName=field_name) if field_name else FieldObj(fieldName=None)
            fields = get_fields_by_table_id(session, table_id, field)
            data = [_public_field(item) for item in fields]
            return tool_success(f"Found {len(data)} table fields", data)

    def update_table_meta(
        table_id: int,
        checked: Optional[bool] = None,
        custom_comment: Optional[str] = None,
    ) -> ToolResult:
        with session_scope() as session:
            item = session.get(CoreTable, table_id)
            if item is None:
                raise ValueError(f"Table {table_id} not found")
            ds = get_ds(session, item.ds_id)
            _assert_ds_writable(user, ds)
            updated = update_table_metadata(
                session,
                table_id=table_id,
                checked=checked,
                custom_comment=custom_comment,
            )
            return tool_success("Table metadata updated", _public_table(updated))

    def update_field_meta(
        field_id: int,
        checked: Optional[bool] = None,
        custom_comment: Optional[str] = None,
    ) -> ToolResult:
        with session_scope() as session:
            item = session.get(CoreField, field_id)
            if item is None:
                raise ValueError(f"Field {field_id} not found")
            ds = get_ds(session, item.ds_id)
            _assert_ds_writable(user, ds)
            updated = update_field_metadata(
                session,
                field_id=field_id,
                checked=checked,
                custom_comment=custom_comment,
            )
            return tool_success("Field metadata updated", _public_field(updated))

    def get_sample_data(
        ds_id: int,
        table_name: str,
        database_name: Optional[str] = None,
    ) -> ToolResult:
        """Protocol-level sample preview for an already-projected table.

        Uses ``get_table_sample_data`` → ``proto.preview`` (CAP_SAMPLE_DATA),
        limited to 3 rows × 10 fields. Not business SQL execution.
        """
        with session_scope() as session:
            ds = get_ds(session, ds_id)
            _assert_ds_in_workspace(user, ds)

            proto = get_protocol_for_ds(ds)
            if not proto.supports(CAP_SAMPLE_DATA):
                raise ValueError(
                    f"Datasource type '{getattr(ds, 'type', None)}' does not "
                    "support sample_data preview (CAP_SAMPLE_DATA)"
                )

            tables = get_tables_by_ds_id(session, ds_id)
            match = next(
                (
                    t
                    for t in tables
                    if (
                        (t.table_name or "") == table_name
                        or (getattr(t, "table_name", None) or "").lower()
                        == table_name.lower()
                    )
                    and (
                        not database_name
                        or (getattr(t, "database_name", None) or "") == database_name
                    )
                ),
                None,
            )
            if match is None:
                raise ValueError(
                    f"Table '{table_name}' is not projected into {APP_DISPLAY_NAME} "
                    "metadata for this datasource. "
                    "Use choose_tables mode=add first, or list_selected_tables."
                )

            fields = get_fields_by_table_id(session, match.id, FieldObj(fieldName=None))
            if not fields:
                raise ValueError(
                    f"No fields stored for projected table '{table_name}' "
                    f"(table_id={match.id})"
                )

            field_names = [f.field_name for f in fields[:10] if getattr(f, "field_name", None)]
            sample_text = get_table_sample_data(
                ds,
                match.table_name or table_name,
                fields,
                database_name=getattr(match, "database_name", None) or database_name,
            )
            if not sample_text:
                return tool_success(
                    f"Preview returned no rows for '{table_name}'",
                    {
                        "ds_id": ds_id,
                        "table_name": match.table_name or table_name,
                        "fields": field_names,
                        "sample_data": [],
                        "row_count": 0,
                    },
                )

            try:
                sample_rows = json.loads(sample_text)
            except Exception:
                sample_rows = sample_text
            row_count = len(sample_rows) if isinstance(sample_rows, list) else None
            return tool_success(
                f"Previewed {row_count or 0} rows",
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
                },
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
            func=list_databases,
            name="list_databases",
            description=(
                "Read-only: list databases for a datasource. For StarRocks/Doris with "
                "an external catalog configured, lists databases under that catalog."
            ),
            args_schema=DsIdArgs,
        ),
        StructuredTool.from_function(
            func=list_selected_tables,
            name="list_selected_tables",
            description=(
                f"List tables currently projected into {APP_DISPLAY_NAME} metadata "
                "for a datasource."
            ),
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
            description=f"List fields stored in {APP_DISPLAY_NAME} metadata for a CoreTable id.",
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
