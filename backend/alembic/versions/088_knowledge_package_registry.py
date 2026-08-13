"""Add imported knowledge package registry.

Revision ID: 088a1b2c3d4e5
Revises: 087a1b2c3d4e5
Create Date: 2026-08-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "088a1b2c3d4e5"
down_revision = "087a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_package_registry",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("package_id", sa.String(255), nullable=False),
        sa.Column("schema_version", sa.String(16), nullable=False),
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("defaults", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("sources", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("generator", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("create_by", sa.BigInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("oid", "package_id", name="uq_knowledge_package_oid_key"),
    )
    op.create_index(
        "ix_knowledge_package_oid_updated",
        "knowledge_package_registry",
        ["oid", "update_time"],
    )
    op.create_table(
        "knowledge_package_item_registry",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("package_registry_id", sa.BigInteger(), nullable=False),
        sa.Column("item_id", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("source_status", sa.String(24), nullable=False),
        sa.Column("readiness", sa.String(24), nullable=False),
        sa.Column("present", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("messages", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("runtime_action", sa.String(32), nullable=True),
        sa.Column("runtime_target_id", sa.BigInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["package_registry_id"],
            ["knowledge_package_registry.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "package_registry_id", "item_id", name="uq_knowledge_package_item_key"
        ),
    )
    op.create_index(
        "ix_knowledge_package_item_governance",
        "knowledge_package_item_registry",
        ["package_registry_id", "present", "kind", "readiness"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_package_item_governance",
        table_name="knowledge_package_item_registry",
    )
    op.drop_table("knowledge_package_item_registry")
    op.drop_index(
        "ix_knowledge_package_oid_updated", table_name="knowledge_package_registry"
    )
    op.drop_table("knowledge_package_registry")
