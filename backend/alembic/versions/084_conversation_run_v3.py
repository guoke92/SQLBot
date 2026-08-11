"""Durable conversation runs, interrupts, NLQ revisions and evidence.

Revision ID: 084a1b2c3d4e5
Revises: 083a1b2c3d4e5
Create Date: 2026-08-10
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "084a1b2c3d4e5"
down_revision = "083a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_run",
        sa.Column("run_id", sa.String(length=36), primary_key=True),
        sa.Column(
            "chat_record_id",
            sa.BigInteger(),
            sa.ForeignKey("chat_record.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("graph_key", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("current_node", sa.String(length=64), nullable=True),
        sa.Column("checkpoint_id", sa.String(length=128), nullable=True),
        sa.Column("active_interrupt_id", sa.String(length=36), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("assistant_id", sa.BigInteger(), nullable=True),
        sa.Column("oid", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("event_cursor", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
    )
    op.create_index("ix_conversation_run_status", "conversation_run", ["status"])
    op.create_index("ix_conversation_run_user", "conversation_run", ["user_id"])

    op.create_table(
        "conversation_run_event",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), primary_key=True
        ),
        sa.Column(
            "run_id",
            sa.String(length=36),
            sa.ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cursor", sa.Integer(), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint("run_id", "cursor", name="uq_run_event_cursor"),
    )
    op.create_index("ix_run_event_run", "conversation_run_event", ["run_id"])

    op.create_table(
        "conversation_interrupt",
        sa.Column("interrupt_id", sa.String(length=36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(length=36),
            sa.ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=False), nullable=True),
        sa.UniqueConstraint("run_id", "version", name="uq_interrupt_run_version"),
        sa.UniqueConstraint(
            "run_id", "idempotency_key", name="uq_interrupt_idempotency"
        ),
    )
    op.create_index("ix_interrupt_run", "conversation_interrupt", ["run_id"])
    op.create_index("ix_interrupt_status", "conversation_interrupt", ["status"])

    op.create_table(
        "nlq_run",
        sa.Column(
            "run_id",
            sa.String(length=36),
            sa.ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "active_specification_revision",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "specifications",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("planning_status", sa.String(length=24), nullable=False),
        sa.Column("active_plan_id", sa.String(length=36), nullable=True),
        sa.Column(
            "plans",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("execution_status", sa.String(length=24), nullable=False),
        sa.Column(
            "executed_plan_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "result_quality", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
    )

    op.create_table(
        "nlq_evidence_event",
        sa.Column("evidence_id", sa.String(length=36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(length=36),
            sa.ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=24), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "structured_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "supersedes",
            sa.String(length=36),
            sa.ForeignKey("nlq_evidence_event.evidence_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint("run_id", "sequence", name="uq_nlq_evidence_sequence"),
    )
    op.create_index("ix_nlq_evidence_run", "nlq_evidence_event", ["run_id"])

    op.drop_index("uq_chat_record_clarification_parent", table_name="chat_record")
    op.drop_column("chat_record", "clarification_parent_id")
    op.drop_column("chat_record", "intent_context")


def downgrade() -> None:
    op.add_column(
        "chat_record",
        sa.Column("intent_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "chat_record",
        sa.Column(
            "clarification_parent_id",
            sa.BigInteger(),
            sa.ForeignKey("chat_record.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "uq_chat_record_clarification_parent",
        "chat_record",
        ["clarification_parent_id"],
        unique=True,
        postgresql_where=sa.text("clarification_parent_id IS NOT NULL"),
    )
    op.drop_table("nlq_evidence_event")
    op.drop_table("nlq_run")
    op.drop_table("conversation_interrupt")
    op.drop_table("conversation_run_event")
    op.drop_table("conversation_run")
