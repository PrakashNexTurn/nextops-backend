"""
Bedrock Entrypoint - Selective MCP Loading Integration Example

This file demonstrates how to integrate the SelectiveMCPLoader into
the existing bedrock_agentcore_entrypoint.py to load only required MCPs.

BEFORE:
    - All 7 MCPs loaded for every invocation
    - Each agent receives all MCP clients
    - Slow initialization
    - Wasted memory

AFTER:
    - Only required MCPs loaded based on agent configuration
    - Each agent receives only its needed MCPs
    - Fast initialization
    - Memory efficient
"""

import os
import asyncio
import logging
from typing import List, Dict, Any

# New imports
from app.services.selective_mcp_loader import (
    SelectiveMCPLoader,
    create_agent_configs_with_mcp_requirements
)

# Existing imports (kept for reference)
# from bedrock_agentcore.runtime import BedrockAgentCoreApp
# from agents.servicenow_agent import create_servicenow_agent
# from agents.azure_agent import create_azure_agent
# etc.

logger = logging.getLogger(__name__)


class SelectiveMCPInitializer:
    """
    Manages selective MCP initialization for Bedrock agents.
    
    This class encapsulates the logic for analyzing agent requirements,
    loading only needed MCPs, and distributing them to agents.
    """
    
    def __init__(self):
        self.loader = SelectiveMCPLoader()
        self.mcp_clients = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize_mcps(
        self,
        agent_configs: List[Dict[str, Any]],
        mcp_factory: Any
    ) -> Dict[str, Any]:
        """
        Initialize only required MCPs based on agent configs.
        
        Args:
            agent_configs: Agent configurations with required_mcp_ids
            mcp_factory: Factory with MCP creation methods
            
        Returns:
            Dictionary mapping MCP IDs to loaded clients
        """
        self.logger.info("🚀 Starting selective MCP initialization...")
        
        # Step 1: Analyze requirements
        self.logger.info("📊 Analyzing agent MCP requirements...")
        required_mcps = self.loader.analyze_requirements(agent_configs)
        
        if not required_mcps:
            self.logger.warning("⚠️ No MCPs required by any agent!")
            return {}
        
        self.logger.info(f"✅ Found {len(required_mcps)} required MCPs")
        
        # Step 2: Load selectively
        self.logger.info("🔄 Loading MCPs in parallel...")
        import time
        start_time = time.time()
        
        self.mcp_clients = await self.loader.load_required_mcps(
            agent_configs, mcp_factory
        )
        
        elapsed = time.time() - start_time
        self.logger.info(
            f"⏱️ MCP initialization completed in {elapsed:.2f}s"
        )
        self.logger.info(f"✅ Loaded {len(self.mcp_clients)} MCP clients")
        
        return self.mcp_clients
    
    def get_agent_mcps(self, agent_name: str, agent_configs: List[Dict]) -> List[Any]:
        """Get MCPs for a specific agent."""
        return self.loader.get_agent_mcps(agent_name, agent_configs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded MCPs."""
        return self.loader.get_mcp_stats()


# ============================================================================
# INTEGRATION EXAMPLE: How to update bedrock_agentcore_entrypoint.py
# ============================================================================

"""
BEFORE (hardcoded, loads all 7 MCPs):

@app.async_task
async def run_swarm_in_background(payload, context):
    # ... existing code ...
    
    # Load ALL MCPs in parallel
    servicenow_task = asyncio.create_task(get_servicenow_mcp())
    azure_task = asyncio.create_task(get_azure_mcp())
    kubernetes_task = asyncio.create_task(get_kubernetes_mcp())
    terraform_task = asyncio.create_task(get_terraform_mcp())
    github_task = asyncio.create_task(get_github_http_mcp_client())
    gcp_task = asyncio.create_task(get_gcp_mcp())
    postgres_task = asyncio.create_task(get_postgres_mcp())
    
    servicenow_mcp, azure_mcp, kubernetes_mcp, terraform_mcp, \
    github_mcp, gcp_mcp, postgres_mcp = await asyncio.gather(
        servicenow_task, azure_task, kubernetes_task, terraform_task,
        github_task, gcp_task, postgres_task
    )
    
    # Every agent gets ALL MCPs
    servicenow_agent = create_servicenow_agent(
        mcp_tools=[servicenow_mcp, azure_mcp, kubernetes_mcp, terraform_mcp,
                   github_mcp, gcp_mcp, postgres_mcp],
        state={"actor_id": actor_id, "session_id": session_id}
    )
    # ... rest of agents with same ALL MCPs ...


AFTER (selective, loads only required MCPs):

@app.async_task
async def run_swarm_in_background(payload, context):
    # ... existing code ...
    
    # Define agent MCP requirements
    agent_configs = create_agent_configs_with_mcp_requirements()
    
    # Initialize selective MCP loader
    mcp_initializer = SelectiveMCPInitializer()
    await mcp_initializer.initialize_mcps(agent_configs, mcp_factory)
    
    # Create agents with ONLY their required MCPs
    servicenow_agent = create_servicenow_agent(
        mcp_tools=mcp_initializer.get_agent_mcps("servicenow", agent_configs),
        state={"actor_id": actor_id, "session_id": session_id}
    )
    
    azure_agent = create_azure_agent(
        mcp_tools=mcp_initializer.get_agent_mcps("azure", agent_configs),
        state={"actor_id": actor_id, "session_id": session_id}
    )
    
    kubernetes_agent = create_kubernetes_agent(
        mcp_tools=mcp_initializer.get_agent_mcps("kubernetes", agent_configs),
        state={"actor_id": actor_id, "session_id": session_id}
    )
    
    # ... rest of agents, each with only their required MCPs ...
    
    # Log statistics
    stats = mcp_initializer.get_stats()
    log.info(f"📊 MCP Loading Stats: {stats}")
"""


# ============================================================================
# PRACTICAL INTEGRATION CHECKLIST
# ============================================================================

INTEGRATION_CHECKLIST = """
STEP-BY-STEP INTEGRATION CHECKLIST
===================================

1. Import the new components:
   [ ] from app.services.selective_mcp_loader import (
           SelectiveMCPLoader,
           create_agent_configs_with_mcp_requirements
       )
   [ ] Create SelectiveMCPInitializer instance

2. Define agent MCP requirements:
   [ ] Get or create agent_configs with required_mcp_ids
   [ ] Verify each agent has a required_mcp_ids list
   [ ] Example:
       {
           "name": "servicenow",
           "required_mcp_ids": ["servicenow-mcp"],
           "description": "ServiceNow agent"
       }

3. Replace MCP loading logic:
   [ ] Remove individual asyncio.create_task() calls
   [ ] Remove individual await calls
   [ ] Replace with: await mcp_initializer.initialize_mcps(...)

4. Update agent creation:
   [ ] For servicenow: mcp_tools=mcp_initializer.get_agent_mcps("servicenow", ...)
   [ ] For azure: mcp_tools=mcp_initializer.get_agent_mcps("azure", ...)
   [ ] For kubernetes: mcp_tools=mcp_initializer.get_agent_mcps("kubernetes", ...)
   [ ] For terraform: mcp_tools=mcp_initializer.get_agent_mcps("terraform", ...)
   [ ] For github: mcp_tools=mcp_initializer.get_agent_mcps("github", ...)
   [ ] For gcp: mcp_tools=mcp_initializer.get_agent_mcps("gcp", ...)
   [ ] For postgres: mcp_tools=mcp_initializer.get_agent_mcps("postgres", ...)

5. Add monitoring/logging:
   [ ] Log MCP initialization start
   [ ] Log MCP initialization completion
   [ ] Log MCP statistics: log.info(mcp_initializer.get_stats())

6. Test the changes:
   [ ] Run bedrock entrypoint with logging enabled
   [ ] Verify only required MCPs are loaded
   [ ] Check initialization time improvement
   [ ] Verify each agent receives correct MCPs
   [ ] Test with memory hooks enabled
   [ ] Test with all 7 agents

7. Measure performance:
   [ ] Record initialization time (before vs after)
   [ ] Monitor memory usage (before vs after)
   [ ] Check logs for MCP loading progression
   [ ] Verify no agents are missing MCPs

8. Deploy and monitor:
   [ ] Deploy to test environment
   [ ] Monitor for errors
   [ ] Verify agents work correctly
   [ ] Monitor resource usage
   [ ] Deploy to production
"""

print(INTEGRATION_CHECKLIST)


# ============================================================================
# CODE SNIPPET: Ready-to-use integration code
# ============================================================================

INTEGRATION_CODE_SNIPPET = """
# Add this to bedrock_agentcore_entrypoint.py

# ─────── NEW IMPORTS ─────────
from app.services.selective_mcp_loader import (
    SelectiveMCPLoader,
    create_agent_configs_with_mcp_requirements
)
from app.services.mcp_clients import MCPFactory  # Your MCP factory
# ────────────────────────────

@app.async_task
async def run_swarm_in_background(payload, context):
    \"\"\"Run the Swarm agents with selective MCP loading\"\"\"
    
    # Extract session info (existing code)
    actor_id = payload.get("actor_id") or payload.get("user_id") or 'default-user'
    session_id = payload.get("session_id") or getattr(context, 'session_id', None) or 'default'
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    
    log.info(f"🚀 Swarm invoked with session_id={session_id}, actor_id={actor_id}")
    
    try:
        # ─────── NEW: Define agent MCP requirements ─────────
        agent_configs = create_agent_configs_with_mcp_requirements()
        log.info(f"📋 Loaded {len(agent_configs)} agent configurations")
        # ────────────────────────────────────────────────────
        
        # ─────── NEW: Initialize selective MCP loader ─────────
        mcp_initializer = SelectiveMCPInitializer()
        mcp_factory = MCPFactory()  # Your MCP factory instance
        
        await mcp_initializer.initialize_mcps(agent_configs, mcp_factory)
        stats = mcp_initializer.get_stats()
        log.info(f"📊 MCP Loading Stats: {stats}")
        # ────────────────────────────────────────────────────
        
        # Initialize memory hook (existing code)
        memory_hook = None
        if MEMORY_ID:
            try:
                memory_client = MemoryClient(region_name=REGION)
                memory_hook = SwarmMemoryHook(memory_client, MEMORY_ID)
            except Exception as e:
                log.warning(f"Failed to initialize memory: {e}")
        
        # ─────── NEW: Create agents with selective MCPs ─────────
        log.info("🎫 Creating agents with selective MCPs...")
        
        # ServiceNow agent
        servicenow_agent = create_servicenow_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("servicenow", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        
        # Azure agent
        azure_agent = create_azure_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("azure", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        
        # Kubernetes agent
        kubernetes_agent = create_kubernetes_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("kubernetes", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        
        # Terraform agent
        terraform_agent = create_terraform_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("terraform", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        
        # GitHub agent
        github_agent = create_github_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("github", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        
        # GCP agent
        gcp_agent = create_gcp_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("gcp", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        
        # PostgreSQL agent
        postgres_agent = create_postgres_agent(
            mcp_tools=mcp_initializer.get_agent_mcps("postgres", agent_configs),
            state={"actor_id": actor_id, "session_id": session_id},
            hooks=[memory_hook] if memory_hook else None
        )
        # ────────────────────────────────────────────────────────
        
        # Create Swarm (existing code)
        swarm = Swarm([
            servicenow_agent,
            azure_agent,
            kubernetes_agent,
            terraform_agent,
            github_agent,
            gcp_agent,
            postgres_agent
        ])
        
        # Run swarm (existing code)
        log.info(f"🔄 Running swarm with user message...")
        response = await swarm.run(
            messages=user_message,
            actor_id=actor_id
        )
        
        log.info(f"✅ Swarm execution completed")
        return response
        
    except Exception as e:
        log.error(f"❌ Error in run_swarm_in_background: {e}", exc_info=True)
        raise
"""

print("\n" + "="*80)
print("READY-TO-USE INTEGRATION CODE")
print("="*80)
print(INTEGRATION_CODE_SNIPPET)
