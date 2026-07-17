import datetime
import json
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import and_, text
from sqlbot_xpack.permissions.models.ds_rules import DsRules
from sqlmodel import select

from apps.datasource.crud.permission import get_column_permission_fields, get_row_permission_filters, is_normal_user
from apps.datasource.embedding.table_embedding import calc_table_embedding
from apps.datasource.utils.utils import aes_decrypt
from apps.db.constant import DB
from apps.protocol import get_protocol_for_ds, QueryPlan
from apps.protocol.base import CAP_CONF_OWNED_RESOURCES, CAP_ROW_PERMISSION, CAP_SAMPLE_DATA, CAP_SQL_DIALECT
from apps.db.engine import get_engine_conn
from apps.system.schemas.auth import CacheName, CacheNamespace
from common.core.config import settings
from common.core.deps import SessionDep, CurrentUser, Trans
from common.utils.embedding_threads import run_save_table_embeddings, run_save_ds_embeddings
from common.utils.utils import SQLBotLogUtil, deepcopy_ignore_extra, equals_ignore_case
from common.core.sqlbot_cache import cache, clear_cache
from .table import get_tables_by_ds_id
from ..crud.field import delete_field_by_ds_id, update_field
from ..crud.table import delete_table_by_ds_id, update_table
from ..models.datasource import CoreDatasource, CreateDatasource, CoreTable, CoreField, ColumnSchema, TableObj, \
    DatasourceConf, TableAndFields


def get_datasource_list(session: SessionDep, user: CurrentUser, oid: Optional[int] = None) -> List[CoreDatasource]:
    current_oid = user.oid if user.oid is not None else 1
    if user.isAdmin and oid:
        current_oid = oid
    return session.exec(
        select(CoreDatasource).where(CoreDatasource.oid == int(current_oid)).order_by(CoreDatasource.name)).all()


def get_ds(session: SessionDep, id: int):
    statement = select(CoreDatasource).where(CoreDatasource.id == id)
    datasource = session.exec(statement).first()
    return datasource


def check_status_by_id(session: SessionDep, trans: Trans, ds_id: int, is_raise: bool = False):
    ds = session.get(CoreDatasource, ds_id)
    if ds is None:
        if is_raise:
            raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid'))
        return False
    return check_status(session, trans, ds, is_raise)


def check_status(session: SessionDep, trans: Trans, ds: CoreDatasource, is_raise: bool = False):
    proto = get_protocol_for_ds(ds)
    return proto.check_connection(ds, trans, is_raise)


def check_name(session: SessionDep, trans: Trans, user: CurrentUser, ds: CoreDatasource):
    if ds.id is not None:
        ds_list = session.query(CoreDatasource).filter(
            and_(CoreDatasource.name == ds.name, CoreDatasource.id != ds.id, CoreDatasource.oid == user.oid)).all()
        if ds_list is not None and len(ds_list) > 0:
            raise HTTPException(status_code=500, detail=trans('i18n_ds_name_exist'))
    else:
        ds_list = session.query(CoreDatasource).filter(
            and_(CoreDatasource.name == ds.name, CoreDatasource.oid == user.oid)).all()
        if ds_list is not None and len(ds_list) > 0:
            raise HTTPException(status_code=500, detail=trans('i18n_ds_name_exist'))


@clear_cache(namespace=CacheNamespace.AUTH_INFO, cacheName=CacheName.DS_ID_LIST, keyExpression="user.oid")
async def create_ds(session: SessionDep, trans: Trans, user: CurrentUser, create_ds: CreateDatasource):
    ds = CoreDatasource()
    deepcopy_ignore_extra(create_ds, ds)
    check_name(session, trans, user, ds)
    ds.create_time = datetime.datetime.now()
    # status = check_status(session, ds)
    ds.create_by = user.id
    ds.oid = user.oid if user.oid is not None else 1
    ds.status = "Success"
    proto = get_protocol_for_ds(ds)
    ds.type_name = proto.engine_display_name(ds)
    record = CoreDatasource(**ds.model_dump())
    session.add(record)
    session.flush()
    session.refresh(record)
    ds.id = record.id
    session.commit()

    # save tables and fields.
    # Protocols that own resources in conf (CAP_CONF_OWNED_RESOURCES) always re-project
    # tables/endpoints from conf so client-selected subsets cannot desync projections.
    if proto.supports(CAP_CONF_OWNED_RESOURCES):
        tables = [
            CoreTable(table_name=t.tableName, table_comment=t.tableComment or "")
            for t in proto.get_tables(ds)
        ]
        # Prefer conf resources; fall back to client-selected list if conf is empty.
        sync_table(session, ds, tables if tables else create_ds.tables)
    else:
        sync_table(session, ds, create_ds.tables)
    updateNum(session, ds)
    return ds


