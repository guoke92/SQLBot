"""Add sql_rules to the versioned agent configuration.

Revision ID: 110a1b2c3d4e5
Revises: 109a1b2c3d4e5
Create Date: 2026-09-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "110a1b2c3d4e5"
down_revision = "109a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("agent_config_version"):
        return
    columns = {col["name"] for col in inspector.get_columns("agent_config_version")}
    if "sql_rules" in columns:
        return
    op.add_column(
        "agent_config_version",
        sa.Column(
            "sql_rules",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="执行前规则 {kind:{enabled}}，空对象表示沿用代码默认",
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("agent_config_version"):
        return
    columns = {col["name"] for col in inspector.get_columns("agent_config_version")}
    if "sql_rules" not in columns:
        return
    op.drop_column("agent_config_version", "sql_rules")
