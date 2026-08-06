"""Deterministic single-table filter SQL compilation."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.query_contract import (  # noqa: E402
    FieldRef,
    LimitRequirement,
    OrderRequirement,
    OutputRequirement,
    PredicateRequirement,
    ProjectionRequirement,
    QueryContract,
    RelationPair,
    RelationRequirement,
    TimeWindowRequirement,
)
from apps.chat.simple_sql import try_compile_simple_batch  # noqa: E402
from apps.protocol import QueryPlan  # noqa: E402
from apps.protocol.sql.identifier_validation import order_by_scope_error  # noqa: E402


class FakeProtocol:
    type_key = "hive"

    def supports(self, _capability: str) -> bool:
        return True

    def _quote_identifier(self, identifier: str) -> str:
        escaped = identifier.replace("`", "``")
        return f"`{escaped}`"

    def schema_namespace(self, _ds: object) -> str:
        return "stg"

    def validate_plan(
        self,
        _ds: object,
        plan: QueryPlan,
        _allowed_resources: list[str],
    ) -> QueryPlan:
        return plan

    def format_statement_for_display(self, plan: QueryPlan) -> str:
        return plan.statement


def _service() -> SimpleNamespace:
    return SimpleNamespace(protocol=FakeProtocol(), ds=object(), table_name_list=[])


def test_listed_in_order_limit_compiles() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="proj",
                label="企业与电话",
                mode="listed",
                fields=(
                    FieldRef(resource="cust_company", field="company_name"),
                    FieldRef(resource="cust_company", field="cellphone"),
                ),
                source="user",
                evidence_refs=["user:question"],
            ),
            PredicateRequirement(
                slot_id="filter",
                label="指定企业",
                field=FieldRef(resource="cust_company", field="company_name"),
                operator="in",
                values=("A", "B"),
                source="user",
                evidence_refs=["user:question"],
            ),
            OrderRequirement(
                slot_id="order",
                label="按名称",
                field=FieldRef(resource="cust_company", field="company_name"),
                direction="asc",
            ),
            LimitRequirement(slot_id="limit", label="上限", value=100),
        ]
    )
    result = try_compile_simple_batch(
        contract, _service(), question="查企业", default_limit=1000
    )

    assert result is not None
    assert result.success
    sql = result.plans[0]["sql"]
    assert "SELECT `company_name`, `cellphone`" in sql
    assert "FROM `stg`.`cust_company`" in sql
    assert "WHERE `company_name` IN ('A', 'B')" in sql
    assert "ORDER BY `company_name` ASC" in sql
    assert sql.endswith("LIMIT 100")
    assert "ORDER BY `cust_company`" not in sql
    assert order_by_scope_error(sql, "hive") is None


def test_all_columns_eq_uses_default_limit() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="proj",
                label="全部字段",
                mode="all",
                source="user",
                evidence_refs=["user:question"],
            ),
            PredicateRequirement(
                slot_id="filter",
                label="状态",
                field=FieldRef(resource="cust_company", field="status"),
                operator="eq",
                values=(1,),
                source="user",
                evidence_refs=["user:question"],
            ),
            OrderRequirement(
                slot_id="order",
                label="创建时间",
                field=FieldRef(resource="cust_company", field="create_time"),
                direction="desc",
            ),
        ]
    )
    result = try_compile_simple_batch(
        contract, _service(), question="查记录", default_limit=1000
    )

    assert result is not None
    sql = result.plans[0]["sql"]
    assert sql.startswith("SELECT * FROM `stg`.`cust_company`")
    assert "WHERE `status` = 1" in sql
    assert "ORDER BY `create_time` DESC" in sql
    assert sql.endswith("LIMIT 1000")
    assert order_by_scope_error(sql, "hive") is None


def test_two_resources_are_not_compiled() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="proj",
                label="跨表",
                mode="listed",
                fields=(
                    FieldRef(resource="company", field="name"),
                    FieldRef(resource="user", field="phone"),
                ),
                source="user",
                evidence_refs=["user:question"],
            )
        ]
    )
    assert try_compile_simple_batch(contract, _service()) is None


def test_relation_is_not_compiled() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="proj",
                label="名称",
                mode="listed",
                fields=(FieldRef(resource="company", field="name"),),
                source="user",
                evidence_refs=["user:question"],
            ),
            RelationRequirement(
                slot_id="rel",
                label="关联",
                pairs=(
                    RelationPair(
                        left=FieldRef(resource="company", field="id"),
                        right=FieldRef(resource="user", field="company_id"),
                    ),
                ),
                population="left",
                source="user",
                evidence_refs=["user:question"],
            ),
        ]
    )
    assert try_compile_simple_batch(contract, _service()) is None


def test_output_requirement_is_not_compiled() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="name",
                label="名称",
                field=FieldRef(resource="company", field="name"),
                operation="value",
            ),
            PredicateRequirement(
                slot_id="filter",
                label="指定",
                field=FieldRef(resource="company", field="status"),
                operator="eq",
                values=(1,),
            ),
        ]
    )
    assert try_compile_simple_batch(contract, _service()) is None


def test_time_window_is_not_compiled() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="proj",
                label="名称",
                mode="listed",
                fields=(FieldRef(resource="company", field="name"),),
                source="user",
                evidence_refs=["user:question"],
            ),
            TimeWindowRequirement(
                slot_id="time",
                label="今年",
                fields=(FieldRef(resource="company", field="create_time"),),
                mode="explicit",
                start="2026-01-01",
                end_exclusive="2027-01-01",
            ),
        ]
    )
    assert try_compile_simple_batch(contract, _service()) is None


def test_order_column_missing_from_listed_projection_is_not_compiled() -> None:
    contract = QueryContract(
        requirements=[
            ProjectionRequirement(
                slot_id="proj",
                label="名称",
                mode="listed",
                fields=(FieldRef(resource="company", field="name"),),
                source="user",
                evidence_refs=["user:question"],
            ),
            OrderRequirement(
                slot_id="order",
                label="按时间",
                field=FieldRef(resource="company", field="create_time"),
                direction="desc",
            ),
        ]
    )
    assert try_compile_simple_batch(contract, _service()) is None
