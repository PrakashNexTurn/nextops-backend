from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    tool_type: str  # "custom" or "mcp"
    python_code: Optional[str] = None
    mcp_id: Optional[UUID] = None
    tags: Optional[Dict[str, Any]] = {}

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tool_type: Optional[str] = None
    python_code: Optional[str] = None
    mcp_id: Optional[UUID] = None
    tags: Optional[Dict[str, Any]] = None

class Tool(ToolBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
