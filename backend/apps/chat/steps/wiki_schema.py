"""Wiki-backend schema rendering (P2) — table pages as schema authority.

wiki 后端下 planner 的 schema_text 改由 wiki table 页渲染：物理类型(phys)、
注释(desc)、值集(topk)、展示名(labels)、枚举页指针(enum)、**表间关联(relation 段)**
一并呈现；字段行 ``name:type, comment[, topk=...][, labels=...][, enum=...]``，
全量缓存还可带 ``group=`` / ``scenes=``（投影输出会剥掉，不进规划器）。
label 只取首个顶层逗号后的第一段；关联行以 ``关联:`` 开头，不进入 label 候选池。
关联行尾方括号是边的观察来源（write-flow / java-eq / ref-convention /
db-index / db-naming），不是选用建议。

列全集不变式在生成侧保证（baseline 断言 字段数==db 列数），本渲染器不做
运行时回退——某表 wiki 页缺失时该表用 db catalog 直渲并记
``SCHEMA_PAGE_MISSING`` 遥测（update.py 增量触发下轮补齐）。

三层、各只实现一次：

1. ``WikiSchemaRenderer`` —— **全量**渲染（全部字段 + 全部紧凑 ``关联:`` 行）。
   渲染结果只依赖语料，不依赖问题，因此可在会话 plane 中按表缓存并跨轮复用。
2. ``project_schema`` —— 提示词投影：枚举页在场时去掉 ``topk=``，保留
   ``labels=`` 与 ``enum=``。无场景标注的表（v1）整表入 prompt。带
   ``group=`` / ``scenes=`` 的表按召回场景窗裁剪：always ∪ 命中场景窗 ∪
   证据列 ∪ 问题点名列 ∪ JOIN 端点；未入窗的列不进 prompt。
3. ``filter_schema_relations`` —— 按累计工作集投影关联行（入选 / 对端未入选 /
   丢弃噪声边）。Agent plane 的 ``schema_catalog_text`` 与 NLQ ``render_schema``
   共用 2 与 3。
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common.utils.utils import SQLBotLogUtil

# schema_field_labels 行格式：name:type, comment[, topk=...][, labels=...][, enum=...]
_FIELD_LINE = "{field}:{type}, {comment}{tail}"
# 关联段行（enrich 生成）：`- [[t2]]：t1.fk → t2.pk（write-flow:Foo，confirmed）`
# 提示词只保留观察来源（write-flow / java-eq / …），丢掉 suggested/confirmed。
_RELATION_ROW_RE = re.compile(
    r"^- \[\[(?P<right>[^\]]+)\]\]："
    r"(?P<left_ref>[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)\s*→\s*"
    r"(?P<right_ref>[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)"
    r"(?:\s*（(?P<note>[^）]*)）)?",
    re.M,
)
_RELATION_HEADING = "## 关联表"
_FIELD_REF_RE = re.compile(r"\b([a-z][a-z0-9_]*)\.([a-zA-Z][a-zA-Z0-9_]*)\b")
_CJK_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")
_TABLE_HEAD_RE = re.compile(r"^##\s+.+\(\s*([A-Za-z_][\w.]*)\s*\)")
_FIELD_NAME_RE = re.compile(r"^([A-Za-z_]\w*):")
_FIELD_BARE_RE = re.compile(r"^(?P<name>[A-Za-z_]\w*):(?P<rest>.*)$")
_RELATION_NOTE_SEP_RE = re.compile(r"[，,]")
_RELATION_TRUST_LABELS = frozenset({"suggested", "confirmed", "candidate", "inferred"})
_TYPE_DISPLAY_WIDTH_RE = re.compile(
    r"^(?P<base>tinyint|smallint|mediumint|int|integer|bigint|"
    r"varchar|nvarchar|char|nchar|character varying|character|"
    r"binary|varbinary)\s*\(\s*\d+\s*\)\s*$",
    re.I,
)
_TYPE_TIME_PREC_RE = re.compile(
    r"^(?P<base>datetime|timestamp|time)\s*\(\s*\d+\s*\)\s*$",
    re.I,
)
_TYPE_ALIASES = {
    "integer": "int",
    "nvarchar": "varchar",
    "nchar": "char",
    "character varying": "varchar",
    "character": "char",
}
_RELATION_PROMPT_RE = re.compile(
    r"^关联:\s*"
    r"(?P<left_table>[A-Za-z_][\w]*)\.(?P<left_col>[A-Za-z_]\w*)"
    r"\s*→\s*"
    r"(?P<right_table>[A-Za-z_][\w]*)\.(?P<right_col>[A-Za-z_]\w*)"
    r"(?:\s*\((?P<peer>[^)]+)\))?"
    r"(?:\s*\[(?P<tag>[^\]]+)\])?"
    r"(?:\s*（对端未入选）)?"
)
RELATION_PEER_MISSING = "（对端未入选）"
OMITTED_FIELDS_PREFIX = "其余字段:"
# Folded items: ``name（comment）`` joined by ``; `` so comments may contain commas.
_OMITTED_ITEM_RE = re.compile(r"([A-Za-z_]\w*)(?:（(?P<comment>[^）]*)）)?")
_TEMPORAL_TYPE_RE = re.compile(r"date|time|timestamp|year", re.I)
_MEASURE_TYPE_RE = re.compile(r"decimal|numeric|double|float|real|money|number", re.I)


# ── store lookups ───────────────────────────────────────────────────────────


def _lookup_store_page(
    store: Any,
    slug: str,
    *,
    belong: str | None = None,
    page_type: str | None = None,
) -> Any | None:
    if store is None:
        return None
    pages = getattr(store, "pages", {}) or {}
    if belong:
        prefixed = pages.get(f"{belong}/{slug}")
        if prefixed is not None:
            return prefixed
    page = pages.get(slug)
    if page is not None:
        actual = getattr(page, "type", None)
        if page_type and actual not in (page_type, None, ""):
            return None
        return page
    getter = getattr(store, "get_page", None)
    if not callable(getter):
        return None
    page = getter(slug)
    if page is None:
        return None
    actual = getattr(page, "type", None)
    if page_type and actual not in (page_type, None, ""):
        return None
    return page


def _wiki_table_block(page_text: str) -> dict[str, Any] | None:
    """解析 table 页的 ground:table 块（已发布的权威字段清单）。"""
    m = re.search(r"```ground:table\n([\s\S]*?)\n```", page_text)
    if not m:
        return None
    try:
        import yaml

        data = yaml.safe_load(m.group(1)) or {}
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


def enum_page_key(dict_key: str) -> str:
    """dict 指针 → 权威枚举页 store key（``enums/<slug>``）。"""
    slug = str(dict_key or "").strip().rsplit("/", 1)[-1]
    return f"enums/{slug}" if slug else ""


def enum_page_present(dict_key: str, present_pages: Iterable[str] | None) -> bool:
    """枚举页是否**真在** prompt 中——只认精确 ``enums/<slug>``，不认同名概念页。"""
    target = enum_page_key(dict_key)
    if not target or not present_pages:
        return False
    return any(str(key).strip() == target for key in present_pages)


def recalled_scenario_keys(present_pages: Iterable[str] | None) -> set[str]:
    """``scenarios/<slug>`` store keys → scenario page_key。裸 slug 不算场景。"""
    out: set[str] = set()
    for raw in present_pages or ():
        key = str(raw or "").strip()
        if key.startswith("scenarios/") and len(key) > len("scenarios/"):
            out.add(key.split("/", 1)[1])
    return out


def collect_schema_evidence(
    store: Any,
    *,
    page_keys: Sequence[str],
    tables: Sequence[str],
) -> dict[str, set[str]]:
    """Field evidence from recalled pages: field_targets, calibers, maps_to."""
    table_set = {str(name) for name in tables if str(name).strip()}
    out: dict[str, set[str]] = {name: set() for name in table_set}

    def _add(table: str, fname: str) -> None:
        if table in out and fname:
            out[table].add(fname)

    for raw_key in page_keys:
        page = _lookup_store_page(store, str(raw_key))
        if page is None:
            page = _lookup_store_page(store, str(raw_key).rsplit("/", 1)[-1])
        if page is None:
            continue
        for target in getattr(page, "field_targets", ()) or ():
            match = _FIELD_REF_RE.search(str(target))
            if match:
                _add(match.group(1), match.group(2))
        maps_to = str(getattr(page, "maps_to", "") or "")
        for match in _FIELD_REF_RE.finditer(maps_to):
            _add(match.group(1), match.group(2))
        for block in getattr(page, "ground_blocks", ()) or ():
            kind = getattr(block, "kind", "")
            data = getattr(block, "data", {}) or {}
            if kind == "caliber":
                predicate = str(data.get("predicate") or "")
                for match in _FIELD_REF_RE.finditer(predicate):
                    _add(match.group(1), match.group(2))
            elif kind == "scenario":
                for group in ("hubs", "shared"):
                    for item in data.get(group) or []:
                        if not isinstance(item, dict):
                            continue
                        table = str(item.get("table") or "")
                        for fname in item.get("window") or []:
                            _add(table, str(fname))
    return out


def merge_field_sets(
    *sources: Mapping[str, Iterable[str]] | None,
) -> dict[str, set[str]]:
    """Union of ``{table: fields}`` maps (evidence ∪ baseline ∪ …)."""
    out: dict[str, set[str]] = {}
    for source in sources:
        for table, names in dict(source or {}).items():
            bucket = out.setdefault(str(table), set())
            bucket.update(str(name) for name in (names or ()) if str(name).strip())
    return out


# ── field line model ────────────────────────────────────────────────────────


def compact_field_type(raw: str) -> str:
    """Drop display widths that do not change SQL quoting / function choice.

    ``varchar(128)`` / ``bigint(20)`` / ``char(1)`` → family name. Keep
    ``decimal(p,s)`` (scale can matter) and ``date`` vs ``datetime``.
    """
    text = str(raw or "").strip()
    if not text:
        return text
    matched = _TYPE_DISPLAY_WIDTH_RE.match(text)
    if matched:
        base = re.sub(r"\s+", " ", matched.group("base").strip().lower())
        return _TYPE_ALIASES.get(base, base)
    timed = _TYPE_TIME_PREC_RE.match(text)
    if timed:
        return timed.group("base").lower()
    return text


def format_enum_labels(values: Sequence[str], labels: Mapping[str, str]) -> str:
    """``ADD:未生效|EFFECT:已生效`` — display names, never mixed into topk."""
    parts: list[str] = []
    for raw in values:
        value = str(raw or "").strip()
        if not value:
            continue
        label = str(labels.get(value) or "").strip()
        if not label or label == value:
            continue
        safe = label.replace("|", "／").replace(":", "：")
        parts.append(f"{value}:{safe}")
    return "|".join(parts)


@dataclass(frozen=True)
class SchemaField:
    name: str
    type: str
    comment: str
    topk: str = ""
    labels: str = ""
    enum: str = ""
    owned_labels: bool = False
    group: str = ""
    scenes: tuple[str, ...] = ()

    def render(
        self,
        *,
        with_topk: bool = True,
        with_labels: bool | None = None,
        with_meta: bool = False,
    ) -> str:
        show_labels = with_topk if with_labels is None else with_labels
        tail = ""
        if self.topk and with_topk:
            tail += f", topk={self.topk}"
        if self.labels and show_labels:
            tail += f", labels={self.labels}"
        if self.enum:
            tail += f", enum={self.enum}"
        if with_meta and self.group:
            tail += f", group={self.group}"
        if with_meta and self.scenes:
            tail += f", scenes={'|'.join(self.scenes)}"
        return _FIELD_LINE.format(
            field=self.name,
            type=compact_field_type(self.type),
            comment=self.comment,
            tail=tail,
        )

    def render_omitted(self) -> str:
        """Compact prompt token: name plus comment, no type / topk."""
        comment = str(self.comment or "").replace("（", "").replace("）", "").strip()
        if comment and comment != self.name:
            return f"{self.name}（{comment}）"
        return self.name


def _split_top_level(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    return parts


def relation_source_tag(note: str) -> str:
    """Wiki note → prompt tag: evidence kind only, never suggested/confirmed.

    ``write-flow:Foo.java，confirmed`` → ``write-flow``
    ``ref-convention，suggested`` → ``ref-convention``
    """
    text = str(note or "").strip()
    if not text:
        return ""
    head = _RELATION_NOTE_SEP_RE.split(text, maxsplit=1)[0].strip()
    kind = head.split(":", 1)[0].strip().lower()
    if not kind or kind in _RELATION_TRUST_LABELS:
        return ""
    return kind


def parse_field_line(line: str) -> SchemaField | None:
    stripped = line.strip().rstrip(",")
    match = _FIELD_BARE_RE.match(stripped)
    if match is None:
        return None
    # ``type`` may itself contain a comma inside parens (decimal(18,2)) —
    # split on top-level commas only.
    segments = _split_top_level(match.group("rest"))
    if len(segments) < 2:
        return None
    ftype = segments[0].strip()
    comment = segments[1].strip()
    topk = ""
    labels = ""
    enum = ""
    group = ""
    scenes: tuple[str, ...] = ()
    for segment in segments[2:]:
        key, sep, value = segment.strip().partition("=")
        if not sep:
            continue
        if key == "topk":
            topk = value.strip()
        elif key == "labels":
            labels = value.strip()
        elif key == "enum":
            enum = value.strip()
        elif key == "group":
            group = value.strip()
        elif key == "scenes":
            scenes = tuple(part for part in value.strip().split("|") if part)
    return SchemaField(
        name=match.group("name"),
        type=ftype,
        comment=comment,
        topk=topk,
        labels=labels,
        enum=enum,
        group=group,
        scenes=scenes,
    )


def omitted_field_names(line: str) -> list[str]:
    """Physical names from a ``其余字段:`` line (new ``;`` form or legacy commas)."""
    tail = line.strip()
    if tail.startswith(OMITTED_FIELDS_PREFIX):
        tail = tail[len(OMITTED_FIELDS_PREFIX) :]
    return [match.group(1) for match in _OMITTED_ITEM_RE.finditer(tail)]


def format_omitted_fields(items: Sequence[SchemaField]) -> str:
    """One folded line: names stay, comments stay, types/topk drop."""
    parts = [item.render_omitted() for item in items if item.name]
    return f"{OMITTED_FIELDS_PREFIX} {'; '.join(parts)}"


# ── relevance (single definition, shared by projection / enum pin / stub) ──


def _is_fk_like_column(name: str) -> bool:
    """Local JOIN endpoint by naming convention (``ref_*`` / ``*_id``)."""
    lowered = name.lower()
    if lowered == "id":
        return False
    return lowered.startswith("ref_") or lowered.endswith("_id")


def resolve_fk_peer_table(field_name: str, known_tables: Iterable[str]) -> str | None:
    """Decode a local FK column to a peer table that exists in ``known_tables``.

    Conventions (same as live/db renderers — one implementation):
    - ``ref_<peer>`` / ``ref_<x>_<peer>`` → peer
    - ``<peer>_id`` → ``<peer>`` or ``d_<peer>`` when either is in the catalog

    Returns the catalog table name, or ``None`` when no real peer matches.
    """
    known = {str(name).strip() for name in known_tables if str(name).strip()}
    raw = str(field_name or "").strip()
    if not raw or raw == "id" or not _is_fk_like_column(raw):
        return None
    candidates: list[str] = []
    if raw.startswith("ref_"):
        stem = raw[len("ref_") :]
        candidates.append(stem)
        for sep_at in range(len(stem)):
            if stem[sep_at] == "_" and sep_at + 1 < len(stem):
                candidates.append(stem[sep_at + 1 :])
    elif raw.endswith("_id"):
        stem = raw[: -len("_id")]
        candidates.extend((stem, f"d_{stem}"))
    for peer in candidates:
        if peer and peer in known:
            return peer
    return None


def _cjk_bigrams(text: str) -> set[str]:
    grams: set[str] = set()
    for run in _CJK_TOKEN_RE.findall(text or ""):
        grams.update(run[i : i + 2] for i in range(len(run) - 1))
    return grams


def _query_hits_field(name: str, comment: str, queries: Sequence[str]) -> bool:
    """双向词命中：注释与问题共享任一中文二元词，或 ASCII 词互含，或字段名 ⊂ 问题。"""
    if not queries:
        return False
    lowered = name.casefold()
    comment_grams = _cjk_bigrams(comment)
    comment_ascii = [tok.casefold() for tok in _ASCII_TOKEN_RE.findall(comment or "")]
    for query in queries:
        q = str(query or "")
        if not q:
            continue
        qf = q.casefold()
        if len(lowered) >= 3 and lowered in qf:
            return True
        if comment_grams & _cjk_bigrams(q):
            return True
        if any(tok in qf for tok in comment_ascii):
            return True
    return False


def _relation_endpoints(lines: Sequence[str], table: str) -> set[str]:
    cols: set[str] = set()
    for raw in lines:
        parsed = _RELATION_PROMPT_RE.match(raw.strip())
        if parsed is None:
            continue
        if parsed.group("left_table") == table:
            cols.add(parsed.group("left_col"))
        if parsed.group("right_table") == table:
            cols.add(parsed.group("right_col"))
    return cols


RANK_EVIDENCE = 0  # evidence / baseline column / JOIN endpoint / scene window
RANK_QUERY = 1  # comment or name matches the turn's wording
RANK_STRUCTURAL = 2  # enum-bound, identity/FK-like, temporal or measure type


def section_is_scene_annotated(fields: Sequence[SchemaField]) -> bool:
    return any(item.group or item.scenes for item in fields)


def field_in_recalled_scene(
    item: SchemaField, recalled_scenarios: Iterable[str]
) -> bool:
    if item.group == "always":
        return True
    recalled = {str(s) for s in recalled_scenarios if str(s)}
    return bool(recalled and set(item.scenes) & recalled)


def field_relevance_rank(
    item: SchemaField,
    *,
    keep: set[str],
    relation_cols: set[str],
    queries: Sequence[str],
    recalled_scenarios: Iterable[str] = (),
) -> int | None:
    """The one relevance rule. ``None`` = foldable under budget pressure."""
    if item.name in keep or item.name in relation_cols:
        return RANK_EVIDENCE
    if field_in_recalled_scene(item, recalled_scenarios):
        return RANK_EVIDENCE
    if _query_hits_field(item.name, item.comment, queries):
        return RANK_QUERY
    if item.enum or item.name.lower() == "id" or _is_fk_like_column(item.name):
        return RANK_STRUCTURAL
    if _TEMPORAL_TYPE_RE.search(item.type) or _MEASURE_TYPE_RE.search(item.type):
        return RANK_STRUCTURAL
    return None


def field_is_relevant(
    item: SchemaField,
    *,
    keep: set[str],
    relation_cols: set[str],
    queries: Sequence[str],
    recalled_scenarios: Iterable[str] = (),
) -> bool:
    return (
        field_relevance_rank(
            item,
            keep=keep,
            relation_cols=relation_cols,
            queries=queries,
            recalled_scenarios=recalled_scenarios,
        )
        is not None
    )


def _keep_scene_field(
    item: SchemaField,
    *,
    keep: set[str],
    relation_cols: set[str],
    queries: Sequence[str],
    recalled_scenarios: Iterable[str],
) -> bool:
    """Scene-annotated tables: do not dump structural/enum columns by default."""
    if item.name in keep or item.name in relation_cols:
        return True
    if field_in_recalled_scene(item, recalled_scenarios):
        return True
    return _query_hits_field(item.name, item.comment, queries)


# ── table section model ─────────────────────────────────────────────────────


@dataclass
class _TableSection:
    table: str
    header: str
    fields: list[SchemaField] = field(default_factory=list)
    others: list[str] = field(default_factory=list)  # relation lines etc.

    def relation_cols(self) -> set[str]:
        return _relation_endpoints(self.others, self.table)


def _parse_sections(schema_text: str) -> list[_TableSection]:
    """Wiki ``## 注释 (table)`` sections; anything before the first header (e.g.
    PROMPT-style ``# Table:`` blobs) is passed through verbatim, in order."""
    sections: list[_TableSection] = []
    current: _TableSection | None = None
    for raw in str(schema_text or "").splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        head = _TABLE_HEAD_RE.match(stripped)
        if head:
            current = _TableSection(table=str(head.group(1)), header=stripped)
            sections.append(current)
            continue
        if current is None:
            current = _TableSection(table="", header="")
            sections.append(current)
        if not current.table:
            current.others.append(stripped)
            continue
        parsed = parse_field_line(stripped)
        if parsed is not None:
            current.fields.append(parsed)
        else:
            current.others.append(stripped)
    return sections


