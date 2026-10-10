"""Session writer. Import and accepted proposals both land through materialize."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.knowledge.db_models import (
    WikiPagePatch,
    WikiPageRevision,
    WikiPageRow,
    WikiSource,
)
from apps.knowledge.wiki.contract import PageContractError, WikiPage, parse_page
from apps.knowledge.wiki.materialize import (
    MaterializeResult,
    PatchOutcome,
    content_sha,
    force_frontmatter_status,
    materialize_markdown,
    promotion_blockers,
)

OVERLAY_STATUSES = ("applied", "conflicted")
_FORBIDDEN_PAYLOAD = frozenset({"sources", "status", "evidence"})


class WikiWriteError(ValueError):
    """A wiki write was refused. Callers map this to a client error."""


def overlay_patches(session: Session, page_id: int) -> list[WikiPagePatch]:
    return list(
        session.exec(
            select(WikiPagePatch)
            .where(
                WikiPagePatch.page_id == page_id,
                WikiPagePatch.origin != "import",
                WikiPagePatch.status.in_(OVERLAY_STATUSES),
            )
            .order_by(WikiPagePatch.id)
        ).all()
    )


def patch_dict(row: WikiPagePatch, *, status: str | None = None) -> dict[str, Any]:
    payload = row.payload if isinstance(row.payload, dict) else {}
    return {
        "op": row.op,
        "origin": row.origin,
        "claim_path": row.claim_path,
        "payload": payload,
        "source_ref": row.source_ref,
        "status": status or row.status,
    }


def proposed_patches(session: Session, run_id: str) -> list[WikiPagePatch]:
    if not run_id:
        return []
    return list(
        session.exec(
            select(WikiPagePatch)
            .where(WikiPagePatch.run_id == run_id, WikiPagePatch.status == "proposed")
            .order_by(WikiPagePatch.id)
        ).all()
    )


def remember_outcome(row: WikiPagePatch, outcome: PatchOutcome) -> None:
    row.status = outcome.status
    if outcome.status != "conflicted" or not outcome.review_title:
        return
    payload = dict(row.payload or {})
    payload["review_title"] = outcome.review_title
    payload["review"] = outcome.review_body
    row.payload = payload


def project_page(row: WikiPageRow, body: str, *, status: str | None = None) -> None:
    try:
        parsed = parse_page(body, belong=row.belong or None)
    except PageContractError as exc:
        raise WikiWriteError(str(exc)) from exc
    row.body_md = body
    row.content_sha = content_sha(body)
    row.title = (parsed.title or parsed.page_key)[:255]
    row.page_type = parsed.type
    row.aliases = list(parsed.aliases)
    row.anchors = list(parsed.anchors)
    row.databases = list(parsed.databases)
    if status is not None:
        row.status = status
    row.update_time = datetime.now()


def add_revision(
    session: Session, row: WikiPageRow, *, source: str, now: datetime
) -> None:
    current = session.exec(
        select(WikiPageRevision.revision_no)
        .where(WikiPageRevision.page_id == row.id)
        .order_by(WikiPageRevision.revision_no.desc())
    ).first()
    try:
        revision_no = int(current or 0) + 1
    except (TypeError, ValueError):
        revision_no = 1
    session.add(
        WikiPageRevision(
            page_id=int(row.id),
            corpus_id=int(row.corpus_id),
            revision_no=revision_no,
            status=row.status,
            body_md=row.body_md,
            content_sha=row.content_sha,
            source=source[:32],
            create_time=now,
        )
    )


def _sync_outcomes(patches: list[WikiPagePatch], result: MaterializeResult) -> None:
    for row, outcome in zip(patches, result.outcomes, strict=True):
        if outcome.status in {"applied", "conflicted"} and outcome.status != row.status:
            remember_outcome(row, outcome)


def replay(row: WikiPageRow, patches: list[WikiPagePatch]) -> MaterializeResult:
    return materialize_markdown(
        row.base_body_md or "",
        [patch_dict(item) for item in patches],
    )


def materialize_row(
    session: Session,
    row: WikiPageRow,
    *,
    source: str,
    now: datetime | None = None,
    extra: list[WikiPagePatch] | None = None,
) -> str:
    """Rebuild ``body_md`` from the baseline and the overlay log."""
    stamp = now or datetime.now()
    patches = overlay_patches(session, int(row.id))
    if extra:
        patches = [*patches, *extra]
    result = replay(row, patches)
    _sync_outcomes(patches, result)
    project_page(row, result.body, status=row.status)
    session.add(row)
    add_revision(session, row, source=source, now=stamp)
    return result.body


def append_patch(
    session: Session,
    *,
    corpus_id: int,
    belong: str,
    page_key: str,
    origin: str,
    op: str,
    claim_path: str,
    payload: dict[str, Any],
    source_ref: str,
    actor: str,
    status: str,
    page_id: int | None = None,
    run_id: str | None = None,
    record_id: int | None = None,
    now: datetime | None = None,
) -> WikiPagePatch:
    clean = {
        key: value for key, value in payload.items() if key not in _FORBIDDEN_PAYLOAD
    }
    row = WikiPagePatch(
        page_id=page_id,
        corpus_id=corpus_id,
        belong=belong[:64],
        page_key=page_key[:255],
        run_id=(run_id or None),
        record_id=record_id,
        origin=origin,
        source_ref=source_ref,
        op=op,
        claim_path=claim_path,
        payload=clean,
        status=status,
        actor=actor[:64],
        create_time=now or datetime.now(),
    )
    session.add(row)
    session.flush()
    return row


def upsert_import_page(
    session: Session,
    *,
    corpus_id: int,
    row: WikiPageRow | None,
    file_body: str,
    file_page: WikiPage,
    now: datetime,
) -> WikiPageRow:
    """Replace the file baseline and replay maintenance. Does not touch page_disabled."""
    overlays = (
        overlay_patches(session, int(row.id)) if row is not None and row.id else []
    )
    existing_status = row.status if row is not None and overlays else None
    result = materialize_markdown(file_body, [patch_dict(item) for item in overlays])
    _sync_outcomes(overlays, result)
    body = result.body
    if existing_status and overlays:
        body = force_frontmatter_status(body, existing_status)
        status = existing_status
    else:
        try:
            parsed = parse_page(body, belong=file_page.belong or None)
        except PageContractError as exc:
            raise WikiWriteError(str(exc)) from exc
        status = (
            parsed.status
            if parsed.status in {"draft", "published", "retired"}
            else "draft"
        )
    try:
        parse_page(body, belong=file_page.belong or None)
    except PageContractError as exc:
        raise WikiWriteError(str(exc)) from exc
    sha = content_sha(body)
    if row is None:
        row = WikiPageRow(
            corpus_id=corpus_id,
            belong=file_page.belong[:64],
            page_key=file_page.page_key[:255],
            page_type=file_page.type,
            title=(file_page.title or file_page.page_key)[:255],
            status=status,
            databases=list(file_page.databases),
            aliases=list(file_page.aliases),
            anchors=list(file_page.anchors),
            body_md=body,
            base_body_md=file_body,
            content_sha=sha,
            page_disabled=False,
            create_time=now,
            update_time=now,
        )
        session.add(row)
        session.flush()
        project_page(row, body, status=status)
        append_patch(
            session,
            corpus_id=corpus_id,
            page_id=int(row.id),
            belong=row.belong,
            page_key=row.page_key,
            origin="import",
            op="replace_base",
            claim_path="",
            payload={},
            source_ref="import",
            actor="import",
            status="applied",
            now=now,
        )
        add_revision(session, row, source="import", now=now)
        return row

    changed = row.content_sha != sha or (row.base_body_md or "") != file_body
    row.base_body_md = file_body
    project_page(row, body, status=status)
    session.add(row)
    if changed:
        append_patch(
            session,
            corpus_id=corpus_id,
            page_id=int(row.id),
            belong=row.belong,
            page_key=row.page_key,
            origin="import",
            op="replace_base",
            claim_path="",
            payload={},
            source_ref="import",
            actor="import",
            status="applied",
            now=now,
        )
        add_revision(session, row, source="import", now=now)
    return row


def mark_absent_page(session: Session, row: WikiPageRow, *, now: datetime) -> str:
    """Delete a page that left the file set, unless maintenance still owns it."""
    if row.id is None:
        return "deleted"
    overlays = overlay_patches(session, int(row.id))
    if not overlays:
        return "deleted"
    already = session.exec(
        select(WikiPagePatch).where(
            WikiPagePatch.page_id == row.id,
            WikiPagePatch.claim_path == "review.stale",
            WikiPagePatch.status.in_(OVERLAY_STATUSES),
        )
    ).first()
    if already is None:
        append_patch(
            session,
            corpus_id=int(row.corpus_id),
            page_id=int(row.id),
            belong=row.belong,
            page_key=row.page_key,
            origin="maintain",
            op="open_review",
            claim_path="review.stale",
            payload={
                "type": "stale",
                "title": "导入基线已消失",
                "body": "文件集里已经没有这一页，维护补丁仍保留。",
            },
            source_ref="import",
            actor="import",
            status="applied",
            now=now,
        )
        materialize_row(session, row, source="import", now=now)
    return "kept"


def apply_proposed(
    session: Session,
    *,
    run_id: str,
    actor: str,
) -> list[WikiPagePatch]:
    """Accept this run's proposals and rebuild each touched draft."""
    rows = proposed_patches(session, run_id)
    if not rows:
        return []
    now = datetime.now()
    for row in rows:
        if not row.actor:
            row.actor = actor[:64]
    by_page: dict[tuple[str, str], list[WikiPagePatch]] = {}
    for row in rows:
        by_page.setdefault((row.belong, row.page_key), []).append(row)
    for (belong, page_key), batch in by_page.items():
        batch.sort(key=lambda item: 0 if item.op == "create_page" else 1)
        page = _page_for(session, int(batch[0].corpus_id), belong, page_key)
        if page is None:
            page = _create_from_batch(session, batch, now=now)
            if page is None:
                for item in batch:
                    session.add(item)
                continue
        else:
            prior = overlay_patches(session, int(page.id))
            combined = [*prior, *batch]
            result = materialize_markdown(
                page.base_body_md or "",
                [
                    *[patch_dict(item) for item in prior],
                    *[patch_dict(item, status="applied") for item in batch],
                ],
            )
            _sync_outcomes(combined, result)
            for item in batch:
                item.page_id = int(page.id)
            project_page(page, result.body, status=page.status)
            session.add(page)
            add_revision(session, page, source=_revision_source(batch), now=now)
        for item in batch:
            session.add(item)
    return rows


