import datetime
import json

from fastapi import HTTPException
from sqlalchemy import and_, text
from sqlbot_xpack.permissions.models.ds_rules import DsRules
from sqlmodel import select

from apps.datasource.crud.permission import (
    get_column_permission_fields,
    get_row_permission_filters,
    is_normal_user,
)
from apps.datasource.embedding.table_embedding import calc_table_embedding
from apps.datasource.relation_service import reconcile_relation_graph
from apps.datasource.utils.utils import aes_decrypt
from apps.db.engine import get_engine_conn
from apps.dictionary.service import reconcile_configs
from apps.protocol import QueryPlan, get_protocol_for_ds
from apps.protocol.base import (
    CAP_CONF_OWNED_RESOURCES,
    CAP_DICTIONARY_VALUES,
    CAP_ROW_PERMISSION,
    CAP_SAMPLE_DATA,
    CAP_SQL_DIALECT,
)
from apps.system.schemas.auth import CacheName, CacheNamespace
from common.core.config import settings
from common.core.deps import CurrentUser, SessionDep, Trans
from common.core.sqlbot_cache import cache, clear_cache
from common.utils.embedding_threads import (
    run_save_ds_embeddings,
    run_save_table_embeddings,
)
from common.utils.utils import SQLBotLogUtil, deepcopy_ignore_extra, equals_ignore_case

from ..crud.field import delete_field_by_ds_id
from ..crud.table import delete_table_by_ds_id
from ..models.datasource import (
    ColumnSchema,
    CoreDatasource,
    CoreField,
    CoreTable,
    CreateDatasource,
    DatasourceConf,
    TableAndFields,
    TableObj,
    table_identity_key,
)
from .table import get_tables_by_ds_id


def get_datasource_list(
    session: SessionDep, user: CurrentUser, oid: int | None = None
) -> list[CoreDatasource]:
    current_oid = user.oid if user.oid is not None else 1
    if user.isAdmin and oid:
        current_oid = oid
    return session.exec(
        select(CoreDatasource)
        .where(CoreDatasource.oid == int(current_oid))
        .order_by(CoreDatasource.name)
    ).all()


def get_ds(session: SessionDep, id: int):
    statement = select(CoreDatasource).where(CoreDatasource.id == id)
    datasource = session.exec(statement).first()
    return datasource


def check_status_by_id(
    session: SessionDep, trans: Trans, ds_id: int, is_raise: bool = False
):
    ds = session.get(CoreDatasource, ds_id)
    if ds is None:
        if is_raise:
            raise HTTPException(status_code=500, detail=trans("i18n_ds_invalid"))
        return False
    return check_status(session, trans, ds, is_raise)


def check_status(
    session: SessionDep, trans: Trans, ds: CoreDatasource, is_raise: bool = False
):
    proto = get_protocol_for_ds(ds)
    return proto.check_connection(ds, trans, is_raise)


def check_name(
    session: SessionDep, trans: Trans, user: CurrentUser, ds: CoreDatasource
):
    if ds.id is not None:
        ds_list = (
            session.query(CoreDatasource)
            .filter(
                and_(
                    CoreDatasource.name == ds.name,
                    CoreDatasource.id != ds.id,
                    CoreDatasource.oid == user.oid,
                )
            )
            .all()
        )
        if ds_list is not None and len(ds_list) > 0:
            raise HTTPException(status_code=500, detail=trans("i18n_ds_name_exist"))
    else:
        ds_list = (
            session.query(CoreDatasource)
            .filter(
                and_(CoreDatasource.name == ds.name, CoreDatasource.oid == user.oid)
            )
            .all()
        )
        if ds_list is not None and len(ds_list) > 0:
            raise HTTPException(status_code=500, detail=trans("i18n_ds_name_exist"))


