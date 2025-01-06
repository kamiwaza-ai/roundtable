"""Fix round table participant relationships

Revision ID: b3baae19d7db
Revises: 87b2a0f84789
Create Date: 2025-01-06 12:03:36.444716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3baae19d7db'
down_revision: Union[str, None] = '87b2a0f84789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('round_table_participants_agent_id_fkey', 'round_table_participants', type_='foreignkey')
    op.drop_constraint('round_table_participants_round_table_id_fkey', 'round_table_participants', type_='foreignkey')
    
    # Re-create foreign key constraints with CASCADE
    op.create_foreign_key(
        'round_table_participants_agent_id_fkey',
        'round_table_participants', 'agents',
        ['agent_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'round_table_participants_round_table_id_fkey',
        'round_table_participants', 'round_tables',
        ['round_table_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    # Drop CASCADE foreign key constraints
    op.drop_constraint('round_table_participants_agent_id_fkey', 'round_table_participants', type_='foreignkey')
    op.drop_constraint('round_table_participants_round_table_id_fkey', 'round_table_participants', type_='foreignkey')
    
    # Re-create original foreign key constraints
    op.create_foreign_key(
        'round_table_participants_agent_id_fkey',
        'round_table_participants', 'agents',
        ['agent_id'], ['id']
    )
    op.create_foreign_key(
        'round_table_participants_round_table_id_fkey',
        'round_table_participants', 'round_tables',
        ['round_table_id'], ['id']
    )