"""Durable store for the single conversation extract key."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Identity, String
from sqlmodel import Field, SQLModel


class ConversationExtractKey(SQLModel, table=True):
    __tablename__ = "conversation_extract_key"

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    key_prefix: str = Field(max_length=16, nullable=False)
    key_hash: str = Field(max_length=64, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    created_by: int = Field(sa_column=Column(BigInteger, nullable=False))
