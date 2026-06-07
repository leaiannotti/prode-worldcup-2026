"""add team identity columns

Revision ID: a1b2c3d4e5f6
Revises: 6397fc500673
Create Date: 2026-06-07 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '6397fc500673'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('teams', sa.Column('name', sa.String(100), nullable=False, server_default=''))
    op.add_column('teams', sa.Column('flag_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('teams', 'flag_url')
    op.drop_column('teams', 'name')
