from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import orjson
import pytest
from langchain_core.messages import AIMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.binding_resolver import apply_confirmed_entity_bindings  # noqa: E402
from apps.chat.plan_context import render_intent_decisions  # noqa: E402
from apps.chat.query_contract import compile_query_contract  # noqa: E402
from apps.chat.semantic_intent import (  # noqa: E402
    ClarificationAnswer,
    ClarificationQuestion,
    IntentBinding,
    IntentContext,
    IntentDecision,
    IntentIssue,
    IntentOption,
    IntentResolution,
    merge_clarification_answers,
    render_planning_question,
)
from apps.chat.steps.clarification import assess_semantic_intent  # noqa: E402
from apps.conversation.outcome import (  # noqa: E402
    awaiting_input_outcome,
    blocked_outcome,
    outcome_is_success,
)


def _context() -> IntentContext:
    return IntentContext(
        status="needs_clarification",
        original_question="按系统统计研发二部每月 task 数",
        issues=[
            IntentIssue(
                key="scope.department_basis",
                kind="scope",
                reason="部门可按任务执行人或项目归属过滤",
            )
        ],
        questions=[
            ClarificationQuestion(
                id="department_basis",
                issue_keys=["scope.department_basis"],
                kind="scope",
                title="研发二部按什么口径认定？",
                recommended_option_ids=["assignee"],
                options=[
                    IntentOption(
                        id="assignee",
                        label="任务执行人所属部门",
                        impact="按执行人组织过滤",
                        resolutions={
                            "scope.department_basis": IntentResolution(
                                label="部门口径",
                                value="任务执行人所属部门",
                            )
                        },
                    ),
                    IntentOption(
                        id="project",
                        label="项目归属部门",
                        impact="按项目组织过滤",
                        resolutions={
                            "scope.department_basis": IntentResolution(
                                label="部门口径",
                                value="项目归属部门",
                            )
                        },
                    ),
                ],
            )
        ],
    )


def test_recommended_option_is_not_confirmed_until_submitted() -> None:
    context = _context()
    assert context.decisions == []
    with pytest.raises(ValueError, match="Missing clarification"):
        merge_clarification_answers(context, [])


def test_answers_become_locked_decisions_and_planning_text() -> None:
    merged = merge_clarification_answers(
        _context(),
        [
            ClarificationAnswer(
                question_id="department_basis",
                option_ids=["assignee"],
            )
        ],
    )
    assert merged.status == "ready"
    assert merged.issues == []
    assert merged.summary.startswith("部门口径: 任务执行人所属部门")
    assert "待确认" not in merged.summary
    assert merged.decisions[0].locked
    assert (
        merged.decisions[0].value["selected_options"][0]["label"]
        == "任务执行人所属部门"
    )
    assert (
        merged.decisions[0].value["selected_options"][0]["impact"] == "按执行人组织过滤"
    )
    planning = render_planning_question(merged, latest_user_text="按推荐口径继续")
    assert "原始问题" in planning
    assert "不得改写或忽略" in planning
    assert "任务执行人所属部门" in planning
    assert "按执行人组织过滤" in planning


def test_custom_answer_requires_one_semantic_reassessment() -> None:
    merged = merge_clarification_answers(
        _context(),
        [
            ClarificationAnswer(
                question_id="department_basis",
                custom_text="仅统计任务验收人当前所属部门",
            )
        ],
    )

    assert merged.status == "evaluating"
    assert merged.issues[0].key == "scope.department_basis"
    assert not merged.decisions[0].locked


def test_custom_answer_is_locked_only_after_semantic_reassessment() -> None:
    class FakeModel:
        received = ""

        def invoke(self, messages: object) -> AIMessage:
            self.received = str(messages[-1].content)
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"口径明确",'
                    '"resolved_decisions":[{"key":"scope.department_basis",'
                    '"kind":"scope","label":"部门口径",'
                    '"value":"仅统计任务验收人当前所属部门",'
                    '"source":"user","bindings":[{"identifier":"accepter",'
                    '"role":"filter","aggregation":"none"}]}],'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                )
            )

    merged = merge_clarification_answers(
        _context(),
        [
            ClarificationAnswer(
                question_id="department_basis",
                custom_text="仅统计任务验收人当前所属部门",
            )
        ],
    )
    model = FakeModel()
    service = SimpleNamespace(
        planning_question="按系统统计研发二部每月 task 数",
        llm=model,
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: task\n(accepter:text)",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    result = assess_semantic_intent(
        service,
        context=merged,
        bindings={},
        time_intent={},
    )
    assessed = result.context

    assert "provisional_decisions" in model.received
    assert "仅统计任务验收人当前所属部门" in model.received
    assert assessed.status == "ready"
    assert assessed.issues == []
    assert assessed.decisions[0].locked
    assert [binding.identifier for binding in assessed.decisions[0].bindings] == [
        "accepter"
    ]