def reject_proposed(session: Session, *, run_id: str) -> int:
    rows = proposed_patches(session, run_id)
    for row in rows:
        row.status = "rejected"
        session.add(row)
    return len(rows)


def promote_page(
    session: Session,
    row: WikiPageRow,
    *,
    actor: str,
    siblings: list[dict[str, str]],
) -> WikiPageRow:
    """The only runtime status writer. Refuses while structural lint is open."""
    blockers = promotion_blockers(row.body_md, siblings=siblings)
    if blockers:
        raise WikiWriteError(
            "；".join(f"{item.code}: {item.message}" for item in blockers)
        )
    now = datetime.now()
    patch = append_patch(
        session,
        corpus_id=int(row.corpus_id),
        page_id=int(row.id),
        belong=row.belong,
        page_key=row.page_key,
        origin="maintain",
        op="promote",
        claim_path="status",
        payload={"status": "published"},
        source_ref=f"user_statement:{actor}",
        actor=actor,
        status="applied",
        now=now,
    )
    prior = [
        item for item in overlay_patches(session, int(row.id)) if item.id != patch.id
    ]
    result = materialize_markdown(
        row.base_body_md or "",
        [patch_dict(item) for item in [*prior, patch]],
    )
    project_page(row, result.body, status="published")
    session.add(row)
    add_revision(session, row, source="promote", now=now)
    return row


