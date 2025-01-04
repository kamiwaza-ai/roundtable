# app/services/round_table_service.py
from typing import List, Optional, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..repositories.base import BaseRepository
from ..models.round_table import RoundTable, RoundTableParticipant
from ..models.agent import Agent
from ..schemas.round_table import RoundTableCreate, RoundTableUpdate, RoundTableInDB
from ..utils.ag2_wrapper import AG2Wrapper
from .agent_service import AgentService

class RoundTableService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(RoundTable, db)
        self.agent_service = AgentService(db)
        self.ag2_wrapper = AG2Wrapper()
        
    async def create_round_table(self, data: RoundTableCreate) -> RoundTableInDB:
        """Create a new round table discussion."""
        # Verify all participants exist
        participants = []
        for agent_id in data.participant_ids:
            agent = self.agent_service.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            participants.append(agent)

        # Create database record
        db_round_table = self.repository.create(data)
        
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

    async def run_discussion(
        self,
        round_table_id: UUID,
        discussion_prompt: str
    ) -> Dict:
        """Run a round table discussion with the given prompt.
        
        Args:
            round_table_id: UUID of the round table discussion
            discussion_prompt: The prompt to initiate the discussion
            
        Returns:
            Dict containing status, round_table_id, and chat_history
            
        Raises:
            HTTPException: If round table not found or in invalid state
        """
        round_table = self.repository.get(round_table_id)
        if not round_table:
            raise HTTPException(status_code=404, detail="Round table not found")
        
        if round_table.status != "pending":
            raise HTTPException(status_code=400, detail="Round table must be in pending state")

        # Get all participants and create AG2 agents
        participants = (
            self.db.query(RoundTableParticipant)
            .filter(RoundTableParticipant.round_table_id == round_table_id)
            .all()
        )

        ag2_agents = []
        for participant in participants:
            db_agent = self.agent_service.get_agent(participant.agent_id)
            ag2_agent = self.ag2_wrapper.create_agent(db_agent)
            if db_agent.tool_config:
                self.ag2_wrapper.register_tools(ag2_agent, db_agent.tool_config)
            ag2_agents.append(ag2_agent)

        # Create and configure group chat
        group_chat = self.ag2_wrapper.create_group_chat(
            agents=ag2_agents,
            settings=round_table.settings
        )

        # Run the discussion
        try:
            # Update status
            round_table.status = "active"
            round_table.current_phase = "initial"
            self.db.commit()

            # Format initial message with objective and prompt
            initial_message = (
                f"Round Table Discussion\n"
                f"Objective: {round_table.objective}\n"
                f"Task: {discussion_prompt}\n"
                f"Current Phase: {round_table.current_phase}\n"
                "Please discuss this topic and work together to reach a conclusion."
            )

            # Run the discussion
            chat_history = await self.ag2_wrapper.run_group_discussion(
                group_chat=group_chat,
                initial_message=initial_message,
                max_rounds=round_table.settings.max_rounds
            )

            # Update status to completed
            round_table.status = "completed"
            round_table.completed_at = datetime.utcnow()
            self.db.commit()

            return {
                "status": "completed",
                "round_table_id": round_table_id,
                "chat_history": chat_history
            }

        except Exception as e:
            round_table.status = "error"
            self.db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"Error running discussion: {str(e)}"
            )