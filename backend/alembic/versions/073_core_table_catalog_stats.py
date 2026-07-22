"""core_table catalog stats: approx_rows, data_bytes, index_summary, stats_updated_at

Revision ID: 073a1b2c3d4e5
Revises: 072a1b2c3d4e5
Create Date: 2026-07-21
"""

from alembic import op
import sqlalchemy as sa

revision = "073a1b2c3d4e5"
down_revision = "072a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("core_table", sa.Column("approx_rows", sa.BigInteger(), nullable=True))
    op.add_column("core_table", sa.Column("data_bytes", sa.BigInteger(), nullable=True))
    op.add_column("core_table", sa.Column("index_summary", sa.Text(), nullable=True))
    op.add_column(
        "core_table",
        sa.Column("stats_updated_at", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("core_table", "stats_updated_at")
    op.drop_column("core_table", "index_summary")
    op.drop_column("core_table", "data_bytes")
    op.drop_column("core_table", "approx_rows")