def schema_fields_by_table(schema_text: str) -> dict[str, list[SchemaField]]:
    return {s.table: list(s.fields) for s in _parse_sections(schema_text) if s.table}


@dataclass(frozen=True)
class SchemaProjection:
    text: str
    omitted: dict[str, int]
    enum_stripped: dict[str, list[str]]
    relevant: dict[str, list[str]]

    def as_stats(self) -> dict[str, Any]:
        return {
            "chars": len(self.text),
            "omitted": dict(self.omitted),
            "enum_stripped": {k: list(v) for k, v in self.enum_stripped.items()},
        }


def relevant_fields(
    schema_text: str,
    *,
    queries: Sequence[str] = (),
    keep_fields: Mapping[str, Iterable[str]] | None = None,
    present_pages: Iterable[str] | None = None,
) -> dict[str, set[str]]:
    """``{table: relevant field names}`` — the one relevance rule."""
    keep = merge_field_sets(keep_fields)
    recalled = recalled_scenario_keys(present_pages)
    out: dict[str, set[str]] = {}
    for section in _parse_sections(schema_text):
        if not section.table:
            continue
        rel_cols = section.relation_cols()
        annotated = section_is_scene_annotated(section.fields)
        names: set[str] = set()
        for item in section.fields:
            if annotated:
                if _keep_scene_field(
                    item,
                    keep=keep.get(section.table, set()),
                    relation_cols=rel_cols,
                    queries=queries,
                    recalled_scenarios=recalled,
                ):
                    names.add(item.name)
            elif field_is_relevant(
                item,
                keep=keep.get(section.table, set()),
                relation_cols=rel_cols,
                queries=queries,
                recalled_scenarios=recalled,
            ):
                names.add(item.name)
        out[section.table] = names
    return out


