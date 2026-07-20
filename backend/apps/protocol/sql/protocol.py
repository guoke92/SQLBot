"""SQL protocol — wraps existing DB layer with zero new behavior.

Delegates to `apps.db.db` for connection, execution, safety, schema discovery.
All prompt/template logic stays here for protocol-level isolation.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import orjson
import sqlparse

from apps.protocol.base import (
    CAP_ROW_PERMISSION,
    CAP_SAMPLE_DATA,
    CAP_SQL_DIALECT,
    CAP_TABLE_RELATION,
    BaseProtocol,
    PromptBundle,
    QueryPlan,
    QueryResult,
    SchemaSnapshot,
)


def _extract_nested_json(text: str) -> Optional[str]:
    """Locate the outermost JSON object in *text* (may include markdown fences)."""
    text = text.strip()
    if text.startswith("```"):
        # Strip markdown code fence
        fence_end = text.find("```", 3)
        if fence_end > 0:
            text = text[3:fence_end].strip()
            if text.startswith("json"):
                text = text[4:].strip()
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


class SqlProtocol(BaseProtocol):
    """Protocol implementation backed by SQL datasources.

    All heavy lifting delegated to existing `apps.db.db` / `apps.datasource.crud.datasource`.
    """

    def __init__(self, type_key: str) -> None:
        self.type_key = type_key

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def check_connection(self, ds: Any, trans: Any = None, is_raise: bool = False) -> bool:
        from apps.db.db import check_connection

        return check_connection(trans, ds, is_raise)

    # ------------------------------------------------------------------
    # Schema discovery
    # ------------------------------------------------------------------

    def get_tables(self, ds: Any) -> List[Any]:
        from apps.db.db import get_tables

        return get_tables(ds)

    def get_fields(self, ds: Any, table_name: str) -> List[Any]:
        from apps.db.db import get_fields

        return get_fields(ds, table_name)

    def retrieve_schema(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        question: str,
        *,
        embedding: bool = True,
        out_ds_instance: Any = None,
        resource_names: Optional[Sequence[str]] = None,
    ) -> SchemaSnapshot:
        from apps.datasource.crud.datasource import get_table_schema, get_tables_sample_data

        table_list = list(resource_names) if resource_names is not None else None

        if out_ds_instance is not None:
            # Out-DS does not run table vector ranking (assistant get_db_schema
            # embedding path is intentionally inactive). resource filter only.
            if table_list is not None:
                schema_text, names = out_ds_instance.get_db_schema(
                    ds.id, question, table_list=table_list
                )
            else:
                schema_text, names = out_ds_instance.get_db_schema(ds.id, question)
            sample_data = ""
        else:
            schema_text, names = get_table_schema(
                session=session,
                current_user=current_user,
                ds=ds,
                question=question,
                embedding=embedding,
                table_list=table_list,
            )
            sample_data = get_tables_sample_data(
                session=session, current_user=current_user, ds=ds, table_list=names
            )

        return SchemaSnapshot(
            schema_text=schema_text,
            resource_names=list(names),
            sample_data=sample_data,
        )

    # ------------------------------------------------------------------
    # Prompt assembly
    # ------------------------------------------------------------------

    def build_prompt_bundle(self, chat_question: Any, *, enable_query_limit: bool = True) -> PromptBundle:
        from apps.template.generate_sql.generator import get_sql_template, get_sql_example_template

        q = chat_question
        sql_template = get_sql_example_template(getattr(q, "_ds_type", "pg"))
        base_template = get_sql_template()

        process_check = sql_template.get("process_check") or base_template["process_check"]
        query_limit = base_template["query_limit"] if enable_query_limit else base_template["no_query_limit"]
        other_rule = sql_template["other_rule"].format(
            multi_table_condition=base_template["multi_table_condition"]
        )
        base_sql_rules = (
            sql_template["quot_rule"] + query_limit + sql_template["limit_rule"] + other_rule
        )

        system = base_template["system"].format(lang=q.lang, process_check=process_check, sqlbot_name=q.sqlbot_name)
        rules = base_template["generate_rules"].format(
            lang=q.lang,
            sqlbot_name=q.sqlbot_name,
            base_sql_rules=base_sql_rules,
            basic_sql_examples=sql_template["basic_example"],
            example_engine=sql_template["example_engine"],
            example_answer_1=sql_template["example_answer_1_with_limit"] if enable_query_limit else sql_template["example_answer_1"],
            example_answer_2=sql_template["example_answer_2_with_limit"] if enable_query_limit else sql_template["example_answer_2"],
            example_answer_3=sql_template["example_answer_3_with_limit"] if enable_query_limit else sql_template["example_answer_3"],
        )
        schema = base_template["generate_basic_info"].format(
            engine=q.engine, schema=q.db_schema, sample_data=q.sample_data
        )

        bundle = PromptBundle(
            system=system, rules=rules, schema=schema,
            ack_rules="我已掌握所有规则，包括表结构、SQL规范、安全限制和输出格式，我会严格遵守这些规则。",
            ack_schema="我已确认您提供的数据库信息与表结构schema，我生成的SQL不会超出您提供的范围。",
            ack_data_training="我已确认您提供的SQL示例，我会进行参考。",
        )

        if getattr(q, "terminologies", ""):
            bundle.terminologies = base_template["generate_terminologies_info"].format(terminologies=q.terminologies)
        if getattr(q, "data_training", ""):
            bundle.data_training = base_template["generate_data_training_info"].format(data_training=q.data_training)
        if getattr(q, "custom_prompt", ""):
            bundle.custom_prompt = base_template["generate_custom_prompt_info"].format(custom_prompt=q.custom_prompt)

        return bundle

    def build_user_prompt(self, chat_question: Any, *, current_time: str, change_title: bool) -> str:
        from apps.template.generate_sql.generator import get_sql_template

        q = chat_question
        question = q.question
        if getattr(q, "regenerate_record_id", None):
            question = get_sql_template()["regenerate_hint"] + q.question
        return get_sql_template()["user"].format(
            lang=q.lang, engine=q.engine, schema=q.db_schema,
            question=question, rule=q.rule, current_time=current_time,
            error_msg=getattr(q, "error_msg", ""), change_title=change_title,
        )

    # ------------------------------------------------------------------
    # Parse / validate / execute
    # ------------------------------------------------------------------

    def parse_llm_output(self, text: str) -> QueryPlan:
        json_str = _extract_nested_json(text)
        if json_str is None:
            return QueryPlan(success=False, message="SQL answer is not a valid json object", statement="", payload={})
        try:
            data = orjson.loads(json_str)
        except Exception:
            return QueryPlan(success=False, message="Cannot parse sql from answer", statement="", payload={})

        if not data.get("success"):
            return QueryPlan(success=False, message=data.get("message", "Unknown error"), statement="", payload={})

        sql = data.get("sql", "")
        if not sql or not sql.strip():
            return QueryPlan(success=False, message="SQL query is empty", statement="", payload={})

        return QueryPlan(
            success=True,
            statement=sql.strip().rstrip(";"),
            payload={"sql": sql.strip().rstrip(";")},
            resources=data.get("tables") or [],
            chart_type=data.get("chart-type"),
            brief=data.get("brief"),
        )

    def validate_plan(self, ds: Any, plan: QueryPlan, allowed_resources: Sequence[str]) -> QueryPlan:
        from apps.protocol.registry import get_spec
        from apps.db.db import check_sql_read, get_sqlglot_dialect
        import sqlglot as _sg
        from sqlglot import exp as _exp

        sql = plan.payload.get("sql", "")
        if not sql:
            return plan

        is_safe, reason = check_sql_read(sql, ds)
        if not is_safe:
            return QueryPlan(success=False, message=f"SQL safety check failed: {reason}", statement=sql, payload=plan.payload)

        # Table name allow-list check
        spec = get_spec(self.type_key)
        dialect = spec.sqlglot_dialect
        actual_tables: set = set()
        try:
            statements = _sg.parse(sql, dialect=dialect)
            for stmt in statements:
                if stmt:
                    for table in stmt.find_all(_exp.Table):
                        if table.name:
                            actual_tables.add(table.name)
        except Exception:
            pass

        if actual_tables and allowed_resources:
            allowed_set = set(allowed_resources)
            unauthorized = actual_tables - allowed_set
            if unauthorized:
                return QueryPlan(
                    success=False,
                    message=f"SQL contains unauthorized tables: {', '.join(unauthorized)}. Allowed: {', '.join(allowed_set)}",
                    statement=sql,
                    payload=plan.payload,
                )

        return plan

    def execute(self, ds: Any, plan: QueryPlan, *, origin_column: bool = False) -> QueryResult:
        from apps.db.db import exec_sql

        sql = plan.payload.get("sql", "")
        raw = exec_sql(ds=ds, sql=sql, origin_column=origin_column)
        return QueryResult(
            fields=raw.get("fields", []),
            data=raw.get("data", []),
            fields_info=raw.get("fields_info"),
            raw=raw,
            statement=sql,
            re_exec={"sql": sql},
        )

    def plan_from_re_exec(self, ds: Any, re_exec: Dict[str, Any]) -> Optional[QueryPlan]:
        if not re_exec:
            return None
        sql = (re_exec.get("sql") or "").strip()
        if not sql:
            return None
        return QueryPlan(success=True, statement=sql, payload={"sql": sql})

    def preview(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        table_name: str,
        fields: Sequence[str],
        *,
        where: str = "",
        limit: int = 100,
    ) -> QueryResult:
        from apps.db.db import exec_sql
        from apps.protocol.registry import get_spec

        spec = get_spec(self.type_key)
        pre = spec.quote_prefix
        suf = spec.quote_suffix
        schema = getattr(ds, "_preview_schema", "")

        where_clause = f" WHERE {where}" if where else ""

        type_key = self.type_key
        if type_key in ("mysql", "doris", "starrocks", "hive"):
            col_list = ", ".join(f"`{f}`" for f in fields)
            if schema:
                from_clause = f"`{schema}`.`{table_name}`"
            else:
                from_clause = f"`{table_name}`"
            sql = f"SELECT {col_list} FROM {from_clause}{where_clause} LIMIT {limit}"
        elif type_key == "sqlServer":
            col_list = ", ".join(f"[{f}]" for f in fields)
            if schema:
                from_clause = f"[{schema}].[{table_name}]"
            else:
                from_clause = f"[{table_name}]"
            sql = f"SELECT TOP {limit} {col_list} FROM {from_clause}{where_clause}"
        elif type_key in ("ck",):
            col_list = ", ".join(f'"{f}"' for f in fields)
            sql = f'SELECT {col_list} FROM "{table_name}"{where_clause} LIMIT {limit}'
        elif type_key in ("oracle",):
            col_list = ", ".join(f'"{f}"' for f in fields)
            if schema:
                from_clause = f'"{schema}"."{table_name}"'
            else:
                from_clause = f'"{table_name}"'
            if fields:
                sql = (
                    f"SELECT * FROM (SELECT {col_list} FROM {from_clause}{where_clause} "
                    f'ORDER BY "{fields[0]}") WHERE ROWNUM <= {limit}'
                )
            else:
                sql = f"SELECT * FROM {from_clause}{where_clause} WHERE ROWNUM <= {limit}"
        else:
            # pg, excel, redshift, kingbase, dm default
            col_list = ", ".join(f'"{f}"' for f in fields)
            if schema:
                from_clause = f'"{schema}"."{table_name}"'
            else:
                from_clause = f'"{table_name}"'
            sql = f"SELECT {col_list} FROM {from_clause}{where_clause} LIMIT {limit}"

        raw = exec_sql(ds, sql, True)
        return QueryResult(
            fields=raw.get("fields", []),
            data=raw.get("data", []),
            fields_info=raw.get("fields_info"),
            raw=raw,
            statement=sql,
            re_exec={"sql": sql},
        )

    def format_statement_for_display(self, plan: QueryPlan) -> str:
        sql = plan.payload.get("sql", plan.statement)
        if sql:
            return sqlparse.format(sql, reindent=True)
        return plan.statement or ""

    def engine_display_name(self, ds: Any) -> str:
        # Prefer host DB catalog name ("MySQL"), not internal type_key ("mysql").
        # Do not reuse existing type_name here — create/update must be authoritative.
        from apps.db.constant import DB

        try:
            return DB.get_db(getattr(ds, "type", None) or self.type_key).db_name
        except Exception:
            type_name = getattr(ds, "type_name", None)
            if type_name:
                return str(type_name)
            return self.type_key

    def server_version(self, ds: Any) -> str:
        from apps.db.db import get_version

        try:
            return get_version(ds) or ""
        except Exception:
            return ""

    def schema_namespace(self, ds: Any) -> str:
        import json

        from apps.datasource.models.datasource import DatasourceConf
        from apps.datasource.utils.utils import aes_decrypt
        from apps.db.engine import get_engine_config

        try:
            if self.type_key == "excel":
                conf = get_engine_config()
            else:
                conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
            if conf.dbSchema is not None and conf.dbSchema != "":
                return conf.dbSchema
            return conf.database or ""
        except Exception:
            return ""