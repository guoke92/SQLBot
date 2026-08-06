"""Atomic query-plan and clause-oriented contract tests."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import orjson
import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.contract.validation import validate_contract  # noqa: E402
from apps.chat.planning import parse_query_generation  # noqa: E402
from apps.chat.query_contract import (  # noqa: E402
    FieldRef,
    GroupRequirement,
    LimitRequirement,
    OrderRequirement,
    OutputRequirement,
    PopulationPolicy,
    PredicateRequirement,
    ProjectionRequirement,
    QueryContract,
    RelationPair,
    RelationRequirement,
    TimeWindowRequirement,
)
from apps.protocol import QueryPlan  # noqa: E402


class FakeProtocol:
    type_key = "mysql"

    def __init__(self, *, sql_capability: bool = True) -> None:
        self.sql_capability = sql_capability

    def supports(self, _capability: str) -> bool:
        return self.sql_capability

    def parse_llm_output(self, text: str) -> QueryPlan:
        data = orjson.loads(text)
        if not data.get("success"):
            return QueryPlan(success=False, message=data.get("message") or "invalid")
        sql = data.get("sql") or ""
        return QueryPlan(
            success=True,
            statement=sql,
            payload={"sql": sql},
            resources=data.get("tables") or [],
            chart_type=data.get("chart-type"),
            brief=data.get("brief"),
        )

    def validate_plan(
        self,
        _ds: object,
        plan: QueryPlan,
        _allowed_resources: list[str],
    ) -> QueryPlan:
        if "bad_column" in plan.statement:
            return plan.model_copy(
                update={"success": False, "message": "unknown column bad_column"}
            )
        return plan.model_copy(update={"resources": ["physical_table"]})

    def format_statement_for_display(self, plan: QueryPlan) -> str:
        return plan.statement


def service(
    *, sql_capability: bool = True, contract: QueryContract | None = None
) -> SimpleNamespace:
    return SimpleNamespace(
        protocol=FakeProtocol(sql_capability=sql_capability),
        ds=object(),
        table_name_list=["physical_table"],
        chat_question=SimpleNamespace(
            question="查询数据",
            intent_context=(
                {"contract": contract.model_dump(mode="json") if contract else None}
            ),
        ),
    )


def _raw(*sqls: str) -> str:
    payload = [
        {"success": True, "sql": sql, "tables": ["physical_table"]} for sql in sqls
    ]
    return orjson.dumps(payload[0] if len(payload) == 1 else payload).decode()


def test_mixed_valid_invalid_batch_is_rejected_atomically() -> None:
    result = parse_query_generation(
        _raw("SELECT 1", "SELECT bad_column FROM physical_table"),
        service(),
        max_batch_size=3,
    )
    assert not result.success
    assert result.plans == []
    assert result.contract_status == "unsupported"
    assert "计划 2" in (result.error_message or "")


def test_non_sql_protocol_is_explicitly_unsupported_not_verified() -> None:
    result = parse_query_generation(
        _raw("SELECT 1"),
        service(sql_capability=False),
        max_batch_size=3,
    )
    assert result.success
    assert result.contract_status == "unsupported"


def _latest_contract() -> QueryContract:
    return QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="slot_projection",
                label="全部字段",
                mode="all",
            ),
            OrderRequirement(
                slot_id="slot_order",
                label="按创建时间判断最新",
                field=FieldRef(resource="physical_table", field="create_time"),
                direction="desc",
            ),
            LimitRequirement(slot_id="slot_limit", label="十条", value=10),
        ]
    )


def test_latest_ten_rows_is_verified_without_a_time_window() -> None:
    result = parse_query_generation(
        _raw("SELECT * FROM physical_table ORDER BY create_time DESC LIMIT 10"),
        service(contract=_latest_contract()),
        max_batch_size=3,
        query_contract=_latest_contract(),
    )
    assert result.success
    assert result.contract_status == "verified"


def test_unconfirmed_schema_policy_predicate_is_advisory() -> None:
    result = parse_query_generation(
        _raw(
            "SELECT * FROM physical_table WHERE hide_flag != 'Y' "
            "ORDER BY create_time DESC LIMIT 10"
        ),
        service(contract=_latest_contract()),
        max_batch_size=3,
        query_contract=_latest_contract(),
    )
    assert result.success
    assert result.plans
    assert "unconfirmed business predicates" in (result.contract_message or "")


def test_unconfirmed_public_output_is_advisory() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="amount",
                label="签收额",
                field=FieldRef(resource="physical_table", field="amount"),
                operation="sum",
            )
        ]
    )
    result = parse_query_generation(
        _raw("SELECT SUM(amount) AS amount, name FROM physical_table GROUP BY name"),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "unconfirmed public outputs" in (result.contract_message or "")


def test_unconfirmed_public_grouping_is_advisory() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="amount",
                label="签收额",
                field=FieldRef(resource="physical_table", field="amount"),
                operation="sum",
            )
        ]
    )
    result = parse_query_generation(
        _raw("SELECT SUM(amount) AS amount FROM physical_table GROUP BY name"),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "unconfirmed public grouping" in (result.contract_message or "")


def test_output_must_be_projected_with_the_confirmed_aggregation() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="amount",
                label="签收额",
                field=FieldRef(resource="physical_table", field="amount"),
                operation="sum",
            )
        ]
    )
    invalid = parse_query_generation(
        _raw("SELECT name FROM physical_table WHERE amount > 0"),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    valid = parse_query_generation(
        _raw("SELECT SUM(amount) AS amount FROM physical_table"),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert invalid.contract_message
    assert valid.contract_status == "verified"


def test_cte_output_lineage_preserves_the_confirmed_aggregation() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="amount",
                label="签收额",
                field=FieldRef(resource="physical_table", field="amount"),
                operation="sum",
            )
        ]
    )
    valid = parse_query_generation(
        _raw(
            "WITH aggregate_result AS ("
            "SELECT SUM(amount) AS total_amount FROM physical_table"
            ") SELECT total_amount FROM aggregate_result"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    hidden = parse_query_generation(
        _raw(
            "WITH aggregate_result AS ("
            "SELECT SUM(amount) AS total_amount FROM physical_table"
            ") SELECT 1 AS unrelated_value FROM aggregate_result"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert valid.contract_status == "verified"
    assert hidden.contract_message


def test_group_time_bucket_is_part_of_the_contract() -> None:
    contract = QueryContract(
        requirements=[
            GroupRequirement(
                slot_id="month",
                label="按月统计",
                field=FieldRef(resource="physical_table", field="create_time"),
                bucket="month",
            ),
            OutputRequirement(
                slot_id="count",
                label="记录数",
                field=FieldRef(resource="physical_table", field="id"),
                operation="count",
            ),
        ]
    )
    valid = parse_query_generation(
        _raw(
            "SELECT DATE_FORMAT(create_time, '%Y-%m') AS month, COUNT(id) AS count "
            "FROM physical_table GROUP BY DATE_FORMAT(create_time, '%Y-%m')"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    wrong_grain = parse_query_generation(
        _raw(
            "SELECT create_time, COUNT(id) AS count FROM physical_table "
            "GROUP BY create_time"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert valid.contract_status == "verified"
    assert wrong_grain.contract_message


def test_derived_output_requires_the_confirmed_arithmetic_operation() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="amount",
                label="签收额",
                field=FieldRef(resource="physical_table", field="amount"),
                operation="sum",
            ),
            OutputRequirement(
                slot_id="target",
                label="目标额",
                field=FieldRef(resource="physical_table", field="target"),
                operation="sum",
            ),
            OutputRequirement(
                slot_id="rate",
                label="完成率",
                field=FieldRef(field="completion_rate"),
                operation="ratio",
                operands=["amount", "target"],
            ),
        ]
    )
    valid = parse_query_generation(
        _raw(
            "SELECT SUM(amount) AS amount, SUM(target) AS target, "
            "SUM(amount) / NULLIF(SUM(target), 0) AS completion_rate "
            "FROM physical_table"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    wrong_formula = parse_query_generation(
        _raw(
            "SELECT SUM(amount) AS amount, SUM(target) AS target, "
            "1 AS completion_rate FROM physical_table"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert valid.contract_status == "verified"
    assert wrong_formula.contract_message


def test_order_by_output_alias_resolves_through_projection_lineage() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="amount",
                label="签收额",
                field=FieldRef(resource="physical_table", field="amount"),
                operation="sum",
            ),
            OrderRequirement(
                slot_id="order",
                label="签收额倒序",
                output_slot_id="amount",
                direction="desc",
            ),
        ]
    )
    result = parse_query_generation(
        _raw(
            "SELECT SUM(amount) AS total_amount FROM physical_table "
            "ORDER BY total_amount DESC"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.contract_status == "verified"


def test_predicate_null_policy_is_never_silently_treated_as_verified() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="projection",
                label="全部字段",
                mode="all",
            ),
            PredicateRequirement(
                slot_id="status",
                label="排除草稿状态",
                field=FieldRef(resource="physical_table", field="status"),
                operator="not_in",
                values=["draft"],
            ),
        ]
    )
    result = parse_query_generation(
        _raw("SELECT * FROM physical_table WHERE status NOT IN ('draft')"),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    preserve = contract.model_copy(
        update={
            "requirements": (
                contract.requirements[0],
                contract.requirements[1].model_copy(update={"null_policy": "preserve"}),
            )
        }
    )
    partial = parse_query_generation(
        _raw("SELECT * FROM physical_table WHERE status NOT IN ('draft')"),
        service(contract=preserve),
        max_batch_size=3,
        query_contract=preserve,
    )
    assert result.contract_status == "verified"
    assert partial.success
    assert partial.contract_status == "partial"


def test_explicit_time_window_requires_both_bounds_on_every_fact_field() -> None:
    contract = QueryContract(
        requirements=[
            TimeWindowRequirement(
                slot_id="time",
                label="2026年",
                fields=[
                    FieldRef(resource="task", field="create_time"),
                    FieldRef(resource="story", field="create_time"),
                ],
                mode="explicit",
                start="2026-01-01",
                end_exclusive="2027-01-01",
            ),
            OutputRequirement(
                slot_id="task_count",
                label="任务数",
                field=FieldRef(resource="task", field="id"),
                operation="count",
            ),
            OutputRequirement(
                slot_id="story_count",
                label="需求数",
                field=FieldRef(resource="story", field="id"),
                operation="count",
            ),
        ]
    )
    sql = (
        "SELECT COUNT(t.id) task_count, COUNT(s.id) story_count "
        "FROM task t JOIN story s ON t.project_id=s.project_id "
        "WHERE t.create_time >= '2026-01-01' AND t.create_time < '2027-01-01'"
    )
    result = parse_query_generation(
        _raw(sql),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "Missing contract slots: time" in (result.contract_message or "")


def _multi_fact_contract(
    *, population: PopulationPolicy = "union"
) -> QueryContract:
    return QueryContract(
        requirements=[
            GroupRequirement(
                slot_id="company",
                label="企业",
                field=FieldRef(resource="finance", field="company_name"),
            ),
            OutputRequirement(
                slot_id="signed",
                label="累计签收额",
                field=FieldRef(resource="asset", field="transfer_amt"),
                operation="sum",
            ),
            OutputRequirement(
                slot_id="financed",
                label="累计融资额",
                field=FieldRef(resource="finance", field="fin_apply_amt"),
                operation="sum",
            ),
            RelationRequirement(
                slot_id="population",
                label="企业展示范围",
                pairs=[
                    RelationPair(
                        left=FieldRef(resource="asset", field="company_name"),
                        right=FieldRef(resource="finance", field="company_name"),
                    )
                ],
                population=population,
            ),
        ]
    )


def test_grouped_multi_resource_contract_freezes_before_planning_diagnostics() -> None:
    contract = QueryContract(
        requirements=[
            GroupRequirement(
                slot_id="company",
                label="企业",
                field=FieldRef(resource="finance", field="company_name"),
            ),
            OutputRequirement(
                slot_id="signed",
                label="累计签收额",
                field=FieldRef(resource="asset", field="transfer_amt"),
                operation="sum",
            ),
        ]
    )

    assert contract.result_mode == "aggregate"
    assert [
        item.code for item in validate_contract(contract)
    ] == ["relation_coverage_missing"]


def test_union_population_flags_a_silent_finance_left_join() -> None:
    contract = _multi_fact_contract()
    result = parse_query_generation(
        _raw(
            "SELECT f.company_name, a.total_transfer_amt, f.total_fin_apply_amt "
            "FROM (SELECT company_name, SUM(fin_apply_amt) total_fin_apply_amt "
            "FROM finance GROUP BY company_name) f "
            "LEFT JOIN (SELECT company_name, SUM(transfer_amt) total_transfer_amt "
            "FROM asset GROUP BY company_name) a "
            "ON f.company_name=a.company_name"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "Missing contract slots: population" in (result.contract_message or "")


def test_union_dimension_scaffold_satisfies_union_population() -> None:
    contract = _multi_fact_contract()
    result = parse_query_generation(
        _raw(
            "SELECT d.company_name, a.total_transfer_amt, f.total_fin_apply_amt "
            "FROM (SELECT company_name FROM asset "
            "UNION SELECT company_name FROM finance) d "
            "LEFT JOIN (SELECT company_name, SUM(transfer_amt) total_transfer_amt "
            "FROM asset GROUP BY company_name) a "
            "ON d.company_name=a.company_name "
            "LEFT JOIN (SELECT company_name, SUM(fin_apply_amt) total_fin_apply_amt "
            "FROM finance GROUP BY company_name) f "
            "ON d.company_name=f.company_name"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success, result.error_message
    assert result.contract_status == "verified"


def test_a_join_on_the_wrong_keys_misses_the_frozen_relation_pairs() -> None:
    # Joins as such are the schema's business, but a relation the user did
    # confirm still has to be honoured on the keys and side they agreed to.
    contract = _multi_fact_contract(population="left")
    result = parse_query_generation(
        _raw(
            "SELECT f.company_name, SUM(a.transfer_amt) total_transfer_amt, "
            "SUM(f.fin_apply_amt) total_fin_apply_amt FROM finance f "
            "LEFT JOIN asset a ON f.company_id=a.company_id "
            "GROUP BY f.company_name"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "population" in (result.contract_message or "")


def test_dialect_specific_rolling_window_is_partial_but_publishable() -> None:
    contract = QueryContract(
        requirements=[
            TimeWindowRequirement(
                slot_id="time",
                label="最近三个月",
                fields=[FieldRef(resource="physical_table", field="create_time")],
                mode="rolling",
                rolling_months=3,
            ),
            OutputRequirement(
                slot_id="count",
                label="数量",
                field=FieldRef(resource="physical_table", field="id"),
                operation="count",
            ),
        ]
    )
    result = parse_query_generation(
        _raw(
            "SELECT COUNT(id) count FROM physical_table "
            "WHERE create_time >= DATE_SUB(CURRENT_DATE, INTERVAL 3 MONTH)"
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert result.contract_status == "partial"


def _complementary_contract() -> QueryContract:
    return QueryContract(
        requirements=[
            PredicateRequirement(
                slot_id="department",
                label="研发二部",
                field=FieldRef(field="department"),
                operator="eq",
                values=["研发二部"],
            ),
            GroupRequirement(
                slot_id="month",
                label="月份",
                field=FieldRef(field="month"),
            ),
            OutputRequirement(
                slot_id="task_count",
                label="任务数",
                field=FieldRef(field="task_id"),
                operation="count",
            ),
            OutputRequirement(
                slot_id="story_count",
                label="需求数",
                field=FieldRef(field="story_id"),
                operation="count",
            ),
        ]
    )


def test_complementary_batch_requires_universal_scope_in_every_plan() -> None:
    contract = _complementary_contract()
    result = parse_query_generation(
        _raw(
            "SELECT month, COUNT(task_id) task_count FROM physical_table "
            "WHERE department='研发二部' GROUP BY month",
            "SELECT month, COUNT(story_id) story_count FROM physical_table GROUP BY month",
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "omits universal contract slots" in (result.contract_message or "")


def test_complementary_batch_is_disjoint_nonempty_and_complete() -> None:
    contract = _complementary_contract()
    result = parse_query_generation(
        _raw(
            "SELECT month, COUNT(task_id) task_count FROM physical_table "
            "WHERE department='研发二部' GROUP BY month",
            "SELECT month, COUNT(story_id) story_count FROM physical_table "
            "WHERE department='研发二部' GROUP BY month",
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert result.contract_status == "verified"
    assert result.plans[0]["covered_requirement_keys"] == [
        "department",
        "month",
        "task_count",
    ]


def test_batch_flags_overlapping_or_zero_output_plans() -> None:
    contract = _complementary_contract()
    overlap = parse_query_generation(
        _raw(
            "SELECT month, COUNT(task_id) task_count FROM physical_table "
            "WHERE department='研发二部' GROUP BY month",
            "SELECT month, COUNT(task_id) task_count, COUNT(story_id) story_count "
            "FROM physical_table WHERE department='研发二部' GROUP BY month",
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert overlap.success
    assert "overlap output slots" in (overlap.contract_message or "")


def test_user_order_or_limit_flags_a_multi_plan_batch() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="value",
                label="金额",
                field=FieldRef(field="amount"),
                operation="sum",
            ),
            OrderRequirement(
                slot_id="order",
                label="金额倒序",
                output_slot_id="value",
                direction="desc",
            ),
            LimitRequirement(slot_id="limit", label="前十", value=10),
        ]
    )
    result = parse_query_generation(
        _raw(
            "SELECT SUM(amount) amount FROM physical_table ORDER BY amount DESC LIMIT 10",
            "SELECT SUM(amount) amount FROM physical_table ORDER BY amount DESC LIMIT 10",
        ),
        service(contract=contract),
        max_batch_size=3,
        query_contract=contract,
    )
    assert result.success
    assert "must be implemented by one plan" in (result.contract_message or "")


def test_batch_size_limit_is_rejected_not_truncated() -> None:
    result = parse_query_generation(
        _raw("SELECT 1", "SELECT 2", "SELECT 3"),
        service(),
        max_batch_size=2,
    )
    assert not result.success
    assert "超过单批上限" in (result.error_message or "")
