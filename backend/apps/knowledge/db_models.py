"""SQLModel tables for the Conversation knowledge plane."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, Identity, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import BigInteger, Field, SQLModel


class KnowledgeStaging(SQLModel, table=True):
    __tablename__ = "knowledge_staging"

    id: Optional[int] = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    kind: str = Field(sa_column=Column(String(32), nullable=False))
    status: str = Field(sa_column=Column(String(24), nullable=False))
    natural_key: str = Field(sa_column=Column(String(128), nullable=False))
    scope: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    trigger_id: str = Field(sa_column=Column(String(32), nullable=False))
    source_record_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    suggested_trust_tier: Optional[str] = Field(
        default=None, sa_column=Column(String(24), nullable=True)
    )
    quality_snapshot: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    conflict_with: Optional[list[int]] = Field(
        default=None, sa_column=Column(ARRAY(BigInteger), nullable=True)
    )
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False))
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))


class BusinessCaliber(SQLModel, table=True):
    __tablename__ = "business_caliber"

    id: Optional[int] = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False))
    version: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    datasource_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    advanced_application_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    label: str = Field(sa_column=Column(String(255), nullable=False))
    summary: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    contract_fragment: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    field_targets: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False),
    )
    synonyms: Optional[list[Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    trust_tier: str = Field(
        default="published", sa_column=Column(String(24), nullable=False)
    )
    certified: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False)
    )
    enabled: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    superseded_by: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    provenance: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    natural_key: str = Field(sa_column=Column(String(128), nullable=False))
    create_by: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    certify_by: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))


class KnowledgeLineageEvent(SQLModel, table=True):
    __tablename__ = "knowledge_lineage_event"

    event_id: str = Field(sa_column=Column(String(64), primary_key=True))
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False, index=True))
    asset_kind: str = Field(sa_column=Column(String(32), nullable=False))
    asset_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    asset_version: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True)
    )
    at: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    actor: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    action: str = Field(sa_column=Column(String(48), nullable=False))
    from_tier: Optional[str] = Field(
        default=None, sa_column=Column(String(24), nullable=True)
    )
    to_tier: Optional[str] = Field(
        default=None, sa_column=Column(String(24), nullable=True)
    )
    trigger_id: Optional[str] = Field(
        default=None, sa_column=Column(String(32), nullable=True)
    )
    refs: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    evidence_snapshot: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    decision: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    payload: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )


class KnowledgeCaptureJob(SQLModel, table=True):
    __tablename__ = "knowledge_capture_job"

    id: Optional[int] = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    record_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    status: str = Field(sa_column=Column(String(24), nullable=False))
    attempt: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    max_attempts: int = Field(default=3, sa_column=Column(Integer, nullable=False))
    lease_owner: Optional[str] = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    lease_until: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    snapshot: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    error: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    finished_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )


class ProcessEpisode(SQLModel, table=True):
    __tablename__ = "process_episode"

    id: Optional[int] = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False))
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    datasource_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    question_norm: str = Field(sa_column=Column(String(512), nullable=False))
    episode: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    trust_tier: str = Field(
        default="published", sa_column=Column(String(24), nullable=False)
    )
    enabled: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    source_record_id: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    provenance: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
