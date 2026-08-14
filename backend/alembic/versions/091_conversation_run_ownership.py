"""Fence running conversation workers and bind audit spans to run attempts.

Revision ID: 091a1b2c3d4e5
Revises: 090a1b2c3d4e5
Create Date: 2026-08-14
"""

import sqlalchemy as sa

from alembic import op

revision = "091a1b2c3d4e5"
down_revision = "090a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversation_run", sa.Column("worker_token", sa.String(36)))
    op.add_column(
        "conversation_run",
        sa.Column("lease_expires_at", sa.DateTime(timezone=False)),
    )
    op.create_index(
        "ix_conversation_run_lease_expires_at",
        "conversation_run",
        ["lease_expires_at"],
    )
    op.add_column("chat_log", sa.Column("run_id", sa.String(36)))
    op.create_index("ix_chat_log_run_id", "chat_log", ["run_id"])
    op.execute(
        """
        UPDATE chat_log AS l
           SET run_id = r.run_id
          FROM conversation_run AS r
         WHERE l.pid = r.chat_record_id
           AND l.run_id IS NULL
           AND r.attempt_index = 1
        """
    )


def downgrade() -> None:
    op.drop_index("ix_chat_log_run_id", table_name="chat_log")
    op.drop_column("chat_log", "run_id")
    op.drop_index(
        "ix_conversation_run_lease_expires_at", table_name="conversation_run"
    )
    op.drop_column("conversation_run", "lease_expires_at")
    op.drop_column("conversation_run", "worker_token")
