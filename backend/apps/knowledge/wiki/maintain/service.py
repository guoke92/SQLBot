"""Open a wiki maintenance chat. The graph is started later by /chat/runs."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, col, select

from apps.chat.curd.chat import create_chat
from apps.chat.models.chat_model import Chat, ChatRecord, CreateChat
from apps.knowledge.db_models import (
    WikiCorpus,
    WikiCorpusBinding,
    WikiPagePatch,
    WikiPageRevision,
    WikiPageRow,
    WikiSource,
)
from apps.knowledge.wiki.corpus_store import get_corpus
from apps.knowledge.wiki.embeddings_sync import schedule_embed_sync
from apps.knowledge.wiki.maintain.materials import (
    content_sha,
    conversation_locator,
    document_locator,
    spec_for,
)
from apps.knowledge.wiki.materialize import materialize_markdown
from apps.knowledge.wiki.writer import (
    WikiWriteError,
    apply_one,
    body_diff,
    create_source,
    list_revisions,
    overlay_patches,
    patch_dict,
    patches_between,
    promote_page,
    proposed_patches,
    revert_to_revision,
)

_ORIGINS = frozenset({"maintain", "conversation", "document"})


def open_maintain_chat(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    belong: str = "",
    page_key: str = "",
    pages: list[dict[str, str]] | None = None,
    source_ids: list[int] | None = None,
    source_id: int | None = None,
    origin: str = "maintain",
    source_ref: str = "",
    brief: str = "",
) -> dict[str, Any]:
    oid = int(getattr(user, "oid", None) or 1)
    corpus = get_corpus(session, oid, corpus_key.strip())
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    targets = _target_pages(session, int(corpus.id), pages, belong, page_key)
    materials = _load_sources(session, int(corpus.id), source_ids, source_id)
    if not targets and not materials:
        raise WikiWriteError("需要选择页面或原料")
    first = materials[0] if materials else None
    origin_name = (
        first.kind
        if first is not None and first.kind in _ORIGINS
        else (origin if origin in _ORIGINS else "maintain")
    )
    info = create_chat(
        session,
        user,
        CreateChat(
            chat_type="wiki",
            question=(brief or (targets[0]["page_key"] if targets else "") or corpus_key)[:20],
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
            "pages": targets,
            "sources": [int(item.id or 0) for item in materials],
            "belong": targets[0]["belong"] if targets else "",
            "page_key": targets[0]["page_key"] if targets else "",
            "source_id": int(first.id) if first is not None else None,
            "origin": origin_name,
            "source_ref": first.locator if first is not None else source_ref,
            "related": [],
        }
    }
    session.add(chat)
    session.commit()
    return {
        "chat_id": int(chat.id),
        "corpus_key": corpus.corpus_key,
        "pages": targets,
        "source_ids": [int(item.id or 0) for item in materials],
    }


def update_chat_focus(
    session: Session,
    user: Any,
    *,
    chat_id: int,
    pages: list[dict[str, str]] | None = None,
    source_ids: list[int] | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    chat = session.get(Chat, chat_id)
    if (
        chat is None
        or chat.chat_type != "wiki"
        or int(chat.create_by or 0) != int(getattr(user, "id", 0))
    ):
        raise WikiWriteError("record not found")
    transcript = dict(chat.agent_transcript or {})
    wiki = dict(transcript.get("wiki") or {})
    corpus = get_corpus(
        session, int(getattr(user, "oid", None) or 1), str(wiki.get("corpus_key") or "")
    )
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    prior_pages = [] if replace else list(wiki.get("pages") or [])
    prior_sources = [] if replace else list(wiki.get("sources") or [])
    targets = _target_pages(
        session,
        int(corpus.id),
        [*prior_pages, *(pages or [])],
        "",
        "",
    )
    materials = _load_sources(
        session,
        int(corpus.id),
        [*prior_sources, *(source_ids or [])],
        None,
    )
    first = materials[0] if materials else None
    wiki["pages"] = targets
    wiki["sources"] = [int(item.id or 0) for item in materials]
    if targets:
        wiki["belong"] = targets[0]["belong"]
        wiki["page_key"] = targets[0]["page_key"]
    if first is not None:
        wiki["source_id"] = int(first.id or 0)
        wiki["source_ref"] = first.locator
        if first.kind in _ORIGINS:
            wiki["origin"] = first.kind
    elif replace:
        wiki["source_id"] = None
        wiki["source_ref"] = ""
    transcript["wiki"] = wiki
    chat.agent_transcript = transcript
    session.add(chat)
    session.commit()
    return {"chat_id": chat_id, "pages": targets, "source_ids": wiki["sources"]}


def read_chat_focus(session: Session, user: Any, *, chat_id: int) -> dict[str, Any]:
    chat = session.get(Chat, chat_id)
    if (
        chat is None
        or chat.chat_type != "wiki"
        or int(chat.create_by or 0) != int(getattr(user, "id", 0))
    ):
        raise WikiWriteError("record not found")
    focus = _wiki_focus_of(chat)
    corpus = get_corpus(
        session, int(getattr(user, "oid", None) or 1), str(focus.get("corpus_key") or "")
    )
    pages: list[dict[str, str]] = []
    for item in focus.get("pages") or []:
        if not isinstance(item, dict):
            continue
        belong = str(item.get("belong") or "")
        page_key = str(item.get("page_key") or "")
        title = page_key
        if corpus is not None and corpus.id is not None and belong and page_key:
            row = session.exec(
                select(WikiPageRow).where(
                    WikiPageRow.corpus_id == int(corpus.id),
                    WikiPageRow.belong == belong,
                    WikiPageRow.page_key == page_key,
                )
            ).first()
            if row is not None and row.title:
                title = row.title
        pages.append({"belong": belong, "page_key": page_key, "title": title})
    sources: list[dict[str, Any]] = []
    raw_ids = list(focus.get("sources") or [])
    if not raw_ids and focus.get("source_id"):
        raw_ids = [focus.get("source_id")]
    for raw in raw_ids:
        try:
            source_id = int(raw)
        except (TypeError, ValueError):
            continue
        source = session.get(WikiSource, source_id)
        if source is None:
            continue
        sources.append(
            {
                "source_id": source_id,
                "title": source.title or source.locator,
                "locator": source.locator,
            }
        )
    return {
        "corpus_key": str(focus.get("corpus_key") or ""),
        "pages": pages,
        "sources": sources,
    }


def preview_material(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    kind: str,
    belong: str = "",
    page_key: str = "",
    record_id: int = 0,
    source_id: int = 0,
) -> dict[str, Any]:
    """Read-only detail for a chip. Does not open a dialogue."""
    from apps.knowledge.wiki.present import present_page_body

    oid = int(getattr(user, "oid", None) or 1)
    user_id = int(getattr(user, "id", 0) or 0)
    corpus = get_corpus(session, oid, corpus_key.strip())
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    if kind == "page":
        row = session.exec(
            select(WikiPageRow).where(
                WikiPageRow.corpus_id == int(corpus.id),
                WikiPageRow.belong == belong.strip(),
                WikiPageRow.page_key == page_key.strip(),
            )
        ).first()
        if row is None:
            raise WikiWriteError("page not found")
        return {
            "kind": "page",
            "title": row.title or row.page_key,
            "subtitle": f"{row.belong}/{row.page_key}",
            "question": "",
            "body": present_page_body(row.body_md or ""),
            "feedback": "",
            "comment": "",
        }
    if kind == "record":
        record = _owned_record(session, user_id, int(record_id))
        if record is None:
            raise WikiWriteError("record not found")
        return _record_preview(record)
    if kind == "source":
        source = session.get(WikiSource, int(source_id))
        if source is None or int(source.corpus_id) != int(corpus.id):
            raise WikiWriteError("source not found")
        pointer = source.pointer if isinstance(source.pointer, dict) else {}
        linked = pointer.get("record_id")
        if linked:
            record = _owned_record(session, user_id, int(linked))
            if record is not None:
                view = _record_preview(record)
                view["title"] = source.title or view["title"]
                return view
        return {
            "kind": source.kind,
            "title": source.title or source.locator,
            "subtitle": source.locator,
            "question": "",
            "body": source.body_md or "",
            "feedback": "",
            "comment": "",
        }
    raise WikiWriteError("source not found")


def _owned_record(session: Session, user_id: int, record_id: int) -> ChatRecord | None:
    record = session.get(ChatRecord, record_id)
    if record is None:
        return None
    if int(record.create_by or 0) == user_id:
        return record
    chat = session.get(Chat, int(record.chat_id))
    if chat is not None and int(chat.create_by or 0) == user_id:
        return record
    return None


def _record_preview(record: ChatRecord) -> dict[str, Any]:
    raw = record.answer if isinstance(record.answer, dict) else {}
    parts: list[str] = []
    prose = str(raw.get("content") or record.sql_answer or record.analysis or "").strip()
    if prose:
        parts.append(prose[:4000])
    datasets = raw.get("datasets")
    if isinstance(datasets, list):
        for item in datasets[:3]:
            if not isinstance(item, dict):
                continue
            sql = str(item.get("sql") or "").strip()
            if not sql:
                continue
            title = str(item.get("title") or "SQL")
            parts.append(f"**{title}**\n\n```sql\n{sql[:1500]}\n```")
    legacy_sql = (record.sql or "").strip()
    if legacy_sql and "```sql" not in "\n".join(parts):
        parts.append(f"```sql\n{legacy_sql[:2000]}\n```")
    return {
        "kind": "record",
        "chat_id": int(getattr(record, "chat_id", 0) or 0),
        "record_id": int(getattr(record, "id", 0) or 0),
        "title": (record.question or "")[:80],
        "subtitle": "",
        "question": record.question or "",
        "body": "\n\n".join(parts),
        "feedback": record.feedback or "",
        "comment": record.feedback_comment or "",
    }


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
        pointer={"belong": belong, "page_key": page_key},
        create_by=int(getattr(user, "id", 0) or 0) or None,
        toolset=spec_for("document").toolset,
        content_sha=content_sha(text),
    )
    source.locator = document_locator(int(source.id or 0))
    session.add(source)
    session.commit()
    return {
        "corpus_key": corpus.corpus_key,
        "source_id": int(source.id or 0),
        "locator": source.locator,
    }


def sediment_record(
    session: Session,
    user: Any,
    *,
    record_id: int,
) -> dict[str, Any]:
    """Register one问数 record as material. Does not open a chat."""
    captured = _capture_record(session, user, record_id=record_id, strict=True)
    if captured is None:
        raise WikiWriteError("record not found")
    return captured


_ACTIVE_RUNS = frozenset({"queued", "running", "awaiting_input"})


def _wiki_focus_of(chat: Chat) -> dict[str, Any]:
    raw = chat.agent_transcript if isinstance(chat.agent_transcript, dict) else {}
    focus = raw.get("wiki") if isinstance(raw.get("wiki"), dict) else {}
    return focus


def _chats_with_open_proposals(session: Session, chat_ids: list[int]) -> set[int]:
    from apps.conversation.models import ConversationRun

    if not chat_ids:
        return set()
    rows = session.exec(
        select(ConversationRun.chat_id)
        .join(WikiPagePatch, WikiPagePatch.run_id == ConversationRun.run_id)
        .where(
            col(ConversationRun.chat_id).in_(chat_ids),
            WikiPagePatch.status == "proposed",
        )
    ).all()
    return {int(item) for item in rows}


def _lane(status: str | None) -> str:
    if status in {"queued", "running"}:
        return "processing"
    if status == "awaiting_input":
        return "pending"
    return "done"


def _latest_runs(session: Session, chat_ids: list[int]) -> dict[int, Any]:
    from apps.conversation.models import ConversationRun

    if not chat_ids:
        return {}
    rows = session.exec(
        select(ConversationRun)
        .where(col(ConversationRun.chat_id).in_(chat_ids))
        .order_by(col(ConversationRun.update_time).desc())
    ).all()
    found: dict[int, Any] = {}
    for row in rows:
        chat_id = int(row.chat_id)
        if chat_id not in found:
            found[chat_id] = row
    return found


def _wiki_chats(session: Session, user: Any, corpus_key: str) -> list[Chat]:
    oid = int(getattr(user, "oid", None) or 1)
    rows = session.exec(
        select(Chat).where(
            Chat.oid == oid,
            Chat.create_by == int(user.id),
            Chat.chat_type == "wiki",
        )
    ).all()
    return [
        row
        for row in rows
        if str(_wiki_focus_of(row).get("corpus_key") or "") == corpus_key
    ]


def _chat_holds_source(chat: Chat, source_id: int, locator: str) -> bool:
    focus = _wiki_focus_of(chat)
    raw = focus.get("sources") if isinstance(focus.get("sources"), list) else []
    held: set[int] = set()
    for item in raw:
        try:
            held.add(int(item))
        except (TypeError, ValueError):
            continue
    if source_id and source_id in held:
        return True
    return str(focus.get("source_ref") or "") == locator


def find_active_dialogue(
    session: Session, user: Any, *, corpus_key: str, source_id: int, locator: str
) -> Chat | None:
    chats = _wiki_chats(session, user, corpus_key)
    runs = _latest_runs(session, [int(item.id or 0) for item in chats])
    for chat in chats:
        if not _chat_holds_source(chat, source_id, locator):
            continue
        run = runs.get(int(chat.id or 0))
        if run is not None and str(run.status) in _ACTIVE_RUNS:
            return chat
    return None


def list_dialogue_groups(session: Session, user: Any) -> list[dict[str, Any]]:
    """Every corpus the workspace can see, with its wiki dialogues inside."""
    from apps.knowledge.wiki.corpus_store import list_corpora

    oid = int(getattr(user, "oid", None) or 1)
    groups: list[dict[str, Any]] = []
    for corpus in list_corpora(session, oid):
        data = list_dialogues(session, user, corpus_key=corpus.corpus_key)
        groups.append(
            {
                "corpus_key": corpus.corpus_key,
                "name": corpus.name or corpus.corpus_key,
                "processing": data["processing"],
                "pending": data["pending"],
                "items": data["items"],
            }
        )
    groups.sort(key=lambda item: 0 if item["pending"] or item["processing"] else 1)
    return groups


def list_dialogues(session: Session, user: Any, *, corpus_key: str) -> dict[str, Any]:
    oid = int(getattr(user, "oid", None) or 1)
    corpus = get_corpus(session, oid, corpus_key.strip())
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    chats = _wiki_chats(session, user, corpus.corpus_key)
    chat_ids = [int(item.id or 0) for item in chats]
    runs = _latest_runs(session, chat_ids)
    open_proposals = _chats_with_open_proposals(session, chat_ids)
    items: list[dict[str, Any]] = []
    for chat in chats:
        focus = _wiki_focus_of(chat)
        run = runs.get(int(chat.id or 0))
        status = _lane(str(run.status) if run is not None else None)
        if status != "processing" and int(chat.id or 0) in open_proposals:
            status = "pending"
        stamp = run.update_time if run is not None and run.update_time else chat.create_time
        items.append(
            {
                "kind": "chat",
                "chat_id": int(chat.id or 0),
                "title": chat.brief or focus.get("page_key") or corpus.corpus_key,
                "status": status,
                "run_status": str(run.status) if run is not None else "",
                "run_id": str(run.run_id) if run is not None else "",
                "update_time": stamp.isoformat() if stamp else "",
            }
        )
    rank = {"pending": 0, "processing": 1, "done": 2}
    items.sort(key=lambda item: str(item.get("update_time") or ""), reverse=True)
    items.sort(key=lambda item: rank.get(str(item["status"]), 9))
    processing = sum(1 for item in items if item["status"] == "processing")
    pending = sum(1 for item in items if item["status"] == "pending")
    return {"processing": processing, "pending": pending, "items": items}


def list_bound_conversations(
    session: Session, user: Any, *, corpus_key: str
) -> list[dict[str, Any]]:
    records = list_maintain_records(session, user, corpus_key=corpus_key)
    grouped: dict[int, dict[str, Any]] = {}
    for item in records:
        chat_id = int(item["chat_id"])
        bucket = grouped.get(chat_id)
        if bucket is None:
            chat = session.get(Chat, chat_id)
            bucket = {
                "chat_id": chat_id,
                "title": (chat.brief if chat is not None and chat.brief else "") or item["question"],
                "records": [],
            }
            grouped[chat_id] = bucket
        bucket["records"].append(item)
    return list(grouped.values())


def capture_records(
    session: Session, user: Any, *, record_ids: list[int]
) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []
    for record_id in record_ids:
        row = _capture_record(session, user, record_id=int(record_id), strict=True)
        if row is not None:
            captured.append(row)
    return captured


async def start_voted_dialogue(
    session: Session,
    user: Any,
    record_id: int,
    trans: Any,
) -> dict[str, Any] | None:
    """Open one wiki dialogue for a vote and submit its first turn."""
    record = session.get(ChatRecord, record_id)
    if record is None or not record.feedback:
        return None
    captured = _capture_record(
        session,
        user,
        record_id=record_id,
        strict=False,
    )
    if captured is None:
        return None
    active = find_active_dialogue(
        session,
        user,
        corpus_key=str(captured["corpus_key"]),
        source_id=int(captured["source_id"]),
        locator=str(captured["locator"]),
    )
    if active is not None:
        return {"chat_id": int(active.id or 0), "started": False, "corpus_key": captured["corpus_key"]}
    opened = open_maintain_chat(
        session,
        user,
        corpus_key=str(captured["corpus_key"]),
        source_ids=[int(captured["source_id"])],
        brief=(record.question or trans("i18n_wiki_vote_brief"))[:20],
    )
    comment = record.feedback_comment or ""
    if record.feedback == "up":
        question = trans("i18n_wiki_vote_up")
    else:
        question = trans(
            "i18n_wiki_vote_down",
            comment=comment or trans("i18n_wiki_vote_no_comment"),
        )
    from apps.conversation.runtime import submit_graph
    from apps.knowledge.wiki.maintain.nodes import initialize_wiki_state

    state = await initialize_wiki_state(
        session,
        user=user,
        chat_id=int(opened["chat_id"]),
        question=question,
        base_state={"sink": "sse", "in_chat": True, "stream": True},
    )
    submit_graph("wiki_maintain", state).detach()
    return {
        "chat_id": int(opened["chat_id"]),
        "started": True,
        "corpus_key": captured["corpus_key"],
    }


def capture_voted_record(session: Session, record: ChatRecord) -> int | None:
    """Idempotent material capture after a vote. Missing wiki binding is a no-op."""
    user_id = int(record.create_by or 0)
    chat = session.get(Chat, int(record.chat_id))
    if chat is None:
        return None
    try:
        captured = _capture_record(
            session,
            _VoteUser(user_id, int(chat.oid or 1)),
            record_id=int(record.id or 0),
            strict=False,
        )
    except WikiWriteError:
        return None
    if captured is None:
        return None
    return int(captured["source_id"])


class _VoteUser:
    def __init__(self, user_id: int, oid: int) -> None:
        self.id = user_id
        self.oid = oid


def _target_pages(
    session: Session,
    corpus_id: int,
    pages: list[dict[str, str]] | None,
    belong: str,
    page_key: str,
) -> list[dict[str, str]]:
    raw = list(pages or [])
    if belong.strip() and page_key.strip():
        raw.append({"belong": belong.strip(), "page_key": page_key.strip()})
    seen: set[tuple[str, str]] = set()
    targets: list[dict[str, str]] = []
    for item in raw:
        key = (str(item.get("belong") or "").strip(), str(item.get("page_key") or "").strip())
        if not key[0] or not key[1] or key in seen:
            continue
        row = session.exec(
            select(WikiPageRow).where(
                WikiPageRow.corpus_id == corpus_id,
                WikiPageRow.belong == key[0],
                WikiPageRow.page_key == key[1],
                WikiPageRow.page_disabled.is_(False),
            )
        ).first()
        if row is None:
            raise WikiWriteError("page not found")
        seen.add(key)
        targets.append({"belong": key[0], "page_key": key[1]})
    return targets


def _load_sources(
    session: Session,
    corpus_id: int,
    source_ids: list[int] | None,
    source_id: int | None,
) -> list[WikiSource]:
    wanted = [int(item) for item in (source_ids or []) if int(item) > 0]
    if source_id:
        wanted.append(int(source_id))
    found: list[WikiSource] = []
    seen: set[int] = set()
    for item_id in wanted:
        if item_id in seen:
            continue
        row = session.get(WikiSource, item_id)
        if row is None or int(row.corpus_id) != corpus_id:
            raise WikiWriteError("source not found")
        seen.add(item_id)
        found.append(row)
    return found


def _capture_record(
    session: Session,
    user: Any,
    *,
    record_id: int,
    strict: bool,
) -> dict[str, Any] | None:
    record = session.get(ChatRecord, record_id)
    user_id = int(getattr(user, "id", 0) or 0)
    if record is None or int(record.create_by or 0) != user_id:
        if strict:
            raise WikiWriteError("record not found")
        return None
    chat = session.get(Chat, int(record.chat_id))
    oid = int(getattr(user, "oid", None) or 1)
    if (
        chat is None
        or int(chat.oid or 1) != oid
        or int(chat.create_by or 0) != user_id
    ):
        if strict:
            raise WikiWriteError("record not found")
        return None
    feedback = record.feedback
    comment = record.feedback_comment
    if not chat.datasource:
        if strict:
            raise WikiWriteError("这条问数没有数据源，不能沉淀")
        return None
    binding = session.exec(
        select(WikiCorpusBinding).where(
            WikiCorpusBinding.oid == oid,
            WikiCorpusBinding.datasource_id == int(chat.datasource),
            WikiCorpusBinding.enabled.is_(True),
        )
    ).first()
    if binding is None:
        if strict:
            raise WikiWriteError("这个数据源还没有绑定问数 Wiki")
        return None
    corpus = session.get(WikiCorpus, int(binding.corpus_id))
    if corpus is None or corpus.id is None:
        if strict:
            raise WikiWriteError("corpus not found")
        return None
    locator = conversation_locator(int(chat.id), int(record.id or 0))
    existing = session.exec(
        select(WikiSource).where(
            WikiSource.corpus_id == int(corpus.id),
            WikiSource.locator == locator,
        )
    ).first()
    if existing is None:
        existing = create_source(
            session,
            corpus_id=int(corpus.id),
            oid=oid,
            kind="conversation",
            title=(record.question or "问数反馈")[:255],
            body_md="",
            pointer={"chat_id": int(chat.id), "record_id": int(record.id or 0)},
            create_by=user_id,
            locator=locator,
            toolset=spec_for("conversation").toolset,
        )
        session.commit()
    return {
        "corpus_key": corpus.corpus_key,
        "source_id": int(existing.id or 0),
        "locator": locator,
        "feedback": feedback,
        "comment": comment,
    }


def classify_scope(
    session: Session, belong: str, page_key: str, focus: dict[str, Any]
) -> str:
    targets = {
        (str(item.get("belong") or ""), str(item.get("page_key") or ""))
        for item in (focus.get("pages") or [])
        if isinstance(item, dict)
    }
    if (belong, page_key) in targets:
        return "target"
    related = {
        (str(item.get("belong") or ""), str(item.get("page_key") or ""))
        for item in (focus.get("related") or [])
        if isinstance(item, dict)
    }
    if (belong, page_key) in related or (belong, page_key) in _linked_pages(session, focus):
        return "related"
    return "outside"


def _linked_pages(session: Session, focus: dict[str, Any]) -> set[tuple[str, str]]:
    import re

    corpus_key = str(focus.get("corpus_key") or "")
    links: set[tuple[str, str]] = set()
    corpus = session.exec(
        select(WikiCorpus).where(WikiCorpus.corpus_key == corpus_key)
    ).first()
    if corpus is None or corpus.id is None:
        return links
    pattern = re.compile(r"\[\[([^\]|#]+)")
    for item in focus.get("pages") or []:
        if not isinstance(item, dict):
            continue
        row = session.exec(
            select(WikiPageRow).where(
                WikiPageRow.corpus_id == int(corpus.id),
                WikiPageRow.belong == str(item.get("belong") or ""),
                WikiPageRow.page_key == str(item.get("page_key") or ""),
            )
        ).first()
        if row is None:
            continue
        for match in pattern.findall(row.body_md or ""):
            slug = match.strip()
            if "/" in slug:
                belong, page_key = slug.split("/", 1)
                links.add((belong, page_key))
    return links


def list_maintain_records(
    session: Session, user: Any, *, corpus_key: str
) -> list[dict[str, Any]]:
    oid = int(getattr(user, "oid", None) or 1)
    corpus = get_corpus(session, oid, corpus_key.strip())
    if corpus is None or corpus.id is None:
        raise WikiWriteError("corpus not found")
    bindings = session.exec(
        select(WikiCorpusBinding).where(
            WikiCorpusBinding.corpus_id == int(corpus.id),
            WikiCorpusBinding.enabled.is_(True),
        )
    ).all()
    datasource_ids = [int(item.datasource_id) for item in bindings]
    if not datasource_ids:
        return []
    chats = session.exec(
        select(Chat).where(
            Chat.oid == oid,
            Chat.create_by == int(user.id),
            col(Chat.datasource).in_(datasource_ids),
        )
    ).all()
    chat_ids = [int(item.id) for item in chats if item.id]
    if not chat_ids:
        return []
    records = session.exec(
        select(ChatRecord)
        .where(col(ChatRecord.chat_id).in_(chat_ids))
        .order_by(col(ChatRecord.id).desc())
        .limit(300)
    ).all()
    rows: list[dict[str, Any]] = []
    for record in records:
        locator = conversation_locator(int(record.chat_id), int(record.id or 0))
        source = session.exec(
            select(WikiSource).where(
                WikiSource.corpus_id == int(corpus.id),
                WikiSource.locator == locator,
            )
        ).first()
        rows.append(
            {
                "record_id": int(record.id or 0),
                "chat_id": int(record.chat_id),
                "question": record.question or "",
                "feedback": record.feedback,
                "comment": record.feedback_comment,
                "source_id": int(source.id) if source is not None and source.id else None,
                "locator": locator,
            }
        )
    rows.sort(key=lambda item: (item["feedback"] is None, -int(item["record_id"])))
    return rows


def page_history(
    session: Session, user: Any, *, corpus_key: str, belong: str, page_key: str
) -> list[dict[str, Any]]:
    row = _owned_page(session, user, corpus_key, belong, page_key)
    revisions = list_revisions(session, int(row.id or 0))
    history: list[dict[str, Any]] = []
    for revision in revisions:
        patches = patches_between(
            session, int(row.id or 0), int(revision.revision_no) - 1, int(revision.revision_no)
        )
        head = patches[-1] if patches else None
        history.append(
            {
                "revision_no": int(revision.revision_no),
                "create_time": revision.create_time.isoformat() if revision.create_time else "",
                "actor": head.actor if head is not None else "",
                "tool_name": head.tool_name if head is not None else revision.source,
                "source_ref": head.source_ref if head is not None else "",
                "content_sha": revision.content_sha,
                "status": revision.status,
            }
        )
    return history


def page_revision_diff(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    belong: str,
    page_key: str,
    left: int,
    right: int,
) -> dict[str, Any]:
    row = _owned_page(session, user, corpus_key, belong, page_key)
    left_row = _revision(session, int(row.id or 0), left)
    right_row = _revision(session, int(row.id or 0), right)
    between = patches_between(session, int(row.id or 0), left, right)
    return {
        "diff": body_diff(left_row.body_md or "", right_row.body_md or ""),
        "patches": [
            {
                "id": item.id,
                "op": item.op,
                "claim_path": item.claim_path,
                "status": item.status,
                "tool_name": item.tool_name,
                "source_ref": item.source_ref,
                "trust": item.trust,
                "revision_no": item.revision_no,
            }
            for item in between
        ],
    }


def page_revision_body(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    belong: str,
    page_key: str,
    revision_no: int,
) -> dict[str, Any]:
    row = _owned_page(session, user, corpus_key, belong, page_key)
    from apps.knowledge.wiki.present import present_page_body

    revision = _revision(session, int(row.id or 0), revision_no)
    return {
        "revision_no": int(revision.revision_no),
        "body_md": present_page_body(revision.body_md or ""),
        "content_sha": revision.content_sha,
    }


def rollback_page(
    session: Session,
    user: Any,
    *,
    corpus_key: str,
    belong: str,
    page_key: str,
    revision_no: int,
    confirm: bool,
) -> dict[str, Any]:
    row = _owned_page(session, user, corpus_key, belong, page_key)
    result = revert_to_revision(
        session,
        row,
        revision_no=revision_no,
        actor=str(getattr(user, "id", "") or ""),
        confirm=confirm,
    )
    if confirm and not result.get("already"):
        session.commit()
        schedule_embed_sync(int(row.corpus_id))
    return result


def _owned_page(
    session: Session, user: Any, corpus_key: str, belong: str, page_key: str
) -> WikiPageRow:
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
    if row is None or row.id is None:
        raise WikiWriteError("page not found")
    return row


def _revision(session: Session, page_id: int, revision_no: int) -> WikiPageRevision:
    row = session.exec(
        select(WikiPageRevision).where(
            WikiPageRevision.page_id == page_id,
            WikiPageRevision.revision_no == revision_no,
        )
    ).first()
    if row is None:
        raise WikiWriteError("revision not found")
    return row


def list_run_proposals(
    session: Session, *, run_id: str, user_id: int
) -> list[dict[str, Any]]:
    from apps.conversation.models import ConversationRun

    run = session.get(ConversationRun, run_id)
    if run is None or int(run.user_id) != user_id:
        raise WikiWriteError("run not found")
    chat = session.get(Chat, int(run.chat_id))
    transcript = chat.agent_transcript if chat is not None else {}
    focus = transcript.get("wiki") if isinstance(transcript, dict) else {}
    if not isinstance(focus, dict):
        focus = {}
    return _serialize_proposals(session, proposed_patches(session, run_id), focus)


def list_chat_proposals(session: Session, user: Any, *, chat_id: int) -> list[dict[str, Any]]:
    """Open claims for this dialogue, including after the turn has finished."""
    from apps.conversation.models import ConversationRun

    chat = session.get(Chat, chat_id)
    user_id = int(getattr(user, "id", 0) or 0)
    if chat is None or int(chat.create_by or 0) != user_id:
        raise WikiWriteError("record not found")
    run_ids = list(
        session.exec(
            select(ConversationRun.run_id).where(ConversationRun.chat_id == chat_id)
        ).all()
    )
    if not run_ids:
        return []
    rows = list(
        session.exec(
            select(WikiPagePatch)
            .where(
                col(WikiPagePatch.run_id).in_(run_ids),
                WikiPagePatch.status == "proposed",
            )
            .order_by(col(WikiPagePatch.id))
        ).all()
    )
    return _serialize_proposals(session, rows, _wiki_focus_of(chat))


def decide_proposal(
    session: Session, user: Any, *, patch_id: int, decision: str
) -> dict[str, Any]:
    """Accept or reject one claim. Accept rebuilds that page only."""
    from apps.conversation.models import ConversationRun

    row = session.get(WikiPagePatch, patch_id)
    if row is None or not row.run_id or row.status != "proposed":
        raise WikiWriteError("source not found")
    run = session.get(ConversationRun, row.run_id)
    user_id = int(getattr(user, "id", 0) or 0)
    if run is None or int(run.user_id) != user_id:
        raise WikiWriteError("source not found")
    if decision == "accept":
        apply_one(session, row, actor=str(user_id))
        corpus_id = int(row.corpus_id)
        session.commit()
        schedule_embed_sync(corpus_id)
    elif decision == "reject":
        row.status = "rejected"
        session.add(row)
        session.commit()
    else:
        raise WikiWriteError("source not found")
    return {"id": int(row.id or 0), "status": row.status}


def _serialize_proposals(
    session: Session, rows: list[Any], focus: dict[str, Any]
) -> list[dict[str, Any]]:
    diffs = _proposal_diffs(session, rows)
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
            "scope": classify_scope(session, row.belong, row.page_key, focus),
            "tool_name": row.tool_name,
            "trust": row.trust,
            "aspect": row.aspect,
            "source_ref": row.source_ref,
            "detail": proposal_detail(row),
            "reason": proposal_reason(row),
            "basis": proposal_basis(row),
            "diff": diffs.get(int(row.id or 0), ""),
        }
        for row in rows
    ]


def proposal_detail(row: Any) -> str:
    """The changed value. Display copy for the operation stays in the client."""
    payload = row.payload if isinstance(row.payload, dict) else {}
    if row.op == "add_alias":
        return str(payload.get("alias") or "").strip()
    if row.op == "create_page":
        return str(payload.get("title") or row.page_key or "").strip()
    return str(row.claim_path or "").strip()


def proposal_reason(row: Any) -> str:
    """Why this claim should change. The only store is observation.reason."""
    observed = row.observation if isinstance(row.observation, dict) else {}
    return str(observed.get("reason") or "").strip()


def proposal_basis(row: Any) -> str:
    """The material the claim cites: locator plus a short excerpt."""
    observed = row.observation if isinstance(row.observation, dict) else {}
    excerpt = str(observed.get("excerpt") or "").strip()
    locator = str(observed.get("locator") or getattr(row, "source_ref", "") or "").strip()
    if excerpt and locator and excerpt not in locator:
        return f"{locator} · {excerpt}"
    return excerpt or locator


def _proposal_diffs(session: Session, rows: list[Any]) -> dict[int, str]:
    """Preview each claim on its own. Accepting one does not include its siblings."""
    from difflib import unified_diff

    shown: dict[int, str] = {}
    for row in rows:
        page = session.exec(
            select(WikiPageRow).where(
                WikiPageRow.corpus_id == int(row.corpus_id),
                WikiPageRow.belong == row.belong,
                WikiPageRow.page_key == row.page_key,
            )
        ).first()
        base = page.base_body_md if page is not None and page.base_body_md else ""
        current = page.body_md if page is not None and page.body_md else ""
        prior = (
            overlay_patches(session, int(page.id)) if page is not None and page.id else []
        )
        preview = materialize_markdown(
            base,
            [
                *[patch_dict(item) for item in prior],
                patch_dict(row, status="applied"),
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
        shown[int(row.id or 0)] = text
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
