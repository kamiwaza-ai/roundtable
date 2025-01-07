from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services.round_table_service import RoundTableService
from ...schemas.message import MessageInDB

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/round-table/{round_table_id}", response_model=List[MessageInDB])
async def get_round_table_messages(
    round_table_id: UUID,
    db: Session = Depends(get_db)
) -> List[MessageInDB]:
    """Get all messages for a specific round table discussion."""
    service = RoundTableService(db)
    messages = service.get_discussion_history(round_table_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this round table")
    return messages 

@router.delete("/", response_model=bool)
async def delete_all_messages(
    db: Session = Depends(get_db)
) -> bool:
    """Delete all messages from all round tables.
    
    Args:
        db: Database session
        
    Returns:
        bool: True if successful
    """
    service = RoundTableService(db)
    return await service.delete_all_messages() 