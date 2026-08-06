from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.outcome import (  # noqa: E402
    classify_failure,
    format_error_message,
    outcome_allows_retry,
    outcome_from_steps,
)
from common.error import SQLBotDBError  # noqa: E402


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


def test_unrecognised_dialect_rejection_still_earns_a_rewrite() -> None:
    # Hive words a bad column reference in none of the phrasings we match on,
    # yet it is exactly the kind of complaint a rewritten statement answers.
    failure = classify_failure(
        "SemanticException [Error 10004]: Line 1:313 Invalid table alias or "
        "column reference 't1': (possible column names are: company_name)"
    )
    assert failure["retryable"] is True


def test_execution_envelope_hides_the_driver_dump_without_losing_it() -> None:
    # The page shows a localized line keyed on ``type``; the driver text has to
    # survive anyway, because the repair prompt is what fixes the statement.
    envelope = format_error_message(
        SQLBotDBError("SemanticException [Error 10004]: Invalid table alias 't1'")
    )
    assert '"type":"exec-query-err"' in envelope
    assert "Error 10004" in classify_failure(envelope)["message"]
