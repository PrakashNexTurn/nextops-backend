from sqlalchemy import Column, UUID, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class PlannerAgent(Base):
    __tablename__ = "planner_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planner_id = Column(UUID(as_uuid=True), ForeignKey("planners.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    planner = relationship("Planner", back_populates="planner_agents")
    agent = relationship("Agent", back_populates="planner_agents")
