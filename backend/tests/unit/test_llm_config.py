import pytest
from pydantic import ValidationError
import os
from app.utils.llm_config import LLMConfigManager, LLMConfigurationError
from app.schemas.llm import AzureOpenAIConfig, OpenAIConfig, LLMConfig
import openai
from openai import AzureOpenAI
import dotenv

dotenv.load_dotenv()

def test_azure_config_validation():
    # Skip if Azure credentials are not configured
    if not all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_MODEL")
    ]):
        pytest.skip("Azure OpenAI credentials not configured")

    # Valid config
    config = AzureOpenAIConfig(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model=os.getenv("AZURE_OPENAI_MODEL"),
        temperature=0.7
    )
    assert config.model == os.getenv("AZURE_OPENAI_MODEL")
    assert config.api_key == os.getenv("AZURE_OPENAI_API_KEY")
    assert config.azure_endpoint == os.getenv("AZURE_OPENAI_ENDPOINT")
    
    # Invalid model
    with pytest.raises(ValidationError):
        AzureOpenAIConfig(
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com",
            model="invalid-model"
        )
    
    # Invalid endpoint
    with pytest.raises(ValidationError):
        AzureOpenAIConfig(
            api_key="test-key",
            azure_endpoint="invalid-endpoint",
            model="gpt-4o-mini"
        )

def test_config_manager_azure_initialization():
    # Skip if Azure credentials are not configured
    if not all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_MODEL")
    ]):
        pytest.skip("Azure OpenAI credentials not configured")
    
    manager = LLMConfigManager()
    manager.initialize_from_env()
    
    config = manager.get_active_config()
    assert isinstance(config["config_list"][0], dict)
    assert config["config_list"][0]["api_key"] == os.getenv("AZURE_OPENAI_API_KEY")
    assert config["config_list"][0]["azure_endpoint"] == os.getenv("AZURE_OPENAI_ENDPOINT")
    assert config["config_list"][0]["model"] == os.getenv("AZURE_OPENAI_MODEL")

def test_azure_live_connection():
    """Integration test to verify Azure OpenAI connectivity"""
    # Skip if Azure credentials are not configured
    if not all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_MODEL")
    ]):
        pytest.skip("Azure OpenAI credentials not configured")
    
    manager = LLMConfigManager()
    manager.initialize_from_env()
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-02-15-preview"
    )
    
    try:
        # Make a simple test call
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL"),
            messages=[{"role": "user", "content": "Say hello in a creative way"}],
            max_tokens=50
        )
        print("\nAzure OpenAI Response:", response.choices[0].message.content)
        assert response.choices[0].message.content is not None
    except Exception as e:
        pytest.fail(f"Failed to connect to Azure OpenAI: {str(e)}")