def chooseTables(session: SessionDep, trans: Trans, id: int, tables: List[CoreTable]):
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == id).first()
    if ds is not None:
        proto = get_protocol_for_ds(ds)
        # Conf-owned resources cannot be freely replaced by client table picks.
        if proto.supports(CAP_CONF_OWNED_RESOURCES):
            tables = [
                CoreTable(table_name=t.tableName, table_comment=t.tableComment or "")
                for t in proto.get_tables(ds)
            ]
    check_status(session, trans, ds, True)
    sync_table(session, ds, tables)
    updateNum(session, ds)


def update_ds(session: SessionDep, trans: Trans, user: CurrentUser, ds: CoreDatasource):
    ds.id = int(ds.id)
    check_name(session, trans, user, ds)
    # status = check_status(session, trans, ds)
    ds.status = "Success"
    proto = get_protocol_for_ds(ds)
    ds.type_name = proto.engine_display_name(ds)
    record = session.exec(select(CoreDatasource).where(CoreDatasource.id == ds.id)).first()
    update_data = ds.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    session.add(record)
    session.commit()

    # Conf-owned resources re-project into CoreTable/CoreField on every conf update.
    if proto.supports(CAP_CONF_OWNED_RESOURCES):
        tables = [
            CoreTable(table_name=t.tableName, table_comment=t.tableComment or "")
            for t in proto.get_tables(ds)
        ]
        sync_table(session, ds, tables)
        updateNum(session, ds)

    run_save_ds_embeddings([ds.id])
    return ds


def update_ds_recommended_config(session: SessionDep, datasource_id: int, recommended_config: int):
    record = session.exec(select(CoreDatasource).where(CoreDatasource.id == datasource_id)).first()
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
    return {
        "message": f"Datasource with ID {id} deleted successfully."
    }


def getTables(session: SessionDep, id: int):
    ds = session.exec(select(CoreDatasource).where(CoreDatasource.id == id)).first()
    proto = get_protocol_for_ds(ds)
    return proto.get_tables(ds)


def getTablesByDs(session: SessionDep, ds: CoreDatasource):
    proto = get_protocol_for_ds(ds)
    return proto.get_tables(ds)


def getFields(session: SessionDep, id: int, table_name: str):
    ds = session.exec(select(CoreDatasource).where(CoreDatasource.id == id)).first()
    proto = get_protocol_for_ds(ds)
    return proto.get_fields(ds, table_name)


def getFieldsByDs(session: SessionDep, ds: CoreDatasource, table_name: str):
    proto = get_protocol_for_ds(ds)
    return proto.get_fields(ds, table_name)


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


def sync_single_fields(session: SessionDep, trans: Trans, id: int):
    table = session.query(CoreTable).filter(CoreTable.id == id).first()
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == table.ds_id).first()

    tables = getTablesByDs(session, ds)
    t_name = []
    for _t in tables:
        t_name.append(_t.tableName)

    if not table.table_name in t_name:
        raise HTTPException(status_code=500, detail=trans('i18n_table_not_exist'))

    # sync field
    fields = getFieldsByDs(session, ds, table.table_name)
    sync_fields(session, ds, table, fields)

    # do table embedding
    run_save_table_embeddings([table.id])
    run_save_ds_embeddings([ds.id])