def test_assessor_cannot_mark_unresolved_custom_answer_ready() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"可以查询",'
                    '"resolved_decisions":[],"issues":[],"questions":[],'
                    '"blocking_reasons":[]}'
                )
            )

    merged = merge_clarification_answers(
        _context(),
        [
            ClarificationAnswer(
                question_id="department_basis",
                custom_text="按我们平时的部门口径",
            )
        ],
    )
    service = SimpleNamespace(
        planning_question="按系统统计研发二部每月 task 数",
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: task",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    result = assess_semantic_intent(
        service,
        context=merged,
        bindings={},
        time_intent={},
    )

    assert result.context.status == "blocked"
    assert len(result.attempts) == 2
    assert all(not attempt["valid"] for attempt in result.attempts)
    assert "provisional" in result.attempts[0]["validation_error"]


def test_confirmed_entity_promotes_ambiguous_binding() -> None:
    bindings = {
        "resolved": {},
        "ambiguous": {
            "研发二部": {
                "options": [
                    {
                        "canonical": "研发二部",
                        "targets": [
                            {
                                "table_name": "d_user",
                                "field_name": "organization_name",
                            }
                        ],
                    }
                ]
            }
        },
    }
    context = {
        "decisions": [
            {
                "key": "entity.研发二部",
                "kind": "entity",
                "locked": True,
                "binding_phrase": "研发二部",
                "value": {"selected_options": [{"id": "value_1", "label": "研发二部"}]},
            }
        ]
    }
    result = apply_confirmed_entity_bindings(bindings, context)
    assert result["ambiguous"] == {}
    assert result["resolved"]["研发二部"]["canonical"] == "研发二部"
    assert result["resolved"]["研发二部"]["match"] == "eq"


def test_confirmed_decisions_are_in_plan_context() -> None:
    block = render_intent_decisions(
        {
            "decisions": [
                {
                    "key": "time.field",
                    "label": "时间口径",
                    "locked": True,
                    "value": {
                        "selected_options": [
                            {
                                "id": "created_at",
                                "label": "创建时间",
                                "impact": "使用记录创建时间过滤",
                            }
                        ]
                    },
                }
            ]
        }
    )
    assert "最高优先级" in block
    assert "创建时间" in block


def test_field_mapping_decision_is_not_promoted_to_entity_binding() -> None:
    context = {
        "decisions": [
            {
                "key": "entity.supplier_level",
                "kind": "entity",
                "locked": True,
                "binding_phrase": "",
                "value": {
                    "selected_options": [
                        {
                            "id": "apply_level",
                            "label": "资产层级",
                            "evidence_refs": ["finance.apply_level"],
                        }
                    ]
                },
            }
        ]
    }
    bindings = {"resolved": {}, "ambiguous": {}}

    assert apply_confirmed_entity_bindings(bindings, context) == bindings


def test_option_and_custom_answer_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="either option_ids or custom_text"):
        ClarificationAnswer(
            question_id="department_basis",
            option_ids=["assignee"],
            custom_text="但排除外包人员",
        )


def test_custom_answer_can_reference_an_option_without_selecting_it() -> None:
    merged = merge_clarification_answers(
        _context(),
        [
            ClarificationAnswer(
                question_id="department_basis",
                custom_text="基于 A，但排除外包人员",
            )
        ],
    )

    assert merged.status == "evaluating"
    assert merged.decisions[0].locked is False
    assert merged.decisions[0].value["selected_options"] == []
    assert merged.decisions[0].value["custom_text"] == "基于 A，但排除外包人员"
    assert merged.submitted_answers[0].option_ids == []
    assert merged.submitted_answers[0].custom_text == "基于 A，但排除外包人员"
    assert merged.questions[0].options[0].id == "assignee"


