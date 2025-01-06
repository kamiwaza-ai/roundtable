from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..db.session import Base
from sqlalchemy.orm import relationship


class Agent(Base):
    __tablename__ = "agents"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    background = Column(String, nullable=False)  # System message/personality
    agent_type = Column(String(50), nullable=False, default="standard")
    llm_config = Column(JSON, nullable=False)
    tool_config = Column(JSON)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship with cascade delete
    round_table_participants = relationship(
        "RoundTableParticipant",
        back_populates="agent",
        cascade="all, delete-orphan"
    )


class AgentCapability(Base):
    __tablename__ = "agent_capabilities"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    agent_id = Column(PGUUID, nullable=False)
    capability_type = Column(String(50), nullable=False)
    capability_config = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)