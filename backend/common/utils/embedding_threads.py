from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlmodel import Session

from common.core.db import engine

executor = ThreadPoolExecutor(max_workers=200)
# Background embedding jobs share the same SQLModel Session class as request DI.
session_maker = scoped_session(sessionmaker(bind=engine, class_=Session))


def run_save_terminology_embeddings(ids: list[int]):
    from apps.terminology.curd.terminology import save_embeddings

    executor.submit(save_embeddings, session_maker, ids)


def sync_terminology_embeddings():
    from apps.terminology.curd.terminology import run_sync_embeddings

    executor.submit(run_sync_embeddings, session_maker)


def run_save_data_training_embeddings(ids: list[int]):
    from apps.data_training.curd.data_training import save_embeddings

    executor.submit(save_embeddings, session_maker, ids)


def sync_data_training_embeddings():
    from apps.data_training.curd.data_training import run_sync_embeddings

    executor.submit(run_sync_embeddings, session_maker)


def run_save_table_embeddings(ids: list[int]):
    from apps.datasource.crud.table import save_table_embedding

    executor.submit(save_table_embedding, session_maker, ids)


def run_save_ds_embeddings(ids: list[int]):
    from apps.datasource.crud.table import save_ds_embedding

    executor.submit(save_ds_embedding, session_maker, ids)


def run_save_schema_vectors(ds_ids: list[int] | None):
    from apps.datasource.embedding.schema_index import sync_schema_vectors

    executor.submit(sync_schema_vectors, session_maker, ds_ids)


def sync_table_and_ds_embeddings():
    from apps.datasource.crud.table import run_sync_table_and_ds_embeddings

    executor.submit(run_sync_table_and_ds_embeddings, session_maker)
