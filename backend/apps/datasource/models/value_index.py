"""Persisted value-to-field reverse index built at datasource sync."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class CoreValueIndex(SQLModel, table=True):
    """One indexed business value (enum code/label or instance) on a field."""

    __tablename__ = "core_value_index"
    __table_args__ = (
        UniqueConstraint(
            "ds_id",
            "table_name",
            "field_name",
            "val_type",
            "normalized_value",
            name="uq_core_value_index_slot",
        ),
        Index("ix_core_value_index_ds_norm", "ds_id", "normalized_value"),
        Index(
            "ix_core_value_index_ds_table_field",
            "ds_id",
            "table_name",
            "field_name",
        ),
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
    table_name: str = Field(sa_column=Column(String(128), nullable=False))
    field_name: str = Field(sa_column=Column(String(128), nullable=False))
    val_type: str = Field(sa_column=Column(String(32), nullable=False))
    raw_value: str = Field(sa_column=Column(Text, nullable=False))
    normalized_value: str = Field(sa_column=Column(Text, nullable=False))
    extra: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
