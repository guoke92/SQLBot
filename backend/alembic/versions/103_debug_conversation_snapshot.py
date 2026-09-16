"""Debug conversation snapshot store.

Revision ID: 103a1b2c3d4e5
Revises: 102a1b2c3d4e5
Create Date: 2026-09-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "103a1b2c3d4e5"
down_revision = "102a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "debug_conversation_snapshot",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="排查快照主键",
        ),
        sa.Column(
            "source_base_url",
            sa.String(length=512),
            nullable=False,
            comment="来源环境 URL",
        ),
        sa.Column(
            "source_oid",
            sa.BigInteger(),
            nullable=True,
            comment="来源工作空间 ID",
        ),
        sa.Column(
            "source_chat_id",
            sa.BigInteger(),
            nullable=False,
            comment="来源对话 ID",
        ),
        sa.Column(
            "operator_id",
            sa.BigInteger(),
            nullable=True,
            comment="来源操作人 ID",
        ),
        sa.Column(
            "operator_account",
            sa.String(length=255),
            nullable=True,
            comment="来源操作人账号",
        ),
        sa.Column(
            "operator_name",
            sa.String(length=255),
            nullable=True,
            comment="来源操作人姓名",
        ),
        sa.Column("brief", sa.Text(), nullable=True, comment="对话标题"),
        sa.Column(
            "feedback_up",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="有帮助次数",
        ),
        sa.Column(
            "feedback_down",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="没帮助次数",
        ),
        sa.Column(
            "has_error",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="是否含报错回合",
        ),
        sa.Column(
            "imported_at",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="导入时间",
        ),
        sa.Column(
            "imported_by",
            sa.BigInteger(),
            nullable=False,
            comment="本机导入人",
        ),
        sa.Column(
            "pack",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="ConversationPack JSON",
        ),
    )
    op.create_index(
        "ix_debug_conversation_snapshot_source_chat_id",
        "debug_conversation_snapshot",
        ["source_chat_id"],
    )
    op.create_index(
        "ix_debug_snapshot_source_url_chat",
        "debug_conversation_snapshot",
        ["source_base_url", "source_chat_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_debug_snapshot_source_url_chat", table_name="debug_conversation_snapshot"
    )
    op.drop_index(
        "ix_debug_conversation_snapshot_source_chat_id",
        table_name="debug_conversation_snapshot",
    )
    op.drop_table("debug_conversation_snapshot")
