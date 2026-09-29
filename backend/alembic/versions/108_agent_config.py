"""Versioned agent runtime configuration (prompt + tools + loop bounds).

Revision ID: 108a1b2c3d4e5
Revises: 107a1b2c3d4e5
Create Date: 2026-09-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "108a1b2c3d4e5"
down_revision = "107a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("agent_config_version"):
        return
    op.create_table(
        "agent_config_version",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="配置版本主键",
        ),
        sa.Column(
            "scope_key",
            sa.String(64),
            nullable=False,
            server_default="global",
            comment="作用域键，当前固定 global",
        ),
        sa.Column(
            "version_no",
            sa.Integer(),
            nullable=False,
            comment="单调递增版本号",
        ),
        sa.Column(
            "status",
            sa.String(16),
            nullable=False,
            comment="draft | published | archived",
        ),
        sa.Column(
            "prompt_body",
            sa.Text(),
            nullable=False,
            comment="系统提示词全文，含占位符 {execution_limit}",
        ),
        sa.Column(
            "tools",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="工具覆盖 {name:{enabled,description,parallel_safe,round_budget}}",
        ),
        sa.Column(
            "loop_params",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="循环参数 {execution_round_limit,probe_sql_limit,...}",
        ),
        sa.Column(
            "change_note",
            sa.String(255),
            nullable=True,
            comment="变更说明",
        ),
        sa.Column("create_by", sa.BigInteger(), nullable=True, comment="创建人"),
        sa.Column(
            "create_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column("published_by", sa.BigInteger(), nullable=True, comment="发布人"),
        sa.Column(
            "published_time",
            sa.DateTime(timezone=False),
            nullable=True,
            comment="发布时间",
        ),
    )
    op.create_index(
        "ix_agent_config_version_scope_status",
        "agent_config_version",
        ["scope_key", "status"],
    )
    op.create_index(
        "uq_agent_config_version_no",
        "agent_config_version",
        ["scope_key", "version_no"],
        unique=True,
    )
    # Database-level guarantee: at most one published / one draft per scope.
    op.create_index(
        "uq_agent_config_version_published",
        "agent_config_version",
        ["scope_key"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )
    op.create_index(
        "uq_agent_config_version_draft",
        "agent_config_version",
        ["scope_key"],
        unique=True,
        postgresql_where=sa.text("status = 'draft'"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("agent_config_version"):
        return
    op.drop_index("uq_agent_config_version_draft", table_name="agent_config_version")
    op.drop_index(
        "uq_agent_config_version_published", table_name="agent_config_version"
    )
    op.drop_index("uq_agent_config_version_no", table_name="agent_config_version")
    op.drop_index(
        "ix_agent_config_version_scope_status", table_name="agent_config_version"
    )
    op.drop_table("agent_config_version")
