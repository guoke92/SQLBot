"""Gateway 三契约测试: submit_candidate / emit_signal / reject_staging."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.db_models import (  # noqa: E402
    KnowledgeAsset,
    KnowledgeSchemaRef,
    KnowledgeStaging,
)
from apps.knowledge.gateway import (  # noqa: E402
    KnowledgeCandidate,
    KnowledgeScope,
    KnowledgeSignal,
    emit_signal,
    reject_staging,
    submit_candidate,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _mock_session(
    *,
    exec_first: Any = None,
    exec_all: list[Any] | None = None,
    get_return: Any = None,
) -> MagicMock:
    session = MagicMock()
    result_proxy = MagicMock()
    result_proxy.first.return_value = exec_first
    result_proxy.one.return_value = 0
    result_proxy.all.return_value = exec_all or []
    session.exec.return_value = result_proxy
    session.get.return_value = get_return
    return session


def _chat_candidate(
    fragment: dict[str, Any] | None = None,
    source_type: str = "chat",
    record_id: int | None = 100,
) -> KnowledgeCandidate:
    frag = fragment or {
        "version": 3,
        "requirements": [
            {
                "clause": "output",
                "requirement_id": "amt",
                "business_label": "金额",
                "field": {"resource": "order", "field": "amount"},
                "aggregation": "sum",
            }
        ],
    }
    prov: dict[str, Any] = {"source_type": source_type}
    if record_id is not None:
        prov["record_id"] = record_id
    return KnowledgeCandidate(
        kind="caliber",
        payload={
            "contract_fragment": frag,
            "field_targets": [
                {"ds_id": 1, "table_name": "order", "field_name": "amount"},
            ],
        },
        scope=KnowledgeScope(oid=1, datasource_id=1),
        provenance=prov,
    )


# ---------------------------------------------------------------------------
# submit_candidate
# ---------------------------------------------------------------------------


class TestSubmitCandidate:
    @patch("apps.knowledge.gateway.admit_candidate")
    def test_new_candidate_admitted(self, mock_admit: MagicMock) -> None:
        staging = SimpleNamespace(
            id=10,
            natural_key="nk-1",
            lineage_id="lin-1",
        )
        mock_admit.return_value = (staging, "admitted")
        session = _mock_session()  # exec_first=None → no existing asset/pending

        receipt = submit_candidate(session, _chat_candidate(), source_record_id=100)
        assert receipt.action == "admitted"
        assert receipt.staging_id == 10

    def test_chat_missing_record_id_rejected(self) -> None:
        session = _mock_session()
        receipt = submit_candidate(
            session,
            _chat_candidate(record_id=None),
            source_record_id=None,
        )
        assert receipt.action == "rejected"
        assert "record_id" in receipt.detail

    def test_manual_missing_actor_rejected(self) -> None:
        session = _mock_session()
        c = _chat_candidate(source_type="manual")
        receipt = submit_candidate(session, c, actor_user_id=None)
        assert receipt.action == "rejected"
        assert "actor_user_id" in receipt.detail

    def test_mining_missing_scan_run_id_rejected(self) -> None:
        session = _mock_session()
        c = KnowledgeCandidate(
            kind="caliber",
            payload={"contract_fragment": {}},
            scope=KnowledgeScope(oid=1),
            provenance={"source_type": "mining"},
        )
        receipt = submit_candidate(session, c)
        assert receipt.action == "rejected"
        assert "scan_run_id" in receipt.detail

    def test_package_missing_package_id_rejected(self) -> None:
        session = _mock_session()
        candidate = _chat_candidate(source_type="package")
        receipt = submit_candidate(session, candidate)
        assert receipt.action == "rejected"
        assert "package_id" in receipt.detail

    def test_existing_asset_merges_evidence(self) -> None:
        existing = KnowledgeAsset(
            id=5,
            kind="caliber",
            natural_key="nk-5",
            lineage_id="lin-5",
            version=1,
            oid=1,
            label="test",
            payload={},
            enabled=True,
            create_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
        )
        session = _mock_session(exec_first=existing)
        receipt = submit_candidate(session, _chat_candidate(), source_record_id=100)
        assert receipt.action == "merged_evidence"
        assert receipt.lineage_id == "lin-5"
        session.scalar.assert_called_once()

    def test_existing_pending_staging_merges(self) -> None:
        pending = KnowledgeStaging(
            id=20,
            oid=1,
            kind="caliber",
            status="pending",
            natural_key="nk-20",
            lineage_id="lin-20",
            trigger_id="chat",
            payload=_chat_candidate().payload,
            scope={},
            quality_snapshot=None,
            create_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
        )
        # first exec → no asset; second exec → pending staging
        results = [None, pending, None]
        session = _mock_session()
        session.scalar.return_value = 1
        session.get.return_value = SimpleNamespace(id=1)
        session.exec.side_effect = lambda _stmt: SimpleNamespace(
            first=lambda: results.pop(0)
        )
        receipt = submit_candidate(session, _chat_candidate(), source_record_id=100)
        assert receipt.action == "merged"
        assert receipt.staging_id == 20

    def test_ephemeral_predicates_rejected(self) -> None:
        fragment = {
            "version": 3,
            "requirements": [
                {
                    "clause": "predicate",
                    "requirement_id": "id_filter",
                    "business_label": "ID过滤",
                    "field": {"resource": "t", "field": "id"},
                    "operator": "eq",
                    "values": ["abc12345-def6-7890-abcd-ef1234567890"],
                }
            ],
        }
        session = _mock_session()
        receipt = submit_candidate(
            session,
            _chat_candidate(fragment=fragment),
            source_record_id=100,
        )
        assert receipt.action == "rejected"
        assert "ephemeral" in receipt.detail


# ---------------------------------------------------------------------------
# emit_signal
# ---------------------------------------------------------------------------


class TestEmitSignal:
    def test_apply_outcome_writes_evidence(self) -> None:
        session = _mock_session()
        session.scalar.return_value = 1
        session.get.return_value = SimpleNamespace(id=1)
        count = emit_signal(
            session,
            KnowledgeSignal(
                kind="apply_outcome",
                refs={"asset_id": 1, "asset_kind": "caliber"},
                fact={"record_id": 10, "outcome": "success"},
            ),
        )
        assert count == 1
        session.scalar.assert_called_once()

    def test_user_feedback_writes_evidence(self) -> None:
        session = _mock_session()
        session.scalar.return_value = 2
        session.get.return_value = SimpleNamespace(id=2)
        count = emit_signal(
            session,
            KnowledgeSignal(
                kind="turn_feedback",
                fact={"record_id": 11, "feedback": "up", "revision": 1},
            ),
        )
        assert count == 1
        session.scalar.assert_called_once()

    @patch("apps.knowledge.gateway.append_event")
    def test_schema_drift_disables_affected(self, mock_append: MagicMock) -> None:
        asset = KnowledgeAsset(
            id=3,
            kind="caliber",
            natural_key="nk",
            lineage_id="lin",
            version=1,
            oid=1,
            label="test",
            payload={},
            enabled=True,
            create_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
        )
        ref = KnowledgeSchemaRef(
            id=1,
            asset_id=3,
            asset_kind="caliber",
            datasource_id=1,
            table_name="order",
            field_name="amount",
            field_id=99,
        )
        session = _mock_session(exec_all=[ref], get_return=asset)
        count = emit_signal(
            session,
            KnowledgeSignal(
                kind="schema_drift",
                refs={"ds_id": 1, "changed_field_ids": [99]},
            ),
        )
        assert count == 1
        assert asset.enabled is False

    def test_usage_writes_evidence(self) -> None:
        session = _mock_session()
        session.scalar.return_value = 3
        session.get.return_value = SimpleNamespace(id=3)
        count = emit_signal(
            session,
            KnowledgeSignal(
                kind="usage",
                refs={"asset_id": 4},
                fact={"record_id": 20},
            ),
        )
        assert count == 1
        session.scalar.assert_called_once()

    def test_unknown_kind_returns_zero(self) -> None:
        session = _mock_session()
        count = emit_signal(session, KnowledgeSignal(kind="bogus"))
        assert count == 0


# ---------------------------------------------------------------------------
# reject_staging
# ---------------------------------------------------------------------------


class TestRejectStaging:
    @patch("apps.knowledge.gateway.append_event")
    def test_reject_staging_ok(self, mock_append: MagicMock) -> None:
        staging = KnowledgeStaging(
            id=30,
            oid=1,
            kind="caliber",
            status="pending",
            natural_key="nk",
            lineage_id="lin",
            trigger_id="chat",
            payload={},
            scope={},
            create_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
        )
        session = _mock_session(get_return=staging)
        result = reject_staging(
            session, staging_id=30, oid=1, actor_user_id=5, reason="bad"
        )
        assert result.status == "rejected"
        assert result.reject_reason == "bad"

    def test_staging_not_found_raises(self) -> None:
        session = _mock_session(get_return=None)
        with pytest.raises(ValueError, match="staging not found"):
            reject_staging(
                session, staging_id=999, oid=1, actor_user_id=5, reason="bad"
            )
