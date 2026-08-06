from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, SystemMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.binding_resolver import apply_confirmed_entity_bindings  # noqa: E402
from apps.chat.contract.issues import QUESTION_EVIDENCE  # noqa: E402
from apps.chat.contract.validation import validate_contract  # noqa: E402
from apps.chat.query_contract import (  # noqa: E402
    ContractDraft,
    ContractSlot,
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
    SlotEffect,
    TimeWindowRequirement,
)
from apps.chat.semantic_intent import (  # noqa: E402
    ClarificationAnswer,
    ClarificationQuestion,
    IntentContext,
    IntentIssue,
    IntentOption,
    finalize_intent_context,
    intent_context_from_payload,
    merge_clarification_answers,
    new_intent_context,
)
from apps.chat.time_intent import infer_time_intent  # noqa: E402
from apps.chat.steps.clarification import (  # noqa: E402
    IntentAssessment,
    _normalize_assessment,
    _reject_unknown_fields,
    _remap_new_slots,
    _validate_assessment_relation_resolution,
    assess_semantic_intent,
)


def _latest_rows_context() -> IntentContext:
    order_slot = ContractSlot(
        slot_id="slot_0002",
        clause="order",
        label="最新记录的判断口径",
        reason="不同业务时间会改变最新记录",
    )
    option = IntentOption(
        id="create_time",
        label="按创建时间(create_time)",
        effects=[
            SlotEffect(
                slot_id=order_slot.slot_id,
                action="set",
                requirement=OrderRequirement(
                    slot_id=order_slot.slot_id,
                    label=order_slot.label,
                    field=FieldRef(resource="asset", field="create_time"),
                    direction="desc",
                ),
            )
        ],
    )
    return IntentContext(
        status="needs_clarification",
        original_question="查询最新的十条数据",
        draft=ContractDraft(
            requirements=[
                ProjectionRequirement(
                    slot_id="slot_0001",
                    label="查询字段",
                    mode="all",
                ),
                LimitRequirement(slot_id="slot_0003", label="返回条数", value=10),
            ],
            open_slots=[order_slot],
        ),
        questions=[
            ClarificationQuestion(
                id="latest_basis",
                slot_ids=[order_slot.slot_id],
                title="按哪个业务时间判断最新记录？",
                options=[
                    option,
                    IntentOption(
                        id="update_time",
                        label="按更新时间(update_time)",
                        effects=[
                            SlotEffect(
                                slot_id=order_slot.slot_id,
                                action="set",
                                requirement=OrderRequirement(
                                    slot_id=order_slot.slot_id,
                                    label=order_slot.label,
                                    field=FieldRef(
                                        resource="asset", field="update_time"
                                    ),
                                    direction="desc",
                                ),
                            )
                        ],
                    ),
                ],
            )
        ],
    )


def test_structured_answer_fills_slot_and_freezes_without_second_assessment() -> None:
    context = _latest_rows_context()
    merged = merge_clarification_answers(
        context,
        [ClarificationAnswer(question_id="latest_basis", option_ids=["create_time"])],
    )

    assert merged.status == "ready"
    assert merged.contract is not None
    assert not merged.draft.open_slots
    assert {item.clause for item in merged.contract.requirements} == {
        "projection",
        "order",
        "limit",
    }


def test_custom_answer_is_mutually_exclusive_and_remains_targeted_evidence() -> None:
    with pytest.raises(ValueError, match="either option_ids or custom_text"):
        ClarificationAnswer(
            question_id="latest_basis",
            option_ids=["create_time"],
            custom_text="基于 A 但改用签收时间",
        )

    context = _latest_rows_context()
    merged = merge_clarification_answers(
        context,
        [
            ClarificationAnswer(
                question_id="latest_basis",
                custom_text="基于 A，但改为按签收时间",
            )
        ],
    )
    assert merged.status == "evaluating"
    assert [slot.slot_id for slot in merged.draft.open_slots] == ["slot_0002"]
    assert merged.submitted_answers[0].custom_text.startswith("基于 A")


def test_latest_rows_is_order_and_limit_not_a_time_window() -> None:
    assert infer_time_intent("查询最新的十条数据") is None


