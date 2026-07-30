from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.outcome import (  # noqa: E402
    classify_failure,
    outcome_allows_retry,
    outcome_from_steps,
)


def test_all_failed_steps_are_terminal_failure() -> None:
    outcome = outcome_from_steps(
        [
            {"error": "SQL syntax error"},
            {"error": "unknown column department_name"},
        ]
    )
    assert outcome["status"] == "failed"
    assert outcome["successful_steps"] == 0
    assert outcome_allows_retry(outcome)


def test_partial_batch_is_degraded_success() -> None:
    outcome = outcome_from_steps(
        [
            {"result": {"data": [{"count": 1}]}},
            {"error": "permission denied"},
        ]
    )
    assert outcome["status"] == "degraded"
    assert outcome["successful_steps"] == 1
    assert not outcome_allows_retry(outcome)


def test_connection_failure_is_not_sql_repairable() -> None:
    failure = classify_failure("Connection refused")
    assert failure["kind"] == "connection"
    assert failure["retryable"] is False
