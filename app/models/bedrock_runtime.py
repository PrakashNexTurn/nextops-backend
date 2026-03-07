"""
Bedrock Runtime Configuration Model

This model manages Bedrock agent core runtime configurations in the database,
allowing dynamic runtime creation and management without code changes.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Text, Enum, Table, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid
from app.db.base import Base


class RuntimeStatus(str, enum.Enum):
    """Status of Bedrock runtime configuration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    ERROR = "error"


class BedrockRuntime(Base):
    """
    Bedrock Agent Core Runtime Configuration
    
    Stores configuration for Bedrock agent runtimes including:
    - Selected agents to initialize
    - Runtime parameters (memory, timeout, concurrency)
    - AWS region and deployment configuration
    - Status tracking and audit information
    """
    __tablename__ = "bedrock_runtimes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic configuration
    name = Column(String(255), unique=True, nullable=False, index=True, doc="Unique runtime name")
    description = Column(Text, nullable=True, doc="Runtime description")
    
    # Agent configuration
    selected_agent_ids = Column(JSON, default=list, nullable=True, doc="List of selected agent IDs to initialize")
    selected_agent_names = Column(JSON, default=list, nullable=True, doc="List of selected agent names to initialize")
    
    # AWS deployment configuration
    aws_region = Column(String(50), default="us-east-1", nullable=False, doc="AWS region for deployment")
    aws_account_id = Column(String(12), nullable=True, doc="AWS account ID for deployment")
    
    # Runtime parameters
    memory_mb = Column(Integer, default=512, nullable=False, doc="Memory allocation in MB (128-10240)")
    timeout_seconds = Column(Integer, default=300, nullable=False, doc="Timeout in seconds")
    max_concurrency = Column(Integer, default=10, nullable=False, doc="Maximum concurrent executions")
    logging_level = Column(String(20), default="INFO", nullable=False, doc="Logging level (ERROR, WARN, INFO, DEBUG)")
    
    # VPC configuration (optional)
    vpc_enabled = Column(Boolean, default=False, nullable=False, doc="Enable VPC deployment")
    vpc_id = Column(String(50), nullable=True, doc="VPC ID for deployment")
    subnet_ids = Column(JSON, default=list, nullable=True, doc="List of subnet IDs")
    security_group_ids = Column(JSON, default=list, nullable=True, doc="List of security group IDs")
    
    # Environment and variables
    environment = Column(String(20), default="dev", nullable=False, doc="Environment (dev, staging, prod)")
    environment_variables = Column(JSON, default=dict, nullable=True, doc="Custom environment variables")
    
    # Status and metadata
    status = Column(
        Enum(RuntimeStatus),
        default=RuntimeStatus.INACTIVE,
        nullable=False,
        doc="Runtime status"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        doc="Creation timestamp"
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last update timestamp"
    )
    
    # Error tracking
    last_error = Column(Text, nullable=True, doc="Last error message")
    last_error_at = Column(DateTime, nullable=True, doc="Timestamp of last error")
    
    # Additional metadata
    tags = Column(JSON, default=dict, nullable=True, doc="Tags for runtime categorization")
    runtime_metadata = Column(JSON, default=dict, nullable=True, doc="Additional runtime metadata")
    
    # Relationships
    agents = relationship(
        "Agent",
        secondary="bedrock_runtime_agents",
        back_populates="runtimes",
        doc="Agents associated with this runtime"
    )
    
    def __repr__(self):
        return f"<BedrockRuntime(id={self.id}, name={self.name}, status={self.status}, agents={len(self.selected_agent_ids or [])})"
    
    def to_dict(self):
        """Convert runtime configuration to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "selected_agent_ids": self.selected_agent_ids or [],
            "selected_agent_names": self.selected_agent_names or [],
            "aws_region": self.aws_region,
            "aws_account_id": self.aws_account_id,
            "memory_mb": self.memory_mb,
            "timeout_seconds": self.timeout_seconds,
            "max_concurrency": self.max_concurrency,
            "logging_level": self.logging_level,
            "vpc_enabled": self.vpc_enabled,
            "vpc_id": self.vpc_id,
            "subnet_ids": self.subnet_ids or [],
            "security_group_ids": self.security_group_ids or [],
            "environment": self.environment,
            "environment_variables": self.environment_variables or {},
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_error": self.last_error,
            "last_error_at": self.last_error_at.isoformat() if self.last_error_at else None,
            "tags": self.tags or {},
            "runtime_metadata": self.runtime_metadata or {}
        }
    
    @staticmethod
    def create_from_dict(db, data: dict):
        """Create runtime from dictionary"""
        runtime = BedrockRuntime(
            name=data.get("name"),
            description=data.get("description"),
            selected_agent_ids=data.get("selected_agent_ids", []),
            selected_agent_names=data.get("selected_agent_names", []),
            aws_region=data.get("aws_region", "us-east-1"),
            aws_account_id=data.get("aws_account_id"),
            memory_mb=data.get("memory_mb", 512),
            timeout_seconds=data.get("timeout_seconds", 300),
            max_concurrency=data.get("max_concurrency", 10),
            logging_level=data.get("logging_level", "INFO"),
            vpc_enabled=data.get("vpc_enabled", False),
            vpc_id=data.get("vpc_id"),
            subnet_ids=data.get("subnet_ids", []),
            security_group_ids=data.get("security_group_ids", []),
            environment=data.get("environment", "dev"),
            environment_variables=data.get("environment_variables", {}),
            status=RuntimeStatus(data.get("status", "inactive")),
            tags=data.get("tags", {}),
            runtime_metadata=data.get("runtime_metadata", {})
        )
        
        db.add(runtime)
        db.commit()
        db.refresh(runtime)
        
        return runtime
    
    def update_from_dict(self, db, data: dict):
        """Update runtime configuration"""
        for key, value in data.items():
            if key not in ("id", "created_at", "last_error_at"):
                if key == "status" and isinstance(value, str):
                    setattr(self, key, RuntimeStatus(value))
                else:
                    setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(self)
        
        return self
    
    def record_error(self, db, error_message: str):
        """Record an error"""
        self.last_error = error_message
        self.last_error_at = datetime.utcnow()
        self.status = RuntimeStatus.ERROR
        db.commit()
        db.refresh(self)
    
    def activate(self, db):
        """Activate runtime"""
        self.status = RuntimeStatus.ACTIVE
        self.last_error = None
        self.last_error_at = None
        db.commit()
        db.refresh(self)
    
    def deactivate(self, db):
        """Deactivate runtime"""
        self.status = RuntimeStatus.INACTIVE
        db.commit()
        db.refresh(self)
    
    def archive(self, db):
        """Archive runtime"""
        self.status = RuntimeStatus.ARCHIVED
        db.commit()
        db.refresh(self)


# Association table for BedrockRuntime -> Agent relationship
bedrock_runtime_agents = Table(
    'bedrock_runtime_agents',
    Base.metadata,
    Column('runtime_id', Integer, ForeignKey('bedrock_runtimes.id', ondelete='CASCADE'), primary_key=True),
    Column('agent_id', UUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), primary_key=True)
)
