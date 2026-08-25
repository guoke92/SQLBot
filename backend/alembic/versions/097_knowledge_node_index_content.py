"""Add knowledge_node_index.content (missed by the applied 096 revision).

The 096 migration file was extended with the content column after it had
already been applied, so the live table lacks it while the SQLModel maps it.
This revision backfills the column idempotently.

Revision ID: 097a1b2c3d4e5
Revises: 096f1e2d3c4b5
Create Date: 2026-08-21
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "097a1b2c3d4e5"
down_revision = "096f1e2d3c4b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "knowledge_node_index",
        sa.Column("content", postgresql.JSONB(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("knowledge_node_index", "content")
