import base64
import json
import os
import platform
import re
import urllib.parse
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Any, Optional, List, Iterator
from contextlib import contextmanager

import oracledb
import psycopg2
import pymssql

from apps.db.db_sql import get_table_sql, get_field_sql, get_version_sql
from common.error import SQLBotDBError

if platform.system() != "Darwin":
    import dmPython
import pymysql
import redshift_connector
from sqlalchemy import create_engine, text, Engine, types
from sqlalchemy.orm import sessionmaker

from apps.datasource.models.datasource import DatasourceConf, CoreDatasource, TableSchema, ColumnSchema
from apps.datasource.utils.utils import aes_decrypt
from apps.db.constant import DB, ConnectType
from apps.db.engine import get_engine_config
from apps.system.crud.assistant import get_out_ds_conf
from apps.system.schemas.system_schema import AssistantOutDsSchema
from common.core.deps import Trans
from common.utils.utils import SQLBotLogUtil, equals_ignore_case
from fastapi import HTTPException
from apps.db.es_engine import get_es_connect, get_es_index, get_es_fields, get_es_data_by_http
from common.core.config import settings
import sqlglot
from sqlglot import expressions as exp
from sqlalchemy.pool import NullPool
from pyhive import hive

try:
    if os.path.exists(settings.ORACLE_CLIENT_PATH):
        oracledb.init_oracle_client(
            lib_dir=settings.ORACLE_CLIENT_PATH
        )
        SQLBotLogUtil.info("init oracle client success, use thick mode")
    else:
        SQLBotLogUtil.info("init oracle client failed, because not found oracle client, use thin mode")
except Exception as e:
    SQLBotLogUtil.error("init oracle client failed, check your client is installed, use thin mode")


def get_uri(ds: CoreDatasource) -> str:
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration))) if not equals_ignore_case(ds.type,
                                                                                                 "excel") else get_engine_config()
    return get_uri_from_config(ds.type, conf)


def get_uri_from_config(type: str, conf: DatasourceConf) -> str:
    db_url: str
    if equals_ignore_case(type, "mysql"):
        checkParams(conf.extraJdbc, DB.mysql.illegalParams)
        if conf.extraJdbc is not None and conf.extraJdbc != '':
            db_url = f"mysql+pymysql://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}?{conf.extraJdbc}"
        else:
            db_url = f"mysql+pymysql://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}"
    elif equals_ignore_case(type, "sqlServer"):
        if conf.extraJdbc is not None and conf.extraJdbc != '':
            db_url = f"mssql+pymssql://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}?{conf.extraJdbc}"
        else:
            db_url = f"mssql+pymssql://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}"
    elif equals_ignore_case(type, "pg", "excel"):
        if conf.extraJdbc is not None and conf.extraJdbc != '':
            db_url = f"postgresql+psycopg2://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}?{conf.extraJdbc}"
        else:
            db_url = f"postgresql+psycopg2://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}"
    elif equals_ignore_case(type, "oracle"):
        if equals_ignore_case(conf.mode, "service_name", "serviceName"):
            if conf.extraJdbc is not None and conf.extraJdbc != '':
                db_url = f"oracle+oracledb://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}?service_name={conf.database}&{conf.extraJdbc}"
            else:
                db_url = f"oracle+oracledb://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}?service_name={conf.database}"
        else:
            if conf.extraJdbc is not None and conf.extraJdbc != '':
                db_url = f"oracle+oracledb://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}?{conf.extraJdbc}"
            else:
                db_url = f"oracle+oracledb://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}"
    elif equals_ignore_case(type, "ck"):
        if conf.extraJdbc is not None and conf.extraJdbc != '':
            db_url = f"clickhouse+http://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}?{conf.extraJdbc}"
        else:
            db_url = f"clickhouse+http://{urllib.parse.quote(conf.username)}:{urllib.parse.quote(conf.password)}@{conf.host}:{conf.port}/{conf.database}"
    else:
        raise 'The datasource type not support.'
    return db_url


def get_extra_config(conf: DatasourceConf):
    config_dict = {}
    if conf.extraJdbc:
        config_arr = conf.extraJdbc.split("&")
        for config in config_arr:
            kv = config.split("=")
            if len(kv) == 2 and kv[0] and kv[1]:
                config_dict[kv[0]] = kv[1]
            else:
                raise Exception(f'param: {config} is error')
    return config_dict


@contextmanager
def starrocks_connection(
    conf: DatasourceConf,
    *,
    default_database: str | None = None,
    connect_timeout: int | None = None,
    read_timeout: int | None = None,
) -> Iterator[tuple[Any, Any]]:
    """Open a pymysql session for Doris/StarRocks with optional SET CATALOG.

    Never passes a dotted ``catalog.database`` as the MySQL protocol database.
    """
    from apps.db.starrocks_catalog import (
        connect_database_arg,
        resolve_sr_scope,
        set_catalog_sql,
        use_database_sql,
    )

    catalog, databases = resolve_sr_scope(conf)
    db_arg = connect_database_arg(conf)
    extra_config_dict = get_extra_config(conf)
    ssl_args = {"ssl": {"ssl_mode": "REQUIRE"}} if conf.ssl else {}
    ct = int(connect_timeout if connect_timeout is not None else (conf.timeout or 10))
    rt = int(read_timeout if read_timeout is not None else (conf.timeout or 10))
    connect_kwargs: dict[str, Any] = {
        "user": conf.username,
        "passwd": conf.password,
        "host": conf.host,
        "port": conf.port,
        "connect_timeout": ct,
        "read_timeout": rt,
        **extra_config_dict,
        **ssl_args,
    }
    if db_arg:
        connect_kwargs["db"] = db_arg

    conn = pymysql.connect(**connect_kwargs)
    try:
        cursor = conn.cursor()
        try:
            if catalog:
                cursor.execute(set_catalog_sql(catalog))
                use_db = default_database or (databases[0] if databases else None)
                if use_db:
                    cursor.execute(use_database_sql(use_db))
            yield conn, cursor
        finally:
            cursor.close()
    finally:
        conn.close()


