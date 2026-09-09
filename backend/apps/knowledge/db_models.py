"""Wiki corpus storage models (pages, revisions, embeddings, bindings)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class WikiCorpus(SQLModel, table=True):
    __tablename__ = "wiki_corpus"
    __table_args__ = (
        UniqueConstraint("oid", "corpus_key", name="uq_wiki_corpus_oid_key"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    corpus_key: str = Field(max_length=64, nullable=False)
    name: str | None = Field(default=None, max_length=128)
    generation: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default="0")
    )
    page_count: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default="0")
    )
    published_count: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default="0")
    )
    draft_count: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default="0")
    )
    status: str = Field(
        default="indexing",
        sa_column=Column(String(32), nullable=False, server_default="indexing"),
    )
    embedded_chunks: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default="0")
    )
    failed_chunks: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default="0")
    )
    embed_error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    source_path: str | None = Field(default=None, max_length=512)
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class WikiPageRow(SQLModel, table=True):
    __tablename__ = "wiki_page"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id", "belong", "page_key", name="uq_wiki_page_corpus_belong_key"
        ),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    corpus_id: int = Field(
        sa_column=Column(
            BigInteger, ForeignKey("wiki_corpus.id", ondelete="CASCADE"), nullable=False
        )
    )
    belong: str = Field(
        default="",
        sa_column=Column(String(64), nullable=False, server_default=""),
    )
    page_key: str = Field(max_length=255, nullable=False)
    page_type: str = Field(max_length=32, nullable=False)
    title: str = Field(max_length=255, nullable=False)
    status: str = Field(max_length=32, nullable=False)
    databases: list[Any] = Field(
        default_factory=list,
        sa_column=Column(
            JSONB,
            nullable=False,
            server_default="[]",
        ),
    )
    aliases: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    anchors: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    body_md: str = Field(sa_column=Column(Text, nullable=False))
    content_sha: str = Field(max_length=64, nullable=False)
    page_disabled: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false"),
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class WikiPageRevision(SQLModel, table=True):
    __tablename__ = "wiki_page_revision"

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    page_id: int = Field(
        sa_column=Column(
            BigInteger, ForeignKey("wiki_page.id", ondelete="CASCADE"), nullable=False
        )
    )
    corpus_id: int = Field(
        sa_column=Column(
            BigInteger, ForeignKey("wiki_corpus.id", ondelete="CASCADE"), nullable=False
        )
    )
    revision_no: int = Field(sa_column=Column(Integer, nullable=False))
    status: str = Field(max_length=32, nullable=False)
    body_md: str = Field(sa_column=Column(Text, nullable=False))
    content_sha: str = Field(max_length=64, nullable=False)
    source: str = Field(
        default="import",
        sa_column=Column(String(32), nullable=False, server_default="import"),
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class WikiChunkEmbedding(SQLModel, table=True):
    __tablename__ = "wiki_chunk_embedding"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "belong",
            "page_key",
            "chunk_index",
            name="uq_wiki_chunk_corpus_belong_page_idx",
        ),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    corpus_id: int = Field(
        sa_column=Column(
            BigInteger, ForeignKey("wiki_corpus.id", ondelete="CASCADE"), nullable=False
        )
    )
    belong: str = Field(
        default="",
        sa_column=Column(String(64), nullable=False, server_default=""),
    )
    page_key: str = Field(max_length=255, nullable=False)
    chunk_index: int = Field(sa_column=Column(Integer, nullable=False))
    chunk_hash: str = Field(max_length=64, nullable=False)
    heading_path: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    model_key: str = Field(max_length=128, nullable=False)
    dimension: int = Field(sa_column=Column(Integer, nullable=False))
    vector: list[Any] = Field(sa_column=Column(JSONB, nullable=False))
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class WikiCorpusBinding(SQLModel, table=True):
    __tablename__ = "wiki_corpus_binding"
    __table_args__ = (
        UniqueConstraint("datasource_id", name="uq_wiki_corpus_binding_ds"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    datasource_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    corpus_id: int = Field(
        sa_column=Column(
            BigInteger, ForeignKey("wiki_corpus.id", ondelete="CASCADE"), nullable=False
        )
    )
    remap_databases: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="{}"),
    )
    enabled: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="true"),
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
