# Agent Creation API Examples

This document provides curl and Python examples for using the new agent creation API with MCP support.

## Prerequisites

- Running nextops-backend API server at `http://localhost:8000`
- Valid MCP IDs and Tool IDs from your system

## Quick Start

### 1. Create agent with MCPs (simplest way)

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Agent",
    "description": "For production automation",
    "system_prompt": "You are a production automation specialist",
    "mcp_ids": ["550e8400-e29b-41d4-a716-446655440000"]
  }'
```

### 2. Create agent with tools and MCPs (mixed)

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hybrid Agent",
    "description": "Uses MCPs and custom tools",
    "system_prompt": "You have mixed capabilities",
    "mcp_ids": ["550e8400-e29b-41d4-a716-446655440000"],
    "tool_ids": ["770e8400-e29b-41d4-a716-446655440002"]
  }'
```

### 3. Create agent with direct tools only

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minimal Agent",
    "description": "Limited tool set",
    "system_prompt": "You have basic tools",
    "tool_ids": [
      "770e8400-e29b-41d4-a716-446655440002",
      "880e8400-e29b-41d4-a716-446655440003"
    ]
  }'
```

## Detailed Examples

### Example: GitHub + Docker Integration Agent

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Pipeline Agent",
    "description": "Manages GitHub and Docker operations",
    "system_prompt": "You are a CI/CD specialist. Use GitHub to manage repositories and Docker to manage containers.",
    "mcp_ids": [
      "github-mcp-uuid-here",
      "docker-mcp-uuid-here"
    ],
    "tool_ids": [
      "monitoring-tool-uuid",
      "notification-tool-uuid"
    ],
    "tags": {
      "environment": "production",
      "team": "devops",
      "tier": "premium"
    }
  }'
```

### Example: Kubernetes Operations Agent

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "K8s Operations Agent",
    "description": "Kubernetes cluster operations",
    "system_prompt": "You are a Kubernetes expert. Manage deployments, services, and configurations.",
    "mcp_ids": ["kubernetes-mcp-uuid"],
    "tags": {
      "specialty": "kubernetes",
      "version": "1.28"
    }
  }'