def test_company_list_records_freeze_as_detail_without_synthetic_grain() -> None:
    companies = [
        "荆门新宙邦新材料有限公司",
        "浙江锦泰电子有限公司",
        "张家港市国泰华荣化工新材料有限公司",
    ]
    contract = ContractDraft(
        requirements=[
            ProjectionRequirement(
                slot_id="projection",
                label="登记记录",
                mode="all",
            ),
            PredicateRequirement(
                slot_id="company_scope",
                label="登记公司范围",
                field=FieldRef(
                    resource="dwd_zhanke_recv_finance_info_full",
                    field="company_name",
                ),
                operator="in",
                values=companies,
            ),
        ]
    ).freeze()

    assert contract.result_mode == "detail"
    assert not contract.clauses("group")
    assert validate_contract(contract) == []


def _confirmed(requirement):
    return requirement.model_copy(
        update={"source": "user", "evidence_refs": (QUESTION_EVIDENCE,)}
    )


def test_freeze_preserves_business_contract_when_planning_metadata_is_missing() -> None:
    draft = ContractDraft(
        requirements=[
            _confirmed(
                GroupRequirement(
                    slot_id="company",
                    label="企业",
                    field=FieldRef(resource="finance", field="company_name"),
                )
            ),
            _confirmed(
                OutputRequirement(
                    slot_id="signed",
                    label="签收额",
                    field=FieldRef(resource="asset", field="amount"),
                    operation="sum",
                )
            ),
            _confirmed(
                OutputRequirement(
                    slot_id="financed",
                    label="融资额",
                    field=FieldRef(resource="finance", field="amount"),
                    operation="sum",
                )
            ),
        ]
    )

    contract = draft.freeze()
    issues = validate_contract(contract)
    assert contract.result_mode == "aggregate"
    assert [(item.code, item.severity) for item in issues] == [
        ("relation_coverage_missing", "blocking")
    ]

    context = finalize_intent_context(
        new_intent_context("按企业汇总签收额和融资额"),
        draft=draft,
        summary="按企业汇总签收额和融资额",
    )
    assert context.status == "blocked"
    assert context.contract == contract
    assert context.contract_issues == issues
    assert context.blocking_reasons == []
    restored = intent_context_from_payload(context.model_dump(mode="json"))
    assert restored.contract == contract
    assert restored.contract_issues == issues


def test_inferred_metric_is_dropped_instead_of_blocking_the_turn() -> None:
    """An unjoinable metric the user never asked for must not block the turn."""
    draft = ContractDraft(
        requirements=[
            _confirmed(
                GroupRequirement(
                    slot_id="company",
                    label="企业",
                    field=FieldRef(resource="finance", field="company_name"),
                )
            ),
            _confirmed(
                OutputRequirement(
                    slot_id="financed",
                    label="融资额",
                    field=FieldRef(resource="finance", field="amount"),
                    operation="sum",
                )
            ),
            OutputRequirement(
                slot_id="signed",
                label="签收额",
                field=FieldRef(resource="asset", field="amount"),
                operation="sum",
            ),
        ]
    )

    context = finalize_intent_context(
        new_intent_context("按企业汇总融资额"),
        draft=draft,
        summary="按企业汇总融资额",
    )

    assert context.status == "ready"
    assert context.contract is not None
    assert [item.slot_id for item in context.contract.requirements] == [
        "company",
        "financed",
    ]
    assert [(item.code, item.slot_id) for item in context.assumptions] == [
        ("dropped_inference", "signed")
    ]


def test_ready_context_recomputes_contract_preparation_invariant() -> None:
    draft = ContractDraft(
        requirements=[
            _confirmed(
                GroupRequirement(
                    slot_id="company",
                    label="企业",
                    field=FieldRef(resource="finance", field="company_name"),
                )
            ),
            _confirmed(
                OutputRequirement(
                    slot_id="amount",
                    label="签收额",
                    field=FieldRef(resource="asset", field="amount"),
                    operation="sum",
                )
            ),
        ]
    )

    with pytest.raises(ValueError, match="blocking contract issues"):
        IntentContext(
            status="ready",
            original_question="按企业汇总签收额",
            draft=draft,
            contract=draft.freeze(),
        )


def test_frozen_contract_is_an_independent_immutable_snapshot() -> None:
    requirement = OutputRequirement(
        slot_id="count",
        label="数量",
        field=FieldRef(resource="task", field="id"),
        operation="count",
    )
    draft = ContractDraft(requirements=[requirement])
    contract = draft.freeze()
    draft.requirements.clear()

    assert [item.slot_id for item in contract.requirements] == ["count"]
    with pytest.raises(AttributeError):
        contract.requirements.append(requirement)  # type: ignore[attr-defined]


