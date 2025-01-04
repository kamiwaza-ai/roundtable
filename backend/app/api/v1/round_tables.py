# app/api/v1/round_tables.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.round_table import RoundTableCreate, RoundTableUpdate, RoundTableInDB
from ...services.round_table_service import RoundTableService

router = APIRouter(prefix="/round-tables", tags=["round_tables"])

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
    discussion_prompt: str,
    db: Session = Depends(get_db)
):
    """Start and run a round table discussion
    
    Args:
        round_table_id: UUID of the round table
        discussion_prompt: The prompt to initiate the discussion
        db: Database session
        
    Returns:
        Dict containing status, round_table_id, and chat_history
    """
    service = RoundTableService(db)
    return await service.run_discussion(round_table_id, discussion_prompt)