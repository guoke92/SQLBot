"""Compact unified-agent final copy before it is shown or persisted."""

from __future__ import annotations

import re
from typing import Any

_MD_TABLE_RE = re.compile(
    r"(?ms)^[ \t]*\|[^\n]+\|\s*\n[ \t]*\|[-:| ]+\|[ \t]*\n(?:[ \t]*\|[^\n]+\|\s*\n)*"
)
_OPENER_RE = re.compile(
    r"^(?:查询已完成[，,。.\s]*|企业清单已生成[。.\s]*|"
    r"以下是本次查询的说明与结果概要[：:]\s*)+",
    re.M,
)
_SECTION_HEAD_RE = re.compile(r"(?m)^#{1,3}\s*(?:结果概览|样本示例|几点说明)\s*$")
_SAMPLE_HEAD_RE = re.compile(r"(?ms)^\s*(?:\*\*)?样本示例[：:]?(?:\*\*)?\s*\n+")
_TIP_BLOCKQUOTE_RE = re.compile(r"(?ms)^>\s*提示：.*(?:\n|$)+")
_VERBOSE_TRUNC_RE = re.compile(
    r"(?ms)^[^\n]*(?:结果集有截断|符合条件的记录超过|超过\s*\d+\s*条|"
    r"默认返回上限|完整清单[（(]全部行数[）)])[^\n]*(?:\n|$)+"
)
_NUMBERED_ASIDE_RE = re.compile(
    r"(?ms)^\s*\*\*几点说明[：:]*\*\*\s*\n(?:\s*\d+\.\s.+\n?)+"
)

_TRUNCATED_NOTE_KEY = "i18n_chat.agent.display_truncated"
_TRUNCATED_NOTE_FALLBACK = "仅展示前 {limit} 条。"


def truncated_display_note(limit: int | None, *, trans: Any | None = None) -> str:
    n = int(limit or 0)
    if n <= 0:
        return ""
    if callable(trans):
        try:
            text = str(trans(_TRUNCATED_NOTE_KEY, limit=n) or "").strip()
            if text and text != _TRUNCATED_NOTE_KEY:
                return text
        except Exception:
            pass
    return _TRUNCATED_NOTE_FALLBACK.format(limit=n)


def compact_agent_final_text(
    text: str,
    *,
    truncated: bool = False,
    limit: int | None = None,
    truncation_note: str = "",
) -> str:
    """Drop openers, sample tables, and verbose truncation talk."""
    body = str(text or "").strip()
    body = _MD_TABLE_RE.sub("", body)
    body = _SAMPLE_HEAD_RE.sub("", body)
    body = _TIP_BLOCKQUOTE_RE.sub("", body)
    body = _NUMBERED_ASIDE_RE.sub("", body)
    body = _VERBOSE_TRUNC_RE.sub("", body)
    body = _OPENER_RE.sub("", body)
    body = _SECTION_HEAD_RE.sub("", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if truncated:
        note = truncation_note or truncated_display_note(limit)
        if note and note not in body:
            body = f"{body}\n\n{note}".strip() if body else note
    return body