def test_contract_rejects_duplicate_slots_and_unknown_derived_operands() -> None:
    first = OutputRequirement(
        slot_id="slot_0001",
        label="签收额",
        field=FieldRef(field="amount"),
        operation="sum",
    )
    with pytest.raises(ValueError, match="duplicate slot"):
        ContractDraft(requirements=[first, first])
    with pytest.raises(ValueError, match="unknown slots"):
        QueryContract(
            requirements=[
                OutputRequirement(
                    slot_id="slot_0002",
                    label="差额",
                    field=FieldRef(field="difference_value"),
                    operation="difference",
                    operands=["slot_0001", "slot_missing"],
                )
            ]
        )


def test_old_intent_payload_is_display_only_and_cannot_be_reused() -> None:
    with pytest.raises(ValueError, match="version 4"):
        intent_context_from_payload(
            {
                "version": 2,
                "status": "ready",
                "original_question": "old",
                "decisions": [],
            }
        )


def test_known_slot_identity_is_preserved_for_set_edit() -> None:
    assessment = IntentAssessment(
        status="ready",
        edits=[
            SlotEffect(
                action="set",
                slot_id="slot_0001",
                requirement=LimitRequirement(
                    slot_id="slot_0001",
                    label="返回条数",
                    value=10,
                ),
            )
        ],
    )
    remapped = _remap_new_slots(assessment, existing_ids={"slot_0001"})
    assert remapped.edits[0].slot_id == "slot_0001"


def test_one_business_answer_can_resolve_multiple_clause_slots() -> None:
    output_slot = ContractSlot(
        slot_id="slot_output",
        clause="output",
        label="签收金额",
        reason="金额口径待确认",
    )
    time_slot = ContractSlot(
        slot_id="slot_time",
        clause="time_window",
        label="签收期间",
        reason="业务时间待确认",
    )
    option = IntentOption(
        id="signed",
        label="按签收口径统计",
        effects=[
            SlotEffect(
                slot_id="slot_output",
                action="set",
                requirement=OutputRequirement(
                    slot_id="slot_output",
                    label="签收金额",
                    field=FieldRef(resource="asset", field="amount"),
                    operation="sum",
                ),
            ),
            SlotEffect(
                slot_id="slot_time",
                action="set",
                requirement=TimeWindowRequirement(
                    slot_id="slot_time",
                    label="签收期间",
                    fields=[FieldRef(resource="asset", field="sign_date")],
                    mode="explicit",
                    start="2026-01-01",
                    end_exclusive="2027-01-01",
                ),
            ),
        ],
    )
    context = IntentContext(
        status="needs_clarification",
        original_question="统计今年签收额",
        draft=ContractDraft(open_slots=[output_slot, time_slot]),
        questions=[
            ClarificationQuestion(
                id="signed_basis",
                slot_ids=["slot_output", "slot_time"],
                title="签收额按什么业务口径统计？",
                options=[
                    option,
                    option.model_copy(update={"id": "other", "label": "其他"}),
                ],
            )
        ],
    )
    merged = merge_clarification_answers(
        context,
        [ClarificationAnswer(question_id="signed_basis", option_ids=["signed"])],
    )
    assert merged.status == "ready"
    assert {item.clause for item in merged.contract.requirements} == {
        "output",
        "time_window",
    }


def test_multi_resource_draft_requires_a_population_question() -> None:
    group = _confirmed(
        GroupRequirement(
            slot_id="company",
            label="企业",
            field=FieldRef(resource="finance", field="company_name"),
        )
    )
    financed = _confirmed(
        OutputRequirement(
            slot_id="financed",
            label="累计融资额",
            field=FieldRef(resource="finance", field="fin_apply_amt"),
            operation="sum",
        )
    )
    signed_slot = ContractSlot(
        slot_id="signed",
        clause="output",
        label="累计签收额",
        reason="金额口径待确认",
    )
    signed_options = [
        IntentOption(
            id=option_id,
            label=label,
            effects=[
                SlotEffect(
                    slot_id="signed",
                    action="set",
                    requirement=OutputRequirement(
                        slot_id="signed",
                        label="累计签收额",
                        field=FieldRef(resource="asset", field=field),
                        operation="sum",
                    ),
                )
            ],
        )
        for option_id, label, field in (
            ("transfer", "按上链金额", "transfer_amt"),
            ("original", "按原始金额", "original_amt"),
        )
    ]
    question = ClarificationQuestion(
        id="signed_basis",
        slot_ids=["signed"],
        title="累计签收额按什么金额统计？",
        options=signed_options,
    )

    with pytest.raises(ValueError, match="relation/population contract slot"):
        _validate_assessment_relation_resolution(
            [group, financed],
            {signed_slot.slot_id: signed_slot},
            [question],
        )


