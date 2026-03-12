"""add_videos_user_id_index

Revision ID: 18f2a42d12c9
Revises: 001_initial_schema
Create Date: 2026-03-09 17:22:09.993113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18f2a42d12c9'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Safely create the index using IF NOT EXISTS logic
    op.execute("CREATE INDEX IF NOT EXISTS videos_user_id_idx ON video(user_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS videos_user_id_idx")
