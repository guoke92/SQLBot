"""SQLModel tables for the v3.1 node store (migration 096)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pgvector.sqlalchemy.vector import VECTOR
from sqlalchemy import (
    BigInteger,
    Boolean,
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


class KnowledgeNode(SQLModel, table=True):
    """Identity head of one layered knowledge node (the editing truth)."""

    __tablename__ = "knowledge_node"
    __table_args__ = (
        UniqueConstraint(
            "oid", "node_kind", "natural_key", name="uq_knowledge_node_key"
        ),
        Index("ix_knowledge_node_kind", "oid", "node_kind", "status"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    node_kind: str = Field(sa_column=Column(String(32), nullable=False))
    natural_key: str = Field(sa_column=Column(String(500), nullable=False))
    namespace: str = Field(default="", sa_column=Column(String(255), nullable=False))
    status: str = Field(default="ACTIVE", sa_column=Column(String(24), nullable=False))
    current_version_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class KnowledgeNodeVersion(SQLModel, table=True):
    """Immutable content version of one node."""

    __tablename__ = "knowledge_node_version"
    __table_args__ = (
        UniqueConstraint("node_id", "version", name="uq_knowledge_node_version"),
        Index("ix_knowledge_node_version_hash", "content_hash"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    node_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_node.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    version: int = Field(sa_column=Column(Integer, nullable=False))
    payload: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    evidence_refs: list[Any] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False)
    )
    confidence: float = Field(default=0.5, sa_column=Column(Float, nullable=False))
    content_hash: str = Field(sa_column=Column(String(64), nullable=False))
    stub: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    origin_package_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    superseded_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(VECTOR(), nullable=True)
    )
    embedding_fingerprint: str | None = Field(
        default=None, sa_column=Column(String(64), nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class KnowledgeEdge(SQLModel, table=True):
    """Typed edge between two nodes; the knowledge graph proper."""

    __tablename__ = "knowledge_edge"
    __table_args__ = (
        UniqueConstraint(
            "src_node_id", "dst_node_id", "edge_kind", name="uq_knowledge_edge"
        ),
        Index("ix_knowledge_edge_dst", "dst_node_id", "edge_kind", "status"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    src_node_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_node.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    dst_node_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_node.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    edge_kind: str = Field(sa_column=Column(String(32), nullable=False))
    status: str = Field(
        default="proposed", sa_column=Column(String(16), nullable=False)
    )
    evidence: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    valid_from: datetime | None = Field(
        default=None, sa_column=Column(DateTime(), nullable=True)
    )
    valid_to: datetime | None = Field(
        default=None, sa_column=Column(DateTime(), nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class UnitComposition(SQLModel, table=True):
    """A scenario unit as a manifest of node references (governance object)."""

    __tablename__ = "unit_composition"
    __table_args__ = (
        UniqueConstraint("oid", "unit_key", name="uq_unit_composition_key"),
        Index(
            "ix_unit_composition_lifecycle",
            "oid",
            "lifecycle_status",
            "validation_status",
        ),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    unit_key: str = Field(sa_column=Column(String(255), nullable=False))
    package_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_package.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    domain: str = Field(sa_column=Column(String(255), nullable=False))
    title: str = Field(sa_column=Column(String(255), nullable=False))
    applicability: str = Field(default="", sa_column=Column(Text(), nullable=False))
    lifecycle_status: str = Field(
        default="DRAFT", sa_column=Column(String(24), nullable=False)
    )
    validation_status: str = Field(
        default="NOT_RUN", sa_column=Column(String(24), nullable=False)
    )
    active_deployment_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    refs: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    content_hash: str = Field(default="", sa_column=Column(String(64), nullable=False))
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class CompositionBinding(SQLModel, table=True):
    __tablename__ = "composition_binding"
    __table_args__ = (
        UniqueConstraint(
            "composition_id", "datasource_id", name="uq_composition_binding"
        ),
        Index("ix_composition_binding_state", "oid", "status"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    composition_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("unit_composition.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    datasource_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    catalog_fingerprint: str = Field(
        default="", sa_column=Column(String(64), nullable=False)
    )
    status: str = Field(default="UNBOUND", sa_column=Column(String(24), nullable=False))
    mapping: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    validation_result: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class CompositionDeployment(SQLModel, table=True):
    """Immutable pinned snapshot serving the runtime."""

    __tablename__ = "composition_deployment"
    __table_args__ = (
        UniqueConstraint(
            "composition_id", "binding_id", name="uq_composition_deployment"
        ),
        Index("ix_composition_deployment_active", "oid", "status", "activated_at"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    composition_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("unit_composition.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    binding_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("composition_binding.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    pinned_snapshot: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    status: str = Field(
        default="NOT_PUBLISHED", sa_column=Column(String(24), nullable=False)
    )
    error: str | None = Field(default=None, sa_column=Column(Text(), nullable=True))
    activated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(), nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class KnowledgeNodeIndex(SQLModel, table=True):
    """Derived retrieval index rows built at publish time."""

    __tablename__ = "knowledge_node_index"
    __table_args__ = (
        Index("ix_knowledge_node_index_lookup", "oid", "node_kind", "active"),
        Index("ix_knowledge_node_index_deployment", "deployment_id"),
    )

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    deployment_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("composition_deployment.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    node_version_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_node_version.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    node_kind: str = Field(sa_column=Column(String(32), nullable=False))
    physical_key: str = Field(default="", sa_column=Column(String(500), nullable=False))
    text_repr: str = Field(default="", sa_column=Column(Text(), nullable=False))
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(VECTOR(), nullable=True)
    )
    content: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))


class KnowledgeMergeConflict(SQLModel, table=True):
    """Merge-point M2 queue: divergent claims about one node."""

    __tablename__ = "knowledge_merge_conflict"
    __table_args__ = (Index("ix_knowledge_merge_conflict_queue", "oid", "status"),)

    id: int | None = Field(
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True)
    )
    oid: int = Field(sa_column=Column(BigInteger, nullable=False))
    node_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("knowledge_node.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    claim: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    source_authority: str = Field(
        default="", sa_column=Column(String(32), nullable=False)
    )
    status: str = Field(default="open", sa_column=Column(String(16), nullable=False))
    resolution: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    create_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
    update_time: datetime = Field(sa_column=Column(DateTime(), nullable=False))
