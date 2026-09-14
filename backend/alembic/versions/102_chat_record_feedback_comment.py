"""Add feedback_comment to chat_record for unhelpful descriptions.

Revision ID: 102a1b2c3d4e5
Revises: 101a1b2c3d4e5
Create Date: 2026-09-11
"""

import sqlalchemy as sa

from alembic import op

revision = "102a1b2c3d4e5"
down_revision = "101a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_record",
        sa.Column(
            "feedback_comment",
            sa.Text(),
            nullable=True,
            comment="没帮助时的反馈描述",
        ),
    )


def downgrade() -> None:
    op.drop_column("chat_record", "feedback_comment")
