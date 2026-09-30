"""Transcript projection and continue-turn recap from TurnAnswer."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any, Literal

import orjson
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from apps.chat.turn_contracts import TurnRoute
from apps.chat.turn_fold import (
    DEFAULT_KEEP_TURNS,
    DEFAULT_TOKEN_BUDGET,
    estimate_tokens,
    fold_history,
)
from apps.conversation.messages import deserialize_messages, serialize_messages
from common.utils.utils import SQLBotLogUtil


class ContextSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    content: Any
    estimated_tokens: int = 0
    trusted: bool = False


def estimate_context_tokens(value: Any) -> int:
    if value is None:
        return 0
    if not isinstance(value, str):
        value = orjson.dumps(value, default=str).decode()
    return max(1, len(value) // 3)


def context_fingerprint(parts: dict[str, Any]) -> str:
    return hashlib.sha256(
        orjson.dumps(parts, option=orjson.OPT_SORT_KEYS, default=str)
    ).hexdigest()


def budget_context_sections(
    sections: list[ContextSection], *, max_tokens: int
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    used = 0
    kept: dict[str, Any] = {}
    truncated: list[dict[str, Any]] = []
    for section in sections:
        cost = section.estimated_tokens or estimate_context_tokens(section.content)
        if section.trusted or used + cost <= max_tokens:
            kept[section.name] = section.content
            used += cost
            continue
        truncated.append(
            {
                "section": section.name,
                "estimated_tokens": cost,
                "reason": "context_budget",
            }
        )
    return kept, tuple(truncated)


def choose_data_strategy(
    route: TurnRoute,
    *,
    referenced_datasets: tuple[dict[str, Any], ...],
    message_has_query_need: bool,
) -> Literal["direct_query", "existing_results", "derived_query", "unavailable"]:
    if route.task_kind == "query":
        return "direct_query"
    usable = [
        item
        for item in referenced_datasets
        if item.get("status") in {"succeeded", "degraded"}
    ]
    if route.task_kind == "analysis":
        if usable:
            return "existing_results"
        return "derived_query" if message_has_query_need else "unavailable"
    if route.task_kind == "prediction":
        time_series = [
            item
            for item in usable
            if item.get("has_time_field")
            and item.get("has_numeric_measure")
            and int(item.get("valid_points") or 0) >= 6
        ]
        if time_series:
            return "existing_results"
        return "derived_query"
    return "unavailable"


def recap_from_turn_answer(answer: Mapping[str, Any] | None) -> dict[str, Any]:
    """Continue-turn recap from persisted TurnAnswer — never ToolMessage SQL."""
    payload = dict(answer or {})
    datasets = (
        payload.get("datasets") if isinstance(payload.get("datasets"), list) else []
    )
    sql = ""
    dataset_id = ""
    for item in reversed(datasets):
        if not isinstance(item, Mapping):
            continue
        candidate = str(item.get("sql") or "").strip()
        if candidate:
            sql = candidate
            dataset_id = str(item.get("dataset_id") or "")
            break
    knowledge_refs = (
        dict(payload.get("knowledge_refs") or {})
        if isinstance(payload.get("knowledge_refs"), Mapping)
        else {}
    )
    return {
        "sql": sql,
        "dataset_id": dataset_id,
        "confirmed_calibers": list(payload.get("confirmed_calibers") or []),
        "assumptions": list(payload.get("assumptions") or []),
        "knowledge_refs": knowledge_refs,
        "content": str(payload.get("content") or "")[:1000],
        "status": payload.get("status"),
    }


def _token_budget() -> int:
    try:
        from common.core.config import settings

        return int(
            getattr(settings, "AGENT_TRANSCRIPT_TOKEN_BUDGET", DEFAULT_TOKEN_BUDGET)
            or DEFAULT_TOKEN_BUDGET
        )
    except Exception:
        return DEFAULT_TOKEN_BUDGET


def _keep_turns() -> int:
    try:
        from common.core.config import settings

        return int(
            getattr(settings, "AGENT_TRANSCRIPT_KEEP_TURNS", DEFAULT_KEEP_TURNS)
            or DEFAULT_KEEP_TURNS
        )
    except Exception:
        return DEFAULT_KEEP_TURNS


def empty_transcript() -> dict[str, Any]:
    return {"messages": [], "folds": []}


def load_agent_transcript(session: Session, chat_id: int) -> list[BaseMessage]:
    from apps.chat.models.chat_model import Chat

    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return []
    raw = getattr(chat, "agent_transcript", None)
    if not isinstance(raw, Mapping):
        return []
    stored = raw.get("messages") or []
    if not stored:
        return []
    try:
        from apps.conversation.messages import sanitize_for_checkpoint

        return deserialize_messages(sanitize_for_checkpoint(list(stored)))
    except Exception as exc:
        SQLBotLogUtil.warning(
            f"agent_transcript deserialize failed chat={chat_id}: {exc}"
        )
        return []


def append_agent_transcript(
    session: Session, chat_id: int, messages: Sequence[BaseMessage]
) -> dict[str, Any]:
    from apps.chat.models.chat_model import Chat

    chunk = [message for message in messages if not isinstance(message, SystemMessage)]
    if not chunk:
        return empty_transcript()
    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return empty_transcript()
    raw = (
        dict(chat.agent_transcript or {})
        if isinstance(chat.agent_transcript, Mapping)
        else {}
    )
    existing = list(raw.get("messages") or [])
    existing.extend(serialize_messages(chunk))
    payload = {
        "messages": existing,
        "folds": list(raw.get("folds") or []),
    }
    chat.agent_transcript = payload
    session.add(chat)
    return payload


def persist_turn_from_state(state: Mapping[str, Any]) -> bool:
    if state.get("agent_transcript_saved"):
        return True
    chat_id = state.get("chat_id")
    start = state.get("turn_message_start")
    if chat_id is None or start is None:
        return False
    messages = deserialize_messages(list(state.get("messages") or []))
    chunk = [
        item for item in messages[int(start) :] if not isinstance(item, SystemMessage)
    ]
    if not chunk:
        return False
    from apps.conversation.session import session_scope

    with session_scope() as session:
        append_agent_transcript(session, int(chat_id), chunk)
        session.commit()
    return True


def save_fold_meta(
    session: Session, chat_id: int, folds: Sequence[Mapping[str, Any]]
) -> None:
    from apps.chat.models.chat_model import Chat

    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return
    raw = (
        dict(chat.agent_transcript or {})
        if isinstance(chat.agent_transcript, Mapping)
        else {}
    )
    raw["messages"] = list(raw.get("messages") or [])
    raw["folds"] = [dict(item) for item in folds]
    chat.agent_transcript = raw
    session.add(chat)


def build_continued_messages(
    *,
    history: Sequence[BaseMessage],
    question: str,
    knowledge_plane: Any = None,
    token_budget: int | None = None,
    keep_turns: int | None = None,
) -> tuple[list[BaseMessage], int, list[dict[str, Any]]]:
    from apps.chat.agent.prompt import build_agent_system_prompt
    from apps.conversation.tooling import sanitize_messages_for_model

    system = SystemMessage(
        content=build_agent_system_prompt(knowledge_plane=knowledge_plane)
    )
    human = HumanMessage(content=question)
    budget = int(token_budget if token_budget is not None else _token_budget())
    keep = int(keep_turns if keep_turns is not None else _keep_turns())
    folded, folds = fold_history(
        list(history),
        token_budget=budget,
        keep_turns=keep,
        extra_tokens=estimate_tokens([system, human]),
    )
    messages = [system, *folded, human]
    return sanitize_messages_for_model(messages), len(messages) - 1, folds
