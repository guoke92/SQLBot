from __future__ import annotations

import pytest

from apps.chat.answer_payload import project_turn_answer
from apps.chat.context_bundle import ContextSection, budget_context_sections
from apps.chat.intent_validation import validate_plan_against_intent
from apps.chat.plan_facts import extract_sql_plan_facts
from apps.chat.query_intent import (
    QueryIntent,
    build_intent_revision,
    calculate_intent_confidence,
    intent_item_catalog,
    resolve_intent_item_key,
)
from apps.chat.semantic_planning import (
    PLANNING_DECISION_ADAPTER,
    NeedClarification,
    Ready,
)
from apps.chat.turn_router import route_turn
from apps.protocol.rest.protocol import RestProtocol
from apps.protocol.sql.protocol import SqlProtocol


def _intent() -> QueryIntent:
    return QueryIntent.model_validate(
        {
            "purpose": "统计今年每月新增客户数",
            "datasets": [
                {
                    "purpose": "展示每月新增客户数",
                    "required": True,
                    "mode": "aggregate",
                    "subject": "客户",
                    "outputs": [
                        {
                            "business_name": "月份",
                            "semantic_definition": "客户创建日期所在月份",
                            "role": "attribute",
                        },
                        {
                            "business_name": "新增客户数",
                            "semantic_definition": "去重后的新增客户数量",
                            "role": "measure",
                            "aggregation": "count_distinct",
                        },
                    ],
                    "groupings": [{"business_name": "月份", "grain": "month"}],
                    "filters": [],
                    "time": {
                        "original_expression": "今年",
                        "start": "2026-01-01",
                        "end_exclusive": "2027-01-01",
                        "grain": "month",
                        "basis_concept": "客户创建日期",
                    },
                    "population": "有效客户",
                    "ordering": [{"business_name": "月份", "direction": "asc"}],
                }
            ],
            "confidence": 0.9,
        }
    )


def test_query_intent_contains_no_physical_schema() -> None:
    payload = _intent().model_dump(mode="json")
    assert "table" not in str(payload).casefold()
    assert "join" not in str(payload).casefold()


def test_plan_facts_never_create_an_intent() -> None:
    facts = extract_sql_plan_facts(
        "SELECT date_format(created_at, '%Y-%m') month, count(distinct id) n "
        "FROM customer GROUP BY month"
    )
    assert facts.resources
    assert not hasattr(facts, "to_intent")
    with pytest.raises(TypeError):
        build_intent_revision(  # type: ignore[arg-type]
            facts,
            revision=1,
            status="accepted",
        )


def test_service_owns_intent_item_ids() -> None:
    intent = _intent()
    first_output = resolve_intent_item_key(
        intent, dataset_index=0, kind="output", item_index=0
    )
    revision = build_intent_revision(intent, revision=1, status="accepted")
    assert first_output in revision.item_catalog
    assert "requirement_id" not in intent.model_dump_json()


def test_intent_confidence_comes_from_evidence_not_model_rating() -> None:
    intent = _intent()
    inferred = dict.fromkeys(intent_item_catalog(intent), ())
    confirmed = dict.fromkeys(
        intent_item_catalog(intent),
        ("user:answer:evidence-1",),
    )
    assert calculate_intent_confidence(intent, inferred) == 0.45
    assert calculate_intent_confidence(intent, confirmed) == 1.0


def test_first_turn_router_does_not_call_model() -> None:
    called = False

    def model_router(_: str) -> dict[str, object]:
        nonlocal called
        called = True
        return {}

    route = route_turn("你好，查询今年销售额", model_router=model_router)
    assert route.task_kind == "query"
    assert route.source == "deterministic"
    assert not called


def test_context_budget_never_drops_user_evidence() -> None:
    kept, truncated = budget_context_sections(
        [
            ContextSection(name="user", content="用户原始问题", trusted=True),
            ContextSection(name="schema", content="x" * 3000),
        ],
        max_tokens=10,
    )
    assert kept["user"] == "用户原始问题"
    assert "schema" not in kept
    assert truncated[0]["section"] == "schema"


def _grounding(intent: QueryIntent) -> list[dict[str, object]]:
    return [
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="subject", item_index=0
            ),
            "resources": ["customer"],
            "fields": [],
        },
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="population", item_index=0
            ),
            "resources": ["customer"],
            "fields": ["deleted"],
        },
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="output", item_index=0
            ),
            "resources": ["customer"],
            "fields": ["created_at"],
        },
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="output", item_index=1
            ),
            "resources": ["customer"],
            "fields": ["id"],
        },
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="group", item_index=0
            ),
            "resources": ["customer"],
            "fields": ["created_at"],
        },
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="time", item_index=0
            ),
            "resources": ["customer"],
            "fields": ["created_at"],
        },
        {
            "intent_item_id": resolve_intent_item_key(
                intent, dataset_index=0, kind="order", item_index=0
            ),
            "resources": ["customer"],
            "fields": ["created_at"],
        },
    ]


