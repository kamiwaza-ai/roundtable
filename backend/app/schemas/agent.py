# app/schemas/agent.py
from uuid import UUID
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re

class KamiwazaLLMConfig(BaseModel):
    provider: str = "kamiwaza"
    model_name: str
    host_name: str
    port: int
    temperature: float = 0.7
    max_tokens: int = 150

class AzureLLMConfig(BaseModel):
    api_type: str = "azure"
    model: str
    api_key: str
    azure_endpoint: str
    api_version: str = "2024-02-15-preview"
    temperature: float = 0.7
    max_tokens: int = 150

class AgentBase(BaseModel):
    name: str
    title: str
    background: str
    agent_type: str = "standard"
    llm_config: Dict[str, Any]
    tool_config: Optional[Dict] = None

class AgentCreate(BaseModel):
    name: str
    title: str
    background: str
    agent_type: str = "assistant"
    llm_config: Union[KamiwazaLLMConfig, AzureLLMConfig, Dict[str, Any]]
    tool_config: Optional[Dict[str, Any]] = None

    @field_validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Name must contain only letters, numbers, underscores, and hyphens')
        return v

    @field_validator('llm_config')
    def validate_llm_config(cls, v):
        if isinstance(v, (KamiwazaLLMConfig, AzureLLMConfig)):
            return v.model_dump()
        
        # If it's a dict, validate it has minimum required fields
        if isinstance(v, dict):
            if "config_list" in v:
                return v
            
            if "provider" in v and v["provider"] == "kamiwaza":
                if not all(k in v for k in ["model_name", "port"]):
                    raise ValueError("Kamiwaza config must include model_name and port")
            elif "api_type" in v and v["api_type"] == "azure":
                if not all(k in v for k in ["model", "api_key", "azure_endpoint"]):
                    raise ValueError("Azure config must include model, api_key, and azure_endpoint")
            else:
                raise ValueError("Invalid LLM configuration")
        
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