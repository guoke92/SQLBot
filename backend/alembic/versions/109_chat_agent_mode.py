"""Add session-level Query/Analyze mode on chat.

Revision ID: 109a1b2c3d4e5
Revises: 108a1b2c3d4e5
Create Date: 2026-09-30
"""

import sqlalchemy as sa
from alembic import op

revision = "109a1b2c3d4e5"
down_revision = "108a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("chat")}
    if "agent_mode" in columns:
        return
    op.add_column(
        "chat",
        sa.Column(
            "agent_mode",
            sa.String(20),
            nullable=False,
            server_default="query",
            comment="会话级 Agent 模式：query | analyze",
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("chat")}
    if "agent_mode" not in columns:
        return
    op.drop_column("chat", "agent_mode")