def test_time_basis_selection_needs_a_structured_range_before_ready() -> None:
    context = IntentContext(
        status="needs_clarification",
        original_question="按确权日期统计签收额",
        issues=[
            IntentIssue(
                key="time.basis",
                kind="time",
                reason="需要确认业务时间",
            )
        ],
        questions=[
            ClarificationQuestion(
                id="time_basis",
                issue_keys=["time.basis"],
                kind="time",
                title="按哪个业务时间统计？",
                options=[
                    IntentOption(
                        id="confirm_date",
                        label="确权日期(confirm_date)",
                        resolutions={
                            "time.basis": IntentResolution(
                                label="业务时间",
                                value="确权日期",
                                bindings=[
                                    IntentBinding(
                                        identifier="confirm_date",
                                        role="filter",
                                    )
                                ],
                            )
                        },
                    )
                ],
            )
        ],
    )

    incomplete = merge_clarification_answers(
        context,
        [ClarificationAnswer(question_id="time_basis", option_ids=["confirm_date"])],
    )
    range_without_boundaries = merge_clarification_answers(
        context.model_copy(
            update={"time_intent": {"scope": "explicit", "range_unit": "year"}}
        ),
        [ClarificationAnswer(question_id="time_basis", option_ids=["confirm_date"])],
    )
    complete = merge_clarification_answers(
        context.model_copy(
            update={
                "time_intent": {
                    "scope": "explicit",
                    "start": "2026-01-01",
                    "end_exclusive": "2027-01-01",
                }
            }
        ),
        [ClarificationAnswer(question_id="time_basis", option_ids=["confirm_date"])],
    )

    assert incomplete.status == "evaluating"
    assert range_without_boundaries.status == "evaluating"
    assert complete.status == "ready"


def test_one_question_can_lock_multiple_related_issues() -> None:
    context = IntentContext(
        status="needs_clarification",
        original_question="汇总签收额和融资额",
        issues=[
            IntentIssue(
                key="relation.population",
                kind="relation",
                reason="基础数据集合不明确",
            ),
            IntentIssue(
                key="grain.join_strategy",
                kind="grain",
                reason="关联粒度不明确",
            ),
        ],
        questions=[
            ClarificationQuestion(
                id="population_and_grain",
                issue_keys=["relation.population", "grain.join_strategy"],
                kind="relation",
                title="选择基础集合与关联粒度",
                options=[
                    IntentOption(
                        id="all_entities",
                        label="企业并集后按企业-核企展示",
                        resolutions={
                            "relation.population": IntentResolution(
                                label="基础数据集合",
                                value="融资与资产企业并集",
                            ),
                            "grain.join_strategy": IntentResolution(
                                label="统计粒度",
                                value="企业-核企",
                                bindings=[
                                    IntentBinding(
                                        identifier="company_name",
                                        role="group",
                                    ),
                                    IntentBinding(
                                        identifier="core_company_id",
                                        role="group",
                                    ),
                                ],
                            ),
                        },
                    ),
                    IntentOption(
                        id="financed_entities",
                        label="仅融资企业并按企业-核企展示",
                        resolutions={
                            "relation.population": IntentResolution(
                                label="基础数据集合",
                                value="仅融资企业",
                            ),
                            "grain.join_strategy": IntentResolution(
                                label="统计粒度",
                                value="企业-核企",
                                bindings=[
                                    IntentBinding(
                                        identifier="company_name",
                                        role="group",
                                    ),
                                    IntentBinding(
                                        identifier="core_company_id",
                                        role="group",
                                    ),
                                ],
                            ),
                        },
                    ),
                ],
            )
        ],
    )

    merged = merge_clarification_answers(
        context,
        [
            ClarificationAnswer(
                question_id="population_and_grain",
                option_ids=["all_entities"],
            )
        ],
    )

    assert {decision.key for decision in merged.decisions} == {
        "relation.population",
        "grain.join_strategy",
    }
    decisions = {decision.key: decision for decision in merged.decisions}
    assert (
        decisions["relation.population"].value["selected_options"][0]["resolution"]
        == "融资与资产企业并集"
    )
    assert [binding.identifier for binding in decisions["grain.join_strategy"].bindings] == [
        "company_name",
        "core_company_id",
    ]
    assert decisions["relation.population"].kind == "relation"
    assert decisions["grain.join_strategy"].kind == "grain"
    planning = render_planning_question(merged)
    assert "基础数据集合" in planning
    assert "统计粒度" in planning


