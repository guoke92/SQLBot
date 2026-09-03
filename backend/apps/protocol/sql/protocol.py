"""SQL protocol — owns SQL-specific schema, validation, and execution.

Database primitives remain delegated to ``apps.db.db`` while dialect syntax
and physical-resource validation stay behind this protocol boundary.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import orjson
import sqlparse

from apps.protocol.base import (
    BaseProtocol,
    DictionaryExtractResult,
    PromptBundle,
    QueryPlan,
    QueryResult,
    SchemaSnapshot,
)
from common.utils.json_utils import extract_nested_json


def rewrite_identifier_quotes(
    sql: str,
    *,
    dialect: str | None,
    quote_prefix: str,
) -> str:
    """Re-emit SQL with the connector's identifier quotes.

    Model output often copies Postgres ``"ident"`` onto MySQL-family dialects
    (StarRocks / Doris / Hive). Parse with a quote-tolerant dialect and generate
    with the target sqlglot dialect so execute sees legal SQL.
    """
    if not sql or not dialect:
        return sql
    import sqlglot
    from sqlglot.errors import ParseError

    read_order: list[str] = []
    if '"' in sql and quote_prefix != '"':
        read_order.append("postgres")
    if dialect not in read_order:
        read_order.append(dialect)
    for read in read_order:
        try:
            parsed = sqlglot.parse_one(sql, dialect=read)
        except ParseError:
            continue
        except Exception:
            continue
        try:
            return parsed.sql(dialect=dialect)
        except Exception:
            continue
    return sql


class SqlProtocol(BaseProtocol):
    """Protocol implementation backed by SQL datasources.

    All heavy lifting delegated to existing `apps.db.db` / `apps.datasource.crud.datasource`.
    """

    def __init__(self, type_key: str) -> None:
        self.type_key = type_key

    def normalize_configuration(
        self,
        configuration: Mapping[str, Any],
    ) -> dict[str, Any]:
        from apps.datasource.models.datasource import DatasourceConf

        unknown = sorted(set(configuration) - set(DatasourceConf.model_fields))
        if unknown:
            raise ValueError(
                "Unsupported SQL datasource configuration field(s): "
                f"{', '.join(unknown)}. Use canonical fields such as 'username', "
                "not aliases such as 'user'."
            )
        conf = DatasourceConf.model_validate(dict(configuration))
        # Scope sync is StarRocks/Doris-only — do not mutate shared Conf for other engines.
        if self.type_key in ("doris", "starrocks"):
            from apps.db.starrocks_catalog import sync_conf_scope

            sync_conf_scope(conf)
        return conf.model_dump()

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def check_connection(
        self, ds: Any, trans: Any = None, is_raise: bool = False
    ) -> bool:
        from apps.db.db import check_connection

        return check_connection(trans, ds, is_raise)

    # ------------------------------------------------------------------
    # Schema discovery
    # ------------------------------------------------------------------

    def get_tables(self, ds: Any) -> list[Any]:
        from apps.db.db import get_tables

        return get_tables(ds)

    def get_fields(
        self, ds: Any, table_name: str, database_name: str | None = None
    ) -> list[Any]:
        from apps.db.db import get_fields

        return get_fields(ds, table_name, database_name=database_name)

    def retrieve_schema(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        question: str,
        *,
        embedding: bool = True,
        out_ds_instance: Any = None,
        resource_names: Sequence[str] | None = None,
        required_resource_names: Sequence[str] = (),
        access_scope: Any = None,
        table_limit: int | None = None,
    ) -> SchemaSnapshot:
        from apps.datasource.access import project_schema_resources
        from apps.datasource.crud.datasource import (
            get_table_schema,
            get_tables_sample_data,
        )

        table_list = project_schema_resources(resource_names, access_scope)

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
                required_table_list=list(required_resource_names),
                table_limit=table_limit,
            )
            sample_data = get_tables_sample_data(
                session=session,
                current_user=current_user,
                ds=ds,
                table_list=names,
            )

        return SchemaSnapshot(
            schema_text=schema_text,
            resource_names=list(names),
            sample_data=sample_data,
        )

    # ------------------------------------------------------------------
    # Prompt assembly
    # ------------------------------------------------------------------

    def build_prompt_bundle(
        self, chat_question: Any, *, enable_query_limit: bool = True
    ) -> PromptBundle:
        from apps.chat.plan_policy import ROW_LIMIT
        from apps.template.generate_sql.generator import (
            get_sql_example_template,
            get_sql_template,
        )

        q = chat_question
        sql_template = get_sql_example_template(self.type_key)
        base_template = get_sql_template()

        process_check = (
            sql_template.get("process_check") or base_template["process_check"]
        )
        query_limit = (
            base_template["query_limit"].format(row_limit=ROW_LIMIT)
            if enable_query_limit
            else base_template["no_query_limit"]
        )
        other_rule = sql_template["other_rule"].format(
            multi_table_condition=base_template["multi_table_condition"]
        )
        base_sql_rules = (
            sql_template["quot_rule"]
            + query_limit
            + sql_template["limit_rule"]
            + other_rule
        )

        system = base_template["system"].format(
            lang=q.lang, process_check=process_check, sqlbot_name=q.sqlbot_name
        )
        rules = base_template["generate_rules"].format(
            lang=q.lang,
            sqlbot_name=q.sqlbot_name,
            base_sql_rules=base_sql_rules,
            basic_sql_examples=sql_template["basic_example"],
            example_engine=sql_template["example_engine"],
            example_answer_1=sql_template["example_answer_1_with_limit"]
            if enable_query_limit
            else sql_template["example_answer_1"],
            example_answer_2=sql_template["example_answer_2_with_limit"]
            if enable_query_limit
            else sql_template["example_answer_2"],
            example_answer_3=sql_template["example_answer_3_with_limit"]
            if enable_query_limit
            else sql_template["example_answer_3"],
        )
        schema = base_template["generate_basic_info"].format(
            engine=q.engine, schema=q.db_schema, sample_data=q.sample_data
        )

        bundle = PromptBundle(
            system=system,
            rules=rules,
            schema_text=schema,
            ack_rules="我已掌握所有规则，包括表结构、SQL规范、安全限制和输出格式，我会严格遵守这些规则。",
            ack_schema="我已确认您提供的数据库信息与表结构schema，我生成的SQL不会超出您提供的范围。",
            ack_data_training="我已确认您提供的SQL示例，我会进行参考。",
        )

        if getattr(q, "terminologies", ""):
            bundle.terminologies = base_template["generate_terminologies_info"].format(
                terminologies=q.terminologies
            )
        if getattr(q, "data_training", ""):
            bundle.data_training = base_template["generate_data_training_info"].format(
                data_training=q.data_training
            )
        if getattr(q, "custom_prompt", ""):
            bundle.custom_prompt = base_template["generate_custom_prompt_info"].format(
                custom_prompt=q.custom_prompt
            )

        return bundle

    def build_user_prompt(
        self, chat_question: Any, *, current_time: str, change_title: bool
    ) -> str:
        from apps.template.generate_sql.generator import get_sql_template

        q = chat_question
        question = getattr(q, "generation_question", "") or q.question
        if getattr(q, "regenerate_record_id", None):
            question = get_sql_template()["regenerate_hint"] + question
        user = get_sql_template()["user"]
        return user.format(
            lang=q.lang,
            engine=q.engine,
            schema=q.db_schema,
            question=question,
            rule=q.rule,
            current_time=current_time,
            error_msg=getattr(q, "error_msg", ""),
            change_title=change_title,
        )

    # ------------------------------------------------------------------
    # Parse / validate / execute
    # ------------------------------------------------------------------

    def parse_llm_output(self, text: str) -> QueryPlan:
        json_str = extract_nested_json(text)
        if json_str is None:
            return QueryPlan(
                success=False,
                message="SQL answer is not a valid json object",
                statement="",
                payload={},
            )
        try:
            data = orjson.loads(json_str)
        except Exception:
            return QueryPlan(
                success=False,
                message="Cannot parse sql from answer",
                statement="",
                payload={},
            )

        if not data.get("success"):
            return QueryPlan(
                success=False,
                message=data.get("message", "Unknown error"),
                statement="",
                payload={},
            )

        sql = data.get("sql", "")
        if not sql or not sql.strip():
            return QueryPlan(
                success=False, message="SQL query is empty", statement="", payload={}
            )

        return QueryPlan(
            success=True,
            statement=sql.strip().rstrip(";"),
            payload={"sql": sql.strip().rstrip(";")},
            resources=data.get("tables") or [],
            chart_type=data.get("chart-type"),
            brief=data.get("brief"),
        )

    def parse_candidate_payload(self, payload: Mapping[str, Any]) -> QueryPlan:
        sql = str(payload.get("sql") or "").strip().rstrip(";")
        if not sql:
            return QueryPlan(
                success=False,
                message="SQL query is empty",
                statement="",
                payload={},
            )
        return QueryPlan(
            success=True,
            statement=sql,
            payload={"sql": sql},
            resources=list(payload.get("tables") or []),
            chart_type=payload.get("chart-type") or payload.get("chart_type"),
            brief=payload.get("brief"),
        )

    def validate_plan(
        self, ds: Any, plan: QueryPlan, allowed_resources: Sequence[str]
    ) -> QueryPlan:
        """Safety + table allow-list + physical-column catalog check.

        Column validation uses CoreField (same catalog as schema prompts).
        Only **physical** table columns are checked. SELECT aliases referenced
        again in GROUP BY / ORDER BY / HAVING (e.g. ``AS month`` then
        ``GROUP BY month``) are not table columns and must not be rejected.
        """
        from apps.db.db import check_sql_read
        from apps.protocol.registry import get_spec
        from apps.protocol.sql.identifier_validation import (
            PhysicalColumnRef,
            collect_sql_identifier_usage,
            order_by_scope_error,
        )

        sql = plan.payload.get("sql", "")
        if not sql:
            return plan

        spec = get_spec(self.type_key)
        dialect = spec.sqlglot_dialect
        rewritten = rewrite_identifier_quotes(
            sql, dialect=dialect, quote_prefix=spec.quote_prefix
        )
        if rewritten != sql:
            sql = rewritten
            plan = plan.model_copy(
                deep=True,
                update={
                    "statement": sql,
                    "payload": {**(plan.payload or {}), "sql": sql},
                },
            )

        def reject(message: str) -> QueryPlan:
            """Preserve plan metadata while marking validation failure."""
            return plan.model_copy(
                deep=True,
                update={
                    "success": False,
                    "message": message,
                    "statement": sql,
                },
            )

        is_safe, reason = check_sql_read(sql, ds)
        if not is_safe:
            return reject(f"SQL safety check failed: {reason}")

        actual_tables: set[str] = set()
        physical_cols: tuple[PhysicalColumnRef, ...] = ()
        order_by_problem = order_by_scope_error(sql, dialect)
        if order_by_problem:
            return reject(order_by_problem)

        try:
            usage = collect_sql_identifier_usage(sql, dialect)
            actual_tables = set(usage.physical_tables)
            physical_cols = usage.physical_columns
        except Exception as exc:
            return reject(f"SQL identifier validation failed: {exc}")

        validated_plan = plan.model_copy(deep=True)
        if actual_tables:
            # Physical resources are derived from the SQL AST. Model-declared
            # `tables` are advisory and must not drive permission/schema paths.
            validated_plan.resources = sorted(actual_tables)

        if actual_tables and allowed_resources:
            allowed_set = set(allowed_resources)
            unauthorized = actual_tables - allowed_set
            if unauthorized:
                return reject(
                    f"SQL contains unauthorized tables: "
                    f"{', '.join(sorted(unauthorized))}. "
                    f"Allowed: {', '.join(sorted(allowed_set))}"
                )

        ds_id = getattr(ds, "id", None)
        if not (ds_id and physical_cols and actual_tables):
            return validated_plan

        try:
            from sqlmodel import Session, select

            from apps.datasource.models.datasource import (
                CoreField,
                CoreTable,
                table_identity_key,
            )
            from common.core.db import engine as _sqlbot_engine

            table_names = sorted(actual_tables)
            with Session(_sqlbot_engine) as session:
                tables = session.exec(
                    select(CoreTable).where(
                        CoreTable.ds_id == ds_id,
                        CoreTable.table_name.in_(table_names),
                    )
                ).all()
                catalog_tables = [t for t in tables if t.id is not None]
                if not catalog_tables:
                    return validated_plan

                fields = session.exec(
                    select(CoreField).where(
                        CoreField.table_id.in_([t.id for t in catalog_tables])
                    )
                ).all()
                id_to_key = {t.id: table_identity_key(t) for t in catalog_tables}
                fields_by_key: dict[tuple[str, str], set[str]] = {
                    table_identity_key(t): set() for t in catalog_tables
                }
                orig_by_key: dict[tuple[str, str], list[str]] = {
                    table_identity_key(t): [] for t in catalog_tables
                }
                for f in fields:
                    key = id_to_key.get(f.table_id)
                    if not key or not f.field_name:
                        continue
                    fields_by_key[key].add(f.field_name)
                    fields_by_key[key].add(f.field_name.lower())
                    orig_by_key[key].append(f.field_name)

                def _lookup_fields(
                    table_name: str,
                    database_name: str | None,
                ) -> tuple[str, str] | None:
                    """Return identity key for a SQL table ref, or None to skip."""
                    db = (database_name or "").strip()
                    if db:
                        key = (db, table_name)
                        return key if key in fields_by_key else None
                    matches = [k for k in fields_by_key if k[1] == table_name]
                    if len(matches) == 1:
                        return matches[0]
                    # Missing or ambiguous across databases — do not guess.
                    return None

                def _display_key(key: tuple[str, str]) -> str:
                    db, name = key
                    return f"{db}.{name}" if db else name

                missing: list[str] = []
                for ref in physical_cols:
                    cname = ref.column_name
                    c_raw, c_l = cname, cname.lower()
                    if ref.table_name:
                        key = _lookup_fields(ref.table_name, ref.database_name)
                        if key is None:
                            continue
                        allowed_cols = fields_by_key[key]
                        if c_raw not in allowed_cols and c_l not in allowed_cols:
                            missing.append(f"{_display_key(key)}.{c_raw}")
                    else:
                        candidate_keys: list[tuple[str, str] | None] = []
                        dbs = ref.candidate_databases
                        for i, table_name in enumerate(ref.candidate_tables):
                            db = dbs[i] if i < len(dbs) else ""
                            candidate_keys.append(
                                _lookup_fields(table_name, db or None)
                            )
                        # Skip when a source is absent / ambiguous in the local
                        # catalog; otherwise an unqualified reference is too
                        # unreliable for a rejection.
                        if not candidate_keys or any(
                            key is None for key in candidate_keys
                        ):
                            continue
                        if any(
                            c_raw in fields_by_key[key] or c_l in fields_by_key[key]
                            for key in candidate_keys
                            if key is not None
                        ):
                            continue
                        missing.append(c_raw)

                if missing:
                    uniq: list[str] = []
                    seen: set[str] = set()
                    for m in missing:
                        if m not in seen:
                            seen.add(m)
                            uniq.append(m)
                    hints: list[str] = []
                    hinted_keys: set[tuple[str, str]] = set()
                    for m in uniq[:6]:
                        if "." not in m:
                            continue
                        # m is "db.table.col" or "table.col"
                        parts = m.rsplit(".", 1)
                        prefix, _col = parts[0], parts[1]
                        if "." in prefix:
                            db, tn = prefix.split(".", 1)
                            key = (db, tn)
                        else:
                            key = _lookup_fields(prefix, None)
                            if key is None:
                                continue
                        if key in hinted_keys or key not in orig_by_key:
                            continue
                        orig = sorted(set(orig_by_key.get(key) or []))
                        if orig:
                            hint = f"{_display_key(key)}: {', '.join(orig[:12])}"
                            if len(orig) > 12:
                                hint += "…"
                            hints.append(hint)
                            hinted_keys.add(key)
                    msg = (
                        "SQL references unknown column(s): "
                        + ", ".join(uniq)
                        + ". Use only columns from the provided schema "
                        "(SELECT aliases in GROUP BY/ORDER BY are allowed)."
                    )
                    if hints:
                        msg += " Catalog samples — " + " | ".join(hints)
                    return reject(msg)
        except Exception as exc:
            return reject(f"SQL catalog validation failed: {exc}")

        # ── Cost gates (catalog stats + structure + EXPLAIN) ──
        try:
            from sqlmodel import Session

            from apps.chat.plan_policy import LARGE_TABLE_ROWS
            from apps.datasource.crud.catalog_stats import load_table_stats_for_ds
            from apps.protocol.sql.cost_validate import (
                check_multi_fact_fanout,
                explain_cost_too_high,
            )
            from common.core.db import engine as _sqlbot_engine

            stats_by_table: dict = {}
            ds_id = getattr(ds, "id", None)
            if ds_id and actual_tables:
                with Session(_sqlbot_engine) as _sess:
                    stats_by_table = load_table_stats_for_ds(
                        _sess, int(ds_id), list(actual_tables)
                    )
            fan = check_multi_fact_fanout(sql, dialect or "mysql", stats_by_table)
            if fan:
                return reject(fan)
            # EXPLAIN can be relatively expensive; only when multiple tables or large facts
            need_explain = len(actual_tables) >= 3 or any(
                (stats_by_table.get(n) or {}).get("approx_rows")
                and int((stats_by_table.get(n) or {}).get("approx_rows") or 0)
                >= LARGE_TABLE_ROWS
                for n in actual_tables
            )
            if need_explain:
                exp_msg = explain_cost_too_high(ds, sql)
                if exp_msg:
                    return reject(exp_msg)
        except Exception as exc:
            # Cost estimation is advisory. Safety/catalog validation above has
            # already completed and must never be skipped by this branch.
            from common.utils.utils import SQLBotLogUtil

            SQLBotLogUtil.warning(f"SQL cost validation skipped: {exc}")

        return validated_plan

    def execute(
        self,
        ds: Any,
        plan: QueryPlan,
        *,
        origin_column: bool = False,
        max_rows: int | None = None,
    ) -> QueryResult:
        from apps.db.db import exec_sql

        sql = plan.payload.get("sql", "")
        raw = exec_sql(
            ds=ds,
            sql=sql,
            origin_column=origin_column,
            max_rows=max_rows,
        )
        return QueryResult(
            fields=raw.get("fields", []),
            data=raw.get("data", []),
            fields_info=raw.get("fields_info"),
            raw=raw,
            statement=sql,
            re_exec={"sql": sql},
            truncated=bool(raw.get("truncated")),
            limit=raw.get("limit"),
            truncation_reason=raw.get("truncation_reason"),
        )

    def _quote_identifier(self, identifier: str) -> str:
        from apps.protocol.registry import get_spec

        spec = get_spec(self.type_key)
        escaped = identifier.replace(spec.quote_suffix, spec.quote_suffix * 2)
        return f"{spec.quote_prefix}{escaped}{spec.quote_suffix}"

    def qualify_table(
        self,
        ds: Any,
        table_name: str,
        *,
        database_name: str | None = None,
    ) -> str:
        """Build a dialect-quoted FROM target for ``table_name``."""
        import json

        from apps.datasource.models.datasource import DatasourceConf
        from apps.datasource.utils.utils import aes_decrypt

        if self.type_key in ("doris", "starrocks"):
            from apps.db.starrocks_catalog import qualified_table, resolve_sr_scope

            conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
            catalog, databases = resolve_sr_scope(conf)
            db = (database_name or "").strip() or (databases[0] if databases else "")
            return qualified_table(
                catalog, db, table_name, include_catalog=bool(catalog)
            )

        schema = self.schema_namespace(ds)
        table_sql = self._quote_identifier(table_name)
        if schema:
            return f"{self._quote_identifier(schema)}.{table_sql}"
        return table_sql

    def table_prompt_label(
        self,
        ds: Any,
        table_name: str,
        *,
        database_name: str | None = None,
    ) -> str:
        """Unquoted table label for m-schema prompts (aligned with qualify_table)."""
        import json

        from apps.datasource.models.datasource import DatasourceConf
        from apps.datasource.utils.utils import aes_decrypt

        if self.type_key in ("doris", "starrocks"):
            from apps.db.starrocks_catalog import resolve_sr_scope, table_label

            conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
            catalog, databases = resolve_sr_scope(conf)
            db = (database_name or "").strip() or (databases[0] if databases else "")
            return table_label(catalog if catalog else "", db, table_name)

        schema = self.schema_namespace(ds)
        if schema and self.type_key not in (
            "mysql",
            "es",
            "sqlite",
            "hive",
            "doris",
            "starrocks",
        ):
            return f"{schema}.{table_name}"
        if database_name:
            return f"{database_name}.{table_name}"
        return table_name

    def extract_dictionary_values(
        self,
        ds: Any,
        *,
        resource: str,
        field: str,
        limit: int,
        database_name: str | None = None,
    ) -> DictionaryExtractResult:
        """Return a limit+1 DISTINCT snapshot using dialect-owned syntax."""
        from apps.db.db import exec_sql

        if not resource or not field:
            return DictionaryExtractResult()
        bounded_limit = max(1, min(int(limit), 5000))
        fetch_limit = bounded_limit + 1
        table_sql = self.qualify_table(ds, resource, database_name=database_name)
        field_sql = self._quote_identifier(field)
        where_sql = f"{field_sql} IS NOT NULL AND TRIM({field_sql}) <> ''"
        if self.type_key == "sqlServer":
            sql = (
                f"SELECT DISTINCT TOP {fetch_limit} {field_sql} AS v "
                f"FROM {table_sql} WHERE {where_sql}"
            )
        elif self.type_key == "oracle":
            sql = (
                f"SELECT DISTINCT {field_sql} AS v FROM {table_sql} "
                f"WHERE {where_sql} FETCH FIRST {fetch_limit} ROWS ONLY"
            )
        else:
            sql = (
                f"SELECT DISTINCT {field_sql} AS v FROM {table_sql} "
                f"WHERE {where_sql} LIMIT {fetch_limit}"
            )
        raw = exec_sql(ds=ds, sql=sql, origin_column=True)
        values: list[str] = []
        for row in raw.get("data") or []:
            if not isinstance(row, dict):
                continue
            value = row.get("v")
            if value is None and row:
                value = next(iter(row.values()), None)
            if value is not None and str(value).strip():
                values.append(str(value).strip())
        unique_values = list(dict.fromkeys(values))
        return DictionaryExtractResult(
            values=unique_values[:bounded_limit],
            truncated=len(unique_values) > bounded_limit,
            statement=sql,
        )

    def profile_field(
        self,
        ds: Any,
        *,
        resource: str,
        field: str,
        field_type: str | None = None,
        database_name: str | None = None,
        sample_limit: int = 5000,
        top_k: int = 20,
    ) -> Any:
        """Sample-bounded null/ndv/min/max/topk profile for one column."""
        from apps.db.db import exec_sql
        from apps.protocol.base import FieldProfileResult

        if not resource or not field:
            return FieldProfileResult(
                supported=False, field_name=field or "", error="missing target"
            )
        if self.type_key in ("es", "api"):
            return FieldProfileResult(
                supported=False, field_name=field, error="unsupported dialect"
            )

        table_sql = self.qualify_table(ds, resource, database_name=database_name)
        field_sql = self._quote_identifier(field)
        bounded = max(100, min(int(sample_limit), 20000))
        k = max(1, min(int(top_k), 50))

        # Prefer a bounded sample subquery so large facts do not full-scan.
        if self.type_key == "sqlServer":
            sample_sql = f"(SELECT TOP {bounded} {field_sql} AS v FROM {table_sql}) s"
        elif self.type_key == "oracle":
            sample_sql = (
                f"(SELECT {field_sql} AS v FROM {table_sql} "
                f"FETCH FIRST {bounded} ROWS ONLY) s"
            )
        else:
            sample_sql = f"(SELECT {field_sql} AS v FROM {table_sql} LIMIT {bounded}) s"

        agg_sql = (
            f"SELECT COUNT(*) AS row_count, "
            f"COUNT(v) AS non_null_count, "
            f"COUNT(DISTINCT v) AS approx_distinct, "
            f"MIN(v) AS min_value, MAX(v) AS max_value "
            f"FROM {sample_sql}"
        )
        try:
            raw = exec_sql(ds=ds, sql=agg_sql, origin_column=True)
        except Exception as exc:
            return FieldProfileResult(
                supported=True,
                field_name=field,
                error=str(exc)[:500],
                statement=agg_sql,
            )

        row = (raw.get("data") or [{}])[0] if raw.get("data") else {}
        row_count = int(row.get("row_count") or 0)
        non_null = int(row.get("non_null_count") or 0)
        approx_distinct = int(row.get("approx_distinct") or 0)
        null_rate = ((row_count - non_null) / row_count) if row_count > 0 else None
        distinct_ratio = (approx_distinct / non_null) if non_null > 0 else None
        min_value = row.get("min_value")
        max_value = row.get("max_value")

        top_values: list[dict[str, Any]] = []
        top_sql = (
            f"SELECT v, COUNT(*) AS c FROM {sample_sql} "
            f"WHERE v IS NOT NULL GROUP BY v ORDER BY c DESC"
        )
        if self.type_key == "sqlServer":
            top_sql = (
                f"SELECT TOP {k} v, COUNT(*) AS c FROM {sample_sql} "
                f"WHERE v IS NOT NULL GROUP BY v ORDER BY c DESC"
            )
        elif self.type_key == "oracle":
            top_sql = (
                f"SELECT v, COUNT(*) AS c FROM {sample_sql} "
                f"WHERE v IS NOT NULL GROUP BY v ORDER BY COUNT(*) DESC "
                f"FETCH FIRST {k} ROWS ONLY"
            )
        else:
            top_sql = f"{top_sql} LIMIT {k}"
        try:
            top_raw = exec_sql(ds=ds, sql=top_sql, origin_column=True)
            for item in top_raw.get("data") or []:
                if not isinstance(item, dict):
                    continue
                value = item.get("v")
                if value is None and item:
                    value = next(iter(item.values()), None)
                count = item.get("c")
                if count is None and len(item) >= 2:
                    count = list(item.values())[1]
                if value is None:
                    continue
                top_values.append({"value": str(value)[:200], "count": int(count or 0)})
        except Exception:
            top_values = []

        return FieldProfileResult(
            supported=True,
            field_name=field,
            row_count=row_count,
            non_null_count=non_null,
            null_rate=null_rate,
            approx_distinct=approx_distinct,
            distinct_ratio=distinct_ratio,
            min_value=None if min_value is None else str(min_value)[:200],
            max_value=None if max_value is None else str(max_value)[:200],
            top_values=top_values,
            sample_method="limit_sample",
            sample_size=bounded,
            statement=agg_sql,
        )

    def extract_table_constraints(
        self,
        ds: Any,
        *,
        resource: str,
        database_name: str | None = None,
    ) -> Any:
        """Best-effort PK/FK extraction for MySQL/PG families."""
        import json

        from sqlalchemy import text

        from apps.datasource.models.datasource import DatasourceConf
        from apps.datasource.utils.utils import aes_decrypt
        from apps.db.db import get_session
        from apps.protocol.base import TableConstraintsResult

        if self.type_key not in (
            "mysql",
            "mariadb",
            "pg",
            "postgresql",
            "kingbase",
            "excel",
        ):
            return TableConstraintsResult(
                supported=False, error=f"unsupported dialect {self.type_key}"
            )
        if not resource:
            return TableConstraintsResult(supported=False, error="missing table")

        conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
        try:
            if self.type_key in ("mysql", "mariadb"):
                schema = conf.database
                with get_session(ds) as remote:
                    pk_rows = remote.execute(
                        text(
                            """
                            SELECT COLUMN_NAME
                            FROM information_schema.KEY_COLUMN_USAGE
                            WHERE TABLE_SCHEMA = :schema
                              AND TABLE_NAME = :table
                              AND CONSTRAINT_NAME = 'PRIMARY'
                            ORDER BY ORDINAL_POSITION
                            """
                        ),
                        {"schema": schema, "table": resource},
                    ).all()
                    primary_keys = [str(r[0]) for r in pk_rows]
                    fk_rows = remote.execute(
                        text(
                            """
                            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                            FROM information_schema.KEY_COLUMN_USAGE
                            WHERE TABLE_SCHEMA = :schema
                              AND TABLE_NAME = :table
                              AND REFERENCED_TABLE_NAME IS NOT NULL
                            ORDER BY ORDINAL_POSITION
                            """
                        ),
                        {"schema": schema, "table": resource},
                    ).all()
                    foreign_keys = [
                        {
                            "column": str(r[0]),
                            "ref_table": str(r[1]),
                            "ref_column": str(r[2]),
                        }
                        for r in fk_rows
                    ]
                return TableConstraintsResult(
                    supported=True,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                )

            schema = conf.dbSchema or "public"
            with get_session(ds) as remote:
                pk_rows = remote.execute(
                    text(
                        """
                        SELECT a.attname
                        FROM pg_index i
                        JOIN pg_class c ON c.oid = i.indrelid
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(i.indkey)
                        WHERE i.indisprimary
                          AND n.nspname = :schema
                          AND c.relname = :table
                        ORDER BY a.attnum
                        """
                    ),
                    {"schema": schema, "table": resource},
                ).all()
                primary_keys = [str(r[0]) for r in pk_rows]
                fk_rows = remote.execute(
                    text(
                        """
                        SELECT
                          src.attname AS column_name,
                          dst_cls.relname AS ref_table,
                          dst.attname AS ref_column
                        FROM pg_constraint con
                        JOIN pg_class src_cls ON src_cls.oid = con.conrelid
                        JOIN pg_namespace src_ns ON src_ns.oid = src_cls.relnamespace
                        JOIN pg_class dst_cls ON dst_cls.oid = con.confrelid
                        JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS src_cols(attnum, ord) ON TRUE
                        JOIN LATERAL unnest(con.confkey) WITH ORDINALITY AS dst_cols(attnum, ord)
                          ON src_cols.ord = dst_cols.ord
                        JOIN pg_attribute src
                          ON src.attrelid = con.conrelid AND src.attnum = src_cols.attnum
                        JOIN pg_attribute dst
                          ON dst.attrelid = con.confrelid AND dst.attnum = dst_cols.attnum
                        WHERE con.contype = 'f'
                          AND src_ns.nspname = :schema
                          AND src_cls.relname = :table
                        """
                    ),
                    {"schema": schema, "table": resource},
                ).all()
                foreign_keys = [
                    {
                        "column": str(r[0]),
                        "ref_table": str(r[1]),
                        "ref_column": str(r[2]),
                    }
                    for r in fk_rows
                ]
            return TableConstraintsResult(
                supported=True,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
            )
        except Exception as exc:
            return TableConstraintsResult(supported=False, error=str(exc)[:500])

    def plan_from_re_exec(self, ds: Any, re_exec: dict[str, Any]) -> QueryPlan | None:
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
        database_name: str | None = None,
    ) -> QueryResult:
        from apps.db.db import exec_sql

        where_clause = f" WHERE {where}" if where else ""

        type_key = self.type_key
        if type_key in ("mysql", "doris", "starrocks", "hive"):
            col_list = ", ".join(f"`{f}`" for f in fields)
            if type_key in ("doris", "starrocks"):
                from_clause = self.qualify_table(
                    ds, table_name, database_name=database_name
                )
            else:
                schema = self.schema_namespace(ds)
                if schema:
                    from_clause = f"`{schema}`.`{table_name}`"
                else:
                    from_clause = f"`{table_name}`"
            sql = f"SELECT {col_list} FROM {from_clause}{where_clause} LIMIT {limit}"
        elif type_key == "sqlServer":
            col_list = ", ".join(f"[{f}]" for f in fields)
            schema = self.schema_namespace(ds)
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
            schema = self.schema_namespace(ds)
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
                sql = (
                    f"SELECT * FROM {from_clause}{where_clause} WHERE ROWNUM <= {limit}"
                )
        else:
            # pg, excel, redshift, kingbase, dm default
            col_list = ", ".join(f'"{f}"' for f in fields)
            schema = self.schema_namespace(ds)
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
        from apps.db.starrocks_catalog import resolve_sr_scope

        try:
            if self.type_key == "excel":
                conf = get_engine_config()
            else:
                conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
            if self.type_key in ("doris", "starrocks"):
                catalog, databases = resolve_sr_scope(conf)
                if catalog:
                    return catalog
                if databases:
                    return databases[0]
            if conf.dbSchema is not None and conf.dbSchema != "":
                return conf.dbSchema
            return conf.database or ""
        except Exception:
            return ""
