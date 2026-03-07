from sqlalchemy import Column, String, UUID, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    planner_id = Column(UUID(as_uuid=True), ForeignKey("planners.id"), nullable=False)
    tags = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    planner = relationship("Planner", back_populates="sessions")
