"""add messages_state to round_table

Revision ID: 41dc3daf566b
Revises: previous_revision
Create Date: 2024-01-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41dc3daf566b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add messages_state column to round_tables
    op.add_column('round_tables', sa.Column('messages_state', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove messages_state column from round_tables
    op.drop_column('round_tables', 'messages_state')
