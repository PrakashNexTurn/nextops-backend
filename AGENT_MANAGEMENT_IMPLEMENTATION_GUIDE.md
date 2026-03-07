# Dynamic Agent Management System - Implementation Guide

## 🎯 Overview

This guide provides step-by-step instructions for implementing and using the Dynamic Agent Management System. This system allows you to create, configure, and manage agents without code changes by using REST APIs.

## 📦 What Was Delivered

### 1. Database Models
- **Agent** - Stores agent configurations with MCP and tool associations
- **AgentTemplate** - Pre-defined templates for common agent types

### 2. REST API Endpoints
```
POST   /agents                              - Create agent
GET    /agents                              - List agents
GET    /agents/{id}                         - Get agent
PUT    /agents/{id}                         - Update agent
DELETE /agents/{id}                         - Delete agent
POST   /agents/{id}/enable                  - Enable agent
POST   /agents/{id}/disable                 - Disable agent
POST   /agents/templates                    - Create template
GET    /agents/templates                    - List templates
GET    /agents/templates/{id}               - Get template
POST   /agents/templates/{id}/clone         - Clone template to agent
```

### 3. AgentFactory Service
- Loads agent configurations from database
- Resolves MCP IDs to actual MCP clients
- Creates Strands Agent instances
- Integrates memory hooks and state management

### 4. Updated Bedrock Entrypoint
- Uses AgentFactory to load agents dynamically
- No hardcoded agent functions
- Maintains memory integration
- Ready for production

### 5. Pre-built Templates
- terraform-foundation
- azure-foundation
- kubernetes-foundation
- servicenow-foundation
- github-foundation
- full-stack-foundation

## 🚀 Quick Start

### Step 1: Setup Templates

```bash
python agent_templates_setup.py setup
```

This creates standard templates in the database.

### Step 2: Create Agent from Template

```bash
curl -X POST http://localhost:8000/agents/templates/terraform-foundation/clone \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "my-terraform-agent",
    "description": "Custom Terraform agent"
  }'
```

### Step 3: Verify Agent

```bash
curl -X GET http://localhost:8000/agents
```

### Step 4: Agent is Ready!

On the next Bedrock invocation, the agent will automatically be loaded and available in the Swarm.

## 📋 Creating Custom Agents

### Manual Creation

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-agent",
    "description": "My custom agent",
    "system_prompt": "You are a specialized agent...",
    "agent_type": "custom",
    "capabilities": ["capability1", "capability2"],
    "mcp_ids": ["mcp-id-1", "mcp-id-2"],
    "tool_ids": ["tool-id-1", "tool-id-2"],
    "enabled": true,
    "parameters": {
      "timeout": 900,
      "max_retries": 3
    }
  }'
