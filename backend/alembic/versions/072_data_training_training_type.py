"""add training_type to data_training

Revision ID: 072a1b2c3d4e5
Revises: 071a2b3c4d5e6
Create Date: 2026-07-16
"""
from alembic import op
import sqlalchemy as sa

revision = '072a1b2c3d4e5'
down_revision = '071a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('data_training', sa.Column('training_type', sa.String(16), server_default='sql'))


def downgrade() -> None:
    op.drop_column('data_training', 'training_type')
