# app/utils/ag2_wrapper.py - Complete updated file

from typing import List, Optional, Dict, Callable
import autogen
from app.schemas.round_table import RoundTableSettings
from app.schemas.agent import AgentCreate

class AG2Wrapper:
    def __init__(self, llm_config_manager):
        self.llm_config_manager = llm_config_manager

    def create_agent(self, agent_data: AgentCreate) -> autogen.ConversableAgent:
        """Create an AG2 agent based on configuration"""
        # Use the agent's llm_config, falling back to global config if needed
        agent_llm_config = agent_data.llm_config
        
        # If agent config doesn't have config_list, create it from the config
        if "config_list" not in agent_llm_config:
            if "api_type" in agent_llm_config and agent_llm_config["api_type"] == "azure":
                model = agent_llm_config.get("model", "gpt-4o")
                endpoint = agent_llm_config['azure_endpoint'].rstrip('/')  # Remove trailing slash
                config_list = [{
                    "model": model,
                    "api_key": agent_llm_config["api_key"],
                    "azure_endpoint": endpoint,
                    "api_version": agent_llm_config.get("api_version", "2024-02-15-preview"),
                    "api_type": "azure"
                }]
            elif "provider" in agent_llm_config and agent_llm_config["provider"] == "kamiwaza":
                # Simplified config for Kamiwaza following AG2 docs
                print(f"\n=== Creating Kamiwaza Config ===")
                print(f"Agent name: {agent_data.name}")
                print(f"Raw config: {agent_llm_config}")
                
                # Create minimal config that worked before
                config_list = [{
                    "model": agent_llm_config["model_name"],
                    "base_url": f"http://{agent_llm_config.get('host_name', 'localhost')}:{agent_llm_config['port']}/v1",
                    "api_key": "not-needed",  # Required by OpenAI client
                    "api_type": "open_ai",
                    "temperature": agent_llm_config.get("temperature", 0.7),  # Pass through temperature
                    "max_tokens": agent_llm_config.get("max_tokens", 150),  # Pass through max_tokens
                    "context_window": 4096,  # Add context window size
                    "seed": 42,  # Add deterministic seed
                    "timeout": 120,  # Add timeout
                }]
                
                print(f"Created config: {config_list}")
                print(f"=== End Kamiwaza Config ===\n")
            else:
                # Fallback to global config
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
            print(f"Creating system agent with config: {base_config}")
            agent = autogen.AssistantAgent(
                name=agent_data.name,
                system_message=system_message,
                llm_config=base_config
            )
        elif agent_data.agent_type in ["assistant", "standard"]:
            print(f"Creating assistant/standard agent with config: {base_config}")
            agent = autogen.AssistantAgent(
                name=agent_data.name,
                system_message=system_message,
                llm_config=base_config
            )
        elif agent_data.agent_type == "user_proxy":
            print(f"Creating user proxy agent")
            agent = autogen.UserProxyAgent(
                name=agent_data.name,
                code_execution_config={"use_docker": False}
            )
        else:
            raise ValueError(f"Unsupported agent type: {agent_data.agent_type}")
            
        print(f"Created agent with name: {agent.name}")
        print(f"Agent type: {type(agent)}")
        print(f"Agent system message: {getattr(agent, 'system_message', None)}")
        print(f"Agent llm_config: {getattr(agent, 'llm_config', None)}")
        print(f"Agent client: {getattr(agent, 'client', None)}")
        print(f"Agent reply functions: {getattr(agent, '_reply_func_list', [])}")
        
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
        
        # Create GroupChat with minimal settings
        group_chat = autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=12,
            speaker_selection_method="round_robin"
        )
        
        print(f"Created GroupChat object: {group_chat}")
        print(f"GroupChat max_round: {getattr(group_chat, 'max_round', None)}")
        
        return group_chat

    def create_group_chat_manager(
        self, 
        group_chat: autogen.GroupChat
    ) -> autogen.GroupChatManager:
        """Create an AG2 GroupChatManager with optimized settings"""
        print(f"\n=== Creating GroupChatManager ===")
        
        # Get config from first agent
        first_agent = group_chat.agents[0]
        print(f"First agent: {first_agent.name}")
        print(f"First agent config: {getattr(first_agent, 'llm_config', None)}")
        
        llm_config = getattr(first_agent, 'llm_config', None)
        if not llm_config:
            print("No llm_config found, using fallback config")
            llm_config = self.llm_config_manager.get_active_config()
            
        print(f"Final manager config: {llm_config}")
            
        # Create manager with minimal settings
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )
        
        print(f"Created manager: {manager}")
        print(f"Manager config: {getattr(manager, 'llm_config', None)}")
        print(f"Manager groupchat: {getattr(manager, 'groupchat', None)}")
        
        return manager