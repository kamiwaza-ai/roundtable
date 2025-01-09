# app/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os
from typing import Optional

# Load the .env file explicitly
load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/roundtable"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "your-development-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str = "your-openai-key"
    
    # Azure OpenAI
    azure_openai_api_key: str 
    azure_openai_endpoint: str = "https://oaity.openai.azure.com/"
    azure_openai_model: str = "gpt-4o"
    azure_openai_api_version: str = "2024-02-15-preview"

    # Kamiwaza API URI
    kamiwaza_api_uri: Optional[str] = "http://localhost:7777"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()