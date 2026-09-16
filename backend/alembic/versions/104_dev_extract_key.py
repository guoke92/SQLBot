"""Drop debug snapshots; add conversation extract key.

Revision ID: 104a1b2c3d4e5
Revises: 103a1b2c3d4e5
Create Date: 2026-09-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "104a1b2c3d4e5"
down_revision = "103a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("debug_conversation_snapshot"):
        op.drop_index(
            "ix_debug_snapshot_source_url_chat",
            table_name="debug_conversation_snapshot",
        )
        op.drop_index(
            "ix_debug_conversation_snapshot_source_chat_id",
            table_name="debug_conversation_snapshot",
        )
        op.drop_table("debug_conversation_snapshot")
    if not inspector.has_table("conversation_extract_key"):
        op.create_table(
            "conversation_extract_key",
            sa.Column(
                "id",
                sa.BigInteger(),
                sa.Identity(always=True),
                primary_key=True,
                comment="提取密钥主键",
            ),
            sa.Column(
                "key_prefix",
                sa.String(length=16),
                nullable=False,
                comment="密钥前缀（展示用）",
            ),
            sa.Column(
                "key_hash",
                sa.String(length=64),
                nullable=False,
                comment="密钥 SHA-256",
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=False),
                nullable=False,
                comment="生成时间",
            ),
            sa.Column(
                "created_by",
                sa.BigInteger(),
                nullable=False,
                comment="生成人",
            ),
        )


def downgrade() -> None:
    op.drop_table("conversation_extract_key")
    op.create_table(
        "debug_conversation_snapshot",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("source_base_url", sa.String(length=512), nullable=False),
        sa.Column("source_oid", sa.BigInteger(), nullable=True),
        sa.Column("source_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("operator_id", sa.BigInteger(), nullable=True),
        sa.Column("operator_account", sa.String(length=255), nullable=True),
        sa.Column("operator_name", sa.String(length=255), nullable=True),
        sa.Column("brief", sa.Text(), nullable=True),
        sa.Column(
            "feedback_up",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "feedback_down",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "has_error",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("imported_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("imported_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "pack",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
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