```

### Key Fields

- **name**: Unique agent identifier (required)
- **system_prompt**: Instructions for the agent (required)
- **agent_type**: Category (custom, terraform, azure, etc.)
- **capabilities**: List of what agent can do
- **mcp_ids**: MCP servers to use (auto-discovers tools)
- **tool_ids**: Direct tool references
- **enabled**: Whether agent is active
- **parameters**: Custom agent-specific settings

## 🔧 Configuration Examples

### Terraform Agent

```json
{
  "name": "terraform-automation",
  "description": "Terraform infrastructure automation",
  "system_prompt": "You are a Terraform specialist...",
  "agent_type": "terraform",
  "capabilities": ["plan", "apply", "destroy", "validate"],
  "mcp_ids": ["terraform-mcp", "github-mcp"],
  "enabled": true
}
```

### Multi-MCP Agent

```json
{
  "name": "full-stack-agent",
  "description": "End-to-end automation",
  "system_prompt": "You coordinate infrastructure, deployments, and tickets...",
  "agent_type": "custom",
  "capabilities": ["infrastructure", "deployment", "monitoring", "orchestration"],
  "mcp_ids": [
    "terraform-mcp",
    "azure-mcp",
    "kubernetes-mcp",
    "github-mcp",
    "servicenow-mcp"
  ],
  "enabled": true
}
```

### Specialized Agent

```json
{
  "name": "compliance-checker",
  "description": "Security and compliance verification",
  "system_prompt": "You verify security and compliance requirements...",
  "agent_type": "custom",
  "tool_ids": ["policy-checker", "audit-logger", "compliance-reporter"],
  "enabled": true,
  "parameters": {
    "strict_mode": true,
    "fail_on_warnings": true
  }
}
```

## 🔄 Agent Lifecycle

### 1. Create
```bash
POST /agents
```
Agent is stored in database, not yet active.

### 2. Enable (Optional)
```bash
POST /agents/{id}/enable
```
Agent is marked as enabled.

### 3. Load
On next Bedrock invocation, AgentFactory loads all enabled agents.

### 4. Execute
Agent participates in Swarm alongside other agents.

### 5. Update (Anytime)
```bash
PUT /agents/{id}
```
Changes take effect on next Bedrock invocation.

### 6. Disable
```bash
POST /agents/{id}/disable
```
Agent won't be loaded in future invocations.

### 7. Delete
```bash
DELETE /agents/{id}
```
Agent is permanently removed.

## 🎨 Agent Templates System

### Why Templates?

- Quick starting point for common patterns
- Consistent system prompts across similar agents
- Easy customization without writing from scratch
- Shareable best practices

### Using Templates

List available templates:
```bash
curl -X GET http://localhost:8000/agents/templates
```

Clone a template:
```bash
curl -X POST http://localhost:8000/agents/templates/{template_id}/clone \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "my-agent"}'
```

Create custom template:
```bash
curl -X POST http://localhost:8000/agents/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-template",
    "category": "custom",
    "description": "My template",
    "system_prompt_template": "Template system prompt...",
    "default_capabilities": ["cap1", "cap2"],
    "default_mcp_ids": ["mcp1", "mcp2"],
    "is_public": true
  }'
```

## 🔌 MCP Integration

### Automatic Tool Discovery

When you add MCP IDs to an agent, tools are automatically discovered:

1. Agent specifies `mcp_ids`
2. AgentFactory retrieves MCP configuration
3. All tools from MCP are automatically added
4. Agent has immediate access to tools

### Example

```json
{
  "name": "github-agent",
  "mcp_ids": ["github-mcp"]
}
```

This automatically adds all GitHub MCP tools without having to list them individually.

### Multiple MCPs

```json
{
  "name": "full-devops-agent",
  "mcp_ids": [
    "terraform-mcp",    // Gets all Terraform tools
    "github-mcp",       // Gets all GitHub tools
    "azure-mcp"         // Gets all Azure tools
  ]
}
```

Agent has 50+ tools available immediately!

## 💾 Database Schema

### agents table

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    agent_type VARCHAR(50),
    capabilities JSON,
    mcp_ids JSON,
    tool_ids JSON,
    enabled BOOLEAN DEFAULT TRUE,
    parameters JSON,
    tags JSON,
    created_at DATETIME,
    updated_at DATETIME,
    created_by VARCHAR(255)
);
```

### agent_templates table

```sql
CREATE TABLE agent_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(50),
    description TEXT,
    system_prompt_template TEXT,
    default_capabilities JSON,
    default_mcp_ids JSON,
    default_tool_ids JSON,
    default_parameters JSON,
    is_public BOOLEAN,
    version VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME
);
```

## 🔗 Integration with Bedrock

### Before (Hardcoded)

```python
# main.py - Had to hardcode every agent
from agents.terraform_agent import create_terraform_agent
from agents.azure_agent import create_azure_agent
# ... etc

agents = [
    create_terraform_agent(...),
    create_azure_agent(...),
    # ... manually create each agent
]

swarm = Swarm(agents)
```

### After (Dynamic)

```python
# bedrock_dynamic_entrypoint.py
from app.services.agent_factory import AgentFactory

factory = AgentFactory(db, memory_client)
agents = await factory.create_agents_from_database(
    actor_id=actor_id,
    session_id=session_id,
    enabled_only=True,
    hooks=[memory_hook]
)

swarm = Swarm(agents)  # All agents loaded!
```

