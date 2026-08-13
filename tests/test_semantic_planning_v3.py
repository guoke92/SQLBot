from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.semantic_planning import (  # noqa: E402
    Ambiguity,
    AmbiguitySet,
    CandidateResolution,
    NeedClarification,
    QueryPlanCandidate,
    enforce_clarification_policy,
)


def test_ambiguity_and_options_receive_stable_ids_without_preselection() -> None:
    decision = NeedClarification(
        ambiguity_set=AmbiguitySet(
            ambiguities=[
                Ambiguity(
                    business_axis="department_scope",
                    business_question="研发二部按什么口径确定？",
                    impact_level="high",
                    candidate_resolutions=[
                        CandidateResolution(
                            label="按负责人所属部门",
                            resolution={"department_scope": "owner"},
                        ),
                        CandidateResolution(
                            label="按项目所属部门",
                            resolution={"department_scope": "project"},
                        ),
                    ],
                )
            ]
        )
    )
    ambiguity = decision.ambiguity_set.ambiguities[0]
    assert ambiguity.ambiguity_id.startswith("amb_")
    assert all(
        item.option_id.startswith("opt_") for item in ambiguity.candidate_resolutions
    )
    assert ambiguity.recommended_candidate_id is None


def test_recommendation_must_reference_an_existing_candidate() -> None:
    with pytest.raises(ValidationError, match="Recommended candidate"):
        Ambiguity(
            business_axis="subject_scope",
            business_question="按哪个主体统计？",
            candidate_resolutions=[
                CandidateResolution(label="主体 A", resolution={"subject": "a"}),
                CandidateResolution(label="主体 B", resolution={"subject": "b"}),
            ],
            recommended_candidate_id="missing",
        )


def test_business_axis_not_question_wording_owns_ambiguity_identity() -> None:
    def build(question: str) -> Ambiguity:
        return Ambiguity(
            business_axis="department_scope",
            business_question=question,
            candidate_resolutions=[
                CandidateResolution(
                    label="负责人部门", resolution={"scope": {"kind": "owner"}}
                ),
                CandidateResolution(
                    label="项目部门", resolution={"scope": {"kind": "project"}}
                ),
            ],
        )

    first = build("研发二部按什么口径确定？")
    rewritten = build("请确认研发二部工作的归属方式？")
    assert first.ambiguity_id == rewritten.ambiguity_id
    assert [item.option_id for item in first.candidate_resolutions] == [
        item.option_id for item in rewritten.candidate_resolutions
    ]


def test_structured_resolutions_not_model_axis_own_ambiguity_identity() -> None:
    first = Ambiguity(
        business_axis="department_scope",
        business_question="研发二部按什么口径确定？",
        candidate_resolutions=[
            CandidateResolution(label="负责人部门", resolution={"scope": "owner"}),
            CandidateResolution(label="项目部门", resolution={"scope": "project"}),
        ],
    )
    renamed = Ambiguity(
        business_axis="organization_scope",
        business_question="研发二部的归属方式是什么？",
        candidate_resolutions=[
            CandidateResolution(label="按人员归属", resolution={"scope": "owner"}),
            CandidateResolution(label="按项目归属", resolution={"scope": "project"}),
        ],
    )
    assert first.ambiguity_id == renamed.ambiguity_id
    assert [item.option_id for item in first.candidate_resolutions] == [
        item.option_id for item in renamed.candidate_resolutions
    ]


def test_clarification_policy_rejects_resolved_or_non_blocking_questions() -> None:
    ambiguity = Ambiguity(
        business_axis="department_scope",
        business_question="按什么部门口径统计？",
        candidate_resolutions=[
            CandidateResolution(label="负责人部门", resolution={"scope": "owner"}),
            CandidateResolution(label="项目部门", resolution={"scope": "project"}),
        ],
    )
    ambiguity_set = AmbiguitySet(ambiguities=[ambiguity])
    with pytest.raises(ValueError, match="repeated resolved business axes"):
        enforce_clarification_policy(
            ambiguity_set, resolved_business_axes={"department_scope"}
        )

    optional = ambiguity.model_copy(update={"can_assume": True})
    with pytest.raises(ValueError, match="must be recorded as assumptions"):
        enforce_clarification_policy(AmbiguitySet(ambiguities=[optional]))


