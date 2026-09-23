"""Raw LLM request/response capture for analysis.

Revision ID: 107a1b2c3d4e5
Revises: 106a1b2c3d4e5
Create Date: 2026-09-22
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "107a1b2c3d4e5"
down_revision = "106a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("llm_call_log"):
        return
    op.create_table(
        "llm_call_log",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="LLM 调用日志主键",
        ),
        sa.Column(
            "chat_id",
            sa.BigInteger(),
            nullable=True,
            comment="关联对话 ID",
        ),
        sa.Column(
            "chat_record_id",
            sa.BigInteger(),
            nullable=True,
            comment="关联对话记录 ID",
        ),
        sa.Column(
            "request_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="真实发出的 LLM 请求报文（原始 body）",
        ),
        sa.Column(
            "response_content",
            sa.Text(),
            nullable=True,
            comment="流式合并后的完整回复文本",
        ),
        sa.Column(
            "reasoning_content",
            sa.Text(),
            nullable=True,
            comment="流式合并后的完整思考文本",
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
            comment="调用失败时的错误信息",
        ),
        sa.Column(
            "start_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="请求落库时间",
        ),
        sa.Column(
            "finish_time",
            sa.DateTime(timezone=False),
            nullable=True,
            comment="响应合并完成时间",
        ),
    )
    op.create_index("ix_llm_call_log_chat_id", "llm_call_log", ["chat_id"])
    op.create_index(
        "ix_llm_call_log_chat_record_id", "llm_call_log", ["chat_record_id"]
    )
    op.create_index("ix_llm_call_log_start_time", "llm_call_log", ["start_time"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("llm_call_log"):
        return
    op.drop_index("ix_llm_call_log_start_time", table_name="llm_call_log")
    op.drop_index("ix_llm_call_log_chat_record_id", table_name="llm_call_log")
    op.drop_index("ix_llm_call_log_chat_id", table_name="llm_call_log")
    op.drop_table("llm_call_log")
