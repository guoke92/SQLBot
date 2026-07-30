from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlmodel import Field, SQLModel


class DictionaryStatus(str, Enum):
    EMPTY = "EMPTY"
    READY = "READY"
    STALE = "STALE"
    DISABLED = "DISABLED"


class DictionaryFieldConfig(SQLModel, table=True):
    __tablename__ = "dictionary_field_config"
    __table_args__ = (
        UniqueConstraint("oid", "ds_id", "field_id", name="uq_dictionary_field_scope"),
        Index("ix_dictionary_field_ds_table", "ds_id", "table_id"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    ds_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    table_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    field_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    enabled: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    max_values: int = Field(default=500, sa_column=Column(Integer, nullable=False))
    schema_fingerprint: str = Field(sa_column=Column(String(64), nullable=False))
    status: DictionaryStatus = Field(
        default=DictionaryStatus.DISABLED,
        sa_column=Column(String(24), nullable=False),
    )
    published_generation: int = Field(
        default=0, sa_column=Column(BigInteger, nullable=False)
    )
    revision: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    value_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    last_synced_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    last_error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class DictionaryValue(SQLModel, table=True):
    __tablename__ = "dictionary_value"
    __table_args__ = (
        UniqueConstraint(
            "config_id",
            "generation",
            "normalized_value",
            name="uq_dictionary_value_generation",
        ),
        Index(
            "ix_dictionary_value_config_generation",
            "config_id",
            "generation",
        ),
        Index("ix_dictionary_value_normalized", "normalized_value"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    config_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("dictionary_field_config.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    value: str = Field(sa_column=Column(Text, nullable=False))
    normalized_value: str = Field(sa_column=Column(Text, nullable=False))
    generation: int = Field(sa_column=Column(BigInteger, nullable=False))
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class DictionaryConfigUpdate(BaseModel):
    enabled: bool | None = None
    max_values: int | None = PydanticField(default=None, ge=1, le=5000)


class DictionaryConfigCreate(BaseModel):
    field_id: int
    enabled: bool = True
    max_values: int = PydanticField(default=500, ge=1, le=5000)


class DictionaryFieldOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    configured: bool
    ds_id: int
    table_id: int
    field_id: int
    enabled: bool
    max_values: int
    status: DictionaryStatus
    published_generation: int
    value_count: int
    last_synced_at: datetime | None = None
    last_error: str | None = None
    table_name: str
    table_comment: str | None = None
    field_name: str
    field_type: str | None = None
    field_comment: str | None = None


class DictionaryRefreshResult(BaseModel):
    id: int
    status: DictionaryStatus
    value_count: int = 0
    error: str | None = None
