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
    """Create agent with support for direct tool IDs and MCP IDs"""
    tool_ids: Optional[List[UUID]] = []
    mcp_ids: Optional[List[UUID]] = []
    # Legacy support - tools field maps to tool_ids
    tools: Optional[List[UUID]] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Handle backward compatibility: if tools is provided, use it as tool_ids
        if self.tools is not None and self.tool_ids is None:
            self.tool_ids = self.tools
        elif self.tools is None:
            self.tools = self.tool_ids

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    tool_ids: Optional[List[UUID]] = None
    mcp_ids: Optional[List[UUID]] = None
    # Legacy support
    tools: Optional[List[UUID]] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Handle backward compatibility
        if self.tools is not None and self.tool_ids is None:
            self.tool_ids = self.tools

class Agent(AgentBase):
    id: UUID
    created_at: datetime
    tool_ids: List[UUID] = []  # Direct tool associations
    mcp_ids: List[UUID] = []   # MCP associations (for reference)

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

class AgentMCP(BaseModel):
    """Represents association between Agent and MCP"""
    id: UUID
    agent_id: UUID
    mcp_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
