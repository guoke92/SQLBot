"""Drop legacy knowledge tables (package/unit/composition/node/staging/lineage).

Legacy knowledge package and composition planes are retired in favor of the unified
wiki knowledge system.

Revision ID: 098a1b2c3d4e5
Revises: 097a1b2c3d4e5
Create Date: 2026-09-03
"""

from alembic import op

revision = "098a1b2c3d4e5"
down_revision = "097a1b2c3d4e5"
branch_labels = None
depends_on = None

# Drop in reverse topological order of foreign key dependencies
_LEGACY_TABLES = [
    # Composition & node indexes/deployments
    "knowledge_node_index",
    "composition_deployment",
    "composition_binding",
    "unit_composition",
    "knowledge_edge",
    "knowledge_merge_conflict",
    "knowledge_node_version",
    "knowledge_node",
    # Units & deployments
    "knowledge_deployment",
    "knowledge_binding",
    "knowledge_unit_revision",
    "knowledge_source_evidence",
    "knowledge_unit",
    "knowledge_package",
    # Legacy assets, evidence & staging
    "knowledge_schema_ref",
    "knowledge_evidence",
    "knowledge_episode",
    "knowledge_staging",
    "knowledge_lineage_event",
    "knowledge_capture_job",
    "knowledge_asset",
]


def upgrade() -> None:
    for table_name in _LEGACY_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")


def downgrade() -> None:
    # Legacy tables are retired permanently.
    pass
