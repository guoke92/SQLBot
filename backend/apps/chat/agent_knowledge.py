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
# Tool budgets by category (single definition; the system prompt renders them).
PROBE_SQL_LIMIT = 2
KNOWLEDGE_ROUND_LIMIT = 2  # telemetry only; recall tools are not gated
KNOWLEDGE_SEARCH_LIMIT = 1  # legacy unused
KNOWLEDGE_BUDGET_SKIP = "knowledge_budget"
SEARCH_WIKI_ROUND_LIMIT = 2  # legacy alias of KNOWLEDGE_ROUND_LIMIT
EXECUTION_ROUND_LIMIT = 5
KNOWLEDGE_TOOLS = frozenset(
    {
        "get_table_schema",
        "get_table_relations",
        "search_knowledge",
        "lookup_values",
        "get_dict_values",
    }
)
# Clarify / knowledge / text-exit do not consume execution rounds.
UNCOUNTED_TOOLS = (
    frozenset({"request_clarification", "complete_without_sql"}) | KNOWLEDGE_TOOLS
)


def tool_calls_advance_round(calls: Sequence[Mapping[str, Any]]) -> bool:
    """Execution rounds advance only when at least one counted tool is called."""
    return any(
        str(item.get("name") or "") not in UNCOUNTED_TOOLS for item in calls or []
    )


_TABLE_HEADER_RE = re.compile(r"^# Table:\s*([^,\n]+)", re.MULTILINE)
_SCHEMA_SPLIT_RE = re.compile(r"(?=^# Table: )", re.MULTILINE)
_WIKI_H1_SPLIT_RE = re.compile(r"(?=^# )", re.MULTILINE)
_WIKI_H2_SPLIT_RE = re.compile(r"(?=^## )", re.MULTILINE)
_WIKI_TABLE_HEADER_RE = re.compile(
    r"^##\s+.+?\s+\(\s*([A-Za-z_][\w.]*)\s*\)",
)
# Field presence (schema_ready): wiki bare rows and PROMPT ``# Table:``
# blobs that still wrap columns as ``(name:type, …)``. Structured parse
# in wiki_schema.parse_field_line is bare-only.
_FIELD_LINE_RE = re.compile(r"^(?:\()?[A-Za-z_]\w*:.+")
_CONFLICT_CANDIDATE_KEYS = ("saying", "table", "field", "value", "value_label")

_STUB_DATA_KEYS = (
    "added_tables",
    "added_pages",
    "added_fields",
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
    "dropped_tables",
    "dropped_pages",
    "excluded",
    "focus",
    "focus_facts",
    "rejected_tables",
    "rejected_pages",
    "folded_tables",
)


def knowledge_key_variants(raw: str) -> set[str]:
    """page_key / ``tables/foo`` / physical name all match the same identity."""
    text = str(raw or "").strip()
    if not text:
        return set()
    variants = {text, text.rsplit("/", 1)[-1]}
    lowered = text.casefold()
    if lowered.startswith("tables/"):
        variants.add(text.split("/", 1)[1])
    return {item for item in variants if item}


def knowledge_key_matches(token: str, candidate: str) -> bool:
    left = {item.casefold() for item in knowledge_key_variants(token)}
    right = {item.casefold() for item in knowledge_key_variants(candidate)}
    return bool(left and right and left & right)


class MergeDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    added_tables: list[str] = Field(default_factory=list)
    added_pages: list[str] = Field(default_factory=list)
    added_evidence_pages: list[str] = Field(default_factory=list)
    # Fields newly promoted to a full line in the projected catalog (a
    # search_wiki round can widen relevance without adding a table).
    added_fields: dict[str, list[str]] = Field(default_factory=dict)
    schema_ready: bool = False
    unchanged: bool = True


