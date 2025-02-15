# app/models/round_table.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from ..db.session import Base
from sqlalchemy.orm import relationship


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
    messages_state = Column(JSON, nullable=True)  # Store serialized chat state for pause/resume
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Add relationships
    participants = relationship(
        "RoundTableParticipant",
        back_populates="round_table",
        cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message",
        back_populates="round_table",
        cascade="all, delete-orphan"
    )