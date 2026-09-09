"""Session knowledge plane — sole schema/wiki context for the unified agent.

Wiki prose and physical table schema live here once. SystemMessage is the only
prompt surface that renders them; search_wiki ToolMessages return stubs.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import BaseMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field

WIKI_SCHEMA_GAP_SEARCH_LIMIT = 2
PROBE_SQL_LIMIT = 2

_TABLE_HEADER_RE = re.compile(r"^# Table:\s*([^,\n]+)", re.MULTILINE)
_SCHEMA_SPLIT_RE = re.compile(r"(?=^# Table: )", re.MULTILINE)
_WIKI_H2_SPLIT_RE = re.compile(r"(?=^## )", re.MULTILINE)
_WIKI_TABLE_HEADER_RE = re.compile(
    r"^##\s+.+?\s+\(\s*([A-Za-z_][\w.]*)\s*\)",
)
_FIELD_LINE_RE = re.compile(r"^\([^)\n]+:[^)\n]+\)")

_STUB_DATA_KEYS = (
    "added_tables",
    "added_pages",
    "schema_ready",
    "stop_search",
    "recall_status",
    "unchanged",
    "backend",
    "tables",
    "page_keys",
    "hit_count",
    "schema_gap_searches",
    "store_source",
)


class MergeDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    added_tables: list[str] = Field(default_factory=list)
    added_pages: list[str] = Field(default_factory=list)
    schema_ready: bool = False
    unchanged: bool = True


class AgentKnowledgePlane(BaseModel):
    """Deduped wiki passages + one schema blob per table."""

    model_config = ConfigDict(extra="forbid")

    wiki_passages: dict[str, str] = Field(default_factory=dict)
    schema_by_table: dict[str, str] = Field(default_factory=dict)
    page_keys: list[str] = Field(default_factory=list)
    tables: list[str] = Field(default_factory=list)
    schema_ready: bool = False
    backend: str = ""
    store_source: str = ""
    schema_gap_searches: int = 0
    coverage_fp: str = ""

    def to_dump(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dump(cls, raw: Mapping[str, Any] | None) -> AgentKnowledgePlane:
        if not raw:
            return cls()
        data = {k: v for k, v in dict(raw).items() if k in cls.model_fields}
        return cls.model_validate(data)

    def merge_recall(self, payload: Mapping[str, Any] | None) -> MergeDelta:
        data = dict(payload or {})
        added_pages: list[str] = []
        added_tables: list[str] = []

        for key in _page_keys_from(data):
            if key not in self.page_keys:
                self.page_keys.append(key)
                added_pages.append(key)

        wiki_text = str(data.get("knowledge_text") or "").strip()
        if wiki_text:
            self._store_wiki_blob(_page_keys_from(data), wiki_text)

        for name, body in split_schema_text(
            str(data.get("schema_text") or ""),
            tables=_table_names_from(data),
        ).items():
            if not name or name.startswith("_") or not body.strip():
                continue
            if not schema_body_has_fields(body):
                continue
            prior = self.schema_by_table.get(name)
            if prior == body:
                if name not in self.tables:
                    self.tables.append(name)
                    added_tables.append(name)
                continue
            if name not in self.tables:
                self.tables.append(name)
                added_tables.append(name)
            self.schema_by_table[name] = body

        if data.get("backend"):
            self.backend = str(data.get("backend") or self.backend)
        if data.get("store_source"):
            self.store_source = str(data.get("store_source") or self.store_source)

        self.schema_ready = any(
            schema_body_has_fields(body)
            for key, body in self.schema_by_table.items()
            if not str(key).startswith("_")
        )

        self.coverage_fp = _coverage_fp(self.page_keys, self.tables)
        unchanged = not added_pages and not added_tables
        return MergeDelta(
            added_tables=added_tables,
            added_pages=added_pages,
            schema_ready=self.schema_ready,
            unchanged=unchanged,
        )

    def _store_wiki_blob(self, page_keys: Sequence[str], wiki_text: str) -> None:
        """Keep one wiki blob per page-key set; overwrite instead of appending."""
        blob_key = ",".join(page_keys) if page_keys else "_wiki"
        incoming = set(page_keys) if page_keys else {"_wiki"}
        stale = [
            key
            for key in list(self.wiki_passages)
            if key != blob_key and set(str(key).split(",")) <= incoming
        ]
        for key in stale:
            del self.wiki_passages[key]
        self.wiki_passages[blob_key] = wiki_text

    def has_new_coverage(self, delta: MergeDelta) -> bool:
        return not delta.unchanged

    def apply_to_system_message(
        self,
        messages: Sequence[BaseMessage],
        *,
        memory_slots: Mapping[str, Any] | None = None,
        change_baseline: Mapping[str, Any] | None = None,
    ) -> list[BaseMessage]:
        return rebuild_system_message(
            messages,
            plane=self,
            memory_slots=memory_slots,
            change_baseline=change_baseline,
        )

    def render_system_sections(self) -> str:
        parts: list[str] = []
        wiki = "\n\n".join(
            text.strip() for text in self.wiki_passages.values() if str(text).strip()
        )
        if wiki:
            parts.append(
                "<wiki_knowledge>\n"
                "以下是当前任务相关的业务 Wiki 知识（计算口径与业务定义；表结构见 schema_catalog）：\n"
                f"{wiki}\n"
                "</wiki_knowledge>"
            )
            if not self.schema_ready:
                parts.append(
                    "<wiki_schema_gap>\n"
                    "当前 Wiki 召回没有给出可用的表结构或枚举页。"
                    "最多再调用一次针对性 search_wiki；若仍无表/枚举，立即停止工具调用并向用户说明知识不足。"
                    "禁止查询 information_schema / SHOW COLUMNS / DESCRIBE，禁止猜测字段写 SQL。\n"
                    "</wiki_schema_gap>"
                )
        schema = "\n".join(
            self.schema_by_table[name]
            for name in self.tables
            if self.schema_by_table.get(name)
        )
        extra = [
            body
            for key, body in self.schema_by_table.items()
            if key not in self.tables and not str(key).startswith("_") and body.strip()
        ]
        if extra:
            schema = (schema + "\n" + "\n".join(extra)).strip()
        if schema:
            parts.append(
                "<schema_catalog>\n"
                "当前会话已召回的物理表结构（同表只保留一份，后续 search_wiki 只补充新表）：\n"
                f"{schema}\n"
                "</schema_catalog>"
            )
        return "\n\n".join(parts)

    def apply_search_policy(self, delta: MergeDelta) -> dict[str, Any]:
        """Gap/stagnate policy owned by the plane, not llm_service attrs."""
        if self.schema_ready and delta.unchanged:
            return {
                "recall_status": "stagnant",
                "stop_search": True,
                "schema_ready": True,
                "schema_gap_searches": self.schema_gap_searches,
            }
        if self.schema_ready:
            self.schema_gap_searches = 0
            return {
                "recall_status": "hit",
                "stop_search": False,
                "schema_ready": True,
                "schema_gap_searches": 0,
            }
        self.schema_gap_searches += 1
        stagnant = self.schema_gap_searches >= WIKI_SCHEMA_GAP_SEARCH_LIMIT
        return {
            "recall_status": "stagnant" if stagnant else "schema_missing",
            "stop_search": stagnant,
            "schema_ready": False,
            "schema_gap_searches": self.schema_gap_searches,
        }


def schema_body_has_fields(schema_text: str) -> bool:
    """True when a table blob contains at least one field row (wiki or PROMPT)."""
    for raw in str(schema_text or "").splitlines():
        line = raw.strip().rstrip(",")
        if _FIELD_LINE_RE.match(line):
            return True
    return False


def physical_table_name(chunk: str) -> str | None:
    """Physical table id from `# Table:` or `## 中文名 (table)` headers."""
    first = ""
    for raw in str(chunk or "").splitlines():
        if raw.strip():
            first = raw.strip()
            break
    if not first:
        return None
    prompt = _TABLE_HEADER_RE.match(first)
    if prompt:
        name = str(prompt.group(1) or "").split(",")[0].strip()
        return name or None
    wiki = _WIKI_TABLE_HEADER_RE.match(first)
    if wiki:
        return str(wiki.group(1) or "").strip() or None
    return None


def recall_schema_is_ready(payload: Mapping[str, Any] | None) -> bool:
    """Usable schema = at least one physical table with field rows."""
    bodies = split_schema_text(
        str((payload or {}).get("schema_text") or ""),
        tables=_table_names_from(payload or {}),
    )
    return any(
        not str(name).startswith("_") and schema_body_has_fields(body)
        for name, body in bodies.items()
    )


def split_schema_text(
    schema_text: str, *, tables: Sequence[str] | None = None
) -> dict[str, str]:
    """Split concatenated wiki/PROMPT schema into physical_table → body."""
    text = str(schema_text or "").strip()
    if not text:
        return {}
    if text.startswith("# Table:"):
        chunks = [part.strip() for part in _SCHEMA_SPLIT_RE.split(text) if part.strip()]
    else:
        chunks = [
            part.strip() for part in _WIKI_H2_SPLIT_RE.split(text) if part.strip()
        ]
        if not chunks:
            chunks = [text]

    by_table: dict[str, str] = {}
    leftover: list[str] = []
    for chunk in chunks:
        name = physical_table_name(chunk)
        if name:
            by_table[name] = chunk
            continue
        leftover.append(chunk)
    if leftover and tables and not by_table:
        return {str(tables[0]): text}
    if leftover and not by_table:
        return {"_schema": text}
    if leftover:
        by_table["_relations"] = "\n".join(leftover)
    return by_table


def search_wiki_stub(
    *,
    delta: MergeDelta,
    policy: Mapping[str, Any],
    plane: AgentKnowledgePlane,
    backend: str = "",
) -> dict[str, Any]:
    """ToolMessage payload: coverage delta only, never full schema/wiki text."""
    return {
        "added_tables": list(delta.added_tables),
        "added_pages": list(delta.added_pages),
        "schema_ready": bool(policy.get("schema_ready")),
        "stop_search": bool(policy.get("stop_search")),
        "recall_status": str(policy.get("recall_status") or ""),
        "unchanged": bool(delta.unchanged),
        "backend": backend or plane.backend,
        "tables": list(plane.tables),
        "page_keys": list(plane.page_keys),
        "hit_count": len(delta.added_tables) + len(delta.added_pages),
        "schema_gap_searches": int(policy.get("schema_gap_searches") or 0),
        "store_source": plane.store_source,
    }


def strip_search_wiki_payload(data: Mapping[str, Any] | None) -> dict[str, Any]:
    """Guard: drop full-text fields if a caller still attached them."""
    raw = dict(data or {})
    return {key: raw[key] for key in _STUB_DATA_KEYS if key in raw}


def rebuild_system_message(
    messages: Sequence[BaseMessage],
    *,
    plane: AgentKnowledgePlane,
    memory_slots: Mapping[str, Any] | None = None,
    change_baseline: Mapping[str, Any] | None = None,
) -> list[BaseMessage]:
    from apps.chat.task.agent_prompt import build_agent_system_prompt

    text = build_agent_system_prompt(
        memory_slots=memory_slots,
        change_baseline=change_baseline,
        knowledge_plane=plane,
    )
    out = list(messages)
    if out and isinstance(out[0], SystemMessage):
        out[0] = SystemMessage(content=text)
    else:
        out.insert(0, SystemMessage(content=text))
    return out


def _page_keys_from(data: Mapping[str, Any]) -> list[str]:
    keys: list[str] = []
    for item in data.get("page_keys") or []:
        name = str(item or "").strip()
        if name and name not in keys:
            keys.append(name)
    return keys


def _table_names_from(data: Mapping[str, Any]) -> list[str]:
    names: list[str] = []
    for item in data.get("tables") or []:
        name = str(item or "").strip()
        if name and name not in names:
            names.append(name)
    return names


def _coverage_fp(page_keys: Sequence[str], tables: Sequence[str]) -> str:
    payload = f"{','.join(page_keys)}|{','.join(tables)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
