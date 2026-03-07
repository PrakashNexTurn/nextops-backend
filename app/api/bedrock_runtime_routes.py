"""
API Routes for Bedrock Runtime Management

Provides REST endpoints for managing Bedrock runtime configurations in the database.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.services.bedrock_runtime_service import BedrockRuntimeService
from app.models.bedrock_runtime import BedrockRuntime, RuntimeStatus

router = APIRouter(
    prefix="/bedrock-runtimes",
    tags=["Bedrock Runtimes"]
)


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class CreateRuntimeRequest:
    """Request to create a new runtime"""
    name: str
    description: Optional[str] = None
    selected_agent_ids: Optional[List[int]] = None
    selected_agent_names: Optional[List[str]] = None
    aws_region: str = "us-east-1"
    aws_account_id: Optional[str] = None
    memory_mb: int = 512
    timeout_seconds: int = 300
    max_concurrency: int = 10
    logging_level: str = "INFO"
    vpc_enabled: bool = False
    environment: str = "dev"
    environment_variables: Optional[dict] = None
    tags: Optional[dict] = None
    runtime_metadata: Optional[dict] = None


class UpdateRuntimeRequest:
    """Request to update a runtime"""
    name: Optional[str] = None
    description: Optional[str] = None
    selected_agent_ids: Optional[List[int]] = None
    selected_agent_names: Optional[List[str]] = None
    aws_region: Optional[str] = None
    memory_mb: Optional[int] = None
    timeout_seconds: Optional[int] = None
    max_concurrency: Optional[int] = None
    logging_level: Optional[str] = None
    vpc_enabled: Optional[bool] = None
    environment: Optional[str] = None
    environment_variables: Optional[dict] = None
    tags: Optional[dict] = None
    runtime_metadata: Optional[dict] = None


# ============================================================================
# CREATE ENDPOINTS
# ============================================================================

@router.post("", status_code=201)
async def create_runtime(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Create a new Bedrock runtime configuration
    
    Example:
    ```json
    {
        "name": "production-runtime",
        "description": "Production runtime with DataProcessor and ReportGenerator",
        "selected_agent_ids": [1, 2],
        "aws_region": "us-east-1",
        "memory_mb": 1024,
        "timeout_seconds": 600,
        "environment": "prod"
    }
    ```
    """
    try:
        service = BedrockRuntimeService(db)
        
        runtime = service.create_runtime(
            name=request_data.get("name"),
            description=request_data.get("description"),
            selected_agent_ids=request_data.get("selected_agent_ids"),
            selected_agent_names=request_data.get("selected_agent_names"),
            aws_region=request_data.get("aws_region", "us-east-1"),
            aws_account_id=request_data.get("aws_account_id"),
            memory_mb=request_data.get("memory_mb", 512),
            timeout_seconds=request_data.get("timeout_seconds", 300),
            max_concurrency=request_data.get("max_concurrency", 10),
            logging_level=request_data.get("logging_level", "INFO"),
            vpc_enabled=request_data.get("vpc_enabled", False),
            environment=request_data.get("environment", "dev"),
            environment_variables=request_data.get("environment_variables"),
            tags=request_data.get("tags"),
            runtime_metadata=request_data.get("runtime_metadata")
        )
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# READ ENDPOINTS
# ============================================================================

@router.get("")
async def list_runtimes(
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    offset: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """
    List Bedrock runtime configurations with optional filtering
    
    Query parameters:
    - status: Filter by status (active, inactive, archived, error)
    - environment: Filter by environment (dev, staging, prod)
    - offset: Pagination offset (default: 0)
    - limit: Pagination limit (default: 100, max: 1000)
    """
    try:
        service = BedrockRuntimeService(db)
        
        status_enum = RuntimeStatus(status) if status else None
        
        runtimes, total = service.list_runtimes(
            status=status_enum,
            environment=environment,
            offset=offset,
            limit=min(limit, 1000)
        )
        
        return {
            "status": "success",
            "data": [r.to_dict() for r in runtimes],
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": total
            }
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{runtime_id}")
async def get_runtime(
    runtime_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific Bedrock runtime configuration by ID"""
    try:
        service = BedrockRuntimeService(db)
        runtime = service.get_runtime_by_id(runtime_id)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-name/{name}")
async def get_runtime_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """Get a specific Bedrock runtime configuration by name"""
    try:
        service = BedrockRuntimeService(db)
        runtime = service.get_runtime_by_name(name)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime '{name}' not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{runtime_id}/agents")
async def get_runtime_agents(
    runtime_id: int,
    db: Session = Depends(get_db)
):
    """Get agents associated with a runtime"""
    try:
        service = BedrockRuntimeService(db)
        runtime = service.get_runtime_by_id(runtime_id)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        agents = service.get_runtime_agents(runtime_id)
        
        return {
            "status": "success",
            "data": {
                "runtime_id": runtime_id,
                "runtime_name": runtime.name,
                "agents": [{"id": a.id, "name": a.name} for a in agents]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UPDATE ENDPOINTS
# ============================================================================

@router.put("/{runtime_id}")
async def update_runtime(
    runtime_id: int,
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Update a Bedrock runtime configuration"""
    try:
        service = BedrockRuntimeService(db)
        
        # Filter out None values
        updates = {k: v for k, v in request_data.items() if v is not None}
        
        runtime = service.update_runtime(runtime_id, **updates)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{runtime_id}/agents")
async def update_runtime_agents(
    runtime_id: int,
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Update agents for a runtime"""
    try:
        service = BedrockRuntimeService(db)
        
        runtime = service.update_selected_agents(
            runtime_id,
            agent_ids=request_data.get("agent_ids"),
            agent_names=request_data.get("agent_names")
        )
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DELETE ENDPOINTS
# ============================================================================

@router.delete("/{runtime_id}", status_code=204)
async def delete_runtime(
    runtime_id: int,
    db: Session = Depends(get_db)
):
    """Delete a Bedrock runtime configuration"""
    try:
        service = BedrockRuntimeService(db)
        service.delete_runtime(runtime_id)
        
        return {"status": "success", "message": f"Runtime {runtime_id} deleted"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATUS MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{runtime_id}/activate", status_code=200)
async def activate_runtime(
    runtime_id: int,
    db: Session = Depends(get_db)
):
    """Activate a runtime"""
    try:
        service = BedrockRuntimeService(db)
        runtime = service.activate_runtime(runtime_id)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{runtime_id}/deactivate", status_code=200)
async def deactivate_runtime(
    runtime_id: int,
    db: Session = Depends(get_db)
):
    """Deactivate a runtime"""
    try:
        service = BedrockRuntimeService(db)
        runtime = service.deactivate_runtime(runtime_id)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{runtime_id}/archive", status_code=200)
async def archive_runtime(
    runtime_id: int,
    db: Session = Depends(get_db)
):
    """Archive a runtime"""
    try:
        service = BedrockRuntimeService(db)
        runtime = service.archive_runtime(runtime_id)
        
        if not runtime:
            raise HTTPException(status_code=404, detail=f"Runtime {runtime_id} not found")
        
        return {"status": "success", "data": runtime.to_dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/stats/summary")
async def get_runtime_stats(
    db: Session = Depends(get_db)
):
    """Get Bedrock runtime statistics"""
    try:
        service = BedrockRuntimeService(db)
        stats = service.get_stats()
        
        return {"status": "success", "data": stats}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
