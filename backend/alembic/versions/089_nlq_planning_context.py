"""Persist the replayable NLQ planning context.

Revision ID: 089a1b2c3d4e5
Revises: 088a1b2c3d4e5
Create Date: 2026-08-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "089a1b2c3d4e5"
down_revision = "088a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "nlq_run",
        sa.Column(
            "planning_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("nlq_run", "planning_context")
