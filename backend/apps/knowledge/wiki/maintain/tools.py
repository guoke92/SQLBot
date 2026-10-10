"""Read and propose tools. None of these assign wiki_page.body_md."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from sqlmodel import select

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
from apps.knowledge.wiki.writer import append_patch

MAINTAIN_TOOL_NAMES = frozenset(
    {
        "read_page",
        "search_pages",
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
_BODY_CAP = 6000


class ReadPageArgs(BaseModel):
    belong: str = ""
    page_key: str = ""


class SearchArgs(BaseModel):
    query: str = ""
    belong: str = ""


class SourceArgs(BaseModel):
    source_id: int = 0


class ProposeArgs(BaseModel):
    op: str
    claim_path: str = ""
    payload_json: str = "{}"
    belong: str = ""
    page_key: str = ""


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
                    record_view = {
                        "chat_id": int(record.chat_id),
                        "record_id": int(record.id or 0),
                        "question": record.question or "",
                        "feedback": record.feedback,
                        "feedback_comment": record.feedback_comment,
                        "answer": str(record.sql_answer or "")[:2000],
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
        belong, page_key, local = _split_claim(
            claim_path,
            (belong or str(focus.get("belong") or "")).strip(),
            (page_key or str(focus.get("page_key") or "")).strip(),
        )
        if op_name == "create_page":
            if belong not in _BUSINESS_BELONGS:
                return tool_failure("不能新建物理页", belong or "空")
            payload = {
                "belong": belong,
                "page_key": page_key,
                "title": str(payload.get("title") or page_key),
            }
        else:
            payload.pop("sources", None)
            payload.pop("status", None)
            payload.pop("evidence", None)
            payload.pop("page_key", None)
            payload.pop("belong", None)
        if not belong or not page_key:
            return tool_failure("缺少页面", "belong/page_key")
        origin = str(focus.get("origin") or "maintain")
        if origin not in {"maintain", "conversation", "document"}:
            origin = "maintain"
        source_ref = (
            str(focus.get("source_ref") or "").strip() or f"user_statement:{run_id}"
        )
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
                "Record a claim patch for the user to accept. Does not modify the page."
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
