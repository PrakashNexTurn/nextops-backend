from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class SessionBase(BaseModel):
    name: str
    planner_id: UUID
    tags: Optional[Dict[str, Any]] = {}

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    name: Optional[str] = None
    planner_id: Optional[UUID] = None
    tags: Optional[Dict[str, Any]] = None

class Session(SessionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CloudAccountBase(BaseModel):
    provider: str  # "aws", "azure", "gcp"
    name: str
    region: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = {}

class CloudAccountCreate(CloudAccountBase):
    pass

class CloudAccountUpdate(BaseModel):
    provider: Optional[str] = None
    name: Optional[str] = None
    region: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None

class CloudAccount(CloudAccountBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class DeploymentBase(BaseModel):
    agent_id: UUID
    bedrock_agent_id: Optional[str] = None
    deployment_type: str  # "new" or "existing"
    status: str  # "pending" or "deployed"

class DeploymentCreate(BaseModel):
    agent_id: UUID
    deployment_type: str  # "new" or "existing"

class DeploymentUpdate(BaseModel):
    bedrock_agent_id: Optional[str] = None
    status: Optional[str] = None

class Deployment(DeploymentBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