```

## Python Examples

### Using requests library

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Create agent with MCPs
def create_agent_with_mcps(agent_name, mcp_ids):
    """Create an agent using MCP IDs."""
    
    payload = {
        "name": agent_name,
        "description": f"Agent using {len(mcp_ids)} MCPs",
        "system_prompt": "You are a versatile automation agent",
        "mcp_ids": mcp_ids
    }
    
    response = requests.post(
        f"{BASE_URL}/agents",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        agent = response.json()
        print(f"✅ Created agent: {agent['name']}")
        print(f"   ID: {agent['id']}")
        print(f"   Tools: {len(agent['tool_ids'])}")
        print(f"   MCPs: {len(agent['mcp_ids'])}")
        return agent
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None


# Create agent with mixed tools and MCPs
def create_agent_mixed(agent_name, mcp_ids, tool_ids):
    """Create an agent with both MCP and direct tool IDs."""
    
    payload = {
        "name": agent_name,
        "description": "Mixed capability agent",
        "system_prompt": "You have diverse tools and capabilities",
        "mcp_ids": mcp_ids,
        "tool_ids": tool_ids
    }
    
    response = requests.post(
        f"{BASE_URL}/agents",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        agent = response.json()
        print(f"✅ Created agent: {agent['name']}")
        print(f"   Total tools: {len(agent['tool_ids'])}")
        print(f"   From MCPs: {len(agent['mcp_ids'])}")
        return agent
    else:
        print(f"❌ Error creating agent: {response.json()}")
        return None


# List all agents with their MCPs and tools
def list_agents_with_details():
    """List all agents showing their MCPs and tools."""
    
    response = requests.get(f"{BASE_URL}/agents")
    
    if response.status_code == 200:
        agents = response.json()
        print(f"\n📋 Total agents: {len(agents)}\n")
        
        for agent in agents:
            print(f"Agent: {agent['name']}")
            print(f"  ID: {agent['id']}")
            print(f"  Tools: {len(agent['tool_ids'])}")
            print(f"  MCPs: {len(agent['mcp_ids'])}")
            if agent['mcp_ids']:
                print(f"  MCP IDs: {', '.join(str(m) for m in agent['mcp_ids'][:3])}")
            print()
    else:
        print(f"❌ Error: {response.status_code}")


# Get a specific agent with full details
def get_agent_details(agent_id):
    """Get full details of a specific agent."""
    
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    
    if response.status_code == 200:
        agent = response.json()
        print(f"\n🤖 Agent: {agent['name']}")
        print(f"Description: {agent['description']}")
        print(f"Created: {agent['created_at']}")
        print(f"\nTools: {len(agent['tool_ids'])}")
        for i, tool_id in enumerate(agent['tool_ids'][:5], 1):
            print(f"  {i}. {tool_id}")
        if len(agent['tool_ids']) > 5:
            print(f"  ... and {len(agent['tool_ids']) - 5} more")
        
        print(f"\nMCPs: {len(agent['mcp_ids'])}")
        for i, mcp_id in enumerate(agent['mcp_ids'], 1):
            print(f"  {i}. {mcp_id}")
    else:
        print(f"❌ Error: {response.status_code}")


# Update agent MCPs
def update_agent_mcps(agent_id, new_mcp_ids):
    """Update an agent's MCP associations."""
    
    payload = {
        "mcp_ids": new_mcp_ids
    }
    
    response = requests.put(
        f"{BASE_URL}/agents/{agent_id}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        agent = response.json()
        print(f"✅ Updated agent MCPs")
        print(f"   Now has {len(agent['mcp_ids'])} MCPs")
        print(f"   Total tools: {len(agent['tool_ids'])}")
    else:
        print(f"❌ Error: {response.json()}")


# Add an MCP to existing agent
def add_mcp_to_agent(agent_id, mcp_id):
    """Add an MCP to an existing agent."""
    
    response = requests.post(
        f"{BASE_URL}/agents/{agent_id}/mcps/{mcp_id}",
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Added MCP to agent")
        print(f"   {result['message']}")
    else:
        print(f"❌ Error: {response.json()}")


# Remove an MCP from agent
def remove_mcp_from_agent(agent_id, mcp_id):
    """Remove an MCP from an agent."""
    
    response = requests.delete(
        f"{BASE_URL}/agents/{agent_id}/mcps/{mcp_id}"
    )
    
    if response.status_code == 204:
        print(f"✅ Removed MCP from agent")
    else:
        print(f"❌ Error: {response.json()}")


# Usage examples
if __name__ == "__main__":
    # Example 1: Create agent with MCPs
    print("=" * 50)
    print("Example 1: Create agent with MCPs")
    print("=" * 50)
    mcp_ids = [
        "550e8400-e29b-41d4-a716-446655440000",
        "660e8400-e29b-41d4-a716-446655440001"
    ]
    agent1 = create_agent_with_mcps("DevOps Agent", mcp_ids)
    
    # Example 2: Create agent with mixed tools
    print("\n" + "=" * 50)
    print("Example 2: Create agent with mixed tools and MCPs")
    print("=" * 50)
    tool_ids = ["770e8400-e29b-41d4-a716-446655440002"]
    agent2 = create_agent_mixed("Hybrid Agent", mcp_ids, tool_ids)
    
    # Example 3: List all agents
    print("\n" + "=" * 50)
    print("Example 3: List all agents")
    print("=" * 50)
    list_agents_with_details()
    
    # Example 4: Get agent details (if we have an ID)
    if agent1:
        print("\n" + "=" * 50)
        print("Example 4: Get agent details")
        print("=" * 50)
        get_agent_details(agent1['id'])
```

### Advanced: Batch create multiple agents

