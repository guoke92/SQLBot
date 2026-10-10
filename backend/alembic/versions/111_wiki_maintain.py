"""Wiki maintenance log: base body, patch log, and immutable sources.

Revision ID: 111a1b2c3d4e5
Revises: 110a1b2c3d4e5
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "111a1b2c3d4e5"
down_revision = "110a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("wiki_page"):
        return
    columns = {col["name"] for col in inspector.get_columns("wiki_page")}
    if "base_body_md" not in columns:
        op.add_column(
            "wiki_page",
            sa.Column(
                "base_body_md",
                sa.Text(),
                nullable=True,
                comment="最近一次文件导入原文；维护诞生的页为空",
            ),
        )
        op.execute("UPDATE wiki_page SET base_body_md = body_md WHERE base_body_md IS NULL")

    if not inspector.has_table("wiki_page_patch"):
        op.create_table(
            "wiki_page_patch",
            sa.Column(
                "id",
                sa.BigInteger(),
                sa.Identity(always=True),
                primary_key=True,
                comment="补丁主键",
            ),
            sa.Column(
                "page_id",
                sa.BigInteger(),
                sa.ForeignKey("wiki_page.id", ondelete="CASCADE"),
                nullable=True,
                comment="目标页；新建页在接受前为空",
            ),
            sa.Column(
                "corpus_id",
                sa.BigInteger(),
                sa.ForeignKey("wiki_corpus.id", ondelete="CASCADE"),
                nullable=False,
                comment="所属语料",
            ),
            sa.Column("belong", sa.String(length=64), nullable=False, server_default="", comment="页类型目录"),
            sa.Column("page_key", sa.String(length=255), nullable=False, server_default="", comment="页标识"),
            sa.Column("run_id", sa.String(length=64), nullable=True, comment="维护回合"),
            sa.Column("record_id", sa.BigInteger(), nullable=True, comment="维护对话记录"),
            sa.Column("origin", sa.String(length=32), nullable=False, comment="import/maintain/conversation/document"),
            sa.Column("source_ref", sa.Text(), nullable=False, server_default="", comment="程序盖章的来源"),
            sa.Column("op", sa.String(length=32), nullable=False, comment="主张操作"),
            sa.Column("claim_path", sa.Text(), nullable=False, server_default="", comment="主张路径"),
            sa.Column(
                "payload",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
                comment="主张内容，不含 sources/status",
            ),
            sa.Column(
                "status",
                sa.String(length=32),
                nullable=False,
                server_default="proposed",
                comment="proposed/applied/conflicted/rejected",
            ),
            sa.Column("actor", sa.String(length=64), nullable=False, server_default="", comment="操作者"),
            sa.Column("create_time", sa.DateTime(), nullable=False, comment="写入时间"),
        )
        op.create_index("ix_wiki_page_patch_page", "wiki_page_patch", ["page_id"])
        op.create_index("ix_wiki_page_patch_run", "wiki_page_patch", ["run_id"])
        op.execute(
            """
            INSERT INTO wiki_page_patch (
                page_id, corpus_id, belong, page_key, origin, source_ref, op,
                claim_path, payload, status, actor, create_time
            )
            SELECT
                id, corpus_id, belong, page_key, 'import', 'import', 'replace_base',
                '', '{}'::jsonb, 'applied', 'migration', NOW()
            FROM wiki_page
            """
        )

    if not inspector.has_table("wiki_source"):
        op.create_table(
            "wiki_source",
            sa.Column(
                "id",
                sa.BigInteger(),
                sa.Identity(always=True),
                primary_key=True,
                comment="原料主键",
            ),
            sa.Column(
                "corpus_id",
                sa.BigInteger(),
                sa.ForeignKey("wiki_corpus.id", ondelete="CASCADE"),
                nullable=False,
                comment="所属语料",
            ),
            sa.Column("oid", sa.BigInteger(), nullable=False, comment="工作区"),
            sa.Column("kind", sa.String(length=32), nullable=False, comment="document 或 conversation"),
            sa.Column("title", sa.String(length=255), nullable=False, server_default="", comment="标题"),
            sa.Column("body_md", sa.Text(), nullable=False, server_default="", comment="粘贴正文；问数沉淀为空"),
            sa.Column(
                "pointer",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
                comment="问数沉淀只存 chat_id/record_id",
            ),
            sa.Column("create_by", sa.BigInteger(), nullable=True, comment="创建人"),
            sa.Column("create_time", sa.DateTime(), nullable=False, comment="写入时间"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("wiki_source"):
        op.drop_table("wiki_source")
    if inspector.has_table("wiki_page_patch"):
        op.drop_index("ix_wiki_page_patch_run", table_name="wiki_page_patch")
        op.drop_index("ix_wiki_page_patch_page", table_name="wiki_page_patch")
        op.drop_table("wiki_page_patch")
    if inspector.has_table("wiki_page"):
        columns = {col["name"] for col in inspector.get_columns("wiki_page")}
        if "base_body_md" in columns:
            op.drop_column("wiki_page", "base_body_md")
