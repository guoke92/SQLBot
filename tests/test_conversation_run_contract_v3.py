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
    ConversationRunCancelled,
    CorrectionRequest,
    ResumeAnswer,
    ResumeRequest,
    active_evidence,
    claim_run,
    create_interrupt,
    finalize_run,
    interrupt_payload_identity,
    record_run_dispatch,
    require_active_run,
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


def test_effective_context_evidence_uses_latest_snapshot_only() -> None:
    original_schema = NlqEvidenceEvent(
        evidence_id="schema-1",
        run_id="run-1",
        sequence=1,
        kind="schema_fact",
        source="schema",
        content="schema:original",
    )
    user_answer = NlqEvidenceEvent(
        evidence_id="answer-1",
        run_id="run-1",
        sequence=2,
        kind="clarification_option",
        source="user",
        content="按签收日统计",
    )
    refreshed_schema = NlqEvidenceEvent(
        evidence_id="schema-2",
        run_id="run-1",
        sequence=3,
        kind="schema_fact",
        source="schema",
        content="schema:refreshed",
    )

    class Result:
        def scalars(self):
            return self

        def all(self):
            return [original_schema, user_answer, refreshed_schema]

    class Session:
        def exec(self, _statement):
            return Result()

    effective = active_evidence(Session(), "run-1")  # type: ignore[arg-type]

    assert [item.evidence_id for item in effective] == ["answer-1", "schema-2"]


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
    lock_result.scalars.return_value.one.return_value = locked_run
    latest_result = Mock()
    latest_result.scalars.return_value.one_or_none.return_value = consumed
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


def test_dispatch_and_claim_are_single_owner_transitions() -> None:
    run = SimpleNamespace(
        run_id="run-1",
        chat_record_id=99,
        graph_key="chat",
        status="queued",
        dispatch_attempts=0,
        update_time=None,
        started_at=None,
        error_summary=None,
    )
    dispatch_result = Mock()
    dispatch_result.scalars.return_value.one_or_none.return_value = run
    claim_result = Mock()
    claim_result.scalars.return_value.one_or_none.return_value = run
    session = Mock()
    session.exec.side_effect = [dispatch_result, claim_result]

    dispatched = record_run_dispatch(session, "run-1")
    claimed = claim_run(session, "run-1")

    assert dispatched is run
    assert run.dispatch_attempts == 1
    assert claimed is run
    assert run.status == "running"
    assert run.started_at is not None


def test_duplicate_worker_cannot_claim_running_run() -> None:
    run = SimpleNamespace(status="running")
    result = Mock()
    result.scalars.return_value.one_or_none.return_value = run
    session = Mock()
    session.exec.return_value = result

    assert claim_run(session, "run-1") is None
    session.commit.assert_not_called()


def test_terminal_run_fences_late_domain_writes() -> None:
    run = SimpleNamespace(run_id="run-1", status="failed")
    result = Mock()
    result.scalars.return_value.one_or_none.return_value = run
    session = Mock()
    session.exec.return_value = result

    with pytest.raises(ConversationRunCancelled, match="no longer active"):
        require_active_run(session, "run-1")

    session.commit.assert_not_called()


def test_recovery_queue_uses_status_and_timestamp_cas() -> None:
    from datetime import datetime, timedelta

    from apps.conversation.run_service import queue_run_for_dispatch

    observed = datetime.now()
    run = SimpleNamespace(
        status="running",
        update_time=observed + timedelta(seconds=1),
        dispatch_attempts=1,
    )
    result = Mock()
    result.scalars.return_value.one.return_value = run
    session = Mock()
    session.exec.return_value = result

    queued = queue_run_for_dispatch(
        session,
        "run-1",
        expected_status="running",
        expected_update_time=observed,
    )

    assert queued is None
    assert run.status == "running"
    session.commit.assert_not_called()


