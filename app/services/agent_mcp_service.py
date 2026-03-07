"""
Service for handling agent creation with MCP-to-tool resolution.
Supports creating agents by specifying MCP IDs directly.
"""

from typing import List, Optional, Set
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.agent import Agent
from app.models.agent_tool import AgentTool
from app.models.agent_mcp import AgentMCP
from app.models.tool import Tool
from app.models.mcp import MCP


class AgentMCPResolutionService:
    """
    Service to resolve MCP IDs to their tools and manage agent-MCP associations.
    """

    @staticmethod
    def resolve_mcp_ids_to_tools(
        mcp_ids: List[UUID], 
        db: Session
    ) -> Set[UUID]:
        """
        Resolve a list of MCP IDs to all their available tools.
        
        Args:
            mcp_ids: List of MCP IDs to resolve
            db: Database session
            
        Returns:
            Set of tool IDs from all specified MCPs
            
        Raises:
            ValueError: If any MCP ID doesn't exist
        """
        tool_ids = set()
        
        for mcp_id in mcp_ids:
            # Verify MCP exists
            mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
            if not mcp:
                raise ValueError(f"MCP with ID {mcp_id} not found")
            
            # Get all tools for this MCP
            mcp_tools = db.query(Tool).filter(Tool.mcp_id == mcp_id).all()
            tool_ids.update([tool.id for tool in mcp_tools])
        
        return tool_ids

    @staticmethod
    def create_agent_with_tools_and_mcps(
        agent: Agent,
        tool_ids: List[UUID],
        mcp_ids: List[UUID],
        db: Session
    ) -> Agent:
        """
        Create an agent with specified tools and MCPs.
        Automatically resolves MCP IDs to their tools.
        
        Args:
            agent: Agent model instance to save
            tool_ids: List of direct tool IDs
            mcp_ids: List of MCP IDs
            db: Database session
            
        Returns:
            Created agent with all associations
        """
        # Resolve MCP IDs to tools
        resolved_tool_ids = set(tool_ids)
        
        if mcp_ids:
            mcp_tools = AgentMCPResolutionService.resolve_mcp_ids_to_tools(
                mcp_ids, db
            )
            resolved_tool_ids.update(mcp_tools)
        
        # Save agent
        db.add(agent)
        db.flush()
        
        # Add direct tool associations
        for tool_id in resolved_tool_ids:
            # Verify tool exists
            tool = db.query(Tool).filter(Tool.id == tool_id).first()
            if not tool:
                db.rollback()
                raise ValueError(f"Tool with ID {tool_id} not found")
            
            agent_tool = AgentTool(agent_id=agent.id, tool_id=tool_id)
            db.add(agent_tool)
        
        # Add MCP associations (for reference)
        for mcp_id in mcp_ids:
            agent_mcp = AgentMCP(agent_id=agent.id, mcp_id=mcp_id)
            db.add(agent_mcp)
        
        db.commit()
        db.refresh(agent)
        
        return agent

    @staticmethod
    def get_agent_tool_ids(agent_id: UUID, db: Session) -> List[UUID]:
        """Get all tool IDs for an agent (both direct and from MCPs)."""
        agent_tools = db.query(AgentTool.tool_id).filter(
            AgentTool.agent_id == agent_id
        ).all()
        return [tool.tool_id for tool in agent_tools]

    @staticmethod
    def get_agent_mcp_ids(agent_id: UUID, db: Session) -> List[UUID]:
        """Get all MCP IDs associated with an agent."""
        agent_mcps = db.query(AgentMCP.mcp_id).filter(
            AgentMCP.agent_id == agent_id
        ).all()
        return [mcp.mcp_id for mcp in agent_mcps]

    @staticmethod
    def update_agent_tools_and_mcps(
        agent_id: UUID,
        tool_ids: Optional[List[UUID]],
        mcp_ids: Optional[List[UUID]],
        db: Session
    ) -> None:
        """
        Update an agent's tools and MCP associations.
        
        Args:
            agent_id: Agent ID to update
            tool_ids: New list of direct tool IDs (if provided)
            mcp_ids: New list of MCP IDs (if provided)
            db: Database session
        """
        # Update tool associations
        if tool_ids is not None:
            # Delete existing tool associations
            db.query(AgentTool).filter(AgentTool.agent_id == agent_id).delete()
            
            # Resolve MCP IDs to tools if provided
            resolved_tool_ids = set(tool_ids)
            if mcp_ids:
                mcp_tools = AgentMCPResolutionService.resolve_mcp_ids_to_tools(
                    mcp_ids, db
                )
                resolved_tool_ids.update(mcp_tools)
            
            # Add new tool associations
            for tool_id in resolved_tool_ids:
                tool = db.query(Tool).filter(Tool.id == tool_id).first()
                if not tool:
                    db.rollback()
                    raise ValueError(f"Tool with ID {tool_id} not found")
                
                agent_tool = AgentTool(agent_id=agent_id, tool_id=tool_id)
                db.add(agent_tool)
        
        # Update MCP associations
        if mcp_ids is not None:
            # Delete existing MCP associations
            db.query(AgentMCP).filter(AgentMCP.agent_id == agent_id).delete()
            
            # Add new MCP associations
            for mcp_id in mcp_ids:
                mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
                if not mcp:
                    db.rollback()
                    raise ValueError(f"MCP with ID {mcp_id} not found")
                
                agent_mcp = AgentMCP(agent_id=agent_id, mcp_id=mcp_id)
                db.add(agent_mcp)
        
        db.commit()
