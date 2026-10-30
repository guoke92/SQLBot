"""Read and propose tools. None of these assign wiki_page.body_md."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from sqlmodel import col, select

from apps.chat.models.chat_model import Chat, ChatRecord
from apps.config_assistant.tools.common import require_workspace_admin
from apps.conversation.models import ConversationRun
from apps.conversation.runtime_context import current_worker_identity
from apps.conversation.session import session_scope
from apps.conversation.tooling import tool_failure, tool_success
from apps.knowledge.db_models import WikiPagePatch, WikiPageRow, WikiSource
from apps.knowledge.wiki.browse import CatalogNotFound, list_page_catalog
from apps.knowledge.wiki.contract import (
    BELONG_DIRS,
    PageContractError,
    lint_page,
    parse_page,
)
from apps.knowledge.wiki.corpus_store import get_corpus
from apps.knowledge.wiki.maintain.materials import cap_claim, content_sha, spec_for
from apps.knowledge.wiki.recall import InMemoryWikiStore, recall
from apps.knowledge.wiki.writer import append_patch

MAINTAIN_TOOL_NAMES = frozenset(
    {
        "read_page",
        "search_pages",
        "recall_pages",
        "lint_page",
        "read_source",
        "propose_patch",
        "discard_proposal",
    }
)
_PROPOSE_OPS = frozenset(
    {"upsert_claim", "dispute_claim", "add_alias", "open_review", "create_page"}
)
_BUSINESS_BELONGS = frozenset(
    {"concepts", "processes", "calibers", "metrics", "rules", "patterns", "scenarios"}
)
_CREATE_REQUIRED = {
    "calibers": "predicate",
    "metrics": "field",
    "rules": "content",
    "patterns": "question",
    "scenarios": "scenario",
}
_CREATE_DROP = frozenset(
    {
        "sources",
        "status",
        "evidence",
        "trust",
        "page_key",
        "belong",
        "reason",
        "type",
    }
)
_BODY_KEYS = (
    "predicate",
    "boundary",
    "text",
    "notes",
    "content",
    "question",
    "scope",
    "caliber",
    "metric",
)
_SNAPSHOT_COUNT = re.compile(r"\d{4,}|\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s*[%％]")
_NOT_A_FILTER = re.compile(r"未按|不要用|不能用|不作为|不要拿|不能拿|不是筛选|不要用来")


def create_page_payload(
    payload: dict[str, Any], belong: str, page_key: str
) -> tuple[dict[str, Any] | None, str]:
    """Keep the ground fields that make a new page reviewable.

    A title-only caliber or metric confirms into an empty draft. Counts from
    one question stay in the proposal reason, not in these fields.
    """
    kept = {
        key: value
        for key, value in payload.items()
        if key not in _CREATE_DROP and value not in ("", None, [], {})
    }
    required = _CREATE_REQUIRED.get(belong, "")
    if required and required not in kept:
        return None, (
            f"新建 {belong}/{page_key} 需要 payload.{required}。"
            "一次问数的企业数、条数和占比写在 reason，不要写进页面。"
        )
    title = str(kept.pop("title", "") or page_key)
    shaped = {"belong": belong, "page_key": page_key, "title": title, **kept}
    issue = page_body_issues(shaped)
    if issue:
        return None, issue
    return shaped, ""


def page_body_issues(payload: dict[str, Any]) -> str:
    """Reject page text that copies a page, cites a statistic, or lists a non-filter."""
    copied = [
        key
        for key in ("text", "notes")
        if isinstance(payload.get(key), str) and "document_claim:" in str(payload[key])
    ]
    if copied:
        return "说明里抄了页面原文。只写页面上还没有的一句，没有新规则就不要提案。"
    counted = [
        key
        for key in _BODY_KEYS
        if isinstance(payload.get(key), str)
        and _SNAPSHOT_COUNT.search(str(payload[key]))
    ]
    if counted:
        return (
            f"{'、'.join(counted)} 里有一次问数的计数或占比。"
            "计数写在 reason，页面只留可复用的判定。"
        )
    predicate = str(payload.get("predicate") or "")
    if re.search(r"\b(NOT\s+EXISTS|SELECT|JOIN)\b", predicate, re.IGNORECASE):
        return "predicate 写判定，不要写查询语句。"
    targets = payload.get("field_targets")
    if predicate and isinstance(targets, list):
        columns = [str(item).rsplit(".", 1)[-1] for item in targets]
        if any(column and column in predicate for column in columns):
            absent = [
                str(item)
                for item, column in zip(targets, columns, strict=True)
                if column not in predicate
            ]
            if absent:
                return (
                    f"{'、'.join(absent)} 没有出现在 predicate 里。"
                    "field_targets 只留真正用来判定的列。"
                )
    prose_sentences = re.split(
        r"[。；\n]",
        " ".join(
            str(payload.get(key) or "")
            for key in ("boundary", "predicate", "text", "notes")
        ),
    )
    targets = payload.get("field_targets")
    if not isinstance(targets, list):
        return ""
    excluded: list[str] = []
    for item in targets:
        column = str(item).rsplit(".", 1)[-1]
        if not column:
            continue
        if any(
            column in sentence and _NOT_A_FILTER.search(sentence)
            for sentence in prose_sentences
        ):
            excluded.append(str(item))
    if excluded:
        return (
            f"field_targets 含有明确不做筛选的字段：{'、'.join(excluded)}。"
            "只保留真正参与判定的字段。"
        )
    return ""


_BODY_CAP = 6000


class ReadPageArgs(BaseModel):
    belong: str = ""
    page_key: str = ""


class SearchArgs(BaseModel):
    query: str = ""
    belong: str = ""


class RecallArgs(BaseModel):
    query: str = ""


class SourceArgs(BaseModel):
    source_id: int = 0


class ProposeArgs(BaseModel):
    op: str
    claim_path: str = ""
    payload_json: str = "{}"
    belong: str = ""
    page_key: str = ""
    reason: str = Field(
        default="",
        description=(
            "依据和为什么改。引用问数记录、文档或页面上的具体说法，"
            "说明这个主张为什么成立。不要只复述改动结果。"
        ),
    )


class DiscardArgs(BaseModel):
    patch_id: int = Field(gt=0)


def build_tools(user: Any) -> list[BaseTool]:
    """Wiki maintenance catalog: read and propose only."""

    def _binding() -> tuple[str, Chat, int]:
        require_workspace_admin(user)
        run_id, _token = current_worker_identity()
        if not run_id:
            raise PermissionError("wiki tool is outside a maintenance run")
        with session_scope() as session:
            run = session.get(ConversationRun, run_id)
            if run is None or int(run.chat_id) <= 0:
                raise PermissionError("maintenance run was not found")
            chat = session.get(Chat, int(run.chat_id))
            if chat is None or int(chat.create_by) != int(getattr(user, "id", 0)):
                raise PermissionError("maintenance chat was not found")
            record_id = int(run.chat_record_id or 0)
        return run_id, chat, record_id

    def _focus(chat: Chat) -> dict[str, Any]:
        raw = chat.agent_transcript if isinstance(chat.agent_transcript, dict) else {}
        wiki = raw.get("wiki") if isinstance(raw.get("wiki"), dict) else {}
        return wiki

    def read_page(belong: str = "", page_key: str = "") -> dict[str, Any]:
        run_id, chat, _record_id = _binding()
        _ = run_id
        focus = _focus(chat)
        belong = (belong or str(focus.get("belong") or "")).strip()
        page_key = (page_key or str(focus.get("page_key") or "")).strip()
        corpus_key = str(focus.get("corpus_key") or "").strip()
        with session_scope() as session:
            corpus = get_corpus(session, int(chat.oid or 1), corpus_key)
            if corpus is None or corpus.id is None:
                raise CatalogNotFound("corpus")
            row = session.exec(
                select(WikiPageRow).where(
                    WikiPageRow.corpus_id == int(corpus.id),
                    WikiPageRow.belong == belong,
                    WikiPageRow.page_key == page_key,
                )
            ).first()
            if row is None:
                raise CatalogNotFound("page")
            raw = str(row.body_md or "")
            title = row.title
            status = row.status
        return tool_success(
            f"Read {belong}/{page_key}",
            {
                "belong": belong,
                "page_key": page_key,
                "title": title,
                "status": status,
                "claims": _claim_index(raw, belong, page_key),
                "body_md": raw[:_BODY_CAP],
                "truncated": len(raw) > _BODY_CAP,
            },
        )

    def search_pages(query: str = "", belong: str = "") -> dict[str, Any]:
        _run_id, chat, _record_id = _binding()
        focus = _focus(chat)
        corpus_key = str(focus.get("corpus_key") or "").strip()
        with session_scope() as session:
            catalog = list_page_catalog(
                session,
                int(chat.oid or 1),
                corpus_key,
                q=query,
                belong=belong,
            )
        pages = [
            {
                "belong": item.get("belong"),
                "page_key": item.get("page_key"),
                "title": item.get("title"),
                "status": item.get("status"),
            }
            for item in (catalog.get("pages") or [])[:20]
        ]
        return tool_success(f"Found {len(pages)} pages", {"pages": pages})

    def lint_page_tool(belong: str = "", page_key: str = "") -> dict[str, Any]:
        _run_id, chat, _record_id = _binding()
        focus = _focus(chat)
        belong = (belong or str(focus.get("belong") or "")).strip()
        page_key = (page_key or str(focus.get("page_key") or "")).strip()
        corpus_key = str(focus.get("corpus_key") or "").strip()
        with session_scope() as session:
            corpus = get_corpus(session, int(chat.oid or 1), corpus_key)
            if corpus is None or corpus.id is None:
                raise CatalogNotFound("corpus")
            row = session.exec(
                select(WikiPageRow).where(
                    WikiPageRow.corpus_id == int(corpus.id),
                    WikiPageRow.belong == belong,
                    WikiPageRow.page_key == page_key,
                )
            ).first()
            if row is None:
                raise CatalogNotFound("page")
            known = {
                f"{item.belong}/{item.page_key}"
                for item in session.exec(
                    select(WikiPageRow).where(WikiPageRow.corpus_id == int(corpus.id))
                ).all()
            }
            page = parse_page(row.body_md, page_key=page_key, belong=belong)
            findings = [
                {"code": item.code, "message": item.message}
                for item in lint_page(page, known_keys=known)[:30]
            ]
        return tool_success(
            f"Lint {belong}/{page_key}: {len(findings)} findings",
            {"findings": findings},
        )

    def read_source(source_id: int = 0) -> dict[str, Any]:
        _run_id, chat, _record_id = _binding()
        focus = _focus(chat)
        source_id = int(source_id or focus.get("source_id") or 0)
        with session_scope() as session:
            source = session.get(WikiSource, source_id)
            if source is None or int(source.oid) != int(chat.oid or 1):
                raise CatalogNotFound("page")
            pointer = dict(source.pointer) if isinstance(source.pointer, dict) else {}
            kind = source.kind
            title = source.title
            body = source.body_md[:_BODY_CAP]
            record_view = None
            record_id = pointer.get("record_id")
            if record_id:
                record = session.get(ChatRecord, int(record_id))
                if record is not None and int(record.chat_id) == int(
                    pointer.get("chat_id") or 0
                ):
                    from apps.knowledge.wiki.maintain.service import _record_preview

                    preview = _record_preview(record)
                    record_view = {
                        "chat_id": int(record.chat_id),
                        "record_id": int(record.id or 0),
                        "question": preview["question"],
                        "feedback": preview["feedback"],
                        "feedback_comment": preview["comment"],
                        "answer": preview["body"],
                    }
        return tool_success(
            f"Read source {source_id}",
            {
                "source_id": source_id,
                "kind": kind,
                "title": title,
                "body_md": body,
                "pointer": pointer,
                "record": record_view,
            },
        )

    def propose_patch(
        op: str,
        claim_path: str = "",
        payload_json: str = "{}",
        belong: str = "",
        page_key: str = "",
        reason: str = "",
    ) -> dict[str, Any]:
        run_id, chat, record_id = _binding()
        focus = _focus(chat)
        op_name = op.strip()
        if op_name not in _PROPOSE_OPS:
            return tool_failure("不认识的补丁操作", op_name)
        try:
            payload = json.loads(payload_json or "{}")
        except json.JSONDecodeError as exc:
            return tool_failure("payload_json 不是 JSON 对象", str(exc))
        if not isinstance(payload, dict):
            return tool_failure("payload_json 必须是对象", "not an object")
        reason_text = reason.strip() or str(payload.pop("reason", "") or "").strip()
        if not reason_text:
            return tool_failure(
                "缺少改动依据",
                "reason 要写清依据和为什么改，不要只描述改动结果",
            )
        belong, page_key, local = _split_claim(
            claim_path,
            (belong or str(focus.get("belong") or "")).strip(),
            (page_key or str(focus.get("page_key") or "")).strip(),
        )
        if op_name == "create_page":
            if belong not in _BUSINESS_BELONGS:
                return tool_failure("不能新建物理页", belong or "空")
            payload, missing = create_page_payload(payload, belong, page_key)
            if payload is None:
                return tool_failure("新建页缺少判定", missing)
        else:
            payload.pop("sources", None)
            payload.pop("status", None)
            payload.pop("evidence", None)
            payload.pop("page_key", None)
            payload.pop("belong", None)
            issue = page_body_issues(payload)
            if issue:
                return tool_failure("页面正文不合约束", issue)
            if local == "notes" or local.startswith("notes"):
                note = str(payload.get("text") or payload.get("notes") or "").strip()
                if len(note) > 180:
                    return tool_failure(
                        "说明只写新的一句",
                        "notes 只写页面上还没有的一句。不要抄页面原文，没有新规则就不要提案。",
                    )
        if not belong or not page_key:
            return tool_failure("缺少页面", "belong/page_key")
        origin = str(focus.get("origin") or "maintain")
        if origin not in {"maintain", "conversation", "document", "wiki"}:
            origin = "maintain"
        source_ref = (
            str(focus.get("source_ref") or "").strip() or f"user_statement:{run_id}"
        )
        aspect = _aspect(local, belong)
        kind = "wiki" if origin == "maintain" and not focus.get("sources") else origin
        if kind == "maintain":
            kind = "conversation"
        requested = str(payload.pop("trust", "") or "proposed")
        trust = cap_claim(kind, aspect, requested)
        if trust == "refuse":
            return tool_failure("这个原料不能改这一类主张", f"{kind}/{aspect}")
        payload["trust"] = trust
        corpus_key = str(focus.get("corpus_key") or "").strip()
        with session_scope() as session:
            corpus = get_corpus(session, int(chat.oid or 1), corpus_key)
            if corpus is None or corpus.id is None:
                raise CatalogNotFound("corpus")
            existing = session.exec(
                select(WikiPageRow).where(
                    WikiPageRow.corpus_id == int(corpus.id),
                    WikiPageRow.belong == belong,
                    WikiPageRow.page_key == page_key,
                )
            ).first()
            if op_name == "create_page" and existing is not None:
                return tool_failure("页面已存在", f"{belong}/{page_key}")
            if op_name != "create_page" and existing is None:
                return tool_failure("页面不存在", f"{belong}/{page_key}")
            source_row = _focus_source(session, focus)
            observed = _observation(source_row, source_ref)
            observed["reason"] = reason_text[:800]
            row = append_patch(
                session,
                corpus_id=int(corpus.id),
                page_id=int(existing.id)
                if existing is not None and existing.id
                else None,
                belong=belong,
                page_key=page_key,
                origin=origin,
                op=op_name,
                claim_path=f"{belong}/{page_key}#{local}",
                payload=payload,
                source_ref=source_ref,
                actor=str(getattr(user, "id", "") or ""),
                status="proposed",
                run_id=run_id,
                record_id=record_id or None,
                source_id=int(source_row.id) if source_row is not None else None,
                toolset=spec_for(kind).toolset,
                tool_name="propose_patch",
                aspect=aspect,
                trust=trust,
                observation=observed,
            )
            session.commit()
            patch_id = int(row.id or 0)
        return tool_success(
            "提案已记录，尚未写入页面",
            {
                "patch_id": patch_id,
                "op": op_name,
                "claim_path": f"{belong}/{page_key}#{local}",
            },
        )

    def discard_proposal(patch_id: int) -> dict[str, Any]:
        run_id, _chat, _record_id = _binding()
        with session_scope() as session:
            row = session.get(WikiPagePatch, int(patch_id))
            if row is None or row.run_id != run_id or row.status != "proposed":
                return tool_failure("没有这条待确认提案", str(patch_id))
            row.status = "rejected"
            session.add(row)
            session.commit()
        return tool_success("提案已撤回", {"patch_id": patch_id})

    def recall_pages(query: str) -> dict[str, Any]:
        """Return related page identities. The body stays behind read_page."""
        _run_id, chat, _record_id = _binding()
        focus = _focus(chat)
        corpus_key = str(focus.get("corpus_key") or "").strip()
        targets = {
            (str(item.get("belong") or ""), str(item.get("page_key") or ""))
            for item in (focus.get("pages") or [])
            if isinstance(item, dict)
        }
        pins = [
            f"{belong}/{page_key}"
            for belong, page_key in targets
            if belong and page_key
        ]
        with session_scope() as session:
            corpus = get_corpus(session, int(chat.oid or 1), corpus_key)
            if corpus is None or corpus.id is None:
                raise CatalogNotFound("corpus")
            stored = session.exec(
                select(WikiPageRow).where(
                    WikiPageRow.corpus_id == int(corpus.id),
                    WikiPageRow.page_disabled.is_(False),
                    col(WikiPageRow.status).in_(["draft", "published"]),
                )
            ).all()
            pages = []
            for item in stored:
                try:
                    pages.append(
                        parse_page(
                            item.body_md or "",
                            page_key=item.page_key,
                            belong=item.belong,
                        )
                    )
                except PageContractError:
                    continue
            store = InMemoryWikiStore(pages)
            text = query.strip() or " ".join(page_key for _belong, page_key in targets)
            hits = recall(text, store, pin_keys=pins, top_k=8) if text else []
            found = [
                {
                    "belong": hit.belong,
                    "page_key": hit.page_key,
                    "title": hit.title,
                    "reason": hit.source,
                    "related_to": list(hit.related_to),
                }
                for hit in hits
                if hit.page_key
            ]
            current = session.get(Chat, int(chat.id))
            if current is None:
                raise PermissionError("maintenance chat was not found")
            transcript = dict(current.agent_transcript or {})
            wiki = dict(transcript.get("wiki") or {})
            wiki["related"] = [
                item
                for item in found
                if (item["belong"], item["page_key"]) not in targets
            ]
            transcript["wiki"] = wiki
            current.agent_transcript = transcript
            session.add(current)
            session.commit()
        return tool_success("召回到相关页", {"pages": found})

    def _guard(func: Any) -> Any:
        def wrapped(*args: Any, **kwargs: Any) -> dict[str, Any]:
            try:
                return func(*args, **kwargs)
            except CatalogNotFound:
                return tool_failure("没有找到页面或语料", "not found")
            except (PermissionError, PageContractError, ValueError) as exc:
                return tool_failure("维护操作被拒绝", str(exc))

        return wrapped

    tools = [
        StructuredTool.from_function(
            func=_guard(read_page),
            name="read_page",
            description="Read one wiki page, including claim paths and the raw contract markdown.",
            args_schema=ReadPageArgs,
        ),
        StructuredTool.from_function(
            func=_guard(search_pages),
            name="search_pages",
            description="Search pages in the focused corpus by title, key, or alias.",
            args_schema=SearchArgs,
        ),
        StructuredTool.from_function(
            func=_guard(recall_pages),
            name="recall_pages",
            description=(
                "Recall related pages in this corpus. Returns identity, reason, and "
                "related_to only. Read a page before proposing a change to it."
            ),
            args_schema=RecallArgs,
        ),
        StructuredTool.from_function(
            func=_guard(lint_page_tool),
            name="lint_page",
            description="Lint one page. Findings are review items; this does not publish.",
            args_schema=ReadPageArgs,
        ),
        StructuredTool.from_function(
            func=_guard(read_source),
            name="read_source",
            description="Read pasted text or the chat record a conversation source points at.",
            args_schema=SourceArgs,
        ),
        StructuredTool.from_function(
            func=_guard(propose_patch),
            name="propose_patch",
            description=(
                "Record a claim patch for the user to accept. Does not modify the page. "
                "reason is required: cite the material and explain why the claim should change."
            ),
            args_schema=ProposeArgs,
        ),
        StructuredTool.from_function(
            func=_guard(discard_proposal),
            name="discard_proposal",
            description="Withdraw one proposal from this turn before the user accepts it.",
            args_schema=DiscardArgs,
        ),
    ]
    actual = {tool.name for tool in tools}
    if actual != MAINTAIN_TOOL_NAMES:
        raise RuntimeError(
            f"wiki tool catalog mismatch: {actual ^ MAINTAIN_TOOL_NAMES}"
        )
    return tools


def _aspect(local: str, belong: str) -> str:
    head = local.split(".", 1)[0]
    if head in {"primary_key", "grain", "name_anchors", "default_filter"}:
        return "structure"
    if belong == "dicts" or head == "values":
        return "enum_label"
    if head == "relations" or local.startswith("relations"):
        return "relation"
    if belong == "patterns" or head in {"sql", "pattern"}:
        return "pattern"
    return "business"


def _focus_source(session: Any, focus: dict[str, Any]) -> WikiSource | None:
    raw = focus.get("sources") or []
    source_id = 0
    if isinstance(raw, list) and raw:
        source_id = int(raw[0] or 0)
    elif focus.get("source_id"):
        source_id = int(focus.get("source_id") or 0)
    if source_id <= 0:
        return None
    return session.get(WikiSource, source_id)


def _observation(source: WikiSource | None, source_ref: str) -> dict[str, str]:
    if source is None:
        return {"locator": source_ref, "excerpt": "", "content_sha": ""}
    excerpt = (source.body_md or source.title or "")[:240]
    digest = source.content_sha or (
        content_sha(source.body_md) if source.body_md else ""
    )
    return {
        "locator": source.locator or source_ref,
        "excerpt": excerpt,
        "content_sha": digest,
    }


def _split_claim(claim_path: str, belong: str, page_key: str) -> tuple[str, str, str]:
    text = claim_path.strip()
    local = text
    if "#" in text:
        head, local = text.split("#", 1)
        if "/" in head:
            belong, page_key = head.split("/", 1)
    elif "/" in text:
        head, tail = text.split("/", 1)
        if head in BELONG_DIRS:
            belong, page_key = head, tail
            local = "page"
    return belong.strip(), page_key.strip(), local.strip() or "page"


def _claim_index(body: str, belong: str, page_key: str) -> list[str]:
    try:
        page = parse_page(body, page_key=page_key, belong=belong or None)
    except PageContractError:
        return []
    paths = [f"{belong}/{page_key}#aliases.{alias}" for alias in page.aliases]
    for block in page.ground_blocks:
        data = block.data
        if block.kind == "dict" and isinstance(data.get("values"), dict):
            paths.extend(
                f"{belong}/{page_key}#values.{code}" for code in data["values"]
            )
        elif block.kind == "table":
            for item in data.get("fields") or []:
                if isinstance(item, dict) and item.get("name"):
                    paths.append(f"{belong}/{page_key}#fields.{item['name']}")
        elif block.kind == "relation":
            left = data.get("left") or ""
            right = data.get("right") or ""
            paths.append(f"{belong}/{page_key}#relations.{left}__{right}")
        elif block.kind == "process":
            for stage in data.get("stages") or []:
                if isinstance(stage, dict) and stage.get("stage"):
                    paths.append(f"{belong}/{page_key}#stages.{stage['stage']}")
    paths.append(f"{belong}/{page_key}#notes")
    return paths[:80]