class AgentKnowledgePlane(BaseModel):
    """Deduped wiki passages + one **full** schema blob per table.

    Schema bodies are stored as rendered by the corpus (all fields); the prompt
    projection (``project_schema``) runs at render time against the accumulated
    ``queries`` / ``keep_fields``, so visibility is monotonic across rounds.
    """

    model_config = ConfigDict(extra="forbid")

    wiki_passages: dict[str, str] = Field(default_factory=dict)
    schema_by_table: dict[str, str] = Field(default_factory=dict)
    page_keys: list[str] = Field(default_factory=list)
    tables: list[str] = Field(default_factory=list)
    schema_ready: bool = False
    backend: str = ""
    store_source: str = ""
    schema_gap_searches: int = 0
    search_rounds: int = 0
    idle_coarse_searches: int = 0
    coverage_fp: str = ""
    caliber_conflicts: list[dict[str, Any]] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)
    question: str = ""
    schema_outline: str = ""
    knowledge_rounds: int = 0
    knowledge_searches: int = 0
    value_grounding: str = ""
    keep_fields: dict[str, list[str]] = Field(default_factory=dict)
    # LLM-directed eviction: table names and/or wiki page_keys. Sticky until a
    # later search query explicitly names the key (restore), never auto-trimmed
    # by char/count budgets.
    excluded: list[str] = Field(default_factory=list)

    def to_dump(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dump(cls, raw: Mapping[str, Any] | None) -> AgentKnowledgePlane:
        if not raw:
            return cls()
        data = {k: v for k, v in dict(raw).items() if k in cls.model_fields}
        return cls.model_validate(data)

    def knowledge_refs(
        self, *, sql: str = "", dialect: str | None = None
    ) -> dict[str, Any]:
        """Durable snapshot. With ``sql``, only tables the statement actually used."""
        if not str(sql or "").strip():
            return {"page_keys": list(self.page_keys), "tables": list(self.tables)}
        from apps.chat.steps.recall_request import sql_references
        from apps.chat.steps.wiki_focus import is_binding_page

        used, _columns = sql_references(sql, dialect=dialect)
        if not used:
            return {"page_keys": list(self.page_keys), "tables": list(self.tables)}
        tables = [
            name for name in used if name in self.tables or name in self.schema_by_table
        ]
        if not tables:
            return {"page_keys": [], "tables": []}
        pages = [key for key in self.page_keys if is_binding_page(key, tables)]
        return {"page_keys": pages, "tables": tables}

    def prompt_stats(self) -> dict[str, Any]:
        """What the model sees this round (size of each system section)."""
        from apps.chat.steps.wiki_schema import project_schema
        from apps.knowledge.recall_kernel.types import RecallBudget

        schema, _visible = self._full_schema_text()
        projection = (
            project_schema(
                schema,
                budget_chars=RecallBudget.from_settings().schema_chars,
                queries=self.queries,
                keep_fields=self.keep_fields,
                present_pages=self.wiki_passages.keys(),
            )
            if schema
            else None
        )
        return {
            "tables": list(self.tables),
            "pages": len(self.page_keys),
            "excluded": list(self.excluded),
            "wiki_chars": sum(len(text) for text in self._wiki_texts_in_order()),
            "schema_chars_full": len(schema),
            "schema_chars": len(projection.text) if projection else 0,
            "schema_omitted": dict(projection.omitted) if projection else {},
            "enum_stripped": dict(projection.enum_stripped) if projection else {},
            "conflicts": len(self.caliber_conflicts),
            "queries": list(self.queries)[-3:],
        }

    def is_excluded(self, key: str) -> bool:
        token = str(key or "").strip()
        if not token:
            return False
        return any(knowledge_key_matches(item, token) for item in self.excluded)

    def _unexclude(self, key: str) -> None:
        token = str(key or "").strip()
        if not token:
            return
        self.excluded = [
            item for item in self.excluded if not knowledge_key_matches(item, token)
        ]

    def _query_restores(self, key: str, query: str) -> bool:
        text = str(query or "").casefold()
        if not text:
            return False
        tokens = knowledge_key_variants(key)
        for item in self.excluded:
            if knowledge_key_matches(item, key):
                tokens |= knowledge_key_variants(item)
        return any(len(token) >= 3 and token.casefold() in text for token in tokens)

    def _admit_key(self, key: str, query: str) -> bool:
        """False when the key is excluded and this query does not restore it."""
        token = str(key or "").strip()
        if not token or not self.is_excluded(token):
            return bool(token)
        if self._query_restores(token, query):
            self._unexclude(token)
            return True
        return False

    def exclude_knowledge(self, keys: Sequence[str]) -> dict[str, list[str]]:
        """Drop tables/pages from the prompt; later assembly skips them."""
        for raw in keys:
            token = str(raw or "").strip()
            if not token:
                continue
            if not any(knowledge_key_matches(token, item) for item in self.excluded):
                self.excluded.append(token)
        dropped_tables: list[str] = []
        kept_tables: list[str] = []
        for name in self.tables:
            if self.is_excluded(name):
                dropped_tables.append(name)
                self.schema_by_table.pop(name, None)
                self.keep_fields.pop(name, None)
            else:
                kept_tables.append(name)
        self.tables = kept_tables
        dropped_pages: list[str] = []
        kept_pages: list[str] = []
        for key in self.page_keys:
            if self.is_excluded(key):
                dropped_pages.append(key)
                self.wiki_passages.pop(key, None)
            else:
                kept_pages.append(key)
        self.page_keys = kept_pages
        for key in list(self.wiki_passages):
            if self.is_excluded(key):
                self.wiki_passages.pop(key, None)
                if key not in dropped_pages:
                    dropped_pages.append(key)
        self.coverage_fp = _coverage_fp(self.page_keys, self.tables)
        self.schema_ready = any(
            schema_body_has_fields(body)
            for key, body in self.schema_by_table.items()
            if not str(key).startswith("_")
        )
        return {"tables": dropped_tables, "pages": dropped_pages}

    def merge_recall(self, payload: Mapping[str, Any] | None) -> MergeDelta:
        data = dict(payload or {})
        added_pages: list[str] = []
        added_tables: list[str] = []
        relevant_before = self._relevant_index()

        query = str(data.get("query") or "").strip()
        question = str(data.get("question") or "").strip()
        if question and not self.question:
            self.question = question
        if self.question and self.question not in self.queries:
            self.queries.append(self.question)
        if query and query not in self.queries:
            self.queries.append(query)
        for table, names in dict(data.get("evidence_fields") or {}).items():
            if not self._admit_key(str(table), query):
                continue
            bucket = self.keep_fields.setdefault(str(table), [])
            for name in names or ():
                text = str(name).strip()
                if text and text not in bucket:
                    bucket.append(text)

        for key in _page_keys_from(data):
            if not self._admit_key(key, query):
                continue
            if key not in self.page_keys:
                self.page_keys.append(key)
                added_pages.append(key)

        wiki_passages = {
            key: text
            for key, text in _wiki_passages_from(data).items()
            if self._admit_key(key, query)
        }
        wiki_text = str(data.get("knowledge_text") or "").strip()
        admitted_pages = [
            key for key in _page_keys_from(data) if self._admit_key(key, query)
        ]
        if wiki_passages:
            self._ingest_wiki_passages(admitted_pages, "", wiki_passages)
        elif wiki_text and (admitted_pages or not self.excluded):
            self._ingest_wiki_passages(admitted_pages, wiki_text, None)

        for name, body in split_schema_text(
            str(data.get("schema_text") or ""),
            tables=_table_names_from(data),
        ).items():
            if not name or name.startswith("_") or not body.strip():
                continue
            if not self._admit_key(name, query):
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
        added_fields: dict[str, list[str]] = {}
        for table, names in self._relevant_index().items():
            if table in added_tables:
                continue
            new_names = sorted(names - relevant_before.get(table, set()))
            if new_names:
                added_fields[table] = new_names
        unchanged = not added_pages and not added_tables and not added_fields
        return MergeDelta(
            added_tables=added_tables,
            added_pages=added_pages,
            added_evidence_pages=list(added_pages),
            added_fields=added_fields,
            schema_ready=self.schema_ready,
            unchanged=unchanged,
        )

    def _full_schema_text(
        self, tables: Sequence[str] | None = None
    ) -> tuple[str, list[str]]:
        """Joined full bodies (tables first, then stray extras) + visible names."""
        order = list(tables) if tables is not None else list(self.tables)
        schema = "\n".join(
            self.schema_by_table[name]
            for name in order
            if self.schema_by_table.get(name) and not self.is_excluded(name)
        )
        extra: list[tuple[str, str]] = []
        if tables is None:
            extra = [
                (key, body)
                for key, body in self.schema_by_table.items()
                if key not in self.tables
                and not str(key).startswith("_")
                and body.strip()
                and not self.is_excluded(key)
            ]
            if extra:
                schema = (schema + "\n" + "\n".join(body for _, body in extra)).strip()
        visible = [
            name
            for name in order
            if self.schema_by_table.get(name) and not self.is_excluded(name)
        ]
        visible.extend(key for key, _body in extra)
        return schema, visible

    def _relevant_index(self) -> dict[str, set[str]]:
        from apps.chat.steps.wiki_schema import relevant_fields

        schema, _visible = self._full_schema_text()
        if not schema:
            return {}
        return relevant_fields(
            schema,
            queries=self.queries,
            keep_fields=self.keep_fields,
            present_pages=self.wiki_passages.keys(),
        )

    def _ingest_wiki_passages(
        self,
        page_keys: Sequence[str],
        wiki_text: str,
        wiki_passages: Mapping[str, str] | None = None,
    ) -> None:
        """One passage per page_key; merge upserts. Blob input is split on H1."""
        incoming = {
            str(key).strip(): str(text).strip()
            for key, text in dict(wiki_passages or {}).items()
            if str(key).strip() and str(text).strip() and not _is_blob_key(str(key))
        }
        if incoming:
            for key, text in incoming.items():
                self.wiki_passages[key] = text
                if key not in self.page_keys:
                    self.page_keys.append(key)
            self._drop_blob_passages()
            return

        chunks = _split_wiki_h1_pages(wiki_text)
        keys = [str(key).strip() for key in page_keys if str(key).strip()]
        if keys and len(chunks) == len(keys):
            for key, chunk in zip(keys, chunks, strict=True):
                self.wiki_passages[key] = chunk
            self._drop_blob_passages()
            return
        if len(chunks) == 1 and len(keys) == 1:
            self.wiki_passages[keys[0]] = chunks[0]
            self._drop_blob_passages()
            return
        if wiki_text.strip():
            self.wiki_passages["_wiki"] = wiki_text.strip()

    def _drop_blob_passages(self) -> None:
        for key in list(self.wiki_passages):
            if _is_blob_key(key):
                del self.wiki_passages[key]

    def has_new_coverage(self, delta: MergeDelta) -> bool:
        return not delta.unchanged

    def apply_to_system_message(
        self,
        messages: Sequence[BaseMessage],
        *,
        memory_slots: Mapping[str, Any] | None = None,  # noqa: ARG002 — calibers live in chat
        change_baseline: Mapping[str, Any] | None = None,  # noqa: ARG002
    ) -> list[BaseMessage]:
        return rebuild_system_message(messages, plane=self)

    def schema_catalog_text(self) -> str:
        """Prompt view of opened tables: full fields + JOINs among the working set."""
        from apps.chat.steps.wiki_schema import (
            RELATION_PEER_MISSING,
            filter_schema_relations,
            project_schema,
        )

        schema, _visible = self._full_schema_text()
        if not schema:
            return schema
        keep = {
            table: [item.name for item in fields]
            for table, fields in self._fields_by_table(schema).items()
        }
        projected = project_schema(
            schema,
            queries=self.queries,
            keep_fields=keep or self.keep_fields,
            present_pages=self.wiki_passages.keys(),
        ).text
        peers = [
            name
            for name in self.tables
            if name and not self.is_excluded(name) and self.schema_by_table.get(name)
        ]
        text = filter_schema_relations(projected, peer_tables=peers)
        return "\n".join(
            line for line in text.splitlines() if RELATION_PEER_MISSING not in line
        ).strip()

    @staticmethod
    def _fields_by_table(schema: str) -> dict[str, list[Any]]:
        from apps.chat.steps.wiki_schema import schema_fields_by_table

        return schema_fields_by_table(schema)

    def adopt_conflicts(
        self,
        questions: Sequence[Mapping[str, Any]] | None,
        confirmed: Any = None,
    ) -> list[dict[str, Any]]:
        """Keep Wiki-grounded conflicts that the user has not confirmed."""
        from apps.knowledge.recall_kernel.conflicts import unresolved_conflicts

        raw = [dict(item) for item in (questions or []) if isinstance(item, Mapping)]
        self.caliber_conflicts = unresolved_conflicts(raw, confirmed)
        return list(self.caliber_conflicts)

    def drop_resolved_conflicts(self, confirmed: Any = None) -> list[dict[str, Any]]:
        return self.adopt_conflicts(self.caliber_conflicts, confirmed)

    def render_system_sections(self) -> str:
        """System prompt only carries the bound outline. Tool payloads stay in ToolMessages."""
        return str(self.schema_outline or "").strip()

    def _knowledge_index_block(self) -> str:
        if not (self.tables or self.page_keys or self.excluded):
            return ""
        tables = ", ".join(self.tables) or "(none)"
        pages = ", ".join(self.page_keys) or "(none)"
        dropped = ", ".join(self.excluded) or "(none)"
        return (
            "<knowledge_index>\n"
            f"tables: {tables}\n"
            f"pages: {pages}\n"
            f"dropped: {dropped}\n"
            "tables 已展开完整字段；未列出的表只存在于 schema_outline，"
            "需要时再 get_table_schema。\n"
            "</knowledge_index>"
        )

    def _wiki_texts_in_order(self) -> list[str]:
        seen: set[str] = set()
        texts: list[str] = []
        for key in self.page_keys:
            if self.is_excluded(key):
                continue
            text = str(self.wiki_passages.get(key) or "").strip()
            if text:
                texts.append(text)
                seen.add(key)
        for key, raw in self.wiki_passages.items():
            if key in seen or self.is_excluded(key):
                continue
            text = str(raw).strip()
            if text:
                texts.append(text)
        return texts

    def _conflict_enum_covered(self, table: str, field: str) -> bool:
        """True only when the field's authoritative enum page text is in the prompt.

        Same rule as the catalog projection (``enum_page_present``): the field
        line's ``enum=`` pointer must resolve to a passage we actually hold —
        a same-named concept page does not count.
        """
        from apps.chat.steps.wiki_schema import (
            enum_page_present,
            schema_fields_by_table,
        )

        body = self.schema_by_table.get(str(table or ""))
        if not body:
            return False
        for item in schema_fields_by_table(body).get(str(table), []):
            if item.name == str(field or "") and item.enum:
                return enum_page_present(item.enum, self.wiki_passages.keys())
        return False

    def _slim_conflicts(self) -> list[dict[str, Any]]:
        """Prompt dump: table/field/value only; drop nested enums already in wiki."""
        out: list[dict[str, Any]] = []
        for item in self.caliber_conflicts:
            cands: list[dict[str, Any]] = []
            for raw in item.get("candidates") or []:
                if not isinstance(raw, Mapping):
                    continue
                slim = {
                    key: raw[key]
                    for key in _CONFLICT_CANDIDATE_KEYS
                    if key in raw and raw[key] not in (None, "")
                }
                table = str(raw.get("table") or "")
                field = str(raw.get("field") or "")
                if raw.get("enum_values") and not self._conflict_enum_covered(
                    table, field
                ):
                    slim["enum_values"] = raw["enum_values"]
                cands.append(slim)
            slim_item = {
                key: value for key, value in item.items() if key != "candidates"
            }
            slim_item["candidates"] = cands
            out.append(slim_item)
        return out

    def apply_search_policy(
        self, delta: MergeDelta, *, focus: str = "all"
    ) -> dict[str, Any]:
        """Flag redundant searches; never hard-lock a later new-concept search.

        ``focus=all`` only counts **admitted** new tables or binding pages
        (dicts/calibers/concepts/tables) as progress. Rejected long-tail
        tables, peripheral rules/process pages, and projected field folds
        do not reset idle search guidance.
        Local ``field``/``enum``/``term``/``relation`` checks count confirmed
        facts (``added_fields`` or caller-supplied status).
        """
        from apps.chat.steps.wiki_focus import (
            LOCAL_FOCUS,
            binding_pages,
            normalize_focus,
        )

        kind = normalize_focus(focus)
        if kind in LOCAL_FOCUS:
            found = bool(delta.added_fields) or not delta.unchanged
            return {
                "recall_status": "hit" if found else "not_found",
                "stop_search": not found,
                "schema_ready": self.schema_ready,
                "schema_gap_searches": self.schema_gap_searches,
            }
        bound = binding_pages(delta.added_pages, [*self.tables, *delta.added_tables])
        progressed = bool(delta.added_tables or bound)
        if progressed:
            self.schema_gap_searches = 0
            self.idle_coarse_searches = 0
            return {
                "recall_status": "hit" if self.schema_ready else "schema_missing",
                "stop_search": False,
                "schema_ready": self.schema_ready,
                "schema_gap_searches": self.schema_gap_searches,
            }
        if self.schema_ready:
            self.idle_coarse_searches += 1
            return {
                "recall_status": "diminishing_returns",
                "stop_search": True,
                "schema_ready": True,
                "schema_gap_searches": self.schema_gap_searches,
            }
        if delta.unchanged:
            self.schema_gap_searches += 1
            return {
                "recall_status": "schema_missing",
                "stop_search": False,
                "schema_ready": False,
                "schema_gap_searches": self.schema_gap_searches,
            }
        self.schema_gap_searches += 1
        return {
            "recall_status": "schema_missing",
            "stop_search": False,
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
    hit_count: int | None = None,
) -> dict[str, Any]:
    """ToolMessage payload: coverage delta only, never full schema/wiki text."""
    recalled = (
        int(hit_count)
        if hit_count is not None
        else len(delta.added_tables) + len(delta.added_pages)
    )
    from apps.chat.steps.wiki_focus import LOOKUP_FOUND_LIMIT, is_peripheral_page

    facts = dict(policy.get("focus_facts") or {})
    found = list(facts.get("found") or [])[:LOOKUP_FOUND_LIMIT]
    if found != list(facts.get("found") or []):
        facts = {**facts, "found": found}
    rejected_pages = [
        key
        for key in (policy.get("rejected_pages") or [])
        if not is_peripheral_page(str(key))
    ]
    return {
        "added_tables": list(delta.added_tables),
        "added_pages": list(delta.added_pages),
        "added_fields": {k: list(v) for k, v in delta.added_fields.items()},
        "schema_ready": bool(policy.get("schema_ready")),
        "stop_search": bool(policy.get("stop_search")),
        "recall_status": str(policy.get("recall_status") or ""),
        "unchanged": bool(delta.unchanged),
        "backend": backend or plane.backend,
        "tables": list(plane.tables),
        "page_keys": list(plane.page_keys),
        "hit_count": recalled,
        "schema_gap_searches": int(policy.get("schema_gap_searches") or 0),
        "store_source": plane.store_source,
        "dropped_tables": list(policy.get("dropped_tables") or []),
        "dropped_pages": list(policy.get("dropped_pages") or []),
        "excluded": list(plane.excluded),
        "focus": str(policy.get("focus") or "all"),
        "focus_facts": facts,
        "rejected_tables": list(policy.get("rejected_tables") or []),
        "rejected_pages": rejected_pages,
        "folded_tables": list(policy.get("folded_tables") or []),
    }


def strip_search_wiki_payload(data: Mapping[str, Any] | None) -> dict[str, Any]:
    """Guard: drop full-text fields if a caller still attached them."""
    raw = dict(data or {})
    return {key: raw[key] for key in _STUB_DATA_KEYS if key in raw}


def rebuild_system_message(
    messages: Sequence[BaseMessage],
    *,
    plane: AgentKnowledgePlane,
    memory_slots: Mapping[str, Any] | None = None,  # noqa: ARG001
    change_baseline: Mapping[str, Any] | None = None,  # noqa: ARG001
) -> list[BaseMessage]:
    from apps.chat.task.agent_prompt import build_agent_system_prompt

    text = build_agent_system_prompt(knowledge_plane=plane)
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


def _wiki_passages_from(data: Mapping[str, Any]) -> dict[str, str]:
    raw = data.get("wiki_passages")
    if not isinstance(raw, Mapping):
        raw = data.get("passages")
    if not isinstance(raw, Mapping):
        return {}
    out: dict[str, str] = {}
    for key, text in raw.items():
        name = str(key or "").strip()
        body = str(text or "").strip()
        if name and body and not _is_blob_key(name):
            out[name] = body
    return out


def _split_wiki_h1_pages(wiki_text: str) -> list[str]:
    text = str(wiki_text or "").strip()
    if not text:
        return []
    if not text.startswith("# "):
        match = re.search(r"(?m)^# ", text)
        if match is None:
            return [text]
        text = text[match.start() :]
    return [part.strip() for part in _WIKI_H1_SPLIT_RE.split(text) if part.strip()]


def _is_blob_key(key: str) -> bool:
    return key == "_wiki" or "," in key


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
