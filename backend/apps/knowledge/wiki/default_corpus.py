"""Generate a default wiki corpus from CoreTable / CoreField."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from sqlmodel import Session, select

from apps.datasource.instance_index.extractor import select_extract_scope
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.knowledge.wiki.contract import PHYSICAL_SLUG_RE, PageContractError, parse_page
from apps.knowledge.wiki.corpus_store import (
    CorpusImportError,
    FailedPage,
    ImportResult,
    ParsedCorpus,
    import_parsed_pages,
)
from common.utils.utils import SQLBotLogUtil

_SLUG_CLEAN_RE = re.compile(r"[^a-z0-9_]+")
_TYPE_NUMBER = ("int", "num", "dec", "float", "double", "money", "real", "serial")
_TYPE_TEMPORAL = ("date", "time", "timestamp")


def default_corpus_key(ds_id: int) -> str:
    return f"ds-{int(ds_id)}-default"


def generate_and_bind_default_wiki(
    session: Session,
    *,
    oid: int,
    ds_id: int,
) -> dict[str, Any]:
    """Compile table pages + catalog_summary from the checked catalog, then bind."""
    ds = session.get(CoreDatasource, ds_id)
    if ds is None:
        raise CorpusImportError(f"datasource not found: {ds_id}")
    if int(ds.oid) != int(oid):
        raise CorpusImportError("datasource is not in the current workspace")

    parsed, stats = build_default_corpus(session, ds)
    if not parsed.pages:
        raise CorpusImportError("no tables available to generate a default wiki")
    corpus_key = default_corpus_key(ds_id)
    imported = import_parsed_pages(
        session,
        oid=oid,
        corpus_key=corpus_key,
        parsed=parsed,
        name=f"{ds.name or corpus_key} 默认 Wiki",
        source_path=f"generated:{corpus_key}",
        replace=True,
        schedule_embed=True,
    )
    from apps.knowledge.wiki.binding_service import bind_corpus

    bind_corpus(
        session,
        oid=oid,
        corpus_key=corpus_key,
        datasource_id=ds_id,
        commit=True,
    )
    return {
        "corpus_key": corpus_key,
        "tables": stats["tables"],
        "pages": imported.total,
        "published": imported.published,
        "failed": imported.failed,
        "generation": imported.generation,
        "import": _import_brief(imported),
    }


def build_default_corpus(
    session: Session, ds: CoreDatasource
) -> tuple[ParsedCorpus, dict[str, int]]:
    ds_id = int(ds.id)
    tables = select_extract_scope(
        list(
            session.exec(
                select(CoreTable)
                .where(CoreTable.ds_id == ds_id)
                .order_by(CoreTable.table_name.asc())
            ).all()
        )
    )
    table_ids = [int(table.id) for table in tables if table.id is not None]
    fields_by_table: dict[int, list[CoreField]] = defaultdict(list)
    if table_ids:
        fields = select_extract_scope(
            list(
                session.exec(
                    select(CoreField).where(
                        CoreField.ds_id == ds_id,
                        CoreField.table_id.in_(table_ids),
                    )
                ).all()
            )
        )
        for field in fields:
            fields_by_table[int(field.table_id)].append(field)
        for rows in fields_by_table.values():
            rows.sort(key=lambda item: int(item.field_index or 0))

    database = _datasource_database(ds)
    today = date.today().isoformat()
    pages: list[tuple[Path, Any, str, str]] = []
    failed: list[FailedPage] = []
    table_rows: list[tuple[str, str, list[str]]] = []
    for table in tables:
        name = str(table.table_name or "").strip()
        slug = _table_slug(name)
        if not slug:
            failed.append(
                FailedPage(path=f"tables/{name}", error="table name is not a wiki slug")
            )
            continue
        comment = str(table.custom_comment or table.table_comment or "").strip() or name
        ordered = fields_by_table.get(int(table.id or 0), [])
        markdown = render_default_table_page(
            table_name=slug,
            title=comment,
            database=database,
            fields=ordered,
            today=today,
        )
        try:
            page = parse_page(markdown, belong="tables")
        except PageContractError as exc:
            failed.append(FailedPage(path=f"tables/{slug}.md", error=str(exc)[:300]))
            continue
        sha = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        pages.append((Path(f"tables/{slug}.md"), page, markdown, sha))
        labels = [
            str(field.field_name or "").strip()
            for field in ordered[:8]
            if str(field.field_name or "").strip()
        ]
        table_rows.append((slug, comment, labels))

    summary = render_default_catalog_summary(table_rows, database=database, today=today)
    try:
        page = parse_page(summary, belong="concepts")
        sha = hashlib.sha256(summary.encode("utf-8")).hexdigest()
        pages.append((Path("concepts/catalog_summary.md"), page, summary, sha))
    except PageContractError as exc:
        failed.append(
            FailedPage(path="concepts/catalog_summary.md", error=str(exc)[:300])
        )

    return ParsedCorpus(pages=pages, failed=failed), {
        "tables": len(table_rows),
        "pages": len(pages),
        "failed": len(failed),
    }


def render_default_table_page(
    *,
    table_name: str,
    title: str,
    database: str,
    fields: list[CoreField],
    today: str,
) -> str:
    front = {
        "type": "table",
        "title": title.replace(":", "："),
        "page_key": table_name,
        "belong": "tables",
        "status": "published",
        "anchors": [table_name],
        "sources": [
            f"database_schema:{database}.{table_name}"
            if database
            else f"database_schema:{table_name}"
        ],
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if database:
        front["databases"] = [database]
    ground = {
        "table": table_name,
        "database": database,
        "desc": title,
        "inactive": False,
        "fields": [
            {
                "name": str(field.field_name or "").strip(),
                "type": _field_family(str(field.field_type or "")),
                "desc": str(field.custom_comment or field.field_comment or "").strip()
                or str(field.field_name or "").strip(),
            }
            for field in fields
            if str(field.field_name or "").strip()
        ],
    }
    body = (
        f"# {title}\n\n"
        "数据源目录生成的默认表页。\n\n"
        "## 字段\n\n"
        "```ground:table\n"
        f"{_dump_yaml(ground)}"
        "```\n"
    )
    return f"---\n{_dump_yaml(front)}---\n\n{body}"


def render_default_catalog_summary(
    rows: list[tuple[str, str, list[str]]],
    *,
    database: str,
    today: str,
) -> str:
    grouped: dict[str, list[tuple[str, str, list[str]]]] = defaultdict(list)
    for name, comment, labels in rows:
        prefix = name.split("_", 1)[0] if "_" in name else name
        grouped[prefix].append((name, comment, labels))
    lines = ["# 全库表骨架", "", "数据源目录生成的默认大纲。每表一行。", ""]
    for prefix in sorted(grouped):
        items = grouped[prefix]
        lines.append(f"## {prefix}（{len(items)}）")
        lines.append("")
        for name, comment, labels in items:
            hint = ", ".join(labels[:6])
            extra = f"({hint})" if hint else ""
            lines.append(f"- {name}: {comment}{extra}")
        lines.append("")
    front = {
        "type": "concept",
        "title": "全库表骨架",
        "page_key": "catalog_summary",
        "belong": "concepts",
        "status": "published",
        "recall": False,
        "aliases": ["Catalog Summary", "表目录", "库表一览"],
        "sources": [f"database_schema:{database}"] if database else ["database_schema"],
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    return f"---\n{_dump_yaml(front)}---\n\n" + "\n".join(lines).rstrip() + "\n"


def _table_slug(name: str) -> str:
    slug = _SLUG_CLEAN_RE.sub("_", str(name or "").strip().lower()).strip("_")
    if slug and slug[0].isdigit():
        slug = f"t_{slug}"
    return slug if PHYSICAL_SLUG_RE.match(slug) else ""


def _field_family(raw: str) -> str:
    text = str(raw or "").lower()
    if any(token in text for token in _TYPE_NUMBER):
        return "number"
    if any(token in text for token in _TYPE_TEMPORAL):
        return "temporal"
    if "bool" in text:
        return "boolean"
    return "string"


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def _datasource_database(ds: CoreDatasource) -> str:
    try:
        from apps.protocol import get_protocol_for_ds

        name = get_protocol_for_ds(ds).schema_namespace(ds)
        return str(name or "").strip()
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.debug("default wiki schema namespace skipped: %s", exc)
        return ""


def _import_brief(imported: ImportResult) -> dict[str, Any]:
    return {
        "corpus_id": imported.corpus_id,
        "generation": imported.generation,
        "status": imported.status,
        "failed_files": imported.failed_files[:20],
    }
