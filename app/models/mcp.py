from sqlalchemy import Column, String, UUID, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class MCP(Base):
    __tablename__ = "mcps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(Enum("stdio", "sse", name="mcp_type_enum"), nullable=False)
    command = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    args = Column(JSON, default={})
    headers = Column(JSON, default={})
    env_vars = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    tools = relationship("Tool", back_populates="mcp", cascade="all, delete-orphan")
    mcp_tools = relationship("MCPTool", back_populates="mcp", cascade="all, delete-orphan")
