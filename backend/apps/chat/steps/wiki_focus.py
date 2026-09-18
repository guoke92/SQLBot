"""search_wiki ``focus``: comprehensive recall vs local fact lookup.

``all`` (default) runs Wiki/RRF discovery. ``field`` / ``dict`` / ``term`` /
``relation`` verify facts against the current knowledge plane (and the bound
Wiki store when needed) without ingesting prose pages.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.chat.steps.wiki_schema import (
    _RELATION_PROMPT_RE,
    _RELATION_ROW_RE,
    schema_fields_by_table,
)

FOCUS_ALL = "all"
FOCUS_FIELD = "field"
FOCUS_DICT = "dict"
FOCUS_TERM = "term"
FOCUS_RELATION = "relation"
FOCUS_VALUES = (FOCUS_ALL, FOCUS_FIELD, FOCUS_DICT, FOCUS_TERM, FOCUS_RELATION)
LOCAL_FOCUS = frozenset({FOCUS_FIELD, FOCUS_DICT, FOCUS_TERM, FOCUS_RELATION})

_BINDING_BELONG = frozenset({"dicts", "calibers", "concepts", "tables", "metrics"})
_PERIPHERAL_BELONG = frozenset({"rules", "processes", "patterns", "queries"})
_TABLE_COL_RE = re.compile(
    r"\b([A-Za-z_][\w]*)\.([A-Za-z_]\w*)\b",
)
_LIST_SPLIT_RE = re.compile(r"[\t\n,，、;/|]+")
_CJK_PHRASE_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")
_COVERAGE_LIST_MIN = 6
_COVERAGE_HIT_MIN = 4
RELATIVE_PROMPT_RATIO = 0.4
LOOKUP_FOUND_LIMIT = 12
_PAGE_KEY_RE = re.compile(
    r"(?:tables|enums|dicts|calibers|concepts|metrics|rules|processes|patterns|queries)"
    r"/[A-Za-z0-9_.:\-]+"
)
_HYPHEN_SLUG_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+){2,}")


def normalize_focus(raw: str | None) -> str:
    text = str(raw or "").strip().casefold()
    if not text or text in {"none", "null", "default", "coarse", "discovery"}:
        return FOCUS_ALL
    if text in {"fine", "lookup", "ground"}:
        return FOCUS_FIELD
    if text in {"enum", "dictionary"}:
        return FOCUS_DICT
    if text in FOCUS_VALUES:
        return text
    return FOCUS_ALL


def infer_focus(query: str, plane: AgentKnowledgePlane, *, declared: str) -> str:
    """Upgrade ``all`` to a local focus when the query is clearly a fact check."""
    focus = normalize_focus(declared)
    if focus != FOCUS_ALL:
        return focus
    if not plane.schema_ready:
        return FOCUS_ALL
    clean = str(query or "").strip()
    if not clean:
        return FOCUS_ALL
    if query_names_wiki_page(clean):
        return FOCUS_ALL
    dotted = _TABLE_COL_RE.search(clean)
    if dotted and dotted.group(1) in plane.tables:
        return FOCUS_FIELD
    phrases = [item.strip() for item in _LIST_SPLIT_RE.split(clean) if item.strip()]
    if " " in clean and len(phrases) < 2:
        phrases = [item for item in clean.split() if item.strip()]
    if len(phrases) >= 2:
        hits = [hit for phrase in phrases for hit in _exact_column_hits(plane, phrase)]
        unique = {(item["table"], item["field"]) for item in hits}
        if len(unique) >= 2:
            return FOCUS_FIELD
        return FOCUS_ALL
    if len(clean) > 24:
        return FOCUS_ALL
    hits = _exact_column_hits(plane, clean)
    if hits:
        return FOCUS_FIELD
    return FOCUS_ALL


def _exact_column_hits(plane: AgentKnowledgePlane, query: str) -> list[dict[str, str]]:
    needle = str(query or "").strip()
    if not needle:
        return []
    folded = needle.casefold()
    found: list[dict[str, str]] = []
    for table, body in plane.schema_by_table.items():
        if str(table).startswith("_"):
            continue
        for item in schema_fields_by_table(body).get(table) or []:
            if (
                item.name.casefold() == folded
                or str(item.comment or "").strip() == needle
                or f"{table}.{item.name}".casefold() == folded
            ):
                found.append(
                    {
                        "table": table,
                        "field": item.name,
                        "comment": item.comment,
                    }
                )
    return found


def page_belong(key: str) -> str:
    text = str(key or "").strip()
    if "/" in text:
        return text.split("/", 1)[0]
    return ""


def is_binding_page(key: str, working_tables: Sequence[str]) -> bool:
    """True when a page can count as retrieval progress for ``focus=all``."""
    belong = page_belong(key)
    if belong in _PERIPHERAL_BELONG:
        return False
    tables = [str(name) for name in working_tables if str(name)]
    slug = str(key or "").rsplit("/", 1)[-1]
    if belong == "tables":
        return slug in tables or key in tables
    if belong in _BINDING_BELONG:
        return True
    if slug in tables or key in tables:
        return True
    return False


def binding_pages(keys: Sequence[str], working_tables: Sequence[str]) -> list[str]:
    return [str(key) for key in keys if is_binding_page(str(key), working_tables)]


def is_peripheral_page(key: str) -> bool:
    return page_belong(key) in _PERIPHERAL_BELONG


def page_named_in_query(key: str, query: str) -> bool:
    slug = str(key or "").rsplit("/", 1)[-1]
    text = str(query or "").casefold()
    if len(slug) < 4 or not text:
        return False
    return slug.casefold() in text


def admit_pages(
    keys: Sequence[str],
    *,
    working_tables: Sequence[str],
    query: str,
) -> list[str]:
    """Pages that may enter the prompt. Peripheral prose stays out unless named."""
    admitted: list[str] = []
    for raw in keys:
        key = str(raw or "").strip()
        if not key:
            continue
        if is_peripheral_page(key) and not page_named_in_query(key, query):
            continue
        if page_belong(key) == "tables" and not is_binding_page(key, working_tables):
            if not page_named_in_query(key, query):
                continue
        if is_binding_page(key, working_tables) or page_named_in_query(key, query):
            admitted.append(key)
            continue
        if is_peripheral_page(key):
            continue
        admitted.append(key)
    return admitted


def named_in_query(name: str, query: str) -> bool:
    token = str(name or "").strip()
    text = str(query or "").casefold()
    if len(token) < 4 or not text:
        return False
    return token.casefold() in text


def admit_tables(
    incoming: Sequence[str],
    *,
    plane: AgentKnowledgePlane,
    evidence: Mapping[str, Any],
    scores: Mapping[str, Any],
    query: str,
    schema_text: str = "",
) -> tuple[list[str], list[str]]:
    """Keep the high-confidence cluster; drop unevidenced / coverage-cliff tails.

    Does not elect a primary table. Near-tied JOIN partners stay together.
    After the plane already has tables, a new name still needs evidence (or
    an explicit mention) and must not cliff against established coverage.
    """
    from apps.chat.agent_knowledge import split_schema_text
    from apps.knowledge.recall_kernel.tables import TableCandidate, cut_relative_tail

    names = [str(item).strip() for item in incoming if str(item).strip()]
    if not names:
        return [], []
    bodies = split_schema_text(schema_text, tables=names)
    queries = [item for item in (_coverage_query_text(plane), query) if item]
    named = {name for name in names if named_in_query(name, query)}
    ranked: list[TableCandidate] = []
    coverage: dict[str, int] = {}
    for name in names:
        raw = evidence.get(name) or []
        if isinstance(raw, list | tuple):
            ev = tuple(str(item) for item in raw if str(item).strip())
        elif raw:
            ev = (str(raw),)
        else:
            ev = ()
        body = bodies.get(name) or plane.schema_by_table.get(name) or ""
        hits = _table_body_coverage(body, name, queries)
        coverage[name] = hits
        ranked.append(
            TableCandidate(
                name=name,
                evidence=ev or (("named",) if name in named else ()),
                score=float(scores.get(name) or 0.0) + float(hits),
                source="anchor",
            )
        )
    ranked.sort(key=lambda item: (-len(item.evidence), -item.score, item.name))
    cluster, _cut = cut_relative_tail(ranked, cap=max(8, len(ranked) or 1))
    cluster_names = {item.name for item in cluster}
    plane_best = max(
        (_plane_table_score(plane, name) for name in plane.tables),
        default=0,
    )
    require_evidence = bool(plane.tables)
    admitted: list[str] = []
    rejected: list[str] = []
    for name in names:
        has_ev = bool(evidence.get(name))
        if name in plane.tables or name in named:
            admitted.append(name)
            continue
        if require_evidence and not has_ev:
            rejected.append(name)
            continue
        if name not in cluster_names:
            rejected.append(name)
            continue
        if (
            require_evidence
            and plane_best >= _COVERAGE_HIT_MIN
            and coverage.get(name, 0) + 1e-9 < plane_best * RELATIVE_PROMPT_RATIO
        ):
            rejected.append(name)
            continue
        admitted.append(name)
    return list(dict.fromkeys(admitted)), list(dict.fromkeys(rejected))


def _table_body_coverage(body: str, table: str, queries: Sequence[str]) -> int:
    phrases: list[str] = []
    for item in queries:
        phrases.extend(extract_column_phrases(str(item)))
    if not phrases or not body:
        return 0
    fields = schema_fields_by_table(body).get(table) or []
    hits = 0
    for field in fields:
        blob = f"{field.name} {field.comment}"
        if any(_phrase_hits(phrase, blob, field.name) for phrase in phrases):
            hits += 1
    return hits


def lookup_payload(
    plane: AgentKnowledgePlane,
    query: str,
    *,
    focus: str,
    llm_service: Any = None,
) -> dict[str, Any]:
    """Local fact check. Never attaches knowledge_text / schema_text prose."""
    kind = normalize_focus(focus)
    clean = str(query or "").strip()
    if kind == FOCUS_FIELD:
        facts = _field_facts(plane, clean)
    elif kind == FOCUS_DICT:
        facts = _enum_facts(plane, clean, llm_service)
    elif kind == FOCUS_TERM:
        facts = _term_facts(plane, clean, llm_service)
    elif kind == FOCUS_RELATION:
        facts = _relation_facts(plane, clean)
    else:
        facts = {"found": [], "missing": [clean] if clean else []}
    found = list(facts.get("found") or [])[:LOOKUP_FOUND_LIMIT]
    missing = list(facts.get("missing") or [])
    evidence: dict[str, list[str]] = {}
    for item in found:
        table = str(item.get("table") or "")
        field = str(item.get("field") or "")
        if table and field:
            bucket = evidence.setdefault(table, [])
            if field not in bucket:
                bucket.append(field)
    return {
        "query": clean,
        "knowledge_text": "",
        "schema_text": "",
        "tables": [],
        "page_keys": [],
        "backend": "lookup",
        "hit_count": len(found),
        "schema_ready": plane.schema_ready,
        "evidence_fields": evidence,
        "focus": kind,
        "focus_facts": {
            "kind": kind,
            "found": found,
            "missing": missing,
            "query": clean,
        },
    }


def named_wiki_keys(query: str) -> list[str]:
    """Page keys / hyphenated slugs the tool query is opening by identity."""
    text = str(query or "")
    if not text:
        return []
    keys = _PAGE_KEY_RE.findall(text)
    slugs = _HYPHEN_SLUG_RE.findall(text)
    return list(dict.fromkeys([*keys, *slugs]))


def query_names_wiki_page(query: str) -> bool:
    return bool(named_wiki_keys(query))


def catalog_rank_tables(query: str, store: Any, *, cap: int = 4) -> list[Any]:
    """Score catalog tables by column coverage + title overlap on the Human question.

    This is the table selector for ``focus=all``. Relative-cut the cluster; do
    not elect a primary table.
    """
    from apps.knowledge.recall_kernel.tables import TableCandidate, cut_relative_tail
    from apps.knowledge.wiki.recall import tokenize

    text = str(query or "").strip()
    if not text or store is None:
        return []
    phrases = extract_column_phrases(text)
    index = getattr(store, "table_index", None) or {}
    get_page = getattr(store, "get_page", None)
    q_tokens = tokenize(text)
    ranked: list[TableCandidate] = []
    for page_key, store_key in index.items():
        page = None
        if callable(get_page):
            page = get_page(store_key) or get_page(page_key)
        name = _page_table_name(page, page_key)
        if not name:
            continue
        field_hits = _table_coverage_hits(page, phrases)
        title = str(getattr(page, "title", "") or "")
        aliases = tuple(getattr(page, "aliases", ()) or ())
        title_hits = len(q_tokens & tokenize(f"{title} {' '.join(aliases)} {name}"))
        named = named_in_query(name, text) or named_in_query(
            str(page_key).rsplit("/", 1)[-1], text
        )
        if field_hits < 1 and title_hits < 1 and not named:
            continue
        evidence: list[str] = []
        if field_hits:
            evidence.append(f"coverage:{field_hits}")
        if title_hits:
            evidence.append("title")
        if named:
            evidence.append("named")
        ranked.append(
            TableCandidate(
                name=name,
                evidence=tuple(evidence),
                score=float(field_hits) * 10.0
                + float(title_hits)
                + (5.0 if named else 0.0),
                source="catalog",
            )
        )
    ranked.sort(key=lambda item: (-len(item.evidence), -item.score, item.name))
    kept, _cut = cut_relative_tail(ranked, cap=max(1, int(cap)))
    return kept


def coverage_pin_tables(query: str, store: Any, *, limit: int = 2) -> tuple[str, ...]:
    """Long export-style field lists pin the catalog table that covers them."""
    phrases = extract_column_phrases(query)
    if len(phrases) < _COVERAGE_LIST_MIN or store is None:
        return ()
    ranked = catalog_rank_tables(query, store, cap=limit)
    return tuple(item.name for item in ranked)


def extract_column_phrases(query: str) -> list[str]:
    text = str(query or "").strip()
    if not text:
        return []
    parts = [item.strip() for item in _LIST_SPLIT_RE.split(text) if item.strip()]
    if len(parts) >= _COVERAGE_LIST_MIN:
        return parts
    extra = _CJK_PHRASE_RE.findall(text)
    extra.extend(_IDENT_RE.findall(text))
    return list(dict.fromkeys([*parts, *extra]))


def relation_edges(schema_text: str) -> set[tuple[str, str]]:
    """Undirected table pairs observed in projected relation rows."""
    edges: set[tuple[str, str]] = set()
    for raw in str(schema_text or "").splitlines():
        line = raw.strip()
        wiki = _RELATION_ROW_RE.match(line)
        if wiki:
            left = str(wiki.group("left_ref") or "").split(".", 1)[0]
            right = str(wiki.group("right") or wiki.group("right_ref") or "")
            right = right.split(".", 1)[0]
            _add_edge(edges, left, right)
            continue
        prompt = _RELATION_PROMPT_RE.match(line)
        if prompt:
            _add_edge(
                edges,
                str(prompt.group("left_table") or ""),
                str(prompt.group("right_table") or ""),
            )
    return edges


def expanded_tables(plane: AgentKnowledgePlane) -> list[str]:
    """Tables that deserve a full catalog projection this round.

    Low-coverage passengers stay listed in knowledge_index but do not dump DDL.
    """
    visible = [
        name
        for name in plane.tables
        if name and not plane.is_excluded(name) and plane.schema_by_table.get(name)
    ]
    if len(visible) <= 1:
        return visible
    scored = [(_plane_table_score(plane, name), name) for name in visible]
    best = max(hits for hits, _name in scored)
    if best < 1:
        return visible
    floor = max(1.0, best * RELATIVE_PROMPT_RATIO)
    kept = [name for hits, name in scored if hits + 1e-9 >= floor]
    if not kept:
        kept = [max(scored, key=lambda item: (item[0], item[1]))[1]]
    schema = "\n".join(plane.schema_by_table[name] for name in visible)
    kept_set = set(kept)
    visible_set = set(visible)
    for left, right in relation_edges(schema):
        if left in kept_set and right in visible_set:
            kept_set.add(right)
        if right in kept_set and left in visible_set:
            kept_set.add(left)
    return [name for name in visible if name in kept_set]


def prune_isolated_tables(plane: AgentKnowledgePlane) -> dict[str, list[str]]:
    """No longer evicts tables. Prompt folding is owned by ``expanded_tables``.

    Kept so existing callers do not crash; always a no-op.
    """
    del plane
    return {"tables": [], "pages": []}


def _add_edge(edges: set[tuple[str, str]], left: str, right: str) -> None:
    a, b = str(left or "").strip(), str(right or "").strip()
    if not a or not b or a == b:
        return
    edges.add((a, b) if a < b else (b, a))


def _bfs(start: str, adjacency: Mapping[str, set[str]]) -> set[str]:
    seen = {start}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for peer in adjacency.get(node) or ():
            if peer not in seen:
                seen.add(peer)
                queue.append(peer)
    return seen


def _coverage_query_text(plane: AgentKnowledgePlane) -> str:
    if str(getattr(plane, "question", "") or "").strip():
        return str(plane.question).strip()
    if plane.queries:
        return str(plane.queries[0] or "").strip()
    return ""


def page_binds_to_tables(key: str, working_tables: Sequence[str], store: Any) -> bool:
    """True when a recalled page is binding knowledge of the selected tables."""
    tables = {str(name) for name in working_tables if str(name)}
    if not tables:
        return False
    if is_peripheral_page(key):
        return False
    belong = page_belong(key)
    slug = str(key or "").rsplit("/", 1)[-1]
    if belong == "tables":
        return slug in tables or key in tables
    if "::" in slug and slug.split("::", 1)[0] in tables:
        return True
    if store is not None:
        try:
            from apps.knowledge.wiki.anchors import anchor_tables

            anchored = {str(name) for name in anchor_tables(store, [key]) if str(name)}
        except Exception:
            anchored = set()
        if anchored:
            return bool(anchored & tables)
    return belong in _BINDING_BELONG


def _plane_table_score(plane: AgentKnowledgePlane, table: str) -> int:
    phrases = extract_column_phrases(_coverage_query_text(plane))
    body = plane.schema_by_table.get(table) or ""
    fields = schema_fields_by_table(body).get(table) or []
    if not phrases:
        return len(plane.keep_fields.get(table) or [])
    hits = 0
    for item in fields:
        blob = f"{item.name} {item.comment}"
        if any(_phrase_hits(phrase, blob, item.name) for phrase in phrases):
            hits += 1
    hits += len(plane.keep_fields.get(table) or [])
    return hits


def _match_fields(plane: AgentKnowledgePlane, query: str) -> list[dict[str, str]]:
    dotted = {(table, col) for table, col in _TABLE_COL_RE.findall(query)}
    phrases = [item.strip() for item in _LIST_SPLIT_RE.split(query) if item.strip()]
    if " " in str(query or "") and len(phrases) < 2:
        phrases = [item for item in str(query).split() if item.strip()]
    needles = (
        phrases if len(phrases) >= 2 and not dotted else [str(query or "").strip()]
    )
    found: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for table, body in plane.schema_by_table.items():
        if str(table).startswith("_"):
            continue
        for item in schema_fields_by_table(body).get(table) or []:
            if dotted:
                if (table, item.name) not in dotted:
                    continue
            elif not any(
                _phrase_hits(needle, f"{item.name} {item.comment}", item.name)
                for needle in needles
                if needle
            ):
                continue
            pair = (table, item.name)
            if pair in seen:
                continue
            seen.add(pair)
            found.append(
                {
                    "table": table,
                    "field": item.name,
                    "comment": item.comment,
                    "enum": item.enum,
                    "labels": item.labels,
                    "topk": item.topk,
                }
            )
    return found


def _field_facts(plane: AgentKnowledgePlane, query: str) -> dict[str, Any]:
    found = _match_fields(plane, query)
    missing: list[str] = []
    if not found:
        missing = [query] if query else []
    return {"found": found, "missing": missing}


def _parse_labels(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in str(raw or "").split("|"):
        key, sep, value = part.partition(":")
        if sep and key.strip():
            out[key.strip()] = value.strip()
    return out


def _enum_facts(
    plane: AgentKnowledgePlane, query: str, llm_service: Any
) -> dict[str, Any]:
    fields = _match_fields(plane, query) or [
        item
        for table, body in plane.schema_by_table.items()
        for item in (
            {
                "table": table,
                "field": field.name,
                "comment": field.comment,
                "enum": field.enum,
                "labels": field.labels,
                "topk": field.topk,
            }
            for field in schema_fields_by_table(body).get(table) or []
            if field.enum or field.labels
        )
        if _phrase_hits(query, f"{item['field']} {item['comment']}", item["field"])
    ]
    found: list[dict[str, Any]] = []
    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    for item in fields:
        labels = _parse_labels(str(item.get("labels") or ""))
        if not labels and item.get("enum") and ds_id is not None:
            try:
                from apps.chat.steps.wiki_recall import enum_maps_for

                ref = f"{item['table']}.{item['field']}"
                mapped = enum_maps_for([ref], ds_id=int(ds_id))
                labels = dict(mapped.get(ref) or {})
            except Exception:
                labels = {}
        if not labels and not item.get("enum"):
            continue
        found.append({**item, "enums": labels})
    return {
        "found": found,
        "missing": [] if found else ([query] if query else []),
    }


def _term_facts(
    plane: AgentKnowledgePlane, query: str, llm_service: Any
) -> dict[str, Any]:
    needle = str(query or "").strip()
    found: list[dict[str, str]] = []
    for key, text in plane.wiki_passages.items():
        hay = f"{key}\n{text[:400]}"
        if needle and (
            needle.casefold() in hay.casefold()
            or needle in key
            or key.rsplit("/", 1)[-1] in needle
        ):
            found.append({"page_key": key, "title": key.rsplit("/", 1)[-1]})
    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    if not found and ds_id is not None:
        try:
            from apps.chat.steps.wiki_recall import _store

            store = _store(int(ds_id))
            alias_index = getattr(store, "alias_index", None) or {}
            hit = alias_index.get(needle) or alias_index.get(needle.casefold())
            if not hit:
                for alias, key in alias_index.items():
                    if needle.casefold() in str(alias).casefold():
                        hit = key
                        break
            if hit:
                found.append(
                    {
                        "page_key": str(hit),
                        "title": str(hit).rsplit("/", 1)[-1],
                    }
                )
        except Exception:
            pass
    return {
        "found": found,
        "missing": [] if found else ([needle] if needle else []),
    }


def _relation_facts(plane: AgentKnowledgePlane, query: str) -> dict[str, Any]:
    schema, _visible = plane._full_schema_text()
    edges = relation_edges(schema)
    mentioned = [name for name in dict.fromkeys(_IDENT_RE.findall(query or "")) if name]
    found: list[dict[str, str]] = []
    if len(mentioned) >= 2:
        named = set(mentioned)
        for left, right in sorted(edges):
            if left in named and right in named:
                found.append({"left": left, "right": right})
    elif len(mentioned) == 1:
        target = mentioned[0]
        for left, right in sorted(edges):
            if left == target or right == target:
                found.append({"left": left, "right": right})
    else:
        working = set(plane.tables)
        for left, right in sorted(edges):
            if left in working and right in working:
                found.append({"left": left, "right": right})
    return {
        "found": found,
        "missing": [] if found else ([query] if query else []),
    }


def _phrase_hits(phrase: str, blob: str, field_name: str) -> bool:
    text = str(phrase or "").strip()
    if not text:
        return False
    hay = str(blob or "")
    if text.casefold() in hay.casefold() or text.casefold() == field_name.casefold():
        return True
    if field_name.casefold() in text.casefold() and len(field_name) >= 3:
        return True
    from apps.chat.steps.wiki_schema import _query_hits_field

    return _query_hits_field(field_name, hay, [text])


def _page_table_name(page: Any, fallback: str) -> str:
    if page is not None:
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") == "table":
                data = getattr(block, "data", {}) or {}
                name = str(data.get("table") or "").strip()
                if name:
                    return name
        key = str(getattr(page, "page_key", "") or "")
        if key:
            return key.rsplit("/", 1)[-1]
    return str(fallback or "").rsplit("/", 1)[-1]


def _table_coverage_hits(page: Any, phrases: Sequence[str]) -> int:
    blobs: list[str] = []
    if page is not None:
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") != "table":
                continue
            for entry in (getattr(block, "data", {}) or {}).get("fields") or []:
                if isinstance(entry, Mapping):
                    blobs.append(
                        f"{entry.get('name') or ''} {entry.get('comment') or ''}"
                    )
                else:
                    blobs.append(str(entry))
        blobs.append(str(getattr(page, "title", "") or ""))
        blobs.append(str(getattr(page, "body", "") or "")[:4000])
    if not blobs:
        return 0
    joined = "\n".join(blobs)
    hits = 0
    hay = joined.casefold()
    for phrase in phrases:
        text = str(phrase or "").strip()
        if text and text.casefold() in hay:
            hits += 1
    return hits
