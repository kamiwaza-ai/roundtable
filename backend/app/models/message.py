# app/models/message.py

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.session import Base

class Message(Base):
    __tablename__ = "messages"
    
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
    content = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)  # introduction, discussion, conclusion
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Add relationships
    agent = relationship("Agent", back_populates="messages")
    round_table = relationship("RoundTable", back_populates="messages")