@clear_cache(
    namespace=CacheNamespace.AUTH_INFO,
    cacheName=CacheName.DS_ID_LIST,
    keyExpression="user.oid",
)
async def create_ds(
    session: SessionDep, trans: Trans, user: CurrentUser, create_ds: CreateDatasource
):
    ds = CoreDatasource()
    deepcopy_ignore_extra(create_ds, ds)
    check_name(session, trans, user, ds)
    ds.create_time = datetime.datetime.now()
    ds.create_by = user.id
    ds.oid = user.oid if user.oid is not None else 1
    proto = get_protocol_for_ds(ds)
    check_status(session, trans, ds, True)
    all_tables = list(proto.get_tables(ds))
    if proto.supports(CAP_CONF_OWNED_RESOURCES):
        selected_tables = [
            CoreTable(
                table_name=t.tableName,
                table_comment=t.tableComment or "",
                database_name=getattr(t, "databaseName", None) or None,
            )
            for t in all_tables
        ]
    else:
        selected_tables = list(create_ds.tables or [])

    ds.status = "Success"
    ds.num = f"{len(selected_tables)}/{len(all_tables)}"
    ds.type_name = proto.engine_display_name(ds)
    record = CoreDatasource(**ds.model_dump())
    session.add(record)
    session.flush()
    session.refresh(record)
    ds.id = record.id

    # ``sync_catalog`` discovers all requested fields before its single commit,
    # so datasource + projected catalog either persist together or roll back.
    sync_catalog(session, ds, selected_tables)
    return ds


def chooseTables(session: SessionDep, trans: Trans, id: int, tables: list[CoreTable]):
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == id).first()
    if ds is not None:
        proto = get_protocol_for_ds(ds)
        # Conf-owned resources cannot be freely replaced by client table picks.
        if proto.supports(CAP_CONF_OWNED_RESOURCES):
            tables = [
                CoreTable(
                    table_name=t.tableName,
                    table_comment=t.tableComment or "",
                    database_name=getattr(t, "databaseName", None) or None,
                )
                for t in proto.get_tables(ds)
            ]
    check_status(session, trans, ds, True)
    sync_catalog(session, ds, tables)
    updateNum(session, ds)


def update_ds(session: SessionDep, trans: Trans, user: CurrentUser, ds: CoreDatasource):
    ds.id = int(ds.id)
    check_name(session, trans, user, ds)
    proto = get_protocol_for_ds(ds)
    check_status(session, trans, ds, True)
    projected_tables: list[CoreTable] | None = None
    if proto.supports(CAP_CONF_OWNED_RESOURCES):
        all_tables = list(proto.get_tables(ds))
        projected_tables = [
            CoreTable(
                table_name=t.tableName,
                table_comment=t.tableComment or "",
                database_name=getattr(t, "databaseName", None) or None,
            )
            for t in all_tables
        ]
        ds.num = f"{len(projected_tables)}/{len(all_tables)}"

    ds.status = "Success"
    ds.type_name = proto.engine_display_name(ds)
    record = session.exec(
        select(CoreDatasource).where(CoreDatasource.id == ds.id)
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail=trans("i18n_ds_invalid"))
    update_data = ds.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    session.add(record)

    if projected_tables is not None:
        sync_catalog(session, ds, projected_tables)
    else:
        session.commit()

    run_save_ds_embeddings([ds.id])
    return ds


def update_ds_recommended_config(
    session: SessionDep, datasource_id: int, recommended_config: int
):
    record = session.exec(
        select(CoreDatasource).where(CoreDatasource.id == datasource_id)
    ).first()
    record.recommended_config = recommended_config
    session.add(record)
    session.commit()


async def delete_ds(session: SessionDep, id: int):
    term = session.exec(select(CoreDatasource).where(CoreDatasource.id == id)).first()
    if term.type == "excel":
        # drop all tables for current datasource
        engine = get_engine_conn()
        conf = DatasourceConf(**json.loads(aes_decrypt(term.configuration)))
        with engine.connect() as conn:
            for sheet in conf.sheets:
                conn.execute(text(f'DROP TABLE IF EXISTS "{sheet["tableName"]}"'))
            conn.commit()

    session.delete(term)
    session.commit()
    delete_table_by_ds_id(session, id)
    delete_field_by_ds_id(session, id)
    if term:
        await clear_ws_ds_cache(term.oid)
    return {"message": f"Datasource with ID {id} deleted successfully."}


def getTables(session: SessionDep, id: int):
    ds = session.exec(select(CoreDatasource).where(CoreDatasource.id == id)).first()
    proto = get_protocol_for_ds(ds)
    return proto.get_tables(ds)


def getTablesByDs(session: SessionDep, ds: CoreDatasource):
    proto = get_protocol_for_ds(ds)
    return proto.get_tables(ds)


