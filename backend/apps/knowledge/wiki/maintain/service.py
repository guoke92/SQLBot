"""Open a wiki maintenance chat. The graph is started later by /chat/runs."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from apps.chat.curd.chat import create_chat
from apps.chat.models.chat_model import Chat, ChatRecord, CreateChat
from apps.knowledge.db_models import WikiCorpus, WikiCorpusBinding, WikiPageRow
from apps.knowledge.wiki.corpus_store import get_corpus
from apps.knowledge.wiki.embeddings_sync import schedule_embed_sync
from apps.knowledge.wiki.materialize import materialize_markdown
from apps.knowledge.wiki.writer import (
    WikiWriteError,
    create_source,
    overlay_patches,
    patch_dict,
    promote_page,
    proposed_patches,
)

_ORIGINS = frozenset({"maintain", "conversation", "document"})


def open_maintain_chat(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    belong: str = "",
    page_key: str = "",
    source_id: int | None = None,
    origin: str = "maintain",
    source_ref: str = "",
    brief: str = "",
) -> dict[str, Any]:
    oid = int(getattr(user, "oid", None) or 1)
    corpus = get_corpus(session, oid, corpus_key.strip())
    if corpus is None:
        raise WikiWriteError("corpus not found")
    origin_name = origin if origin in _ORIGINS else "maintain"
    info = create_chat(
        session,
        user,
        CreateChat(
            chat_type="wiki",
            question=(brief or page_key or corpus_key)[:20],
            origin=0,
        ),
        require_datasource=False,
    )
    chat = session.get(Chat, info.id)
    if chat is None:
        raise WikiWriteError("wiki chat was not created")
    chat.agent_transcript = {
        "wiki": {
            "corpus_key": corpus.corpus_key,
            "belong": belong,
            "page_key": page_key,
            "source_id": source_id,
            "origin": origin_name,
            "source_ref": source_ref,
        }
    }
    session.add(chat)
    session.commit()
    return {"chat_id": int(chat.id), "corpus_key": corpus.corpus_key}


def paste_source(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    title: str,
    body: str,
    belong: str = "",
    page_key: str = "",
) -> dict[str, Any]:
    text = body.strip()
    if not text:
        raise WikiWriteError("pasted text is empty")
    oid = int(getattr(user, "oid", None) or 1)
    corpus = get_corpus(session, oid, corpus_key.strip())
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    source = create_source(
        session,
        corpus_id=int(corpus.id),
        oid=oid,
        kind="document",
        title=(title or "粘贴文本")[:255],
        body_md=text,
        pointer={},
        create_by=int(getattr(user, "id", 0) or 0) or None,
    )
    session.commit()
    opened = open_maintain_chat(
        session,
        user,
        corpus_key=corpus.corpus_key,
        belong=belong,
        page_key=page_key,
        source_id=int(source.id),
        origin="document",
        source_ref=f"document:{source.id}",
        brief=title or "粘贴文本",
    )
    return {**opened, "source_id": int(source.id)}


def sediment_record(
    session: Session,
    user: Any,
    *,
    record_id: int,
) -> dict[str, Any]:
    """Store a pointer to one问数 record and open the same maintenance graph."""
    record = session.get(ChatRecord, record_id)
    if record is None or int(record.create_by or 0) != int(getattr(user, "id", 0)):
        raise WikiWriteError("record not found")
    chat = session.get(Chat, int(record.chat_id))
    oid = int(getattr(user, "oid", None) or 1)
    if (
        chat is None
        or int(chat.oid or 1) != oid
        or int(chat.create_by or 0) != int(user.id)
    ):
        raise WikiWriteError("record not found")
    feedback = record.feedback
    comment = record.feedback_comment
    if not chat.datasource:
        raise WikiWriteError("这条问数没有数据源，不能沉淀")
    binding = session.exec(
        select(WikiCorpusBinding).where(
            WikiCorpusBinding.oid == oid,
            WikiCorpusBinding.datasource_id == int(chat.datasource),
            WikiCorpusBinding.enabled.is_(True),
        )
    ).first()
    if binding is None:
        raise WikiWriteError("这个数据源还没有绑定问数 Wiki")
    corpus = session.get(WikiCorpus, int(binding.corpus_id))
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    source = create_source(
        session,
        corpus_id=int(corpus.id),
        oid=oid,
        kind="conversation",
        title=(record.question or "问数反馈")[:255],
        body_md="",
        pointer={"chat_id": int(chat.id), "record_id": int(record.id or 0)},
        create_by=int(user.id),
    )
    session.commit()
    opened = open_maintain_chat(
        session,
        user,
        corpus_key=corpus.corpus_key,
        origin="conversation",
        source_id=int(source.id),
        source_ref=f"conversation:{chat.id}/{record.id}",
        brief=(record.question or "问数反馈")[:20],
    )
    return {
        **opened,
        "source_id": int(source.id),
        "feedback": feedback,
        "comment": comment,
    }


def list_run_proposals(
    session: Session, *, run_id: str, user_id: int
) -> list[dict[str, Any]]:
    from apps.conversation.models import ConversationRun

    run = session.get(ConversationRun, run_id)
    if run is None or int(run.user_id) != user_id:
        raise WikiWriteError("run not found")
    run_rows = proposed_patches(session, run_id)
    diffs = _proposal_diffs(session, run_rows)
    return [
        {
            "id": int(row.id or 0),
            "op": row.op,
            "claim_path": row.claim_path,
            "payload": row.payload,
            "origin": row.origin,
            "status": row.status,
            "belong": row.belong,
            "page_key": row.page_key,
            "diff": diffs.get(int(row.id or 0), ""),
        }
        for row in run_rows
    ]


def _proposal_diffs(session: Session, rows: list[Any]) -> dict[int, str]:
    """Preview the draft each accepted page would become. One diff per page."""
    from difflib import unified_diff

    grouped: dict[tuple[int, str, str], list[Any]] = {}
    for row in rows:
        grouped.setdefault((int(row.corpus_id), row.belong, row.page_key), []).append(
            row
        )
    shown: dict[int, str] = {}
    for (corpus_id, belong, page_key), batch in grouped.items():
        page = session.exec(
            select(WikiPageRow).where(
                WikiPageRow.corpus_id == corpus_id,
                WikiPageRow.belong == belong,
                WikiPageRow.page_key == page_key,
            )
        ).first()
        base = page.base_body_md if page is not None and page.base_body_md else ""
        current = page.body_md if page is not None and page.body_md else ""
        prior = (
            overlay_patches(session, int(page.id))
            if page is not None and page.id
            else []
        )
        preview = materialize_markdown(
            base,
            [
                *[patch_dict(item) for item in prior],
                *[patch_dict(item, status="applied") for item in batch],
            ],
        ).body
        lines = list(
            unified_diff(
                current.splitlines(),
                preview.splitlines(),
                fromfile="current",
                tofile="draft",
                lineterm="",
                n=1,
            )
        )
        text = "\n".join(lines[:120])
        if len(lines) > 120:
            text += "\n…"
        shown[int(batch[0].id or 0)] = text
    return shown


def publish_page(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    belong: str,
    page_key: str,
) -> dict[str, str]:
    oid = int(getattr(user, "oid", None) or 1)
    corpus = get_corpus(session, oid, corpus_key)
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    row = session.exec(
        select(WikiPageRow).where(
            WikiPageRow.corpus_id == int(corpus.id),
            WikiPageRow.belong == belong,
            WikiPageRow.page_key == page_key,
        )
    ).first()
    if row is None:
        raise WikiWriteError("page not found")
    siblings = [
        {"belong": item.belong, "page_key": item.page_key, "status": item.status}
        for item in session.exec(
            select(WikiPageRow).where(WikiPageRow.corpus_id == int(corpus.id))
        ).all()
    ]
    promote_page(
        session, row, actor=str(getattr(user, "id", "") or ""), siblings=siblings
    )
    session.commit()
    schedule_embed_sync(int(corpus.id))
    return {"status": "published", "belong": belong, "page_key": page_key}