def test_planner_budget_is_based_on_resolved_business_axes() -> None:
    """Two confirmed axes exhaust clarification instead of allowing drip-feed rounds."""
    import re
    from types import SimpleNamespace

    import orjson

    from apps.chat.steps import semantic_planner
    from apps.conversation.models import NlqEvidenceEvent

    evidence = [
        NlqEvidenceEvent(
            run_id="run-1",
            sequence=index,
            kind="clarification_option",
            source="user",
            content=axis,
            structured_value={"ambiguity_id": f"amb-{index}", "business_axis": axis},
        )
        for index, axis in enumerate(("metric_scope", "subject_scope"), start=1)
    ]
    captured: dict = {}

    def _section(content: str, tag: str) -> object:
        match = re.search(rf"<{tag}>\n(.*?)\n</{tag}>", content, re.DOTALL)
        assert match is not None, f"missing <{tag}> section"
        return orjson.loads(match.group(1))

    class Planner:
        def invoke(self, messages):  # noqa: ANN001
            body = messages[1].content
            captured["clarification_budget_exhausted"] = _section(
                body, "clarification_budget_exhausted"
            )
            captured["clarification_policy"] = _section(body, "clarification_policy")
            raise RuntimeError("stop after context capture")

    service = SimpleNamespace(
        llm=SimpleNamespace(bind=lambda **_kwargs: Planner()),
        chat_question=SimpleNamespace(
            db_schema="# Table: t\n(id:int)",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
        protocol=SimpleNamespace(
            type_key="sql",
            build_prompt_bundle=lambda *_args, **_kwargs: SimpleNamespace(rules=""),
        ),
        enable_sql_row_limit=True,
    )
    with pytest.raises(RuntimeError, match="context capture"):
        semantic_planner.plan_semantics_and_query(
            service,
            evidence=evidence,
            previous_specification=None,
            entity_bindings={},
            temporal_parse={},
            max_batch_size=1,
        )
    assert captured["clarification_budget_exhausted"] is True
    assert captured["clarification_policy"]["max_questions_this_round"] == 0


def test_inherited_axes_do_not_exhaust_this_turn_budget() -> None:
    import re
    from types import SimpleNamespace

    import orjson

    from apps.chat.steps import semantic_planner

    captured: dict = {}

    def _section(content: str, tag: str) -> object:
        match = re.search(rf"<{tag}>\n(.*?)\n</{tag}>", content, re.DOTALL)
        assert match is not None, f"missing <{tag}> section"
        return orjson.loads(match.group(1))

    class Planner:
        def invoke(self, messages):  # noqa: ANN001
            body = messages[1].content
            captured["clarification_budget_exhausted"] = _section(
                body, "clarification_budget_exhausted"
            )
            captured["clarification_policy"] = _section(body, "clarification_policy")
            captured["resolved_business_axes"] = _section(body, "resolved_business_axes")
            captured["system"] = messages[0].content
            raise RuntimeError("stop after context capture")

    service = SimpleNamespace(
        llm=SimpleNamespace(bind=lambda **_kwargs: Planner()),
        chat_question=SimpleNamespace(
            db_schema="# Table: t\n(id:int)",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
        protocol=SimpleNamespace(type_key="sql"),
        enable_sql_row_limit=True,
    )
    with pytest.raises(RuntimeError, match="context capture"):
        semantic_planner.plan_semantics_and_query(
            service,
            evidence=[],
            previous_specification=None,
            entity_bindings={},
            temporal_parse={},
            max_batch_size=1,
            conversation_history=[
                {
                    "question": "汇总今年签收额",
                    "clarifications": [
                        {"business_axis": "metric_scope", "content": "签收额"},
                        {"business_axis": "subject_scope", "content": "按企业"},
                    ],
                }
            ],
            inherited_business_axes={"metric_scope", "subject_scope"},
        )
    assert captured["clarification_budget_exhausted"] is False
    assert captured["clarification_policy"]["max_questions_this_round"] == 2
    assert set(captured["resolved_business_axes"]) == {"metric_scope", "subject_scope"}
    assert "$defs" not in captured["system"]
    assert "JSON Schema" not in captured["system"]


def test_public_ambiguity_payload_drops_display_noise() -> None:
    from apps.chat.semantic_planning import public_ambiguity_payload

    payload = public_ambiguity_payload(
        AmbiguitySet(
            summary="需要确认口径",
            ambiguities=[
                Ambiguity(
                    business_axis="amount_metric",
                    business_question="签收额用哪个字段？",
                    reason="字段不唯一",
                    recommendation_reason="更常见",
                    candidate_resolutions=[
                        CandidateResolution(
                            label="原始资产金额",
                            description="按签收",
                            impact="金额变大",
                            resolution={"field": "orig_asset_amt"},
                        ),
                        CandidateResolution(
                            label="融资申请金额",
                            resolution={"field": "fin_apply_amt"},
                        ),
                    ],
                )
            ],
        )
    )
    option = payload["ambiguities"][0]["candidate_resolutions"][0]
    assert "summary" not in payload
    assert "reason" not in payload["ambiguities"][0]
    assert "recommendation_reason" not in payload["ambiguities"][0]
    assert "description" not in option
    assert "impact" not in option
    assert option["label"] == "原始资产金额"
    assert option["resolution"] == {"field": "orig_asset_amt"}


def test_plan_candidate_id_is_stable_for_nested_payload_key_order() -> None:
    first = QueryPlanCandidate(
        payload={"body": {"filters": {"status": "done", "year": 2026}}}
    )
    reordered = QueryPlanCandidate(
        payload={"body": {"filters": {"year": 2026, "status": "done"}}}
    )
    assert first.plan_id == reordered.plan_id
