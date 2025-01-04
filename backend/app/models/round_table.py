# app/models/round_table.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from ..db.session import Base

class RoundTable(Base):
    __tablename__ = "round_tables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    objective = Column(String, nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, active, completed
    phase_config = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=False, default={})
    current_phase = Column(String(50))
    max_rounds = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))

class RoundTableParticipant(Base):
    __tablename__ = "round_table_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_table_id = Column(UUID(as_uuid=True), ForeignKey("round_tables.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    role = Column(String(50))
    speaking_priority = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)