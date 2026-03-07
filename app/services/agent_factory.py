"""
Dynamic Agent Factory Service

Creates Agent instances dynamically based on database configuration.
Loads MCP clients, resolves tools, and builds agents without hardcoding.
Supports selective agent initialization from a list.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from strands import Agent
from model.load import load_model
from bedrock_agentcore.memory import MemoryClient
from strands.hooks import HookProvider

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating dynamic agents from database configuration.
    
    Features:
    - Load agent configs from database
    - Selective agent initialization by name or ID
    - Resolve MCP IDs to MCP clients
    - Resolve tool IDs to actual tools
    - Create Strands Agent instances
    - Support memory hooks and state
    - Graceful error handling for missing agents
    """
    
    def __init__(self, db: Session, memory_client: Optional[MemoryClient] = None):
        """
        Initialize agent factory.
        
        Args:
            db: Database session
            memory_client: Optional memory client for agent state management
        """
        self.db = db
        self.memory_client = memory_client
        self.logger = logger
        self._mcp_client_cache = {}
        self._tool_cache = {}
    
    async def create_agent_from_config(
        self,
        agent_config: Dict[str, Any],
        actor_id: str,
        session_id: str,
        hooks: Optional[List[HookProvider]] = None
    ) -> Agent:
        """
        Create a Strands Agent from configuration.
        
        Args:
            agent_config: Agent configuration dictionary
            actor_id: Actor ID for memory tracking
            session_id: Session ID for memory tracking
            hooks: Optional list of hook providers
            
        Returns:
            Configured Strands Agent instance
        """
        agent_id = agent_config.get("id")
        agent_name = agent_config.get("name", "Unknown")
        
        self.logger.info(f"🔨 Creating agent: {agent_name} (ID: {agent_id})")
        
        # Load MCP clients and tools
        tools = await self._resolve_tools(agent_config)
        
        self.logger.info(f"✅ Resolved {len(tools)} tools for agent {agent_name}")
        
        # Build agent state
        agent_state = {
            "actor_id": actor_id,
            "session_id": session_id,
            "agent_id": agent_id,
            "agent_name": agent_name,
        }
        
        # Merge custom parameters into state
        if "parameters" in agent_config and agent_config["parameters"]:
            agent_state.update(agent_config["parameters"])
        
        # Build agent kwargs
        agent_kwargs = {
            "agent_id": agent_id or agent_name.lower().replace(" ", "_"),
            "name": agent_name,
            "model": load_model(),
            "state": agent_state,
            "tools": tools,
            "system_prompt": agent_config.get("system_prompt", "You are a helpful AI assistant."),
        }
        
        # Add hooks if provided
        if hooks:
            agent_kwargs["hooks"] = hooks
        
        # Create and return agent
        agent = Agent(**agent_kwargs)
        self.logger.info(f"✅ Agent created: {agent_name}")
        
        return agent
    
    async def create_agents_from_database(
        self,
        actor_id: str,
        session_id: str,
        enabled_only: bool = True,
        hooks: Optional[List[HookProvider]] = None,
        selected_agents: Optional[List[Union[str, int]]] = None
    ) -> tuple[List[Agent], Dict[str, Any]]:
        """
        Load agent configurations from database and create Agent instances.
        
        Supports selective agent initialization - only the specified agents will be loaded.
        
        Args:
            actor_id: Actor ID for memory tracking
            session_id: Session ID for memory tracking
            enabled_only: Only load enabled agents (ignored if selected_agents provided)
            hooks: Optional hooks for all agents
            selected_agents: List of agent names or IDs to initialize.
                           If None, loads all agents (filtered by enabled_only).
                           Examples: ["agent-1", "DataProcessor"], [1, 2, 3]
            
        Returns:
            Tuple of (List of created Agent instances, metadata dict with stats)
            
        Raises:
            ValueError: If no agents found matching selected_agents criteria
        """
        from app.models.agent import Agent as AgentModel
        
        self.logger.info("📚 Loading agents from database...")
        
        # Track statistics
        stats = {
            "total_available": 0,
            "total_selected": 0,
            "successfully_created": 0,
            "failed": [],
            "not_found": [],
            "mode": "all" if not selected_agents else "selective"
        }
        
        # Query agents from database
        query = self.db.query(AgentModel)
        
        # If selective mode: filter by selected agents
        if selected_agents:
            self.logger.info(f"🎯 Selective mode: Loading {len(selected_agents)} specified agent(s)")
            
            # Convert selected_agents to list of identifiers
            selected_names = []
            selected_ids = []
            
            for agent_ref in selected_agents:
                if isinstance(agent_ref, int):
                    selected_ids.append(agent_ref)
                else:
                    selected_names.append(str(agent_ref))
            
            # Build query with OR conditions
            if selected_ids or selected_names:
                from sqlalchemy import or_
                conditions = []
                
                if selected_ids:
                    conditions.append(AgentModel.id.in_(selected_ids))
                if selected_names:
                    conditions.append(AgentModel.name.in_(selected_names))
                
                query = query.filter(or_(*conditions))
            else:
                query = query.filter(False)  # No valid references provided
        
        else:
            # Load all agents (respecting enabled_only filter)
            if enabled_only:
                self.logger.info("📋 Loading all enabled agents")
                query = query.filter(AgentModel.enabled == True)
            else:
                self.logger.info("📋 Loading all agents")
        
        agent_configs = query.all()
        stats["total_available"] = len(agent_configs)
        stats["total_selected"] = len(selected_agents) if selected_agents else len(agent_configs)
        
        self.logger.info(f"📦 Found {len(agent_configs)} agent(s) matching criteria")
        
        # Track which agents were requested but not found
        if selected_agents:
            found_ids = {str(config.id) for config in agent_configs}
            found_names = {config.name for config in agent_configs}
            
            for agent_ref in selected_agents:
                agent_ref_str = str(agent_ref)
                if agent_ref_str not in found_ids and agent_ref_str not in found_names:
                    stats["not_found"].append(agent_ref_str)
            
            if stats["not_found"]:
                self.logger.warning(
                    f"⚠️ {len(stats['not_found'])} requested agent(s) not found: "
                    f"{', '.join(stats['not_found'])}"
                )
        
        # Create agents in parallel
        agents = []
        tasks = []
        task_to_config = {}
        
        for config in agent_configs:
            config_dict = config.to_dict()
            task = self.create_agent_from_config(
                agent_config=config_dict,
                actor_id=actor_id,
                session_id=session_id,
                hooks=hooks
            )
            tasks.append(task)
            task_to_config[id(task)] = config
        
        # Run all tasks and handle failures
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    config = agent_configs[i]
                    error_msg = f"{config.name}: {str(result)}"
                    stats["failed"].append(error_msg)
                    self.logger.error(f"❌ Error creating agent: {error_msg}")
                else:
                    agents.append(result)
                    stats["successfully_created"] += 1
        
        stats["successfully_created"] = len(agents)
        
        # Log summary
        self.logger.info(
            f"✅ Summary: {stats['successfully_created']} agent(s) created, "
            f"{len(stats['failed'])} error(s), {len(stats['not_found'])} not found"
        )
        
        return agents, stats
    
    async def _resolve_tools(self, agent_config: Dict[str, Any]) -> List[Any]:
        """
        Resolve MCP IDs and tool IDs to actual tool instances.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            List of tool instances
        """
        tools = []
        
        # Resolve MCP IDs to tools
        mcp_ids = agent_config.get("mcp_ids", [])
        if mcp_ids:
            self.logger.info(f"🔌 Resolving {len(mcp_ids)} MCP(s)...")
            mcp_tools = await self._resolve_mcp_ids(mcp_ids)
            tools.extend(mcp_tools)
            self.logger.info(f"✅ Got {len(mcp_tools)} tools from MCPs")
        
        # Resolve direct tool IDs
        tool_ids = agent_config.get("tool_ids", [])
        if tool_ids:
            self.logger.info(f"🔧 Resolving {len(tool_ids)} tool(s)...")
            direct_tools = await self._resolve_tool_ids(tool_ids)
            tools.extend(direct_tools)
            self.logger.info(f"✅ Got {len(direct_tools)} direct tools")
        
        return tools
    
    async def _resolve_mcp_ids(self, mcp_ids: List[str]) -> List[Any]:
        """
        Resolve MCP IDs to MCP client tools.
        
        Args:
            mcp_ids: List of MCP IDs
            
        Returns:
            List of MCP tools
        """
        from app.services.mcp_dynamic_client import get_mcp_client_by_name
        
        tools = []
        
        for mcp_id in mcp_ids:
            try:
                # Get MCP client
                client = await asyncio.to_thread(
                    get_mcp_client_by_name,
                    mcp_id,
                    self.db
                )
                
                if client:
                    # Extract tools from MCP client
                    if hasattr(client, 'tools'):
                        tools.extend(client.tools)
                    else:
                        tools.append(client)
                    
                    self.logger.info(f"✅ Loaded MCP client: {mcp_id}")
                else:
                    self.logger.warning(f"⚠️ MCP not found: {mcp_id}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error loading MCP {mcp_id}: {e}")
        
        return tools
    
    async def _resolve_tool_ids(self, tool_ids: List[str]) -> List[Any]:
        """
        Resolve tool IDs to actual tool instances.
        
        Args:
            tool_ids: List of tool IDs
            
        Returns:
            List of tools
        """
        from app.models.tool import Tool as ToolModel
        
        tools = []
        
        for tool_id in tool_ids:
            try:
                # Query tool from database
                tool = self.db.query(ToolModel).filter(
                    ToolModel.id == tool_id
                ).first()
                
                if tool:
                    # Convert tool to executable form
                    # This depends on your Tool model structure
                    tools.append(tool)
                    self.logger.info(f"✅ Loaded tool: {tool_id}")
                else:
                    self.logger.warning(f"⚠️ Tool not found: {tool_id}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error loading tool {tool_id}: {e}")
        
        return tools
    
    def get_agent_config(self, agent_id_or_name: str) -> Optional[Dict[str, Any]]:
        """
        Get agent configuration by ID or name.
        
        Args:
            agent_id_or_name: Agent UUID or name
            
        Returns:
            Agent configuration dict or None
        """
        from app.models.agent import Agent as AgentModel
        
        try:
            agent = self.db.query(AgentModel).filter(
                (AgentModel.id == agent_id_or_name) | 
                (AgentModel.name == agent_id_or_name)
            ).first()
            
            if agent:
                return agent.to_dict()
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting agent config: {e}")
            return None
    
    def list_agents(
        self, 
        enabled_only: bool = False, 
        agent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List agent configurations.
        
        Args:
            enabled_only: Only return enabled agents
            agent_type: Filter by agent type
            
        Returns:
            List of agent configs
        """
        from app.models.agent import Agent as AgentModel
        
        query = self.db.query(AgentModel)
        
        if enabled_only:
            query = query.filter(AgentModel.enabled == True)
        
        if agent_type:
            query = query.filter(AgentModel.agent_type == agent_type)
        
        agents = query.all()
        return [agent.to_dict() for agent in agents]
