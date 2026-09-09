"""Load a bound wiki corpus from DB into the in-memory recall store."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace

from sqlmodel import Session, select

from apps.knowledge.db_models import WikiChunkEmbedding, WikiPageRow
from apps.knowledge.wiki.binding_service import get_enabled_binding
from apps.knowledge.wiki.contract import PageContractError, parse_page
from apps.knowledge.wiki.recall import RUNTIME_PAGE_STATUSES, InMemoryWikiStore
from common.utils.utils import SQLBotLogUtil

CacheStamp = tuple[int, int, str, str, int, str]


@dataclass(frozen=True)
class BoundCorpusLoad:
    store: InMemoryWikiStore
    vectors: dict[str, list[float]]
    generation: int
    corpus_id: int
    remap_fp: str
    status: str
    embedded_chunks: int = 0


def corpus_cache_stamp(
    *,
    corpus_id: int,
    generation: int,
    remap: dict[str, str] | None,
    status: str,
    embedded_chunks: int,
) -> CacheStamp:
    """Process-cache key. Embed finish does not bump generation, so status/chunks must be in the stamp.
    Runtime status set is part of the stamp so toggling draft admission busts the process cache."""
    cleaned = {str(k): str(v) for k, v in (remap or {}).items() if k and v}
    return (
        int(corpus_id),
        int(generation),
        json.dumps(cleaned, sort_keys=True, ensure_ascii=True),
        str(status or ""),
        int(embedded_chunks or 0),
        ",".join(sorted(RUNTIME_PAGE_STATUSES)),
    )


def binding_stamp(session: Session, datasource_id: int) -> CacheStamp | None:
    """Cheap cache key: corpus + generation + remap + embed progress."""
    pair = get_enabled_binding(session, datasource_id)
    if pair is None:
        return None
    binding, corpus = pair
    return corpus_cache_stamp(
        corpus_id=int(corpus.id or 0),
        generation=int(corpus.generation or 0),
        remap=binding.remap_databases,
        status=str(corpus.status or ""),
        embedded_chunks=int(corpus.embedded_chunks or 0),
    )


def remap_databases(
    databases: tuple[str, ...] | list[str], remap: dict[str, str] | None
) -> tuple[str, ...]:
    mapping = {str(k).strip(): str(v).strip() for k, v in (remap or {}).items() if k}
    if not mapping:
        return tuple(str(name).strip().lower() for name in databases)
    mapped: list[str] = []
    for name in databases:
        src = str(name).strip()
        dest = mapping.get(src) or mapping.get(src.lower()) or src
        mapped.append(dest.strip().lower())
    return tuple(mapped)


def load_bound_corpus(session: Session, datasource_id: int) -> BoundCorpusLoad | None:
    pair = get_enabled_binding(session, datasource_id)
    if pair is None:
        return None
    binding, corpus = pair
    remap = {
        str(k): str(v) for k, v in (binding.remap_databases or {}).items() if k and v
    }
    remap_fp = json.dumps(remap, sort_keys=True, ensure_ascii=True)
    rows = session.exec(
        select(WikiPageRow).where(
            WikiPageRow.corpus_id == corpus.id,
            WikiPageRow.status.in_(tuple(sorted(RUNTIME_PAGE_STATUSES))),
            WikiPageRow.page_disabled == False,  # noqa: E712
        )
    ).all()
    pages = []
    for row in rows:
        try:
            page = parse_page(
                row.body_md, page_key=row.page_key, belong=str(row.belong or "") or None
            )
        except PageContractError as exc:
            SQLBotLogUtil.warning(
                "wiki db page skipped page_key=%s: %s", row.page_key, exc
            )
            continue
        mapped = remap_databases(page.databases, remap)
        if mapped != page.databases:
            page = replace(page, databases=mapped)
        pages.append(page)
    store = InMemoryWikiStore(pages)
    vectors: dict[str, list[float]] = {}
    embeddings = session.exec(
        select(WikiChunkEmbedding).where(WikiChunkEmbedding.corpus_id == corpus.id)
    ).all()
    for emb in embeddings:
        page = store.get_page(emb.page_key)
        if page is None and getattr(emb, "belong", None):
            page = store.pages.get(f"{emb.belong}/{emb.page_key}")
        if page is None:
            continue
        raw = emb.vector if isinstance(emb.vector, list) else []
        if not raw:
            continue
        vectors[f"{page.store_key}#{emb.chunk_index}"] = [float(x) for x in raw]
    return BoundCorpusLoad(
        store=store,
        vectors=vectors,
        generation=int(corpus.generation or 0),
        corpus_id=int(corpus.id or 0),
        remap_fp=remap_fp,
        status=str(corpus.status or ""),
        embedded_chunks=int(corpus.embedded_chunks or 0),
    )
