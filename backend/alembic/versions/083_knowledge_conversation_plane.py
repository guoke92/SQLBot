"""Conversation knowledge plane: unified asset model.

Revision ID: 083a1b2c3d4e5
Revises: 082a1b2c3d4e5
Create Date: 2026-08-07
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "083a1b2c3d4e5"
down_revision = "082a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_asset",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column(
            "kind",
            sa.String(length=32),
            nullable=False,
            comment="caliber|rule",
        ),
        sa.Column("natural_key", sa.String(length=128), nullable=False),
        sa.Column("lineage_id", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("superseded_by", sa.BigInteger(), nullable=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("datasource_id", sa.BigInteger(), nullable=True),
        sa.Column("assistant_id", sa.BigInteger(), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "trust_tier",
            sa.String(length=24),
            nullable=False,
            server_default="published",
            comment="staged|published|trusted|certified",
        ),
        sa.Column("certified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("valid_from", sa.DateTime(timezone=False), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("embedding_fingerprint", sa.String(length=64), nullable=True),
        sa.Column("create_by", sa.BigInteger(), nullable=True),
        sa.Column("certify_by", sa.BigInteger(), nullable=True),
        sa.Column("certify_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
    )
    op.create_index(
        "ix_knowledge_asset_oid_ds_enabled",
        "knowledge_asset",
        ["oid", "datasource_id", "enabled"],
    )
    op.create_index(
        "ix_knowledge_asset_lineage",
        "knowledge_asset",
        ["lineage_id"],
    )
    op.create_index(
        "ix_knowledge_asset_natural_key",
        "knowledge_asset",
        ["natural_key"],
    )
    op.create_index(
        "ix_knowledge_asset_bindable",
        "knowledge_asset",
        ["oid", "kind", "trust_tier", "certified", "enabled"],
    )

    op.create_table(
        "knowledge_schema_ref",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("asset_id", sa.BigInteger(), nullable=False),
        sa.Column("asset_kind", sa.String(length=32), nullable=False),
        sa.Column("datasource_id", sa.BigInteger(), nullable=False),
        sa.Column("table_name", sa.String(length=255), nullable=False),
        sa.Column("field_name", sa.String(length=255), nullable=True),
        sa.Column("table_id", sa.BigInteger(), nullable=True),
        sa.Column("field_id", sa.BigInteger(), nullable=True),
    )
    op.create_index(
        "ix_knowledge_schema_ref_asset",
        "knowledge_schema_ref",
        ["asset_id"],
    )
    op.create_index(
        "ix_knowledge_schema_ref_ds_table",
        "knowledge_schema_ref",
        ["datasource_id", "table_name"],
    )
    op.create_index(
        "ix_knowledge_schema_ref_field",
        "knowledge_schema_ref",
        ["field_id"],
    )

    op.create_table(
        "knowledge_evidence",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("asset_id", sa.BigInteger(), nullable=True),
        sa.Column("asset_kind", sa.String(length=32), nullable=False),
        sa.Column("natural_key", sa.String(length=128), nullable=True),
        sa.Column(
            "signal_kind",
            sa.String(length=32),
            nullable=False,
            comment="reproduce|apply_outcome|feedback|usage",
        ),
        sa.Column("record_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "fact",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
    )
    op.create_index(
        "ix_knowledge_evidence_asset",
        "knowledge_evidence",
        ["asset_id"],
    )
    op.create_index(
        "ix_knowledge_evidence_natural_key",
        "knowledge_evidence",
        ["natural_key"],
    )
    op.create_index(
        "ix_knowledge_evidence_signal_time",
        "knowledge_evidence",
        ["signal_kind", "create_time"],
    )

    op.create_table(
        "knowledge_episode",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("datasource_id", sa.BigInteger(), nullable=True),
        sa.Column("record_id", sa.BigInteger(), nullable=True),
        sa.Column("question_norm", sa.String(length=512), nullable=False),
        sa.Column(
            "episode",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
    )
    op.create_index(
        "ix_knowledge_episode_oid_ds",
        "knowledge_episode",
        ["oid", "datasource_id"],
    )

    op.create_table(
        "knowledge_staging",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False, comment="Workspace id"),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.String(length=24),
            nullable=False,
            comment="pending|rejected|promoted|expired",
        ),
        sa.Column("natural_key", sa.String(length=128), nullable=False),
        sa.Column(
            "scope",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("trigger_id", sa.String(length=32), nullable=False),
        sa.Column("source_record_id", sa.BigInteger(), nullable=True),
        sa.Column("suggested_trust_tier", sa.String(length=24), nullable=True),
        sa.Column(
            "quality_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "lineage_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("reject_reason", sa.Text(), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
    )
    op.create_index(
        "ix_knowledge_staging_oid_kind_status",
        "knowledge_staging",
        ["oid", "kind", "status"],
    )
    op.create_index(
        "ix_knowledge_staging_natural_key",
        "knowledge_staging",
        ["natural_key"],
    )
    op.create_index(
        "ix_knowledge_staging_source_record",
        "knowledge_staging",
        ["source_record_id"],
    )

    op.create_table(
        "knowledge_lineage_event",
        sa.Column("event_id", sa.String(length=64), primary_key=True),
        sa.Column("lineage_id", sa.String(length=64), nullable=False),
        sa.Column("asset_kind", sa.String(length=32), nullable=False),
        sa.Column("asset_id", sa.BigInteger(), nullable=True),
        sa.Column("asset_version", sa.Integer(), nullable=True),
        sa.Column("at", sa.DateTime(timezone=False), nullable=False),
        sa.Column(
            "actor",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("action", sa.String(length=48), nullable=False),
        sa.Column("from_tier", sa.String(length=24), nullable=True),
        sa.Column("to_tier", sa.String(length=24), nullable=True),
        sa.Column("trigger_id", sa.String(length=32), nullable=True),
        sa.Column(
            "refs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "evidence_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "decision",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_knowledge_lineage_event_lineage_at",
        "knowledge_lineage_event",
        ["lineage_id", "at"],
    )

    op.create_table(
        "knowledge_capture_job",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("record_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=24),
            nullable=False,
            comment="pending|running|succeeded|failed",
        ),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("lease_owner", sa.String(length=128), nullable=True),
        sa.Column("lease_until", sa.DateTime(timezone=False), nullable=True),
        sa.Column(
            "snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("create_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("update_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=False), nullable=True),
    )
    op.create_index(
        "ix_knowledge_capture_job_status_lease",
        "knowledge_capture_job",
        ["status", "lease_until"],
    )
    op.create_index(
        "ix_knowledge_capture_job_record",
        "knowledge_capture_job",
        ["record_id"],
    )

    op.add_column(
        "data_training",
        sa.Column(
            "knowledge_meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="lineage_id / trust_tier / natural_key for knowledge plane",
        ),
    )
    op.add_column(
        "terminology",
        sa.Column(
            "knowledge_meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="lineage_id / trust_tier / natural_key for knowledge plane",
        ),
    )


def downgrade() -> None:
    op.drop_column("terminology", "knowledge_meta")
    op.drop_column("data_training", "knowledge_meta")
    op.drop_index("ix_knowledge_capture_job_record", table_name="knowledge_capture_job")
    op.drop_index(
        "ix_knowledge_capture_job_status_lease", table_name="knowledge_capture_job"
    )
    op.drop_table("knowledge_capture_job")
    op.drop_index(
        "ix_knowledge_lineage_event_lineage_at", table_name="knowledge_lineage_event"
    )
    op.drop_table("knowledge_lineage_event")
    op.drop_index("ix_knowledge_staging_source_record", table_name="knowledge_staging")
    op.drop_index("ix_knowledge_staging_natural_key", table_name="knowledge_staging")
    op.drop_index(
        "ix_knowledge_staging_oid_kind_status", table_name="knowledge_staging"
    )
    op.drop_table("knowledge_staging")
    op.drop_index("ix_knowledge_episode_oid_ds", table_name="knowledge_episode")
    op.drop_table("knowledge_episode")
    op.drop_index("ix_knowledge_evidence_signal_time", table_name="knowledge_evidence")
    op.drop_index("ix_knowledge_evidence_natural_key", table_name="knowledge_evidence")
    op.drop_index("ix_knowledge_evidence_asset", table_name="knowledge_evidence")
    op.drop_table("knowledge_evidence")
    op.drop_index("ix_knowledge_schema_ref_field", table_name="knowledge_schema_ref")
    op.drop_index("ix_knowledge_schema_ref_ds_table", table_name="knowledge_schema_ref")
    op.drop_index("ix_knowledge_schema_ref_asset", table_name="knowledge_schema_ref")
    op.drop_table("knowledge_schema_ref")
    op.drop_index("ix_knowledge_asset_bindable", table_name="knowledge_asset")
    op.drop_index("ix_knowledge_asset_natural_key", table_name="knowledge_asset")
    op.drop_index("ix_knowledge_asset_lineage", table_name="knowledge_asset")
    op.drop_index("ix_knowledge_asset_oid_ds_enabled", table_name="knowledge_asset")
    op.drop_table("knowledge_asset")
