# app/utils/ag2_wrapper.py - Complete updated file

from typing import List, Optional, Dict, Callable
import autogen
import os
from dotenv import load_dotenv
from app.schemas.round_table import RoundTableSettings
from app.schemas.agent import AgentCreate

# Load environment variables
load_dotenv()

class AG2Wrapper:
    def __init__(self, llm_config_manager):
        self.llm_config_manager = llm_config_manager

    def create_agent(self, agent_data: AgentCreate) -> autogen.ConversableAgent:
        """Create an AG2 agent based on configuration"""
        # Use the agent's llm_config, falling back to global config if needed
        agent_llm_config = agent_data.llm_config
        
        # If agent config doesn't have config_list, create it from the config
        if "config_list" not in agent_llm_config:
            # Determine the config type and create appropriate config
            if "api_type" in agent_llm_config and agent_llm_config["api_type"] == "azure":
                # Fill in empty values from environment
                api_key = agent_llm_config.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY")
                azure_endpoint = agent_llm_config.get("azure_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
                model = agent_llm_config.get("model") or os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
                api_version = agent_llm_config.get("api_version") or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
                
                if not (api_key and azure_endpoint):
                    raise ValueError("Azure configuration is incomplete. Please provide api_key and azure_endpoint.")
                
                endpoint = azure_endpoint.rstrip('/')  # Remove trailing slash
                config_list = [{
                    "model": model,
                    "api_key": api_key,
                    "azure_endpoint": endpoint,
                    "api_version": api_version,
                    "api_type": "azure"
                }]
            elif "provider" in agent_llm_config and agent_llm_config["provider"] == "kamiwaza":
                port = agent_llm_config.get("port")
                model = agent_llm_config.get("model_name")
                host = agent_llm_config.get("host_name")
                
                if not (port and model and host):
                    raise ValueError("Kamiwaza configuration is incomplete. Please provide port, model_name, and host_name.")
                
                config_list = [{
                    "model": "model",  # Always use "model" as the model name for Kamiwaza
                    "base_url": f"http://{host}:{port}/v1",
                    "api_key": "not-needed"
                }]
            else:
                # For OpenAI or unknown configs, use the global config
                global_config = self.llm_config_manager.get_active_config()
                config_list = global_config.get("config_list", [])
                
            base_config = {"config_list": config_list}
        else:
            base_config = agent_llm_config

        print(f"Using LLM config: {base_config}")

        # Format system message with constraints
        system_message = self._format_system_message(agent_data.background)
        
        print(f"Creating agent with name: {agent_data.name}")
        
        # Handle different agent types
        if agent_data.agent_type == "system":
            agent = autogen.AssistantAgent(
                name=agent_data.name,
                system_message=system_message,
                llm_config=base_config
            )
        elif agent_data.agent_type in ["assistant", "standard"]:
            agent = autogen.AssistantAgent(
                name=agent_data.name,
                system_message=system_message,
                llm_config=base_config
            )
        elif agent_data.agent_type == "user_proxy":
            agent = autogen.UserProxyAgent(
                name=agent_data.name,
                code_execution_config={"use_docker": False}
            )
        else:
            raise ValueError(f"Unsupported agent type: {agent_data.agent_type}")
            
        print(f"Created agent with name: {agent.name}")
        print(f"Verifying agent config - llm_config: {getattr(agent, 'llm_config', None)}")
        print(f"Verifying agent config - client: {getattr(agent, 'client', None)}")
        
        # Force set the config if it's not sticking
        if not hasattr(agent, 'llm_config'):
            print("WARNING: Agent missing llm_config, forcing it")
            agent.llm_config = base_config
            
        return agent

    def _format_system_message(self, message: str) -> str:
        """Add constraints to system message to control agent behavior"""
        return f"""
{message}

Follow these guidelines in all responses:
1. Keep responses brief and focused (2-3 sentences maximum)
2. Stay strictly on topic and avoid tangential discussions
3. Use clear, natural conversational language
4. Only include actionable points directly related to the current topic
5. Wait for others to finish before responding
6. Format code blocks and technical terms appropriately
"""

    def create_group_chat(
        self, 
        agents: List[autogen.ConversableAgent],
        settings: Dict
    ) -> autogen.GroupChat:
        """Create an AG2 GroupChat with optimized settings"""
        print(f"Creating GroupChat with settings: {settings}")
        print(f"Number of agents: {len(agents)}")
        
        # Create GroupChat exactly like the docs example
        group_chat = autogen.GroupChat(
            agents=agents,
            messages=[],  # This must be passed directly, not through settings
            max_round=settings.get("max_round", 12),
            speaker_selection_method='round_robin',
            allow_repeat_speaker=settings.get("allow_repeat_speaker", False)
        )

        # Initalize message
        if not group_chat.messages:
            group_chat.messages = [{
                "role": "system",
                "content": "Discussion initialized.",
                "name": "system"
            }]
        
        print(f"Created GroupChat object: {group_chat}")
        print(f"GroupChat max_round: {getattr(group_chat, 'max_round', None)}")
        
        # Verify the group chat was created properly
        if not hasattr(group_chat, 'max_round'):
            raise ValueError("GroupChat initialization failed - max_round not set")
                
        return group_chat

    def create_group_chat_manager(
        self, 
        group_chat: autogen.GroupChat
    ) -> autogen.GroupChatManager:
        """Create an AG2 GroupChatManager with optimized settings"""
        print(f"Creating GroupChatManager with group_chat: {group_chat}")
        
        if not hasattr(group_chat, 'max_round'):
            raise ValueError("GroupChat must be properly initialized with max_round")
            
        # Get config from first agent (EXACTLY like test)
        first_agent = group_chat.agents[0]
        
        if hasattr(first_agent, "llm_config") and first_agent.llm_config:
            # Just pass through the config_list like in test
            llm_config = {"config_list": first_agent.llm_config["config_list"]}
        else:
            # Use fallback config
            base_config = self.llm_config_manager.get_active_config()
            llm_config = {"config_list": base_config["config_list"]}
            
        print(f"Final LLM config for manager: {llm_config}")
            
        # Create manager exactly like the test
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )
        
        return manager