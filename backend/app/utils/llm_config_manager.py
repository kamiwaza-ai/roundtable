from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()

class LLMConfigManager:
    def __init__(self):
        self.initialize_from_env()

    def initialize_from_env(self):
        """Initialize configuration from environment variables"""
        self.default_config = {
            "temperature": 0.7,
            "config_list": [
                {
                    "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini"),
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "api_version": "2024-02-15-preview",
                    "api_type": "azure"
                }
            ]
        }

    def get_active_config(self) -> Dict:
        """Get the current active LLM configuration"""
        if not self.default_config["config_list"][0]["api_key"]:
            raise ValueError("Azure OpenAI API key not found in environment")
        if not self.default_config["config_list"][0]["azure_endpoint"]:
            raise ValueError("Azure OpenAI endpoint not found in environment")
        return self.default_config 