def project_schema(
    schema_text: str,
    *,
    budget_chars: int = 0,
    queries: Sequence[str] = (),
    keep_fields: Mapping[str, Iterable[str]] | None = None,
    present_pages: Iterable[str] | None = None,
) -> SchemaProjection:
    """Prompt projection of a full schema blob.

    When the enum page is actually in the prompt, drop ``topk=`` (SQL values
    live on the enum page) but keep ``labels=`` and the ``enum=`` pointer.
    Field-owned labels are column-specific overlay; enum pages still carry
    conversion flows / state machines.

    Tables without ``group=`` / ``scenes=`` stay full (v1). Scene-annotated
    tables keep always ∪ recalled scenario windows ∪ evidence ∪ query hits ∪
    JOIN endpoints. ``budget_chars`` is accepted for call-site compatibility
    and ignored.
    """
    present = {str(key).strip() for key in (present_pages or ())}
    keep = merge_field_sets(keep_fields)
    recalled = recalled_scenario_keys(present)
    sections = _parse_sections(schema_text)
    enum_stripped: dict[str, list[str]] = {}
    for section in sections:
        for item in section.fields:
            if item.topk and item.enum and enum_page_present(item.enum, present):
                enum_stripped.setdefault(section.table, []).append(item.name)

    relevant: dict[str, set[str]] = {}
    omitted: dict[str, int] = {}
    blocks: list[str] = []
    for section in sections:
        lines = [section.header] if section.header else []
        stripped = set(enum_stripped.get(section.table, ()))
        rel_cols = section.relation_cols() if section.table else set()
        annotated = section_is_scene_annotated(section.fields)
        kept: list[SchemaField] = []
        dropped = 0
        for item in section.fields:
            if annotated and not _keep_scene_field(
                item,
                keep=keep.get(section.table, set()),
                relation_cols=rel_cols,
                queries=queries,
                recalled_scenarios=recalled,
            ):
                dropped += 1
                continue
            kept.append(item)
        if section.table:
            relevant[section.table] = {item.name for item in kept}
            if dropped:
                omitted[section.table] = dropped
        for item in kept:
            lines.append(
                item.render(
                    with_topk=item.name not in stripped,
                    with_labels=True,
                    with_meta=False,
                )
            )
        lines.extend(section.others)
        blocks.append("\n".join(lines))
    text = "\n".join(blocks).strip()
    _ = budget_chars
    return SchemaProjection(
        text=text,
        omitted=omitted,
        enum_stripped=enum_stripped,
        relevant={key: sorted(names) for key, names in relevant.items()},
    )


