from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.plan_context import (  # noqa: E402
    normalize_plan_context_block,
    render_entity_bindings,
    render_plan_context,
    render_query_contract,
    wrap_plan_context,
)
from apps.chat.query_contract import (  # noqa: E402
    FieldRef,
    GroupRequirement,
    OutputRequirement,
    QueryContract,
    RelationPair,
    RelationRequirement,
    TimeWindowRequirement,
)


def _contract() -> QueryContract:
    return QueryContract(
        requirements=[
            GroupRequirement(
                slot_id="slot_department",
                label="部门",
                field=FieldRef(resource="d_user", field="organization_name"),
            ),
            OutputRequirement(
                slot_id="slot_task_count",
                label="任务数",
                field=FieldRef(resource="d_task", field="id"),
                operation="count",
            ),
            TimeWindowRequirement(
                slot_id="slot_time",
                label="2026年创建时间",
                fields=[FieldRef(resource="d_task", field="create_time")],
                mode="explicit",
                start="2026-01-01",
                end_exclusive="2027-01-01",
            ),
            GroupRequirement(
                slot_id="slot_month",
                label="创建月份",
                field=FieldRef(resource="d_task", field="create_time"),
                bucket="month",
            ),
            RelationRequirement(
                slot_id="slot_relation",
                label="任务所属部门范围",
                pairs=[
                    RelationPair(
                        left=FieldRef(resource="d_user", field="id"),
                        right=FieldRef(resource="d_task", field="dispatch_to"),
                    )
                ],
                population="intersection",
            ),
        ]
    )


def test_plan_context_renders_only_the_frozen_contract_as_execution_truth() -> None:
    body = render_plan_context(contract=_contract(), include_playbook=False)
    assert "已冻结查询契约" in body
    assert "[slot_department] group" in body
    assert "[slot_task_count] output" in body
    assert "[slot_time] time_window" in body
    assert "2026-01-01" in body
    assert "decision" not in body.casefold()
    assert "binding role" not in body.casefold()


def test_contract_renderer_does_not_invent_a_default_time_range() -> None:
    contract = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="slot_count",
                label="数量",
                field=FieldRef(field="id"),
                operation="count",
            )
        ]
    )
    rendered = render_query_contract(contract)
    assert "最近" not in rendered
    assert "默认时间" not in rendered


def test_entity_bindings_remain_grounding_evidence_not_a_second_contract() -> None:
    rendered = render_entity_bindings(
        {
            "resolved": {
                "研发二部": {
                    "canonical": "技术研发中心/研发二部",
                    "match": "eq",
                    "targets": [
                        {
                            "table_name": "d_user",
                            "field_name": "organization_name",
                        }
                    ],
                }
            }
        }
    )
    assert "实体绑定" in rendered
    assert "d_user.organization_name" in rendered


def test_plan_context_wrapping_is_idempotent() -> None:
    body = render_plan_context(contract=_contract(), include_playbook=False)
    wrapped = wrap_plan_context(body)
    assert normalize_plan_context_block(body) == wrapped
    assert normalize_plan_context_block(wrapped) == wrapped
