from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    tags: Optional[Dict[str, Any]] = {}

class AgentCreate(AgentBase):
    tools: Optional[List[UUID]] = []

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    tools: Optional[List[UUID]] = None

class Agent(AgentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class AgentToolBase(BaseModel):
    agent_id: UUID
    tool_id: UUID

class AgentTool(AgentToolBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