def enum_pins_for(
    schema_text: str,
    *,
    queries: Sequence[str] = (),
    keep_fields: Mapping[str, Iterable[str]] | None = None,
    present_pages: Iterable[str] | None = None,
    limit: int = 3,
) -> list[str]:
    """Enum pages worth pinning: dict fields the turn actually touches
    (evidence / baseline columns / wording hits / recalled scene windows),
    best rank first. Structural relevance alone (every enum column) does not
    earn a pin."""
    keep = merge_field_sets(keep_fields)
    recalled = recalled_scenario_keys(present_pages)
    ranked: list[tuple[int, int, str]] = []
    order = 0
    for section in _parse_sections(schema_text):
        if not section.table:
            continue
        rel_cols = section.relation_cols()
        annotated = section_is_scene_annotated(section.fields)
        for item in section.fields:
            if not item.enum:
                continue
            if annotated:
                if not _keep_scene_field(
                    item,
                    keep=keep.get(section.table, set()),
                    relation_cols=rel_cols,
                    queries=queries,
                    recalled_scenarios=recalled,
                ):
                    continue
                rank = RANK_EVIDENCE
            else:
                rank = field_relevance_rank(
                    item,
                    keep=keep.get(section.table, set()),
                    relation_cols=rel_cols,
                    queries=queries,
                    recalled_scenarios=recalled,
                )
                if rank is None or rank >= RANK_STRUCTURAL:
                    continue
            key = enum_page_key(item.enum)
            if key and key not in {k for _, _, k in ranked}:
                ranked.append((rank, order, key))
                order += 1
    ranked.sort()
    return [key for _, _, key in ranked][: max(0, int(limit))]


