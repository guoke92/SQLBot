"""Unify conversation turns, run attempts and query intent storage.

Revision ID: 090a1b2c3d4e5
Revises: 089a1b2c3d4e5
Create Date: 2026-08-14

This is intentionally an incompatible semantic-store migration.  The old
QuerySpecification revisions are not execution-compatible with QueryIntent,
so they are discarded instead of being guessed into the new model.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "090a1b2c3d4e5"
down_revision = "089a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # One visible turn may be regenerated.  Runs are immutable attempts and
    # only one non-terminal attempt may own a chat at a time.
    op.drop_constraint(
        "conversation_run_chat_record_id_key",
        "conversation_run",
        type_="unique",
    )
    op.add_column("conversation_run", sa.Column("chat_id", sa.BigInteger()))
    op.add_column(
        "conversation_run",
        sa.Column("attempt_index", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "conversation_run",
        sa.Column(
            "route_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column("conversation_run", sa.Column("context_fingerprint", sa.String(64)))
    op.execute(
        """
        UPDATE conversation_run AS r
           SET chat_id = cr.chat_id
          FROM chat_record AS cr
         WHERE cr.id = r.chat_record_id
        """
    )
    op.drop_column("chat_record", "analysis_record_id")
    op.drop_column("chat_record", "predict_record_id")
    op.drop_column("chat_record", "regenerate_record_id")
    op.alter_column("conversation_run", "chat_id", nullable=False)
    op.create_unique_constraint(
        "uq_conversation_run_attempt",
        "conversation_run",
        ["chat_record_id", "attempt_index"],
    )
    op.create_index("ix_conversation_run_chat_id", "conversation_run", ["chat_id"])
    op.execute(
        """
        WITH ranked AS (
            SELECT run_id,
                   row_number() OVER (
                       PARTITION BY chat_id ORDER BY create_time DESC, run_id DESC
                   ) AS rn
              FROM conversation_run
             WHERE status IN ('queued', 'running', 'awaiting_input')
        )
        UPDATE conversation_run AS r
           SET status = 'failed',
               error_summary = 'Superseded during run-attempt migration',
               completed_at = COALESCE(completed_at, now()),
               update_time = now()
          FROM ranked
         WHERE ranked.run_id = r.run_id AND ranked.rn > 1
        """
    )
    op.create_index(
        "uq_conversation_run_active_chat",
        "conversation_run",
        ["chat_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued', 'running', 'awaiting_input')"),
    )

    op.add_column(
        "chat_record",
        sa.Column("turn_kind", sa.String(20), nullable=False, server_default="query"),
    )
    op.add_column(
        "chat_record",
        sa.Column(
            "relation", sa.String(20), nullable=False, server_default="independent"
        ),
    )
    op.add_column(
        "chat_record",
        sa.Column(
            "reference_record_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column("chat_record", sa.Column("active_run_id", sa.String(36)))
    op.add_column(
        "chat_record",
        sa.Column("answer_revision", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "chat_record",
        sa.Column("answer", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_foreign_key(
        "fk_chat_record_active_run",
        "chat_record",
        "conversation_run",
        ["active_run_id"],
        ["run_id"],
        ondelete="SET NULL",
    )
    op.execute(
        """
        UPDATE chat_record AS cr
           SET active_run_id = latest.run_id
          FROM (
                SELECT DISTINCT ON (chat_record_id) chat_record_id, run_id
                  FROM conversation_run
                 ORDER BY chat_record_id, attempt_index DESC, create_time DESC
               ) AS latest
         WHERE latest.chat_record_id = cr.id
        """
    )
    # Normal conversations now persist only TurnAnswerV1.  These columns stay
    # available to the separate config graph, but are not a second NLQ truth.
    op.execute(
        """
        UPDATE chat_record AS cr
           SET data = NULL,
               sql = NULL,
               chart = NULL,
               analysis = NULL,
               predict = NULL,
               predict_data = NULL,
               re_exec = NULL
          FROM chat AS c
         WHERE c.id = cr.chat_id AND COALESCE(c.chat_type, 'chat') <> 'config'
        """
    )

    # Old specifications/evidence encode a different semantic standard.  A
    # clean cut avoids keeping two executable truths in production.
    op.drop_table("nlq_evidence_event")
    op.drop_table("nlq_run")
    op.create_table(
        "query_run",
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "active_intent_revision", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "intent_revisions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "planning_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("planning_status", sa.String(24), nullable=False),
        sa.Column("active_plan_id", sa.String(36)),
        sa.Column(
            "plans",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "executions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("execution_status", sa.String(24), nullable=False),
        sa.Column(
            "executed_plan_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("result_quality", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
    )

    op.create_table(
        "conversation_evidence",
        sa.Column("evidence_id", sa.String(36), primary_key=True),
        sa.Column(
            "chat_record_id",
            sa.BigInteger(),
            sa.ForeignKey("chat_record.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by_run_id",
            sa.String(36),
            sa.ForeignKey("conversation_run.run_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("source", sa.String(24), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("structured_value", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "supersedes",
            sa.String(36),
            sa.ForeignKey("conversation_evidence.evidence_id", ondelete="SET NULL"),
        ),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint(
            "chat_record_id", "sequence", name="uq_conversation_evidence_sequence"
        ),
    )
    op.create_index(
        "ix_conversation_evidence_record",
        "conversation_evidence",
        ["chat_record_id"],
    )
    op.create_index(
        "ix_conversation_evidence_run",
        "conversation_evidence",
        ["created_by_run_id"],
    )

    op.create_table(
        "result_dataset",
        sa.Column("result_id", sa.String(36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dataset_id", sa.String(64), nullable=False),
        sa.Column("plan_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "fields",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "rows",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("row_count", sa.Integer()),
        sa.Column("truncated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "schema_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "statistics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("error", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint(
            "run_id", "dataset_id", "plan_id", name="uq_result_dataset_execution"
        ),
    )
    op.create_index("ix_result_dataset_run", "result_dataset", ["run_id"])

    # Legacy query-contract fragments are not valid QueryIntent defaults. Keep
    # their lineage/evidence for audit but remove them from runtime Bind until
    # an operator re-certifies a v1 intent-default fragment.
    op.execute(
        """
        UPDATE knowledge_asset
           SET enabled = false,
               certified = false,
               update_time = now()
         WHERE kind = 'caliber'
        """
    )
    op.execute(
        """
        UPDATE knowledge_staging
           SET status = 'rejected',
               update_time = now()
         WHERE kind = 'caliber' AND status = 'pending'
        """
    )


def downgrade() -> None:
    # This revision intentionally has no semantic downgrade.  Recreating the
    # old QuerySpecification store would fabricate data the upgrade discards.
    raise RuntimeError("090_unified_turn_query_intent is not reversible")
