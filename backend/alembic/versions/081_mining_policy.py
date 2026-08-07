"""Add mining_policy JSON on datasource and table.

Revision ID: 081a1b2c3d4e5
Revises: 080a1b2c3d4e5
Create Date: 2026-08-07
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "081a1b2c3d4e5"
down_revision = "080a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "core_datasource",
        sa.Column(
            "mining_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Default mining preset/capabilities for tables in this datasource",
        ),
    )
    op.add_column(
        "core_table",
        sa.Column(
            "mining_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Table mining policy override (preset/custom/inherit)",
        ),
    )


def downgrade() -> None:
    op.drop_column("core_table", "mining_policy")
    op.drop_column("core_datasource", "mining_policy")
