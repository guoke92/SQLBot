"""Deterministic whole-turn folding for the agent transcript.

Folding is a model-facing projection. Stored transcript stays full-fidelity.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage

from apps.conversation.messages import message_content_text
from apps.conversation.tooling import tool_result_from_message

DEFAULT_TOKEN_BUDGET = 48000
DEFAULT_KEEP_TURNS = 3

_CLARIFY_PREFIXES = ("用户已完成澄清", "用户已确认澄清")
_TABLE_HEADER_RE = re.compile(r"^##\s+.+\(\s*([A-Za-z_][\w.]*)\s*\)")
_TABLE_PROMPT_RE = re.compile(r"^# Table:\s*(\S+)")
_FIELD_LINE_RE = re.compile(r"^([A-Za-z_]\w*)\s*:")
_LABELS_RE = re.compile(r"labels=([^,\n]+)")


def estimate_tokens(messages: Sequence[Any]) -> int:
    """Cheap char/4 estimate; good enough to trigger whole-turn folds."""
    total = 0
    for message in messages:
        total += len(message_content_text(getattr(message, "content", "") or ""))
        for call in getattr(message, "tool_calls", None) or []:
            total += len(str(call))
        name = getattr(message, "name", None)
        if name:
            total += len(str(name))
    return max(1, (total + 3) // 4)


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
) -> tuple[list[BaseMessage], list[dict[str, Any]]]:
    """Fold oldest turns first (L1 then L2) until under budget; keep last K raw."""
    history = list(messages)
    turns = split_turns(history)
    if not turns:
        return history, []
    keep = max(int(keep_turns), 1)
    levels = [0] * len(turns)
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
    sql = _baseline_sql(turn)
    lines = [f'<turn_fold level="{1 if level < 2 else 2}">', f"问：{question}"]
    if clarification:
        lines.append(f"澄清：{clarification}")
    if sql:
        lines.append("SQL：")
        lines.append(sql)
    if level < 2:
        used = _used_schema_lines(turn, sql)
        if used:
            lines.append("用到：" + "；".join(used))
        pages = _page_keys(turn)
        if pages:
            lines.append("知识：page_keys=" + ", ".join(pages))
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


def _tool_payload(message: BaseMessage) -> dict[str, Any]:
    if (
        not isinstance(message, ToolMessage)
        and str(getattr(message, "type", "") or "") != "tool"
    ):
        return {}
    return tool_result_from_message(message)


def _baseline_sql(turn: Sequence[BaseMessage]) -> str:
    last = ""
    required = ""
    for message in turn:
        payload = _tool_payload(message)
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        sql = str(data.get("sql") or "").strip()
        if not sql:
            continue
        name = str(getattr(message, "name", "") or "")
        if name == "execute_sql_sandbox":
            last = sql
            if data.get("required") is not False:
                required = sql
        elif name == "patch_and_compile_sql" and not last:
            last = sql
    return required or last


def _sql_usage(sql: str) -> dict[str, list[str]]:
    tables: dict[str, list[str]] = {}
    if not str(sql or "").strip():
        return tables
    try:
        import sqlglot
        from sqlglot import exp
    except Exception:
        return tables
    try:
        statements = [item for item in sqlglot.parse(sql) if item is not None]
    except Exception:
        return tables
    for statement in statements:
        for table in statement.find_all(exp.Table):
            name = str(table.name or "").strip()
            if name:
                tables.setdefault(name, [])
        for column in statement.find_all(exp.Column):
            col = str(column.name or "").strip()
            if not col:
                continue
            table = ""
            raw_table = getattr(column, "table", None)
            if isinstance(raw_table, str):
                table = raw_table.strip()
            elif raw_table is not None:
                table = str(getattr(raw_table, "name", "") or "").strip()
            if table:
                bucket = tables.setdefault(table, [])
                if col not in bucket:
                    bucket.append(col)
            elif tables:
                first = next(iter(tables))
                if col not in tables[first]:
                    tables[first].append(col)
    return tables


def _schema_field_map(turn: Sequence[BaseMessage]) -> dict[str, dict[str, str]]:
    """table -> {column: labels-or-empty} from get_table_schema / get_dict_values."""
    fields: dict[str, dict[str, str]] = {}
    for message in turn:
        name = str(getattr(message, "name", "") or "")
        payload = _tool_payload(message)
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        if name == "get_table_schema":
            table = ""
            for line in str(data.get("schema_text") or "").splitlines():
                header = _TABLE_HEADER_RE.match(line) or _TABLE_PROMPT_RE.match(line)
                if header:
                    table = header.group(1)
                    fields.setdefault(table, {})
                    continue
                field_match = _FIELD_LINE_RE.match(line.strip())
                if not field_match or not table:
                    continue
                col = field_match.group(1)
                labels = _LABELS_RE.search(line)
                fields.setdefault(table, {})[col] = (
                    labels.group(1).strip() if labels else ""
                )
        elif name == "get_dict_values":
            table = str(data.get("table") or "").strip()
            field = str(data.get("field") or "").strip()
            values = data.get("values") or []
            if table and field and isinstance(values, list):
                labels = "|".join(
                    f"{item.get('value')}:{item.get('label')}"
                    if isinstance(item, Mapping)
                    else str(item)
                    for item in values
                    if item
                )
                fields.setdefault(table, {})[field] = labels
    return fields


def _used_schema_lines(turn: Sequence[BaseMessage], sql: str) -> list[str]:
    usage = _sql_usage(sql)
    schema = _schema_field_map(turn)
    lines: list[str] = []
    for table, cols in usage.items():
        known = schema.get(table) or {}
        wanted = cols or list(known)
        if not wanted:
            lines.append(table)
            continue
        parts: list[str] = []
        for col in wanted:
            labels = known.get(col) or ""
            parts.append(f"{col} labels={labels}" if labels else col)
        lines.append(f"{table}[{', '.join(parts)}]")
    return lines


def _page_keys(turn: Sequence[BaseMessage]) -> list[str]:
    keys: list[str] = []
    for message in turn:
        if str(getattr(message, "name", "") or "") != "search_knowledge":
            continue
        payload = _tool_payload(message)
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        for item in data.get("page_keys") or []:
            key = str(item or "").strip()
            if key and key not in keys:
                keys.append(key)
    return keys
