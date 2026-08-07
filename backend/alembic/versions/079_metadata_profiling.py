"""Metadata cognition: scan runs, field profiles, relations, table profile status.

Revision ID: 079a1b2c3d4e5
Revises: 078a1b2c3d4e5
Create Date: 2026-08-06
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "079a1b2c3d4e5"
down_revision = "078a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "core_table",
        sa.Column(
            "active_profile_generation",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
            comment="Published field-profile generation for this table",
        ),
    )
    op.add_column(
        "core_table",
        sa.Column(
            "profile_status",
            sa.String(length=24),
            nullable=False,
            server_default="EMPTY",
            comment="EMPTY/PROFILING/READY/STALE/UNSUPPORTED/FAILED",
        ),
    )
    op.add_column(
        "core_table",
        sa.Column(
            "schema_fingerprint",
            sa.String(length=64),
            nullable=True,
            comment="Hash of table+field structural identity",
        ),
    )
    op.add_column(
        "core_table",
        sa.Column(
            "profile_error",
            sa.Text(),
            nullable=True,
            comment="Last profiling error message",
        ),
    )
    op.add_column(
        "core_table",
        sa.Column(
            "profile_updated_at",
            sa.DateTime(timezone=False),
            nullable=True,
            comment="When active profile generation was published",
        ),
    )

    op.create_table(
        "metadata_scan_run",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column(
            "ds_id",
            sa.BigInteger(),
            sa.ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "table_id",
            sa.BigInteger(),
            sa.ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("run_mode", sa.String(length=32), nullable=False),
        sa.Column("trigger", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("lease_owner", sa.String(length=128), nullable=True),
        sa.Column("lease_until", sa.DateTime(timezone=False), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column(
            "targets",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Optional table_ids/field_ids/task_types",
        ),
        sa.Column("schema_fingerprint", sa.String(length=64), nullable=True),
        sa.Column("data_watermark", sa.String(length=128), nullable=True),
        sa.Column("pending_generation", sa.BigInteger(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("graph_run_id", sa.String(length=64), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=False), nullable=True),
    )
    op.create_index(
        "ix_metadata_scan_run_status_lease",
        "metadata_scan_run",
        ["status", "lease_until"],
    )
    op.create_index(
        "ix_metadata_scan_run_ds_table",
        "metadata_scan_run",
        ["ds_id", "table_id"],
    )

    op.create_table(
        "field_profile_snapshot",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "scan_id",
            sa.BigInteger(),
            sa.ForeignKey("metadata_scan_run.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "ds_id",
            sa.BigInteger(),
            sa.ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "table_id",
            sa.BigInteger(),
            sa.ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "field_id",
            sa.BigInteger(),
            sa.ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("generation", sa.BigInteger(), nullable=False),
        sa.Column("window_code", sa.String(length=16), nullable=False, server_default="ALL"),
        sa.Column("row_count", sa.BigInteger(), nullable=True),
        sa.Column("non_null_count", sa.BigInteger(), nullable=True),
        sa.Column("null_rate", sa.Float(), nullable=True),
        sa.Column("approx_distinct", sa.BigInteger(), nullable=True),
        sa.Column("distinct_ratio", sa.Float(), nullable=True),
        sa.Column("min_value", sa.Text(), nullable=True),
        sa.Column("max_value", sa.Text(), nullable=True),
        sa.Column("top_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("extended_stats", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("sample_method", sa.String(length=32), nullable=True),
        sa.Column("sample_size", sa.BigInteger(), nullable=True),
        sa.Column("algo_version", sa.String(length=32), nullable=False, server_default="v1"),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="READY"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("profiled_at", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint(
            "field_id",
            "window_code",
            "generation",
            name="uq_field_profile_generation_window",
        ),
    )
    op.create_index(
        "ix_field_profile_table_generation",
        "field_profile_snapshot",
        ["table_id", "generation"],
    )
    op.create_index(
        "ix_field_profile_ds_field",
        "field_profile_snapshot",
        ["ds_id", "field_id"],
    )

    op.create_table(
        "field_relation",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column(
            "ds_id",
            sa.BigInteger(),
            sa.ForeignKey("core_datasource.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_table_id",
            sa.BigInteger(),
            sa.ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_field_id",
            sa.BigInteger(),
            sa.ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_table_id",
            sa.BigInteger(),
            sa.ForeignKey("core_table.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_field_id",
            sa.BigInteger(),
            sa.ForeignKey("core_field.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("cardinality", sa.String(length=16), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("infer_generation", sa.BigInteger(), nullable=True),
        sa.Column("algo_version", sa.String(length=32), nullable=True),
        sa.Column("confirmed_by", sa.BigInteger(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
        sa.UniqueConstraint(
            "ds_id",
            "source_field_id",
            "target_field_id",
            "kind",
            name="uq_field_relation_endpoints_kind",
        ),
    )
    op.create_index("ix_field_relation_ds_status", "field_relation", ["ds_id", "status"])
    op.create_index(
        "ix_field_relation_source_table",
        "field_relation",
        ["source_table_id"],
    )


def downgrade() -> None:
    op.drop_table("field_relation")
    op.drop_table("field_profile_snapshot")
    op.drop_table("metadata_scan_run")
    op.drop_column("core_table", "profile_updated_at")
    op.drop_column("core_table", "profile_error")
    op.drop_column("core_table", "schema_fingerprint")
    op.drop_column("core_table", "profile_status")
    op.drop_column("core_table", "active_profile_generation")
