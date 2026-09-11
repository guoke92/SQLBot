"""Single table-selection implementation for Wiki anchors and schema_vector."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from apps.knowledge.recall_kernel.types import RecallBudget, TableCandidate
from apps.knowledge.wiki.anchors import anchor_table_attribution

_MIN_TABLE_MENTION = 3
PINNED_EVIDENCE = "pinned:baseline"


def resolve_wiki_tables(
    store: Any,
    *,
    page_keys: list[str],
    extra_keys: list[str] | None = None,
    table_pages: list[str] | None = None,
    scores: dict[str, float] | None = None,
    budget: RecallBudget | None = None,
    query: str = "",
    pinned_tables: Sequence[str] | None = None,
) -> tuple[list[TableCandidate], list[str]]:
    """Wiki tables from semantic/conflict anchors; table pages only if evidenced.

    Rank by evidence count, then page score. Budget ``max_tables`` cuts the tail.
    Gated table pages may enrich an already-attributed table, or become a
    candidate when the query itself names that table. They do not flood the
    resolver on their own.
    ``pinned_tables`` (continue/revise turns: tables of the baseline SQL) are
    always kept, ranked first, and do not consume ``max_tables``.
    Returns ``(kept, budget_cut_names)``.
    """
    cap = (budget or RecallBudget()).max_tables
    page_scores = scores or {}
    seeds = list(dict.fromkeys([*(page_keys or []), *(extra_keys or [])]))
    attribution = anchor_table_attribution(store, seeds) if store is not None else {}
    ranked: dict[str, TableCandidate] = {}
    pinned = [str(name).strip() for name in (pinned_tables or ()) if str(name).strip()]
    for name in pinned:
        ranked[name] = TableCandidate(
            name=name, evidence=(PINNED_EVIDENCE,), score=0.0, source="pinned"
        )
    for name, sources in attribution.items():
        evidence = tuple(
            dict.fromkeys(
                str(item.get("page_key") or "")
                for item in sources
                if item.get("page_key")
            )
        )
        score = max((float(page_scores.get(key, 0.0)) for key in evidence), default=0.0)
        prior = ranked.get(name)
        if prior is not None and prior.source == "pinned":
            ranked[name] = TableCandidate(
                name=name,
                evidence=tuple(dict.fromkeys([*prior.evidence, *evidence])),
                score=score + float(len(evidence)),
                source="pinned",
            )
            continue
        ranked[name] = TableCandidate(
            name=name,
            evidence=evidence,
            score=score + float(len(evidence)),
            source="anchor",
        )
    for raw in table_pages or []:
        name = _physical_table_name(store, raw)
        if not name:
            continue
        evidence = (raw,) if raw else ()
        prior = ranked.get(name)
        if prior is not None:
            merged = tuple(dict.fromkeys([*prior.evidence, *evidence]))
            ranked[name] = TableCandidate(
                name=name,
                evidence=merged,
                score=max(
                    prior.score, float(page_scores.get(raw, 0.0)) + float(len(merged))
                ),
                source=prior.source,
            )
            continue
        if not _table_mentioned(store, raw, name, query):
            continue
        ranked[name] = TableCandidate(
            name=name,
            evidence=evidence,
            score=float(page_scores.get(raw, 0.0)) + 1.0,
            source="table_page",
        )
    pinned_items = [ranked[name] for name in pinned if name in ranked]
    ordered = sorted(
        (item for item in ranked.values() if item.source != "pinned"),
        key=lambda item: (-len(item.evidence), -item.score, item.name),
    )
    kept = ordered[: max(1, cap)] if ordered else []
    cut = [item.name for item in ordered[len(kept) :]]
    return [*pinned_items, *kept], cut


def resolve_schema_vector_tables(
    scored: list[dict[str, Any]],
    *,
    table_limit: int,
    pinned_tables: Sequence[str] | None = None,
) -> list[TableCandidate]:
    """schema_vector docs → TableCandidate. Same ranking as the old _pick_tables.

    ``pinned_tables`` (continue/revise baseline) are always kept first and do
    not consume ``table_limit``.
    """
    ranked: dict[str, float] = {}
    for doc in scored:
        kind = str(doc.get("kind") or "")
        score = float(doc.get("score") or 0.0)
        names: list[str] = []
        if kind == "relation":
            names.extend(
                [
                    str(doc.get("table_name") or "").strip(),
                    str(doc.get("peer_table") or "").strip(),
                ]
            )
        else:
            names.append(str(doc.get("table_name") or "").strip())
        for name in names:
            if not name:
                continue
            ranked[name] = max(ranked.get(name, 0.0), score)
    pinned = [str(name).strip() for name in (pinned_tables or ()) if str(name).strip()]
    pinned_items = [
        TableCandidate(
            name=name,
            evidence=(PINNED_EVIDENCE,),
            score=ranked.get(name, 0.0),
            source="pinned",
        )
        for name in pinned
    ]
    ordered = sorted(
        (
            (name, score)
            for name, score in ranked.items()
            if name not in {item.name for item in pinned_items}
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    limit = max(1, int(table_limit))
    seeded = [
        TableCandidate(name=name, evidence=("schema_vector",), score=score, source="schema_vector")
        for name, score in ordered[:limit]
        if name
    ]
    return [*pinned_items, *seeded]


def expand_schema_working_set(
    seeds: Sequence[TableCandidate],
    *,
    edges: Sequence[tuple[str, str]],
    scores: Mapping[str, float] | None = None,
    total_limit: int,
) -> list[TableCandidate]:
    """1-hop structural expansion over catalog edges.

    ``edges`` are undirected ``(left, right)`` pairs from confirmed joins and
    naming-convention FKs. Seeds are never dropped. Missing peers are admitted
    by descending cosine score (then name) until ``total_limit``.
    """
    if not seeds:
        return []
    score_of = dict(scores or {})
    for item in seeds:
        score_of[item.name] = max(score_of.get(item.name, 0.0), float(item.score))
    selected = list(seeds)
    selected_names = {item.name for item in selected}
    peers: list[tuple[float, str]] = []
    seen_peer: set[str] = set()
    for left, right in edges:
        a, b = str(left or "").strip(), str(right or "").strip()
        if not a or not b or a == b:
            continue
        if a in selected_names and b not in selected_names and b not in seen_peer:
            peers.append((score_of.get(b, 0.0), b))
            seen_peer.add(b)
        elif b in selected_names and a not in selected_names and a not in seen_peer:
            peers.append((score_of.get(a, 0.0), a))
            seen_peer.add(a)
    peers.sort(key=lambda item: (-item[0], item[1]))
    room = max(0, int(total_limit) - len(selected))
    for score, name in peers[:room]:
        selected.append(
            TableCandidate(
                name=name,
                evidence=("schema_expand",),
                score=score,
                source="schema_expand",
            )
        )
        selected_names.add(name)
    return selected


def trim_schema_chars(
    tables: list[TableCandidate],
    schema_by_table: dict[str, str],
    *,
    schema_chars: int,
    measure: Callable[[str], int] | None = None,
) -> tuple[list[TableCandidate], list[str]]:
    """Drop least-evidenced tables until rendered schema fits ``schema_chars``.

    Unused on the live Wiki/agent path: char-budget table cuts drop JOIN
    hubs and hurt SQL accuracy. Kept for unit tests and optional callers.
    Pinned tables are never dropped.
    """
    if schema_chars <= 0 or not tables:
        return tables, []
    size = measure or len
    kept = list(tables)
    cut: list[str] = []
    while kept:
        rendered = "\n".join(
            schema_by_table[item.name]
            for item in kept
            if schema_by_table.get(item.name)
        )
        if size(rendered) <= schema_chars:
            break
        if len(kept) == 1 or kept[-1].source == "pinned":
            break
        dropped = kept.pop()
        cut.append(dropped.name)
    return kept, cut


def _table_mentioned(store: Any, raw_key: str, physical: str, query: str) -> bool:
    text = str(query or "").casefold()
    if not text:
        return False
    tokens = [physical, raw_key.rsplit("/", 1)[-1]]
    getter = getattr(store, "get_page", None) if store is not None else None
    page = getter(raw_key) if callable(getter) else None
    if page is not None:
        tokens.extend(
            [
                str(getattr(page, "page_key", "") or ""),
                str(getattr(page, "title", "") or ""),
                *list(getattr(page, "aliases", ()) or ()),
            ]
        )
    for token in tokens:
        name = str(token or "").strip()
        if len(name) >= _MIN_TABLE_MENTION and name.casefold() in text:
            return True
    return False


def _physical_table_name(store: Any, key: str) -> str:
    if not key:
        return ""
    if store is None:
        return key.rsplit("/", 1)[-1]
    getter = getattr(store, "get_page", None)
    page = getter(key) if callable(getter) else None
    if page is None:
        pages = getattr(store, "pages", {}) or {}
        page = pages.get(key)
    if page is None:
        return key.rsplit("/", 1)[-1]
    slug = str(getattr(page, "page_key", "") or key)
    return slug.rsplit("/", 1)[-1]
