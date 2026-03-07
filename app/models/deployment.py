from sqlalchemy import Column, String, UUID, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    bedrock_agent_id = Column(String(255), nullable=True)
    deployment_type = Column(Enum("new", "existing", name="deployment_type_enum"), nullable=False)
    status = Column(Enum("pending", "deployed", name="deployment_status_enum"), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="deployments")