def sync_table(session: SessionDep, ds: CoreDatasource, tables: List[CoreTable]):
    id_list = []
    for item in tables:
        statement = select(CoreTable).where(and_(CoreTable.ds_id == ds.id, CoreTable.table_name == item.table_name))
        record = session.exec(statement).first()
        # update exist table, only update table_comment
        if record is not None:
            item.id = record.id
            id_list.append(record.id)

            record.table_comment = item.table_comment
            session.add(record)
            session.commit()
        else:
            # save new table
            table = CoreTable(ds_id=ds.id, checked=True, table_name=item.table_name, table_comment=item.table_comment,
                              custom_comment=item.table_comment)
            session.add(table)
            session.flush()
            session.refresh(table)
            item.id = table.id
            id_list.append(table.id)
            session.commit()

        # sync field
        fields = getFieldsByDs(session, ds, item.table_name)
        sync_fields(session, ds, item, fields)

    if len(id_list) > 0:
        session.query(CoreTable).filter(and_(CoreTable.ds_id == ds.id, CoreTable.id.not_in(id_list))).delete(
            synchronize_session=False)
        session.query(CoreField).filter(and_(CoreField.ds_id == ds.id, CoreField.table_id.not_in(id_list))).delete(
            synchronize_session=False)
        session.commit()
    else:  # delete all tables and fields in this ds
        session.query(CoreTable).filter(CoreTable.ds_id == ds.id).delete(synchronize_session=False)
        session.query(CoreField).filter(CoreField.ds_id == ds.id).delete(synchronize_session=False)
        session.commit()

    # do table embedding
    run_save_table_embeddings(id_list)
    run_save_ds_embeddings([ds.id])


def sync_fields(session: SessionDep, ds: CoreDatasource, table: CoreTable, fields: List[ColumnSchema]):
    id_list = []
    for index, item in enumerate(fields):
        statement = select(CoreField).where(
            and_(CoreField.table_id == table.id, CoreField.field_name == item.fieldName))
        record = session.exec(statement).first()
        if record is not None:
            item.id = record.id
            id_list.append(record.id)

            record.field_comment = item.fieldComment
            record.field_index = index
            record.field_type = item.fieldType
            session.add(record)
            session.commit()
        else:
            field = CoreField(ds_id=ds.id, table_id=table.id, checked=True, field_name=item.fieldName,
                              field_type=item.fieldType, field_comment=item.fieldComment,
                              custom_comment=item.fieldComment, field_index=index)
            session.add(field)
            session.flush()
            session.refresh(field)
            item.id = field.id
            id_list.append(field.id)
            session.commit()

    if len(id_list) > 0:
        session.query(CoreField).filter(and_(CoreField.table_id == table.id, CoreField.id.not_in(id_list))).delete(
            synchronize_session=False)
        session.commit()


def update_table_and_fields(session: SessionDep, data: TableObj):
    update_table(session, data.table)
    for field in data.fields:
        update_field(session, field)

    # do table embedding
    run_save_table_embeddings([data.table.id])
    run_save_ds_embeddings([data.table.ds_id])


def updateTable(session: SessionDep, table: CoreTable):
    update_table(session, table)

    # do table embedding
    run_save_table_embeddings([table.id])
    run_save_ds_embeddings([table.ds_id])


def updateField(session: SessionDep, field: CoreField):
    update_field(session, field)

    # do table embedding
    run_save_table_embeddings([field.table_id])
    run_save_ds_embeddings([field.ds_id])


def preview(session: SessionDep, current_user: CurrentUser, id: int, data: TableObj):
    ds = session.query(CoreDatasource).filter(CoreDatasource.id == id).first()

    # ignore data's fields param, query fields from database
    if not data.table.id:
        return {"fields": [], "data": [], "sql": ""}

    proto = get_protocol_for_ds(ds)
    # Conf-owned resources (e.g. API endpoints) may preview before response fields are projected.
    conf_owned = proto.supports(CAP_CONF_OWNED_RESOURCES)
    fields = session.query(CoreField).filter(CoreField.table_id == data.table.id).order_by(
        CoreField.field_index.asc()).all()

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
    # SqlProtocol includes schema in preview SQL when present on the ds.
    if proto.supports(CAP_SQL_DIALECT):
        setattr(ds, "_preview_schema", proto.schema_namespace(ds))
    result = proto.preview(session, current_user, ds, table.table_name, field_names, where=where, limit=100)
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

    # Field enums only make sense for SQL dialects.
    proto = get_protocol_for_ds(ds)
    if not proto.supports(CAP_SQL_DIALECT):
        return []

    db = DB.get_db(ds.type)
    sql = f"""SELECT DISTINCT {db.prefix}{field.field_name}{db.suffix} FROM {db.prefix}{table.table_name}{db.suffix}"""
    qr = proto.execute(
        ds,
        QueryPlan(success=True, statement=sql, payload={"sql": sql}),
        origin_column=True,
    )
    if not qr.fields:
        return []
    key = qr.fields[0]
    return [row.get(key) for row in qr.data]


