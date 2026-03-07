# Agent Creation with Tool IDs and MCP IDs - Guide

## Overview

This guide explains how to create agents in the new intuitive way by specifying **MCP IDs** directly, instead of having to know and specify individual tool IDs.

## Problem Solved

**Before:** Users had to know which tools were inside each MCP and specify each tool ID individually
```json
{
  "name": "My Agent",
  "system_prompt": "...",
  "tools": ["tool-1", "tool-2", "tool-3", ...]  // How do I know all the tool IDs?
}
```

**After:** Users can simply specify which MCPs they want to use
```json
{
  "name": "My Agent",
  "system_prompt": "...",
  "mcp_ids": ["github-mcp-id", "docker-mcp-id"],  // Much simpler!
  "tool_ids": ["custom-tool-1"]  // Plus any specific tools
}
```

## Key Features

✅ **Automatic Tool Resolution** - Specify an MCP, get all its tools automatically  
✅ **Mixed Approach** - Combine direct tool IDs with MCP IDs  
✅ **Backward Compatible** - Old `tools` field still works  
✅ **MCP Tracking** - Know which MCPs are assigned to your agent  
✅ **Easy Updates** - Add/remove tools or MCPs anytime  

## Creating an Agent

### Example 1: Using only MCPs

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Automation Agent",
    "description": "Automates GitHub operations",
    "system_prompt": "You are a GitHub automation expert",
    "mcp_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "660e8400-e29b-41d4-a716-446655440001"
    ]
  }'
```

**Result:** The agent gets ALL tools from both MCPs automatically.

### Example 2: Using both MCPs and direct tool IDs

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Multi-Purpose Agent",
    "description": "Works with multiple services",
    "system_prompt": "You have access to many tools",
    "mcp_ids": [
      "550e8400-e29b-41d4-a716-446655440000"
    ],
    "tool_ids": [
      "770e8400-e29b-41d4-a716-446655440002",
      "880e8400-e29b-41d4-a716-446655440003"
    ]
  }'
```

**Result:** Agent gets all tools from the MCP + the 2 specific tools.

### Example 3: Only specific tools (no MCPs)

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Agent",
    "description": "Uses specific tools only",
    "system_prompt": "Limited capability agent",
    "tool_ids": [
      "770e8400-e29b-41d4-a716-446655440002",
      "880e8400-e29b-41d4-a716-446655440003"
    ]
  }'
```

**Result:** Agent gets only these 2 specific tools.

## Getting Agent Details

### Get a specific agent

```bash
curl http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000
```

**Response includes:**
- `tool_ids`: All resolved tools (direct + from MCPs)
- `mcp_ids`: The MCPs assigned to the agent

### List all agents

```bash
curl http://localhost:8000/agents
```

Each agent in the list shows its `tool_ids` and `mcp_ids`.

## Managing MCPs on Agents

### Add an MCP to an agent

```bash
curl -X POST http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000/mcps/660e8400-e29b-41d4-a716-446655440001 \
  -H "Content-Type: application/json"
```

**Result:** 
- MCP is added to the agent
- All tools from that MCP are automatically added
- Response shows how many tools were added

### Remove an MCP from an agent

```bash
curl -X DELETE http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000/mcps/660e8400-e29b-41d4-a716-446655440001
```

**Result:** 
- MCP is removed from the agent
- Tools from that MCP are removed (if not from another source)

### List MCPs for an agent

```bash
curl http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000/mcps
```

**Response:** List of all MCPs assigned to this agent.

## Managing Tools on Agents

### Add a tool to an agent

```bash
curl -X POST http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000/tools/770e8400-e29b-41d4-a716-446655440002 \
  -H "Content-Type: application/json"
```

### Remove a tool from an agent

```bash
curl -X DELETE http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000/tools/770e8400-e29b-41d4-a716-446655440002
```

## Updating an Agent

### Update with new MCPs and tools

```bash
curl -X PUT http://localhost:8000/agents/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "mcp_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "991e8400-e29b-41d4-a716-446655440004"
    ],
    "tool_ids": [
      "770e8400-e29b-41d4-a716-446655440002"
    ]
  }'
```

**Result:** Agent's MCPs and tools are completely replaced with the new ones.

## Understanding Tool Resolution

Here's how the system resolves MCPs to tools:

```
User creates agent with:
  mcp_ids: [github-mcp, docker-mcp]
  tool_ids: [custom-tool-1]
       ↓
System resolves:
  github-mcp → [tool-a, tool-b, tool-c]
  docker-mcp → [tool-d, tool-e]
       ↓
Agent gets combined tools:
  [tool-a, tool-b, tool-c, tool-d, tool-e, custom-tool-1]
```

## Backward Compatibility

The old `tools` field still works:

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Legacy Agent",
    "system_prompt": "...",
    "tools": ["tool-1", "tool-2"]  // Still works!
  }'
```

This is equivalent to `"tool_ids": ["tool-1", "tool-2"]`.

## Error Handling

### Invalid MCP ID

```json
{
  "detail": "MCP with ID invalid-uuid not found"
}
```

### MCP already assigned

```json
{
  "detail": "MCP already assigned to agent"
}
```

### Tool not found

```json
{
  "detail": "Tool with ID invalid-uuid not found"
}
```

## Response Examples

### Successful agent creation

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "GitHub Agent",
  "description": "Works with GitHub",
  "system_prompt": "You are a GitHub expert",
  "tags": {},
  "created_at": "2026-03-07T10:05:17.123456",
  "tool_ids": [
    "770e8400-e29b-41d4-a716-446655440002",
    "880e8400-e29b-41d4-a716-446655440003",
    "990e8400-e29b-41d4-a716-446655440004"
  ],
  "mcp_ids": [
    "660e8400-e29b-41d4-a716-446655440001"
  ]
}
```

## Best Practices

1. **Use MCPs when possible** - Simpler and more maintainable
2. **Keep tool_ids for special cases** - Custom or non-MCP tools
3. **Update instead of recreate** - Use PUT to change agent tools
4. **Verify MCP exists** - Check available MCPs before assigning
5. **Monitor tool count** - Ensure agent doesn't have too many tools

## Summary

| Scenario | Use |
|----------|-----|
| All tools from an MCP | Use `mcp_ids` |
| Mix of MCP and custom tools | Use both `mcp_ids` and `tool_ids` |
| Only custom tools | Use `tool_ids` only |
| Legacy code | Use `tools` field (maps to `tool_ids`) |
