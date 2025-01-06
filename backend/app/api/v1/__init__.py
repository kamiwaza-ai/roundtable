from fastapi import APIRouter
from .agents import router as agents_router
from .round_tables import router as round_tables_router
from .messages import router as messages_router

router = APIRouter()
router.include_router(agents_router)
router.include_router(round_tables_router)
router.include_router(messages_router)
