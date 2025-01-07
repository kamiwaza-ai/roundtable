import pytest
from unittest.mock import Mock, patch
import autogen
from backend.app.utils.ag2_wrapper import AG2Wrapper
from backend.app.schemas.agent import AgentCreate

@pytest.fixture
def ag2_wrapper():
    # Mock the entire LLM config manager
    with patch('backend.app.utils.ag2_wrapper.get_llm_config_manager') as mock_get_manager:
        # Create a mock manager
        mock_manager = Mock()
        # Set up the mock to return a test config
        mock_manager.get_active_config.return_value = {
            "config_list": [{
                "model": "gpt-4",
                "api_key": "test-key"
            }]
        }
        # Make get_llm_config_manager return our mock manager
        mock_get_manager.return_value = mock_manager
        yield AG2Wrapper()

def test_create_standard_agent(ag2_wrapper):
    config = AgentCreate(
        name="Test Agent",
        title="Test Title",
        background="Test background",
        agent_type="standard",
        llm_config={"model": "gpt-4o"}
    )
    
    agent = ag2_wrapper.create_agent(config)
    
    assert isinstance(agent, autogen.ConversableAgent)
    assert agent.name == "Test Agent"
    assert agent.system_message == "Test background"

def test_create_human_proxy_agent(ag2_wrapper):
    config = AgentCreate(
        name="Human Agent",
        title="Human Title",
        background="Human background",
        agent_type="human_proxy",
        llm_config={"model": "gpt-4o"}
    )
    
    agent = ag2_wrapper.create_agent(config)
    
    assert isinstance(agent, autogen.UserProxyAgent)
    assert agent.name == "Human Agent"
    assert agent.system_message == "Human background"
    assert agent.human_input_mode == "TERMINATE"
    assert agent.code_execution_config is False

def test_create_invalid_agent_type(ag2_wrapper):
    config = AgentCreate(
        name="Invalid Agent",
        title="Invalid Title",
        background="Invalid background",
        agent_type="invalid_type",
        llm_config={"model": "gpt-4o"}
    )
    
    with pytest.raises(ValueError) as exc_info:
        ag2_wrapper.create_agent(config)
    assert str(exc_info.value) == "Unsupported agent type: invalid_type"

def test_register_tools(ag2_wrapper):
    mock_agent = Mock(spec=autogen.ConversableAgent)
    tools = {
        "test_tool": {
            "description": "Test tool description",
            "implementation": lambda x: x
        }
    }
    
    ag2_wrapper.register_tools(mock_agent, tools)
    
    mock_agent.register_for_llm.assert_called_once_with(
        name="test_tool",
        description="Test tool description",
        function=tools["test_tool"]["implementation"]
    )
