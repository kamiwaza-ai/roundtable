# Import all the models here for Alembic to detect
from app.db.session import Base
from app.models.agent import Agent
from app.models.round_table import RoundTable
from app.models.round_table_participant import RoundTableParticipant
from app.models.message import Message

# This allows Alembic to detect the models