def getFields(
    session: SessionDep, id: int, table_name: str, database_name: str | None = None
):
    ds = session.exec(select(CoreDatasource).where(CoreDatasource.id == id)).first()
    proto = get_protocol_for_ds(ds)
    return proto.get_fields(ds, table_name, database_name=database_name)


def getFieldsByDs(
    session: SessionDep,
    ds: CoreDatasource,
    table_name: str,
    database_name: str | None = None,
):
    proto = get_protocol_for_ds(ds)
    return proto.get_fields(ds, table_name, database_name=database_name)


def execSql(session: SessionDep, id: int, sql: str):
    """SQL-only debug/exec endpoint; gated via CAP_SQL_DIALECT on the protocol."""
    ds = session.exec(select(CoreDatasource).where(CoreDatasource.id == id)).first()
    if ds is None:
        raise HTTPException(status_code=404, detail="Datasource not found")
    proto = get_protocol_for_ds(ds)
    if not proto.supports(CAP_SQL_DIALECT):
        raise HTTPException(
            status_code=400,
            detail=f"Datasource type '{ds.type}' does not support direct SQL execution",
        )
    qr = proto.execute(
        ds,
        QueryPlan(success=True, statement=sql, payload={"sql": sql}),
        origin_column=True,
    )
    return qr.as_dict()


def sync_table_fields(session: SessionDep, trans: Trans, id: int):
    table = session.query(CoreTable).filter(CoreTable.id == id).first()
    if table is None:
        raise HTTPException(status_code=404, detail=trans("i18n_table_not_exist"))
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == table.ds_id).first()
    if ds is None:
        raise HTTPException(status_code=404, detail=trans("i18n_ds_invalid"))

    tables = getTablesByDs(session, ds)
    t_name = []
    for _t in tables:
        t_name.append(_t.tableName)

    if table.table_name not in t_name:
        raise HTTPException(status_code=500, detail=trans("i18n_table_not_exist"))

    # sync field
    fields = getFieldsByDs(
        session,
        ds,
        table.table_name,
        database_name=getattr(table, "database_name", None),
    )
    _reconcile_fields(session, ds, table, fields)
    reconcile_configs(session, [table])
    session.flush()
    reconcile_relation_graph(
        session,
        oid=int(ds.oid or 1),
        ds_id=int(ds.id),
        commit=False,
    )
    session.commit()

    # do table embedding
    run_save_table_embeddings([table.id])
    run_save_ds_embeddings([ds.id])
    try:
        from apps.datasource.instance_index.service import enqueue_value_index_extract

        enqueue_value_index_extract(int(ds.id), [int(table.id)] if table.id else None)
    except Exception as _value_exc:
        SQLBotLogUtil.warning(f"enqueue value index after sync_single: {_value_exc}")
    try:
        from apps.datasource.profiling.models import ScanRunMode, ScanTrigger
        from apps.datasource.profiling.service import (
            enqueue_table_scan,
            schedule_worker_kick,
        )

        enqueue_table_scan(
            session,
            ds=ds,
            table=table,
            run_mode=ScanRunMode.FACTS_ONLY.value,
            trigger=ScanTrigger.SCHEMA_SYNC.value,
            skip_if_unchanged=True,
        )
        schedule_worker_kick()
    except Exception as _profile_exc:
        SQLBotLogUtil.warning(f"enqueue profiling after sync_single: {_profile_exc}")


