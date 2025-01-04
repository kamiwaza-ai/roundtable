# app/models/round_table.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from ..db.session import Base


class RoundTable(Base):
    __tablename__ = "round_tables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    context = Column(String, nullable=False)  # This will store our objective/context
    status = Column(String, default="pending")  # pending, active, completed
    settings = Column(JSON, nullable=False, default={
        "max_rounds": 12,
        "speaker_selection_method": "auto",
        "allow_repeat_speaker": True,
        "send_introductions": True
    })
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class RoundTableParticipant(Base):
    __tablename__ = "round_table_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_table_id = Column(UUID(as_uuid=True), ForeignKey("round_tables.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    role = Column(String(50))
    speaking_priority = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)