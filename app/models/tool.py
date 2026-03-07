from sqlalchemy import Column, String, Text, UUID, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    tool_type = Column(Enum("custom", "mcp", name="tool_type_enum"), nullable=False)
    python_code = Column(Text, nullable=True)
    mcp_id = Column(UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=True)
    tags = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    mcp = relationship("MCP", back_populates="tools")
    agent_tools = relationship("AgentTool", back_populates="tool", cascade="all, delete-orphan")
