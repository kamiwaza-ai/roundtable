import autogen
import asyncio

# Configuration for the local model
config_list = [
    {
        "model": "Qwen2.5-7B-Instruct-GGUF",  # Model name - match what you use in curl
        "base_url": "http://localhost:51100/v1",  # Local server endpoint
        "api_key": "not-needed"  # API key can be any string for local deployment
    }
]

async def test_group_chat():
    print("\nSetting up group chat test...")
    
    # Create multiple agents like in our app
    agent1 = autogen.AssistantAgent(
        name="Tyler",
        system_message="You are a helpful AI assistant.",
        llm_config={
            "config_list": config_list,
            "temperature": 0.7
        }
    )

    agent2 = autogen.AssistantAgent(
        name="Matt",
        system_message="You are a helpful AI assistant.",
        llm_config={
            "config_list": config_list,
            "temperature": 0.7
        }
    )

    agent3 = autogen.AssistantAgent(
        name="Luke",
        system_message="You are a helpful AI assistant.",
        llm_config={
            "config_list": config_list,
            "temperature": 0.7
        }
    )

    print("Created agents:", [agent1.name, agent2.name, agent3.name])

    # Create group chat with empty messages first
    groupchat = autogen.GroupChat(
        agents=[agent1, agent2, agent3],
        messages=[],  # Start empty
        max_round=12,
        speaker_selection_method="round_robin",
        allow_repeat_speaker=True
    )

    print("Created group chat")

    # Initialize with system message first
    groupchat.messages = [{
        "role": "system",
        "content": "Discussion initialized.",
        "name": "system"
    }]

    print(f"Group chat messages after system init: {groupchat.messages}")

    # Initial message
    initial_message = {
        "role": "user",
        "content": "Let's talk about San Diego. What's your favorite thing about the city?",
        "name": "Tyler"
    }

    print(f"Initial message: {initial_message}")
    
    # Add initial message after system message
    groupchat.messages.append(initial_message)

    print(f"Group chat messages after adding initial: {groupchat.messages}")

    # Create manager
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config={"config_list": config_list}  # Simplified config
    )

    print("Created manager")
    print("Starting group chat...")
    
    try:
        # Run the chat with config
        result = await manager.a_run_chat(
            messages=[initial_message],
            sender=agent1,
            config=groupchat  # Pass the groupchat as config
        )
        
        print(f"Chat result: {result}")
        print(f"Final messages: {manager.groupchat.messages}")
    except Exception as e:
        print(f"Error during chat: {str(e)}")
        print(f"Messages at error: {groupchat.messages if groupchat else None}")
        print(f"Manager groupchat: {manager.groupchat if manager else None}")
        raise

if __name__ == "__main__":
    asyncio.run(test_group_chat())