from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class PlannerBase(BaseModel):
    name: str
    system_prompt: str
    tags: Optional[Dict[str, Any]] = {}

class PlannerCreate(PlannerBase):
    agents: Optional[List[UUID]] = []

class PlannerUpdate(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    agents: Optional[List[UUID]] = None

class Planner(PlannerBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class PlannerAgentBase(BaseModel):
    planner_id: UUID
    agent_id: UUID

class PlannerAgent(PlannerAgentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
