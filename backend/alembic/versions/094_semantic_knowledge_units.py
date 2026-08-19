"""Add authoritative KnowledgePackage 2.0 semantic unit storage.

Revision ID: 094a1b2c3d4e5
Revises: 093a1b2c3d4e5
Create Date: 2026-08-14
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "094a1b2c3d4e5"
down_revision = "093a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_package",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("package_id", sa.String(255), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("namespace", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("schema_version", sa.String(16), nullable=False, server_default="2.0"),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="REGISTERED"),
        sa.Column("source_document", postgresql.JSONB(), nullable=False),
        sa.Column("create_by", sa.BigInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("oid", "package_id", "revision", name="uq_semantic_package_revision"),
    )
    op.create_index("ix_semantic_package_updated", "knowledge_package", ["oid", "update_time"])

    op.create_table(
        "knowledge_source_evidence",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("package_id", sa.BigInteger(), sa.ForeignKey("knowledge_package.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_key", sa.String(255), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("evidence_kind", sa.String(64), nullable=False),
        sa.Column("locator", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("package_id", "evidence_key", name="uq_knowledge_source_evidence"),
    )
    op.create_index("ix_knowledge_source_package", "knowledge_source_evidence", ["package_id", "source_id"])

    op.create_table(
        "knowledge_unit",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("unit_key", sa.String(255), nullable=False),
        sa.Column("namespace", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("active_revision_id", sa.BigInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("oid", "unit_key", name="uq_knowledge_unit_key"),
    )
    op.create_index("ix_knowledge_unit_domain", "knowledge_unit", ["oid", "domain"])

    op.create_table(
        "knowledge_unit_revision",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("unit_id", sa.BigInteger(), sa.ForeignKey("knowledge_unit.id", ondelete="CASCADE"), nullable=False),
        sa.Column("package_id", sa.BigInteger(), sa.ForeignKey("knowledge_package.id", ondelete="SET NULL"), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("lifecycle_status", sa.String(24), nullable=False, server_default="DRAFT"),
        sa.Column("validation_status", sa.String(24), nullable=False, server_default="NOT_RUN"),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("validation_summary", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("create_by", sa.BigInteger(), nullable=True),
        sa.Column("review_by", sa.BigInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("unit_id", "revision", name="uq_knowledge_unit_revision"),
    )
    op.create_index("ix_knowledge_unit_review", "knowledge_unit_revision", ["oid", "lifecycle_status", "validation_status"])
    op.create_foreign_key(
        "fk_knowledge_unit_active_revision",
        "knowledge_unit",
        "knowledge_unit_revision",
        ["active_revision_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "knowledge_binding",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("revision_id", sa.BigInteger(), sa.ForeignKey("knowledge_unit_revision.id", ondelete="CASCADE"), nullable=False),
        sa.Column("datasource_id", sa.BigInteger(), nullable=False),
        sa.Column("catalog_fingerprint", sa.String(64), nullable=False, server_default=""),
        sa.Column("status", sa.String(24), nullable=False, server_default="UNBOUND"),
        sa.Column("mapping", postgresql.JSONB(), nullable=False),
        sa.Column("validation_result", postgresql.JSONB(), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("revision_id", "datasource_id", name="uq_knowledge_binding"),
    )
    op.create_index("ix_knowledge_binding_state", "knowledge_binding", ["oid", "status"])

    op.create_table(
        "knowledge_deployment",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("revision_id", sa.BigInteger(), sa.ForeignKey("knowledge_unit_revision.id", ondelete="CASCADE"), nullable=False),
        sa.Column("binding_id", sa.BigInteger(), sa.ForeignKey("knowledge_binding.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="NOT_PUBLISHED"),
        sa.Column("projection_manifest", postgresql.JSONB(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("revision_id", "binding_id", name="uq_knowledge_deployment"),
    )
    op.create_index("ix_knowledge_deployment_active", "knowledge_deployment", ["oid", "status", "activated_at"])


def downgrade() -> None:
    op.drop_table("knowledge_deployment")
    op.drop_table("knowledge_binding")
    op.drop_constraint(
        "fk_knowledge_unit_active_revision", "knowledge_unit", type_="foreignkey"
    )
    op.drop_table("knowledge_unit_revision")
    op.drop_table("knowledge_unit")
    op.drop_table("knowledge_source_evidence")
    op.drop_table("knowledge_package")
