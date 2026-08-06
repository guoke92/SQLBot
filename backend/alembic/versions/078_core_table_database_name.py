"""Add core_table.database_name for multi-database datasources (StarRocks catalogs).

Revision ID: 078a1b2c3d4e5
Revises: 077a1b2c3d4e5
Create Date: 2026-08-06
"""

import sqlalchemy as sa

from alembic import op

revision = "078a1b2c3d4e5"
down_revision = "077a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "core_table",
        sa.Column("database_name", sa.Text(), nullable=True, comment="Logical DB within datasource/catalog"),
    )


def downgrade() -> None:
    op.drop_column("core_table", "database_name")
