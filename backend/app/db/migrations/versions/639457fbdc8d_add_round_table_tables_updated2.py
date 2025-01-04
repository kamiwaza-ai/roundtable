"""add_round_table_tables_updated2

Revision ID: 639457fbdc8d
Revises: 85131176a608
Create Date: 2025-01-04 14:44:17.172845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '639457fbdc8d'
down_revision: Union[str, None] = '85131176a608'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('round_tables', sa.Column('status', sa.String(), nullable=True))
    op.alter_column('round_tables', 'context',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('round_tables', 'context',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('round_tables', 'status')
    # ### end Alembic commands ###