def test_awaiting_input_is_normal_terminal_but_blocked_is_not_success() -> None:
    assert outcome_is_success(awaiting_input_outcome())
    assert not outcome_is_success(blocked_outcome("missing schema"))


def test_chat_graph_places_clarity_gate_before_sql_generation() -> None:
    spec = (_BACKEND / "graphs/current/chat.yaml").read_text(encoding="utf-8")
    assert "retrieve_schema: apps.chat.graphs.nodes.nlq.retrieve_schema_node" in spec
    assert "assess_clarity: apps.chat.graphs.nodes.nlq.assess_clarity_node" in spec
    assert "complete_intent: apps.chat.graphs.nodes.nlq.complete_intent_node" in spec
    assert spec.index("- from: assess_clarity") < spec.index("- from: generate_queries")


def test_query_contract_rejects_conflicting_roles_for_one_field() -> None:
    with pytest.raises(ValueError, match="conflicting bindings for amount"):
        compile_query_contract(
            [
                {
                    "key": "metric.amount",
                    "kind": "metric",
                    "label": "金额",
                    "locked": True,
                    "bindings": [
                        {
                            "identifier": "amount",
                            "role": "measure",
                            "aggregation": "sum",
                        },
                        {
                            "identifier": "amount",
                            "role": "filter",
                            "aggregation": "none",
                        },
                    ],
                }
            ]
        )


def test_semantic_assessor_returns_ready_from_validated_json() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"口径唯一",'
                    '"resolved_decisions":[{"key":"metric.orders.count",'
                    '"kind":"metric","label":"订单数","value":"COUNT(*)",'
                    '"source":"user","bindings":[{"identifier":"orders.id",'
                    '"role":"measure","aggregation":"count"}]}],'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                ),
                usage_metadata={
                    "input_tokens": 8,
                    "output_tokens": 4,
                    "total_tokens": 12,
                },
            )

    service = SimpleNamespace(
        planning_question="查询今年订单数",
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            db_schema="# Table: orders\n[(id:bigint),(created_at:datetime)]",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )
    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question="查询今年订单数"),
        bindings={},
        time_intent={"scope": "explicit", "range_unit": "year"},
    )
    assessed, usage, reasoning = result.context, result.usage, result.reasoning
    assert assessed.status == "ready"
    assert assessed.summary == "口径唯一"
    assert usage["total_tokens"] == 12
    assert reasoning == ""