def test_recovery_queue_does_not_redispatch_terminal_run() -> None:
    from apps.conversation.run_service import queue_run_for_dispatch

    run = SimpleNamespace(status="failed")
    result = Mock()
    result.scalars.return_value.one.return_value = run
    session = Mock()
    session.exec.return_value = result

    queued = queue_run_for_dispatch(session, "run-1")

    assert queued is None
    session.commit.assert_not_called()


def test_recovered_running_phase_resets_dispatch_attempts() -> None:
    from datetime import datetime

    from apps.conversation.run_service import queue_run_for_dispatch

    observed = datetime.now()
    run = SimpleNamespace(
        status="running",
        update_time=observed,
        dispatch_attempts=2,
    )
    result = Mock()
    result.scalars.return_value.one.return_value = run
    session = Mock()
    session.exec.return_value = result

    queued = queue_run_for_dispatch(
        session,
        "run-1",
        reset_attempts=True,
        expected_status="running",
        expected_update_time=observed,
    )

    assert queued is run
    assert run.status == "queued"
    assert run.dispatch_attempts == 0
    session.commit.assert_called_once()


def test_recovered_queued_phase_resets_previous_process_attempts() -> None:
    from datetime import datetime

    from apps.conversation.run_service import queue_run_for_dispatch

    observed = datetime.now()
    run = SimpleNamespace(
        status="queued",
        update_time=observed,
        dispatch_attempts=2,
    )
    result = Mock()
    result.scalars.return_value.one.return_value = run
    session = Mock()
    session.exec.return_value = result

    queued = queue_run_for_dispatch(
        session,
        "run-1",
        reset_attempts=True,
        expected_status="queued",
        expected_update_time=observed,
    )

    assert queued is run
    assert run.status == "queued"
    assert run.dispatch_attempts == 0
    session.commit.assert_called_once()


def test_finalize_run_commits_record_domain_and_terminal_state_once() -> None:
    run = SimpleNamespace(
        run_id="run-1",
        chat_record_id=99,
        graph_key="chat",
        status="running",
        current_node="complete",
        error_summary=None,
        completed_at=None,
        active_interrupt_id="interrupt-1",
        update_time=None,
        event_cursor=0,
        dispatch_attempts=1,
    )
    nlq = SimpleNamespace(
        planning_status="ready",
        executed_plan_ids=["plan-1"],
        execution_status="running",
        result_quality=None,
        update_time=None,
    )
    run_result = Mock()
    run_result.scalars.return_value.one.return_value = run
    nlq_result = Mock()
    nlq_result.scalars.return_value.one_or_none.return_value = nlq
    audit_result = Mock()
    audit_result.scalars.return_value.all.return_value = []
    update_result = Mock(rowcount=1)
    session = Mock()
    session.exec.side_effect = [run_result, nlq_result, audit_result]
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


def test_failure_before_execution_preserves_origin_and_marks_not_started() -> None:
    run = SimpleNamespace(
        run_id="run-resume",
        chat_record_id=101,
        graph_key="chat",
        status="running",
        current_node="retrieve_context",
        error_summary=None,
        completed_at=None,
        active_interrupt_id=None,
        update_time=None,
        event_cursor=0,
        dispatch_attempts=1,
    )
    nlq = SimpleNamespace(
        planning_status="planning",
        executed_plan_ids=[],
        execution_status="pending",
        result_quality=None,
        update_time=None,
    )
    run_result = Mock()
    run_result.scalars.return_value.one.return_value = run
    nlq_result = Mock()
    nlq_result.scalars.return_value.one_or_none.return_value = nlq
    audit_result = Mock()
    audit_result.scalars.return_value.all.return_value = []
    session = Mock()
    session.exec.side_effect = [run_result, nlq_result, audit_result]
    session.execute.return_value = Mock(rowcount=1)

    finalize_run(
        session,
        run_id=run.run_id,
        status="failed",
        current_node=None,
        record_snapshot={"terminal": True, "error": "hydrate failed"},
        error_summary="hydrate failed",
    )

    assert run.current_node == "retrieve_context"
    assert nlq.planning_status == "failed"
    assert nlq.execution_status == "not_started"
