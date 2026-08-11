"""Add feedback column to chat_record for user up/down votes.

Revision ID: 085a1b2c3d4e5
Revises: 084a1b2c3d4e5
Create Date: 2026-08-11
"""

import sqlalchemy as sa

from alembic import op

revision = "085a1b2c3d4e5"
down_revision = "084a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_record",
        sa.Column(
            "feedback",
            sa.String(length=8),
            nullable=True,
            comment="User feedback: up / down / null",
        ),
    )


def downgrade() -> None:
    op.drop_column("chat_record", "feedback")
