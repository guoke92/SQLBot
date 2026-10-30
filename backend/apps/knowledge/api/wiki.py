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
from apps.knowledge.wiki.browse import (
    CatalogNotFound,
    get_page_detail,
    list_page_catalog,
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


def catalog_http_error(exc: CatalogNotFound) -> HTTPException:
    if exc.kind == "page":
        return HTTPException(status_code=404, detail="page not found")
    return HTTPException(status_code=404, detail="corpus not found")


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


@router.get("/corpora/{corpus_key}/pages")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_pages(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    q: str = "",
    belong: str = "",
    status: str = "",
) -> dict[str, Any]:
    try:
        return list_page_catalog(
            session,
            _oid(current_user),
            corpus_key,
            q=q,
            belong=belong,
            status=status,
        )
    except CatalogNotFound as exc:
        raise catalog_http_error(exc) from exc


class RevertBody(BaseModel):
    revision_no: int
    confirm: bool = False


@router.get("/corpora/{corpus_key}/pages/{belong}/{page_key}/history")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def wiki_page_history(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    belong: str,
    page_key: str,
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import page_history
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return page_history(
            session,
            current_user,
            corpus_key=corpus_key,
            belong=belong,
            page_key=page_key,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/corpora/{corpus_key}/pages/{belong}/{page_key}/revisions/{revision_no}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def wiki_page_revision(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    belong: str,
    page_key: str,
    revision_no: int,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import page_revision_body
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return page_revision_body(
            session,
            current_user,
            corpus_key=corpus_key,
            belong=belong,
            page_key=page_key,
            revision_no=revision_no,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/corpora/{corpus_key}/pages/{belong}/{page_key}/diff")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def wiki_page_diff(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    belong: str,
    page_key: str,
    left: int,
    right: int,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import page_revision_diff
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return page_revision_diff(
            session,
            current_user,
            corpus_key=corpus_key,
            belong=belong,
            page_key=page_key,
            left=left,
            right=right,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.post("/corpora/{corpus_key}/pages/{belong}/{page_key}/revert")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def wiki_page_revert(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    belong: str,
    page_key: str,
    body: RevertBody,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import rollback_page
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return rollback_page(
            session,
            current_user,
            corpus_key=corpus_key,
            belong=belong,
            page_key=page_key,
            revision_no=body.revision_no,
            confirm=body.confirm,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.post("/corpora/{corpus_key}/pages/{belong}/{page_key}/promote")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def promote_wiki_page(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    belong: str,
    page_key: str,
) -> dict[str, str]:
    from apps.knowledge.wiki.maintain.service import publish_page
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return publish_page(
            session,
            current_user,
            corpus_key=corpus_key,
            belong=belong,
            page_key=page_key,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/corpora/{corpus_key}/pages/{belong}/{page_key:path}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def read_wiki_page(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    belong: str,
    page_key: str,
) -> dict[str, Any]:
    try:
        return get_page_detail(
            session, _oid(current_user), corpus_key, belong, page_key
        )
    except CatalogNotFound as exc:
        raise catalog_http_error(exc) from exc


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


class PageRef(BaseModel):
    belong: str = ""
    page_key: str = ""


class MaintainChatBody(BaseModel):
    """Corpus comes from the path."""

    belong: str = ""
    page_key: str = ""
    pages: list[PageRef] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    brief: str = ""


class PasteSourceBody(BaseModel):
    title: str = Field(default="", max_length=255)
    body: str = Field(min_length=1)
    belong: str = ""
    page_key: str = ""


class SedimentBody(BaseModel):
    record_id: int


def _write_http_error(exc: Exception) -> HTTPException:
    from apps.knowledge.wiki.writer import WikiWriteError

    if not isinstance(exc, WikiWriteError):
        raise exc
    detail = str(exc)
    missing = detail in {
        "corpus not found",
        "page not found",
        "record not found",
        "run not found",
    }
    return HTTPException(status_code=404 if missing else 400, detail=detail)


@router.post("/corpora/{corpus_key}/maintain/chats")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def open_wiki_maintain_chat(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    body: MaintainChatBody,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import open_maintain_chat
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return open_maintain_chat(
            session,
            current_user,
            corpus_key=corpus_key,
            belong=body.belong,
            page_key=body.page_key,
            pages=[item.model_dump() for item in body.pages],
            source_ids=body.source_ids,
            brief=body.brief,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


class FocusBody(BaseModel):
    pages: list[PageRef] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    replace: bool = False


@router.get("/corpora/{corpus_key}/maintain/preview")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def preview_wiki_material(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    kind: str,
    belong: str = "",
    page_key: str = "",
    record_id: int = 0,
    source_id: int = 0,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import preview_material
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return preview_material(
            session,
            current_user,
            corpus_key=corpus_key,
            kind=kind,
            belong=belong,
            page_key=page_key,
            record_id=record_id,
            source_id=source_id,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/maintain/chats/{chat_id}/focus")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def read_wiki_focus(
    session: SessionDep, current_user: CurrentUser, chat_id: int
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import read_chat_focus
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return read_chat_focus(session, current_user, chat_id=chat_id)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.post("/maintain/chats/{chat_id}/focus")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def update_wiki_focus(
    session: SessionDep, current_user: CurrentUser, chat_id: int, body: FocusBody
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import update_chat_focus
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return update_chat_focus(
            session,
            current_user,
            chat_id=chat_id,
            pages=[item.model_dump() for item in body.pages],
            source_ids=body.source_ids,
            replace=body.replace,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.post("/corpora/{corpus_key}/maintain/sources")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def paste_wiki_source(
    session: SessionDep,
    current_user: CurrentUser,
    corpus_key: str,
    body: PasteSourceBody,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import paste_source
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return paste_source(
            session,
            current_user,
            corpus_key=corpus_key,
            title=body.title,
            body=body.body,
            belong=body.belong,
            page_key=body.page_key,
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.post("/maintain/sediment")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def sediment_wiki_candidate(
    session: SessionDep, current_user: CurrentUser, body: SedimentBody
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import sediment_record
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return sediment_record(session, current_user, record_id=body.record_id)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/corpora/{corpus_key}/maintain/records")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_maintain_records(
    session: SessionDep, current_user: CurrentUser, corpus_key: str
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import list_maintain_records
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return list_maintain_records(session, current_user, corpus_key=corpus_key)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/dialogues")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_dialogue_groups(
    session: SessionDep, current_user: CurrentUser
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import list_dialogue_groups
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return list_dialogue_groups(session, current_user)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/corpora/{corpus_key}/dialogues")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_dialogues(
    session: SessionDep, current_user: CurrentUser, corpus_key: str
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import list_dialogues
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return list_dialogues(session, current_user, corpus_key=corpus_key)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/corpora/{corpus_key}/maintain/conversations")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_conversations(
    session: SessionDep, current_user: CurrentUser, corpus_key: str
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import list_bound_conversations
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return list_bound_conversations(session, current_user, corpus_key=corpus_key)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


class CaptureRecordsBody(BaseModel):
    record_ids: list[int] = Field(default_factory=list)


@router.post("/maintain/materials")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def capture_wiki_materials(
    session: SessionDep, current_user: CurrentUser, body: CaptureRecordsBody
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import capture_records
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return capture_records(session, current_user, record_ids=body.record_ids)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/maintain/chats/{chat_id}/proposals")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_chat_wiki_proposals(
    session: SessionDep, current_user: CurrentUser, chat_id: int
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import list_chat_proposals
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return list_chat_proposals(session, current_user, chat_id=chat_id)
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


class ProposalDecision(BaseModel):
    decision: str


@router.post("/maintain/patches/{patch_id}/decision")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def decide_wiki_proposal(
    session: SessionDep,
    current_user: CurrentUser,
    patch_id: int,
    body: ProposalDecision,
) -> dict[str, Any]:
    from apps.knowledge.wiki.maintain.service import decide_proposal
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return decide_proposal(
            session, current_user, patch_id=patch_id, decision=body.decision.strip()
        )
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc


@router.get("/maintain/runs/{run_id}/proposals")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_wiki_proposals(
    session: SessionDep, current_user: CurrentUser, run_id: str
) -> list[dict[str, Any]]:
    from apps.knowledge.wiki.maintain.service import list_run_proposals
    from apps.knowledge.wiki.writer import WikiWriteError

    try:
        return list_run_proposals(session, run_id=run_id, user_id=int(current_user.id))
    except WikiWriteError as exc:
        raise _write_http_error(exc) from exc
