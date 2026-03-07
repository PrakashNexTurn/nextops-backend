"""
Dynamic Agent Factory Service

Creates Agent instances dynamically based on database configuration.
Loads MCP clients, resolves tools, and builds agents without hardcoding.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
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
    - Resolve MCP IDs to MCP clients
    - Resolve tool IDs to actual tools
    - Create Strands Agent instances
    - Support memory hooks and state
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
        hooks: Optional[List[HookProvider]] = None
    ) -> List[Agent]:
        """
        Load all agent configurations from database and create Agent instances.
        
        Args:
            actor_id: Actor ID for memory tracking
            session_id: Session ID for memory tracking
            enabled_only: Only load enabled agents
            hooks: Optional hooks for all agents
            
        Returns:
            List of created Agent instances
        """
        from app.models.agent import Agent as AgentModel
        
        self.logger.info("📚 Loading agents from database...")
        
        # Query agents from database
        query = self.db.query(AgentModel)
        if enabled_only:
            query = query.filter(AgentModel.enabled == True)
        
        agent_configs = query.all()
        self.logger.info(f"📦 Found {len(agent_configs)} agent(s)")
        
        # Create agents in parallel
        agents = []
        tasks = []
        
        for config in agent_configs:
            config_dict = config.to_dict()
            task = self.create_agent_from_config(
                agent_config=config_dict,
                actor_id=actor_id,
                session_id=session_id,
                hooks=hooks
            )
            tasks.append(task)
        
        if tasks:
            agents = await asyncio.gather(*tasks)
        
        self.logger.info(f"✅ Created {len(agents)} agent(s)")
        return agents
    
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
