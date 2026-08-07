"""Store embedding content fingerprint on core_datasource.

Revision ID: 082a1b2c3d4e5
Revises: 081a1b2c3d4e5
Create Date: 2026-08-07
"""

import sqlalchemy as sa

from alembic import op

revision = "082a1b2c3d4e5"
down_revision = "081a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "core_datasource",
        sa.Column(
            "embedding_fingerprint",
            sa.String(length=64),
            nullable=True,
            comment="Hash of RANK schema text used for the stored DS embedding",
        ),
    )
    # Invalidate prior fingerprints so startup sync rebuilds lean RANK vectors
    # (old text may have included profile/join noise).
    op.execute(sa.text("UPDATE core_table SET embedding_fingerprint = NULL"))


def downgrade() -> None:
    op.drop_column("core_datasource", "embedding_fingerprint")