def sync_catalog(session: SessionDep, ds: CoreDatasource, tables: list[CoreTable]):
    """Atomically replace the selected local catalog from one remote snapshot."""
    requested = list(tables or [])
    # Complete all remote discovery before mutating the local transaction.
    fields_by_key = {
        table_identity_key(item): getFieldsByDs(
            session,
            ds,
            item.table_name,
            database_name=getattr(item, "database_name", None),
        )
        for item in requested
    }
    existing = session.exec(select(CoreTable).where(CoreTable.ds_id == ds.id)).all()
    existing_by_key = {table_identity_key(table): table for table in existing}
    synced_tables: list[CoreTable] = []
    try:
        for item in requested:
            key = table_identity_key(item)
            record = existing_by_key.get(key)
            if record is None:
                record = CoreTable(
                    ds_id=ds.id,
                    checked=True,
                    table_name=item.table_name,
                    database_name=getattr(item, "database_name", None) or None,
                    table_comment=item.table_comment,
                    custom_comment=item.table_comment,
                )
                session.add(record)
                session.flush()
            else:
                record.table_comment = item.table_comment
                record.database_name = (
                    getattr(item, "database_name", None) or record.database_name
                )
                session.add(record)
            item.id = record.id
            _reconcile_fields(
                session,
                ds,
                record,
                fields_by_key[key],
            )
            synced_tables.append(record)

        keep_ids = [int(table.id) for table in synced_tables if table.id is not None]
        stale_ids = [
            int(table.id)
            for table in existing
            if table.id is not None and table.id not in keep_ids
        ]
        if stale_ids:
            session.query(CoreField).filter(CoreField.table_id.in_(stale_ids)).delete(
                synchronize_session=False
            )
            session.query(CoreTable).filter(CoreTable.id.in_(stale_ids)).delete(
                synchronize_session=False
            )
        if not keep_ids:
            session.query(CoreField).filter(CoreField.ds_id == ds.id).delete(
                synchronize_session=False
            )
            session.query(CoreTable).filter(CoreTable.ds_id == ds.id).delete(
                synchronize_session=False
            )

        reconcile_configs(session, synced_tables)
        session.flush()
        reconcile_relation_graph(
            session,
            oid=int(ds.oid or 1),
            ds_id=int(ds.id),
            commit=False,
        )
        session.commit()
    except Exception:
        session.rollback()
        raise

    id_list = [int(table.id) for table in synced_tables if table.id is not None]
    run_save_table_embeddings(id_list)
    run_save_ds_embeddings([ds.id])
    try:
        from apps.datasource.instance_index.service import enqueue_value_index_extract

        enqueue_value_index_extract(int(ds.id), id_list)
    except Exception as _value_exc:  # never block sync
        SQLBotLogUtil.warning(f"enqueue value index after sync_catalog: {_value_exc}")
    # Catalog stats + field profiling run asynchronously via metadata cognition.
    try:
        from apps.datasource.profiling.models import ScanRunMode, ScanTrigger
        from apps.datasource.profiling.service import (
            enqueue_tables_after_sync,
            schedule_worker_kick,
        )

        if synced_tables:
            enqueue_tables_after_sync(
                session,
                ds=ds,
                tables=synced_tables,
                trigger=ScanTrigger.SCHEMA_SYNC.value,
                run_mode=ScanRunMode.FACTS_ONLY.value,
            )
            schedule_worker_kick()
    except Exception as _profile_exc:  # never block sync
        SQLBotLogUtil.warning(f"enqueue profiling after sync_catalog: {_profile_exc}")


def _reconcile_fields(
    session: SessionDep,
    ds: CoreDatasource,
    table: CoreTable,
    fields: list[ColumnSchema],
) -> None:
    existing = session.exec(
        select(CoreField).where(CoreField.table_id == table.id)
    ).all()
    existing_by_name = {field.field_name: field for field in existing}
    id_list: list[int] = []
    for index, item in enumerate(fields):
        record = existing_by_name.get(item.fieldName)
        if record is not None:
            item.id = record.id
            id_list.append(int(record.id))

            record.field_comment = item.fieldComment
            record.field_index = index
            record.field_type = item.fieldType
            session.add(record)
        else:
            field = CoreField(
                ds_id=ds.id,
                table_id=table.id,
                checked=True,
                field_name=item.fieldName,
                field_type=item.fieldType,
                field_comment=item.fieldComment,
                custom_comment=item.fieldComment,
                field_index=index,
            )
            session.add(field)
            session.flush()
            item.id = field.id
            id_list.append(int(field.id))

    stale_ids = [
        int(field.id)
        for field in existing
        if field.id is not None and field.id not in id_list
    ]
    if stale_ids:
        session.query(CoreField).filter(CoreField.id.in_(stale_ids)).delete(
            synchronize_session=False
        )


