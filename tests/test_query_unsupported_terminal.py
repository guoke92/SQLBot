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


def test_route_after_plan_gate_keeps_unsupported_terminal_semantics() -> None:
    """经 plan_gate 的 unsupported 路由仍指向终局节点（gate 放行时不改写语义）."""
    assert (
        nlq.route_after_plan_gate({"planning_decision": "unsupported"}) == "unsupported"
    )


def test_missing_concepts_survive_decision_parsing() -> None:
    from apps.chat.semantic_planning import PLANNING_DECISION_ADAPTER

    unsupported = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "unsupported",
            "message": "当前数据源缺少组织维度。",
            "reason_code": "SCHEMA_NOT_SUPPORTED",
            "missing_concepts": ["组织/部门表", "部门名称字段"],
        }
    )
    assert unsupported.missing_concepts == ["组织/部门表", "部门名称字段"]

    clarify = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "clarify",
            "questions": [
                {
                    "question": "按哪个日期归月",
                    "why": "口径影响结果",
                    "options": [
                        {"label": "创建时间", "fields": [{"table": "d_task", "name": "create_time"}]},
                        {"label": "关闭时间", "fields": [{"table": "d_task", "name": "close_time"}]},
                    ],
                }
            ],
            "missing_concepts": ["交付时效口径"],
        }
    )
    # NeedClarification 的 coerce_payload 重建 dict — 必须保留新字段
    assert clarify.missing_concepts == ["交付时效口径"]

    legacy = PLANNING_DECISION_ADAPTER.validate_python(
        {
            "decision": "unsupported",
            "message": "不支持",
            "reason_code": "SCHEMA_NOT_SUPPORTED",
        }
    )
    assert legacy.missing_concepts == []


def test_unsupported_query_node_persists_public_business_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sink = Mock()
    finalize = Mock()

    @contextmanager
    def fake_session_scope():
        yield object()

    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.routing, nlq.planning, nlq.execution, nlq.presentation, nlq.analysis, nlq.audit):
        monkeypatch.setattr(_patch_target, "session_scope",
fake_session_scope)
    for _patch_target in (nlq, nlq.routing, nlq.presentation, nlq.analysis, nlq.planning):
        monkeypatch.setattr(_patch_target, "finalize_run",
finalize)
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
