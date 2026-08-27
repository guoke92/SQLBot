"""Add knowledge_node_index.content (missed by the applied 096 revision).

The 096 migration file was extended with the content column after it had
already been applied on some environments, so those live tables already carry
the column while their alembic version sits below this revision. The DDL is
guarded by an inspector check so re-running against such a schema is a no-op
instead of a DuplicateColumn crash loop at startup.

Revision ID: 097a1b2c3d4e5
Revises: 096f1e2d3c4b5
Create Date: 2026-08-21
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "097a1b2c3d4e5"
down_revision = "096f1e2d3c4b5"
branch_labels = None
depends_on = None

_TABLE = "knowledge_node_index"
_COLUMN = "content"


def _column_exists(inspector: sa.Inspector) -> bool:
    return any(
        column["name"] == _COLUMN for column in inspector.get_columns(_TABLE)
    )


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(_TABLE) or _column_exists(inspector):
        return
    op.add_column(
        _TABLE,
        sa.Column(_COLUMN, postgresql.JSONB(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(_TABLE) or not _column_exists(inspector):
        return
    op.drop_column(_TABLE, _COLUMN)