def preview(session: SessionDep, current_user: CurrentUser, id: int, data: TableObj):
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == id).first()

    # ignore data's fields param, query fields from database
    if not data.table.id:
        return {"fields": [], "data": [], "sql": ""}

    proto = get_protocol_for_ds(ds)
    # Conf-owned resources (e.g. API endpoints) may preview before response fields are projected.
    conf_owned = proto.supports(CAP_CONF_OWNED_RESOURCES)
    fields = (
        session.query(CoreField)
        .filter(CoreField.table_id == data.table.id)
        .order_by(CoreField.field_index.asc())
        .all()
    )

    if (fields is None or len(fields) == 0) and not conf_owned:
        return {"fields": [], "data": [], "sql": ""}

    where = ""
    f_list = [f for f in (fields or []) if f.checked]
    # Row/column permission is SQL-shaped and capability-gated.
    if proto.supports(CAP_ROW_PERMISSION) and is_normal_user(current_user):
        contain_rules = session.query(DsRules).all()
        f_list = get_column_permission_fields(
            session=session,
            current_user=current_user,
            table=data.table,
            fields=f_list,
            contain_rules=contain_rules,
        )

        where_str = ""
        filter_mapping = get_row_permission_filters(
            session=session,
            current_user=current_user,
            ds=ds,
            tables=None,
            single_table=data.table,
        )
        if filter_mapping:
            mapping_dict = filter_mapping[0]
            where_str = mapping_dict.get("filter")
        where = where_str if where_str else ""

    field_names = [f.field_name for f in f_list]
    if not field_names and not conf_owned:
        return {"fields": [], "data": [], "sql": ""}

    table = session.query(CoreTable).filter(CoreTable.id == data.table.id).first()
    result = proto.preview(
        session,
        current_user,
        ds,
        table.table_name,
        field_names,
        where=where,
        limit=100,
        database_name=getattr(table, "database_name", None),
    )
    return result.as_dict()


def fieldEnum(session: SessionDep, id: int):
    field = session.query(CoreField).filter(CoreField.id == id).first()
    if field is None:
        return []
    table = session.query(CoreTable).filter(CoreTable.id == field.table_id).first()
    if table is None:
        return []
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == table.ds_id).first()
    if ds is None:
        return []

    # Reuse the bounded protocol-owned dictionary extraction contract.
    proto = get_protocol_for_ds(ds)
    if not proto.supports(CAP_DICTIONARY_VALUES):
        return []
    result = proto.extract_dictionary_values(
        ds,
        resource=table.table_name,
        field=field.field_name,
        limit=5000,
        database_name=getattr(table, "database_name", None),
    )
    return result.values


def updateNum(session: SessionDep, ds: CoreDatasource):
    # Excel stores sheets in configuration rather than live get_tables.
    if equals_ignore_case(ds.type, "excel"):
        all_tables = json.loads(aes_decrypt(ds.configuration)).get("sheets")
    else:
        proto = get_protocol_for_ds(ds)
        all_tables = proto.get_tables(ds)
    selected_tables = get_tables_by_ds_id(session, ds.id)
    num = f"{len(selected_tables)}/{len(all_tables)}"

    record = session.exec(
        select(CoreDatasource).where(CoreDatasource.id == ds.id)
    ).first()
    update_data = ds.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    record.num = num
    session.add(record)
    session.commit()


def get_table_obj_by_ds(
    session: SessionDep, current_user: CurrentUser, ds: CoreDatasource
) -> list[TableAndFields]:
    _list: list = []
    tables = (
        session.query(CoreTable)
        .filter(and_(CoreTable.ds_id == ds.id, CoreTable.checked == True))
        .all()
    )
    proto = get_protocol_for_ds(ds)
    schema = proto.schema_namespace(ds)

    # get all field
    table_ids = [table.id for table in tables]
    all_fields = (
        session.query(CoreField)
        .filter(and_(CoreField.table_id.in_(table_ids), CoreField.checked == True))
        .all()
    )
    # build dict
    fields_dict = {}
    for field in all_fields:
        if fields_dict.get(field.table_id):
            fields_dict.get(field.table_id).append(field)
        else:
            fields_dict[field.table_id] = [field]

    contain_rules = session.query(DsRules).all()
    for table in tables:
        # fields = session.query(CoreField).filter(and_(CoreField.table_id == table.id, CoreField.checked == True)).all()
        fields = fields_dict.get(table.id)

        # do column permissions, filter fields
        fields = get_column_permission_fields(
            session=session,
            current_user=current_user,
            table=table,
            fields=fields,
            contain_rules=contain_rules,
        )
        _list.append(TableAndFields(schema=schema, table=table, fields=fields))
    return _list


