from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.mcp import MCP
from app.models.mcp_tool import MCPTool
from app.schemas.mcp_schema import MCPCreate, MCPUpdate, MCP as MCPSchema, MCPToolCreate, MCPTool as MCPToolSchema

router = APIRouter(prefix="/mcps", tags=["mcps"])

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
    """List all tools for an MCP server"""
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP not found")
    
    tools = db.query(MCPTool).filter(MCPTool.mcp_id == mcp_id).all()
    return tools
