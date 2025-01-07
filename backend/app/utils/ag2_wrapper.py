# app/utils/ag2_wrapper.py
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
        
        # Treat "standard" as an alias for "assistant"
        if agent_data.agent_type in ["assistant", "standard"]:
            return autogen.AssistantAgent(
                name=agent_data.name,
                system_message=agent_data.background,
                llm_config=llm_config
            )
        elif agent_data.agent_type == "user_proxy":
            return autogen.UserProxyAgent(
                name=agent_data.name,
                code_execution_config={"use_docker": False}
            )
        # Add other agent types as needed
        raise ValueError(f"Unsupported agent type: {agent_data.agent_type}")

    def create_group_chat(
        self, 
        agents: List[autogen.ConversableAgent],
        settings: Dict
    ) -> autogen.GroupChat:
        """Create an AG2 GroupChat with specified settings"""
        return autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=settings.get("max_rounds", 12),
            speaker_selection_method=settings.get("speaker_selection_method", "auto"),
            allow_repeat_speaker=settings.get("allow_repeat_speaker", True),
            send_introductions=settings.get("send_introductions", True)
        )

    def create_group_chat_manager(
        self, 
        group_chat: autogen.GroupChat
    ) -> autogen.GroupChatManager:
        """Create an AG2 GroupChatManager"""
        return autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=self.llm_config_manager.get_active_config()
        )

    async def initiate_group_discussion(
        self,
        initiating_agent: autogen.ConversableAgent,
        manager: autogen.GroupChatManager,
        message: str,
        max_rounds: Optional[int] = None,
        message_callback: Optional[Callable] = None
    ) -> autogen.ChatResult:
        """Initiate a group discussion using AG2's pattern"""
        # Register message callback if provided
        if message_callback:
            def message_handler(self, messages, sender, config):
                if messages and isinstance(messages[-1], dict) and messages[-1].get("content"):
                    message_callback(messages[-1])
                return False, None
            
            def trigger_fn(sender):
                return True  # Handle all messages
            
            # Register the message handler for each agent in the group chat
            for agent in manager.groupchat.agents:
                agent.register_reply(
                    reply_func=message_handler,
                    trigger=trigger_fn,
                    config=None,
                    reset_config=False
                )

        return await initiating_agent.a_initiate_chat(
            manager,
            message=message,
            max_rounds=max_rounds
        )