def test_refinement_preserves_unmodified_previous_contract_decisions() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=(
                    '{"intent_mode":"refine","status":"ready",'
                    '"summary":"签收额改用上链金额",'
                    '"resolved_decisions":[{"key":"metric.sign_amount",'
                    '"kind":"metric","label":"签收额","value":"上链金额合计",'
                    '"source":"user","bindings":[{"identifier":"transfer_amt",'
                    '"role":"measure","aggregation":"sum"}]}],'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                )
            )

    base_decisions = [
        IntentDecision(
            key="metric.sign_amount",
            kind="metric",
            label="签收额",
            value="原始资产金额合计",
            bindings=[
                IntentBinding(
                    identifier="orig_asset_amt",
                    role="measure",
                    aggregation="sum",
                )
            ],
        ),
        IntentDecision(
            key="metric.financing_amount",
            kind="metric",
            label="融资额",
            value="融资申请金额合计",
            bindings=[
                IntentBinding(
                    identifier="fin_apply_amt",
                    role="measure",
                    aggregation="sum",
                )
            ],
        ),
        IntentDecision(
            key="dimension.core_company",
            kind="dimension",
            label="核企名称",
            value="核心企业",
            bindings=[
                IntentBinding(identifier="core_company_name", role="attribute")
            ],
        ),
    ]
    context = IntentContext(
        original_question="签收额改用上链金额",
        base_record_id=280,
        base_decisions=base_decisions,
        base_time_intent={
            "scope": "explicit",
            "start": "2026-01-01",
            "end_exclusive": "2027-01-01",
        },
    )
    service = SimpleNamespace(
        generation_question=context.original_question,
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    result = assess_semantic_intent(
        service,
        context=context,
        bindings={},
        time_intent={},
    )

    decisions = {decision.key: decision for decision in result.context.decisions}
    assert result.context.status == "ready"
    assert set(decisions) == {
        "metric.sign_amount",
        "metric.financing_amount",
        "dimension.core_company",
    }
    assert decisions["metric.sign_amount"].bindings[0].identifier == "transfer_amt"
    assert result.context.time_intent["start"] == "2026-01-01"


def test_explicit_query_contract_only_leaves_true_field_mapping_ambiguity() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=orjson.dumps(
                    {
                        "status": "needs_clarification",
                        "summary": "除供应商层级字段映射外均已明确",
                        "resolved_decisions": [
                            {
                                "key": "relation.finance_asset.keys",
                                "kind": "relation",
                                "label": "企业与核企识别口径",
                                "value": "company_name + core_company_id",
                                "source": "user",
                                "bindings": [
                                    {
                                        "identifier": "company_name",
                                        "role": "join",
                                        "aggregation": "none",
                                    },
                                    {
                                        "identifier": "core_company_id",
                                        "role": "join",
                                        "aggregation": "none",
                                    },
                                ],
                            },
                            {
                                "key": "metric.financing",
                                "kind": "metric",
                                "label": "融资额聚合",
                                "value": "SUM(fin_apply_amt)",
                                "source": "user",
                                "bindings": [
                                    {
                                        "identifier": "fin_apply_amt",
                                        "role": "measure",
                                        "aggregation": "sum",
                                    }
                                ],
                            },
                            {
                                "key": "metric.signing",
                                "kind": "metric",
                                "label": "签收额聚合",
                                "value": "SUM(transfer_amt)",
                                "source": "user",
                                "bindings": [
                                    {
                                        "identifier": "transfer_amt",
                                        "role": "measure",
                                        "aggregation": "sum",
                                    }
                                ],
                            },
                            {
                                "key": "relation.population",
                                "kind": "relation",
                                "label": "基础数据集合",
                                "value": "两表合集",
                                "source": "user",
                            },
                        ],
                        "issues": [
                            {
                                "key": "dimension.supplier_level.field",
                                "kind": "dimension",
                                "reason": "供应商层级与资产层级含义不一致",
                            }
                        ],
                        "questions": [
                            {
                                "id": "supplier_level_field",
                                "issue_keys": ["dimension.supplier_level.field"],
                                "kind": "dimension",
                                "title": "您说的供应商层级是否指资产层级(apply_level)？",
                                "recommended_option_ids": ["apply_level"],
                                "options": [
                                    {
                                        "id": "apply_level",
                                        "label": "资产层级",
                                        "resolutions": {
                                            "dimension.supplier_level.field": {
                                                "label": "供应商层级口径",
                                                "value": "资产层级",
                                                "bindings": [
                                                    {
                                                        "identifier": "apply_level",
                                                        "role": "attribute",
                                                        "aggregation": "min",
                                                    }
                                                ],
                                            }
                                        },
                                    },
                                    {
                                        "id": "omit",
                                        "label": "不输出供应商层级",
                                        "resolutions": {
                                            "dimension.supplier_level.field": {
                                                "label": "供应商层级口径",
                                                "value": "不输出",
                                                "bindings": [],
                                                "effect": "omit",
                                            }
                                        },
                                    },
                                ],
                            }
                        ],
                        "blocking_reasons": [],
                    }
                ).decode()
            )

    service = SimpleNamespace(
        generation_question=(
            "通过company_name和core_company_id关联两表并取合集，"
            "汇总fin_apply_amt和transfer_amt，供应商层级取最小值"
        ),
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema=("# Table: finance\n(apply_level:int, 资产层级)\n# Table: asset"),
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question=service.generation_question),
        bindings={},
        time_intent={"scope": "explicit"},
    )
    assessed = result.context

    assert assessed.status == "needs_clarification"
    assert {decision.key for decision in assessed.decisions} == {
        "relation.finance_asset.keys",
        "metric.financing",
        "metric.signing",
        "relation.population",
    }
    assert [question.id for question in assessed.questions] == ["supplier_level_field"]
    assert assessed.questions[0].options[0].label == "资产层级(apply_level)"
    assert {
        option.id: option.resolutions["dimension.supplier_level.field"].effect
        for option in assessed.questions[0].options
    } == {"apply_level": "include", "omit": "omit"}


