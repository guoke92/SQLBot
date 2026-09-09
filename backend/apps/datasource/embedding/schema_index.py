"""Isolated schema vector index (table / field / relation).

Wiki chunk embeddings live in ``wiki_chunk_embedding``. This module never
reads or writes that table. Query vectors may share the same embedding
*model*; the document space and storage are separate.

``schema_vector`` is the sole schema-fallback recall store. Sync (startup /
catalog change / admin trigger / lazy schedule) must keep it populated;
recall does not fall back to ``CoreTable.embedding``.
"""

from __future__ import annotations

import json
import threading
from copy import deepcopy
from datetime import datetime
from typing import Any

from sqlmodel import Session, col, func, select

from apps.ai_model.embedding import EmbeddingModelCache, has_compatible_dimension
from apps.datasource.embedding.recall import select_by_similarity
from apps.datasource.embedding.utils import cosine_similarity
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.models.schema_vector import SchemaVector
from apps.datasource.profiling.fingerprint import content_fingerprint
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

KIND_TABLE = "table"
KIND_FIELD = "field"
KIND_RELATION = "relation"

_job_lock = threading.Lock()
_sync_lock = threading.Lock()
_job: dict[str, Any] = {
    "status": "idle",
    "ds_ids": None,
    "phase": "",
    "message": "",
    "started_at": None,
    "finished_at": None,
    "table_docs": 0,
    "field_docs": 0,
    "relation_docs": 0,
    "embedded_docs": 0,
    "skipped_docs": 0,
    "error": None,
}


def get_schema_vector_job() -> dict[str, Any]:
    with _job_lock:
        return deepcopy(_job)


def _set_job(**kwargs: Any) -> None:
    with _job_lock:
        _job.update(kwargs)


def _iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def parse_vector(raw: Any) -> list[float] | None:
    if not raw:
        return None
    if isinstance(raw, list):
        try:
            return [float(item) for item in raw]
        except (TypeError, ValueError):
            return None
    try:
        stored = json.loads(raw) if isinstance(raw, str) else None
    except (TypeError, ValueError):
        return None
    if not isinstance(stored, list):
        return None
    try:
        return [float(item) for item in stored]
    except (TypeError, ValueError):
        return None


def field_rank_text(*, table_name: str, field: Any) -> str:
    name = str(getattr(field, "field_name", "") or "")
    ftype = str(getattr(field, "field_type", "") or "")
    comment = str(
        getattr(field, "custom_comment", None)
        or getattr(field, "field_comment", "")
        or ""
    ).strip()
    bits = [f"{table_name}.{name}"]
    if ftype:
        bits.append(ftype)
    if comment:
        bits.append(comment)
    return " ".join(bits)


def relation_rank_text(
    *,
    source_table: str,
    source_field: str,
    target_table: str,
    target_field: str,
    kind: str,
) -> str:
    return (
        f"{source_table}.{source_field} → {target_table}.{target_field} "
        f"({kind})"
    )


def _allowed_tables(access_scope: Any) -> set[str] | None:
    if access_scope is None:
        return None
    names = getattr(access_scope, "resource_names", None) or ()
    allowed = {str(name).strip() for name in names if str(name).strip()}
    return allowed or None


def _score_docs(
    docs: list[dict[str, Any]], query_embedding: list[float], *, top_count: int
) -> list[dict[str, Any]]:
    for doc in docs:
        stored = parse_vector(doc.get("embedding"))
        if not stored or not has_compatible_dimension(query_embedding, stored):
            doc["score"] = 0.0
            continue
        try:
            doc["score"] = float(cosine_similarity(query_embedding, stored))
        except Exception:
            doc["score"] = 0.0
    return select_by_similarity(
        docs,
        score_of=lambda item: float(item.get("score") or 0.0),
        threshold=float(settings.EMBEDDING_TABLE_SIMILARITY),
        top_count=max(1, int(top_count)),
        has_vector=lambda item: parse_vector(item.get("embedding")) is not None,
    )



