# app/repositories/agent_repository.py
from ..repositories.base import BaseRepository
from ..models.agent import Agent
from ..schemas.agent import AgentCreate, AgentUpdate

class AgentRepository(BaseRepository[Agent, AgentCreate, AgentUpdate]):
    pass