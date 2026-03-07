from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.mcp import MCP
from app.models.mcp_tool import MCPTool
from app.schemas.mcp_schema import MCPCreate, MCPUpdate, MCP as MCPSchema, MCPToolCreate, MCPTool as MCPToolSchema
from app.services.mcp_discovery import MCPDiscoveryService

router = APIRouter(prefix="/mcps", tags=["mcps"])

# Initialize discovery service
discovery_service = MCPDiscoveryService()

@router.post("", response_model=MCPSchema, status_code=status.HTTP_201_CREATED)
async def create_mcp(mcp: MCPCreate, db: Session = Depends(get_db)):
    """Register a new MCP server"""
    db_mcp = MCP(**mcp.model_dump())
    db.add(db_mcp)
    db.commit()
    db.refresh(db_mcp)
    return db_mcp

@router.get("", response_model=List[MCPSchema])
async def list_mcps(db: Session = Depends(get_db)):
    """List all registered MCP servers"""
    mcps = db.query(MCP).all()
    return mcps

@router.get("/{mcp_id}", response_model=MCPSchema)
async def get_mcp(mcp_id: UUID, db: Session = Depends(get_db)):
    """Get a specific MCP server by ID"""
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    return mcp

@router.put("/{mcp_id}", response_model=MCPSchema)
async def update_mcp(mcp_id: UUID, mcp_update: MCPUpdate, db: Session = Depends(get_db)):
    """Update an MCP server configuration"""
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    
    update_data = mcp_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mcp, field, value)
    
    db.commit()
    db.refresh(mcp)
    return mcp

@router.delete("/{mcp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp(mcp_id: UUID, db: Session = Depends(get_db)):
    """Delete an MCP server"""
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    
    # Stop any running processes
    discovery_service.stop_server(mcp_id)
    
    db.delete(mcp)
    db.commit()
    return None

@router.post("/{mcp_id}/tools", response_model=MCPToolSchema, status_code=status.HTTP_201_CREATED)
async def add_mcp_tool(mcp_id: UUID, tool: MCPToolCreate, db: Session = Depends(get_db)):
    """Add a tool to an MCP server"""
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    
    db_tool = MCPTool(mcp_id=mcp_id, **tool.model_dump(exclude={"mcp_id"}))
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

@router.get("/{mcp_id}/tools", response_model=List[MCPToolSchema])
async def list_mcp_tools(mcp_id: UUID, db: Session = Depends(get_db)):
    """List all tools for an MCP server (from database)"""
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    
    tools = db.query(MCPTool).filter(MCPTool.mcp_id == mcp_id).all()
    return tools

@router.post("/{mcp_id}/discover-tools")
async def discover_mcp_tools(
    mcp_id: UUID,
    refresh: bool = False,
    db: Session = Depends(get_db)
):
    """
    Discover and list tools from an MCP server.
    
    This endpoint:
    1. Retrieves MCP server configuration from database
    2. Starts/connects to the MCP server (stdio or SSE)
    3. Queries available tools via MCP protocol
    4. Returns formatted list of tools
    
    Args:
        mcp_id: UUID of the MCP server
        refresh: Force refresh of tool list (bypass cache)
    
    Returns:
        Dictionary with MCP info and discovered tools
    """
    # Get MCP configuration from database
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP server with ID {mcp_id} not found"
        )
    
    # Validate MCP configuration
    mcp_config = {
        "type": mcp.type,
        "command": mcp.command,
        "url": mcp.url,
        "args": mcp.args or {},
        "headers": mcp.headers or {},
        "env_vars": mcp.env_vars or {}
    }
    
    if not discovery_service.validate_mcp_config(mcp.type, mcp_config):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MCP configuration for type '{mcp.type}'. "
                   f"For 'stdio' type, 'command' is required. "
                   f"For 'sse' type, 'url' is required."
        )
    
    try:
        # Discover tools from MCP server
        tools = await discovery_service.discover_tools(mcp_id, mcp_config, refresh=refresh)
        
        return {
            "mcp_id": str(mcp_id),
            "mcp_name": mcp.name,
            "mcp_type": mcp.type,
            "tools_count": len(tools),
            "tools": tools,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover tools: {str(e)}"
        )

@router.post("/{mcp_id}/stop")
async def stop_mcp_server(mcp_id: UUID, db: Session = Depends(get_db)):
    """
    Stop a running MCP server process.
    
    Only applicable for stdio-type MCP servers.
    """
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP server with ID {mcp_id} not found"
        )
    
    discovery_service.stop_server(mcp_id)
    
    return {
        "mcp_id": str(mcp_id),
        "mcp_name": mcp.name,
        "status": "stopped"
    }

@router.post("/clear-cache")
async def clear_tool_cache(mcp_id: str = None):
    """
    Clear MCP tool discovery cache.
    
    Args:
        mcp_id: Optional UUID to clear cache for specific MCP. If not provided, clears all.
    """
    try:
        if mcp_id:
            discovery_service.clear_cache(UUID(mcp_id))
            return {
                "status": "success",
                "message": f"Cache cleared for MCP {mcp_id}"
            }
        else:
            discovery_service.clear_cache()
            return {
                "status": "success",
                "message": "All MCP tool cache cleared"
            }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MCP ID format"
        )
