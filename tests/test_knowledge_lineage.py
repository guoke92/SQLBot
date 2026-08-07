from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.lineage.service import (  # noqa: E402
    PROMOTION_ACTIONS,
    append_event,
    new_lineage_id,
)


class _FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, obj: object) -> None:
        self.added.append(obj)

    def flush(self) -> None:
        return None


def test_append_event_requires_evidence_for_certify() -> None:
    session = _FakeSession()
    with pytest.raises(ValueError, match="evidence_snapshot"):
        append_event(
            session,  # type: ignore[arg-type]
            lineage_id=new_lineage_id(),
            asset_kind="caliber",
            action="certified",
            evidence_snapshot=None,
        )


def test_append_event_accepts_captured_without_evidence() -> None:
    session = _FakeSession()
    event = append_event(
        session,  # type: ignore[arg-type]
        lineage_id=new_lineage_id(),
        asset_kind="caliber",
        action="captured",
        require_evidence=False,
    )
    assert event.event_id.startswith("evt_")
    assert len(session.added) == 1


def test_promotion_actions_include_schema_invalidated() -> None:
    assert "schema_invalidated" in PROMOTION_ACTIONS
    assert "certified" in PROMOTION_ACTIONS
