import json
import time
import traceback

from sqlalchemy import and_, select, update

from apps.ai_model.embedding import EmbeddingModelCache
from apps.datasource.schema_text import SchemaTextPurpose, render_table_schema_text
from common.core.config import settings
from common.core.deps import SessionDep
from common.utils.utils import SQLBotLogUtil

from ..models.datasource import CoreDatasource, CoreField, CoreTable


def delete_table_by_ds_id(session: SessionDep, id: int):
    session.query(CoreTable).filter(CoreTable.ds_id == id).delete(
        synchronize_session=False
    )
    session.commit()


def get_tables_by_ds_id(session: SessionDep, id: int):
    return (
        session.query(CoreTable)
        .filter(CoreTable.ds_id == id)
        .order_by(CoreTable.table_name.asc())
        .all()
    )


def _needs_embedding_refresh(value: str | None, active_dimension: int) -> bool:
    if not value:
        return True
    try:
        vector = json.loads(value)
    except (TypeError, ValueError):
        return True
    return not isinstance(vector, list) or len(vector) != active_dimension


def run_sync_table_and_ds_embeddings(session_maker):
    """Refresh schema vectors missing from the active embedding space."""
    try:
        if not settings.TABLE_EMBEDDING_ENABLED:
            return

        active_dimension = EmbeddingModelCache.get_dimension()
        session = session_maker()

        SQLBotLogUtil.info("get tables")
        table_rows = session.execute(
            select(
                CoreTable.id,
                CoreTable.embedding,
                CoreTable.embedding_fingerprint,
            )
        ).all()
        results = [
            table_id
            for table_id, embedding, fingerprint in table_rows
            if _needs_embedding_refresh(embedding, active_dimension) or not fingerprint
        ]
        SQLBotLogUtil.info("table result: " + str(len(results)))
        save_table_embedding(session_maker, results)

        SQLBotLogUtil.info("get datasource")
        datasource_rows = session.execute(
            select(
                CoreDatasource.id,
                CoreDatasource.embedding,
                CoreDatasource.embedding_fingerprint,
            )
        ).all()
        ds_results = [
            datasource_id
            for datasource_id, embedding, fingerprint in datasource_rows
            if _needs_embedding_refresh(embedding, active_dimension) or not fingerprint
        ]
        SQLBotLogUtil.info("datasource result: " + str(len(ds_results)))
        save_ds_embedding(session_maker, ds_results)
    except Exception:
        traceback.print_exc()
    finally:
        session_maker.remove()


def _checked_fields(session, table_id: int) -> list[CoreField]:
    return (
        session.query(CoreField)
        .filter(CoreField.table_id == table_id, CoreField.checked == True)  # noqa: E712
        .order_by(CoreField.field_index.asc())
        .all()
    )


def _rank_table_text(session, table: CoreTable, fields: list[CoreField]) -> str:
    """Structural RANK text for table vectors (see schema_text contract)."""
    return render_table_schema_text(
        session,
        table=table,
        fields=fields,
        purpose=SchemaTextPurpose.RANK,
    )


def save_table_embedding(session_maker, ids: list[int]):
    """Embed tables from RANK schema text; skip when content fingerprint matches."""
    if not settings.TABLE_EMBEDDING_ENABLED:
        return

    if not ids or len(ids) == 0:
        return
    try:
        from apps.datasource.profiling.fingerprint import content_fingerprint

        SQLBotLogUtil.info("start table embedding")
        start_time = time.time()
        model = EmbeddingModelCache.get_model()
        active_dimension = EmbeddingModelCache.get_dimension()
        session = session_maker()
        refreshed = 0
        skipped = 0
        for _id in ids:
            table = session.query(CoreTable).filter(CoreTable.id == _id).first()
            if table is None:
                continue
            fields = _checked_fields(session, int(table.id))
            schema_table = _rank_table_text(session, table, fields)
            fp = content_fingerprint(schema_table)
            prior_fp = getattr(table, "embedding_fingerprint", None)
            if (
                prior_fp
                and prior_fp == fp
                and not _needs_embedding_refresh(table.embedding, active_dimension)
            ):
                skipped += 1
                continue

            emb = json.dumps(model.embed_query(schema_table))
            stmt = (
                update(CoreTable)
                .where(and_(CoreTable.id == _id))
                .values(embedding=emb, embedding_fingerprint=fp)
            )
            session.execute(stmt)
            session.commit()
            refreshed += 1

        end_time = time.time()
        SQLBotLogUtil.info(
            "table embedding finished in: "
            + str(end_time - start_time)
            + f" seconds (refreshed={refreshed}, skipped={skipped})"
        )
    except Exception:
        traceback.print_exc()
    finally:
        session_maker.remove()


def save_ds_embedding(session_maker, ids: list[int]):
    """Embed datasources from RANK table texts; fingerprint-skip no-ops."""
    if not settings.TABLE_EMBEDDING_ENABLED:
        return

    if not ids or len(ids) == 0:
        return
    try:
        from apps.datasource.profiling.fingerprint import content_fingerprint

        SQLBotLogUtil.info("start datasource embedding")
        start_time = time.time()
        model = EmbeddingModelCache.get_model()
        active_dimension = EmbeddingModelCache.get_dimension()
        session = session_maker()
        refreshed = 0
        skipped = 0
        for _id in ids:
            ds = session.query(CoreDatasource).filter(CoreDatasource.id == _id).first()
            if ds is None:
                continue
            parts = [f"{ds.name}, {ds.description or ''}"]
            tables = (
                session.query(CoreTable)
                .filter(
                    CoreTable.ds_id == ds.id,
                    CoreTable.checked == True,  # noqa: E712
                )
                .order_by(CoreTable.table_name.asc())
                .all()
            )
            for table in tables:
                fields = _checked_fields(session, int(table.id))
                parts.append(
                    render_table_schema_text(
                        session,
                        table=table,
                        fields=fields,
                        purpose=SchemaTextPurpose.RANK,
                    ).rstrip()
                )
            schema_table = "\n".join(parts) + "\n"
            fp = content_fingerprint(schema_table)
            prior_fp = getattr(ds, "embedding_fingerprint", None)
            if (
                prior_fp
                and prior_fp == fp
                and not _needs_embedding_refresh(ds.embedding, active_dimension)
            ):
                skipped += 1
                continue

            emb = json.dumps(model.embed_query(schema_table))
            stmt = (
                update(CoreDatasource)
                .where(and_(CoreDatasource.id == _id))
                .values(embedding=emb, embedding_fingerprint=fp)
            )
            session.execute(stmt)
            session.commit()
            refreshed += 1

        end_time = time.time()
        SQLBotLogUtil.info(
            "datasource embedding finished in: "
            + str(end_time - start_time)
            + f" seconds (refreshed={refreshed}, skipped={skipped})"
        )
    except Exception:
        traceback.print_exc()
    finally:
        session_maker.remove()
