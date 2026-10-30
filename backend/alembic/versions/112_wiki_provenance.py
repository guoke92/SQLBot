"""Wiki material locators, patch provenance, and revision stamps.

Revision ID: 112a1b2c3d4e5
Revises: 111a1b2c3d4e5
Create Date: 2026-10-12
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "112a1b2c3d4e5"
down_revision = "111a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("wiki_source"):
        columns = {col["name"] for col in inspector.get_columns("wiki_source")}
        if "locator" not in columns:
            op.add_column(
                "wiki_source",
                sa.Column("locator", sa.String(length=512), nullable=False, server_default="", comment="稳定定位符"),
            )
        if "toolset" not in columns:
            op.add_column(
                "wiki_source",
                sa.Column("toolset", sa.String(length=32), nullable=False, server_default="", comment="只读工具集"),
            )
        if "content_sha" not in columns:
            op.add_column(
                "wiki_source",
                sa.Column("content_sha", sa.String(length=64), nullable=False, server_default="", comment="正文哈希"),
            )
        op.execute(
            """
            UPDATE wiki_source
            SET locator = 'document:' || id::text,
                toolset = 'document'
            WHERE kind = 'document' AND locator = ''
            """
        )
        op.execute(
            """
            UPDATE wiki_source
            SET locator = 'conversation:' || COALESCE(pointer->>'chat_id', '0')
                    || '/' || COALESCE(pointer->>'record_id', id::text),
                toolset = 'conversation'
            WHERE kind = 'conversation' AND locator = ''
            """
        )
        indexes = {idx["name"] for idx in inspector.get_indexes("wiki_source")}
        if "uq_wiki_source_locator" not in indexes:
            op.create_index(
                "uq_wiki_source_locator",
                "wiki_source",
                ["corpus_id", "locator"],
                unique=True,
            )

    if inspector.has_table("wiki_page_patch"):
        columns = {col["name"] for col in inspector.get_columns("wiki_page_patch")}
        additions = [
            ("source_id", sa.BigInteger(), True, None, "原料主键"),
            ("toolset", sa.String(length=32), False, "", "工具集"),
            ("tool_name", sa.String(length=64), False, "", "加工方式"),
            ("aspect", sa.String(length=32), False, "", "主张方面"),
            ("trust", sa.String(length=32), False, "", "盖章后的可信度"),
            ("revision_no", sa.Integer(), True, None, "纳入的修订号"),
            ("interrupt_id", sa.String(length=64), True, None, "确认中断"),
        ]
        for name, type_, nullable, default, comment in additions:
            if name in columns:
                continue
            op.add_column(
                "wiki_page_patch",
                sa.Column(name, type_, nullable=nullable, server_default=default, comment=comment),
            )
        if "observation" not in columns:
            op.add_column(
                "wiki_page_patch",
                sa.Column(
                    "observation",
                    postgresql.JSONB(astext_type=sa.Text()),
                    nullable=False,
                    server_default=sa.text("'{}'::jsonb"),
                    comment="提案时冻结的摘录与原料哈希",
                ),
            )
        op.execute(
            """
            UPDATE wiki_page_patch AS patch
            SET revision_no = rev.revision_no
            FROM (
                SELECT page_id, MAX(revision_no) AS revision_no
                FROM wiki_page_revision
                GROUP BY page_id
            ) AS rev
            WHERE patch.page_id = rev.page_id
              AND patch.revision_no IS NULL
              AND patch.status IN ('applied', 'conflicted')
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("wiki_page_patch"):
        columns = {col["name"] for col in inspector.get_columns("wiki_page_patch")}
        for name in (
            "observation",
            "interrupt_id",
            "revision_no",
            "trust",
            "aspect",
            "tool_name",
            "toolset",
            "source_id",
        ):
            if name in columns:
                op.drop_column("wiki_page_patch", name)
    if inspector.has_table("wiki_source"):
        indexes = {idx["name"] for idx in inspector.get_indexes("wiki_source")}
        if "uq_wiki_source_locator" in indexes:
            op.drop_index("uq_wiki_source_locator", table_name="wiki_source")
        columns = {col["name"] for col in inspector.get_columns("wiki_source")}
        for name in ("content_sha", "toolset", "locator"):
            if name in columns:
                op.drop_column("wiki_source", name)
