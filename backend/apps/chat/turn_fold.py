"""Deterministic whole-turn folding for the agent transcript.

Folding is a model-facing projection. Stored transcript stays full-fidelity.
Fold levels are monotonic: a stored level never decreases.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage

from apps.chat.agent.tokens import count_message_tokens
from apps.conversation.messages import message_content_text

DEFAULT_TOKEN_BUDGET = 48000
DEFAULT_KEEP_TURNS = 3

_CLARIFY_PREFIXES = ("用户已完成澄清", "用户已确认澄清")


def estimate_tokens(messages: Sequence[Any]) -> int:
    return count_message_tokens(messages)


def is_clarify_human(text: str) -> bool:
    stripped = str(text or "").strip()
    return any(stripped.startswith(prefix) for prefix in _CLARIFY_PREFIXES)


def split_turns(messages: Sequence[BaseMessage]) -> list[list[BaseMessage]]:
    """Split Human→answer runs. Clarification Humans stay inside the current turn."""
    turns: list[list[BaseMessage]] = []
    current: list[BaseMessage] = []
    for message in messages:
        kind = str(getattr(message, "type", "") or "")
        if kind == "system":
            continue
        if (
            kind == "human"
            and current
            and not is_clarify_human(
                message_content_text(getattr(message, "content", "") or "")
            )
        ):
            turns.append(current)
            current = [message]
            continue
        current.append(message)
    if current:
        turns.append(current)
    return turns


def fold_history(
    messages: Sequence[BaseMessage],
    *,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
    keep_turns: int = DEFAULT_KEEP_TURNS,
    extra_tokens: int = 0,
    stored_folds: Sequence[Mapping[str, Any]] | None = None,
) -> tuple[list[BaseMessage], list[dict[str, Any]]]:
    """Fold oldest turns first until under budget; keep last K raw.

    ``stored_folds`` is the ledger: levels only increase.
    """
    history = list(messages)
    turns = split_turns(history)
    if not turns:
        return history, []
    keep = max(int(keep_turns), 1)
    levels = [0] * len(turns)
    for item in stored_folds or []:
        if not isinstance(item, Mapping):
            continue
        try:
            index = int(item.get("index"))
            level = int(item.get("level") or 0)
        except (TypeError, ValueError):
            continue
        if 0 <= index < len(levels):
            levels[index] = max(levels[index], level)
    protect_from = max(0, len(turns) - keep)

    def project() -> tuple[list[BaseMessage], list[dict[str, Any]]]:
        out: list[BaseMessage] = []
        meta: list[dict[str, Any]] = []
        for index, turn in enumerate(turns):
            level = levels[index]
            if level <= 0:
                out.extend(turn)
                continue
            out.append(fold_turn(turn, level=level))
            meta.append({"index": index, "level": level})
        return out, meta

    projected, folds = project()
    while estimate_tokens(projected) + extra_tokens > token_budget:
        foldable = [i for i in range(protect_from) if levels[i] == 0]
        if foldable:
            levels[foldable[0]] = 1
        else:
            demote = [i for i in range(protect_from) if levels[i] == 1]
            if not demote:
                break
            levels[demote[0]] = 2
        projected, folds = project()
    return projected, folds


def fold_turn(turn: Sequence[BaseMessage], *, level: int) -> HumanMessage:
    question = _question_text(turn)
    clarification = _clarification_text(turn)
    lines = [f'<turn_fold level="{1 if level < 2 else 2}">', f"问：{question}"]
    if clarification:
        lines.append(f"澄清：{clarification}")
    lines.append("</turn_fold>")
    return HumanMessage(content="\n".join(lines))


def _question_text(turn: Sequence[BaseMessage]) -> str:
    for message in turn:
        if str(getattr(message, "type", "") or "") != "human":
            continue
        text = message_content_text(getattr(message, "content", "") or "")
        if not is_clarify_human(text):
            return text.strip()
    return ""


def _clarification_text(turn: Sequence[BaseMessage]) -> str:
    parts: list[str] = []
    for message in turn:
        if str(getattr(message, "type", "") or "") != "human":
            continue
        text = message_content_text(getattr(message, "content", "") or "").strip()
        if is_clarify_human(text):
            parts.append(text)
    return "\n".join(parts)