def _docs_from_schema_vector(
    session: Session, *, ds_id: int, allowed: set[str] | None
) -> list[dict[str, Any]]:
    rows = list(session.exec(select(SchemaVector).where(SchemaVector.ds_id == ds_id)).all())
    docs: list[dict[str, Any]] = []
    for row in rows:
        name = str(row.table_name or "").strip()
        peer = str(row.peer_table or "").strip()
        if allowed is not None:
            if row.kind == KIND_RELATION:
                if name not in allowed and peer not in allowed:
                    continue
            elif name not in allowed:
                continue
        docs.append(
            {
                "kind": str(row.kind or ""),
                "object_key": str(row.object_key or ""),
                "table_name": name,
                "peer_table": peer or None,
                "embedding": row.embedding,
                "score": 0.0,
                "table_id": None,
            }
        )
    return docs


def _pick_tables(
    scored: list[dict[str, Any]], *, table_limit: int
) -> list[str]:
    from apps.knowledge.recall_kernel.tables import resolve_schema_vector_tables

    return [
        item.name
        for item in resolve_schema_vector_tables(scored, table_limit=table_limit)
    ]


def _live_tables_map(
    session: Session,
    *,
    llm_service: Any,
    table_names: list[str],
) -> dict[str, Any]:
    from apps.datasource.crud.datasource import get_table_obj_by_ds
    from apps.protocol import get_protocol_for_ds

    ds = getattr(llm_service, "ds", None)
    user = getattr(llm_service, "current_user", None)
    wanted = {str(name) for name in table_names}
    projection: dict[str, Any] = {}
    table_objs: list[Any] = []
    try:
        if ds is not None:
            table_objs = list(
                get_table_obj_by_ds(session=session, current_user=user, ds=ds) or []
            )
    except Exception as exc:
        SQLBotLogUtil.warning("schema vector live tables degraded: %s", exc)
        table_objs = []
    for obj in table_objs:
        table = getattr(obj, "table", None)
        name = str(getattr(table, "table_name", "") or "")
        if name not in wanted:
            continue
        projection[name] = {
            "comment": getattr(table, "table_comment", None) or "",
            "fields": [
                (
                    str(getattr(f, "field_name", "") or ""),
                    str(getattr(f, "field_type", "") or "string"),
                    str(
                        getattr(f, "custom_comment", None)
                        or getattr(f, "field_comment", "")
                        or ""
                    ),
                )
                for f in (getattr(obj, "fields", None) or [])
            ],
        }
    if projection:
        return projection
    if ds is None:
        return {}
    tables = list(
        session.exec(
            select(CoreTable).where(
                CoreTable.ds_id == int(ds.id),
                CoreTable.checked == True,  # noqa: E712
                CoreTable.table_name.in_(list(wanted)),
            )
        ).all()
    )
    fields = list(
        session.exec(
            select(CoreField).where(
                CoreField.ds_id == int(ds.id),
                CoreField.checked == True,  # noqa: E712
                CoreField.table_id.in_([int(t.id) for t in tables if t.id]),
            )
        ).all()
    )
    by_table: dict[int, list[CoreField]] = {}
    for field in fields:
        by_table.setdefault(int(field.table_id), []).append(field)
    proto = get_protocol_for_ds(ds)
    for table in tables:
        name = str(table.table_name or "")
        if name not in wanted:
            continue
        projection[name] = {
            "comment": getattr(table, "table_comment", None)
            or proto.table_prompt_label(ds, name)
            or name,
            "fields": [
                (
                    str(f.field_name or ""),
                    str(f.field_type or "string"),
                    str(getattr(f, "custom_comment", None) or f.field_comment or ""),
                )
                for f in by_table.get(int(table.id), [])
            ],
        }
    return projection


def _render_schema(
    session: Session,
    *,
    llm_service: Any,
    table_names: list[str],
) -> tuple[str, list[str]]:
    from apps.knowledge.recall_kernel.render import render_schema

    ds = getattr(llm_service, "ds", None)
    if ds is None or not table_names:
        return "", []
    live = _live_tables_map(session, llm_service=llm_service, table_names=table_names)
    kept = [name for name in table_names if name in live]
    if not kept:
        return "", []
    relations = _relation_lines(session, ds_id=int(ds.id), table_names=kept)
    schema = render_schema(
        kept,
        live_tables=live,
        confirmed_relations=relations,
    )
    return schema, kept