# ── relation projection ─────────────────────────────────────────────────────


def format_relation_line(
    left_table: str,
    left_col: str,
    right_table: str,
    right_col: str,
    *,
    peer: str | None = None,
    tag: str = "",
    peer_missing: bool = False,
) -> str:
    peer_name = peer or right_table
    line = f"关联: {left_table}.{left_col} → {right_table}.{right_col} ({peer_name})"
    if tag:
        line = f"{line} [{tag}]"
    if peer_missing:
        return f"{line}{RELATION_PEER_MISSING}"
    return line


def filter_schema_relations(schema_text: str, *, peer_tables: Sequence[str]) -> str:
    """Working-set projection for ``关联:`` lines — the sole peer policy.

    Renderer emits every compact edge. This function decides what the prompt
    sees, given the *accumulated* table set (plane.tables / NLQ working set):

    - peer already in the set → keep the compact JOIN
    - peer missing, but the local endpoint is a still-visible FK-like column
      → keep and mark ``（对端未入选）`` so the model does not guess ``= id``
    - otherwise drop (identity-column edges to unloaded tables are noise)
    """
    peers = {str(name).strip() for name in peer_tables if str(name).strip()}
    lines = str(schema_text or "").splitlines()
    out: list[str] = []
    buf: list[str] = []
    table = ""

    def flush() -> None:
        if not buf:
            return
        out.extend(_project_table_relation_lines(buf, table=table, peers=peers))
        buf.clear()

    for raw in lines:
        match = _TABLE_HEAD_RE.match(raw.strip())
        if match:
            flush()
            table = str(match.group(1) or "").strip()
            buf.append(raw)
            continue
        buf.append(raw)
    flush()
    return "\n".join(out)


