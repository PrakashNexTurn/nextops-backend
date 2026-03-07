"""
Selective MCP Loader Service

This module implements selective loading of MCP clients based on agent requirements.
Instead of loading all 7 MCPs for every agent, it:
1. Analyzes agent configurations
2. Collects unique required MCPs
3. Creates only necessary asyncio tasks
4. Returns only needed MCP clients to agents

Benefits:
- Faster initialization (load only what's needed)
- Lower memory usage (unused MCPs not instantiated)
- Better scalability (add more agents without proportional overhead)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentMCPRequirement:
    """Represents an agent's MCP requirements"""
    agent_name: str
    required_mcp_ids: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"Agent({self.agent_name}): {self.required_mcp_ids}"


class SelectiveMCPLoader:
    """
    Service that intelligently loads only required MCP clients.
    
    Usage:
        loader = SelectiveMCPLoader()
        requirements = [
            AgentMCPRequirement("servicenow", ["servicenow-mcp"]),
            AgentMCPRequirement("azure", ["azure-mcp"]),
        ]
        mcp_clients = await loader.load_required_mcps(requirements, mcp_factory)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._mcp_task_map = {}
        self._loaded_clients = {}
    
    def analyze_requirements(self, agent_configs: List[Dict[str, Any]]) -> set:
        """
        Analyze all agent configurations to determine unique required MCPs.
        
        Args:
            agent_configs: List of agent configuration dictionaries
            
        Returns:
            Set of unique required MCP IDs
            
        Example:
            agent_configs = [
                {"name": "servicenow", "required_mcp_ids": ["servicenow-mcp"]},
                {"name": "azure", "required_mcp_ids": ["azure-mcp"]},
            ]
            required = loader.analyze_requirements(agent_configs)
            # Returns: {"servicenow-mcp", "azure-mcp"}
        """
        required_mcps = set()
        
        for config in agent_configs:
            required_ids = config.get("required_mcp_ids", [])
            if required_ids:
                required_mcps.update(required_ids)
                self.logger.info(
                    f"✓ Agent '{config.get('name')}' requires: {required_ids}"
                )
            else:
                self.logger.warning(
                    f"⚠ Agent '{config.get('name')}' has no MCP requirements specified"
                )
        
        self.logger.info(
            f"📊 Total unique required MCPs: {len(required_mcps)} - {required_mcps}"
        )
        return required_mcps
    
    async def load_required_mcps(
        self,
        agent_configs: List[Dict[str, Any]],
        mcp_factory: Any
    ) -> Dict[str, Any]:
        """
        Selectively load only required MCP clients.
        
        Args:
            agent_configs: List of agent configurations with required_mcp_ids
            mcp_factory: Factory object with methods like get_servicenow_mcp()
            
        Returns:
            Dictionary mapping MCP ID to client instance
            
        Example:
            mcp_clients = await loader.load_required_mcps(agent_configs, mcp_factory)
            # Returns: {"servicenow-mcp": <client>, "azure-mcp": <client>}
        """
        # Step 1: Analyze requirements
        required_mcps = self.analyze_requirements(agent_configs)
        
        if not required_mcps:
            self.logger.warning("⚠ No MCPs required by any agent!")
            return {}
        
        # Step 2: Create asyncio tasks only for required MCPs
        self.logger.info(f"🔄 Creating asyncio tasks for {len(required_mcps)} required MCPs...")
        tasks = self._create_selective_tasks(required_mcps, mcp_factory)
        
        if not tasks:
            self.logger.warning("⚠ No asyncio tasks created!")
            return {}
        
        # Step 3: Wait for all required tasks
        self.logger.info(f"⏳ Waiting for {len(tasks)} MCP tasks to complete...")
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Step 4: Map results back to MCP IDs
        self.logger.info("📦 Mapping results back to MCP IDs...")
        mcp_clients = {}
        for mcp_id, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Failed to load {mcp_id}: {result}")
            else:
                mcp_clients[mcp_id] = result
                self.logger.info(f"✅ Loaded {mcp_id}")
        
        self._loaded_clients = mcp_clients
        return mcp_clients
    
    def _create_selective_tasks(
        self,
        required_mcps: set,
        mcp_factory: Any
    ) -> Dict[str, asyncio.Task]:
        """
        Create asyncio tasks only for required MCPs.
        
        Args:
            required_mcps: Set of MCP IDs to load
            mcp_factory: Factory with MCP creation methods
            
        Returns:
            Dictionary mapping MCP ID to asyncio task
        """
        tasks = {}
        
        # Map MCP ID to factory method
        mcp_methods = {
            "servicenow-mcp": lambda: mcp_factory.get_servicenow_mcp(),
            "azure-mcp": lambda: mcp_factory.get_azure_mcp(),
            "kubernetes-mcp": lambda: mcp_factory.get_kubernetes_mcp(),
            "terraform-mcp": lambda: mcp_factory.get_terraform_mcp(),
            "github-mcp": lambda: mcp_factory.get_github_http_mcp_client(),
            "gcp-mcp": lambda: mcp_factory.get_gcp_mcp(),
            "postgres-mcp": lambda: mcp_factory.get_postgres_mcp(),
        }
        
        for mcp_id in required_mcps:
            if mcp_id not in mcp_methods:
                self.logger.warning(f"⚠ Unknown MCP ID: {mcp_id}")
                continue
            
            self.logger.info(f"📌 Creating task for {mcp_id}")
            try:
                task = asyncio.create_task(
                    self._safe_mcp_load(mcp_id, mcp_methods[mcp_id])
                )
                tasks[mcp_id] = task
            except Exception as e:
                self.logger.error(f"❌ Error creating task for {mcp_id}: {e}")
        
        return tasks
    
    async def _safe_mcp_load(self, mcp_id: str, loader_func) -> Any:
        """
        Safely load an MCP with error handling.
        
        Args:
            mcp_id: ID of the MCP being loaded
            loader_func: Function that loads the MCP
            
        Returns:
            MCP client instance or raises exception
        """
        try:
            self.logger.debug(f"Loading {mcp_id}...")
            result = await loader_func()
            self.logger.debug(f"✓ {mcp_id} loaded successfully")
            return result
        except Exception as e:
            self.logger.error(f"✗ Error loading {mcp_id}: {type(e).__name__}: {e}")
            raise
    
    def get_agent_mcps(
        self,
        agent_name: str,
        agent_configs: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        Get only the MCP clients required by a specific agent.
        
        Args:
            agent_name: Name of the agent
            agent_configs: List of all agent configurations
            
        Returns:
            List of MCP clients required by the agent
            
        Example:
            mcps = loader.get_agent_mcps("servicenow", agent_configs)
            # Returns: [<servicenow_mcp_client>]
        """
        # Find agent config
        agent_config = next(
            (cfg for cfg in agent_configs if cfg.get("name") == agent_name),
            None
        )
        
        if not agent_config:
            self.logger.warning(f"⚠ Agent config not found: {agent_name}")
            return []
        
        # Get required MCP IDs
        required_ids = agent_config.get("required_mcp_ids", [])
        
        # Get MCP clients for this agent
        agent_mcps = [
            self._loaded_clients[mcp_id]
            for mcp_id in required_ids
            if mcp_id in self._loaded_clients
        ]
        
        self.logger.info(
            f"📌 Agent '{agent_name}' gets {len(agent_mcps)} MCPs: {required_ids}"
        )
        
        return agent_mcps
    
    def get_mcp_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded MCPs.
        
        Returns:
            Dictionary with loading statistics
        """
        return {
            "total_loaded": len(self._loaded_clients),
            "mcp_ids": list(self._loaded_clients.keys()),
            "loaded_clients": self._loaded_clients
        }


def create_agent_configs_with_mcp_requirements() -> List[Dict[str, Any]]:
    """
    Create agent configurations with MCP requirements.
    
    Returns:
        List of agent configurations with required_mcp_ids
    """
    return [
        {
            "name": "servicenow",
            "required_mcp_ids": ["servicenow-mcp"],
            "description": "ServiceNow orchestrator agent"
        },
        {
            "name": "azure",
            "required_mcp_ids": ["azure-mcp"],
            "description": "Azure infrastructure agent"
        },
        {
            "name": "kubernetes",
            "required_mcp_ids": ["kubernetes-mcp"],
            "description": "Kubernetes cluster agent"
        },
        {
            "name": "terraform",
            "required_mcp_ids": ["terraform-mcp"],
            "description": "Terraform IaC agent"
        },
        {
            "name": "github",
            "required_mcp_ids": ["github-mcp"],
            "description": "GitHub repository agent"
        },
        {
            "name": "gcp",
            "required_mcp_ids": ["gcp-mcp"],
            "description": "Google Cloud Platform agent"
        },
        {
            "name": "postgres",
            "required_mcp_ids": ["postgres-mcp"],
            "description": "PostgreSQL database agent"
        }
    ]


# Example: Multi-agent with shared MCPs
def create_multi_agent_config_example() -> List[Dict[str, Any]]:
    """
    Example: Agents that share MCPs (more efficient)
    
    Returns:
        List of agent configurations for multi-agent scenarios
    """
    return [
        {
            "name": "devops-orchestrator",
            "required_mcp_ids": ["servicenow-mcp", "azure-mcp", "kubernetes-mcp"],
            "description": "DevOps orchestrator using multiple MCPs"
        },
        {
            "name": "infrastructure-specialist",
            "required_mcp_ids": ["terraform-mcp", "azure-mcp"],
            "description": "Infrastructure specialist using Terraform and Azure"
        },
        {
            "name": "platform-engineer",
            "required_mcp_ids": ["kubernetes-mcp", "gcp-mcp"],
            "description": "Platform engineer using K8s and GCP"
        }
    ]
