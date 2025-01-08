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
                config_list = [{
                    "model": agent_llm_config["model_name"],
                    "base_url": f"http://{agent_llm_config.get('host_name', 'localhost')}:{agent_llm_config['port']}/v1"
                }]
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
            speaker_selection_method=settings.get("speaker_selection_method", "round_robin"),
            allow_repeat_speaker=settings.get("allow_repeat_speaker", False)
        )
        
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
        print(f"GroupChat max_round before manager creation: {getattr(group_chat, 'max_round', None)}")
        
        if not hasattr(group_chat, 'max_round'):
            raise ValueError("GroupChat must be properly initialized with max_round")
            
        # Use the first agent's config for the manager
        first_agent = group_chat.agents[0]
        print(f"First agent: {first_agent}")
        print(f"First agent type: {type(first_agent)}")
        print(f"First agent attributes: {dir(first_agent)}")
        print(f"First agent llm_config: {getattr(first_agent, 'llm_config', None)}")
        
        if hasattr(first_agent, "llm_config") and first_agent.llm_config:
            llm_config = first_agent.llm_config
            print(f"Using first agent's llm_config: {llm_config}")
            
            # Check if this is a Kamiwaza config
            if (
                isinstance(llm_config.get("config_list"), list) and 
                len(llm_config["config_list"]) > 0 and
                "base_url" in llm_config["config_list"][0] and
                "/v1" in llm_config["config_list"][0]["base_url"]
            ):
                print("Detected Kamiwaza config, using as is")
                # Use Kamiwaza config as is, but ensure it's in the right format
                config = llm_config["config_list"][0]
                llm_config = {
                    "model": config["model"],
                    "base_url": config["base_url"]
                }
            elif (
                isinstance(llm_config.get("config_list"), list) and
                len(llm_config["config_list"]) > 0 and
                llm_config["config_list"][0].get("api_type") == "azure"
            ):
                print("Detected Azure config, using as is")
                # Use Azure config as is
                pass
            else:
                print("Unknown config type, falling back to global config")
                # Fallback to global config
                base_config = self.llm_config_manager.get_active_config()
                llm_config = base_config
        else:
            print("No llm_config found, using fallback config")
            # Fallback to global config
            base_config = self.llm_config_manager.get_active_config()
            llm_config = base_config
            
        print(f"Final LLM config for manager: {llm_config}")
            
        # Create manager exactly like the docs example
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )
        
        print(f"Created GroupChatManager: {manager}")
        print(f"Manager's groupchat: {manager.groupchat}")
        print(f"Manager's groupchat max_round: {getattr(manager.groupchat, 'max_round', None) if manager.groupchat else None}")
        
        return manager