def updateNum(session: SessionDep, ds: CoreDatasource):
    # Excel stores sheets in configuration rather than live get_tables.
    if equals_ignore_case(ds.type, "excel"):
        all_tables = json.loads(aes_decrypt(ds.configuration)).get('sheets')
    else:
        proto = get_protocol_for_ds(ds)
        all_tables = proto.get_tables(ds)
    selected_tables = get_tables_by_ds_id(session, ds.id)
    num = f'{len(selected_tables)}/{len(all_tables)}'

    record = session.exec(select(CoreDatasource).where(CoreDatasource.id == ds.id)).first()
    update_data = ds.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    record.num = num
    session.add(record)
    session.commit()


def get_table_obj_by_ds(session: SessionDep, current_user: CurrentUser, ds: CoreDatasource) -> List[TableAndFields]:
    _list: List = []
    tables = session.query(CoreTable).filter(
        and_(CoreTable.ds_id == ds.id, CoreTable.checked == True)
    ).all()
    proto = get_protocol_for_ds(ds)
    schema = proto.schema_namespace(ds)

    # get all field
    table_ids = [table.id for table in tables]
    all_fields = session.query(CoreField).filter(
        and_(CoreField.table_id.in_(table_ids), CoreField.checked == True)).all()
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
        fields = get_column_permission_fields(session=session, current_user=current_user, table=table, fields=fields,
                                              contain_rules=contain_rules)
        _list.append(TableAndFields(schema=schema, table=table, fields=fields))
    return _list


def get_table_sample_data(ds: CoreDatasource, table_name: str, fields: list) -> str:
    """Get 3 sample rows from a table in JSON format to help AI understand the data"""
    if not fields:
        return ""
    proto = get_protocol_for_ds(ds)
    if not proto.supports(CAP_SAMPLE_DATA):
        return ""

    # Prefer protocol preview so dialect quoting stays inside SqlProtocol.
    field_names = [field.field_name for field in fields[:10]]
    try:
        setattr(ds, "_preview_schema", proto.schema_namespace(ds))
        qr = proto.preview(None, None, ds, table_name, field_names, where="", limit=3)
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


def get_tables_sample_data(session: SessionDep, current_user: CurrentUser, ds: CoreDatasource,
                           table_list: list[str] = None) -> str:
    """Get sample data (3 rows) for all tables to help AI understand the data"""
    table_objs = get_table_obj_by_ds(session=session, current_user=current_user, ds=ds)
    if len(table_objs) == 0:
        return ""

    sample_data_parts = []
    for obj in table_objs:
        if table_list is not None and obj.table.table_name not in table_list:
            continue
        if obj.fields:
            sample = get_table_sample_data(ds, obj.table.table_name, obj.fields)
            if sample:
                sample_data_parts.append(f"# Table: {obj.table.table_name}\n{sample}")
    return "\n".join(sample_data_parts)


