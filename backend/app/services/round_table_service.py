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

        # Create database record (exclude participant_ids from the data)
        round_table_data = {
            "title": data.title,
            "context": data.context,
            "settings": data.settings.model_dump() if data.settings else {
                "max_rounds": 12,
                "speaker_selection_method": "auto",
                "allow_repeat_speaker": True,
                "send_introductions": True
            }
        }
        
        db_round_table = self.repository.create(round_table_data)
        
        # Create participant records
        for agent in participants:
            participant = RoundTableParticipant(
                round_table_id=db_round_table.id,
                agent_id=agent.id
            )
            self.db.add(participant)
        
        self.db.commit()
        return RoundTableInDB.model_validate(db_round_table)

    def _store_message(self, message_data: Dict) -> Message:
        """Store a message in the database."""
        message = Message(
            round_table_id=message_data["round_table_id"],
            agent_id=message_data["agent_id"],
            content=message_data["content"],
            message_type=message_data["message_type"]
        )
        self.db.add(message)
        self.db.commit()
        return message

    def get_discussion_history(self, round_table_id: UUID) -> List[Dict]:
        """Get the message history for a round table discussion."""
        messages = (
            self.db.query(Message)
            .filter(Message.round_table_id == round_table_id)
            .order_by(Message.created_at)
            .all()
        )
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
        for participant in participants:
            agent_data = participant["agent"]
            ag2_agent = self.ag2_wrapper.create_agent(agent_data)
            ag2_agents.append(ag2_agent)

        # Create group chat
        group_chat = self.ag2_wrapper.create_group_chat(
            ag2_agents,
            round_table.settings
        )

        # Create chat manager
        manager = self.ag2_wrapper.create_group_chat_manager(group_chat)

        # Format initial message
        initial_message = self._format_initial_message(round_table, prompt)

        # Store the initial message
        self._store_message({
            "round_table_id": round_table_id,
            "agent_id": participants[0]["agent"].id,  # First agent starts
            "content": initial_message,
            "message_type": "introduction"
        })

        # Start the discussion using the first agent as initiator
        result = await self.ag2_wrapper.initiate_group_discussion(
            ag2_agents[0],
            manager,
            initial_message,
            round_table.settings.get("max_rounds")
        )

        # Store all messages from the discussion
        for msg in result.chat_history:
            # Find the agent ID based on the name in the message
            agent = next(
                (p["agent"] for p in participants if p["agent"].name == msg.get("name")),
                participants[0]["agent"]  # Default to first agent if not found
            )
            
            self._store_message({
                "round_table_id": round_table_id,
                "agent_id": agent.id,
                "content": msg.get("content", ""),
                "message_type": "discussion"
            })

        # Update round table status
        round_table.status = "completed"
        round_table.completed_at = datetime.utcnow()
        self.db.commit()

        return {
            "chat_history": result.chat_history,
            "summary": result.summary if hasattr(result, "summary") else None
        }

    def _format_initial_message(self, round_table, prompt: str) -> str:
        """Format the initial message with context and prompt"""
        return f"""Round Table Discussion: {round_table.title}
        
Context: {round_table.context}

Discussion Prompt: {prompt}

Please begin the discussion following your assigned roles."""

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