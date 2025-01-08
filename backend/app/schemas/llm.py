# app/schemas/llm.py

from typing import Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
import re

class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration"""
    api_key: str
    azure_endpoint: str
    api_version: str = "2024-02-15-preview"
    model: str = "gpt-4o"
    temperature: float = 0.7
    
    @validator('azure_endpoint')
    def validate_endpoint(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Azure endpoint must start with http:// or https://')
        return v.rstrip('/')
        
    @validator('model')
    def validate_model(cls, v):
        allowed = ['gpt-4o', 'gpt-4o-mini']
        if v not in allowed:
            raise ValueError(f'Model must be one of: {allowed}')
        return v

class OpenAIConfig(BaseModel):
    """OpenAI configuration"""
    api_key: str
    model: str = "gpt-4"
    api_base: Optional[str] = None
    temperature: float = 0.7

class KamiwazaConfig(BaseModel):
    """Kamiwaza configuration"""
    model_name: str  # This will be the display name
    model_id: str    # This will be the full path ID from /v1/models
    host_name: str = "localhost"
    port: int
    temperature: float = 0.7
    max_tokens: int = 150
    provider: Literal["kamiwaza"] = "kamiwaza"

    def to_ag2_config(self) -> Dict[str, Any]:
        """Convert to AG2 format"""
        return {
            "model": self.model_id,  # Use full path ID here
            "base_url": f"http://{self.host_name}:{self.port}/v1"
        }
class LLMConfig(BaseModel):
    """Combined LLM configuration"""
    azure_config: Optional[AzureOpenAIConfig] = None
    openai_config: Optional[OpenAIConfig] = None
    kamiwaza_config: Optional[KamiwazaConfig] = None
    
    def get_active_config(self) -> Union[AzureOpenAIConfig, OpenAIConfig, KamiwazaConfig]:
        """Get the active configuration to use"""
        if self.azure_config:
            return self.azure_config
        elif self.kamiwaza_config:
            return self.kamiwaza_config
        elif self.openai_config:
            return self.openai_config
        raise ValueError("No valid LLM configuration found")