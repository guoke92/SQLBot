from __future__ import annotations

from apps.chat.semantic_planning import (
    MAX_CLARIFICATION_QUESTIONS,
    PLANNING_DECISION_ADAPTER,
    ClarificationCard,
    ClarificationOption,
    NeedClarification,
    public_interrupt_payload,
)
from apps.chat.steps.query_agent import SemanticReview, _parse_decision
from apps.conversation.run_service import ResumeAnswer, ResumeRequest


def test_legacy_ambiguity_set_coerces_to_questions() -> None:
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "ambiguity_set": {
                "summary": "需要确认统计口径",
                "ambiguities": [
                    {
                        "business_question": "销售额按什么口径统计？",
                        "reason": "两种口径会产生不同金额",
                        "impact_level": "high",
                        "candidate_resolutions": [
                            {
                                "label": "按签约金额",
                                "description": "汇总已签约合同金额",
                                "impact": "反映签约规模",
                                "resolution": {"business_meaning": "按签约金额统计"},
                            },
                            {
                                "label": "按回款金额",
                                "resolution": {"business_meaning": "按回款金额统计"},
                            },
                        ],
                        "recommendation_reason": "问题原文更接近签约口径",
                    }
                ],
                "can_proceed_with_assumptions": False,
            },
            "can_proceed_with_assumptions": True,
        }
    )
    assert isinstance(decision, NeedClarification)
    card = decision.as_card()
    assert len(card.questions) == 1
    assert card.questions[0].question == "销售额按什么口径统计？"
    assert card.questions[0].why == "两种口径会产生不同金额"
    assert [item.meaning for item in card.questions[0].options] == [
        "按签约金额统计",
        "按回款金额统计",
    ]


def test_nested_can_proceed_does_not_fail_clarify_parse() -> None:
    raw = """
    {"decision":"clarify","ambiguity_set":{"summary":"需要确认签收额口径",
     "ambiguities":[{"business_question":"签收额按哪个日期统计？","reason":"日期不同金额不同",
     "impact_level":"high","candidate_resolutions":[
       {"label":"按签收日","resolution":{"business_meaning":"按签收日统计签收额"}},
       {"label":"按确权日","resolution":{"business_meaning":"按确权日统计签收额"}}
     ],"recommendation_reason":"推荐签收日"}],
     "can_proceed_with_assumptions":false}}
    """
    decision = _parse_decision(raw, fallback_description="查询结果")
    assert isinstance(decision, NeedClarification)
    assert decision.questions[0].question == "签收额按哪个日期统计？"


def test_public_interrupt_payload_canonicalizes_history() -> None:
    payload = public_interrupt_payload(
        {
            "ambiguities": [
                {
                    "ambiguity_id": "old",
                    "business_question": "企业指谁？",
                    "candidate_resolutions": [
                        {
                            "option_id": "a",
                            "label": "原始供应商",
                            "resolution": {"business_meaning": "按原始供应商汇总"},
                        },
                        {
                            "option_id": "b",
                            "label": "申请融资企业",
                            "resolution": {"business_meaning": "按申请融资企业汇总"},
                        },
                    ],
                }
            ]
        }
    )
    assert list(payload) == ["questions"]
    assert payload["questions"][0]["question"] == "企业指谁？"
    assert payload["questions"][0]["question_id"] == "old"
    assert payload["questions"][0]["options"][0]["option_id"] == "a"
    assert "candidate_resolutions" not in payload["questions"][0]


def test_resume_answer_accepts_legacy_ambiguity_id() -> None:
    answer = ResumeAnswer.model_validate(
        {"ambiguity_id": "q_1", "mode": "option", "option_id": "opt_1"}
    )
    assert answer.question_id == "q_1"
    dumped = answer.model_dump(mode="json")
    assert dumped["question_id"] == "q_1"
    assert "ambiguity_id" not in dumped


def test_resume_request_rejects_empty_answers() -> None:
    try:
        ResumeRequest.model_validate(
            {"version": 1, "idempotency_key": "k", "answers": []}
        )
    except Exception as exc:
        assert "at least" in str(exc).casefold() or "min_length" in str(exc).casefold()
    else:
        raise AssertionError("empty answers should fail")


def test_reviewer_clarify_uses_questions() -> None:
    review = SemanticReview.model_validate(
        {
            "verdict": "clarify",
            "issues": [{"code": "BUSINESS_AMBIGUITY", "message": "口径不清"}],
            "ambiguity_set": {
                "ambiguities": [
                    {
                        "business_question": "金额用签约还是回款？",
                        "candidate_resolutions": [
                            {"label": "签约", "meaning": "按签约金额"},
                            {"label": "回款", "meaning": "按回款金额"},
                        ],
                    }
                ]
            },
        }
    )
    card = review.clarification_card()
    assert card is not None
    assert isinstance(card, ClarificationCard)
    assert card.questions[0].question == "金额用签约还是回款？"


def _question(index: int) -> dict[str, object]:
    return {
        "question": f"口径 {index} 怎么选？",
        "why": "会显著改变结果",
        "options": [
            {"label": "甲", "meaning": f"选项甲 {index}"},
            {"label": "乙", "meaning": f"选项乙 {index}"},
        ],
    }


