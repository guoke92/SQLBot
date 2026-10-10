"""Read-only catalog of imported wiki pages for the admin browser."""

from __future__ import annotations

import re
from typing import Any

from sqlmodel import Session, select

from apps.knowledge.db_models import WikiPageRow
from apps.knowledge.wiki.contract import PageContractError, lint_page, parse_page
from apps.knowledge.wiki.corpus_store import get_corpus
from apps.knowledge.wiki.present import present_page_body

BELONG_ORDER = (
    "tables",
    "dicts",
    "concepts",
    "processes",
    "calibers",
    "metrics",
    "rules",
    "patterns",
    "scenarios",
    "sources",
)


class CatalogNotFound(Exception):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        super().__init__(kind)


def list_page_catalog(
    session: Session,
    oid: int,
    corpus_key: str,
    *,
    q: str = "",
    belong: str = "",
    status: str = "",
) -> dict[str, Any]:
    corpus = get_corpus(session, oid, corpus_key)
    if corpus is None or corpus.id is None:
        raise CatalogNotFound("corpus")
    rows = _page_rows(session, int(corpus.id))
    return {
        "corpus_key": corpus.corpus_key,
        **filter_page_catalog(rows, q=q, belong=belong, status=status),
    }


def get_page_detail(
    session: Session,
    oid: int,
    corpus_key: str,
    belong: str,
    page_key: str,
) -> dict[str, Any]:
    corpus = get_corpus(session, oid, corpus_key)
    if corpus is None or corpus.id is None:
        raise CatalogNotFound("corpus")
    corpus_id = int(corpus.id)
    row = session.exec(
        select(WikiPageRow).where(
            WikiPageRow.corpus_id == corpus_id,
            WikiPageRow.belong == belong,
            WikiPageRow.page_key == page_key,
        )
    ).first()
    if row is None:
        raise CatalogNotFound("page")
    return page_detail_payload(row, known_keys=_identity_keys(session, corpus_id))


def filter_page_catalog(
    rows: list[Any],
    *,
    q: str = "",
    belong: str = "",
    status: str = "",
) -> dict[str, Any]:
    status_name = status.strip()
    needle = q.strip().casefold()
    belong_name = belong.strip()
    matched_status = [
        row for row in rows if not status_name or str(row.status) == status_name
    ]
    matched = [row for row in matched_status if _matches_query(row, needle)]
    counts = _counts(matched)
    if belong_name:
        matched = [row for row in matched if str(row.belong) == belong_name]
    pages = [_summary(row) for row in matched]
    pages.sort(
        key=lambda item: (
            str(item["belong"]),
            str(item["title"]),
            str(item["page_key"]),
        )
    )
    return {"counts": counts, "pages": pages}


def page_detail_payload(
    row: Any, *, known_keys: set[str] | None = None
) -> dict[str, Any]:
    stored = _stored_fields(row)
    try:
        page = parse_page(
            str(row.body_md or ""),
            page_key=str(row.page_key),
            belong=str(row.belong or "") or None,
        )
    except PageContractError as exc:
        return {
            **stored,
            "body": present_page_body(str(row.body_md or "")),
            "parse_error": str(exc),
        }
    findings = lint_page(page, known_keys=set(known_keys or ()))
    return {
        **stored,
        "domain": page.domain,
        "aliases": list(page.aliases),
        "anchors": list(page.anchors),
        "maps_to": page.maps_to,
        "field_targets": list(page.field_targets),
        "related": list(page.related),
        "also_confused_with": list(page.also_confused_with),
        "adjudication": page.adjudication,
        "databases": list(page.databases),
        "recall": page.recall,
        "inactive": page.inactive,
        "body": present_page_body(page.body),
        "ground": [
            _ground_item(block.kind, block.data) for block in page.ground_blocks
        ],
        "reviews": [
            {"type": item.type, "title": item.title, "body": item.body}
            for item in page.reviews
        ],
        "links": [{"target": item.target, "alias": item.alias} for item in page.links],
        "findings": [{"code": item.code, "message": item.message} for item in findings],
        "parse_error": None,
    }


