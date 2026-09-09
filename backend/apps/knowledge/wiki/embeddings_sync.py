"""Incremental wiki chunk embedding sync into ``wiki_chunk_embedding``.

Runs off the request path so import stays fast. Query-time recall degrades to
lexical/alias while status is ``indexing``. The job always finishes with
``ready`` plus success/fail counts — it must not stay on ``indexing``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, delete, select

from apps.ai_model.embedding import pack_indices_by_tokens
from apps.knowledge.db_models import WikiChunkEmbedding, WikiCorpus, WikiPageRow
from apps.knowledge.wiki.chunker import chunk_markdown
from apps.knowledge.wiki.embeddings import chunk_fingerprint, chunk_text
from common.core.config import settings
from common.core.db import engine
from common.utils.utils import SQLBotLogUtil


def schedule_embed_sync(corpus_id: int) -> None:
    """Fire-and-forget embed sync on the shared embedding thread pool."""
    try:
        from common.utils.embedding_threads import executor

        executor.submit(_run_embed_sync_safe, corpus_id)
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning("wiki embed sync schedule failed: %s", exc)


def _clip_error(exc: BaseException) -> str:
    return str(exc).replace("\n", " ")[:500]


def _run_embed_sync_safe(corpus_id: int) -> None:
    try:
        sync_corpus_embeddings(corpus_id)
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning("wiki embed sync failed corpus_id=%s: %s", corpus_id, exc)
        with Session(engine) as session:
            corpus = session.get(WikiCorpus, corpus_id)
            if corpus is None:
                return
            corpus.status = "ready"
            corpus.embed_error = _clip_error(exc)
            if int(corpus.failed_chunks or 0) <= 0:
                corpus.failed_chunks = 1
            corpus.update_time = datetime.now()
            session.add(corpus)
            session.commit()


def _split_ident(ident: str) -> tuple[str, str]:
    if "/" in ident:
        belong, key = ident.split("/", 1)
        return belong, key
    return "", ident


def _upsert_vector(
    session: Session,
    *,
    by_page: dict[str, dict[int, WikiChunkEmbedding]],
    corpus_id: int,
    page_key: str,
    index: int,
    digest: str,
    heading: str,
    model_key: str,
    dimension: int,
    vector: list[float],
    now: datetime,
) -> None:
    cached = (by_page.get(page_key) or {}).get(index)
    payload = [float(x) for x in vector]
    belong, slug = _split_ident(page_key)
    if cached is not None:
        cached.belong = belong
        cached.page_key = slug
        cached.chunk_hash = digest
        cached.heading_path = heading
        cached.model_key = model_key
        cached.dimension = dimension
        cached.vector = payload
        cached.create_time = now
        session.add(cached)
        return
    row = WikiChunkEmbedding(
        corpus_id=corpus_id,
        belong=belong,
        page_key=slug,
        chunk_index=index,
        chunk_hash=digest,
        heading_path=heading,
        model_key=model_key,
        dimension=dimension,
        vector=payload,
        create_time=now,
    )
    session.add(row)
    by_page.setdefault(page_key, {})[index] = row


def _embed_group(
    embed_documents: Any,
    items: list[tuple[str, int, str, str, str]],
) -> tuple[list[list[float] | None], str | None]:
    """Embed a packed group. Batch first, then one-by-one on failure."""
    try:
        vectors = embed_documents([item[2] for item in items])
        return list(vectors), None
    except Exception as batch_exc:  # noqa: BLE001
        SQLBotLogUtil.warning(
            "wiki embed batch failed size=%s: %s", len(items), batch_exc
        )
        vectors: list[list[float] | None] = []
        last_error = _clip_error(batch_exc)
        for item in items:
            try:
                one = embed_documents([item[2]])
                vectors.append(list(one[0]) if one else None)
            except Exception as item_exc:  # noqa: BLE001
                last_error = _clip_error(item_exc)
                SQLBotLogUtil.warning(
                    "wiki embed chunk failed page=%s#%s: %s",
                    item[0],
                    item[1],
                    last_error,
                )
                vectors.append(None)
        return vectors, last_error


def _write_progress(
    session: Session,
    corpus: WikiCorpus,
    *,
    success: int,
    failed: int,
    error: str | None,
) -> None:
    corpus.embedded_chunks = success
    corpus.failed_chunks = failed
    corpus.embed_error = error
    corpus.status = "indexing"
    corpus.update_time = datetime.now()
    session.add(corpus)
    session.commit()


def sync_corpus_embeddings(
    corpus_id: int,
    *,
    embed_documents: Any = None,
    model_key: str | None = None,
    dimension: int | None = None,
) -> int:
    """Diff chunk fingerprints and upsert vectors. Returns written chunk count.

    ``embed_documents`` is injectable for tests (``list[str] -> list[list[float]]``).
    """
    with Session(engine) as session:
        corpus = session.get(WikiCorpus, corpus_id)
        if corpus is None:
            return 0
        pages = list(
            session.exec(
                select(WikiPageRow).where(WikiPageRow.corpus_id == corpus_id)
            ).all()
        )
        if not pages:
            corpus.status = "ready"
            corpus.embedded_chunks = 0
            corpus.failed_chunks = 0
            corpus.embed_error = None
            corpus.update_time = datetime.now()
            session.add(corpus)
            session.commit()
            return 0

        if embed_documents is None:
            if not settings.EMBEDDING_ENABLED:
                corpus.status = "ready"
                corpus.update_time = datetime.now()
                session.add(corpus)
                session.commit()
                return int(corpus.embedded_chunks or 0)
            from apps.ai_model.embedding import EmbeddingModelCache

            model = EmbeddingModelCache.get_model()
            embed_documents = model.embed_documents
            model_key = model_key or settings.DEFAULT_EMBEDDING_MODEL
            dimension = dimension or EmbeddingModelCache.get_dimension()
        resolved_model = model_key or settings.DEFAULT_EMBEDDING_MODEL
        resolved_dim = int(dimension or 0)

        existing = list(
            session.exec(
                select(WikiChunkEmbedding).where(
                    WikiChunkEmbedding.corpus_id == corpus_id
                )
            ).all()
        )
        by_page: dict[str, dict[int, WikiChunkEmbedding]] = {}
        for row in existing:
            ident = f"{row.belong}/{row.page_key}" if row.belong else row.page_key
            by_page.setdefault(ident, {})[row.chunk_index] = row

        wanted: set[tuple[str, int]] = set()
        pending: list[tuple[str, int, str, str, str]] = []
        keep: list[WikiChunkEmbedding] = []
        for page in pages:
            ident = f"{page.belong}/{page.page_key}" if page.belong else page.page_key
            chunks = chunk_markdown(page.body_md)
            for index, chunk in enumerate(chunks):
                text = chunk_text(page.page_key, chunk)
                digest = chunk_fingerprint(text, resolved_model, resolved_dim)
                wanted.add((ident, index))
                cached = (by_page.get(ident) or {}).get(index)
                if (
                    cached is not None
                    and cached.chunk_hash == digest
                    and cached.model_key == resolved_model
                    and int(cached.dimension) == resolved_dim
                    and cached.vector
                ):
                    keep.append(cached)
                    continue
                pending.append((ident, index, text, digest, chunk.heading_path or ""))

        stale_ids = [
            row.id
            for row in existing
            if row.id is not None
            and (
                f"{row.belong}/{row.page_key}" if row.belong else row.page_key,
                row.chunk_index,
            )
            not in wanted
        ]
        if stale_ids:
            session.exec(
                delete(WikiChunkEmbedding).where(WikiChunkEmbedding.id.in_(stale_ids))
            )

        corpus.status = "indexing"
        corpus.failed_chunks = 0
        corpus.embed_error = None
        corpus.embedded_chunks = len(keep)
        corpus.update_time = datetime.now()
        session.add(corpus)
        session.commit()

        now = datetime.now()
        written = 0
        failed = 0
        last_error: str | None = None
        texts = [item[2] for item in pending]
        for group in pack_indices_by_tokens(texts):
            items = [pending[i] for i in group]
            vectors, group_error = _embed_group(embed_documents, items)
            if group_error:
                last_error = group_error
            if len(vectors) < len(items):
                vectors.extend([None] * (len(items) - len(vectors)))
            for item, vector in zip(items, vectors, strict=False):
                page_key, index, _text, digest, heading = item
                if not vector:
                    failed += 1
                    continue
                _upsert_vector(
                    session,
                    by_page=by_page,
                    corpus_id=corpus_id,
                    page_key=page_key,
                    index=index,
                    digest=digest,
                    heading=heading,
                    model_key=resolved_model,
                    dimension=resolved_dim,
                    vector=vector,
                    now=now,
                )
                written += 1
            _write_progress(
                session,
                corpus,
                success=len(keep) + written,
                failed=failed,
                error=last_error,
            )

        total = len(keep) + written
        corpus.embedded_chunks = total
        corpus.failed_chunks = failed
        corpus.embed_error = last_error if failed else None
        corpus.status = "ready"
        corpus.update_time = datetime.now()
        session.add(corpus)
        session.commit()
        SQLBotLogUtil.info(
            "wiki embed sync ready corpus_id=%s chunks=%s new=%s failed=%s",
            corpus_id,
            total,
            written,
            failed,
        )
        return total
