# app/schemas/agent.py
from uuid import UUID
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    title: str
    background: str
    agent_type: str = "standard"
    llm_config: Dict
    tool_config: Optional[Dict] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    title: Optional[str] = None
    background: Optional[str] = None
    agent_type: Optional[str] = None
    llm_config: Optional[Dict] = None
    tool_config: Optional[Dict] = None
    is_active: Optional[bool] = None

class AgentInDB(AgentBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True