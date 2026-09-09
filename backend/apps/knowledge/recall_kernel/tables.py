"""Single table-selection implementation for Wiki anchors and schema_vector."""

from __future__ import annotations

from typing import Any

from apps.knowledge.recall_kernel.types import RecallBudget, TableCandidate
from apps.knowledge.wiki.anchors import anchor_table_attribution


def resolve_wiki_tables(
    store: Any,
    *,
    page_keys: list[str],
    extra_keys: list[str] | None = None,
    table_pages: list[str] | None = None,
    scores: dict[str, float] | None = None,
    budget: RecallBudget | None = None,
) -> tuple[list[TableCandidate], list[str]]:
    """Wiki tables: gated semantic-page anchors ∪ gated table pages.

    Rank by evidence count, then page score. Budget ``max_tables`` cuts the tail.
    Returns ``(kept, budget_cut_names)``.
    """
    cap = (budget or RecallBudget()).max_tables
    page_scores = scores or {}
    seeds = list(dict.fromkeys([*(page_keys or []), *(extra_keys or [])]))
    attribution = anchor_table_attribution(store, seeds) if store is not None else {}
    ranked: dict[str, TableCandidate] = {}
    for name, sources in attribution.items():
        evidence = tuple(
            dict.fromkeys(str(item.get("page_key") or "") for item in sources if item.get("page_key"))
        )
        score = max((float(page_scores.get(key, 0.0)) for key in evidence), default=0.0)
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
                score=max(prior.score, float(page_scores.get(raw, 0.0)) + float(len(merged))),
                source=prior.source,
            )
            continue
        ranked[name] = TableCandidate(
            name=name,
            evidence=evidence,
            score=float(page_scores.get(raw, 0.0)) + 1.0,
            source="table_page",
        )
    ordered = sorted(
        ranked.values(),
        key=lambda item: (-len(item.evidence), -item.score, item.name),
    )
    kept = ordered[: max(1, cap)] if ordered else []
    cut = [item.name for item in ordered[len(kept) :]]
    return kept, cut


def resolve_schema_vector_tables(
    scored: list[dict[str, Any]],
    *,
    table_limit: int,
) -> list[TableCandidate]:
    """schema_vector docs → TableCandidate. Same ranking as the old _pick_tables."""
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
    ordered = sorted(ranked.items(), key=lambda item: item[1], reverse=True)
    limit = max(1, int(table_limit))
    return [
        TableCandidate(name=name, evidence=(), score=score, source="schema_vector")
        for name, score in ordered[:limit]
        if name
    ]


def trim_schema_chars(
    tables: list[TableCandidate],
    schema_by_table: dict[str, str],
    *,
    schema_chars: int,
) -> tuple[list[TableCandidate], list[str]]:
    """Drop least-evidenced tables until rendered schema fits ``schema_chars``."""
    if schema_chars <= 0 or not tables:
        return tables, []
    kept = list(tables)
    cut: list[str] = []
    while kept:
        rendered = "\n".join(
            schema_by_table[item.name] for item in kept if schema_by_table.get(item.name)
        )
        if len(rendered) <= schema_chars:
            break
        if len(kept) == 1:
            break
        dropped = kept.pop()
        cut.append(dropped.name)
    return kept, cut


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
