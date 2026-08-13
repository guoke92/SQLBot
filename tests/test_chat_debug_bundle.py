"""Unit tests for chat debug_bundle helpers (no DB)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.curd.debug_bundle import (  # noqa: E402
    _redact_mapping,
    _span_brief,
    _truncate_answer_payload,
)


def test_redact_mapping_hides_secrets() -> None:
    raw = {
        "host": "db.example",
        "password": "secret",
        "bearer_token": "tok",
        "basic_password": "bp",
        "nested": {"api_key": "k", "port": 5432},
    }
    out = _redact_mapping(raw)
    assert out["host"] == "db.example"
    assert out["password"] == "***REDACTED***"
    assert out["bearer_token"] == "***REDACTED***"
    assert out["basic_password"] == "***REDACTED***"
    assert out["nested"]["api_key"] == "***REDACTED***"
    assert out["nested"]["port"] == 5432


def test_truncate_answer_payload_rows() -> None:
    payload = {
        "steps": [
            {
                "sql": "select 1",
                "data": {"fields": ["a"], "data": [{"a": i} for i in range(10)]},
            }
        ],
        "analysis": "",
        "outcome": {"status": "success"},
    }
    clipped = _truncate_answer_payload(payload, 3)
    rows = clipped["steps"][0]["data"]["data"]
    assert len(rows) == 3
    assert clipped["steps"][0]["data"]["truncated"] is True
    assert clipped["steps"][0]["data"]["row_count_original"] == 10


def test_span_brief_from_envelope() -> None:
    message = {
        "sqlbot_span": True,
        "version": 1,
        "phase": "execute",
        "graph_node": "execute_queries",
        "detail": {"sql": "select 1", "error": "boom", "row_count": 0},
    }
    brief = _span_brief(message)
    assert brief["graph_node"] == "execute_queries"
    assert brief["detail"]["sql"] == "select 1"
    assert brief["detail"]["error"] == "boom"


def test_span_brief_uses_canonical_envelope() -> None:
    message = {
        "sqlbot_span": True,
        "version": 1,
        "phase": "plan",
        "graph_node": "generate_queries",
        "detail": {"validation_error": "bad sql"},
    }
    brief = _span_brief(message)
    assert brief["graph_node"] == "generate_queries"
    assert brief["detail"]["validation_error"] == "bad sql"
