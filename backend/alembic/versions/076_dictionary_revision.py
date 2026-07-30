"""add dictionary publication revision

Revision ID: 076a1b2c3d4e5
Revises: 075a1b2c3d4e5
Create Date: 2026-07-27
"""

import sqlalchemy as sa

from alembic import op

revision = "076a1b2c3d4e5"
down_revision = "075a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dictionary_field_config",
        sa.Column(
            "revision",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_index(
        "ix_dictionary_value_normalized",
        "dictionary_value",
        ["normalized_value"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dictionary_value_normalized",
        table_name="dictionary_value",
    )
    op.drop_column("dictionary_field_config", "revision")
