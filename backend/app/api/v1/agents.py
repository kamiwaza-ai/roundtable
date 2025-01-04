# app/api/v1/agents.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.agent import AgentCreate, AgentUpdate, AgentInDB
from ...services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentInDB)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
) -> AgentInDB:
    service = AgentService(db)
    return service.create_agent(agent_data)

@router.get("/", response_model=List[AgentInDB])
def get_agents(
    db: Session = Depends(get_db)
) -> List[AgentInDB]:
    service = AgentService(db)
    return service.get_agents()

@router.get("/{agent_id}", response_model=AgentInDB)
def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db)
) -> AgentInDB:
    service = AgentService(db)
    return service.get_agent(agent_id)

@router.put("/{agent_id}", response_model=AgentInDB)
def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
) -> AgentInDB:
    service = AgentService(db)
    return service.update_agent(agent_id, agent_data)

@router.delete("/{agent_id}")
def delete_agent(
    agent_id: UUID,
    db: Session = Depends(get_db)
) -> bool:
    service = AgentService(db)
    return service.delete_agent(agent_id)

@router.delete("/", response_model=bool)
def delete_all_agents(
    db: Session = Depends(get_db)
) -> bool:
    service = AgentService(db)
    return service.delete_all_agents()