def _starrocks_list_tables(conf: DatasourceConf) -> list[TableSchema]:
    """List tables for Doris/StarRocks.

    External catalog → SHOW TABLES FROM catalog.db (information_schema is unreliable).
    Internal → information_schema.TABLES per database (keeps TABLE_COMMENT).
    """
    from apps.db.starrocks_catalog import resolve_sr_scope, show_tables_sql

    catalog, databases = resolve_sr_scope(conf)
    if not databases:
        return []

    tables: list[TableSchema] = []
    with starrocks_connection(conf, default_database=databases[0]) as (_conn, cursor):
        if catalog:
            for database in databases:
                cursor.execute(show_tables_sql(catalog, database))
                for row in cursor.fetchall():
                    name = row[0] if row else ""
                    if isinstance(name, bytes):
                        name = name.decode("utf-8")
                    tables.append(TableSchema(name, "", database_name=database))
            return tables

        sql = """
                SELECT
                    TABLE_NAME,
                    TABLE_COMMENT
                FROM
                    information_schema.TABLES
                WHERE
                    TABLE_SCHEMA = %s
                """
        for database in databases:
            cursor.execute(sql, (database,))
            for item in cursor.fetchall():
                tables.append(TableSchema(item[0], item[1], database_name=database))
    return tables


def _starrocks_list_fields(
    conf: DatasourceConf,
    table_name: str | None = None,
    database_name: str | None = None,
) -> list[ColumnSchema]:
    """List columns for Doris/StarRocks.

    Identity is (database_name, bare table_name) — no dotted-name parsing.
    External catalog → SHOW FULL COLUMNS; internal → INFORMATION_SCHEMA.COLUMNS.
    """
    from apps.db.starrocks_catalog import (
        bare_table_name,
        resolve_sr_scope,
        show_full_columns_sql,
    )

    catalog, databases = resolve_sr_scope(conf)
    db_name = (database_name or "").strip() or (databases[0] if databases else "")
    bare_table = bare_table_name(table_name)
    if not db_name:
        return []

    if catalog and bare_table:
        with starrocks_connection(conf, default_database=db_name) as (_conn, cursor):
            cursor.execute(show_full_columns_sql(catalog, db_name, bare_table))
            rows = cursor.fetchall()
            # SHOW FULL COLUMNS: Field, Type, Collation, Null, Key, Default, Extra, Privileges, Comment
            out: list[ColumnSchema] = []
            for row in rows:
                field_name = row[0]
                field_type = row[1] if len(row) > 1 else ""
                field_comment = row[8] if len(row) > 8 else (row[-1] if row else "")
                out.append(ColumnSchema(field_name, field_type, field_comment))
            return out

    sql = """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    COLUMN_COMMENT
                FROM
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_SCHEMA = %s
                """
    params: list[Any] = [db_name]
    if bare_table:
        sql += " AND TABLE_NAME = %s"
        params.append(bare_table)
    with starrocks_connection(conf, default_database=db_name) as (_conn, cursor):
        cursor.execute(sql, tuple(params))
        res = cursor.fetchall()
        return [ColumnSchema(*item) for item in res]


def get_origin_connect(type: str, conf: DatasourceConf):
    extra_config_dict = get_extra_config(conf)
    if equals_ignore_case(type, "sqlServer"):
        # none or true, set tds_version = 7.0
        if conf.lowVersion is None or conf.lowVersion:
            return pymssql.connect(
                server=conf.host,
                port=str(conf.port),
                user=conf.username,
                password=conf.password,
                database=conf.database,
                timeout=conf.timeout,
                tds_version='7.0',  # options: '4.2', '7.0', '8.0' ...,
                **extra_config_dict
            )
        else:
            return pymssql.connect(
                server=conf.host,
                port=str(conf.port),
                user=conf.username,
                password=conf.password,
                database=conf.database,
                timeout=conf.timeout,
                **extra_config_dict
            )


# use sqlalchemy
def get_engine(ds: CoreDatasource, timeout: int = 0) -> Engine:
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration))) if not equals_ignore_case(ds.type,
                                                                                                 "excel") else get_engine_config()
    if conf.timeout is None:
        conf.timeout = timeout
    if timeout > 0:
        conf.timeout = timeout
    # Floor for hung analytics queries when DS conf timeout is 0/None
    try:
        from apps.chat.plan_policy import EXECUTE_TIMEOUT_SEC

        floor = int(EXECUTE_TIMEOUT_SEC or 0)
    except Exception:
        floor = 45
    ct = int(conf.timeout or 0)
    if ct <= 0 and floor > 0:
        conf.timeout = floor
        ct = floor

    if equals_ignore_case(ds.type, "pg"):
        if conf.dbSchema is not None and conf.dbSchema != "":
            engine = create_engine(get_uri(ds),
                                   connect_args={"options": f"-c search_path={urllib.parse.quote(conf.dbSchema)}",
                                                 "connect_timeout": conf.timeout}, poolclass=NullPool)
        else:
            engine = create_engine(get_uri(ds), connect_args={"connect_timeout": conf.timeout}, poolclass=NullPool)
    elif equals_ignore_case(ds.type, 'sqlServer'):
        engine = create_engine('mssql+pymssql://', creator=lambda: get_origin_connect(ds.type, conf),
                               poolclass=NullPool)
    elif equals_ignore_case(ds.type, 'oracle'):
        engine = create_engine(get_uri(ds), poolclass=NullPool)
    elif equals_ignore_case(ds.type, 'mysql'):  # mysql — set read/write timeout to avoid hung executes
        ssl_mode = {"require": True} if conf.ssl else None
        connect_args = {
            "connect_timeout": ct or floor or 10,
            "read_timeout": ct or floor or 45,
            "write_timeout": ct or floor or 45,
        }
        if ssl_mode:
            connect_args["ssl"] = ssl_mode
        engine = create_engine(get_uri(ds), connect_args=connect_args, poolclass=NullPool)
    else:  # ck
        engine = create_engine(get_uri(ds), connect_args={"connect_timeout": conf.timeout}, poolclass=NullPool)
    return engine


