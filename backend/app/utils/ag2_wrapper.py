# app/utils/ag2_wrapper.py
from typing import Dict, Any, List, Optional
import autogen
from ..utils.llm_config import get_llm_config_manager
from ..schemas.agent import AgentBase
from ..schemas.round_table import RoundTableSettings

class AG2Wrapper:
    def __init__(self):
        self.llm_config_manager = get_llm_config_manager()
        
    def create_agent(self, config: AgentBase) -> autogen.ConversableAgent:
        """Create appropriate AG2 agent based on configuration"""
        llm_config = self.llm_config_manager.get_active_config()
        
        if config.agent_type == "standard":
            return autogen.ConversableAgent(
                name=config.name,
                system_message=config.background,
                llm_config=llm_config
            )
        elif config.agent_type == "human_proxy":
            return autogen.UserProxyAgent(
                name=config.name,
                system_message=config.background,
                human_input_mode="TERMINATE",
                code_execution_config=False
            )
        else:
            raise ValueError(f"Unsupported agent type: {config.agent_type}")

    def register_tools(self, agent: autogen.ConversableAgent, tools: Dict[str, Any]):
        """Register tools/functions with an agent"""
        for tool_name, tool_config in tools.items():
            agent.register_for_llm(
                name=tool_name,
                description=tool_config.get("description", ""),
                function=tool_config.get("implementation")
            )

    def create_group_chat(
        self, 
        agents: List[autogen.ConversableAgent], 
        settings: RoundTableSettings
    ) -> autogen.GroupChat:
        """Create an AG2 GroupChat instance"""
        return autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=settings.max_rounds,
            speaker_selection_method=settings.speaker_selection_method,
            allow_repeat_speaker=True
        )

    def create_group_chat_manager(
        self, 
        group_chat: autogen.GroupChat,
        llm_config: Optional[Dict] = None
    ) -> autogen.GroupChatManager:
        """Create a GroupChatManager for the given group chat"""
        if llm_config is None:
            llm_config = self.llm_config_manager.get_active_config()
        
        return autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config
        )

    async def run_group_discussion(
        self,
        group_chat: autogen.GroupChat,
        initial_message: str,
        max_rounds: Optional[int] = None
    ) -> List[Dict]:
        """Run a group discussion and return the chat history
        
        Args:
            group_chat: The GroupChat instance to run the discussion with
            initial_message: The message to start the discussion
            max_rounds: Optional override for the maximum number of rounds
            
        Returns:
            List of message dictionaries representing the chat history
        """
        chat_manager = self.create_group_chat_manager(group_chat)
        
        # Choose first agent to start the discussion
        initiating_agent = group_chat.agents[0]
        
        # Run the discussion
        result = await initiating_agent.a_initiate_chat(
            chat_manager,
            message=initial_message,
            max_rounds=max_rounds
        )
        
        return result.chat_history