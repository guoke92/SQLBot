"""Store embedding content fingerprint on core_table.

Revision ID: 080a1b2c3d4e5
Revises: 079a1b2c3d4e5
Create Date: 2026-08-07
"""

import sqlalchemy as sa

from alembic import op

revision = "080a1b2c3d4e5"
down_revision = "079a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "core_table",
        sa.Column(
            "embedding_fingerprint",
            sa.String(length=64),
            nullable=True,
            comment="Hash of schema text used for the stored table embedding",
        ),
    )


def downgrade() -> None:
    op.drop_column("core_table", "embedding_fingerprint")
