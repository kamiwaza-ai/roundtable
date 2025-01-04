# app/schemas/round_table.py
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class PhaseConfig(BaseModel):
    id: str
    name: str
    description: str
    allowed_speakers: List[str]
    transition_trigger: str

class RoundTableSettings(BaseModel):
    max_rounds: Optional[int] = None
    speaker_selection_method: str = "auto"  # auto, round_robin, manual
    allow_human_participation: bool = True

class RoundTableBase(BaseModel):
    name: str
    objective: str
    phase_config: Dict[str, Any] = Field(default_factory=lambda: {
        "phases": [
            {
                "id": "initial",
                "name": "Problem Definition",
                "description": "Initial problem presentation and clarification",
                "allowed_speakers": ["all"],
                "transition_trigger": "objective_stated"
            },
            {
                "id": "discussion",
                "name": "Main Discussion",
                "description": "Primary discussion phase",
                "allowed_speakers": ["all"],
                "transition_trigger": "consensus_reached"
            },
            {
                "id": "conclusion",
                "name": "Conclusion",
                "description": "Summary and final decision",
                "allowed_speakers": ["all"],
                "transition_trigger": "conclusion_provided"
            }
        ],
        "transition_rules": {
            "initial": ["discussion"],
            "discussion": ["conclusion"],
            "conclusion": ["end"]
        }
    })
    settings: RoundTableSettings = Field(default_factory=RoundTableSettings)
    
class RoundTableCreate(RoundTableBase):
    participant_ids: List[UUID]

class RoundTableUpdate(RoundTableBase):
    name: Optional[str] = None
    objective: Optional[str] = None
    phase_config: Optional[Dict[str, Any]] = None
    settings: Optional[RoundTableSettings] = None
    current_phase: Optional[str] = None

class RoundTableInDB(RoundTableBase):
    id: UUID
    status: str
    current_phase: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True