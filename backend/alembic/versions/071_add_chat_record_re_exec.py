"""071_add_chat_record_re_exec

为 chat_record 表添加 re_exec 字段，存储协议重执行所需的数据。
SQL 协议存储 {"sql": "..."}；REST 协议存储 {"endpoint": "...", "params": {...}, "base_url": "..."}。

Revision ID: 071a2b3c4d5e6
Revises: 070a1b2c3d4e5
Create Date: 2026-07-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '071a2b3c4d5e6'
down_revision = '070a1b2c3d4e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('chat_record', sa.Column('re_exec', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('chat_record', 're_exec')
