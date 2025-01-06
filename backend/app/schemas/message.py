from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class MessageBase(BaseModel):
    content: str
    message_type: str
    agent_id: UUID
    round_table_id: UUID

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "content": "Hello, this is a message",
                "message_type": "discussion",
                "agent_id": "123e4567-e89b-12d3-a456-426614174000",
                "round_table_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