def test_population_answer_closes_the_multi_resource_contract_without_llm() -> None:
    requirements = [
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
    ]
    relation_slot = ContractSlot(
        slot_id="population",
        clause="relation",
        label="企业展示范围",
        reason="两类业务的覆盖范围待确认",
    )

    def population_option(
        option_id: str, population: PopulationPolicy
    ) -> IntentOption:
        return IntentOption(
            id=option_id,
            label=(
                "任一类业务有数据都展示"
                if population == "union"
                else "仅展示两类业务都有数据"
            ),
            effects=[
                SlotEffect(
                    slot_id="population",
                    action="set",
                    requirement=RelationRequirement(
                        slot_id="population",
                        label="企业展示范围",
                        pairs=[
                            RelationPair(
                                left=FieldRef(
                                    resource="asset", field="company_name"
                                ),
                                right=FieldRef(
                                    resource="finance", field="company_name"
                                ),
                            )
                        ],
                        population=population,
                    ),
                )
            ],
        )

    context = IntentContext(
        status="needs_clarification",
        original_question="按企业汇总签收额和融资额",
        draft=ContractDraft(
            requirements=requirements,
            open_slots=[relation_slot],
        ),
        questions=[
            ClarificationQuestion(
                id="population_basis",
                slot_ids=["population"],
                title="哪些企业需要展示？",
                options=[
                    population_option("any", "union"),
                    population_option("both", "intersection"),
                ],
            )
        ],
    )
    merged = merge_clarification_answers(
        context,
        [ClarificationAnswer(question_id="population_basis", option_ids=["any"])],
    )
    assert merged.status == "ready"
    relation = next(
        item
        for item in merged.contract.requirements
        if isinstance(item, RelationRequirement)
    )
    assert relation.population == "union"


def test_technical_question_copy_is_normalized_at_the_presentation_boundary() -> None:
    issue = IntentIssue(
        slot_id="enterprise",
        clause="group",
        label="企业主体",
        reason="企业口径待确认",
    )
    options = [
        IntentOption(
            id=option_id,
            label=label,
            description="通过主键和关联字段找到对应企业",
            impact="不同关联路径会改变企业范围",
            effects=[
                SlotEffect(
                    slot_id="enterprise",
                    action="set",
                    requirement=GroupRequirement(
                        slot_id="enterprise",
                        label="企业主体",
                        field=FieldRef(resource="asset", field=field),
                    ),
                )
            ],
        )
        for option_id, label, field in (
            ("supplier", "供应商", "company_name"),
            ("core", "核企", "core_company_name"),
        )
    ]
    result = _normalize_assessment(
        IntentAssessment(
            status="needs_clarification",
            issues=[issue],
            questions=[
                ClarificationQuestion(
                    id="enterprise_basis",
                    slot_ids=["enterprise"],
                    title="按哪个主键汇总企业？",
                    reason="主键不同会改变结果",
                    options=options,
                )
            ],
        ),
        new_intent_context("按企业汇总"),
        {},
        "# Table: asset\n[\n(company_name:varchar),\n(core_company_name:varchar)\n]",
        None,
        {},
    )
    visible = " ".join(
        [
            result.questions[0].title,
            result.questions[0].reason,
            *(
                text
                for option in result.questions[0].options
                for text in (option.description, option.impact)
            ),
        ]
    )
    assert "主键" not in visible
    assert "关联字段" not in visible
    assert "关联路径" not in visible


def test_non_optional_open_slot_cannot_be_omitted() -> None:
    context = IntentContext(
        original_question="按层级统计",
        draft=ContractDraft(
            open_slots=[
                ContractSlot(
                    slot_id="slot_group",
                    clause="group",
                    label="统计层级",
                    reason="待确认",
                )
            ]
        ),
    )
    assessment = IntentAssessment(
        status="ready",
        edits=[SlotEffect(slot_id="slot_group", action="omit")],
    )
    with pytest.raises(ValueError, match="cannot be omitted"):
        _normalize_assessment(assessment, context, {}, "", None, {})


