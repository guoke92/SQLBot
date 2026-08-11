from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.query_specification import (  # noqa: E402
    FieldRef,
    OutputRequirement,
    QuerySpecification,
)
from apps.chat.planning import BatchParseResult  # noqa: E402
from apps.chat.specification_validation import (  # noqa: E402
    validate_specification,
    validate_specification_transition,
)
from apps.protocol.sql.identifier_validation import (  # noqa: E402
    analyze_query_specification_alignment,
)


def _specification() -> QuerySpecification:
    return QuerySpecification(
        revision=1,
        outputs=(
            OutputRequirement(
                requirement_id="req_total",
                business_label="客户数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count",
            ),
        ),
        confidence=0.9,
    )


def test_schema_validation_and_sql_alignment_use_same_specification() -> None:
    specification = _specification()
    schema = "# Table: customer\n(id: bigint, name: varchar)"
    assert not [
        issue
        for issue in validate_specification(specification, schema_text=schema)
        if issue.severity == "blocking"
    ]
    result = analyze_query_specification_alignment(
        ["SELECT COUNT(id) AS customer_count FROM customer"],
        specification,
        dialect="mysql",
    )
    assert result.status == "verified"
    assert result.error is None


def test_empty_result_is_not_part_of_plan_alignment() -> None:
    result = analyze_query_specification_alignment(
        ["SELECT COUNT(id) AS customer_count FROM customer WHERE 1 = 0"],
        _specification(),
        dialect="mysql",
    )
    assert result.status in {"verified", "partial"}


def test_unobservable_alignment_does_not_trigger_physical_repair() -> None:
    unobservable = BatchParseResult(
        plans=[{"sql": "SELECT id FROM customer"}],
        plan_validated=True,
        contract_status="partial",
        contract_message=None,
    )
    mismatch = BatchParseResult(
        plans=[{"sql": "SELECT id FROM customer"}],
        plan_validated=True,
        contract_status="partial",
        contract_message="missing predicate requirement",
    )
    assert not unobservable.requires_contract_repair
    assert mismatch.requires_contract_repair


def test_semantic_reference_is_allowed_until_physical_grounding() -> None:
    specification = QuerySpecification(
        revision=1,
        outputs=(
            OutputRequirement(
                requirement_id="req_total",
                business_label="客户数",
                field=FieldRef(semantic_ref="customer_identifier"),
                aggregation="count_distinct",
                source="user",
                evidence_refs=("user:question",),
            ),
        ),
    )
    issues = validate_specification(
        specification,
        schema_text="# Table: customer\n(id: bigint)",
        available_evidence_refs={"user:question"},
    )
    assert not [item for item in issues if item.severity == "blocking"]
    alignment = analyze_query_specification_alignment(
        ["SELECT COUNT(DISTINCT id) AS customer_count FROM customer"],
        specification,
        dialect="mysql",
    )
    assert alignment.status == "partial"
    assert alignment.error is None


def test_specification_cannot_invent_evidence_references() -> None:
    issues = validate_specification(
        _specification(),
        schema_text="# Table: customer\n(id: bigint)",
        available_evidence_refs={"user:question"},
    )
    assert not [item for item in issues if item.code == "unknown_evidence_reference"]

    invented = QuerySpecification(
        revision=1,
        outputs=(
            OutputRequirement(
                requirement_id="req_total",
                business_label="客户数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count",
                evidence_refs=("user:answer:invented",),
            ),
        ),
    )
    invented_issues = validate_specification(
        invented,
        schema_text="# Table: customer\n(id: bigint)",
        available_evidence_refs={"user:question"},
    )
    assert any(item.code == "unknown_evidence_reference" for item in invented_issues)


def test_revision_cannot_silently_remove_confirmed_user_requirement() -> None:
    previous = QuerySpecification(
        revision=1,
        outputs=(
            OutputRequirement(
                requirement_id="req_total",
                business_label="去重客户数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count_distinct",
                source="user",
                evidence_refs=("user:answer:e1",),
            ),
        ),
    )
    rewritten = QuerySpecification(
        revision=2,
        outputs=(
            OutputRequirement(
                requirement_id="req_changed",
                business_label="客户行数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count",
            ),
        ),
    )
    issues = validate_specification_transition(
        previous,
        rewritten,
        active_evidence_refs={"user:answer:e1"},
    )
    assert [item.code for item in issues] == [
        "confirmed_requirement_changed_without_correction"
    ]
    assert not validate_specification_transition(
        previous,
        rewritten,
        active_evidence_refs={"user:answer:e2"},
    )


def test_user_evidence_is_protected_even_when_model_mislabels_source() -> None:
    previous = QuerySpecification(
        revision=1,
        outputs=(
            OutputRequirement(
                requirement_id="req_total",
                business_label="去重客户数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count_distinct",
                source="model",
                evidence_refs=("user:answer:e1",),
            ),
        ),
    )
    rewritten = QuerySpecification(
        revision=2,
        outputs=(
            OutputRequirement(
                requirement_id="req_changed",
                business_label="客户行数",
                field=FieldRef(resource="customer", field="id"),
                aggregation="count",
            ),
        ),
    )
    issues = validate_specification_transition(
        previous,
        rewritten,
        active_evidence_refs={"user:answer:e1"},
    )
    assert [item.code for item in issues] == [
        "confirmed_requirement_changed_without_correction"
    ]
