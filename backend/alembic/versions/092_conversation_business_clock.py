"""Persist the run-scoped business clock used by temporal intent parsing.

Revision ID: 092a1b2c3d4e5
Revises: 091a1b2c3d4e5
Create Date: 2026-08-14
"""

import sqlalchemy as sa

from alembic import op

revision = "092a1b2c3d4e5"
down_revision = "091a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "conversation_run",
        sa.Column(
            "business_now",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "conversation_run",
        sa.Column(
            "timezone",
            sa.String(64),
            nullable=False,
            server_default="Asia/Shanghai",
        ),
    )


def downgrade() -> None:
    op.drop_column("conversation_run", "timezone")
    op.drop_column("conversation_run", "business_now")
