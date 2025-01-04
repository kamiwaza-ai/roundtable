"""add_round_table_tables

Revision ID: 2885bbe13275
Revises: 734e975b3251
Create Date: 2025-01-04 13:39:01.234444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2885bbe13275'
down_revision: Union[str, None] = '734e975b3251'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('round_tables',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('objective', sa.String(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('phase_config', sa.JSON(), nullable=False),
    sa.Column('settings', sa.JSON(), nullable=False),
    sa.Column('current_phase', sa.String(length=50), nullable=True),
    sa.Column('max_rounds', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('round_table_participants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('round_table_id', sa.UUID(), nullable=False),
    sa.Column('agent_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.Column('speaking_priority', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['round_table_id'], ['round_tables.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('round_table_participants')
    op.drop_table('round_tables')
    # ### end Alembic commands ###
