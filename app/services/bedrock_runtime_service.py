"""
Bedrock Runtime Service

Provides CRUD operations and query methods for managing Bedrock runtime configurations
in the database. This enables database-driven runtime management.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.bedrock_runtime import BedrockRuntime, RuntimeStatus
from app.models.agent import Agent

logger = logging.getLogger(__name__)


class BedrockRuntimeService:
    """Service for managing Bedrock runtime configurations"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
        self.logger = logger
    
    # ============================================================================
    # CREATE OPERATIONS
    # ============================================================================
    
    def create_runtime(
        self,
        name: str,
        description: Optional[str] = None,
        selected_agent_ids: Optional[List[int]] = None,
        selected_agent_names: Optional[List[str]] = None,
        aws_region: str = "us-east-1",
        aws_account_id: Optional[str] = None,
        memory_mb: int = 512,
        timeout_seconds: int = 300,
        max_concurrency: int = 10,
        logging_level: str = "INFO",
        vpc_enabled: bool = False,
        environment: str = "dev",
        environment_variables: Optional[Dict] = None,
        tags: Optional[Dict] = None,
        runtime_metadata: Optional[Dict] = None
    ) -> BedrockRuntime:
        """Create a new Bedrock runtime configuration"""
        try:
            # Check if runtime with this name already exists
            existing = self.db.query(BedrockRuntime).filter(
                BedrockRuntime.name == name
            ).first()
            
            if existing:
                raise ValueError(f"Runtime with name '{name}' already exists")
            
            # Validate memory allocation
            if not (128 <= memory_mb <= 10240):
                raise ValueError("Memory must be between 128 and 10240 MB")
            
            # Validate timeout
            if timeout_seconds <= 0:
                raise ValueError("Timeout must be greater than 0")
            
            # Create runtime
            runtime = BedrockRuntime(
                name=name,
                description=description,
                selected_agent_ids=selected_agent_ids or [],
                selected_agent_names=selected_agent_names or [],
                aws_region=aws_region,
                aws_account_id=aws_account_id,
                memory_mb=memory_mb,
                timeout_seconds=timeout_seconds,
                max_concurrency=max_concurrency,
                logging_level=logging_level,
                vpc_enabled=vpc_enabled,
                environment=environment,
                environment_variables=environment_variables or {},
                tags=tags or {},
                runtime_metadata=runtime_metadata or {}
            )
            
            self.db.add(runtime)
            self.db.commit()
            self.db.refresh(runtime)
            
            self.logger.info(f"✅ Created Bedrock runtime: {name}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to create runtime: {e}")
            raise
    
    # ============================================================================
    # READ OPERATIONS
    # ============================================================================
    
    def get_runtime_by_id(self, runtime_id: int) -> Optional[BedrockRuntime]:
        """Get runtime by ID"""
        return self.db.query(BedrockRuntime).filter(
            BedrockRuntime.id == runtime_id
        ).first()
    
    def get_runtime_by_name(self, name: str) -> Optional[BedrockRuntime]:
        """Get runtime by name"""
        return self.db.query(BedrockRuntime).filter(
            BedrockRuntime.name == name
        ).first()
    
    def list_runtimes(
        self,
        status: Optional[RuntimeStatus] = None,
        environment: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> tuple[List[BedrockRuntime], int]:
        """
        List runtimes with optional filtering
        
        Returns: (list of runtimes, total count)
        """
        query = self.db.query(BedrockRuntime)
        
        # Apply filters
        if status:
            query = query.filter(BedrockRuntime.status == status)
        
        if environment:
            query = query.filter(BedrockRuntime.environment == environment)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        runtimes = query.offset(offset).limit(limit).all()
        
        return runtimes, total
    
    def list_active_runtimes(self) -> List[BedrockRuntime]:
        """Get all active runtimes"""
        return self.db.query(BedrockRuntime).filter(
            BedrockRuntime.status == RuntimeStatus.ACTIVE
        ).all()
    
    def list_runtimes_by_environment(self, environment: str) -> List[BedrockRuntime]:
        """Get all runtimes in a specific environment"""
        return self.db.query(BedrockRuntime).filter(
            BedrockRuntime.environment == environment
        ).all()
    
    # ============================================================================
    # UPDATE OPERATIONS
    # ============================================================================
    
    def update_runtime(
        self,
        runtime_id: int,
        **updates
    ) -> Optional[BedrockRuntime]:
        """Update runtime configuration"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            # Validate specific fields
            if "memory_mb" in updates:
                if not (128 <= updates["memory_mb"] <= 10240):
                    raise ValueError("Memory must be between 128 and 10240 MB")
            
            if "timeout_seconds" in updates:
                if updates["timeout_seconds"] <= 0:
                    raise ValueError("Timeout must be greater than 0")
            
            if "status" in updates and isinstance(updates["status"], str):
                updates["status"] = RuntimeStatus(updates["status"])
            
            # Update fields
            for key, value in updates.items():
                if key not in ("id", "created_at"):
                    setattr(runtime, key, value)
            
            runtime.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(runtime)
            
            self.logger.info(f"✅ Updated runtime: {runtime.name}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to update runtime: {e}")
            raise
    
    def update_selected_agents(
        self,
        runtime_id: int,
        agent_ids: Optional[List[int]] = None,
        agent_names: Optional[List[str]] = None
    ) -> Optional[BedrockRuntime]:
        """Update selected agents for a runtime"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            # Validate agents exist if IDs are provided
            if agent_ids:
                for agent_id in agent_ids:
                    agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
                    if not agent:
                        raise ValueError(f"Agent with ID {agent_id} not found")
            
            # Validate agents exist if names are provided
            if agent_names:
                for agent_name in agent_names:
                    agent = self.db.query(Agent).filter(Agent.name == agent_name).first()
                    if not agent:
                        raise ValueError(f"Agent with name '{agent_name}' not found")
            
            if agent_ids:
                runtime.selected_agent_ids = agent_ids
            
            if agent_names:
                runtime.selected_agent_names = agent_names
            
            runtime.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(runtime)
            
            self.logger.info(f"✅ Updated agents for runtime: {runtime.name}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to update agents: {e}")
            raise
    
    # ============================================================================
    # DELETE OPERATIONS
    # ============================================================================
    
    def delete_runtime(self, runtime_id: int) -> bool:
        """Delete a runtime configuration"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            runtime_name = runtime.name
            self.db.delete(runtime)
            self.db.commit()
            
            self.logger.info(f"✅ Deleted runtime: {runtime_name}")
            
            return True
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to delete runtime: {e}")
            raise
    
    # ============================================================================
    # STATUS OPERATIONS
    # ============================================================================
    
    def activate_runtime(self, runtime_id: int) -> Optional[BedrockRuntime]:
        """Activate a runtime"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            runtime.activate(self.db)
            self.logger.info(f"✅ Activated runtime: {runtime.name}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to activate runtime: {e}")
            raise
    
    def deactivate_runtime(self, runtime_id: int) -> Optional[BedrockRuntime]:
        """Deactivate a runtime"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            runtime.deactivate(self.db)
            self.logger.info(f"✅ Deactivated runtime: {runtime.name}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to deactivate runtime: {e}")
            raise
    
    def archive_runtime(self, runtime_id: int) -> Optional[BedrockRuntime]:
        """Archive a runtime"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            runtime.archive(self.db)
            self.logger.info(f"✅ Archived runtime: {runtime.name}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to archive runtime: {e}")
            raise
    
    def record_runtime_error(
        self,
        runtime_id: int,
        error_message: str
    ) -> Optional[BedrockRuntime]:
        """Record an error for a runtime"""
        try:
            runtime = self.get_runtime_by_id(runtime_id)
            if not runtime:
                raise ValueError(f"Runtime with ID {runtime_id} not found")
            
            runtime.record_error(self.db, error_message)
            self.logger.warning(f"⚠️ Runtime error recorded: {runtime.name} - {error_message}")
            
            return runtime
        
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Failed to record error: {e}")
            raise
    
    # ============================================================================
    # AGENT OPERATIONS
    # ============================================================================
    
    def get_runtime_agents(self, runtime_id: int) -> List[Agent]:
        """Get agents for a runtime"""
        runtime = self.get_runtime_by_id(runtime_id)
        if not runtime:
            return []
        
        # If agent IDs are stored, retrieve them
        if runtime.selected_agent_ids:
            return self.db.query(Agent).filter(
                Agent.id.in_(runtime.selected_agent_ids)
            ).all()
        
        # If agent names are stored, retrieve them
        if runtime.selected_agent_names:
            return self.db.query(Agent).filter(
                Agent.name.in_(runtime.selected_agent_names)
            ).all()
        
        return []
    
    def validate_agents_exist(self, agent_ids: List[int]) -> bool:
        """Validate that all agents exist"""
        for agent_id in agent_ids:
            agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                return False
        
        return True
    
    # ============================================================================
    # QUERY HELPERS
    # ============================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get runtime statistics"""
        total = self.db.query(BedrockRuntime).count()
        active = self.db.query(BedrockRuntime).filter(
            BedrockRuntime.status == RuntimeStatus.ACTIVE
        ).count()
        inactive = self.db.query(BedrockRuntime).filter(
            BedrockRuntime.status == RuntimeStatus.INACTIVE
        ).count()
        archived = self.db.query(BedrockRuntime).filter(
            BedrockRuntime.status == RuntimeStatus.ARCHIVED
        ).count()
        error = self.db.query(BedrockRuntime).filter(
            BedrockRuntime.status == RuntimeStatus.ERROR
        ).count()
        
        # Get environment distribution
        environments = self.db.query(
            BedrockRuntime.environment,
            func.count(BedrockRuntime.id).label('count')
        ).group_by(BedrockRuntime.environment).all()
        
        environment_dist = {env: count for env, count in environments}
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "archived": archived,
            "error": error,
            "environments": environment_dist
        }

from sqlalchemy import func
