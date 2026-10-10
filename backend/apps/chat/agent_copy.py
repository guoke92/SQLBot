"""Compact unified-agent final copy before it is shown or persisted."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

_MD_TABLE_RE = re.compile(
    r"(?ms)^[ \t]*\|[^\n]+\|\s*\n[ \t]*\|[-:| ]+\|[ \t]*\n(?:[ \t]*\|[^\n]+\|\s*\n)*(?:[ \t]*\|[^\n]+\|[ \t]*)?"
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
_META_HEAD_RE = re.compile(r"(?m)^#{1,3}[ \t]*(?:分析报告|核心发现)[ \t]*\n*")


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


def looks_like_analysis_report(text: str) -> bool:
    """A finished Analyze answer is a headed write-up, usually with a table."""
    body = str(text or "")
    has_heading = "##" in body or "###" in body
    if "核心发现" in body and has_heading:
        return True
    return has_heading and _MD_TABLE_RE.search(body) is not None


def recover_analysis_report(messages: Sequence[Any], text: str) -> str:
    """Keep an earlier five-section draft when a later stop is empty.

    Evidence follow-ups can fail after the report is already written. The
    user-facing answer is that draft, not the truncation footnote.
    """
    current = str(text or "").strip()
    if looks_like_analysis_report(current):
        return current
    best = ""
    for message in messages:
        if str(getattr(message, "type", "") or "") != "ai":
            continue
        content = str(getattr(message, "content", "") or "").strip()
        if looks_like_analysis_report(content) and len(content) > len(best):
            best = content
    return best or current


def compact_agent_final_text(
    text: str,
    *,
    truncated: bool = False,
    limit: int | None = None,
    truncation_note: str = "",
    keep_tables: bool = False,
) -> str:
    """Drop openers, sample tables, and verbose truncation talk.

    Query narration strips markdown tables (cards already show rows). Analyze
    reports keep tables — they are the evidence section.
    """
    body = str(text or "").strip()
    if not keep_tables:
        body = _MD_TABLE_RE.sub("", body)
        body = _VERBOSE_TRUNC_RE.sub("", body)
    body = _SAMPLE_HEAD_RE.sub("", body)
    body = _TIP_BLOCKQUOTE_RE.sub("", body)
    body = _NUMBERED_ASIDE_RE.sub("", body)
    body = _OPENER_RE.sub("", body)
    body = _SECTION_HEAD_RE.sub("", body)
    is_report = keep_tables and looks_like_analysis_report(body)
    if keep_tables:
        body = _META_HEAD_RE.sub("", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if truncated:
        note = truncation_note or truncated_display_note(limit)
        # The detail card already labels its own window. Analyze reports
        # must not pick up the query footnote ("仅展示前 N 条").
        if is_report:
            note = ""
        if note and note not in body:
            body = f"{body}\n\n{note}".strip() if body else note
    return body