NO CODE CHANGES NEEDED FOR NEW AGENTS!

## 🧪 Testing

### List All Agents

```bash
curl -X GET http://localhost:8000/agents
```

### Get Specific Agent

```bash
curl -X GET http://localhost:8000/agents/{agent_id}
```

### Create Test Agent

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-agent",
    "system_prompt": "Test agent",
    "agent_type": "custom",
    "enabled": true
  }'
```

### Update Agent

```bash
curl -X PUT http://localhost:8000/agents/{agent_id} \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "Updated system prompt"
  }'
```

### Delete Agent

```bash
curl -X DELETE http://localhost:8000/agents/{agent_id}
```

## 📊 Monitoring

### Check Agent Status

```bash
# List enabled agents only
curl -X GET "http://localhost:8000/agents?enabled_only=true"

# Filter by type
curl -X GET "http://localhost:8000/agents?agent_type=terraform"
```

### Monitor Agent Creation

Watch the logs when agents are created:
```
🔨 Creating agent: terraform-automation (ID: xxxxx)
✅ Resolved 25 tools for agent terraform-automation
✅ Agent created: terraform-automation
```

## 🔐 Security Considerations

1. **Agent Configuration** - Stored securely in database
2. **MCP Credentials** - Handled via auth headers, not exposed
3. **Agent State** - Includes actor_id for access control
4. **Memory Scoping** - Limited to actor_id and session_id
5. **API Authentication** - Can be added to REST endpoints

## 🚨 Troubleshooting

### Agent Not Loading

Check:
1. Is `enabled=true`?
2. Is agent in database?
3. Are MCP IDs valid?
4. Check factory logs

### Tools Not Available

Check:
1. MCP IDs are correct
2. MCPs are registered
3. MCPs have tools available
4. Check MCP client initialization

### Memory Not Working

Check:
1. MEMORY_ID environment variable set
2. Memory client configured
3. actor_id and session_id in payload
4. Memory service connection

## 📈 Performance Tips

1. **Use enabled_only=true** when loading agents
2. **Cache factory instance** across invocations
3. **Parallel MCP loading** happens automatically
4. **Memory loading** optimized for session tracking

## 🔄 Migration from Hardcoded

### Phase 1: Parallel (Recommended)

Keep hardcoded agents working, add new agents via API.

### Phase 2: Gradual Migration

Move hardcoded agents to database one by one.

### Phase 3: Full Dynamic

All agents in database, no hardcoded logic.

## 📚 Files Created/Modified

### Created
- `app/models/agent.py` - Agent models
- `app/schemas/agent_schema.py` - Pydantic schemas
- `app/services/agent_factory.py` - Dynamic agent creation
- `app/api/agents.py` - REST API endpoints
- `bedrock_dynamic_entrypoint.py` - Updated entrypoint
- `agent_templates_setup.py` - Template setup script

### Modified
- Database migrations (agent tables)
- FastAPI app registration (agents router)

## ✅ Validation Checklist

- [ ] Database tables created
- [ ] Templates setup: `python agent_templates_setup.py setup`
- [ ] Can create agent: `POST /agents`
- [ ] Can list agents: `GET /agents`
- [ ] Can enable/disable agents
- [ ] Agents load in Bedrock invocation
- [ ] Memory integration works
- [ ] MCPs auto-discovered for agents

## 🎓 Learning Path

1. Read this guide
2. Setup templates
3. Create agent via API
4. Verify in database
5. Invoke Bedrock and check logs
6. Update agent configuration
7. Try cloning templates
8. Create custom templates

## 🆘 Support

For issues:

1. Check logs for errors
2. Verify database connections
3. Confirm MCP configurations
4. Check API responses for details
5. Review troubleshooting section

## 🎉 You're Ready!

The system is now ready to use. Start creating agents via the REST API!

```bash
# Create your first agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-first-agent",
    "description": "My first dynamically created agent",
    "system_prompt": "You are a helpful automation agent",
    "enabled": true
  }'
```

That's it! Your agent will be ready on the next Bedrock invocation! 🚀