def _project_table_relation_lines(
    lines: Sequence[str], *, table: str, peers: set[str]
) -> list[str]:
    fields = {
        str(match.group(1))
        for raw in lines
        if (match := _FIELD_NAME_RE.match(raw.strip()))
    }
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith(OMITTED_FIELDS_PREFIX):
            fields.update(omitted_field_names(stripped))
    projected: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        parsed = _RELATION_PROMPT_RE.match(stripped)
        if parsed is None:
            projected.append(raw)
            continue
        left_table = parsed.group("left_table")
        left_col = parsed.group("left_col")
        right_table = parsed.group("right_table")
        right_col = parsed.group("right_col")
        peer_label = str(parsed.group("peer") or "").strip()
        tag = str(parsed.group("tag") or "").strip()
        if table == left_table:
            local_col = left_col
            foreign = {right_table, peer_label} - {table, ""}
        elif table == right_table:
            local_col = right_col
            foreign = {left_table, peer_label} - {table, ""}
        else:
            local_col = left_col
            foreign = {right_table, left_table, peer_label} - {table, ""}
        in_set = bool(foreign & peers)
        if in_set:
            projected.append(
                format_relation_line(
                    left_table,
                    left_col,
                    right_table,
                    right_col,
                    peer=peer_label or right_table,
                    tag=tag,
                )
            )
            continue
        if local_col in fields and _is_fk_like_column(local_col):
            projected.append(
                format_relation_line(
                    left_table,
                    left_col,
                    right_table,
                    right_col,
                    peer=peer_label or right_table,
                    tag=tag,
                    peer_missing=True,
                )
            )
    return projected


# ── renderer (full, corpus-only) ────────────────────────────────────────────


