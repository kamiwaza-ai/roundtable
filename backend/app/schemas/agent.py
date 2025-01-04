# app/schemas/agent.py
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re

class AgentBase(BaseModel):
    name: str
    title: str
    background: str
    agent_type: str = "standard"
    llm_config: Dict
    tool_config: Optional[Dict] = None

class AgentCreate(BaseModel):
    name: str
    title: str
    background: str
    agent_type: str = "assistant"
    llm_config: Dict[str, Any]
    tool_config: Optional[Dict[str, Any]] = None

    @field_validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Name must contain only letters, numbers, underscores, and hyphens')
        return v

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