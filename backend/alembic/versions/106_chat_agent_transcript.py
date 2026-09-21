"""Persist chat-scoped agent transcript for same-thread continuation.

Revision ID: 106a1b2c3d4e5
Revises: 105a1b2c3d4e5
Create Date: 2026-09-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "106a1b2c3d4e5"
down_revision = "105a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("chat")}
    if "agent_transcript" in columns:
        return
    op.add_column(
        "chat",
        sa.Column(
            "agent_transcript",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Agent 会话全文 messages + folds 元数据",
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("chat")}
    if "agent_transcript" not in columns:
        return
    op.drop_column("chat", "agent_transcript")