def get_session(ds: CoreDatasource | AssistantOutDsSchema):
    # engine = get_engine(ds) if isinstance(ds, CoreDatasource) else get_ds_engine(ds)
    if isinstance(ds, AssistantOutDsSchema):
        out_conf = get_out_ds_conf(ds, 30)
        ds.configuration = out_conf

    engine = get_engine(ds)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


def check_connection(trans: Optional[Trans], ds: CoreDatasource | AssistantOutDsSchema, is_raise: bool = False):
    if isinstance(ds, AssistantOutDsSchema):
        out_conf = get_out_ds_conf(ds, 10)
        ds.configuration = out_conf

    db = DB.get_db(ds.type)
    if db.connect_type == ConnectType.sqlalchemy:
        conn = get_engine(ds, 10)
        try:
            with conn.connect() as connection:
                SQLBotLogUtil.info("success")
                return True
        except Exception as e:
            SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
            if is_raise:
                raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
            return False
    else:
        conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
        extra_config_dict = get_extra_config(conf)
        if equals_ignore_case(ds.type, 'dm'):
            with dmPython.connect(user=conf.username, password=conf.password, server=conf.host,
                                  port=conf.port, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute('select 1', timeout=10).fetchall()
                    SQLBotLogUtil.info("success")
                    return True
                except Exception as e:
                    SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
                    if is_raise:
                        raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
                    return False
        elif equals_ignore_case(ds.type, 'doris', 'starrocks'):
            with starrocks_connection(conf, connect_timeout=10, read_timeout=10) as (
                _conn,
                cursor,
            ):
                try:
                    cursor.execute('select 1')
                    SQLBotLogUtil.info("success")
                    return True
                except Exception as e:
                    SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
                    if is_raise:
                        raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
                    return False
        elif equals_ignore_case(ds.type, 'redshift'):
            with redshift_connector.connect(host=conf.host, port=conf.port, database=conf.database,
                                            user=conf.username,
                                            password=conf.password,
                                            timeout=10, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute('select 1')
                    SQLBotLogUtil.info("success")
                    return True
                except Exception as e:
                    SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
                    if is_raise:
                        raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
                    return False
        elif equals_ignore_case(ds.type, 'kingbase'):
            with psycopg2.connect(host=conf.host, port=conf.port, database=conf.database,
                                  user=conf.username,
                                  password=conf.password,
                                  connect_timeout=10, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute('select 1')
                    SQLBotLogUtil.info("success")
                    return True
                except Exception as e:
                    SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
                    if is_raise:
                        raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
                    return False
        elif equals_ignore_case(ds.type, 'hive'):
            with hive.connect(host=conf.host, port=conf.port, username=conf.username,
                              database=conf.database, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute('select 1')
                    SQLBotLogUtil.info("success")
                    return True
                except Exception as e:
                    SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
                    if is_raise:
                        raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
                    return False

        elif equals_ignore_case(ds.type, 'es'):
            es_conn = get_es_connect(conf)
            if es_conn.ping():
                SQLBotLogUtil.info("success")
                return True
            else:
                SQLBotLogUtil.info("failed")
                return False
    # else:
    #     conn = get_ds_engine(ds)
    #     try:
    #         with conn.connect() as connection:
    #             SQLBotLogUtil.info("success")
    #             return True
    #     except Exception as e:
    #         SQLBotLogUtil.error(f"Datasource {ds.id} connection failed: {e}")
    #         if is_raise:
    #             raise HTTPException(status_code=500, detail=trans('i18n_ds_invalid') + f': {e.args}')
    #         return False

    return False


def get_version(ds: CoreDatasource | AssistantOutDsSchema):
    version = ''
    # Only SQL protocols have a meaningful server version. Gate via capability so
    # REST / future non-SQL types do not branch on type strings here.
    try:
        from apps.protocol import get_protocol_for_ds
        from apps.protocol.base import CAP_SQL_DIALECT

        if not get_protocol_for_ds(ds).supports(CAP_SQL_DIALECT):
            return ''
    except Exception:
        # Unknown type / protocol not registered: no version, never fall back to
        # type-string special-cases (those belong in protocol capabilities).
        return ''
    if isinstance(ds, CoreDatasource):
        conf = DatasourceConf(
            **json.loads(aes_decrypt(ds.configuration))) if not equals_ignore_case(ds.type,
                                                                                   "excel") else get_engine_config()
    else:
        conf = DatasourceConf(**json.loads(aes_decrypt(get_out_ds_conf(ds, 10))))
    db = DB.get_db(ds.type)
    sql = get_version_sql(ds, conf)
    if not sql:
        return ''
    try:
        if db.connect_type == ConnectType.sqlalchemy:
            with get_session(ds) as session:
                with session.execute(text(sql)) as result:
                    res = result.fetchall()
                    version = res[0][0]
        else:
            extra_config_dict = get_extra_config(conf)
            if equals_ignore_case(ds.type, 'dm'):
                with dmPython.connect(user=conf.username, password=conf.password, server=conf.host,
                                      port=conf.port) as conn, conn.cursor() as cursor:
                    cursor.execute(sql, timeout=10, **extra_config_dict)
                    res = cursor.fetchall()
                    version = res[0][0]
            elif equals_ignore_case(ds.type, 'doris', 'starrocks'):
                with starrocks_connection(conf, connect_timeout=10, read_timeout=10) as (
                    _conn,
                    cursor,
                ):
                    cursor.execute(sql)
                    res = cursor.fetchall()
                    version = res[0][0]
            elif equals_ignore_case(ds.type, 'redshift', 'es', 'hive'):
                version = ''
    except Exception as e:
        print(e)
        version = ''
    return version.decode() if isinstance(version, bytes) else version



def get_schema(ds: CoreDatasource):
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration))) if ds.type != "excel" else get_engine_config()
    db = DB.get_db(ds.type)
    if db.connect_type == ConnectType.sqlalchemy:
        with get_session(ds) as session:
            sql: str = ''
            if equals_ignore_case(ds.type, "sqlServer"):
                sql = """select name
                         from sys.schemas"""
            elif equals_ignore_case(ds.type, "pg", "excel"):
                sql = """SELECT nspname
                         FROM pg_namespace"""
            elif equals_ignore_case(ds.type, "oracle"):
                sql = """select *
                         from all_users"""
            with session.execute(text(sql)) as result:
                res = result.fetchall()
                res_list = [item[0] for item in res]
                return res_list
    else:
        extra_config_dict = get_extra_config(conf)
        if equals_ignore_case(ds.type, 'dm'):
            with dmPython.connect(user=conf.username, password=conf.password, server=conf.host,
                                  port=conf.port, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute("""select OBJECT_NAME
                                  from all_objects
                                  where object_type = 'SCH'""", timeout=conf.timeout)
                res = cursor.fetchall()
                res_list = [item[0] for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'redshift'):
            with redshift_connector.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                            password=conf.password,
                                            timeout=conf.timeout, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute("""SELECT nspname
                                  FROM pg_namespace""")
                res = cursor.fetchall()
                res_list = [item[0] for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'kingbase'):
            with psycopg2.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                  password=conf.password,
                                  options=f"-c statement_timeout={conf.timeout * 1000}",
                                  **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute("""SELECT nspname
                                  FROM pg_namespace""")
                res = cursor.fetchall()
                res_list = [item[0] for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'doris', 'starrocks'):
            from apps.db.starrocks_catalog import resolve_sr_scope, show_databases_sql

            catalog, _databases = resolve_sr_scope(conf)
            with starrocks_connection(conf) as (_conn, cursor):
                cursor.execute(show_databases_sql(catalog))
                res = cursor.fetchall()
                return [item[0] if not isinstance(item[0], bytes) else item[0].decode("utf-8") for item in res]


def get_tables(ds: CoreDatasource):
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration))) if not equals_ignore_case(ds.type,
                                                                                                 "excel") else get_engine_config()
    # Doris/StarRocks own their discovery path (catalog-aware); skip db_sql templates.
    if equals_ignore_case(ds.type, 'doris', 'starrocks'):
        return _starrocks_list_tables(conf)
    db = DB.get_db(ds.type)
    sql, sql_param = get_table_sql(ds, conf, get_version(ds))
    if db.connect_type == ConnectType.sqlalchemy:
        with get_session(ds) as session:
            with session.execute(text(sql), {"param": sql_param}) as result:
                res = result.fetchall()
                res_list = [TableSchema(*item) for item in res]
                return res_list
    else:
        extra_config_dict = get_extra_config(conf)
        if equals_ignore_case(ds.type, 'dm'):
            with dmPython.connect(user=conf.username, password=conf.password, server=conf.host,
                                  port=conf.port, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql, {"param": sql_param}, timeout=conf.timeout)
                res = cursor.fetchall()
                res_list = [TableSchema(*item) for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'redshift'):
            with redshift_connector.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                            password=conf.password,
                                            timeout=conf.timeout, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql, (sql_param,))
                res = cursor.fetchall()
                res_list = [TableSchema(*item) for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'kingbase'):
            with psycopg2.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                  password=conf.password,
                                  options=f"-c statement_timeout={conf.timeout * 1000}",
                                  **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql.format(sql_param))
                res = cursor.fetchall()
                res_list = [TableSchema(*item) for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'es'):
            res = get_es_index(conf)
            res_list = [TableSchema(*item) for item in res]
            return res_list
        elif equals_ignore_case(ds.type, 'hive'):
            with hive.connect(host=conf.host, port=conf.port, username=conf.username,
                              database=conf.database, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
                res_list = [TableSchema(*item) for item in res]
                return res_list


def get_fields(ds: CoreDatasource, table_name: str = None, database_name: str | None = None):
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration))) if not equals_ignore_case(ds.type,
                                                                                                 "excel") else get_engine_config()
    if equals_ignore_case(ds.type, 'doris', 'starrocks'):
        return _starrocks_list_fields(conf, table_name, database_name=database_name)
    db = DB.get_db(ds.type)
    sql, p1, p2 = get_field_sql(ds, conf, table_name)
    if db.connect_type == ConnectType.sqlalchemy:
        with get_session(ds) as session:
            with session.execute(text(sql), {"param1": p1, "param2": p2}) as result:
                res = result.fetchall()
                res_list = [ColumnSchema(*item) for item in res]
                return res_list
    else:
        extra_config_dict = get_extra_config(conf)
        if equals_ignore_case(ds.type, 'dm'):
            with dmPython.connect(user=conf.username, password=conf.password, server=conf.host,
                                  port=conf.port, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql, {"param1": p1, "param2": p2}, timeout=conf.timeout)
                res = cursor.fetchall()
                res_list = [ColumnSchema(*item) for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'redshift'):
            with redshift_connector.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                            password=conf.password,
                                            timeout=conf.timeout, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql, (p1, p2))
                res = cursor.fetchall()
                res_list = [ColumnSchema(*item) for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'kingbase'):
            with psycopg2.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                  password=conf.password,
                                  options=f"-c statement_timeout={conf.timeout * 1000}",
                                  **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql.format(p1, p2))
                res = cursor.fetchall()
                res_list = [ColumnSchema(*item) for item in res]
                return res_list
        elif equals_ignore_case(ds.type, 'es'):
            res = get_es_fields(conf, table_name)
            res_list = [ColumnSchema(*item) for item in res]
            return res_list
        elif equals_ignore_case(ds.type, 'hive'):
            with hive.connect(host=conf.host, port=conf.port, username=conf.username,
                              database=conf.database, **extra_config_dict) as conn, conn.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
                res_list = [ColumnSchema(*item) for item in res]
                return res_list


