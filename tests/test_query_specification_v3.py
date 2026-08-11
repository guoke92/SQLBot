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
    FieldRef,
    GroupRequirement,
    OutputRequirement,
    PredicateRequirement,
    QuerySpecification,
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
