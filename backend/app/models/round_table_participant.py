# app/models/round_table_participant.py

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.session import Base

class RoundTableParticipant(Base):
    __tablename__ = "round_table_participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    round_table_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("round_tables.id", ondelete="CASCADE"),
        nullable=False
    )
    agent_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False
    )
    role = Column(String(50))
    speaking_priority = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Add relationships
    agent = relationship("Agent", back_populates="round_table_participants")
    round_table = relationship("RoundTable", back_populates="participants") 