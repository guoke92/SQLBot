"""Schema vector documents — isolated from Wiki chunk embeddings."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlmodel import Field, SQLModel


class SchemaVector(SQLModel, table=True):
    """One embeddable schema doc: table, field, or confirmed relation."""

    __tablename__ = "schema_vector"
    __table_args__ = (
        UniqueConstraint("ds_id", "kind", "object_key", name="uq_schema_vector_doc"),
        Index("ix_schema_vector_ds_kind", "ds_id", "kind"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    ds_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    kind: str = Field(sa_column=Column(String(16), nullable=False))
    object_key: str = Field(sa_column=Column(String(512), nullable=False))
    table_name: str = Field(sa_column=Column(Text, nullable=False))
    field_name: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    peer_table: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    source_text: str = Field(sa_column=Column(Text, nullable=False))
    embedding: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    fingerprint: str | None = Field(
        default=None, sa_column=Column(String(64), nullable=True)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
