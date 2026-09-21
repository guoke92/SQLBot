"""Admin jobs: value-index extract and default wiki generation."""

from __future__ import annotations

import threading
from copy import deepcopy
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, col, select

from apps.datasource.models.datasource import CoreDatasource, CoreTable
from apps.datasource.models.value_index import CoreValueIndex
from apps.knowledge.db_models import WikiCorpus, WikiCorpusBinding
from common.utils.utils import SQLBotLogUtil

_job_lock = threading.Lock()
_run_lock = threading.Lock()
_job: dict[str, Any] = {
    "status": "idle",
    "kind": "",
    "ds_ids": None,
    "phase": "",
    "message": "",
    "started_at": None,
    "finished_at": None,
    "error": None,
    "tables": 0,
    "pages": 0,
    "value_rows": 0,
}


def get_catalog_index_job() -> dict[str, Any]:
    with _job_lock:
        return deepcopy(_job)


def _set_job(**kwargs: Any) -> None:
    with _job_lock:
        _job.update(kwargs)


def _iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def list_catalog_index_status(
    session: Session, *, oid: int, ds_id: int | None = None
) -> list[dict[str, Any]]:
    ds_stmt = select(CoreDatasource).where(CoreDatasource.oid == int(oid))
    if ds_id is not None:
        ds_stmt = ds_stmt.where(CoreDatasource.id == int(ds_id))
    datasources = list(session.exec(ds_stmt.order_by(col(CoreDatasource.id))).all())
    if not datasources:
        return []
    ds_ids = [int(ds.id) for ds in datasources if ds.id is not None]

    table_rows = list(
        session.exec(
            select(CoreTable.ds_id, func.count(CoreTable.id))
            .where(CoreTable.ds_id.in_(ds_ids))
            .group_by(CoreTable.ds_id)
        ).all()
    )
    checked_rows = list(
        session.exec(
            select(CoreTable.ds_id, func.count(CoreTable.id))
            .where(
                CoreTable.ds_id.in_(ds_ids),
                CoreTable.checked == True,  # noqa: E712
            )
            .group_by(CoreTable.ds_id)
        ).all()
    )
    value_rows = list(
        session.exec(
            select(CoreValueIndex.ds_id, func.count(CoreValueIndex.id))
            .where(CoreValueIndex.ds_id.in_(ds_ids))
            .group_by(CoreValueIndex.ds_id)
        ).all()
    )
    bindings = list(
        session.exec(
            select(WikiCorpusBinding, WikiCorpus)
            .join(WikiCorpus, WikiCorpus.id == WikiCorpusBinding.corpus_id)
            .where(WikiCorpusBinding.datasource_id.in_(ds_ids))
        ).all()
    )
    table_map = {int(row[0]): int(row[1] or 0) for row in table_rows}
    checked_map = {int(row[0]): int(row[1] or 0) for row in checked_rows}
    value_map = {int(row[0]): int(row[1] or 0) for row in value_rows}
    bind_map = {
        int(binding.datasource_id): {
            "corpus_key": corpus.corpus_key,
            "wiki_pages": int(corpus.page_count or 0),
            "wiki_status": corpus.status,
            "wiki_generation": int(corpus.generation or 0),
        }
        for binding, corpus in bindings
    }

    items: list[dict[str, Any]] = []
    for ds in datasources:
        ident = int(ds.id)
        wiki = bind_map.get(ident) or {}
        values = int(value_map.get(ident) or 0)
        pages = int(wiki.get("wiki_pages") or 0)
        if wiki and values:
            state = "ready"
        elif wiki or values:
            state = "partial"
        elif int(table_map.get(ident) or 0) == 0:
            state = "empty"
        else:
            state = "missing"
        items.append(
            {
                "ds_id": ident,
                "name": ds.name,
                "state": state,
                "tables": int(table_map.get(ident) or 0),
                "checked_tables": int(checked_map.get(ident) or 0),
                "value_rows": values,
                "corpus_key": wiki.get("corpus_key") or "",
                "wiki_pages": pages,
                "wiki_status": wiki.get("wiki_status") or "",
                "wiki_generation": wiki.get("wiki_generation") or 0,
            }
        )
    return items


def start_value_index_extract(
    ds_ids: list[int] | None, *, oid: int | None = None
) -> dict[str, Any]:
    return _start_job("extract_values", ds_ids, _run_value_extract, oid=oid)


def start_default_wiki(ds_id: int, *, oid: int) -> dict[str, Any]:
    return _start_job("generate_wiki", [int(ds_id)], _run_default_wiki, oid=oid)


def _start_job(
    kind: str,
    ds_ids: list[int] | None,
    runner: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    if not _run_lock.acquire(blocking=False):
        return {**get_catalog_index_job(), "accepted": False, "reason": "busy"}
    _set_job(
        status="running",
        kind=kind,
        ds_ids=ds_ids,
        phase="queued",
        message="",
        started_at=_iso_now(),
        finished_at=None,
        error=None,
        tables=0,
        pages=0,
        value_rows=0,
    )
    from common.utils.embedding_threads import executor, session_maker

    def _run() -> None:
        try:
            runner(session_maker, ds_ids, **kwargs)
            _set_job(
                status="succeeded",
                phase="done",
                finished_at=_iso_now(),
            )
        except Exception as exc:
            SQLBotLogUtil.exception("catalog-index job %s failed", kind)
            _set_job(
                status="failed",
                phase="error",
                error=str(exc),
                message=str(exc),
                finished_at=_iso_now(),
            )
        finally:
            _run_lock.release()

    executor.submit(_run)
    return {**get_catalog_index_job(), "accepted": True, "reason": None}


def _run_value_extract(
    session_maker: Any, ds_ids: list[int] | None, *, oid: int | None = None
) -> None:
    from apps.datasource.instance_index.service import extract_datasource

    session: Session = session_maker()
    try:
        if ds_ids:
            ids = [int(item) for item in ds_ids]
        else:
            stmt = select(CoreDatasource.id)
            if oid is not None:
                stmt = stmt.where(CoreDatasource.oid == int(oid))
            ids = [int(item) for item in session.exec(stmt).all() if item is not None]
        total = 0
        for ident in ids:
            _set_job(phase="extract", message=f"ds={ident}")
            total += extract_datasource(session, ds_id=int(ident))
        _set_job(value_rows=total, message=f"extracted {total} rows")
    finally:
        session.close()


def _run_default_wiki(
    session_maker: Any, ds_ids: list[int] | None, *, oid: int
) -> None:
    from apps.knowledge.wiki.default_corpus import generate_and_bind_default_wiki

    session: Session = session_maker()
    try:
        ident = int((ds_ids or [0])[0])
        _set_job(phase="generate", message=f"ds={ident}")
        result = generate_and_bind_default_wiki(session, oid=oid, ds_id=ident)
        _set_job(
            tables=int(result.get("tables") or 0),
            pages=int(result.get("pages") or 0),
            message=f"wiki {result.get('corpus_key')}",
        )
    finally:
        session.close()
