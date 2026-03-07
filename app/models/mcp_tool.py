from sqlalchemy import Column, String, UUID, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base

class MCPTool(Base):
    __tablename__ = "mcp_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcp_id = Column(UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    tool_name = Column(String(255), nullable=False)
    description = Column(String(255))
    input_schema = Column(JSON, default={})

    mcp = relationship("MCP", back_populates="mcp_tools")
