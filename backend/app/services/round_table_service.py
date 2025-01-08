# app/services/round_table_service.py
from typing import List, Optional, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import autogen

from ..repositories.base import BaseRepository
from ..models.round_table import RoundTable
from ..models.round_table_participant import RoundTableParticipant
from ..models.message import Message
from ..models.agent import Agent
from ..schemas.round_table import RoundTableCreate, RoundTableUpdate, RoundTableInDB
from ..schemas.message import MessageCreate, MessageInDB
from ..utils.llm_config_manager import LLMConfigManager
from ..utils.ag2_wrapper import AG2Wrapper
from .agent_service import AgentService

class RoundTableService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(RoundTable, db)
        self.agent_service = AgentService(db)
        # Initialize LLMConfigManager and AG2Wrapper
        self.llm_config_manager = LLMConfigManager()
        self.ag2_wrapper = AG2Wrapper(self.llm_config_manager)
        
    async def create_round_table(self, data: RoundTableCreate) -> RoundTableInDB:
        """Create a new round table discussion."""
        # Verify all participants exist
        participants = []
        for agent_id in data.participant_ids:
            agent = self.agent_service.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            participants.append(agent)

        # Create database record with optimized default settings
        round_table_data = {
            "title": data.title,
            "context": data.context,
            "settings": data.settings.model_dump() if data.settings else {
                "max_rounds": 12,
                "max_round": 12,
                "speaker_selection_method": "round_robin",
                "allow_repeat_speaker": False,
                "send_introductions": True
            }
        }
        
        db_round_table = self.repository.create(round_table_data)
        
        # Create participant records with speaking priority
        for i, agent in enumerate(participants):
            participant = RoundTableParticipant(
                round_table_id=db_round_table.id,
                agent_id=agent.id,
                speaking_priority=i + 1  # Assign speaking priority based on order
            )
            self.db.add(participant)
        
        self.db.commit()
        return RoundTableInDB.model_validate(db_round_table)

    def _store_message(self, message_data: Dict) -> Message:
        """Store a message in the database."""
        print(f"Storing message: {message_data}")
        message = Message(
            round_table_id=message_data["round_table_id"],
            agent_id=message_data["agent_id"],
            content=message_data["content"],
            message_type=message_data["message_type"]
        )
        self.db.add(message)
        self.db.commit()
        print(f"Message stored with ID: {message.id}")
        return message

    def get_discussion_history(self, round_table_id: UUID) -> List[Dict]:
        """Get the message history for a round table discussion."""
        print(f"Getting discussion history for round table: {round_table_id}")
        messages = (
            self.db.query(Message)
            .filter(Message.round_table_id == round_table_id)
            .order_by(Message.created_at)
            .all()
        )
        print(f"Found {len(messages)} messages")
        return [MessageInDB.model_validate(msg) for msg in messages]

    async def run_discussion(self, round_table_id: UUID, prompt: str) -> Dict:
        """Run a round table discussion"""
        # Get the round table
        round_table = self.repository.get(round_table_id)
        if not round_table:
            raise HTTPException(status_code=404, detail="Round table not found")

        # Get participants
        participants = self._get_participants(round_table_id)
        if not participants:
            raise HTTPException(
                status_code=400, 
                detail="No participants found for this round table"
            )

        # Create AG2 agents for each participant
        ag2_agents = []
        # Create a mapping of agent names to database IDs
        agent_name_to_id = {}
        for participant in participants:
            agent_data = participant["agent"]
            # Create AG2 agent with the exact same name as the database agent
            ag2_agent = self.ag2_wrapper.create_agent(agent_data)
            ag2_agents.append(ag2_agent)
            # Store the mapping of agent name to database ID
            agent_name_to_id[ag2_agent.name] = agent_data.id
            print(f"Created agent mapping: {ag2_agent.name} -> {agent_data.id}")

        # Create group chat with proper settings
        group_chat_settings = {
            "max_round": round_table.settings.get("max_round", 12),  # Use consistent parameter name
            "speaker_selection_method": round_table.settings.get("speaker_selection_method", "round_robin"),
            "allow_repeat_speaker": round_table.settings.get("allow_repeat_speaker", False),
            "send_introductions": round_table.settings.get("send_introductions", True)
        }
        
        group_chat = self.ag2_wrapper.create_group_chat(
            ag2_agents,
            group_chat_settings
        )

        # Create the GroupChatManager to coordinate the discussion
        manager = self.ag2_wrapper.create_group_chat_manager(group_chat)

        # Format initial message
        initial_message = self._format_initial_message(round_table, prompt)

        # Store the initial message from the first agent
        self._store_message({
            "round_table_id": round_table_id,
            "agent_id": participants[0]["agent"].id,  # First agent starts
            "content": initial_message,
            "message_type": "introduction"
        })

        # Update round table status to in_progress
        round_table.status = "in_progress"
        self.db.commit()

        # Define message callback that correctly maps sender to DB agent
        def message_callback(message: Dict) -> None:
            if not message.get("content"):
                return
                
            # Get the sender's name from the message
            sender_name = message.get("name")
            print(f"Processing message from sender: {sender_name}")
            print(f"Available agent mappings: {agent_name_to_id}")
            
            # Find the corresponding participant agent using the name mapping
            agent_id = agent_name_to_id.get(sender_name)
            if not agent_id:
                print(f"Warning: Could not find agent ID for sender {sender_name}, using first agent")
                agent_id = participants[0]["agent"].id

            # Store the message
            self._store_message({
                "round_table_id": round_table_id,
                "agent_id": agent_id,
                "content": message.get("content", ""),
                "message_type": "discussion"
            })

        # Register callback for all agents
        for agent in ag2_agents:
            agent.register_reply(
                reply_func=lambda recipient, messages, sender, config: (
                    False, 
                    message_callback({
                        "name": messages[-1].get("name") if messages and len(messages) > 0 else sender.name,  # Use message name or sender name
                        "content": messages[-1].get("content", "") if messages and len(messages) > 0 else ""
                    }) if messages and len(messages) > 0 else None
                ),
                trigger=lambda _: True
            )

        # Initialize the group chat with the first message
        group_chat.messages.append({
            "role": "user",
            "content": initial_message,
            "name": ag2_agents[0].name  # Use first agent's name
        })

        # Start discussion using the first agent's message
        result = await manager.a_run_chat(
            messages=group_chat.messages,  # Use the initialized messages
            sender=ag2_agents[0],  # First agent starts the discussion
            config=group_chat  # Pass the GroupChat as config
        )

        # Update round table status
        round_table.status = "completed"
        round_table.completed_at = datetime.utcnow()
        self.db.commit()

        return {
            "chat_history": manager.groupchat.messages,
            "summary": None  # Summary will be handled separately if needed
        }

    def _format_initial_message(self, round_table, prompt: str) -> str:
        """Format the initial message with clear structure and guidelines"""
        return f"""Topic: {round_table.title}

Context: {round_table.context}

Task: {prompt}

Guidelines for Discussion:
1. Keep responses focused and brief (2-3 sentences)
2. Address only the current topic
3. Build on others' contributions
4. Provide specific, actionable input
5. Use natural conversational language

Begin the discussion by addressing the task directly."""

    async def get_all_round_tables(self) -> List[RoundTableInDB]:
        """Get all round tables from the database.
        
        Returns:
            List[RoundTableInDB]: List of all round tables with their messages
        """
        # Query round tables with messages
        round_tables = (
            self.db.query(RoundTable)
            .options(joinedload(RoundTable.messages))
            .all()
        )
        return [RoundTableInDB.model_validate(rt) for rt in round_tables]

    def _get_participants(self, round_table_id: UUID) -> List[Dict]:
        """Get all participants for a round table"""
        # Query the round_table_participants table
        participants = (
            self.db.query(RoundTableParticipant, Agent)
            .join(Agent, RoundTableParticipant.agent_id == Agent.id)
            .filter(RoundTableParticipant.round_table_id == round_table_id)
            .all()
        )
        
        # Convert to list of agents with their roles
        return [
            {
                "agent": self.agent_service.get_agent(participant.agent_id),
                "role": participant.role,
                "speaking_priority": participant.speaking_priority
            }
            for participant, agent in participants
        ]

    async def delete_all_messages(self) -> bool:
        """Delete all messages from the database.
        
        Returns:
            bool: True if successful
        """
        try:
            self.db.query(Message).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_all_round_tables(self) -> bool:
        """Delete all round tables from the database.
        This will cascade delete all associated messages and participants.
        
        Returns:
            bool: True if successful
        """
        try:
            self.db.query(RoundTable).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def pause_discussion(self, round_table_id: UUID) -> Dict:
        """Pause a round table discussion and save its state"""
        print(f"Attempting to pause discussion for round table: {round_table_id}")
        round_table = self.repository.get(round_table_id)
        if not round_table:
            print(f"Round table not found: {round_table_id}")
            raise HTTPException(status_code=404, detail="Round table not found")
        
        if round_table.status != "in_progress":
            print(f"Invalid status for pause. Current status: {round_table.status}")
            raise HTTPException(status_code=400, detail="Round table is not in progress")

        # Get the current messages and participants
        messages = self.get_discussion_history(round_table_id)
        participants = self._get_participants(round_table_id)
        print(f"Retrieved {len(messages)} messages for state storage")
        
        # Create agent ID to name mapping
        agent_id_to_name = {
            participant["agent"].id: participant["agent"].name 
            for participant in participants
        }
        
        # Convert messages to a serializable format
        try:
            # Convert each message to AG2 format with agent names
            serialized_messages = []
            for msg in messages:
                agent_name = agent_id_to_name.get(msg.agent_id, "unknown")
                serialized_messages.append({
                    "role": "assistant",  # All stored messages are from assistants
                    "content": msg.content,
                    "name": agent_name,
                    "function_call": None
                })
            print(f"Successfully serialized {len(serialized_messages)} messages")
        except Exception as e:
            print(f"Error serializing messages: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to serialize messages: {str(e)}")
        
        # Update round table status and save state
        try:
            round_table.status = "paused"
            round_table.messages_state = serialized_messages
            self.db.commit()
            print(f"Successfully paused round table {round_table_id}")
        except Exception as e:
            print(f"Error saving pause state: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save pause state: {str(e)}")
        
        # Signal to the frontend that the discussion is paused
        return {
            "status": "paused",
            "round_table_id": round_table_id,
            "message_count": len(messages)
        }

    async def resume_discussion(self, round_table_id: UUID) -> Dict:
        """Resume a paused round table discussion"""
        print(f"Attempting to resume discussion for round table: {round_table_id}")
        round_table = self.repository.get(round_table_id)
        if not round_table:
            print(f"Round table not found: {round_table_id}")
            raise HTTPException(status_code=404, detail="Round table not found")
        
        if round_table.status != "paused":
            print(f"Invalid status for resume. Current status: {round_table.status}")
            raise HTTPException(status_code=400, detail="Round table is not paused")
            
        if not round_table.messages_state:
            print(f"No saved message state found for round table: {round_table_id}")
            raise HTTPException(status_code=400, detail="No saved state found")

        print(f"Retrieved saved state with {len(round_table.messages_state)} messages")

        # Get participants
        participants = self._get_participants(round_table_id)
        if not participants:
            print(f"No participants found for round table: {round_table_id}")
            raise HTTPException(
                status_code=400, 
                detail="No participants found for this round table"
            )

        print(f"Found {len(participants)} participants")

        # Create AG2 agents and group chat like in run_discussion
        try:
            ag2_agents = []
            agent_name_to_id = {}
            for participant in participants:
                agent_data = participant["agent"]
                ag2_agent = self.ag2_wrapper.create_agent(agent_data)
                ag2_agents.append(ag2_agent)
                agent_name_to_id[ag2_agent.name] = agent_data.id
                print(f"Recreated agent: {ag2_agent.name} -> {agent_data.id}")

            # Create group chat with proper settings
            print("Creating group chat with settings:", {
                "max_round": round_table.settings.get("max_round", 12),
                "speaker_selection_method": round_table.settings.get("speaker_selection_method", "auto"),
                "allow_repeat_speaker": round_table.settings.get("allow_repeat_speaker", True),
                "send_introductions": False
            })

            group_chat = self.ag2_wrapper.create_group_chat(
                ag2_agents,
                {
                    "max_round": round_table.settings.get("max_round", 12),
                    "speaker_selection_method": round_table.settings.get("speaker_selection_method", "auto"),
                    "allow_repeat_speaker": round_table.settings.get("allow_repeat_speaker", True),
                    "send_introductions": False  # Don't send introductions when resuming
                }
            )

            # Create the GroupChatManager
            manager = self.ag2_wrapper.create_group_chat_manager(group_chat)
            print("Successfully created GroupChatManager")

        except Exception as e:
            print(f"Error setting up AG2 components: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to setup discussion: {str(e)}")

        # Register message callbacks
        def message_callback(message: Dict) -> None:
            if not message.get("content"):
                return
                
            sender_name = message.get("name")
            agent_id = agent_name_to_id.get(sender_name)
            if not agent_id:
                print(f"Warning: Could not find agent ID for sender {sender_name}, using first agent")
                agent_id = participants[0]["agent"].id

            self._store_message({
                "round_table_id": round_table_id,
                "agent_id": agent_id,
                "content": message.get("content", ""),
                "message_type": "discussion"
            })

        for agent in ag2_agents:
            agent.register_reply(
                reply_func=lambda recipient, messages, sender, config: (
                    False, 
                    message_callback({
                        "name": messages[-1].get("name") if messages and len(messages) > 0 else sender.name,
                        "content": messages[-1].get("content", "") if messages and len(messages) > 0 else ""
                    }) if messages and len(messages) > 0 else None
                ),
                trigger=lambda _: True
            )

        # Update status to in_progress
        round_table.status = "in_progress"
        self.db.commit()
        print(f"Updated round table status to in_progress")

        # Resume the chat with saved state
        try:
            print(f"Attempting to resume chat with {len(round_table.messages_state)} messages")
            # Initialize the group chat with the saved messages
            group_chat.messages = round_table.messages_state
            
            # Get the last message to determine the next speaker
            last_message = round_table.messages_state[-1] if round_table.messages_state else None
            next_speaker = None
            if last_message:
                last_speaker_name = last_message.get("name")
                for agent in ag2_agents:
                    if agent.name == last_speaker_name:
                        next_speaker = agent
                        break
            
            if not next_speaker:
                next_speaker = ag2_agents[0]
            
            # Start the discussion from where it left off
            result = await manager.a_run_chat(
                messages=group_chat.messages,
                sender=next_speaker,
                config=group_chat
            )
            print("Successfully resumed chat")
            
            return {
                "status": "resumed",
                "round_table_id": round_table_id,
                "chat_history": manager.groupchat.messages
            }
            
        except Exception as e:
            print(f"Error resuming chat: {str(e)}")
            round_table.status = "paused"  # Revert status if resume fails
            self.db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to resume discussion: {str(e)}")