def test_explicit_time_evidence_cannot_be_rewritten_by_assessor() -> None:
    assessment = IntentAssessment(
        status="ready",
        edits=[
            SlotEffect(
                slot_id="time",
                action="set",
                requirement=TimeWindowRequirement(
                    slot_id="time",
                    label="统计期间",
                    fields=[FieldRef(resource="asset", field="sign_date")],
                    mode="explicit",
                    start="2025-01-01",
                    end_exclusive="2026-01-01",
                ),
            )
        ],
    )
    with pytest.raises(ValueError, match="deterministic bounds"):
        _normalize_assessment(
            assessment,
            new_intent_context("统计 2026 年签收额"),
            {},
            "",
            None,
            {
                "scope": "explicit",
                "start": "2026-01-01",
                "end_exclusive": "2027-01-01",
                "confidence": 1.0,
            },
        )


class _AlwaysInvalidLLM:
    def __init__(self) -> None:
        self.calls: list[list[object]] = []

    def bind(self, **_kwargs: object) -> _AlwaysInvalidLLM:
        return self

    def invoke(self, messages: list[object]) -> AIMessage:
        self.calls.append(messages)
        return AIMessage(content="{}")


def _assessor_service(llm: _AlwaysInvalidLLM) -> SimpleNamespace:
    return SimpleNamespace(
        llm=llm,
        generation_question="统计今年签收额",
        chat_question=SimpleNamespace(
            lang="简体中文",
            db_schema="# Table: asset\n[\n(amount:decimal),\n(sign_date:date)\n]",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
        trans=None,
    )


def test_assessment_repair_keeps_original_evidence_before_degrading() -> None:
    llm = _AlwaysInvalidLLM()
    result = assess_semantic_intent(
        _assessor_service(llm),
        context=new_intent_context("统计今年签收额"),
        bindings={},
        temporal_parse={},
    )

    assert len(result.attempts) == 2
    assert len(llm.calls) == 2
    assert isinstance(llm.calls[1][0], SystemMessage)
    assert "asset" in str(llm.calls[1][1].content)
    assert any(isinstance(message, AIMessage) for message in llm.calls[1])
    # Nothing was confirmed, so there is no executable core to fall back on.
    assert result.context.status == "blocked"
    assert [item.code for item in result.context.contract_issues] == [
        "assessment_unavailable"
    ]


def test_failed_assessment_still_executes_the_user_confirmed_core() -> None:
    """A gate that cannot agree with itself must not strand a clear request."""
    llm = _AlwaysInvalidLLM()
    context = new_intent_context("批量查询这些企业的登记记录")
    context.draft.requirements.append(
        _confirmed(
            PredicateRequirement(
                slot_id="slot_company",
                label="登记公司范围",
                field=FieldRef(resource="asset", field="amount"),
                operator="in",
                values=["A", "B"],
            )
        )
    )
    context.draft.requirements.append(
        OutputRequirement(
            slot_id="slot_hidden",
            label="隐藏数据处理",
            field=FieldRef(resource="asset", field="amount"),
            operation="count",
        )
    )

    result = assess_semantic_intent(
        _assessor_service(llm),
        context=context,
        bindings={},
        temporal_parse={},
    )

    assert result.context.status == "ready"
    assert result.context.contract is not None
    assert [item.slot_id for item in result.context.contract.requirements] == [
        "slot_company"
    ]
    assert [item.code for item in result.context.assumptions] == ["gate_degraded"]


def test_contract_field_mapping_is_checked_before_sql_generation() -> None:
    schema = """# Table: asset, 资产
[
(id:bigint, 编号),
(amount:decimal, 金额)
]"""
    valid = OutputRequirement(
        slot_id="slot_amount",
        label="金额",
        field=FieldRef(resource="asset", field="amount"),
        operation="sum",
    )
    _reject_unknown_fields([valid], schema)
    with pytest.raises(ValueError, match="absent from the retrieved schema"):
        _reject_unknown_fields(
            [
                valid.model_copy(
                    update={"field": FieldRef(resource="asset", field="invented")}
                )
            ],
            schema,
        )

    schema_qualified = schema.replace("# Table: asset", "# Table: public.asset")
    qualified = valid.model_copy(
        update={"field": FieldRef(resource="public.asset", field="amount")}
    )
    _reject_unknown_fields([qualified], schema_qualified)
    _reject_unknown_fields([valid], schema_qualified)


def test_new_context_carries_only_the_frozen_base_contract() -> None:
    base = QueryContract(
        requirements=[
            OutputRequirement(
                slot_id="slot_0001",
                label="数量",
                field=FieldRef(resource="task", field="id"),
                operation="count",
            )
        ]
    )
    context = new_intent_context("改成按月统计", base_record_id=8, base_contract=base)
    assert context.status == "evaluating"
    assert context.contract is None
    assert context.draft.requirements == list(base.requirements)
    assert context.base_record_id == 8


def test_confirmed_entity_predicate_promotes_the_existing_candidate() -> None:
    bindings = {
        "ambiguous": {
            "研发二部": {
                "options": [
                    {
                        "canonical": "技术研发中心/研发二部",
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
        "resolved": {},
    }
    requirement = PredicateRequirement(
        slot_id="entity_1",
        label="研发二部",
        source="terminology",
        field=FieldRef(resource="d_user", field="organization_name"),
        operator="eq",
        values=["技术研发中心/研发二部"],
    )
    context = IntentContext(
        status="ready",
        original_question="研发二部任务数",
        draft=ContractDraft(requirements=[requirement]),
        contract=QueryContract(requirements=[requirement]),
    )

    result = apply_confirmed_entity_bindings(bindings, context.model_dump(mode="json"))

    assert result["resolved"]["研发二部"]["canonical"] == "技术研发中心/研发二部"
    assert "研发二部" not in result["ambiguous"]


def _projection(slot_id: str, label: str, field: str) -> ProjectionRequirement:
    return ProjectionRequirement(
        slot_id=slot_id,
        label=label,
        mode="listed",
        fields=[FieldRef(resource="cust_company", field=field)],
        source="user",
        evidence_refs=[QUESTION_EVIDENCE],
    )


def test_projecting_two_different_fields_is_not_a_duplicate() -> None:
    """Showing the name and the phone are two separately confirmable choices.

    Treating every projection as the same clause turned answering a
    "which phone?" clarification into a hard failure, because merging the
    answer produced a second projection.
    """
    draft = ContractDraft(
        requirements=[
            _projection("slot_0002", "企业名称", "company_name"),
            _projection("slot_0003", "建档联系人电话", "legal_person_mobile"),
        ]
    )

    assert len(draft.requirements) == 2


def test_projecting_the_same_field_twice_is_still_a_duplicate() -> None:
    with pytest.raises(ValueError, match="duplicate semantic requirement"):
        ContractDraft(
            requirements=[
                _projection("slot_0002", "企业名称", "company_name"),
                _projection("slot_0003", "公司名", "company_name"),
            ]
        )


def test_clarification_option_that_cannot_form_a_contract_is_rejected() -> None:
    """A card whose answer cannot be merged must fail while repair is possible.

    Once the user has answered, no retry is left, so an option colliding with
    an existing clause has to be caught during assessment review instead.
    """
    context = new_intent_context("查询企业名称")
    context = context.model_copy(
        update={
            "draft": ContractDraft(
                requirements=[_projection("slot_0002", "企业名称", "company_name")]
            )
        }
    )

    def option(option_id: str, label: str, field: str) -> IntentOption:
        return IntentOption(
            id=option_id,
            label=label,
            effects=[
                SlotEffect(
                    slot_id="phone",
                    action="set",
                    requirement=_projection("phone", "联系人电话", field),
                )
            ],
        )

    options = [
        option("mobile", "法定代表人手机号", "legal_person_mobile"),
        option("same_field", "仍然取企业名称", "company_name"),
    ]

    with pytest.raises(ValueError, match="cannot form a valid contract"):
        _normalize_assessment(
            IntentAssessment(
                status="needs_clarification",
                issues=[
                    IntentIssue(
                        slot_id="phone",
                        clause="projection",
                        label="联系人电话口径",
                        reason="电话来源待确认",
                        evidence_refs=[QUESTION_EVIDENCE],
                    )
                ],
                questions=[
                    ClarificationQuestion(
                        id="phone_source",
                        slot_ids=["phone"],
                        title="电话按哪个口径取？",
                        options=options,
                    )
                ],
            ),
            context,
            {},
            "# Table: cust_company\n[\n(company_name:varchar),\n"
            "(legal_person_mobile:varchar)\n]",
            None,
            {},
        )
