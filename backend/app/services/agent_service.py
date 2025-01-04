# app/services/agent_service.py
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..repositories.agent_repository import AgentRepository
from ..schemas.agent import AgentCreate, AgentUpdate, AgentInDB
from ..models.agent import Agent
from ..utils.ag2_wrapper import AG2Wrapper
from ..utils.llm_config_manager import LLMConfigManager

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AgentRepository(Agent, db)
        self.llm_config_manager = LLMConfigManager()
        self.ag2_wrapper = AG2Wrapper(self.llm_config_manager)

    def create_agent(self, agent_data: AgentCreate) -> AgentInDB:
        # Create database record
        db_agent = self.repository.create(agent_data)
        
        # Initialize AG2 agent
        try:
            ag2_agent = self.ag2_wrapper.create_agent(agent_data)
            if agent_data.tool_config:
                self.ag2_wrapper.register_tools(ag2_agent, agent_data.tool_config)
        except Exception as e:
            # Roll back database transaction
            self.repository.delete(db_agent.id)
            raise HTTPException(status_code=500, 
                              detail=f"Failed to initialize AG2 agent: {str(e)}")
        
        return AgentInDB.model_validate(db_agent)

    def get_agent(self, agent_id: UUID) -> Optional[AgentInDB]:
        db_agent = self.repository.get(agent_id)
        if not db_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentInDB.model_validate(db_agent)

    def get_agents(self) -> List[AgentInDB]:
        agents = self.repository.get_all()
        return [AgentInDB.model_validate(agent) for agent in agents]

    def update_agent(self, agent_id: UUID, agent_data: AgentUpdate) -> AgentInDB:
        db_agent = self.repository.update(agent_id, agent_data)
        if not db_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentInDB.model_validate(db_agent)

    def delete_agent(self, agent_id: UUID) -> bool:
        if not self.repository.delete(agent_id):
            raise HTTPException(status_code=404, detail="Agent not found")
        return True

    def delete_all_agents(self) -> bool:
        self.db.query(Agent).delete()
        self.db.commit()
        return True