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
        llm_config = self.llm_config_manager.get_active_config()
        
        # Add response constraints to base config
        base_config = {
            "config_list": [{
                **config,
                "temperature": 0.7,  # Reduce randomness
                "max_tokens": 150,  # Limit response length
            } for config in llm_config.get("config_list", [])]
        }

        # Format system message with constraints
        system_message = self._format_system_message(agent_data.background)
        
        print(f"Creating agent with name: {agent_data.name}")
        
        # Handle different agent types
        if agent_data.agent_type == "system":
            # For system agents, we create an AssistantAgent instead of GroupChatManager
            # since GroupChatManager requires a groupchat during initialization
            agent = autogen.AssistantAgent(
                name=agent_data.name,
                system_message=system_message,
                llm_config=base_config
            )
        # Treat "standard" as an alias for "assistant"
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
            
        base_config = self.llm_config_manager.get_active_config()
        print(f"LLM config for manager: {base_config}")
        
        # Create a clean config without trying to merge
        llm_config = {
            "config_list": base_config.get("config_list", []),
            "temperature": 0.7,
            "max_tokens": 150
        }
            
        # Create manager exactly like the docs example
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )
        
        print(f"Created GroupChatManager: {manager}")
        print(f"Manager's groupchat: {manager.groupchat}")
        print(f"Manager's groupchat max_round: {getattr(manager.groupchat, 'max_round', None) if manager.groupchat else None}")
        
        return manager