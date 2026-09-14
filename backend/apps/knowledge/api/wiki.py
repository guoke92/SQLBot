"""Wiki corpus admin API: import by path, bind/unbind datasources."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apps.knowledge.wiki.binding_service import (
    BindingError,
    bind_corpus,
    collect_bind_ids,
    list_bindings,
    suggested_remap_for,
    sync_corpus_bindings,
    unbind_datasource,
)
from apps.knowledge.wiki.corpus_store import (
    CorpusImportError,
    delete_corpus,
    get_corpus,
    import_corpus,
    list_corpora,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from apps.system.schemas.system_schema import UserInfoDTO
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["Wiki"], prefix="/wiki")


class ImportCorpusBody(BaseModel):
    corpus_key: str = Field(min_length=1, max_length=64)
    pages_dir: str = Field(min_length=1, max_length=512)
    replace: bool = False
    name: str | None = Field(default=None, max_length=128)


class BindCorpusBody(BaseModel):
    corpus_key: str = Field(min_length=1, max_length=64)
    datasource_id: int | None = None
    datasource_ids: list[int] = Field(default_factory=list)
    remap_databases: dict[str, str] | None = None
    remaps_by_datasource: dict[str, dict[str, str]] = Field(default_factory=dict)


def _oid(user: UserInfoDTO) -> int:
    return int(getattr(user, "oid", 1) or 1)


@router.get("/corpora")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_corpora(
    session: SessionDep, current_user: CurrentUser
) -> list[dict[str, Any]]:
    oid = _oid(current_user)
    bindings = list_bindings(session, oid)
    by_corpus: dict[int, list[dict[str, Any]]] = {}
    for item in bindings:
        by_corpus.setdefault(item.corpus_id, []).append(
            {
                "datasource_id": item.datasource_id,
                "datasource_name": item.datasource_name,
                "remap_databases": item.remap_databases,
            }
        )
    rows = []
    for corpus in list_corpora(session, oid):
        rows.append(
            {
                "id": corpus.id,
                "oid": corpus.oid,
                "corpus_key": corpus.corpus_key,
                "name": corpus.name,
                "generation": corpus.generation,
                "page_count": corpus.page_count,
                "published_count": corpus.published_count,
                "draft_count": corpus.draft_count,
                "status": corpus.status,
                "embedded_chunks": corpus.embedded_chunks,
                "failed_chunks": corpus.failed_chunks,
                "embed_error": corpus.embed_error,
                "source_path": corpus.source_path,
                "update_time": corpus.update_time.isoformat()
                if corpus.update_time
                else None,
                "bindings": by_corpus.get(int(corpus.id or 0), []),
            }
        )
    return rows


@router.post("/corpora/import")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def import_wiki_corpus(
    session: SessionDep, current_user: CurrentUser, body: ImportCorpusBody
) -> dict[str, Any]:
    try:
        result = import_corpus(
            session,
            oid=_oid(current_user),
            corpus_key=body.corpus_key,
            pages_dir=body.pages_dir,
            replace=body.replace,
            name=body.name,
        )
    except CorpusImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "corpus_id": result.corpus_id,
        "corpus_key": result.corpus_key,
        "generation": result.generation,
        "total": result.total,
        "published": result.published,
        "draft": result.draft,
        "failed": result.failed,
        "failed_files": result.failed_files[:50],
        "status": result.status,
        "replaced": result.replaced,
    }


@router.get("/corpora/{corpus_key}/status")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def wiki_corpus_status(
    session: SessionDep, current_user: CurrentUser, corpus_key: str
) -> dict[str, Any]:
    corpus = get_corpus(session, _oid(current_user), corpus_key)
    if corpus is None:
        raise HTTPException(status_code=404, detail="corpus not found")
    return {
        "corpus_key": corpus.corpus_key,
        "generation": corpus.generation,
        "page_count": corpus.page_count,
        "published_count": corpus.published_count,
        "draft_count": corpus.draft_count,
        "status": corpus.status,
        "embedded_chunks": corpus.embedded_chunks,
        "failed_chunks": corpus.failed_chunks,
        "embed_error": corpus.embed_error,
        "source_path": corpus.source_path,
        "update_time": corpus.update_time.isoformat() if corpus.update_time else None,
    }


@router.delete("/corpora/{corpus_key}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def remove_wiki_corpus(
    session: SessionDep, current_user: CurrentUser, corpus_key: str
) -> dict[str, bool]:
    ok = delete_corpus(session, _oid(current_user), corpus_key)
    if not ok:
        raise HTTPException(status_code=404, detail="corpus not found")
    return {"deleted": True}


@router.post("/corpora/{corpus_key}/retry-embed")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def retry_wiki_embed(
    session: SessionDep, current_user: CurrentUser, corpus_key: str
) -> dict[str, Any]:
    corpus = get_corpus(session, _oid(current_user), corpus_key)
    if corpus is None or corpus.id is None:
        raise HTTPException(status_code=404, detail="corpus not found")
    from apps.knowledge.wiki.embeddings_sync import schedule_embed_sync

    corpus.status = "indexing"
    session.add(corpus)
    session.commit()
    schedule_embed_sync(int(corpus.id))
    return {
        "scheduled": True,
        "corpus_key": corpus.corpus_key,
        "status": "indexing",
        "embedded_chunks": corpus.embedded_chunks,
        "failed_chunks": corpus.failed_chunks,
    }


@router.get("/bindings")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_bindings(
    session: SessionDep,
    current_user: CurrentUser,
    datasource_id: int | None = None,
    corpus_key: str | None = None,
) -> list[dict[str, Any]]:
    oid = _oid(current_user)
    corpus_id = None
    if corpus_key:
        corpus = get_corpus(session, oid, corpus_key)
        if corpus is None:
            return []
        corpus_id = corpus.id
    views = list_bindings(
        session, oid, corpus_id=corpus_id, datasource_id=datasource_id
    )
    return [
        {
            "id": item.id,
            "datasource_id": item.datasource_id,
            "datasource_name": item.datasource_name,
            "corpus_id": item.corpus_id,
            "corpus_key": item.corpus_key,
            "remap_databases": item.remap_databases,
            "enabled": item.enabled,
        }
        for item in views
    ]


@router.get("/bindings/suggest")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def suggest_wiki_remap(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    datasource_id: int,
) -> dict[str, Any]:
    corpus = get_corpus(session, _oid(current_user), corpus_key)
    if corpus is None or corpus.id is None:
        raise HTTPException(status_code=404, detail="corpus not found")
    remap = suggested_remap_for(
        session, corpus_id=int(corpus.id), datasource_id=datasource_id
    )
    return {"remap_databases": remap}


@router.put("/bindings")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def put_wiki_binding(
    session: SessionDep, current_user: CurrentUser, body: BindCorpusBody
) -> dict[str, Any]:
    ids = collect_bind_ids(body.datasource_id, body.datasource_ids)
    if not ids:
        raise HTTPException(status_code=400, detail="select at least one datasource")
    try:
        if body.datasource_ids:
            views = sync_corpus_bindings(
                session,
                oid=_oid(current_user),
                corpus_key=body.corpus_key,
                datasource_ids=ids,
                remap_databases=body.remap_databases,
                remaps_by_datasource=body.remaps_by_datasource or None,
            )
        else:
            views = [
                bind_corpus(
                    session,
                    oid=_oid(current_user),
                    corpus_key=body.corpus_key,
                    datasource_id=ids[0],
                    remap_databases=body.remap_databases,
                )
            ]
    except BindingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    first = views[0] if views else None
    return {
        "corpus_key": body.corpus_key,
        "datasource_id": first.datasource_id if first else None,
        "datasource_name": first.datasource_name if first else None,
        "remap_databases": first.remap_databases if first else {},
        "enabled": first.enabled if first else False,
        "bindings": [
            {
                "datasource_id": item.datasource_id,
                "datasource_name": item.datasource_name,
                "remap_databases": item.remap_databases,
                "enabled": item.enabled,
            }
            for item in views
        ],
    }


@router.delete("/bindings/{datasource_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def delete_wiki_binding(
    session: SessionDep, current_user: CurrentUser, datasource_id: int
) -> dict[str, bool]:
    ok = unbind_datasource(session, datasource_id=datasource_id, oid=_oid(current_user))
    if not ok:
        raise HTTPException(status_code=404, detail="binding not found")
    return {"deleted": True}
