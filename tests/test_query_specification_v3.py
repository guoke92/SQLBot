from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.query_specification import (  # noqa: E402
    canonicalize_planner_requirement_ids,
    FieldRef,
    GroupRequirement,
    OutputRequirement,
    PredicateRequirement,
    QuerySpecification,
    normalize_specification,
)


def test_clause_oriented_specification_has_one_stable_identity() -> None:
    specification = QuerySpecification(
        revision=2,
        outputs=(
            OutputRequirement(
                requirement_id="req_count",
                business_label="客户数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count_distinct",
                source="user",
                evidence_refs=("user:question",),
                confidence=1,
            ),
        ),
        group_by=(
            GroupRequirement(
                requirement_id="req_month",
                business_label="创建月份",
                field=FieldRef(resource="customer", field="created_at"),
                bucket="month",
            ),
        ),
        confidence=0.9,
    )
    assert specification.result_mode == "aggregate"
    assert set(specification.by_requirement_id()) == {"req_count", "req_month"}
    assert "requirements" not in specification.model_dump(mode="json")


def test_user_clause_requires_immutable_user_evidence() -> None:
    with pytest.raises(ValidationError, match="immutable user evidence"):
        PredicateRequirement(
            requirement_id="req_scope",
            business_label="仅统计已完成客户",
            field=FieldRef(resource="customer", field="status"),
            operator="eq",
            values=("done",),
            source="user",
            evidence_refs=("schema:status",),
        )
    accepted = PredicateRequirement(
        requirement_id="req_scope",
        business_label="仅统计已完成客户",
        field=FieldRef(resource="customer", field="status"),
        operator="eq",
        values=("done",),
        source="user",
        evidence_refs=("user:prior_question:0",),
    )
    assert accepted.evidence_refs == ("user:prior_question:0",)


def test_duplicate_requirement_ids_are_rejected() -> None:
    output = OutputRequirement(
        requirement_id="same",
        business_label="客户数",
        field=FieldRef(resource="customer", field="id"),
        aggregation="count",
    )
    group = GroupRequirement(
        requirement_id="same",
        business_label="月份",
        field=FieldRef(resource="customer", field="created_at"),
        bucket="month",
    )
    with pytest.raises(ValidationError, match="must be unique"):
        QuerySpecification(revision=1, outputs=(output,), group_by=(group,))


def test_planner_temporary_ids_are_reassigned_before_validation() -> None:
    raw = {
        "revision": 1,
        "outputs": [
            {
                "clause": "output",
                "requirement_id": "metric",
                "business_label": "累计签收额",
                "field": {"resource": "asset", "field": "fin_apply_amt"},
                "aggregation": "sum",
            },
            {
                "clause": "output",
                "requirement_id": "metric",
                "business_label": "累计融资额",
                "field": {"resource": "asset", "field": "fin_apply_amt"},
                "aggregation": "sum",
            },
        ],
    }

    canonical = canonicalize_planner_requirement_ids(raw)
    specification = normalize_specification(QuerySpecification.model_validate(canonical))

    assert len(specification.outputs) == 2
    assert len({item.requirement_id for item in specification.outputs}) == 2


def test_ambiguous_duplicate_temporary_reference_is_rejected() -> None:
    raw = {
        "revision": 1,
        "outputs": [
            {
                "clause": "output",
                "requirement_id": "metric",
                "business_label": "指标一",
                "field": {"resource": "asset", "field": "amount"},
                "aggregation": "sum",
            },
            {
                "clause": "output",
                "requirement_id": "metric",
                "business_label": "指标二",
                "field": {"resource": "asset", "field": "amount"},
                "aggregation": "avg",
            },
        ],
        "order_by": [
            {
                "clause": "order",
                "requirement_id": "order",
                "business_label": "按指标排序",
                "output_requirement_id": "metric",
                "direction": "desc",
            }
        ],
    }

    with pytest.raises(ValueError, match="temporary ID was reused"):
        canonicalize_planner_requirement_ids(raw)


def test_duplicate_semantics_have_order_independent_business_ids() -> None:
    def build(labels: tuple[str, str]) -> QuerySpecification:
        return normalize_specification(
            QuerySpecification(
                revision=1,
                outputs=tuple(
                    OutputRequirement(
                        requirement_id=f"temporary_{index}",
                        business_label=label,
                        field=FieldRef(resource="asset", field="amount"),
                        aggregation="sum",
                    )
                    for index, label in enumerate(labels)
                ),
            )
        )

    first = build(("累计签收额", "累计融资额"))
    reversed_order = build(("累计融资额", "累计签收额"))

    assert {
        item.business_label: item.requirement_id for item in first.outputs
    } == {
        item.business_label: item.requirement_id for item in reversed_order.outputs
    }
