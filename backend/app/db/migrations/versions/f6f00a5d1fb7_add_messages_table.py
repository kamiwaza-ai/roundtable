"""add_messages_table

Revision ID: f6f00a5d1fb7
Revises: 2242ffd652c5
Create Date: 2025-01-06 12:39:35.352021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6f00a5d1fb7'
down_revision: Union[str, None] = '2242ffd652c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
