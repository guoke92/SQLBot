"""ContextSpec projection: six sections rebuilt each model round."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

import orjson
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from apps.chat.agent.budget import LoopBudget, budget_from_state
from apps.chat.agent.tokens import count_tokens
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.turn_fold import (
    DEFAULT_KEEP_TURNS,
    DEFAULT_TOKEN_BUDGET,
    estimate_tokens,
    fold_history,
)
from apps.conversation.messages import deserialize_messages, serialize_messages
from common.utils.utils import SQLBotLogUtil


class ContextSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: str = ""
    catalog_outline: str = ""
    recap: str = ""
    working_set: str = ""
    sql_workspace: str = ""
    turn_brief: str = ""
    evidence: str = ""

    def system_body(self) -> str:
        return "\n\n".join(
            part for part in (self.stable_prefix(), self.turn_delta()) if part
        )

    def stable_prefix(self) -> str:
        """Rules, outline, and recap. Unchanged for the rest of the turn."""
        parts: list[str] = []
        if self.rules:
            parts.append(self.rules)
        if self.catalog_outline:
            parts.append(self.catalog_outline)
        if self.recap:
            parts.append("<recap>\n" + self.recap + "\n</recap>")
        return "\n\n".join(parts)

    def turn_delta(self) -> str:
        """Working set, SQL index, and evidence. Appended after the transcript."""
        parts: list[str] = []
        if self.working_set:
            parts.append("<working_set>\n" + self.working_set + "\n</working_set>")
        if self.sql_workspace:
            parts.append(
                "<sql_workspace>\n" + self.sql_workspace + "\n</sql_workspace>"
            )
        if self.evidence:
            parts.append("<evidence>\n" + self.evidence + "\n</evidence>")
        return "\n\n".join(parts)

    def token_counts(self) -> dict[str, int]:
        return {
            "rules": count_tokens(self.rules),
            "catalog_outline": count_tokens(self.catalog_outline),
            "recap": count_tokens(self.recap),
            "working_set": count_tokens(self.working_set),
            "sql_workspace": count_tokens(self.sql_workspace),
            "turn_brief": count_tokens(self.turn_brief),
            "evidence": count_tokens(self.evidence),
        }


def context_fingerprint(parts: dict[str, Any]) -> str:
    return hashlib.sha256(
        orjson.dumps(parts, option=orjson.OPT_SORT_KEYS, default=str)
    ).hexdigest()


class RecapDataset(BaseModel):
    """Handle-only dataset row for the model recap. SQL stays on TurnAnswer."""

    model_config = ConfigDict(extra="forbid")

    rev: str = ""
    dataset_id: str = ""
    title: str = ""
    row_count: int | None = None
    fields: list[str] = Field(default_factory=list)
    status: str | None = None


class TurnRecap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    datasets: list[RecapDataset] = Field(default_factory=list)
    dataset_id: str = ""
    confirmed_calibers: list[Any] = Field(default_factory=list)
    assumptions: list[Any] = Field(default_factory=list)
    knowledge_refs: dict[str, Any] = Field(default_factory=dict)
    content: str = ""
    status: Any = None


def recap_from_turn_answer(answer: Mapping[str, Any] | None) -> TurnRecap:
    """Continue-turn recap from persisted TurnAnswer — never SQL plaintext."""
    payload = dict(answer or {})
    datasets = (
        payload.get("datasets") if isinstance(payload.get("datasets"), list) else []
    )
    rows: list[RecapDataset] = []
    dataset_id = ""
    for item in datasets:
        if not isinstance(item, Mapping):
            continue
        row = RecapDataset(
            rev=str(item.get("rev") or "").strip(),
            dataset_id=str(item.get("dataset_id") or ""),
            title=str(item.get("title") or item.get("brief") or ""),
            row_count=item.get("row_count")
            if isinstance(item.get("row_count"), int)
            else None,
            fields=[str(f) for f in (item.get("fields") or [])],
            status=str(item.get("status") or "") or None,
        )
        rows.append(row)
        if not dataset_id and row.dataset_id:
            dataset_id = row.dataset_id
    knowledge_refs = (
        dict(payload.get("knowledge_refs") or {})
        if isinstance(payload.get("knowledge_refs"), Mapping)
        else {}
    )
    return TurnRecap(
        datasets=rows,
        dataset_id=dataset_id,
        confirmed_calibers=list(payload.get("confirmed_calibers") or []),
        assumptions=list(payload.get("assumptions") or []),
        knowledge_refs=knowledge_refs,
        content=str(payload.get("content") or "")[:1000],
        status=payload.get("status"),
    )


def render_recap(referenced_turns: Sequence[Mapping[str, Any]] | None) -> str:
    lines: list[str] = []
    for turn in referenced_turns or []:
        if not isinstance(turn, Mapping):
            continue
        q = str(turn.get("question") or "").strip()[:400]
        bits = [f"问：{q}"] if q else []
        summary = str(turn.get("answer_summary") or "").strip()
        if summary:
            bits.append(summary[:400])
        for ds in turn.get("datasets") or []:
            if not isinstance(ds, Mapping):
                continue
            rev = str(ds.get("rev") or "").strip()
            did = str(ds.get("dataset_id") or "").strip()
            title = str(ds.get("title") or "").strip()
            count = ds.get("row_count")
            fields = [str(f) for f in (ds.get("fields") or [])][:8]
            piece = " · ".join(
                p
                for p in (
                    rev or None,
                    title or None,
                    f"{count} 行" if count is not None else None,
                    f"fields={','.join(fields)}" if fields else None,
                    f"dataset={did}" if did else None,
                )
                if p
            )
            if piece:
                bits.append(piece)
        calibers = turn.get("confirmed_calibers") or []
        if calibers:
            bits.append("已确认口径沿用，不重问")
        if bits:
            lines.append("\n".join(bits))
    return "\n\n".join(lines)


def render_working_set(
    *,
    knowledge_plane: Any = None,
    memory_slots: Mapping[str, Any] | None = None,
) -> str:
    from apps.chat.agent.prompt import render_memory_slots
    from apps.chat.agent_knowledge import AgentKnowledgePlane

    plane = (
        knowledge_plane
        if isinstance(knowledge_plane, AgentKnowledgePlane)
        else AgentKnowledgePlane.from_dump(
            knowledge_plane if isinstance(knowledge_plane, Mapping) else None
        )
    )
    parts: list[str] = []
    tables = [str(t) for t in (plane.tables or []) if str(t)]
    pages = [str(p) for p in (plane.page_keys or []) if str(p)]
    if tables:
        parts.append("tables: " + ", ".join(tables))
    if pages:
        parts.append("page_keys: " + ", ".join(pages))
    slots_text = render_memory_slots(memory_slots)
    if slots_text:
        parts.append(slots_text)
    catalog = (
        plane.schema_catalog_text() if hasattr(plane, "schema_catalog_text") else ""
    )
    if catalog:
        parts.append(catalog)
    return "\n".join(parts)


def render_turn_brief(
    *,
    question: str,
    budget: LoopBudget | None = None,
    workspace: SqlWorkspace | None = None,
    evidence: str = "",
) -> str:
    lines = [str(question or "").strip()] if str(question or "").strip() else []
    if workspace is not None and workspace.current:
        lines.append(f"当前 rev: {workspace.current}")
        if workspace.delivered:
            lines.append(f"已交付: {workspace.delivered}")
    if budget is not None:
        lines.append(budget.render_brief())
    if evidence:
        lines.append("本轮已有剖析/聚合证据，写报告时引用 <evidence>，不要再用 preview。")
    return "\n".join(lines)


def render_turn_evidence(state: Mapping[str, Any]) -> str:
    """Compact warehouse stats from this-turn analyze tools. Not row dumps."""
    from apps.chat.tools.analyze_result import ANALYZE_SQL_TOOLS
    from apps.chat.tools.contract import outcome_payload

    lines: list[str] = []
    for step in state.get("tool_steps") or []:
        if not isinstance(step, Mapping) or not step.get("ok"):
            continue
        name = str(step.get("name") or step.get("tool") or "")
        if name not in ANALYZE_SQL_TOOLS and name != "compare_results":
            continue
        payload = outcome_payload(step.get("outcome") or step.get("result") or {})
        if name == "profile_sql_result":
            bits = [f"profile {payload.get('sql_ref')} rows={payload.get('row_count')}"]
            for column in list(payload.get("columns") or [])[:6]:
                if isinstance(column, Mapping):
                    bits.append(
                        f"{column.get('name')} nn={column.get('non_null')} "
                        f"min={column.get('min')} max={column.get('max')}"
                    )
            breakdown = payload.get("breakdown")
            if isinstance(breakdown, Mapping):
                top = list(breakdown.get("top") or [])[:5]
                bits.append(
                    "breakdown "
                    + str(breakdown.get("column"))
                    + "="
                    + ",".join(
                        f"{item.get('value')}:{item.get('n')}"
                        for item in top
                        if isinstance(item, Mapping)
                    )
                )
            lines.append("; ".join(str(item) for item in bits if item))
        elif name == "aggregate_sql_result":
            rows = list(payload.get("rows") or [])[:8]
            lines.append(
                f"aggregate {payload.get('sql_ref')} "
                f"dims={payload.get('dimensions')} groups={len(rows)}"
            )
            for row in rows:
                if isinstance(row, Mapping):
                    lines.append(
                        "  "
                        + ", ".join(f"{key}={row[key]}" for key in list(row)[:6])
                    )
        elif name == "compare_results":
            lines.append(str(step.get("summary") or payload.get("summary") or "compare ok"))
    return "\n".join(lines)


def build_context_spec(
    state: Mapping[str, Any],
    *,
    knowledge_plane: Any = None,
    memory_slots: Mapping[str, Any] | None = None,
    question: str = "",
    config: Any = None,
) -> ContextSpec:
    from apps.chat.agent.mode import resolve_agent_mode
    from apps.chat.agent_knowledge import AgentKnowledgePlane

    plane = (
        knowledge_plane
        if isinstance(knowledge_plane, AgentKnowledgePlane)
        else AgentKnowledgePlane.from_dump(
            (knowledge_plane if isinstance(knowledge_plane, Mapping) else None)
            or (
                state.get("knowledge_plane")
                if isinstance(state.get("knowledge_plane"), Mapping)
                else None
            )
        )
    )
    slots = memory_slots
    if slots is None and isinstance(state.get("memory_slots"), Mapping):
        slots = state.get("memory_slots")  # type: ignore[assignment]
    workspace = SqlWorkspace.from_state(state)
    budget = budget_from_state(state, config=config)
    outline = str(getattr(plane, "schema_outline", "") or "").strip()
    evidence = ""
    if resolve_agent_mode(state).id == "analyze":
        evidence = render_turn_evidence(state)
    return ContextSpec(
        rules=resolve_agent_mode(state).compose_rules(config=config),
        catalog_outline=outline,
        recap=render_recap(state.get("referenced_turns") or []),
        working_set=render_working_set(knowledge_plane=plane, memory_slots=slots),
        sql_workspace=workspace.render_index(),
        evidence=evidence,
        turn_brief=render_turn_brief(
            question=question or str(state.get("question") or ""),
            budget=budget,
            workspace=workspace,
            evidence=evidence,
        ),
    )


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


def load_transcript_payload(session: Session, chat_id: int) -> dict[str, Any]:
    from apps.chat.models.chat_model import Chat

    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return empty_transcript()
    raw = getattr(chat, "agent_transcript", None)
    if not isinstance(raw, Mapping):
        return empty_transcript()
    return {
        "messages": list(raw.get("messages") or []),
        "folds": list(raw.get("folds") or []),
    }


def load_agent_transcript(session: Session, chat_id: int) -> list[BaseMessage]:
    payload = load_transcript_payload(session, chat_id)
    stored = payload.get("messages") or []
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


def load_fold_ledger(session: Session, chat_id: int) -> list[dict[str, Any]]:
    payload = load_transcript_payload(session, chat_id)
    return [
        dict(item) for item in (payload.get("folds") or []) if isinstance(item, Mapping)
    ]


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
    previous = list(raw.get("folds") or [])
    merged: dict[int, int] = {}
    for item in [*previous, *folds]:
        if not isinstance(item, Mapping):
            continue
        try:
            index = int(item.get("index"))
            level = int(item.get("level") or 0)
        except (TypeError, ValueError):
            continue
        merged[index] = max(merged.get(index, 0), level)
    raw["messages"] = list(raw.get("messages") or [])
    raw["folds"] = [{"index": i, "level": merged[i]} for i in sorted(merged)]
    chat.agent_transcript = raw
    session.add(chat)


def build_continued_messages(
    *,
    history: Sequence[BaseMessage],
    question: str,
    knowledge_plane: Any = None,
    memory_slots: Mapping[str, Any] | None = None,
    referenced_turns: Sequence[Mapping[str, Any]] | None = None,
    workspace: SqlWorkspace | Mapping[str, Any] | None = None,
    stored_folds: Sequence[Mapping[str, Any]] | None = None,
    token_budget: int | None = None,
    keep_turns: int | None = None,
    state: Mapping[str, Any] | None = None,
    config: Any = None,
) -> tuple[list[BaseMessage], int, list[dict[str, Any]]]:
    from apps.conversation.tooling import sanitize_messages_for_model

    spec_state: dict[str, Any] = dict(state or {})
    if referenced_turns is not None:
        spec_state["referenced_turns"] = list(referenced_turns)
    if knowledge_plane is not None:
        spec_state["knowledge_plane"] = (
            knowledge_plane.to_dump()
            if hasattr(knowledge_plane, "to_dump")
            else knowledge_plane
        )
    if memory_slots is not None:
        spec_state["memory_slots"] = dict(memory_slots)
    if workspace is not None:
        spec_state["sql_workspace"] = (
            workspace.model_dump(mode="json")
            if isinstance(workspace, SqlWorkspace)
            else dict(workspace)
        )
    spec = build_context_spec(
        spec_state,
        knowledge_plane=knowledge_plane,
        memory_slots=memory_slots,
        question=question,
        config=config,
    )
    system = SystemMessage(content=spec.stable_prefix())
    human = HumanMessage(content=question)
    accounted = [system, human]
    delta = spec.turn_delta()
    if delta:
        accounted.append(SystemMessage(content=delta))
    if spec.turn_brief:
        accounted.append(SystemMessage(content=spec.turn_brief))
    budget = int(token_budget if token_budget is not None else _token_budget())
    keep = int(keep_turns if keep_turns is not None else _keep_turns())
    folded, folds = fold_history(
        list(history),
        token_budget=budget,
        keep_turns=keep,
        extra_tokens=estimate_tokens(accounted),
        stored_folds=stored_folds,
    )
    messages = [system, *folded, human]
    return sanitize_messages_for_model(messages), len(messages) - 1, folds