def test_clarification_card_accepts_four_questions() -> None:
    card = ClarificationCard.model_validate(
        {"questions": [_question(i) for i in range(MAX_CLARIFICATION_QUESTIONS)]}
    )
    assert len(card.questions) == MAX_CLARIFICATION_QUESTIONS
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "questions": [_question(i) for i in range(MAX_CLARIFICATION_QUESTIONS)],
        }
    )
    assert isinstance(decision, NeedClarification)
    assert len(decision.questions) == MAX_CLARIFICATION_QUESTIONS


def test_clarification_card_rejects_five_questions() -> None:
    payload = {
        "questions": [_question(i) for i in range(MAX_CLARIFICATION_QUESTIONS + 1)]
    }
    try:
        ClarificationCard.model_validate(payload)
    except Exception as exc:
        assert "4" in str(exc) or "max_length" in str(exc).casefold()
    else:
        raise AssertionError("five questions should fail")


def test_clarification_option_keeps_field_identity() -> None:
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "questions": [
                {
                    "question": "企业指谁？",
                    "why": "主体不同结果不同",
                    "options": [
                        {
                            "label": "原始供应商",
                            "meaning": "按原始供应商汇总",
                            "field": "company_name",
                            "field_comment": "原始供应商",
                        },
                        {
                            "label": "申请融资企业",
                            "meaning": "按申请融资企业汇总",
                            "field_name": "sed_company_name",
                            "comment": "申请融资企业",
                        },
                    ],
                }
            ],
        }
    )
    assert isinstance(decision, NeedClarification)
    options = decision.as_card().questions[0].options
    assert options[0].field == "company_name"
    assert options[0].field_comment == "原始供应商"
    assert options[0].fields[0].name == "company_name"
    assert options[1].field == "sed_company_name"
    assert options[1].field_comment == "申请融资企业"


def test_clarification_option_keeps_composite_fields_and_table() -> None:
    decision = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "questions": [
                {
                    "question": "今年按哪个日期？",
                    "why": "日期不同金额不同",
                    "options": [
                        {
                            "label": "分开取业务日期",
                            "meaning": "签收额按签收日，融资额按融资申请日",
                            "fields": [
                                {
                                    "table": "fin_list",
                                    "name": "sign_date",
                                    "comment": "签收日期",
                                },
                                {
                                    "table": "fin_list",
                                    "name": "fin_apply_date",
                                    "comment": "融资申请日",
                                },
                            ],
                        },
                        {
                            "label": "统一按确权日",
                            "meaning": "两指标都按确权日",
                            "fields": [
                                {
                                    "table": "asset_list",
                                    "name": "confirm_date",
                                    "comment": "确权日期",
                                }
                            ],
                        },
                    ],
                }
            ],
        }
    )
    assert isinstance(decision, NeedClarification)
    option = decision.as_card().questions[0].options[0]
    assert option.field == "sign_date"
    assert option.table == "fin_list"
    assert [item.name for item in option.fields] == ["sign_date", "fin_apply_date"]
    dumped = public_interrupt_payload(decision.as_card().model_dump(mode="json"))
    assert dumped["questions"][0]["options"][0]["fields"][1]["name"] == "fin_apply_date"


def test_clarification_fields_override_singular_aliases() -> None:
    option = ClarificationOption.model_validate(
        {
            "label": "确权日",
            "meaning": "按确权日统计",
            "field": "sign_date",
            "field_comment": "签收日期",
            "fields": [
                {"table": "asset_list", "name": "confirm_date", "comment": "确权日期"}
            ],
        }
    )
    assert option.field == "confirm_date"
    assert option.field_comment == "确权日期"
    assert option.table == "asset_list"


def test_continue_chain_walks_oldest_referenced_turns_first() -> None:
    from apps.conversation.run_service import walk_reference_record_ids

    assert walk_reference_record_ids([371], {371: []}) == [371]
    assert walk_reference_record_ids([375], {375: [371], 371: []}) == [371, 375]
    assert walk_reference_record_ids([376], {376: [375], 375: [371], 371: []}) == [
        371,
        375,
        376,
    ]
    assert walk_reference_record_ids([2], {2: [1], 1: [2]}) == [1, 2]
    assert walk_reference_record_ids([], {}) == []


def test_rule_demotes_forbidden_recommended_field() -> None:
    from apps.chat.semantic_planning import constrain_clarification_by_rules

    card = ClarificationCard.model_validate(
        {
            "questions": [
                {
                    "question": "按哪个日期统计今年？",
                    "why": "多个日期字段会改变结果",
                    "options": [
                        {
                            "label": "按建档/创建时间",
                            "meaning": "以 create_time 落在今年",
                            "recommended": True,
                            "fields": [
                                {
                                    "table": "cust_company_info",
                                    "name": "create_time",
                                    "comment": "创建时间",
                                }
                            ],
                        },
                        {
                            "label": "按首次提交认证时间",
                            "meaning": "以 cust_first_submit_auth 落在今年",
                            "fields": [
                                {
                                    "table": "cust_company_info",
                                    "name": "cust_first_submit_auth",
                                    "comment": "首次提交",
                                }
                            ],
                        },
                    ],
                }
            ]
        }
    )
    constrained = constrain_clarification_by_rules(
        card,
        [
            {
                "rule_id": "create-time-is-not-success-time",
                "content": "create_time 不可顶替建档成功日",
                "query_impact": "缺时间字段时不得默用 create_time",
                "field_targets": [{"dataset": "company", "field": "create_time"}],
            }
        ],
    )
    by_label = {item.label: item.recommended for item in constrained.questions[0].options}
    assert by_label["按建档/创建时间"] is False