def get_table_sample_data(
    ds: CoreDatasource,
    table_name: str,
    fields: list,
    *,
    database_name: str | None = None,
) -> str:
    """Get 3 sample rows from a table in JSON format to help AI understand the data"""
    if not fields:
        return ""
    proto = get_protocol_for_ds(ds)
    if not proto.supports(CAP_SAMPLE_DATA):
        return ""

    # Prefer protocol preview so dialect quoting stays inside SqlProtocol.
    field_names = [field.field_name for field in fields[:10]]
    try:
        qr = proto.preview(
            None,
            None,
            ds,
            table_name,
            field_names,
            where="",
            limit=3,
            database_name=database_name,
        )
        if qr and qr.data:
            json_rows = []
            for row in qr.data[:3]:
                truncated_row = {}
                for key, value in row.items():
                    if value is None:
                        truncated_row[key] = None
                    elif isinstance(value, str):
                        if len(value) > 100:
                            value = value[:100] + "..."
                        truncated_row[key] = value.replace("\n", " ").replace("\r", " ")
                    else:
                        truncated_row[key] = value
                json_rows.append(truncated_row)
            return json.dumps(json_rows, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return ""


def get_tables_sample_data(
    session: SessionDep,
    current_user: CurrentUser,
    ds: CoreDatasource,
    table_list: list[str] = None,
    table_objs: list[TableAndFields] | None = None,
) -> str:
    """Get sample data (3 rows) for all tables to help AI understand the data"""
    if table_objs is None:
        table_objs = get_table_obj_by_ds(
            session=session,
            current_user=current_user,
            ds=ds,
        )
    if len(table_objs) == 0:
        return ""

    sample_data_parts = []
    proto = get_protocol_for_ds(ds)
    for obj in table_objs:
        if table_list is not None and obj.table.table_name not in table_list:
            continue
        if obj.fields:
            sample = get_table_sample_data(
                ds,
                obj.table.table_name,
                obj.fields,
                database_name=getattr(obj.table, "database_name", None),
            )
            if sample:
                label = proto.table_prompt_label(
                    ds,
                    obj.table.table_name,
                    database_name=getattr(obj.table, "database_name", None),
                )
                sample_data_parts.append(f"# Table: {label}\n{sample}")
    return "\n".join(sample_data_parts)


def get_table_schema(
    session: SessionDep,
    current_user: CurrentUser,
    ds: CoreDatasource,
    question: str,
    embedding: bool = True,
    table_list: list[str] = None,
    required_table_list: list[str] = None,
    table_objs: list[TableAndFields] | None = None,
    table_limit: int | None = None,
) -> tuple[str, list]:
    """``table_limit``：embedding 召回后的工作集上限（必选表不计入预算）。

    wiki 主导表选择用：wiki 命中的闭包表走 required_table_list 保证入选，
    embedding 召回只补 (limit − 必选数) 张；None = 现状不裁。"""
    schema_str = ""
    if table_objs is None:
        table_objs = get_table_obj_by_ds(
            session=session,
            current_user=current_user,
            ds=ds,
        )
    if len(table_objs) == 0:
        return schema_str, []
    db_name = table_objs[0].schema
    schema_str += f"【DB_ID】 {db_name}\n【Schema】\n"
    tables = []
    all_tables = []  # temp save all tables
    table_name_list = []
    proto = get_protocol_for_ds(ds)
    for obj in table_objs:
        # 如果传入了table_list，则只处理在列表中的表
        if table_list is not None and obj.table.table_name not in table_list:
            continue

        table_db = getattr(obj.table, "database_name", None) or ""
        label = proto.table_prompt_label(
            ds,
            obj.table.table_name,
            database_name=table_db or None,
        )
        from apps.datasource.schema_text import (
            SchemaTextPurpose,
            render_table_schema_text,
        )

        schema_table = render_table_schema_text(
            session,
            table=obj.table,
            fields=list(obj.fields or []),
            table_label=label,
            purpose=SchemaTextPurpose.PROMPT,
        )

        t_obj = {
            "id": obj.table.id,
            "table_name": obj.table.table_name,
            "schema_table": schema_table,
            "embedding": obj.table.embedding,
        }
        tables.append(t_obj)
        all_tables.append(t_obj)

    # 如果没有符合过滤条件的表，直接返回
    if not tables:
        return schema_str, []

    # do table embedding
    # An explicit table_list is an exact projection selected by an existing
    # query plan. Initial NLQ recall has no table_list and may use embeddings.
    if table_list is None and embedding and tables and settings.TABLE_EMBEDDING_ENABLED:
        tables = calc_table_embedding(tables, question)
    required_names = set(required_table_list or [])
    if required_names:
        selected_names = {item.get("table_name") for item in tables}
        tables.extend(
            item
            for item in all_tables
            if item.get("table_name") in required_names
            and item.get("table_name") not in selected_names
        )
    if table_limit is not None and table_limit > 0 and len(tables) > table_limit:
        # 必选表全保；补充表须过相似度下限，不足预算不凑数。
        supplement_floor = float(settings.EMBEDDING_TABLE_SIMILARITY)
        required_first = [t for t in tables if t.get("table_name") in required_names]
        supplement_all = [
            t
            for t in tables
            if t.get("table_name") not in required_names
            and float(t.get("cosine_similarity") or 0.0) >= supplement_floor
        ]
        budget = max(0, table_limit - len(required_first))
        tables = [*required_first, *supplement_all[:budget]]
    # splice schema
    if tables:
        for s in tables:
            schema_str += s.get("schema_table")
            table_name_list.append(s.get("table_name"))

    # Prefer structured confirmed relations; fall back to legacy X6 graph edges.
    confirmed_block = ""
    try:
        from apps.datasource.profiling.models import RelationKind, RelationStatus
        from apps.datasource.profiling.service import get_published_relations

        selected_ids = [int(s.get("id")) for s in tables if s.get("id") is not None]
        published = get_published_relations(
            session,
            ds_id=int(ds.id),
            table_ids=selected_ids,
            statuses=[RelationStatus.CONFIRMED.value],
        )
        equi = [
            r
            for r in published
            if r.kind in (RelationKind.EQUI_JOIN.value, RelationKind.HIERARCHY.value)
        ]
        if equi:
            field_ids = {int(r.source_field_id) for r in equi} | {
                int(r.target_field_id) for r in equi
            }
            table_ids = {int(r.source_table_id) for r in equi} | {
                int(r.target_table_id) for r in equi
            }
            field_map = {
                int(f.id): f.field_name
                for f in session.query(CoreField)
                .filter(CoreField.id.in_(list(field_ids)))
                .all()
                if f.id is not None
            }
            table_map = {
                int(t.id): t.table_name
                for t in session.query(CoreTable)
                .filter(CoreTable.id.in_(list(table_ids)))
                .all()
                if t.id is not None
            }
            # Pull missing endpoint tables into schema text.
            present = {int(s.get("id")) for s in tables if s.get("id") is not None}
            missing = [tid for tid in table_ids if tid not in present]
            if missing:
                lost = [item for item in all_tables if item.get("id") in missing]
                for s in lost:
                    schema_str += s.get("schema_table")
                    table_name_list.append(s.get("table_name"))
            confirmed_block = "【Confirmed relations】\n"
            for rel in equi:
                confirmed_block += (
                    f"{table_map.get(int(rel.source_table_id))}."
                    f"{field_map.get(int(rel.source_field_id))}="
                    f"{table_map.get(int(rel.target_table_id))}."
                    f"{field_map.get(int(rel.target_field_id))}\n"
                )
    except Exception as _rel_exc:
        SQLBotLogUtil.warning(f"confirmed relation schema inject failed: {_rel_exc}")

    if confirmed_block:
        schema_str += confirmed_block
    # Legacy X6 table_relation edges are layout/UI only — never inject as Join truth.

    return schema_str, table_name_list


@cache(
    namespace=CacheNamespace.AUTH_INFO,
    cacheName=CacheName.DS_ID_LIST,
    keyExpression="oid",
)
async def get_ws_ds(session, oid) -> list:
    stmt = select(CoreDatasource.id).distinct().where(CoreDatasource.oid == oid)
    db_list = session.exec(stmt).all()
    return db_list


@clear_cache(
    namespace=CacheNamespace.AUTH_INFO,
    cacheName=CacheName.DS_ID_LIST,
    keyExpression="oid",
)
async def clear_ws_ds_cache(oid):
    SQLBotLogUtil.info(f"ds cache for ws [{oid}] has been cleaned")
