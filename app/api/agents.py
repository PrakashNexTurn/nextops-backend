from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.agent import Agent
from app.models.agent_tool import AgentTool
from app.models.agent_mcp import AgentMCP
from app.models.tool import Tool
from app.models.mcp import MCP
from app.schemas.agent_schema import AgentCreate, AgentUpdate, Agent as AgentSchema, AgentMCP as AgentMCPSchema
from app.services.agent_mcp_service import AgentMCPResolutionService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentSchema, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """
    Create a new agent with support for tool_ids and mcp_ids.
    
    Request example:
    ```json
    {
      "name": "GitHub Agent",
      "description": "Can work with GitHub",
      "system_prompt": "You are a GitHub automation agent",
      "tool_ids": ["tool-uuid-1", "tool-uuid-2"],
      "mcp_ids": ["github-mcp-uuid", "docker-mcp-uuid"]
    }
    ```
    
    The system will:
    1. Create the agent
    2. Resolve all tools from the specified MCPs
    3. Add both direct tools and MCP tools to the agent
    4. Store the MCP associations for reference
    """
    # Check if agent with same name exists
    existing = db.query(Agent).filter(Agent.name == agent_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with name '{agent_data.name}' already exists"
        )
    
    # Create agent instance
    db_agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        system_prompt=agent_data.system_prompt,
        tags=agent_data.tags
    )
    
    try:
        # Use service to create agent with tools and MCPs
        AgentMCPResolutionService.create_agent_with_tools_and_mcps(
            agent=db_agent,
            tool_ids=agent_data.tool_ids or [],
            mcp_ids=agent_data.mcp_ids or [],
            db=db
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Prepare response with resolved tools and MCPs
    tool_ids = AgentMCPResolutionService.get_agent_tool_ids(db_agent.id, db)
    mcp_ids = AgentMCPResolutionService.get_agent_mcp_ids(db_agent.id, db)
    
    response = AgentSchema.from_orm(db_agent)
    response.tool_ids = tool_ids
    response.mcp_ids = mcp_ids
    
    return response


@router.get("", response_model=List[AgentSchema])
async def list_agents(db: Session = Depends(get_db)):
    """
    List all agents with their tool and MCP associations.
    """
    agents = db.query(Agent).all()
    
    result = []
    for agent in agents:
        agent_schema = AgentSchema.from_orm(agent)
        agent_schema.tool_ids = AgentMCPResolutionService.get_agent_tool_ids(agent.id, db)
        agent_schema.mcp_ids = AgentMCPResolutionService.get_agent_mcp_ids(agent.id, db)
        result.append(agent_schema)
    
    return result


@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Get a specific agent by ID with all tool and MCP associations."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent_schema = AgentSchema.from_orm(agent)
    agent_schema.tool_ids = AgentMCPResolutionService.get_agent_tool_ids(agent.id, db)
    agent_schema.mcp_ids = AgentMCPResolutionService.get_agent_mcp_ids(agent.id, db)
    
    return agent_schema


@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(agent_id: UUID, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """
    Update an agent's properties and/or tool/MCP associations.
    
    Example:
    ```json
    {
      "name": "Updated GitHub Agent",
      "tool_ids": ["new-tool-uuid"],
      "mcp_ids": ["new-mcp-uuid"]
    }
    ```
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Update basic properties
    update_data = agent_update.model_dump(
        exclude_unset=True,
        exclude={"tool_ids", "mcp_ids", "tools"}
    )
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.add(agent)
    
    # Update tools and MCPs
    try:
        AgentMCPResolutionService.update_agent_tools_and_mcps(
            agent_id=agent_id,
            tool_ids=agent_update.tool_ids,
            mcp_ids=agent_update.mcp_ids,
            db=db
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    db.commit()
    db.refresh(agent)
    
    agent_schema = AgentSchema.from_orm(agent)
    agent_schema.tool_ids = AgentMCPResolutionService.get_agent_tool_ids(agent.id, db)
    agent_schema.mcp_ids = AgentMCPResolutionService.get_agent_mcp_ids(agent.id, db)
    
    return agent_schema


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Delete an agent and all its associations."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    db.delete(agent)
    db.commit()
    return None


# Tool management endpoints
@router.post("/{agent_id}/tools/{tool_id}", status_code=status.HTTP_201_CREATED)
async def add_tool_to_agent(agent_id: UUID, tool_id: UUID, db: Session = Depends(get_db)):
    """Add a tool to an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    existing = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool already assigned to agent"
        )
    
    agent_tool = AgentTool(agent_id=agent_id, tool_id=tool_id)
    db.add(agent_tool)
    db.commit()
    return {"message": "Tool added to agent"}


@router.delete("/{agent_id}/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tool_from_agent(agent_id: UUID, tool_id: UUID, db: Session = Depends(get_db)):
    """Remove a tool from an agent."""
    agent_tool = db.query(AgentTool).filter(
        AgentTool.agent_id == agent_id,
        AgentTool.tool_id == tool_id
    ).first()
    
    if not agent_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent tool not found"
        )
    
    db.delete(agent_tool)
    db.commit()
    return None


# MCP management endpoints
@router.post("/{agent_id}/mcps/{mcp_id}", status_code=status.HTTP_201_CREATED)
async def add_mcp_to_agent(agent_id: UUID, mcp_id: UUID, db: Session = Depends(get_db)):
    """
    Add an MCP to an agent.
    All tools from this MCP will be automatically added to the agent.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
    if not mcp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP not found"
        )
    
    # Check if already associated
    existing = db.query(AgentMCP).filter(
        AgentMCP.agent_id == agent_id,
        AgentMCP.mcp_id == mcp_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MCP already assigned to agent"
        )
    
    # Add MCP association
    agent_mcp = AgentMCP(agent_id=agent_id, mcp_id=mcp_id)
    db.add(agent_mcp)
    
    # Get all tools from this MCP and add them
    mcp_tools = db.query(Tool).filter(Tool.mcp_id == mcp_id).all()
    for tool in mcp_tools:
        existing_tool = db.query(AgentTool).filter(
            AgentTool.agent_id == agent_id,
            AgentTool.tool_id == tool.id
        ).first()
        if not existing_tool:
            agent_tool = AgentTool(agent_id=agent_id, tool_id=tool.id)
            db.add(agent_tool)
    
    db.commit()
    return {"message": f"MCP added to agent with {len(mcp_tools)} tools"}


@router.delete("/{agent_id}/mcps/{mcp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_mcp_from_agent(agent_id: UUID, mcp_id: UUID, db: Session = Depends(get_db)):
    """
    Remove an MCP from an agent.
    Tools that came from this MCP will be removed (but not shared tools).
    """
    agent_mcp = db.query(AgentMCP).filter(
        AgentMCP.agent_id == agent_id,
        AgentMCP.mcp_id == mcp_id
    ).first()
    
    if not agent_mcp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent MCP association not found"
        )
    
    # Remove MCP association
    db.delete(agent_mcp)
    
    # Get all tools from this MCP
    mcp_tools = db.query(Tool).filter(Tool.mcp_id == mcp_id).all()
    mcp_tool_ids = [tool.id for tool in mcp_tools]
    
    # Remove agent-tool associations for this MCP's tools
    for tool_id in mcp_tool_ids:
        agent_tool = db.query(AgentTool).filter(
            AgentTool.agent_id == agent_id,
            AgentTool.tool_id == tool_id
        ).first()
        if agent_tool:
            db.delete(agent_tool)
    
    db.commit()
    return None


@router.get("/{agent_id}/mcps", response_model=List[AgentMCPSchema])
async def list_agent_mcps(agent_id: UUID, db: Session = Depends(get_db)):
    """Get all MCPs associated with an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent_mcps = db.query(AgentMCP).filter(AgentMCP.agent_id == agent_id).all()
    return agent_mcps
