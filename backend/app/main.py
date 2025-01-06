from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.v1 import agents, round_tables, messages
from .utils.llm_config_manager import LLMConfigManager

app = FastAPI(
    title="Corporate Strategy Simulator",
    description="API for managing AI agents and strategic discussions",
    version="0.0.1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create singleton instance of LLMConfigManager
llm_config_manager = LLMConfigManager()

# Include routers
app.include_router(agents.router, prefix="/api/v1")
app.include_router(round_tables.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
@app.get("/")
async def root():
    return {"message": "Corporate Strategy Simulator API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)