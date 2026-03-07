"""
Dynamic Agent Management System - Comprehensive Documentation

This module provides the complete framework for creating, managing, and using
agents dynamically without code changes. Users can add agents via REST API,
configure them with MCPs and tools, and use them immediately in the Swarm.
"""

# ============================================================================
# OVERVIEW
# ============================================================================

"""
The Dynamic Agent Management System transforms the agent creation process from
hardcoded functions to a database-driven, API-configurable system.

BEFORE (Hardcoded):
- Each agent required a separate Python file (terraform_agent.py, azure_agent.py)
- Adding new agents required code changes and redeployment
- Limited to predefined agents
- Not scalable

AFTER (Dynamic):
- Define agents via REST API
- Add unlimited agents without code changes
- Configure MCPs, tools, and capabilities per agent
- Enable/disable agents dynamically
- Clone templates for quick setup
- Production-ready with full memory integration
"""

# ============================================================================
# QUICK START
# ============================================================================

"""
1. CREATE AN AGENT via REST API:

POST /agents
{
  "name": "terraform-agent",
  "description": "Handles Terraform infrastructure automation",
  "system_prompt": "You are a Terraform specialist...",
  "agent_type": "terraform",
  "capabilities": ["plan", "apply", "destroy"],
  "mcp_ids": ["terraform-mcp", "github-mcp"],
  "enabled": true
}

2. LOAD AGENTS IN BEDROCK ENTRYPOINT:

from app.services.agent_factory import AgentFactory

async def run_swarm_in_background(payload, context):
    factory = AgentFactory(db, memory_client)
    agents = await factory.create_agents_from_database(
        actor_id=actor_id,
        session_id=session_id,
        enabled_only=True,
        hooks=[memory_hook]
    )
    
    swarm = Swarm(agents)
    result = await swarm.invoke_async(user_message)

3. AGENTS ARE AUTOMATICALLY LOADED AND READY TO USE!
"""

# ============================================================================
# API ENDPOINTS
# ============================================================================

"""
AGENT MANAGEMENT:

POST   /agents                  - Create new agent
GET    /agents                  - List all agents
GET    /agents/{id}             - Get specific agent
PUT    /agents/{id}             - Update agent
DELETE /agents/{id}             - Delete agent
POST   /agents/{id}/enable      - Enable agent
POST   /agents/{id}/disable     - Disable agent

AGENT TEMPLATES:

POST   /agents/templates                      - Create template
GET    /agents/templates                      - List templates
GET    /agents/templates/{id}                 - Get template
POST   /agents/templates/{id}/clone           - Clone to new agent

MCP ASSOCIATIONS:

POST   /agents/{id}/mcps/{mcp_id}             - Add MCP to agent
DELETE /agents/{id}/mcps/{mcp_id}             - Remove MCP from agent
GET    /agents/{id}/mcps                      - List agent MCPs
"""

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

"""
TABLE: agents
- id: UUID (primary key)
- name: String (unique)
- description: Text (optional)
- system_prompt: Text (required)
- agent_type: String (custom, terraform, azure, etc.)
- capabilities: JSON (list of capabilities)
- mcp_ids: JSON (list of MCP server IDs)
- tool_ids: JSON (list of direct tool IDs)
- enabled: Boolean (default: true)
- parameters: JSON (custom agent-specific parameters)
- tags: JSON (metadata)
- created_at: DateTime
- updated_at: DateTime
- created_by: String (optional)

TABLE: agent_templates
- id: UUID (primary key)
- name: String (unique)
- description: Text
- category: String (terraform, azure, kubernetes, etc.)
- system_prompt_template: Text (template for system prompt)
- default_capabilities: JSON
- default_mcp_ids: JSON
- default_tool_ids: JSON
- default_parameters: JSON
- is_public: Boolean
- version: String
- created_at: DateTime
- updated_at: DateTime
"""

# ============================================================================
# AGENT FACTORY SERVICE
# ============================================================================

"""
The AgentFactory service handles:

1. Loading agent configurations from database
2. Resolving MCP IDs to actual MCP clients
3. Resolving tool IDs to tool instances
4. Creating Strands Agent instances with proper configuration
5. Integrating memory hooks and state management

Usage:

from app.services.agent_factory import AgentFactory
from app.db.database import get_db
from bedrock_agentcore.memory import MemoryClient

db = next(get_db())
memory_client = MemoryClient(region_name="us-east-1")

factory = AgentFactory(db, memory_client)

# Create all enabled agents
agents = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    enabled_only=True,
    hooks=[memory_hook]
)

# Use agents in Swarm
swarm = Swarm(agents)
result = await swarm.invoke_async("Your message here")
"""

# ============================================================================
# AGENT CONFIGURATION EXAMPLES
# ============================================================================

"""
EXAMPLE 1: Terraform Agent

POST /agents
{
  "name": "terraform-agent",
  "description": "Infrastructure automation with Terraform and GitHub",
  "system_prompt": "You are a DevOps/Infrastructure specialist...",
  "agent_type": "terraform",
  "capabilities": ["plan", "apply", "destroy", "validate"],
  "mcp_ids": ["terraform-mcp", "github-mcp"],
  "enabled": true,
  "parameters": {
    "timeout": 900,
    "max_retries": 3
  }
}

EXAMPLE 2: Azure Agent

POST /agents
{
  "name": "azure-agent",
  "description": "Azure cloud infrastructure management",
  "system_prompt": "You are an Azure cloud specialist...",
  "agent_type": "azure",
  "capabilities": ["create", "update", "delete", "monitor"],
  "mcp_ids": ["azure-mcp"],
  "enabled": true
}

EXAMPLE 3: Multi-MCP Agent

POST /agents
{
  "name": "full-stack-agent",
  "description": "Handles infrastructure, code, and deployments",
  "system_prompt": "You are a full-stack automation specialist...",
  "agent_type": "custom",
  "capabilities": [
    "infrastructure", "deployment", "monitoring", "code-review"
  ],
  "mcp_ids": [
    "terraform-mcp",
    "azure-mcp",
    "kubernetes-mcp",
    "github-mcp",
    "docker-mcp"
  ],
  "enabled": true
}

EXAMPLE 4: Custom Tool Agent

POST /agents
{
  "name": "custom-integration-agent",
  "description": "Works with custom internal tools",
  "system_prompt": "You are a custom integration specialist...",
  "agent_type": "custom",
  "tool_ids": [
    "internal-api-tool",
    "custom-metric-tool",
    "notification-tool"
  ],
  "enabled": true
}
"""