def convert_value(value, datetime_format='space'):
    """
        将Python值转换为JSON可序列化的类型

        :param value: 要转换的值
        :param datetime_format: 日期时间格式
            'iso' - 2024-01-15T14:30:45 (ISO标准，带T)
            'space' - 2024-01-15 14:30:45 (空格分隔，更常见)
            'auto' - 自动选择
        """
    if value is None:
        return None
        # 处理 bytes 类型（包括 BIT 字段）
    if isinstance(value, bytes):
        # 1. 尝试判断是否是 BIT 类型
        if len(value) <= 8:  # BIT 类型通常不会很长
            try:
                # 转换为整数
                int_val = int.from_bytes(value, 'big')

                # 如果是 0 或 1，返回布尔值更直观
                if int_val in (0, 1):
                    return bool(int_val)
                else:
                    return int_val
            except:
                # 如果转换失败，尝试解码为字符串
                pass

        # 2. 尝试解码为 UTF-8 字符串
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            # 3. 如果包含非打印字符，返回十六进制
            if any(b < 32 and b not in (9, 10, 13) for b in value):  # 非打印字符
                return f"0x{value.hex()}"
            else:
                # 4. 尝试 Latin-1 解码（不会失败）
                return value.decode('latin-1')

    elif isinstance(value, bytearray):
        # 处理 bytearray
        return convert_value(bytes(value))

    if isinstance(value, timedelta):
        # 将 timedelta 转换为秒数（整数）或字符串
        return str(value)  # 或 value.total_seconds()
    elif isinstance(value, Decimal):
        return float(value)
    # 4. 处理 datetime
    elif isinstance(value, datetime):
        if datetime_format == 'iso':
            return value.isoformat()
        elif datetime_format == 'space':
            return value.strftime('%Y-%m-%d %H:%M:%S')
        else:  # 'auto' 或其他
            # 自动判断：没有时间部分只显示日期
            if value.hour == 0 and value.minute == 0 and value.second == 0 and value.microsecond == 0:
                return value.strftime('%Y-%m-%d')
            else:
                return value.strftime('%Y-%m-%d %H:%M:%S')

    # 5. 处理 date
    elif isinstance(value, date):
        return value.isoformat()  # 总是 YYYY-MM-DD

    # 6. 处理 time
    elif isinstance(value, time):
        return str(value)
    else:
        return value


