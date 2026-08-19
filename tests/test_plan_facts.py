"""Plan-fact dialect parsing and grouped aggregation window helpers."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.aggregation_window import (  # noqa: E402
    GROUP_COUNT_ALIAS,
    aggregation_totals_sql,
    apply_grouped_metric_order,
    ensure_grouped_metric_order,
)
from apps.chat.plan_facts import extract_sql_plan_facts, sqlglot_dialect_for  # noqa: E402
from apps.chat.query_risk import QueryRiskInput, classify_query_risk  # noqa: E402

_CHAT117_SQL = (
    "SELECT `company_name` AS `原始供应商`, "
    "SUM(CASE WHEN `sign_date` >= '2026-01-01' AND `sign_date` < '2027-01-01' "
    "THEN `orig_asset_amt` ELSE 0 END) AS `累计签收额`, "
    "SUM(CASE WHEN `fin_apply_date` >= '2026-01-01' AND `fin_apply_date` < '2027-01-01' "
    "THEN `fin_apply_amt` ELSE 0 END) AS `累计融资额`, "
    "GROUP_CONCAT(DISTINCT `core_company_name` ORDER BY `core_company_name` "
    "SEPARATOR '、') AS `核企名称`, "
    "GROUP_CONCAT(DISTINCT `apply_level` ORDER BY `apply_level` SEPARATOR '、') "
    "AS `供应商层级` "
    "FROM `dw`.`dw_mid_crm_wec_xun_core_fin_list` "
    "WHERE (`sign_date` >= '2026-01-01' AND `sign_date` < '2027-01-01') "
    "OR (`fin_apply_date` >= '2026-01-01' AND `fin_apply_date` < '2027-01-01') "
    "GROUP BY `company_name`"
)


def test_backtick_sql_is_unsupported_without_dialect() -> None:
    facts = extract_sql_plan_facts(_CHAT117_SQL)
    assert facts.parser_coverage == "unsupported"


def test_mysql_dialect_parses_chat117_sql_and_proves_time() -> None:
    facts = extract_sql_plan_facts(_CHAT117_SQL, dialect="mysql")
    assert facts.parser_coverage == "full"
    assert "sign_date" in facts.predicate_fields
    assert "fin_apply_date" in facts.predicate_fields
    assert "2026-01-01" in " ".join(facts.predicates)
    result = classify_query_risk(
        QueryRiskInput(
            facts=(facts,),
            schema_text="sign_date varchar, fin_apply_date varchar, orig_asset_amt decimal",
            temporal_evidence={
                "start": "2026-01-01",
                "end_exclusive": "2027-01-01",
            },
        )
    )
    codes = {item.code for item in result.reasons}
    assert "EXPLICIT_TIME_NOT_PROVEN" not in codes
    assert "PARTIAL_PARSER_COVERAGE" not in codes
    assert "MULTIPLE_TIME_BASIS" in codes


def test_sqlglot_dialect_for_mysql_and_starrocks() -> None:
    assert sqlglot_dialect_for("mysql") == "mysql"
    assert sqlglot_dialect_for("starrocks") == "mysql"
    assert sqlglot_dialect_for("pg") == "postgres"


def test_grouped_query_gets_metric_order() -> None:
    sql = (
        "SELECT `company_name` AS `企业`, SUM(`orig_asset_amt`) AS `累计签收额` "
        "FROM `dw`.`t` GROUP BY `company_name`"
    )
    rewritten = ensure_grouped_metric_order(sql, dialect="mysql")
    assert rewritten != sql
    facts = extract_sql_plan_facts(rewritten, dialect="mysql")
    assert facts.parser_coverage == "full"
    assert facts.order_fields
    assert apply_grouped_metric_order(
        [{"sql": sql, "payload": {"sql": sql}}],
        dialect="mysql",
    )


def test_existing_order_is_left_alone() -> None:
    sql = (
        "SELECT company_name, SUM(amt) AS total FROM t "
        "GROUP BY company_name ORDER BY company_name"
    )
    assert ensure_grouped_metric_order(sql, dialect="mysql") == sql


def test_hive_does_not_order_by_alias() -> None:
    sql = "SELECT company_name, SUM(amt) AS total FROM t GROUP BY company_name"
    assert ensure_grouped_metric_order(sql, dialect="hive") == sql


def test_cte_alignment_is_not_a_physical_join() -> None:
    facts = extract_sql_plan_facts(
        """WITH sign AS (SELECT company_name, SUM(amt) total FROM asset GROUP BY company_name),
           fin AS (SELECT company_name, SUM(amt) total FROM finance GROUP BY company_name)
           SELECT s.company_name, s.total, f.total
           FROM sign s LEFT JOIN fin f ON s.company_name = f.company_name"""
    )
    assert facts.parser_coverage == "full"
    assert facts.joins == ()
    assert "asset" in facts.resources
    assert "finance" in facts.resources


def test_physical_table_join_is_recorded() -> None:
    facts = extract_sql_plan_facts(
        "SELECT a.id, b.name FROM account a JOIN customer b ON a.customer_id = b.id"
    )
    assert facts.joins


def test_aggregation_totals_sql_wraps_grouped_metrics() -> None:
    sql = (
        "SELECT `company_name` AS `企业`, SUM(`orig_asset_amt`) AS `累计签收额` "
        "FROM `dw`.`t` GROUP BY `company_name` ORDER BY `累计签收额` DESC"
    )
    wrapped = aggregation_totals_sql(sql, dialect="mysql")
    assert wrapped is not None
    assert GROUP_COUNT_ALIAS in wrapped
    assert "SUM(`累计签收额`)" in wrapped
    assert "AS __agg_groups" in wrapped
    facts = extract_sql_plan_facts(wrapped, dialect="mysql")
    assert facts.parser_coverage == "full"
    assert facts.subquery_count >= 1