# ============================================================================
# MEMORY INTEGRATION
# ============================================================================

"""
Agents automatically integrate with the memory system:

1. Agent state includes actor_id and session_id for conversation tracking
2. Memory hooks load previous conversation history at agent start
3. Memory hooks store new messages during agent execution
4. Each agent maintains separate conversation history

Memory is preserved across:
- Multiple agent invocations in same session
- Agent enable/disable cycles
- Database updates to agent configuration

The conversation context is automatically:
- Loaded before agent execution
- Formatted for the agent's understanding
- Appended to the system prompt
- Stored after each message
"""

# ============================================================================
# TEMPLATE SYSTEM
# ============================================================================

"""
Pre-defined templates provide quick starting points:

POST /agents/templates
{
  "name": "terraform-foundation",
  "category": "terraform",
  "description": "Foundation template for Terraform agents",
  "system_prompt_template": "You are a Terraform specialist...",
  "default_capabilities": ["plan", "apply", "destroy"],
  "default_mcp_ids": ["terraform-mcp", "github-mcp"],
  "is_public": true,
  "version": "1.0.0"
}

Clone template to create new agent:

POST /agents/templates/{template_id}/clone?agent_name=my-terraform-agent

Result: New agent with template settings, ready to customize
"""

# ============================================================================
# WORKFLOW: ADDING NEW AGENTS
# ============================================================================

"""
Step 1: Create agent via API

curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-agent",
    "description": "My new agent",
    "system_prompt": "You are...",
    "agent_type": "custom",
    "mcp_ids": ["mcp-id-1", "mcp-id-2"],
    "enabled": true
  }'

Step 2: Agent is stored in database

Step 3: On next Swarm invocation, AgentFactory loads all enabled agents

Step 4: Agent is created with resolved tools and memory hooks

Step 5: Agent is available in the Swarm alongside all other agents

Step 6: Update agent configuration anytime:

curl -X PUT http://localhost:8000/agents/{agent_id} \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "Updated prompt...",
    "enabled": true
  }'

Changes take effect on next Swarm invocation!
"""

# ============================================================================
# BEDROCK ENTRYPOINT INTEGRATION
# ============================================================================

"""
Updated entrypoint uses dynamic agents:

import asyncio
from app.services.agent_factory import AgentFactory
from app.db.database import get_db
from bedrock_agentcore.memory import MemoryClient
from strands.multiagent import Swarm

@app.async_task
async def run_swarm_in_background(payload, context):
    # Setup
    db = next(get_db())
    memory_client = MemoryClient(region_name=REGION)
    memory_hook = SwarmMemoryHook(memory_client, MEMORY_ID)
    
    # Create agents dynamically
    factory = AgentFactory(db, memory_client)
    agents = await factory.create_agents_from_database(
        actor_id=actor_id,
        session_id=session_id,
        enabled_only=True,
        hooks=[memory_hook]
    )
    
    # Create swarm with dynamic agents
    swarm = Swarm(agents)
    result = await swarm.invoke_async(user_message)
    
    return result

NO CODE CHANGES NEEDED TO ADD NEW AGENTS!
Just create them via REST API!
"""

# ============================================================================
# MIGRATION PATH
# ============================================================================

"""
PHASE 1: Parallel Running (Can use both)
- Keep hardcoded agents in main.py
- Add new agents via REST API
- Factory loads both

PHASE 2: Gradual Migration
- Move hardcoded agents to database
- Use templates for common patterns
- Update main.py to use AgentFactory

PHASE 3: Full Dynamic (Recommended)
- All agents in database
- main.py uses AgentFactory only
- No hardcoded agent logic

Benefits:
- Zero downtime migration
- Can rollback at any phase
- Existing agents keep working
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Q: Agent not loading?
A: Check if enabled=true in database
   Verify mcp_ids and tool_ids are valid UUIDs
   Check factory logs for resolution errors

Q: Agent not using my MCPs?
A: Verify mcp_ids are set correctly
   Check if MCP servers are registered in database
   Verify MCP has tools available

Q: Memory not loading?
A: Ensure memory_client is configured
   Verify actor_id and session_id in payload
   Check memory service connection

Q: Want to add new agent?
A: POST /agents with configuration
   It's immediately available in next Swarm run!
"""

# ============================================================================
# PERFORMANCE NOTES
# ============================================================================

"""
- Agent loading: Parallel MCP client initialization
- Memory loading: Cached for agent lifetime
- Tool resolution: Cached per factory instance
- Swarm creation: Agents added dynamically at runtime
- State management: Maintained per agent in conversation
"""

# ============================================================================
# SECURITY
# ============================================================================

"""
- Agent configuration stored securely in database
- MCP credentials handled via authentication headers
- Agent state includes actor_id for access control
- Memory access scoped to actor_id and session_id
- API endpoints can require authentication
"""
