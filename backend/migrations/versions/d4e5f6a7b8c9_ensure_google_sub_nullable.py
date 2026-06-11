"""ensure google_sub is nullable

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-11 07:40:00.000000

The original migration 6b9f6c63fbe0 was supposed to make users.google_sub
nullable (so email+password users could be created without a Google sub),
but it failed mid-way in production on 2026-06-09 and the previous
entrypoint silently masked the failure with `flask db stamp head`.

Result: prod DB had password_hash added but google_sub stayed NOT NULL.
This migration is the explicit, idempotent fix. It is safe to run on:
- prod databases where google_sub is still NOT NULL (it drops the constraint)
- fresh / staging databases where google_sub is already nullable (no-op)

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    # DROP NOT NULL is idempotent in Postgres — running it on an already-nullable
    # column is a no-op, so no defensive wrapper needed.
    op.alter_column(
        'users',
        'google_sub',
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
    )


def downgrade():
    # NOTE: this downgrade can fail if any user row has google_sub IS NULL
    # (e.g. an email+password user). That is intentional — refusing to recreate
    # a constraint that would be violated by existing data is correct behavior.
    op.alter_column(
        'users',
        'google_sub',
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
    )
