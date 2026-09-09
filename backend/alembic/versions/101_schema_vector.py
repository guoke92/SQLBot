"""Isolated schema vector space: table / field / relation docs.

Revision ID: 101a1b2c3d4e5
Revises: 099a1b2c3d4e5
Create Date: 2026-09-08
"""

import sqlalchemy as sa
from alembic import op

revision = "101a1b2c3d4e5"
down_revision = "099a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schema_vector",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="schema 向量主键",
        ),
        sa.Column(
            "ds_id",
            sa.BigInteger(),
            sa.ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
            comment="数据源 ID",
        ),
        sa.Column(
            "kind",
            sa.String(length=16),
            nullable=False,
            comment="文档类型：table / field / relation",
        ),
        sa.Column(
            "object_key",
            sa.String(length=512),
            nullable=False,
            comment="文档键：表名 / 表.字段 / 关联端点",
        ),
        sa.Column(
            "table_name",
            sa.Text(),
            nullable=False,
            comment="主表名",
        ),
        sa.Column(
            "field_name",
            sa.Text(),
            nullable=True,
            comment="字段名（field 文档）",
        ),
        sa.Column(
            "peer_table",
            sa.Text(),
            nullable=True,
            comment="对端表名（relation 文档）",
        ),
        sa.Column(
            "source_text",
            sa.Text(),
            nullable=False,
            comment="嵌入原文",
        ),
        sa.Column(
            "embedding",
            sa.Text(),
            nullable=True,
            comment="向量 JSON，与 Wiki chunk 向量分表隔离",
        ),
        sa.Column(
            "fingerprint",
            sa.String(length=64),
            nullable=True,
            comment="source_text 指纹，未变则跳过重嵌",
        ),
        sa.Column(
            "update_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="更新时间",
        ),
        sa.UniqueConstraint("ds_id", "kind", "object_key", name="uq_schema_vector_doc"),
    )
    op.create_index("ix_schema_vector_ds_kind", "schema_vector", ["ds_id", "kind"])


def downgrade() -> None:
    op.drop_index("ix_schema_vector_ds_kind", table_name="schema_vector")
    op.drop_table("schema_vector")
