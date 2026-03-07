from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.tool import Tool
from app.schemas.tool_schema import ToolCreate, ToolUpdate, Tool as ToolSchema

router = APIRouter(prefix="/tools", tags=["tools"])

@router.post("", response_model=ToolSchema, status_code=status.HTTP_201_CREATED)
async def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    """Create a new tool"""
    db_tool = Tool(**tool.model_dump())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

@router.get("", response_model=List[ToolSchema])
async def list_tools(db: Session = Depends(get_db)):
    """List all tools"""
    tools = db.query(Tool).all()
    return tools

@router.get("/{tool_id}", response_model=ToolSchema)
async def get_tool(tool_id: UUID, db: Session = Depends(get_db)):
    """Get a specific tool by ID"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool

@router.put("/{tool_id}", response_model=ToolSchema)
async def update_tool(tool_id: UUID, tool_update: ToolUpdate, db: Session = Depends(get_db)):
    """Update a tool"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    
    update_data = tool_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tool, field, value)
    
    db.commit()
    db.refresh(tool)
    return tool

@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: UUID, db: Session = Depends(get_db)):
    """Delete a tool"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    
    db.delete(tool)
    db.commit()
    return None