class WikiSchemaRenderer:
    """把 working set 的表**全量**渲染成 schema_text（wiki 权威 + db 直渲兜底）。"""

    def __init__(
        self,
        store: Any,
        db_catalog: dict[str, Any] | None = None,
        pages_root: Path | None = None,
        missing_tables: list[str] | None = None,
        live_tables: dict[str, Any] | None = None,
        peer_catalog: Sequence[str] | None = None,
    ) -> None:
        self._store = store
        self._db_catalog = db_catalog or {}
        self._pages_root = pages_root
        self._missing: list[str] = missing_tables if missing_tables is not None else []
        # 活元数据第二兜底源（chat 172）：{table_name: (desc, [(name, type, comment)])}。
        # 语料根的 db-catalog.yaml 只覆盖语料所属数据源；其它 ds（如 AIO）的表
        # 走 wiki 接缝时 catalog 不命中，只渲表头零字段 → planner 必然 unsupported。
        # core_table/core_field 就在手边（同步产物），零额外连库。
        self._live_tables = live_tables or {}
        # Full datasource table-name set for FK peer resolution (may exceed the
        # current working set). Empty → fall back to live_tables keys only.
        self._peer_catalog = tuple(
            str(name).strip() for name in (peer_catalog or ()) if str(name).strip()
        )

    @property
    def missing(self) -> list[str]:
        """本轮 render 中缺 wiki 页、走 db 直渲兜底的表(公开投影)。"""
        return list(self._missing)

    @classmethod
    def from_store(
        cls,
        store: Any,
        live_tables: dict[str, Any] | None = None,
        peer_catalog: Sequence[str] | None = None,
    ) -> WikiSchemaRenderer | None:
        """从 wiki store 构建；db catalog 从语料根旁的 db/ 目录装载。"""
        if store is None:
            return None
        db_catalog: dict[str, Any] = {}
        root = getattr(store, "_pages_root", None)
        if root is not None:
            catalog_path = Path(root).parent / "db" / "db-catalog.yaml"
            if catalog_path.exists():
                import yaml

                db_catalog = yaml.safe_load(catalog_path.read_text()) or {}
        return cls(
            store,
            db_catalog,
            root,
            [],
            live_tables=live_tables,
            peer_catalog=peer_catalog,
        )

    def render(self, tables: list[str]) -> str:
        """渲染全部字段与全部紧凑关联；压缩/投影见 ``project_schema`` /
        ``filter_schema_relations``。"""
        sections: list[str] = []
        for table in tables:
            page = _lookup_store_page(
                self._store, table, belong="tables", page_type="table"
            )
            block = _wiki_table_block(page.body) if page else None
            if block is not None:
                sections.append(
                    self._render_wiki_table(
                        table, block, page.body if page is not None else ""
                    )
                )
            else:
                if table not in self._missing:
                    self._missing.append(table)
                sections.append(self._render_db_table(table))
        if self._missing:
            SQLBotLogUtil.warning(
                "SCHEMA_PAGE_MISSING: %s —— wiki 页缺失的表本轮用 db 直渲（update 增量将补页）",
                self._missing,
            )
        return "\n".join(sections)

    # ── wiki 页渲染（权威） ──────────────────────────────────────────────

    def _enum_label_map(self, dict_key: str) -> dict[str, str]:
        """dict 指针 → 权威枚举页的 value→label 映射（页缺失/无块返回空）。

        与 enum_maps_for 同源的宽松语义（不查 published）：schema 呈现的
        是已进 working set 的表页自带的绑定，锚点块即证据。"""
        if not dict_key or not self._store:
            return {}
        page = _lookup_store_page(
            self._store, dict_key, belong="enums", page_type="enum"
        )
        if page is None:
            return {}
        for anchor in getattr(page, "ground_blocks", ()) or ():
            if anchor.kind != "enum":
                continue
            values = anchor.data.get("values") or {}
            return {
                str(value): str((meta or {}).get("label") or "")
                for value, meta in values.items()
                if isinstance(meta, dict) or meta is None
            }
        return {}

    def _wiki_relations(self, page_text: str) -> list[str]:
        """表页「## 关联表」节 → 紧凑关联行；方括号标观察来源，不标建议。"""
        relations: list[str] = []
        heading_at = page_text.find(_RELATION_HEADING)
        if heading_at < 0:
            return relations
        section = page_text[heading_at + len(_RELATION_HEADING) :]
        next_heading = section.find("\n## ", 1)
        if next_heading >= 0:
            section = section[:next_heading]
        for match in _RELATION_ROW_RE.finditer(section):
            left_table, _, left_col = match.group("left_ref").partition(".")
            right_table, _, right_col = match.group("right_ref").partition(".")
            note = str(match.group("note") or "")
            tag = relation_source_tag(note)
            relations.append(
                format_relation_line(
                    left_table,
                    left_col,
                    right_table,
                    right_col,
                    peer=match.group("right").strip(),
                    tag=tag,
                )
            )
        return relations

    def _render_wiki_table(
        self, table: str, block: dict[str, Any], page_text: str = ""
    ) -> str:
        from apps.knowledge.wiki.contract import compact_block

        block = compact_block(block)
        desc = str(block.get("desc") or table)
        lines = [f"## {desc} ({table})"]
        for f in block.get("fields") or []:
            if not isinstance(f, dict):
                continue
            name = str(f.get("name") or "")
            comment = str(f.get("desc") or "").strip()
            ftype = str(f.get("phys") or f.get("type") or "string")
            topk = str(f.get("topk") or "").strip()
            dict_key = str(f.get("dict") or "").strip()
            values = [item for item in topk.split("|") if item]
            raw_labels = f.get("labels")
            owned = False
            label_map: dict[str, str] = {}
            if isinstance(raw_labels, dict):
                label_map = {
                    str(k): str(v) for k, v in raw_labels.items() if str(v).strip()
                }
                owned = bool(label_map)
            elif isinstance(raw_labels, str) and raw_labels.strip():
                label_tail = raw_labels.strip()
                owned = True
            else:
                label_tail = ""
            if owned and isinstance(raw_labels, dict):
                label_tail = format_enum_labels(values or list(label_map), label_map)
            elif not owned:
                label_map = self._enum_label_map(dict_key) if dict_key else {}
                label_tail = format_enum_labels(values, label_map) if label_map else ""
            scenes_raw = f.get("scenes") or []
            if isinstance(scenes_raw, str):
                scenes = tuple(
                    part.strip()
                    for part in scenes_raw.replace(",", "|").split("|")
                    if part.strip()
                )
            elif isinstance(scenes_raw, list | tuple):
                scenes = tuple(
                    str(part).strip() for part in scenes_raw if str(part).strip()
                )
            else:
                scenes = ()
            lines.append(
                SchemaField(
                    name=name,
                    type=ftype,
                    comment=comment or name,
                    topk=topk,
                    labels=label_tail,
                    enum=dict_key.rsplit("/", 1)[-1] if dict_key else "",
                    owned_labels=owned,
                    group=str(f.get("group") or "").strip(),
                    scenes=scenes,
                ).render(with_meta=True)
            )
        lines.extend(self._wiki_relations(page_text))
        return "\n".join(lines)

    # ── db 直渲（页缺失兜底——非常态路径） ────────────────────────────────

    def _db_ref_relations(self, table: str) -> list[str]:
        """db-catalog 索引推导关系（第二通道）：ref_* / ``*_id`` → 候选右表。

        右表必须在 db catalog 中真实存在才产出——宁缺勿错。对端若不在当前
        工作集，仍输出边并标 ``（对端未入选）``，由 ``filter_schema_relations``
        决定最终是否保留。"""
        meta = (self._db_catalog.get("tables") or {}).get(table) or {}
        known_tables = set((self._db_catalog.get("tables") or {}).keys())
        working = set(self._live_tables.keys()) | {table}
        relations: list[str] = []
        seen: set[str] = set()
        for name in meta.get("columns") or {}:
            peer = resolve_fk_peer_table(str(name), known_tables)
            if not peer or peer == table or peer in seen:
                continue
            seen.add(peer)
            relations.append(
                format_relation_line(
                    table,
                    str(name),
                    peer,
                    "id",
                    tag="db-index",
                    peer_missing=peer not in working,
                )
            )
        return relations

    def _render_db_table(self, table: str) -> str:
        meta = (self._db_catalog.get("tables") or {}).get(table)
        if meta is None and table in self._live_tables:
            return self._render_live_table(table)
        meta = meta or {}
        columns = meta.get("columns") or {}
        desc = str(meta.get("comment") or table)
        lines = [f"## {desc} ({table}) [db]"]
        for name, cinfo in columns.items():
            lines.append(
                SchemaField(
                    name=str(name),
                    type=str(cinfo.get("type") or "string"),
                    comment=str(cinfo.get("comment") or name),
                ).render()
            )
        lines.extend(self._db_ref_relations(table))
        return "\n".join(lines)

    def _render_live_table(self, table: str) -> str:
        """活元数据渲染（core_table/core_field 同步产物，非 wiki 语料）。"""
        entry = self._live_tables.get(table) or {}
        desc = str(entry.get("comment") or table)
        lines = [f"## {desc} ({table}) [db]"]
        for name, ftype, comment in entry.get("fields") or []:
            lines.append(
                SchemaField(
                    name=str(name), type=str(ftype), comment=str(comment or name)
                ).render()
            )
        lines.extend(self._db_ref_relations(table))
        lines.extend(self._live_fk_relations(table))
        return "\n".join(lines)

    def _live_fk_relations(self, table: str) -> list[str]:
        """活元数据命名关系：``<right>_id`` / ``ref_*`` → 右表.id。

        右表解析走 ``resolve_fk_peer_table``，对照面是「本轮 live 投影 ∪ 调用方
        注入的 catalog 名」（``_peer_catalog``）。对端未入选时仍保留边并标记，
        避免模型把 FK 列当成普通属性。"""
        entry = self._live_tables.get(table) or {}
        known = set(self._live_tables.keys()) | set(
            getattr(self, "_peer_catalog", ()) or ()
        )
        working = set(self._live_tables.keys())
        relations: list[str] = []
        seen: set[str] = set()
        for name, _ftype, _comment in entry.get("fields") or []:
            peer = resolve_fk_peer_table(str(name), known)
            if not peer or peer == table or peer in seen:
                continue
            seen.add(peer)
            relations.append(
                format_relation_line(
                    table,
                    str(name),
                    peer,
                    "id",
                    tag="db-naming",
                    peer_missing=peer not in working,
                )
            )
        return relations
