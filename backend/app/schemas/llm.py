from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field, field_validator


class BaseLLMConfig(BaseModel):
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    timeout: Optional[int] = Field(default=60, gt=0)

class AzureOpenAIConfig(BaseLLMConfig):
    provider: Literal["azure"] = "azure"
    api_key: str
    azure_endpoint: str
    api_version: str = "2024-08-01-preview" 
    
    @field_validator("model")
    def validate_model(cls, v):
        # Add your specific Azure model deployments here
        valid_models = [
            "gpt-4o",
            "gpt-4o-mini",
        ]
        if v not in valid_models:
            raise ValueError(f"Model must be one of {valid_models}")
        return v

    @field_validator("azure_endpoint")
    def validate_endpoint(cls, v):
        if not v.startswith(("https://", "http://")):
            raise ValueError("Azure endpoint must be a valid URL starting with https:// or http://")
        return v

class OpenAIConfig(BaseLLMConfig):
    provider: Literal["openai"] = "openai"
    api_key: str
    api_base: Optional[str] = "https://api.openai.com/v1"

class LLMConfig(BaseModel):
    azure_config: Optional[AzureOpenAIConfig] = None
    openai_config: Optional[OpenAIConfig] = None
    
    @field_validator("azure_config", "openai_config")
    def validate_one_config_present(cls, v, values):
        if not v and not any(values.values()):
            raise ValueError("At least one configuration must be provided")
        return v

    def get_active_config(self):
        """Returns the active configuration (prioritizing Azure)"""
        return self.azure_config or self.openai_config