```python
def batch_create_agents(agent_configs):
    """Create multiple agents from a list of configurations."""
    
    results = []
    
    for config in agent_configs:
        try:
            response = requests.post(
                f"{BASE_URL}/agents",
                json=config,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                agent = response.json()
                results.append({
                    "status": "success",
                    "name": agent["name"],
                    "id": agent["id"]
                })
                print(f"✅ {agent['name']}")
            else:
                results.append({
                    "status": "error",
                    "name": config["name"],
                    "error": response.json().get("detail", "Unknown error")
                })
                print(f"❌ {config['name']}: {response.json().get('detail')}")
        except Exception as e:
            results.append({
                "status": "error",
                "name": config["name"],
                "error": str(e)
            })
            print(f"❌ {config['name']}: {str(e)}")
    
    return results


# Configuration for multiple agents
agent_configs = [
    {
        "name": "GitHub Agent",
        "description": "GitHub automation",
        "system_prompt": "GitHub specialist",
        "mcp_ids": ["github-mcp-id"]
    },
    {
        "name": "Docker Agent",
        "description": "Docker operations",
        "system_prompt": "Docker specialist",
        "mcp_ids": ["docker-mcp-id"]
    },
    {
        "name": "DevOps Agent",
        "description": "Full DevOps capabilities",
        "system_prompt": "DevOps expert",
        "mcp_ids": ["github-mcp-id", "docker-mcp-id", "kubernetes-mcp-id"]
    }
]

# Batch create
results = batch_create_agents(agent_configs)

# Print summary
print("\n" + "=" * 50)
print("Batch Creation Summary")
print("=" * 50)
successful = sum(1 for r in results if r["status"] == "success")
failed = sum(1 for r in results if r["status"] == "error")
print(f"✅ Successful: {successful}")
print(f"❌ Failed: {failed}")
```

## CLI Tool

Here's a simple CLI tool for managing agents:

```python
#!/usr/bin/env python3
import click
import requests
import json

BASE_URL = "http://localhost:8000"

@click.group()
def cli():
    """Agent management CLI"""
    pass

@cli.command()
@click.option('--name', required=True, help='Agent name')
@click.option('--mcp', multiple=True, help='MCP IDs')
@click.option('--tool', multiple=True, help='Tool IDs')
def create(name, mcp, tool):
    """Create a new agent"""
    payload = {
        "name": name,
        "description": f"Agent {name}",
        "system_prompt": "You are a helpful automation agent",
        "mcp_ids": list(mcp),
        "tool_ids": list(tool)
    }
    
    response = requests.post(
        f"{BASE_URL}/agents",
        json=payload
    )
    
    if response.status_code == 201:
        agent = response.json()
        click.echo(click.style("✅ Agent created!", fg="green"))
        click.echo(f"ID: {agent['id']}")
        click.echo(f"Tools: {len(agent['tool_ids'])}")
        click.echo(f"MCPs: {len(agent['mcp_ids'])}")
    else:
        click.echo(click.style(f"❌ Error: {response.json()['detail']}", fg="red"))

@cli.command()
def list():
    """List all agents"""
    response = requests.get(f"{BASE_URL}/agents")
    agents = response.json()
    
    click.echo(f"\n{'Name':<30} {'Tools':<8} {'MCPs':<8}")
    click.echo("-" * 50)
    for agent in agents:
        click.echo(f"{agent['name']:<30} {len(agent['tool_ids']):<8} {len(agent['mcp_ids']):<8}")

if __name__ == '__main__':
    cli()
```

Usage:
```bash
python agent_cli.py create --name "My Agent" --mcp mcp-uuid-1 --mcp mcp-uuid-2
python agent_cli.py list
```

## Testing

### Curl test script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Get MCPs first
echo "Fetching MCPs..."
MCPS=$(curl -s $BASE_URL/mcps | jq -r '.[0].id')
echo "Using MCP: $MCPS"

# Create agent
echo "Creating agent..."
AGENT=$(curl -s -X POST $BASE_URL/agents \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Agent $(date +%s)\",
    \"description\": \"Test agent\",
    \"system_prompt\": \"Test\",
    \"mcp_ids\": [\"$MCPS\"]
  }")

AGENT_ID=$(echo $AGENT | jq -r '.id')
echo "Created agent: $AGENT_ID"

# Get agent details
echo "Getting agent details..."
curl -s $BASE_URL/agents/$AGENT_ID | jq .

# List MCPs for agent
echo "Listing MCPs..."
curl -s $BASE_URL/agents/$AGENT_ID/mcps | jq .
```

## Performance Considerations

- **MCP Resolution**: Resolving MCPs to tools is instant (database queries)
- **Tool Count**: Agents can have hundreds of tools without performance issues
- **MCP Addition**: Adding an MCP to an agent typically takes <100ms

## Troubleshooting

| Error | Solution |
|-------|----------|
| "MCP with ID X not found" | Verify the MCP ID is correct |
| "Tool with ID X not found" | Verify the tool ID is correct |
| "Agent with name already exists" | Use a unique agent name |
| "MCP already assigned" | MCP is already on this agent |
