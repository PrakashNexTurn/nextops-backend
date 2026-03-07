from sqlalchemy import Column, UUID, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class AgentMCP(Base):
    """
    Association table between Agents and MCPs.
    Allows tracking which MCPs are associated with an agent
    and automatically including all tools from those MCPs.
    """
    __tablename__ = "agent_mcps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    mcp_id = Column(UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="agent_mcps")
    mcp = relationship("MCP", back_populates="agent_mcps")
