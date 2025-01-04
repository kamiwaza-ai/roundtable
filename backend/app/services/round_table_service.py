# app/services/round_table_service.py
from typing import List, Optional, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import autogen

from ..repositories.base import BaseRepository
from ..models.round_table import RoundTable, RoundTableParticipant
from ..models.agent import Agent
from ..schemas.round_table import RoundTableCreate, RoundTableUpdate, RoundTableInDB
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

    # async def start_discussion(self, round_table_id: UUID) -> RoundTableInDB:
    #     """Start a round table discussion."""
    #     round_table = self.repository.get(round_table_id)
    #     if not round_table:
    #         raise HTTPException(status_code=404, detail="Round table not found")
        
    #     if round_table.status != "pending":
    #         raise HTTPException(status_code=400, detail="Round table is not in pending state")

    #     # Get participants
    #     participants = self.db.query(RoundTableParticipant)\
    #         .filter(RoundTableParticipant.round_table_id == round_table_id)\
    #         .all()
        
    #     # Create AG2 agents for all participants
    #     ag2_agents = []
    #     for participant in participants:
    #         agent = self.agent_service.get_agent(participant.agent_id)
    #         ag2_agent = self.ag2_wrapper.create_agent(agent)
    #         ag2_agents.append(ag2_agent)

    #     # Create group chat
    #     group_chat = self.ag2_wrapper.create_group_chat(
    #         agents=ag2_agents,
    #         settings=round_table.settings
    #     )
        
    #     # Create group chat manager
    #     chat_manager = self.ag2_wrapper.create_group_chat_manager(group_chat)
        
    #     # Update round table status
    #     round_table.status = "active"
    #     round_table.current_phase = "initial"
    #     self.db.commit()
        
    #     # Start the discussion
    #     # Note: We'll need to handle this asynchronously and store messages
    #     initial_message = (f"Welcome to the round table discussion on: {round_table.objective}. "
    #                      f"We are now in the {round_table.current_phase} phase.")
        
    #     # Start the group chat with the first agent
    #     first_agent = ag2_agents[0]
    #     await first_agent.a_initiate_chat(
    #         chat_manager,
    #         message=initial_message
    #     )
        
    #     return RoundTableInDB.model_validate(round_table)

    async def handle_phase_transition(
        self,
        round_table_id: UUID,
        new_phase: str
    ) -> RoundTableInDB:
        """Handle transition to a new discussion phase."""
        round_table = self.repository.get(round_table_id)
        if not round_table:
            raise HTTPException(status_code=404, detail="Round table not found")
            
        # Validate phase transition
        current_phase = round_table.current_phase
        allowed_transitions = round_table.phase_config["transition_rules"].get(current_phase, [])
        
        if new_phase not in allowed_transitions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid phase transition from {current_phase} to {new_phase}"
            )
        
        # Update phase
        round_table.current_phase = new_phase
        
        # If transitioning to end, mark as completed
        if new_phase == "end":
            round_table.status = "completed"
            round_table.completed_at = datetime.utcnow()
            
        self.db.commit()
        return RoundTableInDB.model_validate(round_table)

    def get_discussion_history(self, round_table_id: UUID) -> List[Dict]:
        """Get the message history for a round table discussion."""
        # We'll implement this when we add message storage
        pass

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

        # Start the discussion using the first agent as initiator
        result = await self.ag2_wrapper.initiate_group_discussion(
            ag2_agents[0],
            manager,
            initial_message,
            round_table.settings.get("max_rounds")
        )

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
            List[RoundTableInDB]: List of all round tables
        """
        round_tables = self.repository.get_all()
        return [RoundTableInDB.model_validate(rt) for rt in round_tables]