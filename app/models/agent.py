from sqlalchemy import Column, String, Text, UUID, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    tags = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    agent_tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    planner_agents = relationship("PlannerAgent", back_populates="agent", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="agent", cascade="all, delete-orphan")
