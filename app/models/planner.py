from sqlalchemy import Column, String, Text, UUID, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Planner(Base):
    __tablename__ = "planners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    system_prompt = Column(Text, nullable=False)
    tags = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    planner_agents = relationship("PlannerAgent", back_populates="planner", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="planner", cascade="all, delete-orphan")
