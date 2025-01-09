import autogen

# Configuration for the local model
config_list = [
    {
        "model": "Qwen2.5-7B-Instruct-GGUF",  # Model name - match what you use in curl
        "base_url": "http://localhost:51100/v1",  # Local server endpoint
        "api_key": "not-needed"  # API key can be any string for local deployment
    }
]

# Create an assistant agent using the local model configuration
assistant = autogen.AssistantAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant.",
    llm_config={
        "config_list": config_list,
        "temperature": 0.7
    }
)

# Create a user proxy agent - this one doesn't use the LLM, so no config needed
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",  # This allows us to stop the conversation by typing 'exit'
    max_consecutive_auto_reply=1,
    code_execution_config=False  # Disable code execution for this simple test
)

# Test the conversation
user_proxy.initiate_chat(
    assistant,
    message="Tell me what model you are."
)

# You can terminate the chat by typing 'exit' when prompted