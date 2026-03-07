from sqlalchemy import Column, String, UUID, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class CloudAccount(Base):
    __tablename__ = "cloud_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(Enum("aws", "azure", "gcp", name="cloud_provider_enum"), nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    credentials = Column(JSON, default={})
    region = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
