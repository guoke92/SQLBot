"""Add bounded dispatch bookkeeping to conversation runs.

Revision ID: 087a1b2c3d4e5
Revises: 086a1b2c3d4e5
Create Date: 2026-08-12
"""

import sqlalchemy as sa

from alembic import op

revision = "087a1b2c3d4e5"
down_revision = "086a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "conversation_run",
        sa.Column(
            "dispatch_attempts", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.create_index(
        "idx_conversation_run_dispatch",
        "conversation_run",
        ["status", "update_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_conversation_run_dispatch", table_name="conversation_run")
    op.drop_column("conversation_run", "dispatch_attempts")