def _page_rows(session: Session, corpus_id: int) -> list[WikiPageRow]:
    return list(
        session.exec(
            select(WikiPageRow)
            .where(WikiPageRow.corpus_id == corpus_id)
            .order_by(WikiPageRow.belong, WikiPageRow.title, WikiPageRow.page_key)
        ).all()
    )


def _identity_keys(session: Session, corpus_id: int) -> set[str]:
    rows = session.exec(
        select(WikiPageRow.belong, WikiPageRow.page_key).where(
            WikiPageRow.corpus_id == corpus_id
        )
    ).all()
    keys: set[str] = set()
    for item in rows:
        belong = str(item[0] or "")
        page_key = str(item[1] or "")
        if page_key:
            keys.add(page_key)
        if belong and page_key:
            keys.add(f"{belong}/{page_key}")
    return keys


def _matches_query(row: Any, needle: str) -> bool:
    if not needle:
        return True
    if needle in str(row.title or "").casefold():
        return True
    if needle in str(row.page_key or "").casefold():
        return True
    aliases = row.aliases if isinstance(row.aliases, list) else []
    return any(needle in str(item).casefold() for item in aliases)


def _counts(rows: list[Any]) -> list[dict[str, Any]]:
    totals: dict[str, int] = {}
    for row in rows:
        name = str(row.belong or "")
        totals[name] = totals.get(name, 0) + 1
    ordered = [name for name in BELONG_ORDER if name in totals]
    ordered.extend(sorted(name for name in totals if name not in BELONG_ORDER))
    return [{"belong": name, "count": totals[name]} for name in ordered]


def _summary(row: Any) -> dict[str, Any]:
    aliases = row.aliases if isinstance(row.aliases, list) else []
    return {
        "belong": str(row.belong or ""),
        "page_key": str(row.page_key or ""),
        "title": str(row.title or ""),
        "page_type": str(row.page_type or ""),
        "status": str(row.status or ""),
        "aliases": [str(item) for item in aliases],
        "links": _link_targets(str(getattr(row, "body_md", "") or "")),
    }


_LINK_RE = re.compile(r"\[\[(?P<target>[^\]|#|]+)")


def _link_targets(text: str) -> list[str]:
    found: list[str] = []
    for match in _LINK_RE.finditer(text):
        target = match.group("target").strip()
        if target and target not in found:
            found.append(target)
    return found


def _stored_fields(row: Any) -> dict[str, Any]:
    updated = getattr(row, "update_time", None)
    aliases = row.aliases if isinstance(row.aliases, list) else []
    anchors = row.anchors if isinstance(row.anchors, list) else []
    databases = row.databases if isinstance(row.databases, list) else []
    return {
        "belong": str(row.belong or ""),
        "page_key": str(row.page_key or ""),
        "title": str(row.title or ""),
        "page_type": str(row.page_type or ""),
        "status": str(row.status or ""),
        "domain": "",
        "aliases": [str(item) for item in aliases],
        "anchors": [str(item) for item in anchors],
        "maps_to": "",
        "field_targets": [],
        "related": [],
        "also_confused_with": [],
        "adjudication": "",
        "databases": [str(item) for item in databases],
        "recall": True,
        "inactive": False,
        "body": "",
        "ground": [],
        "reviews": [],
        "links": [],
        "findings": [],
        "parse_error": None,
        "page_disabled": bool(getattr(row, "page_disabled", False)),
        "update_time": updated.isoformat() if updated is not None else None,
    }


def _ground_item(kind: str, data: dict[str, Any]) -> dict[str, str]:
    label = ""
    for key in (
        "table",
        "dict",
        "process",
        "caliber",
        "metric",
        "rule",
        "pattern",
        "scenario",
    ):
        value = data.get(key)
        if value:
            label = str(value)
            break
    if not label and kind == "relation":
        left = str(data.get("left") or "")
        right = str(data.get("right") or "")
        label = " → ".join(part for part in (left, right) if part)
    return {"kind": kind, "label": label}
