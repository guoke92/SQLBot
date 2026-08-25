"""QueryUnsupported is a terminal business outcome, not an internal error."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock

import pytest

_ROOT = Path(__file__).resolve().parents[1]
# sqlbot_xpack reads this while importing graph nodes; do not fall back to the
# deployment-only /opt/sqlbot path in local/unit-test runs.
os.environ.setdefault("BASE_DIR", str(_ROOT / "data"))
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.graphs.nodes import nlq  # noqa: E402


def test_route_after_planning_routes_unsupported_to_terminal_node() -> None:
    assert nlq.route_after_planning({"planning_decision": "unsupported"}) == "unsupported"


def test_unsupported_query_node_persists_public_business_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sink = Mock()
    finalize = Mock()

    @contextmanager
    def fake_session_scope():
        yield object()

    monkeypatch.setattr(nlq, "session_scope", fake_session_scope)
    monkeypatch.setattr(nlq, "finalize_run", finalize)
    monkeypatch.setattr(
        nlq.StreamSink,
        "from_state",
        classmethod(lambda _cls, _state: sink),
    )

    message = "当前数据源缺少组织维度，无法定位研发二部。"
    result = nlq.unsupported_query_node(
        {
            "run_id": "run-unsupported",
            "record_id": 401,
            "planning_decision": "unsupported",
            "unsupported_payload": {
                "message": message,
                "reason_code": "SCHEMA_NOT_SUPPORTED",
            },
        }
    )

    kwargs = finalize.call_args.kwargs
    assert kwargs["run_id"] == "run-unsupported"
    assert kwargs["status"] == "failed"
    assert kwargs["current_node"] == "unsupported_query"
    assert kwargs["error_summary"] == message
    assert kwargs["error_visibility"] == "public"
    snapshot = kwargs["record_snapshot"]
    assert snapshot["error"] == message
    assert snapshot["answer"]["kind"] == "query"
    assert snapshot["answer"]["status"] == "failed"
    assert snapshot["answer"]["error"] == {
        "code": "SCHEMA_NOT_SUPPORTED",
        "message": message,
        "retryable": True,
    }
    sink.error.assert_called_once_with(message)
    sink.event.assert_called_once_with({"type": "finish", "id": 401})
    assert result["outcome"]["status"] == "failed"
