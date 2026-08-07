"""Persistence models for metadata cognition (profiles, scan runs, relations)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ProfileStatus(str, Enum):
    EMPTY = "EMPTY"
    PROFILING = "PROFILING"
    READY = "READY"
    STALE = "STALE"
    UNSUPPORTED = "UNSUPPORTED"
    FAILED = "FAILED"


class ScanRunMode(str, Enum):
    FACTS_ONLY = "facts_only"
    SEMANTIC = "semantic"
    VALIDATE = "validate"
    FULL = "full"
    MANUAL = "manual"


class ScanTrigger(str, Enum):
    TABLE_ADDED = "table_added"
    SCHEMA_SYNC = "schema_sync"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WATERMARK = "watermark"


class ScanRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    # Finished work but did not publish a new profile generation (or partial caps).
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RelationKind(str, Enum):
    EQUI_JOIN = "EQUI_JOIN"
    MAP = "MAP"
    HIERARCHY = "HIERARCHY"
    BRIDGE = "BRIDGE"
    DERIVED_AGG = "DERIVED_AGG"
    BINDING = "BINDING"
    DERIVED_EXPR = "DERIVED_EXPR"


class RelationStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    DISABLED = "DISABLED"


class RelationSource(str, Enum):
    DDL = "ddl"
    NAME_OVERLAP = "name+overlap"
    HEURISTIC = "heuristic"
    LLM = "llm"
    MANUAL = "manual"
    PROBE = "probe"
    QUERY_LOG = "query_log"
    INCLUSION = "inclusion"


class MetadataScanRun(SQLModel, table=True):
    __tablename__ = "metadata_scan_run"
    __table_args__ = (
        Index("ix_metadata_scan_run_status_lease", "status", "lease_until"),
        Index("ix_metadata_scan_run_ds_table", "ds_id", "table_id"),
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
    table_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    run_mode: str = Field(sa_column=Column(String(32), nullable=False))
    trigger: str = Field(sa_column=Column(String(32), nullable=False))
    status: str = Field(sa_column=Column(String(24), nullable=False))
    lease_owner: str | None = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    lease_until: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    attempt: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    max_attempts: int = Field(default=3, sa_column=Column(Integer, nullable=False))
    targets: dict[str, Any] | list[Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    schema_fingerprint: str | None = Field(
        default=None, sa_column=Column(String(64), nullable=True)
    )
    data_watermark: str | None = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    pending_generation: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    graph_run_id: str | None = Field(
        default=None, sa_column=Column(String(64), nullable=True)
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    started_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )


class FieldProfileSnapshot(SQLModel, table=True):
    __tablename__ = "field_profile_snapshot"
    __table_args__ = (
        UniqueConstraint(
            "field_id",
            "window_code",
            "generation",
            name="uq_field_profile_generation_window",
        ),
        Index("ix_field_profile_table_generation", "table_id", "generation"),
        Index("ix_field_profile_ds_field", "ds_id", "field_id"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    scan_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("metadata_scan_run.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
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
    generation: int = Field(sa_column=Column(BigInteger, nullable=False))
    window_code: str = Field(
        default="ALL", sa_column=Column(String(16), nullable=False)
    )
    row_count: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    non_null_count: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    null_rate: float | None = Field(default=None, sa_column=Column(Float, nullable=True))
    approx_distinct: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    distinct_ratio: float | None = Field(
        default=None, sa_column=Column(Float, nullable=True)
    )
    min_value: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    max_value: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    top_values: list[Any] | dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    extended_stats: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    sample_method: str | None = Field(
        default=None, sa_column=Column(String(32), nullable=True)
    )
    sample_size: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    algo_version: str = Field(
        default="v1", sa_column=Column(String(32), nullable=False)
    )
    status: str = Field(default="READY", sa_column=Column(String(24), nullable=False))
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    profiled_at: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )


class FieldRelation(SQLModel, table=True):
    __tablename__ = "field_relation"
    __table_args__ = (
        UniqueConstraint(
            "ds_id",
            "source_field_id",
            "target_field_id",
            "kind",
            name="uq_field_relation_endpoints_kind",
        ),
        Index("ix_field_relation_ds_status", "ds_id", "status"),
        Index("ix_field_relation_source_table", "source_table_id"),
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
    source_table_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    source_field_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    target_table_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    target_field_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    kind: str = Field(sa_column=Column(String(32), nullable=False))
    cardinality: str | None = Field(
        default=None, sa_column=Column(String(16), nullable=True)
    )
    status: str = Field(sa_column=Column(String(24), nullable=False))
    source: str = Field(sa_column=Column(String(32), nullable=False))
    confidence: float | None = Field(default=None, sa_column=Column(Float, nullable=True))
    evidence: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    infer_generation: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    algo_version: str | None = Field(
        default=None, sa_column=Column(String(32), nullable=True)
    )
    confirmed_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    confirmed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    update_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