def create_source(
    session: Session,
    *,
    corpus_id: int,
    oid: int,
    kind: str,
    title: str,
    body_md: str,
    pointer: dict[str, Any],
    create_by: int | None,
) -> WikiSource:
    row = WikiSource(
        corpus_id=corpus_id,
        oid=oid,
        kind=kind,
        title=title[:255],
        body_md=body_md,
        pointer=pointer,
        create_by=create_by,
        create_time=datetime.now(),
    )
    session.add(row)
    session.flush()
    return row


def _page_for(
    session: Session, corpus_id: int, belong: str, page_key: str
) -> WikiPageRow | None:
    return session.exec(
        select(WikiPageRow).where(
            WikiPageRow.corpus_id == corpus_id,
            WikiPageRow.belong == belong,
            WikiPageRow.page_key == page_key,
        )
    ).first()


def _create_from_batch(
    session: Session,
    batch: list[WikiPagePatch],
    *,
    now: datetime,
) -> WikiPageRow | None:
    ordered = sorted(batch, key=lambda item: 0 if item.op == "create_page" else 1)
    creates = [item for item in ordered if item.op == "create_page"]
    if not creates:
        for item in batch:
            remember_outcome(
                item,
                PatchOutcome(
                    status="conflicted",
                    review_title="页面不存在",
                    review_body="没有这一页，也没有 create_page",
                ),
            )
        return None
    result = materialize_markdown(
        "",
        [patch_dict(item, status="applied") for item in ordered],
    )
    for item, outcome in zip(ordered, result.outcomes, strict=True):
        remember_outcome(item, outcome)
    if not result.body.strip() or any(item.status == "conflicted" for item in creates):
        return None
    head = creates[0]
    try:
        parsed = parse_page(result.body, belong=head.belong or None)
    except PageContractError as exc:
        for item in creates:
            remember_outcome(
                item,
                PatchOutcome(
                    status="conflicted",
                    review_title="页面无法解析",
                    review_body=str(exc),
                ),
            )
        return None
    row = WikiPageRow(
        corpus_id=int(head.corpus_id),
        belong=head.belong[:64],
        page_key=head.page_key[:255],
        page_type=parsed.type,
        title=(parsed.title or head.page_key)[:255],
        status="draft",
        databases=list(parsed.databases),
        aliases=list(parsed.aliases),
        anchors=list(parsed.anchors),
        body_md=result.body,
        base_body_md="",
        content_sha=content_sha(result.body),
        page_disabled=False,
        create_time=now,
        update_time=now,
    )
    session.add(row)
    session.flush()
    for item in batch:
        item.page_id = int(row.id)
        session.add(item)
    add_revision(session, row, source=_revision_source(batch), now=now)
    return row


def _revision_source(batch: list[WikiPagePatch]) -> str:
    origins = {item.origin for item in batch}
    if origins == {"conversation"}:
        return "conversation"
    if origins == {"document"}:
        return "document"
    return "maintain"
