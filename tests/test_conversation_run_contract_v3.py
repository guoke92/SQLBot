from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.models import (  # noqa: E402
    ConversationInterrupt,
    NlqEvidenceEvent,
)
from apps.conversation.run_service import (  # noqa: E402
    CorrectionRequest,
    ResumeAnswer,
    ResumeRequest,
    active_evidence,
    create_interrupt,
    finalize_run,
    interrupt_payload_identity,
)


def test_option_and_custom_answers_are_strictly_exclusive() -> None:
    with pytest.raises(ValidationError, match="cannot include text"):
        ResumeAnswer(
            ambiguity_id="amb_1",
            mode="option",
            option_id="opt_a",
            text="基于 A 再补充",
        )
    with pytest.raises(ValidationError, match="cannot include option_id"):
        ResumeAnswer(
            ambiguity_id="amb_1",
            mode="custom",
            option_id="opt_a",
            text="基于 A 再补充",
        )


def test_resume_request_rejects_duplicate_ambiguity_answers() -> None:
    with pytest.raises(ValidationError, match="only once"):
        ResumeRequest(
            version=1,
            idempotency_key="request-1",
            answers=[
                ResumeAnswer(ambiguity_id="amb_1", mode="option", option_id="opt_a"),
                ResumeAnswer(ambiguity_id="amb_1", mode="custom", text="自定义口径"),
            ],
        )


def test_correction_request_targets_one_immutable_answer() -> None:
    request = CorrectionRequest(
        version=1,
        idempotency_key="correction-1",
        supersedes_evidence_id="evidence-1",
        answer=ResumeAnswer(
            ambiguity_id="amb_1", mode="custom", text="改为按负责人部门"
        ),
    )
    assert request.supersedes_evidence_id == "evidence-1"
    assert request.answer.option_id is None


def test_effective_evidence_is_projected_without_mutating_history() -> None:
    original = NlqEvidenceEvent(
        evidence_id="e1",
        run_id="run-1",
        sequence=1,
        kind="clarification_option",
        source="user",
        content="按项目部门",
    )
    correction = NlqEvidenceEvent(
        evidence_id="e2",
        run_id="run-1",
        sequence=2,
        kind="user_correction",
        source="user",
        content="改为按负责人部门",
        supersedes="e1",
    )

    class Result:
        def scalars(self):
            return self

        def all(self):
            return [original, correction]

    class Session:
        def exec(self, _statement):
            return Result()

    effective = active_evidence(Session(), "run-1")  # type: ignore[arg-type]
    assert [item.evidence_id for item in effective] == ["e2"]
    assert original.content == "按项目部门"


def test_interrupt_identity_ignores_rewording_but_not_resolution_changes() -> None:
    first = {
        "summary": "请确认",
        "ambiguities": [
            {
                "ambiguity_id": "amb_scope",
                "business_axis": "department_scope",
                "business_question": "研发二部怎么确定？",
                "candidate_resolutions": [
                    {"option_id": "opt_a", "resolution": {"scope": "owner"}},
                    {"option_id": "opt_b", "resolution": {"scope": "project"}},
                ],
            }
        ],
    }
    reworded = {
        **first,
        "summary": "需要确认统计归属",
        "ambiguities": [
            {
                **first["ambiguities"][0],
                "business_question": "按哪种部门归属统计？",
            }
        ],
    }
    changed = {
        **reworded,
        "ambiguities": [
            {
                **reworded["ambiguities"][0],
                "candidate_resolutions": [
                    {"option_id": "opt_a", "resolution": {"scope": "owner"}},
                    {"option_id": "opt_b", "resolution": {"scope": "either"}},
                ],
            }
        ],
    }
    assert interrupt_payload_identity(first) == interrupt_payload_identity(reworded)
    assert interrupt_payload_identity(first) != interrupt_payload_identity(changed)


def test_consumed_interrupt_is_reused_when_langgraph_replays_pause_node() -> None:
    payload = {
        "ambiguities": [
            {
                "ambiguity_id": "amb_scope",
                "business_axis": "department_scope",
                "candidate_resolutions": [
                    {"option_id": "opt_a", "resolution": {"scope": "owner"}},
                    {"option_id": "opt_b", "resolution": {"scope": "project"}},
                ],
            }
        ]
    }
    consumed = ConversationInterrupt(
        interrupt_id="interrupt-1",
        run_id="run-1",
        version=1,
        status="consumed",
        payload=payload,
    )
    locked_run = SimpleNamespace(status="running")
    lock_result = Mock()
    lock_result.one.return_value = locked_run
    latest_result = Mock()
    latest_result.one_or_none.return_value = consumed
    session = Mock()
    session.exec.side_effect = [lock_result, latest_result]

    reused = create_interrupt(session, run_id="run-1", payload=payload)

    assert reused is consumed
    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_append_evidence_reads_max_sequence_via_scalar() -> None:
    """session.exec(select(max)).one() returns Row; sequence must use scalar()."""
    from apps.conversation.run_service import append_evidence

    lock_result = Mock()
    lock_result.first.return_value = "run-1"
    session = Mock()
    session.exec.return_value = lock_result
    session.scalar.return_value = 3

    event = append_evidence(
        session,
        run_id="run-1",
        kind="user_question",
        source="user",
        content="本月签收金额",
    )

    session.scalar.assert_called_once()
    assert event.sequence == 4
    session.add.assert_called_once_with(event)
    session.flush.assert_called_once()


def test_finalize_run_commits_record_domain_and_terminal_state_once() -> None:
    run = SimpleNamespace(
        run_id="run-1",
        chat_record_id=99,
        status="running",
        current_node="complete",
        error_summary=None,
        completed_at=None,
        active_interrupt_id="interrupt-1",
        update_time=None,
    )
    nlq = SimpleNamespace(
        execution_status="running",
        result_quality=None,
        update_time=None,
    )
    run_result = Mock()
    run_result.one.return_value = run
    nlq_result = Mock()
    nlq_result.one_or_none.return_value = nlq
    update_result = Mock(rowcount=1)
    session = Mock()
    session.exec.side_effect = [run_result, nlq_result]
    session.execute.return_value = update_result

    finalized = finalize_run(
        session,
        run_id="run-1",
        status="failed",
        current_node="complete",
        result_quality={"score": 0},
        record_snapshot={"terminal": True, "error": "invalid plan"},
        error_summary="invalid plan",
    )

    assert finalized is run
    assert run.status == "failed"
    assert run.active_interrupt_id is None
    assert nlq.execution_status == "failed"
    assert nlq.result_quality == {"score": 0}
    session.commit.assert_called_once()
