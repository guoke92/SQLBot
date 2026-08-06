"""Regression tests for scope-aware physical SQL identifier extraction."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

_apps_module = sys.modules.get("apps")
if _apps_module is not None and not getattr(_apps_module, "__path__", None):
    for _module_name in list(sys.modules):
        if _module_name == "apps" or _module_name.startswith("apps."):
            sys.modules.pop(_module_name, None)

from apps.chat.query_contract import QueryContract  # noqa: E402
from apps.protocol.sql.identifier_validation import (  # noqa: E402
    PhysicalColumnRef,
    analyze_sql_contract_structure,
    collect_sql_identifier_usage,
    order_by_scope_error,
)


def _usage(sql: str):
    return collect_sql_identifier_usage(sql, "mysql")


def _detail_contract() -> QueryContract:
    """All columns of one table, restricted to a confirmed company list."""
    return QueryContract.model_validate(
        {
            "requirements": [
                {
                    "clause": "projection",
                    "slot_id": "slot_0001",
                    "label": "登记记录明细（全部字段）",
                    "mode": "all",
                    "fields": [],
                    "source": "user",
                    "evidence_refs": ["user:question"],
                },
                {
                    "clause": "predicate",
                    "slot_id": "slot_0002",
                    "label": "登记公司属于指定企业",
                    "field": {"resource": "recv_finance", "field": "company_name"},
                    "operator": "in",
                    "values": ["A", "B"],
                    "source": "user",
                    "evidence_refs": ["user:question"],
                },
            ]
        }
    )


def _analyze(*statements: str):
    return analyze_sql_contract_structure(
        list(statements), _detail_contract(), dialect="mysql"
    )


def _two_resource_contract() -> QueryContract:
    """Company names beside contact phones: two tables, no relation slot."""
    return QueryContract.model_validate(
        {
            "requirements": [
                {
                    "clause": "projection",
                    "slot_id": "slot_0001",
                    "label": "展示企业名称与联系人电话",
                    "mode": "listed",
                    "fields": [
                        {"resource": "cust_company", "field": "company_name"},
                        {"resource": "cust_user", "field": "cellphone"},
                    ],
                    "source": "user",
                    "evidence_refs": ["user:question"],
                },
                {
                    "clause": "predicate",
                    "slot_id": "slot_0002",
                    "label": "限定目标企业",
                    "field": {"resource": "cust_company", "field": "company_name"},
                    "operator": "in",
                    "values": ["A", "B"],
                    "source": "user",
                    "evidence_refs": ["user:question"],
                },
            ]
        }
    )


def test_a_bridge_table_join_is_a_schema_fact_not_a_contract_breach() -> None:
    """Two business entities can only meet through the link table between them.

    A many-to-many bridge can never appear in a contract, because the assessor
    derives clauses from the question and has never seen the schema.  Judging
    joins against the contract therefore rejected the one correct answer and
    left the question permanently unanswerable.
    """
    result = analyze_sql_contract_structure(
        [
            "SELECT `c`.`company_name`, `u`.`cellphone` "
            "FROM `db`.`cust_company` `c` "
            "JOIN `db`.`cust_company_user_ref` `r` ON `c`.`id` = `r`.`company_id` "
            "JOIN `db`.`cust_user` `u` ON `r`.`user_id` = `u`.`id` "
            "WHERE `c`.`company_name` IN ('A', 'B')"
        ],
        _two_resource_contract(),
        dialect="mysql",
    )

    assert result.error is None


def test_all_columns_contract_accepts_an_explicit_column_list() -> None:
    """An explicit column list is the form the SQL prompt teaches.

    Requiring a literal ``SELECT *`` used to reject every correct answer to a
    "show me the records" question until the retries ran out.
    """
    result = _analyze(
        "SELECT `t1`.`id`, `t1`.`company_name`, `t1`.`notice_date` "
        "FROM `db`.`recv_finance` `t1` "
        "WHERE `t1`.`company_name` IN ('A', 'B')"
    )

    assert result.error is None


def test_all_columns_contract_is_verified_by_a_star() -> None:
    result = _analyze(
        "SELECT * FROM `db`.`recv_finance` `t1` WHERE `t1`.`company_name` IN ('A', 'B')"
    )

    assert result.status == "verified"


def test_dropping_a_confirmed_filter_is_still_a_violation() -> None:
    result = _analyze("SELECT `t1`.`id` FROM `db`.`recv_finance` `t1`")

    assert result.error is not None


def test_an_invented_filter_is_reported() -> None:
    result = _analyze(
        "SELECT `t1`.`id` FROM `db`.`recv_finance` `t1` "
        "WHERE `t1`.`company_name` IN ('A', 'B') AND `t1`.`status` = 1"
    )

    assert result.error is not None
    assert "unconfirmed business predicates" in result.error


def test_cte_names_are_not_physical_tables() -> None:
    usage = _usage(
        """
        WITH task_stats AS (
            SELECT t.project_id AS system_id, COUNT(*) AS task_count
            FROM d_task t
            GROUP BY t.project_id
        )
        SELECT stats.system_id, stats.task_count
        FROM task_stats stats
        """
    )

    assert usage.physical_tables == frozenset({"d_task"})
    assert usage.physical_columns == (
        PhysicalColumnRef(table_name="d_task", column_name="project_id"),
    )


def test_derived_alias_outputs_do_not_collide_with_inner_table_alias() -> None:
    usage = _usage(
        """
        SELECT t.month, t.task_count
        FROM (
            SELECT DATE_FORMAT(t.create_time, '%Y-%m') AS month,
                   COUNT(*) AS task_count
            FROM d_task t
            GROUP BY month
        ) t
        """
    )

    assert usage.physical_tables == frozenset({"d_task"})
    assert usage.physical_columns == (
        PhysicalColumnRef(table_name="d_task", column_name="create_time"),
    )


def test_unknown_physical_column_is_still_collected() -> None:
    usage = _usage("SELECT t.not_exists FROM d_task t")

    assert usage.physical_columns == (
        PhysicalColumnRef(table_name="d_task", column_name="not_exists"),
    )


def test_database_qualified_table_carries_database_name() -> None:
    usage = _usage(
        "SELECT a.id, b.id FROM `stg`.`orders` a JOIN `ods`.`orders` b ON a.id = b.id"
    )
    assert usage.physical_tables == frozenset({"orders"})
    assert set(usage.physical_columns) == {
        PhysicalColumnRef(
            column_name="id", table_name="orders", database_name="stg"
        ),
        PhysicalColumnRef(
            column_name="id", table_name="orders", database_name="ods"
        ),
    }


def test_three_part_name_still_uses_bare_table_for_allow_list() -> None:
    usage = _usage(
        "SELECT a.x FROM `hive_emr`.`stg`.`orders` a"
    )
    assert usage.physical_tables == frozenset({"orders"})
    assert usage.physical_columns == (
        PhysicalColumnRef(
            column_name="x", table_name="orders", database_name="stg"
        ),
    )


def test_physical_table_hidden_in_cte_still_hits_allow_list() -> None:
    usage = _usage(
        """
        WITH hidden AS (SELECT s.id FROM secret_story s)
        SELECT h.id FROM hidden h
        """
    )

    assert usage.physical_tables == frozenset({"secret_story"})


def test_unqualified_group_alias_is_not_a_physical_column() -> None:
    usage = _usage(
        """
        SELECT DATE_FORMAT(create_time, '%Y-%m') AS month, COUNT(*) AS total
        FROM d_task
        GROUP BY month
        ORDER BY month
        """
    )

    assert usage.physical_columns == (
        PhysicalColumnRef(
            column_name="create_time",
            candidate_tables=("d_task",),
            candidate_databases=("",),
        ),
    )


def test_hive_order_by_naming_a_table_alias_is_caught_before_execution() -> None:
    """Hive resolves ORDER BY against output names, so this always fails.

    The prompt has said so for three releases and the model keeps writing the
    qualified form, spending a generation and an engine round-trip each time.
    """
    problem = order_by_scope_error(
        "SELECT FROM_UNIXTIME(CAST(`c`.`create_time` / 1000 AS BIGINT), "
        "'yyyy-MM-dd HH:mm:ss') AS `create_time` "
        "FROM `stg`.`stg_b008_cust_company` `c` "
        "ORDER BY `c`.`create_time` LIMIT 1000",
        "hive",
    )

    assert problem is not None
    # The engine answers with a Java stack trace; the model needs the fix.
    assert "use `create_time`" in problem


def test_hive_order_by_on_an_unprojected_column_says_what_is_missing() -> None:
    problem = order_by_scope_error(
        "SELECT `c`.`a` AS `a` FROM `t` `c` ORDER BY `c`.`b`", "hive"
    )

    assert problem is not None
    assert "not in the SELECT output" in problem


def test_an_output_alias_and_a_window_order_are_both_left_alone() -> None:
    assert (
        order_by_scope_error(
            "SELECT ROW_NUMBER() OVER (ORDER BY `c`.`ts`) AS `rn`, `c`.`x` AS `x` "
            "FROM `t` `c` ORDER BY `x`",
            "hive",
        )
        is None
    )


def test_engines_that_resolve_order_by_against_the_source_are_exempt() -> None:
    assert (
        order_by_scope_error(
            "SELECT `c`.`x` AS `x` FROM `t` `c` ORDER BY `c`.`x`", "mysql"
        )
        is None
    )
