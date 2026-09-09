"""Wiki corpus store: pages, revisions, embeddings, bindings (final schema).

Identity is ``(belong, page_key)`` within a corpus. Embed progress counters
live on ``wiki_corpus``. No data-preserving upgrade path — drop and recreate
if an older wiki schema already exists.

Revision ID: 099a1b2c3d4e5
Revises: 098a1b2c3d4e5
Create Date: 2026-09-07
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "099a1b2c3d4e5"
down_revision = "098a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wiki_corpus",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="语料主键",
        ),
        sa.Column("oid", sa.BigInteger(), nullable=False, comment="工作区 ID"),
        sa.Column(
            "corpus_key",
            sa.String(length=64),
            nullable=False,
            comment="语料标识，工作区内唯一",
        ),
        sa.Column("name", sa.String(length=128), nullable=True, comment="展示名称"),
        sa.Column(
            "generation",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="内容世代戳，写入后单调递增",
        ),
        sa.Column(
            "page_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="页面总数",
        ),
        sa.Column(
            "published_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="已发布页数",
        ),
        sa.Column(
            "draft_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="草稿页数",
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="indexing",
            comment="indexing | ready | failed",
        ),
        sa.Column(
            "embedded_chunks",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="已写入向量的 chunk 数",
        ),
        sa.Column(
            "failed_chunks",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="向量化失败的 chunk 数",
        ),
        sa.Column(
            "embed_error",
            sa.Text(),
            nullable=True,
            comment="最近一次向量化失败摘要",
        ),
        sa.Column(
            "source_path",
            sa.String(length=512),
            nullable=True,
            comment="最近一次导入的服务端目录路径",
        ),
        sa.Column(
            "create_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "update_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="更新时间",
        ),
        sa.UniqueConstraint("oid", "corpus_key", name="uq_wiki_corpus_oid_key"),
    )

    op.create_table(
        "wiki_page",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="页面主键",
        ),
        sa.Column(
            "corpus_id",
            sa.BigInteger(),
            sa.ForeignKey("wiki_corpus.id", ondelete="CASCADE"),
            nullable=False,
            comment="所属语料",
        ),
        sa.Column(
            "belong",
            sa.String(length=64),
            nullable=False,
            server_default="",
            comment="上级目录 tables/enums/concepts/…",
        ),
        sa.Column(
            "page_key",
            sa.String(length=255),
            nullable=False,
            comment="页面身份 slug（目录内唯一）",
        ),
        sa.Column(
            "page_type",
            sa.String(length=32),
            nullable=False,
            comment="页面类型 table/enum/caliber/...",
        ),
        sa.Column("title", sa.String(length=255), nullable=False, comment="页面标题"),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            comment="draft | published | retired（原样入库）",
        ),
        sa.Column(
            "databases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
            comment="scope.databases 物理库名",
        ),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
            comment="业务别名",
        ),
        sa.Column(
            "anchors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
            comment="物理锚点清单",
        ),
        sa.Column("body_md", sa.Text(), nullable=False, comment="契约 Markdown 全文"),
        sa.Column(
            "content_sha",
            sa.String(length=64),
            nullable=False,
            comment="正文 SHA-256",
        ),
        sa.Column(
            "page_disabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="管理员禁用开关",
        ),
        sa.Column(
            "create_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "update_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="更新时间",
        ),
        sa.UniqueConstraint(
            "corpus_id",
            "belong",
            "page_key",
            name="uq_wiki_page_corpus_belong_key",
        ),
    )
    op.create_index("ix_wiki_page_corpus_status", "wiki_page", ["corpus_id", "status"])

    op.create_table(
        "wiki_page_revision",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="修订主键",
        ),
        sa.Column(
            "page_id",
            sa.BigInteger(),
            sa.ForeignKey("wiki_page.id", ondelete="CASCADE"),
            nullable=False,
            comment="所属页面",
        ),
        sa.Column(
            "corpus_id",
            sa.BigInteger(),
            sa.ForeignKey("wiki_corpus.id", ondelete="CASCADE"),
            nullable=False,
            comment="所属语料",
        ),
        sa.Column(
            "revision_no",
            sa.Integer(),
            nullable=False,
            comment="页内递增修订号",
        ),
        sa.Column(
            "status", sa.String(length=32), nullable=False, comment="该修订时状态"
        ),
        sa.Column("body_md", sa.Text(), nullable=False, comment="修订正文"),
        sa.Column(
            "content_sha",
            sa.String(length=64),
            nullable=False,
            comment="修订正文 SHA-256",
        ),
        sa.Column(
            "source",
            sa.String(length=32),
            nullable=False,
            server_default="import",
            comment="import | publish",
        ),
        sa.Column(
            "create_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="创建时间",
        ),
    )
    op.create_index(
        "ix_wiki_page_revision_page",
        "wiki_page_revision",
        ["page_id", "revision_no"],
    )

    op.create_table(
        "wiki_chunk_embedding",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="chunk 向量主键",
        ),
        sa.Column(
            "corpus_id",
            sa.BigInteger(),
            sa.ForeignKey("wiki_corpus.id", ondelete="CASCADE"),
            nullable=False,
            comment="所属语料",
        ),
        sa.Column(
            "belong",
            sa.String(length=64),
            nullable=False,
            server_default="",
            comment="页面归属目录，与 wiki_page.belong 对齐",
        ),
        sa.Column(
            "page_key",
            sa.String(length=255),
            nullable=False,
            comment="页面 slug",
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
            comment="页内 chunk 序号",
        ),
        sa.Column(
            "chunk_hash",
            sa.String(length=64),
            nullable=False,
            comment="嵌入输入指纹",
        ),
        sa.Column(
            "heading_path",
            sa.Text(),
            nullable=True,
            comment="切块标题路径",
        ),
        sa.Column(
            "model_key",
            sa.String(length=128),
            nullable=False,
            comment="嵌入模型标识",
        ),
        sa.Column("dimension", sa.Integer(), nullable=False, comment="向量维度"),
        sa.Column(
            "vector",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="float 数组",
        ),
        sa.Column(
            "create_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="创建时间",
        ),
        sa.UniqueConstraint(
            "corpus_id",
            "belong",
            "page_key",
            "chunk_index",
            name="uq_wiki_chunk_corpus_belong_page_idx",
        ),
    )
    op.create_index(
        "ix_wiki_chunk_embedding_hash",
        "wiki_chunk_embedding",
        ["corpus_id", "belong", "page_key", "chunk_hash"],
    )

    op.create_table(
        "wiki_corpus_binding",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
            comment="绑定主键",
        ),
        sa.Column("oid", sa.BigInteger(), nullable=False, comment="工作区 ID"),
        sa.Column(
            "datasource_id",
            sa.BigInteger(),
            nullable=False,
            comment="数据源 ID，同时仅绑一份语料",
        ),
        sa.Column(
            "corpus_id",
            sa.BigInteger(),
            sa.ForeignKey("wiki_corpus.id", ondelete="CASCADE"),
            nullable=False,
            comment="挂接的语料",
        ),
        sa.Column(
            "remap_databases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="语料库名 → 目标 DS 物理库名",
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="是否启用",
        ),
        sa.Column(
            "create_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "update_time",
            sa.DateTime(timezone=False),
            nullable=False,
            comment="更新时间",
        ),
        sa.UniqueConstraint("datasource_id", name="uq_wiki_corpus_binding_ds"),
    )
    op.create_index(
        "ix_wiki_corpus_binding_corpus", "wiki_corpus_binding", ["corpus_id"]
    )


def downgrade() -> None:
    op.drop_table("wiki_corpus_binding")
    op.drop_table("wiki_chunk_embedding")
    op.drop_table("wiki_page_revision")
    op.drop_table("wiki_page")
    op.drop_table("wiki_corpus")
