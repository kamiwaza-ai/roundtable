"""add cascade delete

Revision ID: 0e5d49010756
Revises: b3baae19d7db
Create Date: 2025-01-06 12:06:22.445115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e5d49010756'
down_revision: Union[str, None] = 'b3baae19d7db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('round_table_participants_agent_id_fkey', 'round_table_participants', type_='foreignkey')
    op.drop_constraint('round_table_participants_round_table_id_fkey', 'round_table_participants', type_='foreignkey')
    op.create_foreign_key(None, 'round_table_participants', 'round_tables', ['round_table_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'round_table_participants', 'agents', ['agent_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'round_table_participants', type_='foreignkey')
    op.drop_constraint(None, 'round_table_participants', type_='foreignkey')
    op.create_foreign_key('round_table_participants_round_table_id_fkey', 'round_table_participants', 'round_tables', ['round_table_id'], ['id'])
    op.create_foreign_key('round_table_participants_agent_id_fkey', 'round_table_participants', 'agents', ['agent_id'], ['id'])
    # ### end Alembic commands ###