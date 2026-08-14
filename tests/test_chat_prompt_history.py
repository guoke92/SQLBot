import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ["UPLOAD_DIR"] = "/tmp/sqlbot-test-file"

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps.history import (  # noqa: E402
    extract_prompt_messages,
    get_last_conversation_rounds,
    select_prompt_history,
)


def test_audit_payload_is_not_prompt_history() -> None:
    payload = {
        "sqlbot_span": True,
        "graph_node": "generate_queries",
        "payload": {"generation_source": "compiled", "sql": "SELECT 1"},
    }

    assert extract_prompt_messages(payload) == []
    assert get_last_conversation_rounds(payload) == []


def test_prompt_history_filters_span_metadata_and_invalid_items() -> None:
    messages = [
        {
            "type": "system",
            "content": "span metadata",
            "sqlbot_system": True,
        },
        "invalid",
        {"type": "human", "content": "question"},
        {"type": "ai", "content": "answer"},
        {"type": "tool", "content": "not replayed"},
    ]

    assert extract_prompt_messages(messages) == [
        {"type": "human", "content": "question"},
        {"type": "ai", "content": "answer"},
    ]


def test_prompt_history_uses_latest_log_for_regenerated_record() -> None:
    logs = [
        SimpleNamespace(
            pid=7,
            messages=[{"type": "human", "content": "old attempt"}],
        ),
        SimpleNamespace(
            pid=8,
            messages=[{"type": "human", "content": "other record"}],
        ),
        SimpleNamespace(
            pid=7,
            messages=[{"type": "human", "content": "latest attempt"}],
        ),
    ]

    assert select_prompt_history(logs, record_id=7) == [
        {"type": "human", "content": "latest attempt"}
    ]
