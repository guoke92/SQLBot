"""SQLModel tables for the knowledge plane."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import BigInteger, Field, SQLModel


class KnowledgeAsset(SQLModel, table=True):
    __tablename__ = "knowledge_asset"

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    kind: str = Field(
        sa_column=Column(String(32), nullable=False, comment="caliber|rule")
    )
    natural_key: str = Field(sa_column=Column(String(128), nullable=False))
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False))
    version: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    superseded_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    datasource_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    assistant_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    label: str = Field(sa_column=Column(String(255), nullable=False))
    summary: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    trust_tier: str = Field(
        default="published",
        sa_column=Column(String(24), nullable=False, comment="staged|published|trusted|certified"),
    )
    certified: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False)
    )
    enabled: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    valid_from: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    valid_to: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    provenance: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    embedding_fingerprint: str | None = Field(
        default=None, sa_column=Column(String(64), nullable=True)
    )
    create_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    certify_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    certify_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))


class KnowledgeSchemaRef(SQLModel, table=True):
    __tablename__ = "knowledge_schema_ref"

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    asset_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    asset_kind: str = Field(sa_column=Column(String(32), nullable=False))
    datasource_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    table_name: str = Field(sa_column=Column(String(255), nullable=False))
    field_name: str | None = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
    table_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    field_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )


class KnowledgeEvidence(SQLModel, table=True):
    __tablename__ = "knowledge_evidence"

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    event_key: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    asset_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    asset_kind: str = Field(sa_column=Column(String(32), nullable=False))
    natural_key: str | None = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    signal_kind: str = Field(
        sa_column=Column(
            String(32), nullable=False,
            comment="reproduce|apply_outcome|turn_feedback|usage",
        )
    )
    record_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    fact: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))


class KnowledgeEpisode(SQLModel, table=True):
    __tablename__ = "knowledge_episode"

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    datasource_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    record_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    question_norm: str = Field(sa_column=Column(String(512), nullable=False))
    episode: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    provenance: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))


class KnowledgeStaging(SQLModel, table=True):
    __tablename__ = "knowledge_staging"

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    kind: str = Field(sa_column=Column(String(32), nullable=False))
    status: str = Field(
        sa_column=Column(
            String(24), nullable=False,
            comment="pending|rejected|promoted|expired",
        )
    )
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
    source_record_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    suggested_trust_tier: str | None = Field(
        default=None, sa_column=Column(String(24), nullable=True)
    )
    quality_snapshot: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False))
    provenance: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    reject_reason: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))


class KnowledgeLineageEvent(SQLModel, table=True):
    __tablename__ = "knowledge_lineage_event"

    event_id: str = Field(sa_column=Column(String(64), primary_key=True))
    lineage_id: str = Field(sa_column=Column(String(64), nullable=False, index=True))
    asset_kind: str = Field(sa_column=Column(String(32), nullable=False))
    asset_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    asset_version: int | None = Field(
        default=None, sa_column=Column(Integer, nullable=True)
    )
    at: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    actor: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    action: str = Field(sa_column=Column(String(48), nullable=False))
    from_tier: str | None = Field(
        default=None, sa_column=Column(String(24), nullable=True)
    )
    to_tier: str | None = Field(
        default=None, sa_column=Column(String(24), nullable=True)
    )
    trigger_id: str | None = Field(
        default=None, sa_column=Column(String(32), nullable=True)
    )
    refs: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    evidence_snapshot: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    decision: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    payload: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )


class KnowledgeCaptureJob(SQLModel, table=True):
    __tablename__ = "knowledge_capture_job"

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    record_id: int = Field(
        sa_column=Column(BigInteger, nullable=False, unique=True)
    )
    status: str = Field(sa_column=Column(String(24), nullable=False))
    attempt: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    max_attempts: int = Field(default=3, sa_column=Column(Integer, nullable=False))
    lease_owner: str | None = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    lease_until: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    snapshot: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )


class KnowledgePackageRegistry(SQLModel, table=True):
    """Imported package metadata; runtime assets remain in their domain stores."""

    __tablename__ = "knowledge_package_registry"
    __table_args__ = (
        UniqueConstraint("oid", "package_id", name="uq_knowledge_package_oid_key"),
        Index("ix_knowledge_package_oid_updated", "oid", "update_time"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    package_id: str = Field(sa_column=Column(String(255), nullable=False))
    schema_version: str = Field(sa_column=Column(String(16), nullable=False))
    title: str = Field(default="", sa_column=Column(String(255), nullable=False))
    description: str = Field(default="", sa_column=Column(Text, nullable=False))
    revision: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    item_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    defaults: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    sources: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False)
    )
    generator: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    create_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class KnowledgePackageItemRegistry(SQLModel, table=True):
    """Every extracted item, including review-only and evidence items."""

    __tablename__ = "knowledge_package_item_registry"
    __table_args__ = (
        UniqueConstraint(
            "package_registry_id",
            "item_id",
            name="uq_knowledge_package_item_key",
        ),
        Index(
            "ix_knowledge_package_item_governance",
            "package_registry_id",
            "present",
            "kind",
            "readiness",
        ),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    package_registry_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_package_registry.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    item_id: str = Field(sa_column=Column(String(255), nullable=False))
    kind: str = Field(sa_column=Column(String(32), nullable=False))
    source_status: str = Field(sa_column=Column(String(24), nullable=False))
    readiness: str = Field(sa_column=Column(String(24), nullable=False))
    present: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    payload: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    messages: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False)
    )
    runtime_action: str | None = Field(
        default=None, sa_column=Column(String(32), nullable=True)
    )
    runtime_target_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
