"""Provider-neutral model message content normalization."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.messages import message_content_text  # noqa: E402


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
