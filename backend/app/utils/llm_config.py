#app/utils/llm_config.py

import os
from typing import Optional, Dict, Any
from functools import lru_cache
import logging
from pydantic import ValidationError
from dotenv import load_dotenv

load_dotenv()

#load env 


from ..schemas.llm import LLMConfig, AzureOpenAIConfig, OpenAIConfig, KamiwazaConfig

logger = logging.getLogger(__name__)

class LLMConfigurationError(Exception):
    """Raised when there are issues with LLM configuration"""
    pass

class LLMConfigManager:
    def __init__(self):
        self._config: Optional[LLMConfig] = None
        
    def initialize_from_env(self) -> None:
        """Initialize LLM configuration from environment variables"""
        configs = {}
        active_config = os.getenv("ACTIVE_LLM_CONFIG", "azure")  # Default to azure for backward compatibility
        
        # Try Azure OpenAI configuration
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if azure_key and azure_endpoint and azure_endpoint.strip():
            try:
                configs["azure_config"] = AzureOpenAIConfig(
                    api_key=azure_key,
                    azure_endpoint=azure_endpoint,
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                    model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
                    temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.7"))
                )
                logger.info("Azure OpenAI configuration initialized")
            except ValidationError as e:
                logger.warning(f"Failed to initialize Azure OpenAI configuration: {e}")
        
        # Try Kamiwaza configuration
        kamiwaza_port = os.getenv("KAMIWAZA_PORT")
        kamiwaza_model = os.getenv("KAMIWAZA_MODEL")
        if kamiwaza_port and kamiwaza_model:
            try:
                configs["kamiwaza_config"] = KamiwazaConfig(
                    model=kamiwaza_model,
                    host_name=os.getenv("KAMIWAZA_HOST", "localhost"),
                    port=int(kamiwaza_port),
                    temperature=float(os.getenv("KAMIWAZA_TEMPERATURE", "0.7")),
                    max_tokens=int(os.getenv("KAMIWAZA_MAX_TOKENS", "150"))
                )
                logger.info("Kamiwaza configuration initialized")
            except ValidationError as e:
                logger.warning(f"Failed to initialize Kamiwaza configuration: {e}")
        
        # Try OpenAI configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                configs["openai_config"] = OpenAIConfig(
                    api_key=openai_key,
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
                    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
                )
                logger.info("OpenAI configuration initialized")
            except ValidationError as e:
                logger.warning(f"Failed to initialize OpenAI configuration: {e}")
        
        if not configs:
            raise LLMConfigurationError("No valid LLM configurations found in environment variables")
            
        try:
            self._config = LLMConfig(**configs, active_config=active_config)
        except ValidationError as e:
            raise LLMConfigurationError(f"Invalid LLM configuration: {str(e)}")
    
    def get_active_config(self) -> Dict[str, Any]:
        """Get the current active configuration in AG2 format"""
        if not self._config:
            raise LLMConfigurationError("LLM configuration not initialized")
        
        active_config = self._config.get_active_config()
        
        if isinstance(active_config, AzureOpenAIConfig):
            return {
                "config_list": [{
                    "model": active_config.model,
                    "api_key": active_config.api_key,
                    "api_type": "azure",
                    "azure_endpoint": active_config.azure_endpoint,
                    "api_version": active_config.api_version,
                }]
            }
        elif isinstance(active_config, KamiwazaConfig):
            return {
                "config_list": [{
                    "model": active_config.model,
                    "base_url": f"http://{active_config.host_name}:{active_config.port}/v1",
                    "api_key": "not-needed"
                }]
            }
        elif isinstance(active_config, OpenAIConfig):
            return {
                "config_list": [{
                    "model": active_config.model,
                    "api_key": active_config.api_key,
                    "api_base": active_config.api_base,
                }]
            }
        
        raise LLMConfigurationError(f"Unsupported configuration type: {type(active_config)}")
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get configuration for direct API client usage"""
        if not self._config:
            raise LLMConfigurationError("LLM configuration not initialized")
        
        active_config = self._config.get_active_config()
        
        if isinstance(active_config, AzureOpenAIConfig):
            return {
                "api_key": active_config.api_key,
                "azure_endpoint": active_config.azure_endpoint,
                "api_version": active_config.api_version,
                "model": active_config.model,
                "temperature": active_config.temperature
            }
        elif isinstance(active_config, KamiwazaConfig):
            return {
                "model": active_config.model,
                "base_url": f"http://{active_config.host_name}:{active_config.port}",
                "api_key": "kamiwaza_model",
                "temperature": active_config.temperature
            }
        elif isinstance(active_config, OpenAIConfig):
            return {
                "api_key": active_config.api_key,
                "model": active_config.model,
                "temperature": active_config.temperature
            }
        
        raise LLMConfigurationError(f"Unsupported configuration type: {type(active_config)}")

@lru_cache()
def get_llm_config_manager() -> LLMConfigManager:
    """Get or create a singleton LLM configuration manager"""
    manager = LLMConfigManager()
    manager.initialize_from_env()
    return manager