def test_assessor_evidence_preserves_every_locked_contract_key() -> None:
    class FakeModel:
        received = ""

        def invoke(self, messages: object) -> AIMessage:
            self.received = str(messages[-1].content)
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"完整",'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                )
            )

    model = FakeModel()
    context = IntentContext(
        original_question="查询",
        decisions=[
            {
                "key": "relation.population",
                "kind": "relation",
                "label": "合并口径",
                "value": "两表合集",
            },
                {
                    "key": "grain.supplier",
                    "kind": "grain",
                    "label": "合并口径",
                    "value": "按供应商",
                    "bindings": [
                        {
                            "identifier": "supplier_id",
                            "role": "group",
                            "aggregation": "none",
                        }
                    ],
                },
        ],
    )
    service = SimpleNamespace(
        planning_question="查询",
        llm=model,
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: finance",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    assess_semantic_intent(
        service,
        context=context,
        bindings={},
        time_intent={},
    )

    assert "relation.population" in model.received
    assert "grain.supplier" in model.received


def test_semantic_assessor_normalizes_options_and_single_recommendation() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=(
                    '{"status":"needs_clarification","summary":"需确认口径",'
                    '"issues":[{"key":"scope.department_basis","kind":"scope",'
                    '"reason":"存在不同部门口径"}],'
                    '"questions":[{"id":"department_basis",'
                    '"issue_keys":["scope.department_basis"],"kind":"scope",'
                    '"title":"按什么部门口径？","selection_type":"single",'
                    '"recommended_option_ids":["assignee","project"],'
                    '"options":['
                    '{"id":"assignee","label":"执行人部门","resolutions":'
                    '{"scope.department_basis":{"label":"部门口径","value":"执行人部门"}}},'
                    '{"id":"duplicate","label":"执行人部门","resolutions":'
                    '{"scope.department_basis":{"label":"部门口径","value":"执行人部门"}}},'
                    '{"id":"project","label":"项目部门","resolutions":'
                    '{"scope.department_basis":{"label":"部门口径","value":"项目部门"}}},'
                    '{"id":"creator","label":"创建人部门","resolutions":'
                    '{"scope.department_basis":{"label":"部门口径","value":"创建人部门"}}},'
                    '{"id":"owner","label":"负责人部门","resolutions":'
                    '{"scope.department_basis":{"label":"部门口径","value":"负责人部门"}}}'
                    ']}],"blocking_reasons":[]}'
                )
            )

    service = SimpleNamespace(
        planning_question="按部门统计任务数",
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: task",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )
    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question="按部门统计任务数"),
        bindings={},
        time_intent={},
    )
    assessed = result.context

    question = assessed.questions[0]
    assert [option.label for option in question.options] == [
        "执行人部门",
        "项目部门",
        "创建人部门",
    ]
    assert question.recommended_option_ids == ["assignee"]
    assert question.required
    assert question.allow_custom


def test_semantic_assessor_keeps_recommended_option_inside_cap() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=(
                    '{"status":"needs_clarification","summary":"需确认口径",'
                    '"issues":[{"key":"relation.join","kind":"relation",'
                    '"reason":"关联路径不唯一"}],'
                    '"questions":[{"id":"join","issue_keys":["relation.join"],'
                    '"kind":"relation","title":"企业记录按什么业务标识对应？",'
                    '"selection_type":"single","recommended_option_ids":["project"],'
                    '"options":['
                    '{"id":"asset","label":"资产编号","resolutions":'
                    '{"relation.join":{"label":"企业识别方式","value":"asset_no"}}},'
                    '{"id":"company","label":"企业名称","resolutions":'
                    '{"relation.join":{"label":"企业识别方式","value":"company_name"}}},'
                    '{"id":"core","label":"核企ID","resolutions":'
                    '{"relation.join":{"label":"企业识别方式","value":"core_company_id"}}},'
                    '{"id":"project","label":"项目ID","resolutions":'
                    '{"relation.join":{"label":"企业识别方式","value":"project_id"}}}'
                    ']}],"blocking_reasons":[]}'
                )
            )

    service = SimpleNamespace(
        planning_question="汇总签收额和融资额",
        generation_question="汇总签收额和融资额",
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: asset\n# Table: finance",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question="汇总签收额和融资额"),
        bindings={},
        time_intent={},
    )
    assessed = result.context

    assert [option.id for option in assessed.questions[0].options] == [
        "project",
        "asset",
        "company",
    ]
    assert assessed.questions[0].recommended_option_ids == ["project"]


