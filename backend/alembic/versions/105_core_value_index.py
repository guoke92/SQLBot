"""Persisted datasource value index (enum codes/labels + business instances).

Revision ID: 105a1b2c3d4e5
Revises: 104a1b2c3d4e5
Create Date: 2026-09-18
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "105a1b2c3d4e5"
down_revision = "104a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("core_value_index"):
        return
    op.create_table(
        "core_value_index",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="值索引主键",
        ),
        sa.Column(
            "ds_id",
            sa.BigInteger(),
            sa.ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
            comment="数据源 ID",
        ),
        sa.Column(
            "table_name",
            sa.String(length=128),
            nullable=False,
            comment="物理表名",
        ),
        sa.Column(
            "field_name",
            sa.String(length=128),
            nullable=False,
            comment="物理字段名",
        ),
        sa.Column(
            "val_type",
            sa.String(length=32),
            nullable=False,
            comment="enum_code / enum_label / instance",
        ),
        sa.Column("raw_value", sa.Text(), nullable=False, comment="原始取值"),
        sa.Column(
            "normalized_value",
            sa.Text(),
            nullable=False,
            comment="标准化取值",
        ),
        sa.Column(
            "extra",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="扩展元数据",
        ),
        sa.UniqueConstraint(
            "ds_id",
            "table_name",
            "field_name",
            "val_type",
            "normalized_value",
            name="uq_core_value_index_slot",
        ),
    )
    op.create_index(
        "ix_core_value_index_ds_norm",
        "core_value_index",
        ["ds_id", "normalized_value"],
    )
    op.create_index(
        "ix_core_value_index_ds_table_field",
        "core_value_index",
        ["ds_id", "table_name", "field_name"],
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_core_value_index_norm_trgm "
        "ON core_value_index USING gin (normalized_value gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_core_value_index_norm_trgm")
    op.drop_index("ix_core_value_index_ds_table_field", table_name="core_value_index")
    op.drop_index("ix_core_value_index_ds_norm", table_name="core_value_index")
    op.drop_table("core_value_index")
