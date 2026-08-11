"""证据与升格测试: promote_to_trusted / certify_staging_caliber."""
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

from apps.knowledge.assets.caliber import (  # noqa: E402
    certify_staging_caliber,
    promote_to_trusted,
)
from apps.knowledge.db_models import (  # noqa: E402
    KnowledgeAsset,
    KnowledgeStaging,
)


def _mock_session(
    *,
    get_return: Any = None,
    exec_first: Any = None,
    exec_one: int = 0,
) -> MagicMock:
    session = MagicMock()
    result_proxy = MagicMock()
    result_proxy.first.return_value = exec_first
    result_proxy.one.return_value = exec_one
    session.exec.return_value = result_proxy
    session.get.return_value = get_return
    return session


def _valid_fragment() -> dict[str, Any]:
    return {
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


def _make_staging(
    *,
    status: str = "pending",
    kind: str = "caliber",
    oid: int = 1,
) -> KnowledgeStaging:
    return KnowledgeStaging(
        id=10,
        oid=oid,
        kind=kind,
        status=status,
        natural_key="nk-10",
        lineage_id="lin-10",
        trigger_id="chat",
        payload={
            "contract_fragment": _valid_fragment(),
            "field_targets": [
                {"ds_id": 1, "table_name": "order", "field_name": "amount"},
            ],
            "label": "金额口径",
        },
        scope={"oid": oid, "datasource_id": 1},
        source_record_id=100,
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow(),
    )


def _make_asset(
    *,
    enabled: bool = True,
    trust_tier: str = "published",
    certified: bool = False,
    oid: int = 1,
) -> KnowledgeAsset:
    return KnowledgeAsset(
        id=5,
        kind="caliber",
        natural_key="nk-5",
        lineage_id="lin-5",
        version=1,
        oid=oid,
        label="test",
        payload={},
        trust_tier=trust_tier,
        certified=certified,
        enabled=enabled,
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow(),
    )


# ---------------------------------------------------------------------------
# promote_to_trusted
# ---------------------------------------------------------------------------

class TestPromoteToTrusted:
    @patch("apps.knowledge.assets.caliber.append_event")
    def test_insufficient_evidence_raises(self, _mock: MagicMock) -> None:
        asset = _make_asset()
        session = _mock_session(get_return=asset, exec_one=1)  # policy_n=3
        with pytest.raises(ValueError, match="insufficient evidence"):
            promote_to_trusted(session, caliber_id=5, oid=1, policy_n=3)

    @patch("apps.knowledge.assets.caliber.append_event")
    def test_sufficient_evidence_promotes(self, _mock: MagicMock) -> None:
        asset = _make_asset()
        session = _mock_session(get_return=asset, exec_one=5)  # >= policy_n
        result = promote_to_trusted(session, caliber_id=5, oid=1, policy_n=3)
        assert result is not None
        assert result.trust_tier == "trusted"

    def test_already_trusted_returns_asset(self) -> None:
        asset = _make_asset(trust_tier="trusted", certified=True)
        session = _mock_session(get_return=asset)
        result = promote_to_trusted(session, caliber_id=5, oid=1, policy_n=3)
        assert result is asset

    def test_disabled_raises(self) -> None:
        asset = _make_asset(enabled=False)
        session = _mock_session(get_return=asset)
        with pytest.raises(ValueError, match="not found"):
            promote_to_trusted(session, caliber_id=5, oid=1, policy_n=3)


# ---------------------------------------------------------------------------
# certify_staging_caliber
# ---------------------------------------------------------------------------

class TestCertifyStagingCaliber:
    @patch("apps.knowledge.assets.caliber.append_event")
    def test_certify_ok(self, _mock: MagicMock) -> None:
        staging = _make_staging()
        session = _mock_session(get_return=staging, exec_first=None)
        _id_counter = [100]

        def _flush_side_effect() -> None:
            for call in session.add.call_args_list:
                obj = call[0][0]
                if hasattr(obj, "id") and obj.id is None:
                    obj.id = _id_counter[0]
                    _id_counter[0] += 1

        session.flush.side_effect = _flush_side_effect
        asset = certify_staging_caliber(
            session, staging_id=10, actor_user_id=1, oid=1,
        )
        assert asset.trust_tier == "certified"
        assert asset.certified is True
        assert staging.status == "promoted"

    def test_staging_not_pending_raises(self) -> None:
        staging = _make_staging(status="rejected")
        session = _mock_session(get_return=staging)
        with pytest.raises(ValueError, match="cannot be certified"):
            certify_staging_caliber(session, staging_id=10, actor_user_id=1, oid=1)

    def test_staging_not_found_raises(self) -> None:
        session = _mock_session(get_return=None)
        with pytest.raises(ValueError, match="staging not found"):
            certify_staging_caliber(session, staging_id=999, actor_user_id=1, oid=1)

    @patch("apps.knowledge.assets.caliber.append_event")
    def test_supersede_prior_asset(self, _mock: MagicMock) -> None:
        staging = _make_staging()
        prior = _make_asset(trust_tier="certified", certified=True)
        prior.id = 3

        session = MagicMock()
        session.get.return_value = staging
        session.exec.return_value = SimpleNamespace(
            first=lambda: prior, all=lambda: []
        )
        _id_counter = [200]

        def _flush_side_effect() -> None:
            for call in session.add.call_args_list:
                obj = call[0][0]
                if hasattr(obj, "id") and obj.id is None:
                    obj.id = _id_counter[0]
                    _id_counter[0] += 1

        session.flush.side_effect = _flush_side_effect

        asset = certify_staging_caliber(
            session, staging_id=10, actor_user_id=1, oid=1,
        )
        assert asset.version == 2
        assert prior.enabled is False
        assert prior.superseded_by == asset.id
