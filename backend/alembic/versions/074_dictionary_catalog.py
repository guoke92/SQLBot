"""dictionary catalog and published values

Revision ID: 074a1b2c3d4e5
Revises: 073a1b2c3d4e5
Create Date: 2026-07-27
"""

import sqlalchemy as sa

from alembic import op

revision = "074a1b2c3d4e5"
down_revision = "073a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table(
        "dictionary_field_config",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column(
            "ds_id",
            sa.BigInteger(),
            sa.ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "table_id",
            sa.BigInteger(),
            sa.ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "field_id",
            sa.BigInteger(),
            sa.ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("max_values", sa.Integer(), nullable=False),
        sa.Column("schema_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("published_generation", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("value_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_synced_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint("oid", "ds_id", "field_id", name="uq_dictionary_field_scope"),
    )
    op.create_index(
        "ix_dictionary_field_ds_table",
        "dictionary_field_config",
        ["ds_id", "table_id"],
    )
    op.create_table(
        "dictionary_value",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "config_id",
            sa.BigInteger(),
            sa.ForeignKey("dictionary_field_config.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.Text(), nullable=False),
        sa.Column("generation", sa.BigInteger(), nullable=False),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint(
            "config_id",
            "generation",
            "normalized_value",
            name="uq_dictionary_value_generation",
        ),
    )
    op.create_index(
        "ix_dictionary_value_config_generation",
        "dictionary_value",
        ["config_id", "generation"],
    )
    op.execute(
        "CREATE INDEX ix_dictionary_value_normalized_trgm "
        "ON dictionary_value USING gin (normalized_value gin_trgm_ops)"
    )


def downgrade() -> None:
    op.drop_table("dictionary_value")
    op.drop_table("dictionary_field_config")
