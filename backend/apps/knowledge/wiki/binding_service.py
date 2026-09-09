"""Datasource ↔ wiki corpus bindings (decoupled from import)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreDatasource
from apps.knowledge.db_models import WikiCorpus, WikiCorpusBinding
from apps.knowledge.wiki.corpus_store import corpus_source_databases, get_corpus
from common.utils.utils import SQLBotLogUtil


class BindingError(ValueError):
    """User-facing bind/unbind failure."""


@dataclass
class BindingView:
    id: int
    oid: int
    datasource_id: int
    datasource_name: str | None
    corpus_id: int
    corpus_key: str
    remap_databases: dict[str, str]
    enabled: bool


def suggest_database_remap(
    source_databases: list[str], target_database: str | None
) -> dict[str, str]:
    """Map corpus-declared DBs onto the bound datasource's physical name."""
    target = (target_database or "").strip()
    if not target:
        return {}
    target_key = target.lower()
    remap: dict[str, str] = {}
    for name in source_databases:
        src = str(name).strip()
        if src and src.lower() != target_key:
            remap[src] = target
    return remap


def _datasource_database(ds: CoreDatasource | None) -> str | None:
    if ds is None:
        return None
    try:
        from apps.protocol import get_protocol_for_ds

        name = get_protocol_for_ds(ds).schema_namespace(ds)
        cleaned = str(name or "").strip()
        return cleaned or None
    except Exception:  # noqa: BLE001
        return None


def suggested_remap_for(
    session: Session, *, corpus_id: int, datasource_id: int
) -> dict[str, str]:
    ds = session.get(CoreDatasource, datasource_id)
    return suggest_database_remap(
        corpus_source_databases(session, corpus_id),
        _datasource_database(ds),
    )


def effective_remap_databases(
    provided: dict[str, str] | None, suggested: dict[str, str]
) -> dict[str, str]:
    """Empty ``{}`` from the admin UI is treated as missing, not an explicit no-op.

    The bind dialog always posts ``remap_databases`` (often ``{}``). Saving that
    as-is skips auto-map and leaves ``scope.databases`` on the corpus DB name,
    which silently zeros recall against the bound datasource.
    """
    cleaned = {
        str(k).strip(): str(v).strip()
        for k, v in (provided or {}).items()
        if str(k).strip() and str(v).strip()
    }
    if cleaned:
        return cleaned
    return dict(suggested)


def bind_corpus(
    session: Session,
    *,
    oid: int,
    corpus_key: str,
    datasource_id: int,
    remap_databases: dict[str, str] | None = None,
) -> BindingView:
    corpus = get_corpus(session, oid, corpus_key)
    if corpus is None or corpus.id is None:
        raise BindingError(f"corpus not found: {corpus_key}")
    ds = session.get(CoreDatasource, datasource_id)
    if ds is None:
        raise BindingError(f"datasource not found: {datasource_id}")
    if int(ds.oid) != int(oid):
        raise BindingError("datasource is not in the current workspace")

    remap = effective_remap_databases(
        remap_databases,
        suggested_remap_for(
            session, corpus_id=int(corpus.id), datasource_id=datasource_id
        ),
    )

    now = datetime.now()
    existing = session.exec(
        select(WikiCorpusBinding).where(
            WikiCorpusBinding.datasource_id == datasource_id
        )
    ).first()
    if existing is None:
        existing = WikiCorpusBinding(
            oid=oid,
            datasource_id=datasource_id,
            corpus_id=int(corpus.id),
            remap_databases=dict(remap or {}),
            enabled=True,
            create_time=now,
            update_time=now,
        )
    else:
        existing.oid = oid
        existing.corpus_id = int(corpus.id)
        existing.remap_databases = dict(remap or {})
        existing.enabled = True
        existing.update_time = now
    session.add(existing)
    session.commit()
    session.refresh(existing)
    SQLBotLogUtil.info(
        "wiki corpus bound: ds=%s corpus=%s remap=%s",
        datasource_id,
        corpus_key,
        existing.remap_databases,
    )
    return _to_view(existing, corpus.corpus_key, ds.name)


def unbind_datasource(session: Session, *, datasource_id: int, oid: int) -> bool:
    row = session.exec(
        select(WikiCorpusBinding).where(
            WikiCorpusBinding.datasource_id == datasource_id,
            WikiCorpusBinding.oid == oid,
        )
    ).first()
    if row is None:
        return False
    session.delete(row)
    session.commit()
    return True


def list_bindings(
    session: Session,
    oid: int,
    *,
    corpus_id: int | None = None,
    datasource_id: int | None = None,
) -> list[BindingView]:
    stmt = (
        select(WikiCorpusBinding, WikiCorpus)
        .join(WikiCorpus, WikiCorpus.id == WikiCorpusBinding.corpus_id)
        .where(WikiCorpusBinding.oid == oid)
    )
    if corpus_id is not None:
        stmt = stmt.where(WikiCorpusBinding.corpus_id == corpus_id)
    if datasource_id is not None:
        stmt = stmt.where(WikiCorpusBinding.datasource_id == datasource_id)
    views: list[BindingView] = []
    for binding, corpus in session.exec(stmt).all():
        ds = session.get(CoreDatasource, binding.datasource_id)
        views.append(_to_view(binding, corpus.corpus_key, ds.name if ds else None))
    return views


def get_enabled_binding(
    session: Session, datasource_id: int
) -> tuple[WikiCorpusBinding, WikiCorpus] | None:
    row = session.exec(
        select(WikiCorpusBinding, WikiCorpus)
        .join(WikiCorpus, WikiCorpus.id == WikiCorpusBinding.corpus_id)
        .where(
            WikiCorpusBinding.datasource_id == datasource_id,
            WikiCorpusBinding.enabled == True,  # noqa: E712
        )
    ).first()
    return row


def _to_view(
    binding: WikiCorpusBinding, corpus_key: str, datasource_name: str | None
) -> BindingView:
    remap = binding.remap_databases or {}
    clean = {str(k): str(v) for k, v in remap.items()}
    return BindingView(
        id=int(binding.id or 0),
        oid=int(binding.oid),
        datasource_id=int(binding.datasource_id),
        datasource_name=datasource_name,
        corpus_id=int(binding.corpus_id),
        corpus_key=corpus_key,
        remap_databases=clean,
        enabled=bool(binding.enabled),
    )
