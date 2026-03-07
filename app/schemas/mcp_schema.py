from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class MCPBase(BaseModel):
    name: str
    type: str  # "stdio" or "sse"
    command: Optional[str] = None
    url: Optional[str] = None
    args: Optional[Dict[str, Any]] = {}
    headers: Optional[Dict[str, Any]] = {}
    env_vars: Optional[Dict[str, Any]] = {}

class MCPCreate(MCPBase):
    pass

class MCPUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    command: Optional[str] = None
    url: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    env_vars: Optional[Dict[str, Any]] = None

class MCP(MCPBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class MCPToolBase(BaseModel):
    tool_name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = {}

class MCPToolCreate(MCPToolBase):
    mcp_id: UUID

class MCPTool(MCPToolBase):
    id: UUID
    mcp_id: UUID

    class Config:
        from_attributes = True
