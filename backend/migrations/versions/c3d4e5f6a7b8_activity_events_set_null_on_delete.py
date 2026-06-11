"""activity_events: set null on group/match delete

Revision ID: c3d4e5f6a7b8
Revises: 6b9f6c63fbe0
Create Date: 2026-06-11 07:30:00.000000

Switch the foreign keys on activity_events.group_id and activity_events.match_id
to ON DELETE SET NULL so deleting a prediction_group (or a match) does not
violate referential integrity. Historical activity events are preserved with
group_id / match_id set to NULL.

Defensive (idempotent) on purpose: the activity_events table was created
outside of Alembic in some environments, so constraint names may vary or be
missing. Each step is wrapped in IF EXISTS / DO blocks.

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = '6b9f6c63fbe0'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # group_id FK -> ON DELETE SET NULL
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events DROP CONSTRAINT IF EXISTS activity_events_group_id_fkey;
        EXCEPTION WHEN others THEN NULL;
        END $$;
    '''))
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events
                ADD CONSTRAINT activity_events_group_id_fkey
                FOREIGN KEY (group_id) REFERENCES prediction_groups(id)
                ON DELETE SET NULL;
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    '''))

    # match_id FK -> ON DELETE SET NULL
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events DROP CONSTRAINT IF EXISTS activity_events_match_id_fkey;
        EXCEPTION WHEN others THEN NULL;
        END $$;
    '''))
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events
                ADD CONSTRAINT activity_events_match_id_fkey
                FOREIGN KEY (match_id) REFERENCES matches(id)
                ON DELETE SET NULL;
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    '''))


def downgrade():
    conn = op.get_bind()

    # Revert match_id FK
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events DROP CONSTRAINT IF EXISTS activity_events_match_id_fkey;
        EXCEPTION WHEN others THEN NULL;
        END $$;
    '''))
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events
                ADD CONSTRAINT activity_events_match_id_fkey
                FOREIGN KEY (match_id) REFERENCES matches(id);
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    '''))

    # Revert group_id FK
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events DROP CONSTRAINT IF EXISTS activity_events_group_id_fkey;
        EXCEPTION WHEN others THEN NULL;
        END $$;
    '''))
    conn.execute(sa.text('''
        DO $$ BEGIN
            ALTER TABLE activity_events
                ADD CONSTRAINT activity_events_group_id_fkey
                FOREIGN KEY (group_id) REFERENCES prediction_groups(id);
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    '''))
