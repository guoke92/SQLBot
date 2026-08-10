import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ["UPLOAD_DIR"] = "/tmp/sqlbot-test-file"

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.graphs.nodes import nlq  # noqa: E402
from apps.chat.steps.history import (  # noqa: E402
    extract_prompt_messages,
    get_last_conversation_rounds,
    select_prompt_history,
)


class _PromptBundle:
    def as_dict(self) -> dict[str, str]:
        return {
            "system": "sql-system",
            "rules": "sql-rules",
            "ack_rules": "sql-rules-ack",
            "schema": "schema",
            "ack_schema": "schema-ack",
        }


class _Protocol:
    def build_prompt_bundle(self, *_args, **_kwargs) -> _PromptBundle:
        return _PromptBundle()

    def build_chart_system_prompt(self, _question) -> dict[str, str]:
        return {
            "system": "chart-system",
            "rules": "chart-rules",
            "ack": "chart-ack",
        }


def _service(*, sql_logs=(), chart_logs=(), regenerate_record_id=None):
    return SimpleNamespace(
        generate_sql_logs=list(sql_logs),
        generate_chart_logs=list(chart_logs),
        chat_question=SimpleNamespace(regenerate_record_id=regenerate_record_id),
        base_message_round_count_limit=3,
        ds=SimpleNamespace(type="hive"),
        protocol=_Protocol(),
        enable_sql_row_limit=True,
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


def test_compiled_generation_log_does_not_break_next_turn() -> None:
    compiled_log = SimpleNamespace(
        pid=86,
        messages={
            "sqlbot_span": True,
            "graph_node": "generate_queries",
            "payload": {"generation_source": "compiled", "sql": "SELECT 1"},
        },
    )
    service = _service(sql_logs=[compiled_log], chart_logs=[compiled_log])

    nlq.assemble_prompt_messages(service)

    assert len(service.sql_message) == 5
    assert len(service.chart_message) == 3


def test_regenerate_without_generation_history_uses_empty_history() -> None:
    previous_log = SimpleNamespace(
        pid=86,
        messages=[
            {"type": "human", "content": "question"},
            {"type": "ai", "content": "answer"},
        ],
    )
    service = _service(sql_logs=[previous_log], regenerate_record_id=87)

    nlq.assemble_prompt_messages(service)

    assert len(service.sql_message) == 5
