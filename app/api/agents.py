from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.agent import Agent
from app.models.agent_tool import AgentTool
from app.schemas.agent_schema import AgentCreate, AgentUpdate, Agent as AgentSchema

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("", response_model=AgentSchema, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent"""
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        tags=agent.tags
    )
    db.add(db_agent)
    db.flush()
    
    # Add agent tools
    if agent.tools:
        for tool_id in agent.tools:
            agent_tool = AgentTool(agent_id=db_agent.id, tool_id=tool_id)
            db.add(agent_tool)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("", response_model=List[AgentSchema])
async def list_agents(db: Session = Depends(get_db)):
    """List all agents"""
    agents = db.query(Agent).all()
    return agents

@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Get a specific agent by ID"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(agent_id: UUID, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """Update an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    update_data = agent_update.model_dump(exclude_unset=True, exclude={"tools"})
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    # Update tools if provided
    if agent_update.tools is not None:
        db.query(AgentTool).filter(AgentTool.agent_id == agent_id).delete()
        for tool_id in agent_update.tools:
            agent_tool = AgentTool(agent_id=agent_id, tool_id=tool_id)
            db.add(agent_tool)
    
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Delete an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    return None

@router.post("/{agent_id}/tools/{tool_id}", status_code=status.HTTP_201_CREATED)
async def add_tool_to_agent(agent_id: UUID, tool_id: UUID, db: Session = Depends(get_db)):
    """Add a tool to an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    existing = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tool already assigned to agent")
    
    agent_tool = AgentTool(agent_id=agent_id, tool_id=tool_id)
    db.add(agent_tool)
    db.commit()
    return {"message": "Tool added to agent"}

@router.delete("/{agent_id}/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tool_from_agent(agent_id: UUID, tool_id: UUID, db: Session = Depends(get_db)):
    """Remove a tool from an agent"""
    agent_tool = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    
    if not agent_tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent tool not found")
    
    db.delete(agent_tool)
    db.commit()
    return None