def _relation_lines(session: Session, *, ds_id: int, table_names: list[str]) -> list[str]:
    block = _relation_block(session, ds_id=ds_id, table_names=table_names)
    lines: list[str] = []
    for raw in str(block or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("【"):
            continue
        if "=" in line and "." in line:
            left, _sep, right = line.partition("=")
            left = left.strip()
            right = right.strip()
            if left and right:
                lines.append(f"关联: {left} → {right}")
                continue
        if line.startswith("关联:"):
            lines.append(line)
    return lines


def _relation_block(session: Session, *, ds_id: int, table_names: list[str]) -> str:
    if not table_names:
        return ""
    try:
        from apps.datasource.profiling.models import RelationKind, RelationStatus
        from apps.datasource.profiling.service import get_published_relations

        tables = list(session.exec(select(CoreTable).where(
                    CoreTable.ds_id == ds_id,
                    CoreTable.table_name.in_(table_names),
                )).all())
        id_by_name = {
            str(table.table_name): int(table.id)
            for table in tables
            if table.id is not None
        }
        name_by_id = {int(table.id): str(table.table_name) for table in tables if table.id}
        published = get_published_relations(
            session,
            ds_id=ds_id,
            table_ids=list(id_by_name.values()),
            statuses=[RelationStatus.CONFIRMED.value],
        )
        equi = [
            row
            for row in published
            if row.kind in (RelationKind.EQUI_JOIN.value, RelationKind.HIERARCHY.value)
        ]
        if not equi:
            return ""
        field_ids = {int(row.source_field_id) for row in equi} | {
            int(row.target_field_id) for row in equi
        }
        field_map = {
            int(field.id): str(field.field_name)
            for field in list(session.exec(select(CoreField).where(CoreField.id.in_(list(field_ids)))).all())
            if field.id is not None
        }
        lines = ["【Confirmed relations】\n"]
        for rel in equi:
            src_t = name_by_id.get(int(rel.source_table_id)) or ""
            dst_t = name_by_id.get(int(rel.target_table_id)) or ""
            src_f = field_map.get(int(rel.source_field_id)) or ""
            dst_f = field_map.get(int(rel.target_field_id)) or ""
            if not (src_t and dst_t and src_f and dst_f):
                continue
            lines.append(f"{src_t}.{src_f}={dst_t}.{dst_f}\n")
        if len(lines) == 1:
            return ""
        return "".join(lines)
    except Exception as exc:
        SQLBotLogUtil.warning("schema vector relation render skipped: %s", exc)
        return ""


def recall_schema_context(
    llm_service: Any,
    query: str,
    *,
    access_scope: Any = None,
    table_limit: int = 4,
    session: Session | None = None,
) -> dict[str, Any]:
    """Rank ``schema_vector`` docs for ``query`` and render local catalog text.

    Sole schema-fallback store — does not read ``CoreTable.embedding``.
    Never queries the business datasource for sample rows.
    """
    empty = {
        "knowledge_text": "",
        "tables": [],
        "schema_text": "",
        "backend": "schema_vector",
        "page_keys": [],
        "hit_count": 0,
    }
    ds = getattr(llm_service, "ds", None)
    ds_id = getattr(ds, "id", None)
    clean = str(query or "").strip()
    if ds_id is None or not clean:
        return empty
    if not settings.TABLE_EMBEDDING_ENABLED:
        return empty

    def _run(sess: Session) -> dict[str, Any]:
        allowed = _allowed_tables(access_scope)
        try:
            stored = _docs_from_schema_vector(sess, ds_id=int(ds_id), allowed=allowed)
        except Exception as exc:
            SQLBotLogUtil.warning("schema_vector store unavailable: %s", exc)
            stored = []
        if not stored:
            return empty
        query_embedding = EmbeddingModelCache.embed_query(clean)
        field_budget = max(int(table_limit) * 3, int(settings.TABLE_EMBEDDING_COUNT))
        table_hits = _score_docs(
            [doc for doc in stored if doc.get("kind") == KIND_TABLE],
            query_embedding,
            top_count=max(int(table_limit), int(settings.TABLE_EMBEDDING_COUNT)),
        )
        field_hits = _score_docs(
            [doc for doc in stored if doc.get("kind") == KIND_FIELD],
            query_embedding,
            top_count=field_budget,
        )
        relation_hits = _score_docs(
            [doc for doc in stored if doc.get("kind") == KIND_RELATION],
            query_embedding,
            top_count=max(int(table_limit), 4),
        )
        names = _pick_tables(
            [*table_hits, *field_hits, *relation_hits],
            table_limit=max(int(table_limit), 4),
        )
        schema_text, kept = _render_schema(
            sess,
            llm_service=llm_service,
            table_names=names,
        )
        chat_question = getattr(llm_service, "chat_question", None)
        if chat_question is not None:
            chat_question.db_schema = schema_text
            chat_question.sample_data = ""
        llm_service.table_name_list = list(kept)
        return {
            "knowledge_text": "",
            "tables": kept,
            "schema_text": schema_text,
            "backend": "schema_vector",
            "page_keys": [],
            "hit_count": len(kept),
            "table_evidence": {name: [] for name in kept},
        }

    if session is not None:
        return _run(session)
    from apps.conversation.session import session_scope

    with session_scope() as sess:
        return _run(sess)


def catalog_field_index(
    session: Session, *, ds_id: int, access_scope: Any = None
) -> dict[str, set[str]]:
    """table_name → field names for grounding clarification options."""
    allowed = _allowed_tables(access_scope)
    tables = list(
        session.exec(select(CoreTable).where(
                CoreTable.ds_id == ds_id,
                CoreTable.checked == True,  # noqa: E712
            )).all())
    id_to_name: dict[int, str] = {}
    index: dict[str, set[str]] = {}
    for table in tables:
        name = str(table.table_name or "").strip()
        if not name or table.id is None:
            continue
        if allowed is not None and name not in allowed:
            continue
        id_to_name[int(table.id)] = name
        index[name] = set()
    if not id_to_name:
        return {}
    fields = list(session.exec(select(CoreField).where(
            CoreField.ds_id == ds_id,
            CoreField.checked == True,  # noqa: E712
            CoreField.table_id.in_(list(id_to_name)),
        )).all())
    for field in fields:
        table_name = id_to_name.get(int(field.table_id))
        fname = str(field.field_name or "").strip()
        if table_name and fname:
            index.setdefault(table_name, set()).add(fname)
    return index


def sync_schema_vectors(session_maker: Any, ds_ids: list[int] | None = None) -> None:
    """Upsert table/field/relation docs into ``schema_vector`` (sole recall store).

    Table vectors reuse ``CoreTable.embedding`` when its RANK fingerprint matches;
    otherwise tables are embedded with fields/relations. Recall never reads
    ``CoreTable.embedding`` directly.
    """
    if not settings.TABLE_EMBEDDING_ENABLED:
        _set_job(
            status="failed",
            phase="disabled",
            message="TABLE_EMBEDDING_ENABLED is false",
            error="TABLE_EMBEDDING_ENABLED is false",
            finished_at=_iso_now(),
        )
        return
    if not _sync_lock.acquire(blocking=False):
        SQLBotLogUtil.info("sync_schema_vectors skipped: another job is running")
        return
    scoped_ids = [int(item) for item in ds_ids] if ds_ids else None
    _set_job(
        status="running",
        ds_ids=scoped_ids,
        phase="prepare",
        message="loading catalog",
        started_at=_iso_now(),
        finished_at=None,
        table_docs=0,
        field_docs=0,
        relation_docs=0,
        embedded_docs=0,
        skipped_docs=0,
        error=None,
    )
    session = session_maker()
    try:
        stmt = select(CoreTable).where(CoreTable.checked == True)  # noqa: E712
        if scoped_ids:
            stmt = stmt.where(CoreTable.ds_id.in_(scoped_ids))
        tables = list(session.exec(stmt).all())
        if not tables:
            _set_job(
                status="succeeded",
                phase="done",
                message="no checked tables",
                finished_at=_iso_now(),
            )
            return
        table_ids = [int(table.id) for table in tables if table.id is not None]
        fields = list(
            session.exec(
                select(CoreField).where(
                    CoreField.checked == True,  # noqa: E712
                    CoreField.table_id.in_(table_ids),
                )
            ).all()
        )
        fields_by_table: dict[int, list[CoreField]] = {}
        for field in fields:
            fields_by_table.setdefault(int(field.table_id), []).append(field)

        pending_text: list[tuple[str, int, str, str, str, str | None, str | None]] = []
        now = datetime.utcnow()
        table_docs = 0
        _set_job(phase="tables", message=f"upserting {len(tables)} tables")
        for table in tables:
            if table.id is None:
                continue
            ds_id = int(table.ds_id)
            name = str(table.table_name or "").strip()
            if not name:
                continue
            from apps.datasource.schema_text import (
                SchemaTextPurpose,
                render_table_schema_text,
            )

            source = render_table_schema_text(
                session,
                table=table,
                fields=list(fields_by_table.get(int(table.id), [])),
                purpose=SchemaTextPurpose.RANK,
            )
            fp = content_fingerprint(source)
            table_docs += 1
            prior_fp = getattr(table, "embedding_fingerprint", None)
            if prior_fp == fp and parse_vector(table.embedding):
                _upsert_doc(
                    session,
                    ds_id=ds_id,
                    kind=KIND_TABLE,
                    object_key=name,
                    table_name=name,
                    field_name=None,
                    peer_table=None,
                    source_text=source,
                    fingerprint=fp,
                    embedding=table.embedding,
                    now=now,
                )
            else:
                pending_text.append(
                    (
                        KIND_TABLE,
                        ds_id,
                        name,
                        name,
                        source,
                        None,
                        None,
                    )
                )
            for field in fields_by_table.get(int(table.id), []):
                fname = str(field.field_name or "").strip()
                if not fname:
                    continue
                text = field_rank_text(table_name=name, field=field)
                pending_text.append(
                    (
                        KIND_FIELD,
                        ds_id,
                        f"{name}.{fname}",
                        name,
                        text,
                        fname,
                        None,
                    )
                )
        _set_job(phase="relations", message="collecting confirmed relations", table_docs=table_docs)
        pending_text.extend(_pending_relations(session, tables))
        field_docs = sum(1 for item in pending_text if item[0] == KIND_FIELD)
        relation_docs = sum(1 for item in pending_text if item[0] == KIND_RELATION)
        # Persist copied table docs first; pending embeds commit in the next step.
        session.commit()
        _set_job(
            phase="embed",
            message=f"embedding {len(pending_text)} docs",
            field_docs=field_docs,
            relation_docs=relation_docs,
        )
        try:
            embedded, skipped = _embed_pending(session, pending_text, now=now)
            session.commit()
        except Exception as embed_exc:
            session.rollback()
            SQLBotLogUtil.exception("schema vector embed failed")
            _set_job(
                status="failed",
                phase="embed_error",
                message="partial schema_vector commit; embed failed",
                table_docs=table_docs,
                field_docs=field_docs,
                relation_docs=relation_docs,
                error=str(embed_exc),
                finished_at=_iso_now(),
            )
            return
        _set_job(
            status="succeeded",
            phase="done",
            message="schema vector sync finished",
            table_docs=table_docs,
            field_docs=field_docs,
            relation_docs=relation_docs,
            embedded_docs=embedded,
            skipped_docs=skipped,
            finished_at=_iso_now(),
        )
    except Exception as exc:
        SQLBotLogUtil.exception("sync_schema_vectors failed")
        session.rollback()
        _set_job(
            status="failed",
            phase="error",
            message="schema vector sync failed",
            error=str(exc),
            finished_at=_iso_now(),
        )
    finally:
        session_maker.remove()
        _sync_lock.release()


def list_schema_vector_status(
    session: Session, *, oid: int | None = None, ds_id: int | None = None
) -> list[dict[str, Any]]:
    """Per-datasource catalog vs schema_vector coverage snapshot."""
    ds_stmt = select(CoreDatasource)
    if oid is not None:
        ds_stmt = ds_stmt.where(CoreDatasource.oid == int(oid))
    if ds_id is not None:
        ds_stmt = ds_stmt.where(CoreDatasource.id == int(ds_id))
    datasources = list(session.exec(ds_stmt.order_by(col(CoreDatasource.id))).all())
    if not datasources:
        return []

    ds_ids = [int(ds.id) for ds in datasources if ds.id is not None]
    table_rows = list(
        session.exec(
            select(
                CoreTable.ds_id,
                func.count(CoreTable.id),
                func.count(CoreTable.embedding),
            )
            .where(
                CoreTable.ds_id.in_(ds_ids),
                CoreTable.checked == True,  # noqa: E712
            )
            .group_by(CoreTable.ds_id)
        ).all()
    )
    table_map = {
        int(row[0]): {"checked_tables": int(row[1] or 0), "table_embeddings": int(row[2] or 0)}
        for row in table_rows
    }

    vector_rows = list(
        session.exec(
            select(
                SchemaVector.ds_id,
                SchemaVector.kind,
                func.count(SchemaVector.id),
                func.count(SchemaVector.embedding),
                func.max(SchemaVector.update_time),
            )
            .where(SchemaVector.ds_id.in_(ds_ids))
            .group_by(SchemaVector.ds_id, SchemaVector.kind)
        ).all()
    )
    vector_map: dict[int, dict[str, Any]] = {}
    for row in vector_rows:
        entry = vector_map.setdefault(
            int(row[0]),
            {
                "docs": 0,
                "embedded_docs": 0,
                "tables": 0,
                "fields": 0,
                "relations": 0,
                "update_time": None,
            },
        )
        kind = str(row[1] or "")
        count = int(row[2] or 0)
        embedded = int(row[3] or 0)
        entry["docs"] += count
        entry["embedded_docs"] += embedded
        if kind == KIND_TABLE:
            entry["tables"] = count
        elif kind == KIND_FIELD:
            entry["fields"] = count
        elif kind == KIND_RELATION:
            entry["relations"] = count
        updated = row[4]
        if updated is not None:
            iso = updated.isoformat(timespec="seconds")
            prior = entry.get("update_time")
            if prior is None or iso > prior:
                entry["update_time"] = iso

    enabled = bool(settings.TABLE_EMBEDDING_ENABLED)
    job = get_schema_vector_job()
    running_ids = set(job.get("ds_ids") or []) if job.get("status") == "running" else set()
    rows: list[dict[str, Any]] = []
    for ds in datasources:
        if ds.id is None:
            continue
        tid = int(ds.id)
        catalog = table_map.get(tid, {"checked_tables": 0, "table_embeddings": 0})
        vectors = vector_map.get(
            tid,
            {
                "docs": 0,
                "embedded_docs": 0,
                "tables": 0,
                "fields": 0,
                "relations": 0,
                "update_time": None,
            },
        )
        ready = (
            enabled
            and int(catalog["checked_tables"]) > 0
            and int(vectors["tables"]) >= int(catalog["checked_tables"])
            and int(vectors["embedded_docs"]) > 0
        )
        if not enabled:
            state = "disabled"
        elif job.get("status") == "running" and (not running_ids or tid in running_ids):
            state = "indexing"
        elif int(catalog["checked_tables"]) == 0:
            state = "empty"
        elif ready:
            state = "ready"
        elif int(vectors["docs"]) == 0:
            state = "missing"
        else:
            state = "partial"
        rows.append(
            {
                "ds_id": tid,
                "name": ds.name,
                "enabled": enabled,
                "state": state,
                "checked_tables": catalog["checked_tables"],
                "table_embeddings": catalog["table_embeddings"],
                "schema_docs": vectors["docs"],
                "schema_embedded": vectors["embedded_docs"],
                "schema_tables": vectors["tables"],
                "schema_fields": vectors["fields"],
                "schema_relations": vectors["relations"],
                "update_time": vectors["update_time"],
            }
        )
    return rows


def _pending_relations(
    session: Session, tables: list[CoreTable]
) -> list[tuple[str, int, str, str, str, str | None, str | None]]:
    pending: list[tuple[str, int, str, str, str, str | None, str | None]] = []
    try:
        from apps.datasource.profiling.models import RelationStatus
        from apps.datasource.profiling.service import get_published_relations

        by_ds: dict[int, list[CoreTable]] = {}
        for table in tables:
            by_ds.setdefault(int(table.ds_id), []).append(table)
        for ds_id, group in by_ds.items():
            name_by_id = {
                int(table.id): str(table.table_name)
                for table in group
                if table.id is not None
            }
            rels = get_published_relations(
                session,
                ds_id=ds_id,
                table_ids=list(name_by_id),
                statuses=[RelationStatus.CONFIRMED.value],
            )
            field_ids = {int(row.source_field_id) for row in rels} | {
                int(row.target_field_id) for row in rels
            }
            if not field_ids:
                continue
            field_map = {
                int(field.id): str(field.field_name)
                for field in list(session.exec(select(CoreField).where(CoreField.id.in_(list(field_ids)))).all())
                if field.id is not None
            }
            for rel in rels:
                src_t = name_by_id.get(int(rel.source_table_id)) or ""
                dst_t = name_by_id.get(int(rel.target_table_id)) or ""
                src_f = field_map.get(int(rel.source_field_id)) or ""
                dst_f = field_map.get(int(rel.target_field_id)) or ""
                if not (src_t and dst_t and src_f and dst_f):
                    continue
                key = f"{src_t}.{src_f}>{dst_t}.{dst_f}:{rel.kind}"
                text = relation_rank_text(
                    source_table=src_t,
                    source_field=src_f,
                    target_table=dst_t,
                    target_field=dst_f,
                    kind=str(rel.kind),
                )
                pending.append(
                    (KIND_RELATION, ds_id, key, src_t, text, src_f, dst_t)
                )
    except Exception as exc:
        SQLBotLogUtil.warning("schema vector relation sync skipped: %s", exc)
    return pending


def _embed_pending(
    session: Session,
    pending: list[tuple[str, int, str, str, str, str | None, str | None]],
    *,
    now: datetime,
) -> tuple[int, int]:
    if not pending:
        return 0, 0
    to_embed: list[int] = []
    texts: list[str] = []
    skipped = 0
    for index, item in enumerate(pending):
        kind, ds_id, object_key, table_name, text, field_name, peer = item
        fp = content_fingerprint(text)
        existing = session.exec(select(SchemaVector).where(
                SchemaVector.ds_id == ds_id,
                SchemaVector.kind == kind,
                SchemaVector.object_key == object_key,
            )).first()
        if (
            existing is not None
            and existing.fingerprint == fp
            and parse_vector(existing.embedding)
        ):
            skipped += 1
            continue
        to_embed.append(index)
        texts.append(text)
    if not texts:
        return 0, skipped
    model = EmbeddingModelCache.get_model()
    vectors = model.embed_documents(texts)
    for offset, index in enumerate(to_embed):
        kind, ds_id, object_key, table_name, text, field_name, peer = pending[index]
        raw = vectors[offset] if offset < len(vectors) else None
        embedding = json.dumps(raw) if raw else None
        _upsert_doc(
            session,
            ds_id=ds_id,
            kind=kind,
            object_key=object_key,
            table_name=table_name,
            field_name=field_name,
            peer_table=peer,
            source_text=text,
            fingerprint=content_fingerprint(text),
            embedding=embedding,
            now=now,
        )
    return len(to_embed), skipped


def _upsert_doc(
    session: Session,
    *,
    ds_id: int,
    kind: str,
    object_key: str,
    table_name: str,
    field_name: str | None,
    peer_table: str | None,
    source_text: str,
    fingerprint: str,
    embedding: str | None,
    now: datetime,
) -> None:
    row = session.exec(select(SchemaVector).where(
            SchemaVector.ds_id == ds_id,
            SchemaVector.kind == kind,
            SchemaVector.object_key == object_key,
        )).first()
    if row is None:
        session.add(
            SchemaVector(
                ds_id=ds_id,
                kind=kind,
                object_key=object_key,
                table_name=table_name,
                field_name=field_name,
                peer_table=peer_table,
                source_text=source_text,
                fingerprint=fingerprint,
                embedding=embedding,
                update_time=now,
            )
        )
        return
    row.source_text = source_text
    row.fingerprint = fingerprint
    row.table_name = table_name
    row.field_name = field_name
    row.peer_table = peer_table
    if embedding:
        row.embedding = embedding
    row.update_time = now
    session.add(row)


def schedule_schema_vector_sync(ds_id: int | None) -> None:
    if ds_id is None:
        return
    try:
        start_schema_vector_sync([int(ds_id)])
    except Exception as exc:
        SQLBotLogUtil.debug("schema vector sync not scheduled: %s", exc)


def start_schema_vector_sync(ds_ids: list[int] | None = None) -> dict[str, Any]:
    """Queue a background sync; returns current job snapshot.

    ``ds_ids=None`` or empty list means all datasources.
    """
    job = get_schema_vector_job()
    if job.get("status") == "running":
        return {**job, "accepted": False, "reason": "busy"}
    from common.utils.embedding_threads import run_save_schema_vectors

    scoped = [int(item) for item in ds_ids] if ds_ids else None
    # Mark running early so concurrent clicks see busy before the worker starts.
    _set_job(
        status="running",
        ds_ids=scoped,
        phase="queued",
        message="queued",
        started_at=_iso_now(),
        finished_at=None,
        table_docs=0,
        field_docs=0,
        relation_docs=0,
        embedded_docs=0,
        skipped_docs=0,
        error=None,
    )
    run_save_schema_vectors(scoped)
    return {**get_schema_vector_job(), "accepted": True, "reason": None}
