"""add semantic clarification context to chat records

Revision ID: 077a1b2c3d4e5
Revises: 076a1b2c3d4e5
Create Date: 2026-07-29
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "077a1b2c3d4e5"
down_revision = "076a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_record",
        sa.Column(
            "intent_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    op.add_column(
        "chat_record",
        sa.Column(
            "clarification_parent_id",
            sa.BigInteger(),
            sa.ForeignKey("chat_record.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "uq_chat_record_clarification_parent",
        "chat_record",
        ["clarification_parent_id"],
        unique=True,
        postgresql_where=sa.text("clarification_parent_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_chat_record_clarification_parent",
        table_name="chat_record",
    )
    op.drop_column("chat_record", "clarification_parent_id")
    op.drop_column("chat_record", "intent_context")
