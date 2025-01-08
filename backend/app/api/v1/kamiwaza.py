from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from ...services.kamiwaza_service import KamiwazaService

router = APIRouter(
    prefix="/kamiwaza",
    tags=["kamiwaza"]
)

def get_kamiwaza_service() -> KamiwazaService:
    return KamiwazaService()

@router.get("/models", response_model=List[Dict[str, Any]])
async def get_available_models(
    service: KamiwazaService = Depends(get_kamiwaza_service)
) -> List[Dict[str, Any]]:
    """Get list of available Kamiwaza models"""
    return await service.get_available_models() 