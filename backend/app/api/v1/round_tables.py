# app/api/v1/round_tables.py
from typing import List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...db.session import get_db
from ...schemas.round_table import RoundTableCreate, RoundTableUpdate, RoundTableInDB
from ...services.round_table_service import RoundTableService
from ...models.round_table import RoundTable
from ...models.round_table_participant import RoundTableParticipant

router = APIRouter(prefix="/round-tables", tags=["round_tables"])

class DiscussionRequest(BaseModel):
    discussion_prompt: str

@router.post("/", response_model=RoundTableInDB)
async def create_round_table(
    round_table_data: RoundTableCreate,
    db: Session = Depends(get_db)
) -> RoundTableInDB:
    service = RoundTableService(db)
    return await service.create_round_table(round_table_data)

@router.post("/{round_table_id}/phase/{new_phase}", response_model=RoundTableInDB)
async def transition_phase(
    round_table_id: UUID,
    new_phase: str,
    db: Session = Depends(get_db)
) -> RoundTableInDB:
    service = RoundTableService(db)
    return await service.handle_phase_transition(round_table_id, new_phase)

@router.post("/{round_table_id}/discuss")
async def run_discussion(
    round_table_id: UUID,
    request: DiscussionRequest,
    db: Session = Depends(get_db)
):
    """Start and run a round table discussion
    
    Args:
        round_table_id: UUID of the round table
        request: The discussion request containing the prompt
        db: Database session
        
    Returns:
        Dict containing status, round_table_id, and chat_history
    """
    service = RoundTableService(db)
    return await service.run_discussion(round_table_id, request.discussion_prompt)

@router.get("/", response_model=List[RoundTableInDB])
async def get_all_round_tables(
    db: Session = Depends(get_db)
) -> List[RoundTableInDB]:
    """Get all round tables
    
    Args:
        db: Database session
        
    Returns:
        List of round tables
    """
    service = RoundTableService(db)
    return await service.get_all_round_tables()

@router.delete("/", response_model=bool)
async def delete_all_round_tables(
    db: Session = Depends(get_db)
) -> bool:
    """Delete all round tables and their associated data.
    This will cascade delete all messages and participants.
    
    Args:
        db: Database session
        
    Returns:
        bool: True if successful
    """
    service = RoundTableService(db)
    return await service.delete_all_round_tables()