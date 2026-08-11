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


def test_plan_candidate_id_is_stable_for_nested_payload_key_order() -> None:
    first = QueryPlanCandidate(
        payload={"body": {"filters": {"status": "done", "year": 2026}}}
    )
    reordered = QueryPlanCandidate(
        payload={"body": {"filters": {"year": 2026, "status": "done"}}}
    )
    assert first.plan_id == reordered.plan_id
