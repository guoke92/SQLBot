"""Persist deterministic query risk and semantic review artifacts.

Revision ID: 093a1b2c3d4e5
Revises: 092a1b2c3d4e5
Create Date: 2026-08-14
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "093a1b2c3d4e5"
down_revision = "092a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name, default in (
        ("agent_decision", "{}"),
        ("hard_gate_report", "{}"),
        ("risk_assessment", "{}"),
        ("semantic_reviews", "[]"),
        ("repair_history", "[]"),
    ):
        op.add_column(
            "query_run",
            sa.Column(
                name,
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text(f"'{default}'::jsonb"),
            ),
        )


def downgrade() -> None:
    for name in (
        "repair_history",
        "semantic_reviews",
        "risk_assessment",
        "hard_gate_report",
        "agent_decision",
    ):
        op.drop_column("query_run", name)
