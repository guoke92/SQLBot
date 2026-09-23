"""Provider-neutral model message content normalization."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.messages import (  # noqa: E402
    message_content_text,
    message_reasoning_text,
    sanitize_for_checkpoint,
    serialize_messages,
    deserialize_messages,
)
from langchain_core.messages import ToolMessage  # noqa: E402
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer  # noqa: E402


def test_sanitize_for_checkpoint_stringifies_oversized_ints() -> None:
    huge = 5028344028814876000000
    assert huge.bit_length() > 64
    out = sanitize_for_checkpoint(
        {"column_stats": {"项目id": {"sum": huge, "min": 1, "null_count": 0}}}
    )
    assert out["column_stats"]["项目id"]["sum"] == str(huge)
    assert out["column_stats"]["项目id"]["min"] == 1
    JsonPlusSerializer().dumps_typed(out)


def test_serialize_messages_keeps_tool_artifact_checkpoint_safe() -> None:
    huge = 1865227194684671800000
    msg = ToolMessage(
        content="ok",
        tool_call_id="c1",
        name="execute_sql_sandbox",
        artifact={
            "ok": True,
            "summary": "ok",
            "data": {"column_stats": {"产品编码": {"sum": huge}}},
            "error": None,
            "failure": None,
        },
    )
    stored = serialize_messages([msg])
    assert stored[0]["data"]["artifact"]["data"]["column_stats"]["产品编码"]["sum"] == str(
        huge
    )
    JsonPlusSerializer().dumps_typed(stored)
    roundtrip = deserialize_messages(stored)
    assert isinstance(roundtrip[0], ToolMessage)


def test_message_content_text_supports_structured_provider_blocks() -> None:
    assert (
        message_content_text(
            [
                {"type": "text", "text": "第一段"},
                {"type": "reasoning", "content": "不应展示"},
                {"type": "text", "text": "第二段"},
            ]
        )
        == "第一段第二段"
    )


def test_message_content_text_preserves_plain_text() -> None:
    assert message_content_text("完整总结") == "完整总结"


def test_message_reasoning_text_reads_responses_blocks() -> None:
    assert (
        message_reasoning_text(
            [
                {"type": "reasoning", "summary": [{"text": "推演"}]},
                {"type": "text", "text": "答"},
            ]
        )
        == "推演"
    )
    assert message_reasoning_text("纯文本") == ""


def test_message_reasoning_text_ignores_encrypted_envelope() -> None:
    assert (
        message_reasoning_text(
            {
                "id": "r1",
                "summary": [],
                "type": "reasoning",
                "encrypted_content": "enc-0",
                "status": "in_progress",
            }
        )
        == ""
    )
    assert (
        message_reasoning_text(
            {
                "summary": [{"type": "summary_text", "text": "增量"}],
            }
        )
        == "增量"
    )


def test_message_reasoning_text_reads_plaintext_beside_encrypted_envelope() -> None:
    assert (
        message_reasoning_text(
            {
                "type": "reasoning",
                "encrypted_content": "enc-0",
                "summary": [],
                "content": [{"type": "reasoning_text", "text": "真实思考"}],
            }
        )
        == "真实思考"
    )


def test_message_reasoning_text_prefers_content_over_summary() -> None:
    assert (
        message_reasoning_text(
            {
                "type": "reasoning",
                "summary": [{"type": "summary_text", "text": "摘要"}],
                "content": [{"type": "reasoning_text", "text": "完整思维链"}],
            }
        )
        == "完整思维链"
    )
    assert (
        message_reasoning_text(
            {"type": "reasoning", "content": "先看订单表再聚合金额"}
        )
        == "先看订单表再聚合金额"
    )
