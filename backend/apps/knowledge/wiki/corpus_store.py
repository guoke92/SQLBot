"""Import a wiki page directory into the DB corpus store.

Status is preserved as-is (draft stays draft). Broken pages are skipped.
Identity is ``(belong, page_key)``; replace upserts instead of wiping.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, delete, select

from apps.knowledge.db_models import (
    WikiChunkEmbedding,
    WikiCorpus,
    WikiPageRow,
)
from apps.knowledge.wiki.contract import (
    BELONG_DIRS,
    PageContractError,
    WikiPage,
    parse_page,
)
from apps.knowledge.wiki.writer import (
    WikiWriteError,
    mark_absent_page,
    upsert_import_page,
)
from common.utils.utils import SQLBotLogUtil


class CorpusImportError(ValueError):
    """User-facing import failure (bad path, missing replace, etc.)."""


@dataclass
class FailedPage:
    path: str
    error: str


@dataclass
class ParsedCorpus:
    pages: list[tuple[Path, WikiPage, str, str]]  # path, page, body, sha
    failed: list[FailedPage]


@dataclass
class ImportResult:
    corpus_id: int
    corpus_key: str
    generation: int
    total: int
    published: int
    draft: int
    failed: int
    failed_files: list[dict[str, str]] = field(default_factory=list)
    status: str = "indexing"
    replaced: bool = False


def iter_page_files(pages_dir: Path) -> list[Path]:
    """Markdown pages excluding `_` prefixes and `.runs` working dirs."""
    files: list[Path] = []
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        files.append(path)
    return files


def resolve_pages_dir(pages_dir: str | Path) -> Path:
    """Resolve import path relative to the repo root, not process cwd.

    Matches ``Settings.knowledge_wiki_pages_dirs_abs`` so a UI default like
    ``docs/wiki/v3`` works when uvicorn cwd is
    ``backend/``.
    """
    from common.core.config import _REPO_ROOT

    text = str(pages_dir).strip()
    if not text:
        raise CorpusImportError("pages_dir is required")
    raw = Path(text).expanduser()
    if not raw.is_absolute():
        raw = _REPO_ROOT / raw
    return raw.resolve()


def _directory_belong(pages_dir: Path, path: Path) -> str:
    try:
        relative = path.parent.resolve().relative_to(pages_dir.resolve())
    except ValueError:
        relative = Path(path.parent.name)
    parts = relative.parts
    if not parts:
        raise PageContractError(["page must live under a type directory (tables/…)"])
    belong = parts[0]
    if belong not in BELONG_DIRS:
        raise PageContractError(
            [f"parent directory {belong!r} is not a wiki belong dir"]
        )
    return belong


def parse_directory(pages_dir: Path) -> ParsedCorpus:
    """Zero-trust parse: contract errors skip the file, others keep going."""
    if not pages_dir.is_dir():
        raise CorpusImportError(f"pages_dir is not a directory: {pages_dir}")
    parsed: list[tuple[Path, WikiPage, str, str]] = []
    failed: list[FailedPage] = []
    seen: set[tuple[str, str]] = set()
    for path in iter_page_files(pages_dir):
        try:
            body = path.read_text(encoding="utf-8")
            belong = _directory_belong(pages_dir, path)
            page = parse_page(body, page_key=path.stem, belong=belong)
        except (OSError, UnicodeDecodeError, PageContractError) as exc:
            failed.append(FailedPage(path=str(path), error=str(exc)[:300]))
            continue
        ident = (page.belong, page.page_key)
        if ident in seen:
            failed.append(
                FailedPage(
                    path=str(path),
                    error=f"duplicate ({page.belong}, {page.page_key})",
                )
            )
            continue
        seen.add(ident)
        if path.stem != page.page_key:
            SQLBotLogUtil.warning(
                "wiki import filename stem %s != page_key %s (%s)",
                path.stem,
                page.page_key,
                path,
            )
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
        parsed.append((path, page, body, sha))
    return ParsedCorpus(pages=parsed, failed=failed)


def import_corpus(
    session: Session,
    *,
    oid: int,
    corpus_key: str,
    pages_dir: str | Path,
    replace: bool = False,
    name: str | None = None,
    schedule_embed: bool = True,
) -> ImportResult:
    """Write parsed pages into ``wiki_corpus`` / ``wiki_page`` and bump generation."""
    root = resolve_pages_dir(pages_dir)
    parsed = parse_directory(root)
    if not parsed.pages and not parsed.failed:
        raise CorpusImportError(f"no wiki pages found under {root}")
    return import_parsed_pages(
        session,
        oid=oid,
        corpus_key=corpus_key,
        parsed=parsed,
        name=name,
        source_path=str(root),
        replace=replace,
        schedule_embed=schedule_embed,
    )


def import_parsed_pages(
    session: Session,
    *,
    oid: int,
    corpus_key: str,
    parsed: ParsedCorpus,
    name: str | None = None,
    source_path: str = "",
    replace: bool = False,
    schedule_embed: bool = True,
) -> ImportResult:
    """Persist an already-parsed corpus (directory import or generated default)."""
    key = (corpus_key or "").strip()
    if not key:
        raise CorpusImportError("corpus_key is required")
    if not parsed.pages and not parsed.failed:
        raise CorpusImportError("no wiki pages to import")

    existing = session.exec(
        select(WikiCorpus).where(WikiCorpus.oid == oid, WikiCorpus.corpus_key == key)
    ).first()
    if existing is not None and not replace:
        raise CorpusImportError(
            f"corpus '{key}' already exists; pass replace=true to overwrite pages"
        )

    now = datetime.now()
    if existing is None:
        corpus = WikiCorpus(
            oid=oid,
            corpus_key=key,
            name=name or key,
            generation=0,
            page_count=0,
            published_count=0,
            draft_count=0,
            status="indexing",
            embedded_chunks=0,
            source_path=source_path or None,
            create_time=now,
            update_time=now,
        )
        session.add(corpus)
        session.flush()
        replaced = False
        existing_rows: list[WikiPageRow] = []
    else:
        corpus = existing
        corpus.name = name or corpus.name or key
        if source_path:
            corpus.source_path = source_path
        corpus.embed_error = None
        replaced = True
        existing_rows = list(
            session.exec(
                select(WikiPageRow).where(WikiPageRow.corpus_id == corpus.id)
            ).all()
        )

    by_ident = {(str(row.belong or ""), row.page_key): row for row in existing_rows}
    incoming = {
        (page.belong, page.page_key) for _path, page, _body, _sha in parsed.pages
    }

    for row in existing_rows:
        ident = (str(row.belong or ""), row.page_key)
        if ident in incoming:
            continue
        if mark_absent_page(session, row, now=now) == "kept":
            continue
        session.exec(
            delete(WikiChunkEmbedding).where(
                WikiChunkEmbedding.corpus_id == corpus.id,
                WikiChunkEmbedding.belong == ident[0],
                WikiChunkEmbedding.page_key == ident[1],
            )
        )
        session.delete(row)

    failed = list(parsed.failed)
    for path, page, body, _sha in parsed.pages:
        ident = (page.belong, page.page_key)
        row = by_ident.get(ident)
        try:
            upsert_import_page(
                session,
                corpus_id=int(corpus.id),
                row=row,
                file_body=body,
                file_page=page,
                now=now,
            )
        except WikiWriteError as exc:
            failed.append(FailedPage(path=path, error=str(exc)))

    stored = list(
        session.exec(
            select(WikiPageRow).where(WikiPageRow.corpus_id == corpus.id)
        ).all()
    )
    published = sum(1 for item in stored if item.status == "published")
    draft = sum(1 for item in stored if item.status == "draft")

    corpus.page_count = len(stored)
    corpus.published_count = published
    corpus.draft_count = draft
    corpus.generation = int(corpus.generation or 0) + 1
    corpus.status = "indexing"
    corpus.update_time = now
    session.add(corpus)
    session.commit()
    session.refresh(corpus)

    SQLBotLogUtil.info(
        "wiki corpus imported: key=%s id=%s pages=%s published=%s draft=%s failed=%s gen=%s",
        key,
        corpus.id,
        corpus.page_count,
        published,
        draft,
        len(failed),
        corpus.generation,
    )

    if schedule_embed and corpus.id is not None:
        from apps.knowledge.wiki.embeddings_sync import schedule_embed_sync

        schedule_embed_sync(int(corpus.id))

    return ImportResult(
        corpus_id=int(corpus.id),
        corpus_key=key,
        generation=int(corpus.generation),
        total=len(parsed.pages),
        published=published,
        draft=draft,
        failed=len(failed),
        failed_files=[{"path": item.path, "error": item.error} for item in failed],
        status=str(corpus.status),
        replaced=replaced,
    )


def get_corpus(session: Session, oid: int, corpus_key: str) -> WikiCorpus | None:
    return session.exec(
        select(WikiCorpus).where(
            WikiCorpus.oid == oid, WikiCorpus.corpus_key == corpus_key
        )
    ).first()


def delete_corpus(session: Session, oid: int, corpus_key: str) -> bool:
    corpus = get_corpus(session, oid, corpus_key)
    if corpus is None:
        return False
    session.delete(corpus)
    session.commit()
    return True


def list_corpora(session: Session, oid: int) -> list[WikiCorpus]:
    return list(
        session.exec(
            select(WikiCorpus)
            .where(WikiCorpus.oid == oid)
            .order_by(WikiCorpus.update_time.desc())
        ).all()
    )


def corpus_source_databases(session: Session, corpus_id: int) -> list[str]:
    """Distinct physical database names declared on pages."""
    rows = session.exec(
        select(WikiPageRow.databases).where(WikiPageRow.corpus_id == corpus_id)
    ).all()
    names: list[str] = []
    seen: set[str] = set()
    for value in rows:
        items = value if isinstance(value, list) else []
        for item in items:
            name = str(item).strip()
            key = name.lower()
            if name and key not in seen:
                seen.add(key)
                names.append(name)
    return names
