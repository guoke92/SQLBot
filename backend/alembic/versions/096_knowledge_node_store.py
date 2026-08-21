"""Add the v3.1 node store: layered knowledge nodes, typed edges, unit compositions.

Revision ID: 096f1e2d3c4b5
Revises: 095a1b2c3d4e5
Create Date: 2026-08-19
"""

import sqlalchemy as sa
import pgvector.sqlalchemy.vector
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "096f1e2d3c4b5"
down_revision = "095a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_node",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("node_kind", sa.String(32), nullable=False),
        sa.Column("natural_key", sa.String(500), nullable=False),
        sa.Column("namespace", sa.String(255), nullable=False, server_default=""),
        sa.Column("status", sa.String(24), nullable=False, server_default="ACTIVE"),
        sa.Column("current_version_id", sa.BigInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("oid", "node_kind", "natural_key", name="uq_knowledge_node_key"),
    )
    op.create_index(
        "ix_knowledge_node_kind", "knowledge_node", ["oid", "node_kind", "status"]
    )

    op.create_table(
        "knowledge_node_version",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("node_id", sa.BigInteger(), sa.ForeignKey("knowledge_node.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("evidence_refs", postgresql.JSONB(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("stub", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("origin_package_id", sa.BigInteger(), nullable=True),
        sa.Column("superseded_by", sa.BigInteger(), nullable=True),
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(), nullable=True),
        sa.Column("embedding_fingerprint", sa.String(64), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("node_id", "version", name="uq_knowledge_node_version"),
    )
    op.create_index(
        "ix_knowledge_node_version_hash", "knowledge_node_version", ["content_hash"]
    )
    op.create_foreign_key(
        "fk_knowledge_node_current_version",
        "knowledge_node",
        "knowledge_node_version",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "knowledge_edge",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("src_node_id", sa.BigInteger(), sa.ForeignKey("knowledge_node.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dst_node_id", sa.BigInteger(), sa.ForeignKey("knowledge_node.id", ondelete="CASCADE"), nullable=False),
        sa.Column("edge_kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="proposed"),
        sa.Column("evidence", postgresql.JSONB(), nullable=False),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("src_node_id", "dst_node_id", "edge_kind", name="uq_knowledge_edge"),
    )
    op.create_index(
        "ix_knowledge_edge_dst", "knowledge_edge", ["dst_node_id", "edge_kind", "status"]
    )

    op.create_table(
        "unit_composition",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("unit_key", sa.String(255), nullable=False),
        sa.Column("package_id", sa.BigInteger(), sa.ForeignKey("knowledge_package.id", ondelete="SET NULL"), nullable=True),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("applicability", sa.Text(), nullable=False, server_default=""),
        sa.Column("lifecycle_status", sa.String(24), nullable=False, server_default="DRAFT"),
        sa.Column("validation_status", sa.String(24), nullable=False, server_default="NOT_RUN"),
        sa.Column("active_deployment_id", sa.BigInteger(), nullable=True),
        sa.Column("refs", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("oid", "unit_key", name="uq_unit_composition_key"),
    )
    op.create_index(
        "ix_unit_composition_lifecycle",
        "unit_composition",
        ["oid", "lifecycle_status", "validation_status"],
    )

    op.create_table(
        "composition_binding",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("composition_id", sa.BigInteger(), sa.ForeignKey("unit_composition.id", ondelete="CASCADE"), nullable=False),
        sa.Column("datasource_id", sa.BigInteger(), nullable=False),
        sa.Column("catalog_fingerprint", sa.String(64), nullable=False, server_default=""),
        sa.Column("status", sa.String(24), nullable=False, server_default="UNBOUND"),
        sa.Column("mapping", postgresql.JSONB(), nullable=False),
        sa.Column("validation_result", postgresql.JSONB(), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("composition_id", "datasource_id", name="uq_composition_binding"),
    )
    op.create_index("ix_composition_binding_state", "composition_binding", ["oid", "status"])

    op.create_table(
        "composition_deployment",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("composition_id", sa.BigInteger(), sa.ForeignKey("unit_composition.id", ondelete="CASCADE"), nullable=False),
        sa.Column("binding_id", sa.BigInteger(), sa.ForeignKey("composition_binding.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pinned_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="NOT_PUBLISHED"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("composition_id", "binding_id", name="uq_composition_deployment"),
    )
    op.create_index(
        "ix_composition_deployment_active",
        "composition_deployment",
        ["oid", "status", "activated_at"],
    )
    op.create_foreign_key(
        "fk_unit_composition_active_deployment",
        "unit_composition",
        "composition_deployment",
        ["active_deployment_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "knowledge_node_index",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("deployment_id", sa.BigInteger(), sa.ForeignKey("composition_deployment.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_version_id", sa.BigInteger(), sa.ForeignKey("knowledge_node_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_kind", sa.String(32), nullable=False),
        sa.Column("physical_key", sa.String(500), nullable=False, server_default=""),
        sa.Column("text_repr", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(), nullable=True),
        sa.Column("content", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("create_time", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_knowledge_node_index_lookup",
        "knowledge_node_index",
        ["oid", "node_kind", "active"],
    )
    op.create_index(
        "ix_knowledge_node_index_deployment",
        "knowledge_node_index",
        ["deployment_id"],
    )

    op.create_table(
        "knowledge_merge_conflict",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("node_id", sa.BigInteger(), sa.ForeignKey("knowledge_node.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim", postgresql.JSONB(), nullable=False),
        sa.Column("source_authority", sa.String(32), nullable=False, server_default=""),
        sa.Column("status", sa.String(16), nullable=False, server_default="open"),
        sa.Column("resolution", postgresql.JSONB(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_knowledge_merge_conflict_queue",
        "knowledge_merge_conflict",
        ["oid", "status"],
    )


def downgrade() -> None:
    op.drop_table("knowledge_merge_conflict")
    op.drop_table("knowledge_node_index")
    op.drop_index("ix_composition_deployment_active", table_name="composition_deployment")
    op.drop_table("composition_deployment")
    op.drop_table("composition_binding")
    op.drop_table("unit_composition")
    op.drop_table("knowledge_edge")
    op.drop_table("knowledge_node_version")
    op.drop_table("knowledge_node")
