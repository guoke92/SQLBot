"""Remove QueryIntent storage and persist plan facts for the v7.1 pipeline.

Revision ID: 095a1b2c3d4e5
Revises: 094a1b2c3d4e5
Create Date: 2026-08-14
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "095a1b2c3d4e5"
down_revision = "094a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "query_run",
        sa.Column(
            "plan_facts",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.drop_column("query_run", "intent_revisions")
    op.drop_column("query_run", "active_intent_revision")


def downgrade() -> None:
    op.add_column(
        "query_run",
        sa.Column(
            "active_intent_revision",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "query_run",
        sa.Column(
            "intent_revisions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.drop_column("query_run", "plan_facts")