def test_grounding_is_verified_against_physical_plan_facts() -> None:
    intent = _intent()
    revision = build_intent_revision(intent, revision=1, status="accepted")
    sql = """
        SELECT DATE_FORMAT(created_at, '%Y-%m') AS month,
               COUNT(DISTINCT id) AS customer_count
          FROM customer
         WHERE deleted = 0
           AND created_at >= '2026-01-01'
           AND created_at < '2027-01-01'
         GROUP BY DATE_FORMAT(created_at, '%Y-%m')
         ORDER BY DATE_FORMAT(created_at, '%Y-%m') ASC
    """
    candidate = {
        "dataset_index": 0,
        "payload": {"sql": sql},
        "grounding_manifest": _grounding(intent),
    }
    assert validate_plan_against_intent(revision, candidate).status == "valid"

    lied = {
        **candidate,
        "grounding_manifest": [
            *candidate["grounding_manifest"][:-1],
            {
                **candidate["grounding_manifest"][-1],
                "fields": ["invented_field"],
            },
        ],
    }
    report = validate_plan_against_intent(revision, lied)
    assert report.status == "rejected"
    assert any(issue.code == "PLAN_GROUNDING_FIELD_MISMATCH" for issue in report.issues)


def test_query_agent_can_explicitly_return_unsupported() -> None:
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "unsupported",
            "message": "当前数据源没有可支持该问题的数据。",
            "reason_code": "schema_not_supported",
        }
    )
    assert decision.decision == "unsupported"
    assert decision.reason_code == "SCHEMA_NOT_SUPPORTED"


def test_clarification_payload_keeps_business_explanations() -> None:
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "questions": [
                {
                    "question": "销售额按什么口径统计？",
                    "why": "两种口径会产生不同金额",
                    "options": [
                        {
                            "label": "按签约金额",
                            "meaning": "汇总已签约合同金额",
                            "recommended": True,
                        },
                        {
                            "label": "按回款金额",
                            "meaning": "汇总实际到账金额",
                        },
                    ],
                }
            ],
        }
    )

    assert isinstance(decision, NeedClarification)
    payload = decision.as_card().model_dump(mode="json")
    question = payload["questions"][0]
    assert question["question"] == "销售额按什么口径统计？"
    assert question["why"] == "两种口径会产生不同金额"
    assert question["options"][0]["meaning"] == "汇总已签约合同金额"
    assert question["options"][0]["recommended"] is True


def test_clarification_marker_is_not_used_as_business_label() -> None:
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "questions": [
                {
                    "question": "部门归属按什么口径？",
                    "options": [
                        {
                            "label": "A",
                            "meaning": "按负责人所属部门统计",
                        },
                        {
                            "label": "B",
                            "meaning": "按项目所属部门统计",
                        },
                    ],
                }
            ],
        }
    )
    assert isinstance(decision, NeedClarification)
    payload = decision.as_card().model_dump(mode="json")
    labels = [item["label"] for item in payload["questions"][0]["options"]]
    assert labels == ["按负责人所属部门统计", "按项目所属部门统计"]


def test_protocol_native_candidate_does_not_require_legacy_success_envelope() -> None:
    sql_plan = SqlProtocol("mysql").parse_candidate_payload(
        {"sql": "SELECT COUNT(*) FROM customer;"}
    )
    assert sql_plan.success
    assert sql_plan.statement == "SELECT COUNT(*) FROM customer"

    rest_plan = RestProtocol("api").parse_candidate_payload(
        {"endpoint": "customer_list", "params": {"status": "active"}}
    )
    assert rest_plan.success
    assert rest_plan.payload == {
        "endpoint": "customer_list",
        "params": {"status": "active"},
    }


def test_query_agent_ready_contract_contains_only_description_and_query() -> None:
    first = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "ready",
            "queries": [{"description": "查询一", "sql": "SELECT 1"}],
        }
    )
    repaired = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "ready",
            "queries": [{"description": "查询二", "sql": "SELECT 2"}],
        }
    )
    assert isinstance(first, Ready)
    assert isinstance(repaired, Ready)
    assert first.queries[0].sql == "SELECT 1"
    assert repaired.queries[0].sql == "SELECT 2"
    assert "intent" not in first.model_dump(mode="json")


def test_turn_answer_projection_never_publishes_failed_dataset() -> None:
    projected = project_turn_answer(
        {
            "status": "degraded",
            "content": "部分结果可用",
            "datasets": [
                {
                    "dataset_id": "ok",
                    "status": "succeeded",
                    "fields": ["n"],
                    "rows": [{"n": 1}],
                },
                {
                    "dataset_id": "bad",
                    "status": "failed",
                    "error": {"code": "QUERY_FAILED", "message": "失败"},
                },
            ],
        }
    )
    assert len(projected["steps"]) == 1
    assert projected["steps"][0]["data"]["data"] == [{"n": 1}]
    assert projected["outcome"]["status"] == "degraded"
    assert len(projected["outcome"]["failures"]) == 1
