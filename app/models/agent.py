from sqlalchemy import Column, String, Text, UUID, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Agent(Base):
    """
    Agent configuration model for dynamic agent management.
    
    Stores agent definitions that can be loaded dynamically at runtime.
    Each agent can have multiple MCP servers and custom configuration.
    """
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic info
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    
    # Agent configuration
    tags = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    agent_tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    agent_mcps = relationship("AgentMCP", back_populates="agent", cascade="all, delete-orphan")
    planner_agents = relationship("PlannerAgent", back_populates="agent", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name})>"
    
    def to_dict(self):
        """Convert agent to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AgentTemplate(Base):
    """
    Pre-defined agent templates that users can clone and customize.
    Provides quick starting points for common agent types.
    """
    __tablename__ = "agent_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template info
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # terraform, azure, kubernetes, etc.
    
    # Template configuration (base for new agents)
    system_prompt_template = Column(Text, nullable=False)
    default_mcp_ids = Column(JSON, default=list)
    default_tool_ids = Column(JSON, default=list)
    default_parameters = Column(JSON, default=dict)
    
    # Template status
    is_public = Column(Boolean, default=True)
    version = Column(String(20), default="1.0.0")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AgentTemplate(id={self.id}, name={self.name}, category={self.category})>"
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "system_prompt_template": self.system_prompt_template,
            "default_mcp_ids": self.default_mcp_ids,
            "default_tool_ids": self.default_tool_ids,
            "default_parameters": self.default_parameters,
            "is_public": self.is_public,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