def get_table_schema(session: SessionDep, current_user: CurrentUser, ds: CoreDatasource, question: str,
                     embedding: bool = True, table_list: list[str] = None) -> tuple[str, list]:
    schema_str = ""
    table_objs = get_table_obj_by_ds(session=session, current_user=current_user, ds=ds)
    if len(table_objs) == 0:
        return schema_str, []
    db_name = table_objs[0].schema
    schema_str += f"【DB_ID】 {db_name}\n【Schema】\n"
    tables = []
    all_tables = []  # temp save all tables
    table_name_list = []
    for obj in table_objs:
        # 如果传入了table_list，则只处理在列表中的表
        if table_list is not None and obj.table.table_name not in table_list:
            continue

        schema_table = ''
        no_schema_types = ["mysql", "es", "sqlite", "hive", "doris", "starrocks"]
        schema_table += f"# Table: {db_name}.{obj.table.table_name}" if ds.type not in no_schema_types and db_name else f"# Table: {obj.table.table_name}"
        table_comment = ''
        if obj.table.custom_comment:
            table_comment = obj.table.custom_comment.strip()
        if table_comment == '':
            schema_table += '\n[\n'
        else:
            schema_table += f", {table_comment}\n[\n"

        if obj.fields:
            field_list = []
            for field in obj.fields:
                field_comment = ''
                if field.custom_comment:
                    field_comment = field.custom_comment.strip()
                if field_comment == '':
                    field_list.append(f"({field.field_name}:{field.field_type})")
                else:
                    field_list.append(f"({field.field_name}:{field.field_type}, {field_comment})")
            schema_table += ",\n".join(field_list)
        schema_table += '\n]\n'

        t_obj = {"id": obj.table.id, "table_name": obj.table.table_name, "schema_table": schema_table,
                 "embedding": obj.table.embedding}
        tables.append(t_obj)
        all_tables.append(t_obj)

    # 如果没有符合过滤条件的表，直接返回
    if not tables:
        return schema_str, []

    # do table embedding
    if embedding and tables and settings.TABLE_EMBEDDING_ENABLED:
        tables = calc_table_embedding(tables, question)
    # splice schema
    if tables:
        for s in tables:
            schema_str += s.get('schema_table')
            table_name_list.append(s.get('table_name'))

    # field relation
    if tables and ds.table_relation:
        relations = list(filter(lambda x: x.get('shape') == 'edge', ds.table_relation))
        if relations:
            # Complete the missing table
            # get tables in relation, remove irrelevant relation
            embedding_table_ids = [s.get('id') for s in tables]
            all_relations = list(
                filter(lambda x: x.get('source').get('cell') in embedding_table_ids or x.get('target').get(
                    'cell') in embedding_table_ids, relations))

            # get relation table ids, sub embedding table ids
            relation_table_ids = []
            for r in all_relations:
                relation_table_ids.append(r.get('source').get('cell'))
                relation_table_ids.append(r.get('target').get('cell'))
            relation_table_ids = list(set(relation_table_ids))
            # get table dict
            table_records = session.query(CoreTable).filter(CoreTable.id.in_(list(map(int, relation_table_ids)))).all()
            table_dict = {}
            for ele in table_records:
                table_dict[ele.id] = ele.table_name

            # get lost table ids
            lost_table_ids = list(set(relation_table_ids) - set(embedding_table_ids))
            # get lost table schema and splice it
            lost_tables = list(filter(lambda x: x.get('id') in lost_table_ids, all_tables))
            if lost_tables:
                for s in lost_tables:
                    schema_str += s.get('schema_table')
                    table_name_list.append(s.get('table_name'))

            # get field dict
            relation_field_ids = []
            for relation in all_relations:
                relation_field_ids.append(relation.get('source').get('port'))
                relation_field_ids.append(relation.get('target').get('port'))
            relation_field_ids = list(set(relation_field_ids))
            field_records = session.query(CoreField).filter(CoreField.id.in_(list(map(int, relation_field_ids)))).all()
            field_dict = {}
            for ele in field_records:
                field_dict[ele.id] = ele.field_name

            if all_relations:
                schema_str += '【Foreign keys】\n'
                for ele in all_relations:
                    schema_str += f"{table_dict.get(int(ele.get('source').get('cell')))}.{field_dict.get(int(ele.get('source').get('port')))}={table_dict.get(int(ele.get('target').get('cell')))}.{field_dict.get(int(ele.get('target').get('port')))}\n"

    return schema_str, table_name_list


@cache(namespace=CacheNamespace.AUTH_INFO, cacheName=CacheName.DS_ID_LIST, keyExpression="oid")
async def get_ws_ds(session, oid) -> list:
    stmt = select(CoreDatasource.id).distinct().where(CoreDatasource.oid == oid)
    db_list = session.exec(stmt).all()
    return db_list


@clear_cache(namespace=CacheNamespace.AUTH_INFO, cacheName=CacheName.DS_ID_LIST, keyExpression="oid")
async def clear_ws_ds_cache(oid):
    SQLBotLogUtil.info(f"ds cache for ws [{oid}] has been cleaned")