def test_semantic_assessor_retries_one_invalid_contract() -> None:
    class FakeModel:
        calls = 0

        def invoke(self, _messages: object) -> AIMessage:
            self.calls += 1
            if self.calls == 1:
                return AIMessage(
                    content="not-json",
                    usage_metadata={
                        "input_tokens": 3,
                        "output_tokens": 1,
                        "total_tokens": 4,
                    },
                )
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"口径唯一",'
                    '"resolved_decisions":[{"key":"metric.orders.count",'
                    '"kind":"metric","label":"订单数","value":"COUNT(*)",'
                    '"source":"user","bindings":[{"identifier":"orders.id",'
                    '"role":"measure","aggregation":"count"}]}],'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                ),
                usage_metadata={
                    "input_tokens": 4,
                    "output_tokens": 2,
                    "total_tokens": 6,
                },
            )

    model = FakeModel()
    service = SimpleNamespace(
        planning_question="查询订单数",
        llm=model,
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: orders",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )
    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question="查询订单数"),
        bindings={},
        time_intent={},
    )
    assessed, usage = result.context, result.usage

    assert assessed.status == "ready"
    assert model.calls == 2
    assert usage["total_tokens"] == 10
    assert [attempt["valid"] for attempt in result.attempts] == [False, True]


def test_semantic_assessor_blocks_incomplete_metric_after_bounded_repair() -> None:
    class FakeModel:
        calls = 0

        def invoke(self, _messages: object) -> AIMessage:
            self.calls += 1
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"按签收日期汇总签收额",'
                    '"resolved_decisions":[{'
                    '"key":"metric.sign_amount.aggregation",'
                    '"kind":"calculation","label":"签收额汇总",'
                    '"value":"按签收日期统计",'
                    '"source":"schema","bindings":[{'
                    '"identifier":"sign_date","role":"filter",'
                    '"aggregation":"none"}]}],'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                ),
                usage_metadata={
                    "input_tokens": 5,
                    "output_tokens": 3,
                    "total_tokens": 8,
                },
            )

    model = FakeModel()
    service = SimpleNamespace(
        planning_question="查询今年签收额",
        llm=model,
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: asset\n(sign_amount:decimal, sign_date:date)",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )

    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question="查询今年签收额"),
        bindings={},
        time_intent={"scope": "explicit", "range_unit": "year"},
    )

    assert result.context.status == "blocked"
    assert result.context.questions == []
    assert result.context.blocking_reasons
    assert model.calls == 2
    assert result.usage["total_tokens"] == 16
    assert len(result.attempts) == 2
    assert all(not attempt["valid"] for attempt in result.attempts)
    assert all(
        "measure binding" in attempt["validation_error"]
        for attempt in result.attempts
    )


def test_entity_clarification_merges_duplicate_values_and_caps_candidates() -> None:
    class FakeModel:
        def invoke(self, _messages: object) -> AIMessage:
            return AIMessage(
                content=(
                    '{"status":"ready","summary":"",'
                    '"issues":[],"questions":[],"blocking_reasons":[]}'
                )
            )

    service = SimpleNamespace(
        planning_question="查询研发二部数据",
        llm=FakeModel(),
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: d_user",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
    )
    bindings = {
        "ambiguous": {
            "研发二部": {
                "options": [
                    {
                        "canonical": "研发二部",
                        "targets": [
                            {
                                "table_name": "d_user",
                                "field_name": "organization_name",
                            }
                        ],
                    },
                    {
                        "canonical": "研发二部",
                        "targets": [
                            {
                                "table_name": "d_project",
                                "field_name": "organization_name",
                            }
                        ],
                    },
                    {"canonical": "研发二部（历史）", "targets": []},
                    {"canonical": "研发二部项目组", "targets": []},
                    {"canonical": "研发二部测试组", "targets": []},
                ]
            }
        }
    }

    result = assess_semantic_intent(
        service,
        context=IntentContext(original_question="查询研发二部数据"),
        bindings=bindings,
        time_intent={},
    )
    assessed = result.context

    assert assessed.status == "needs_clarification"
    question = assessed.questions[0]
    assert len(question.options) == 3
    assert [option.label for option in question.options].count("研发二部") == 1
    assert question.options[0].evidence_refs == [
        "field:d_user.organization_name",
        "field:d_project.organization_name",
    ]
    assert question.binding_phrase == "研发二部"
