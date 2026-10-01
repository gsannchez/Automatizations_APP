"""Add scenes_data to GeneratedVideo

Revision ID: 4ec356ef86c0
Revises: 18f2a42d12c9
Create Date: 2026-05-22 17:17:53.343420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ec356ef86c0'
down_revision: Union[str, None] = '18f2a42d12c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from sqlalchemy.dialects import postgresql
import sqlmodel

def upgrade() -> None:
    op.add_column('video', sa.Column('scenes_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('video', 'scenes_data')