def _fetch_query_rows(result, max_rows: int | None):
    """Fetch at most ``max_rows`` rows plus one sentinel for truncation."""
    if max_rows is None or max_rows <= 0:
        return result.fetchall(), False, None
    rows = result.fetchmany(max_rows + 1)
    return rows[:max_rows], len(rows) > max_rows, max_rows


def _query_result_payload(
    *,
    fields,
    data,
    fields_info,
    sql: str,
    truncated: bool,
    limit: int | None,
):
    payload = {
        "fields": fields,
        "data": data,
        "fields_info": fields_info,
        "sql": bytes.decode(base64.b64encode(bytes(sql, "utf-8"))),
    }
    if truncated:
        payload.update(
            {
                "truncated": True,
                "limit": limit,
                "truncation_reason": "query_limit",
            }
        )
    return payload


def exec_sql(
    ds: CoreDatasource | AssistantOutDsSchema,
    sql: str,
    origin_column=False,
    max_rows: int | None = None,
):
    while sql.endswith(';'):
        sql = sql[:-1]
    # check execute sql only contain read operations
    is_safe, error_reason = check_sql_read(sql, ds)
    if not is_safe:
        raise ValueError(f"SQL can only contain read operations: {error_reason}")

    # Inject dialect statement timeouts for long analytics SELECTs (best-effort).
    exec_sql_text = sql
    try:
        from apps.chat.plan_policy import EXECUTE_TIMEOUT_MS

        ms = int(EXECUTE_TIMEOUT_MS or 0)
    except Exception:
        ms = 0
    if ms > 0 and equals_ignore_case(getattr(ds, "type", ""), "mysql", "doris", "starrocks", "mariadb"):
        # MySQL 5.7.8+ SELECT max_execution_time hint (ms)
        stripped = sql.lstrip()
        if stripped[:6].upper() == "SELECT" and "max_execution_time" not in stripped.lower():
            exec_sql_text = f"SELECT /*+ MAX_EXECUTION_TIME({ms}) */ " + stripped[6:].lstrip()
    elif ms > 0 and equals_ignore_case(getattr(ds, "type", ""), "pg", "postgresql", "kingbase"):
        pass

    db = DB.get_db(ds.type)
    if db.connect_type == ConnectType.sqlalchemy:
        with get_session(ds) as session:
            if ms > 0 and equals_ignore_case(getattr(ds, "type", ""), "pg", "postgresql", "kingbase"):
                try:
                    session.execute(text(f"SET LOCAL statement_timeout = {int(ms)}"))
                except Exception:
                    pass
            with session.execute(text(exec_sql_text)) as result:
                try:
                    columns = result.keys()._keys if origin_column else [item.lower() for item in result.keys()._keys]
                    fields_info = build_fields_info_from_cursor(
                        result.cursor,
                        origin_column,
                        ds.type,
                    )

                    res, truncated, limit = _fetch_query_rows(result, max_rows)
                    result_list = [
                        {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                        res
                    ]
                    return _query_result_payload(
                        fields=columns,
                        data=result_list,
                        fields_info=fields_info,
                        sql=sql,
                        truncated=truncated,
                        limit=limit,
                    )
                except Exception as ex:
                    raise SQLBotDBError(str(ex))
    else:
        conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
        extra_config_dict = get_extra_config(conf)
        if equals_ignore_case(ds.type, 'dm'):
            with dmPython.connect(user=conf.username, password=conf.password, server=conf.host,
                                  port=conf.port, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute(sql, timeout=conf.timeout)
                    res, truncated, limit = _fetch_query_rows(cursor, max_rows)
                    columns = [field[0] for field in cursor.description] if origin_column else [field[0].lower() for
                                                                                                field in
                                                                                                cursor.description]
                    fields_info = build_fields_info_from_cursor(cursor, origin_column, ds.type)
                    result_list = [
                        {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                        res
                    ]
                    return _query_result_payload(
                        fields=columns,
                        data=result_list,
                        fields_info=fields_info,
                        sql=sql,
                        truncated=truncated,
                        limit=limit,
                    )
                except Exception as ex:
                    raise SQLBotDBError(str(ex))
        elif equals_ignore_case(ds.type, 'doris', 'starrocks'):
            with starrocks_connection(conf) as (_conn, cursor):
                try:
                    cursor.execute(sql)
                    res, truncated, limit = _fetch_query_rows(cursor, max_rows)
                    columns = [field[0] for field in cursor.description] if origin_column else [field[0].lower() for
                                                                                                field in
                                                                                                cursor.description]
                    fields_info = build_fields_info_from_cursor(cursor, origin_column, ds.type)
                    result_list = [
                        {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                        res
                    ]
                    return _query_result_payload(
                        fields=columns,
                        data=result_list,
                        fields_info=fields_info,
                        sql=sql,
                        truncated=truncated,
                        limit=limit,
                    )
                except Exception as ex:
                    raise SQLBotDBError(str(ex))
        elif equals_ignore_case(ds.type, 'redshift'):
            with redshift_connector.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                            password=conf.password,
                                            timeout=conf.timeout, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    res, truncated, limit = _fetch_query_rows(cursor, max_rows)
                    columns = [field[0] for field in cursor.description] if origin_column else [field[0].lower() for
                                                                                                field in
                                                                                                cursor.description]
                    fields_info = build_fields_info_from_cursor(cursor, origin_column, ds.type)
                    result_list = [
                        {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                        res
                    ]
                    return _query_result_payload(
                        fields=columns,
                        data=result_list,
                        fields_info=fields_info,
                        sql=sql,
                        truncated=truncated,
                        limit=limit,
                    )
                except Exception as ex:
                    raise SQLBotDBError(str(ex))
        elif equals_ignore_case(ds.type, 'kingbase'):
            with psycopg2.connect(host=conf.host, port=conf.port, database=conf.database, user=conf.username,
                                  password=conf.password,
                                  options=f"-c statement_timeout={conf.timeout * 1000}",
                                  **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    res, truncated, limit = _fetch_query_rows(cursor, max_rows)
                    columns = [field[0] for field in cursor.description] if origin_column else [field[0].lower() for
                                                                                                field in
                                                                                                cursor.description]
                    fields_info = build_fields_info_from_cursor(cursor, origin_column, ds.type)
                    result_list = [
                        {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                        res
                    ]
                    return _query_result_payload(
                        fields=columns,
                        data=result_list,
                        fields_info=fields_info,
                        sql=sql,
                        truncated=truncated,
                        limit=limit,
                    )
                except Exception as ex:
                    raise SQLBotDBError(str(ex))
        elif equals_ignore_case(ds.type, 'es'):
            try:
                res, raw_columns = get_es_data_by_http(conf, sql)
                if max_rows is not None and max_rows > 0:
                    truncated = len(res) > max_rows
                    limit = max_rows
                    res = res[:max_rows]
                else:
                    truncated = False
                    limit = None
                columns = [field.get('name') for field in raw_columns] if origin_column else [field.get('name').lower()
                                                                                              for
                                                                                              field in
                                                                                              raw_columns]
                fields_info = build_fields_info_from_es(raw_columns, origin_column)
                result_list = [
                    {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                    res
                ]
                return _query_result_payload(
                    fields=columns,
                    data=result_list,
                    fields_info=fields_info,
                    sql=sql,
                    truncated=truncated,
                    limit=limit,
                )
            except Exception as ex:
                raise SQLBotDBError(str(ex))
        elif equals_ignore_case(ds.type, 'hive'):
            with hive.connect(host=conf.host, port=conf.port, username=conf.username,
                              database=conf.database, **extra_config_dict) as conn, conn.cursor() as cursor:
                try:
                    # Hive uses backticks for identifiers; normalize quoted identifiers as a compatibility fallback.
                    hive_sql = re.sub(r'"([A-Za-z_][A-Za-z0-9_]*)"', r'`\1`', sql)
                    cursor.execute(hive_sql)
                    res, truncated, limit = _fetch_query_rows(cursor, max_rows)
                    columns = [field[0] for field in cursor.description] if origin_column else [field[0].lower() for
                                                                                                field in
                                                                                                cursor.description]
                    fields_info = build_fields_info_from_cursor(cursor, origin_column, ds.type)
                    result_list = [
                        {str(columns[i]): convert_value(value) for i, value in enumerate(tuple_item)} for tuple_item in
                        res
                    ]
                    return _query_result_payload(
                        fields=columns,
                        data=result_list,
                        fields_info=fields_info,
                        sql=hive_sql,
                        truncated=truncated,
                        limit=limit,
                    )
                except Exception as ex:
                    raise SQLBotDBError(str(ex))


_CURSOR_TYPE_FAMILIES = {
    "mysql": "mysql",
    "mariadb": "mysql",
    "doris": "mysql",
    "starrocks": "mysql",
    "pg": "postgresql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "excel": "postgresql",
    "redshift": "postgresql",
    "kingbase": "postgresql",
    "sqlserver": "sqlserver",
    "mssql": "sqlserver",
    "oracle": "oracle",
    "ck": "clickhouse",
    "clickhouse": "clickhouse",
    "dm": "dm",
    "hive": "hive",
}

_NUMERIC_CURSOR_TYPE_CODES = {
    "mysql": frozenset({
        1,  # TINYINT
        2,  # SMALLINT
        3,  # INT
        4,  # FLOAT
        5,  # DOUBLE
        8,  # BIGINT
        9,  # MEDIUMINT
        16,  # BIT
        246,  # DECIMAL
    }),
    "postgresql": frozenset({
        16,  # boolean
        20,  # int8
        21,  # int2
        23,  # int4
        700,  # float4
        701,  # float8
        1700,  # numeric
    }),
    "dm": frozenset({
        2,  # NUMBER
        3,  # DECIMAL/NUMERIC
        4,  # INTEGER
        5,  # INT
        6,  # BIGINT
        7,  # TINYINT
        8,  # BYTE
        9,  # FLOAT
        10,  # DOUBLE
        11,  # REAL
        12,  # BOOLEAN
    }),
}

_NUMERIC_TYPE_NAMES = frozenset({
    "tinyint",
    "smallint",
    "int",
    "bigint",
    "float",
    "double",
    "decimal",
    "numeric",
    "number",
    "real",
    "boolean",
    "bool",
})

_DRIVER_NUMERIC_TYPES = {
    "sqlserver": (pymssql.NUMBER, pymssql.DECIMAL),
    "oracle": (
        oracledb.DB_TYPE_NUMBER,
        oracledb.DB_TYPE_BINARY_INTEGER,
        oracledb.DB_TYPE_BINARY_FLOAT,
        oracledb.DB_TYPE_BINARY_DOUBLE,
        oracledb.DB_TYPE_BOOLEAN,
    ),
}


def _is_numeric_cursor_type(type_code, db_type: str) -> bool:
    family = _CURSOR_TYPE_FAMILIES.get((db_type or "").lower(), (db_type or "").lower())
    numeric_codes = _NUMERIC_CURSOR_TYPE_CODES.get(family)
    if numeric_codes is not None:
        try:
            if type_code in numeric_codes:
                return True
        except TypeError:
            pass

    if any(type_code == driver_type for driver_type in _DRIVER_NUMERIC_TYPES.get(family, ())):
        return True

    # Some DB-API drivers expose type objects/names instead of integer codes.
    type_tokens = set(re.findall(r"[a-z]+[0-9]*", str(type_code).lower()))
    return bool(type_tokens & _NUMERIC_TYPE_NAMES)


def build_fields_info_from_cursor(cursor, origin_column, db_type='postgresql'):
    """
    根据数据库游标的 description 构建字段信息列表

    Args:
        cursor: 数据库游标对象
        origin_column: 是否保留原始列名大小写
        db_type: 数据源类型；同协议的数据源会统一映射到对应驱动类型

    Returns:
        list: 包含字段名和是否数值类型的字典列表
    """
    fields_info = []

    for col_info in cursor.description:
        col_name = col_info[0]

        fields_info.append({
            "name": col_name if origin_column else col_name.lower(),
            "is_numeric": _is_numeric_cursor_type(col_info[1], db_type)
        })

    return fields_info


def build_fields_info_from_es(raw_columns, origin_column):
    """
    专门为 Elasticsearch 构建字段信息

    Args:
        raw_columns: ES 返回的列信息列表
        origin_column: 是否保留原始列名大小写

    Returns:
        list: 包含字段名和是否数值类型的字典列表
    """
    fields_info = []

    for field in raw_columns:
        field_name = field.get('name') if origin_column else field.get('name').lower()
        field_type = field.get('type', '').lower()

        is_numeric = field_type in (
            'long', 'integer', 'short', 'byte',
            'double', 'float', 'half_float', 'scaled_float',
            'unsigned_long', 'boolean'
        )

        fields_info.append({
            "name": field_name,
            "is_numeric": is_numeric
        })

    return fields_info


def get_sqlglot_dialect(ds_type: str) -> str:
    """根据数据源类型获取 sqlglot dialect"""
    if equals_ignore_case(ds_type, 'mysql', 'doris', 'starrocks'):
        return 'mysql'
    elif equals_ignore_case(ds_type, 'sqlServer'):
        return 'tsql'
    elif equals_ignore_case(ds_type, 'hive'):
        return 'hive'
    return None


# 通用危险函数（适用于所有数据库）
COMMON_DANGEROUS_FUNCTIONS = {'version', 'current_user', 'user', 'database'}

# 特定数据库的危险函数
DS_SPECIFIC_DANGEROUS_FUNCTIONS = {
    'mysql': {'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE'},
    'doris': {'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE'},
    'starrocks': {'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE'},
    'postgresql': {'pg_read_file', 'pg_write_file', 'lo_import', 'lo_export'},
    'sqlserver': {'EXEC', 'xp_cmdshell', 'sp_executesql'},
    'oracle': {'UTL_FILE', 'DBMS_PIPE', 'DBMS_LOCK'},
    'hive': {'ADD FILE', 'ADD JAR'},
}

# 危险模式正则表达式（用于检查特殊语法）
import re

DANGEROUS_PATTERNS = [
    r'\bINTO\s+OUTFILE\b',
    r'\bINTO\s+DUMPFILE\b',
    r'\bEXEC\s*\(',
    r'\bCOPY\s+.*\bTO\s+PROGRAM\b',
]


def get_dangerous_functions(ds_type: str) -> set:
    """获取危险函数（通用 + 特定数据源）"""
    functions = COMMON_DANGEROUS_FUNCTIONS.copy()
    ds_key = ds_type.lower() if ds_type else ''
    if ds_key in DS_SPECIFIC_DANGEROUS_FUNCTIONS:
        functions.update(DS_SPECIFIC_DANGEROUS_FUNCTIONS[ds_key])
    return functions


def check_dangerous_functions(statements: list, ds_type: str) -> bool:
    """检查是否使用了危险函数，返回 True 表示安全"""
    dangerous_functions = get_dangerous_functions(ds_type)
    dangerous_functions_upper = {f.upper() for f in dangerous_functions}

    for stmt in statements:
        if stmt:
            for func in stmt.find_all(exp.Anonymous):
                if func.name.upper() in dangerous_functions_upper:
                    return False
    return True


def check_sql_read(sql: str, ds: CoreDatasource | AssistantOutDsSchema) -> tuple[bool, str]:
    """
    检查 SQL 是否为安全的只读查询
    返回: (是否安全, 错误原因)
    """
    try:
        normalized_sql = sql.strip().lstrip("(").strip()
        first_keyword = normalized_sql.split(None, 1)[0].upper() if normalized_sql else ""

        # 根据配置决定是否允许元数据查询
        if settings.SQLBOT_ALLOW_METADATA_QUERIES:
            allowed_read_commands = {"SELECT", "WITH", "SHOW", "DESCRIBE", "DESC", "EXPLAIN"}
        else:
            allowed_read_commands = {"SELECT", "WITH"}

        denied_write_commands = {
            "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER",
            "TRUNCATE", "MERGE", "COPY", "REPLACE", "GRANT", "REVOKE",
            "USE", "SET", "CALL"
        }

        if not first_keyword:
            raise ValueError("Parse SQL Error")
        if first_keyword in denied_write_commands:
            return False, f"Write operation '{first_keyword}' is not allowed"

        # 1. 使用正则检查特殊模式
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return False, f"SQL contains dangerous pattern: {pattern}"

        dialect = get_sqlglot_dialect(ds.type)
        statements = sqlglot.parse(sql, dialect=dialect)

        if not statements:
            raise ValueError("Parse SQL Error")

        # 2. 使用 sqlglot 检查函数调用
        dangerous_functions = get_dangerous_functions(ds.type)
        dangerous_functions_upper = {f.upper() for f in dangerous_functions}
        for stmt in statements:
            if stmt:
                for func in stmt.find_all(exp.Anonymous):
                    if func.name.upper() in dangerous_functions_upper:
                        return False, f"SQL contains dangerous function: {func.name}"

        # 3. 检查写操作类型
        write_types = (
            exp.Insert, exp.Update, exp.Delete,
            exp.Create, exp.Drop, exp.Alter,
            exp.Merge, exp.Copy
        )

        for stmt in statements:
            if stmt is None:
                continue
            if isinstance(stmt, write_types):
                return False, f"SQL contains write operation: {type(stmt).__name__}"

        if first_keyword not in allowed_read_commands:
            return False, f"SQL command '{first_keyword}' is not allowed. Only SELECT and WITH are permitted"

        return True, ""

    except Exception as e:
        raise ValueError(f"Parse SQL Error: {e}")


def checkParams(extraParams: str, illegalParams: List[str]):
    kvs = extraParams.split('&')
    for kv in kvs:
        if kv and '=' in kv:
            k, v = kv.split('=')
            if k in illegalParams:
                raise HTTPException(status_code=500, detail=f'Illegal Parameter: {k}')
