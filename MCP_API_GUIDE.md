# MCP API Usage Guide - Complete Examples

## Endpoint Reference with cURL Examples

### Base URL
```
http://localhost:8000
```

---

## 1. List All MCP Servers

### Request
```bash
curl -X GET http://localhost:8000/mcps
```

### Response (200 OK)
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "url": null,
    "args": {"token": "github_pat_123"},
    "headers": {},
    "env_vars": {"GITHUB_TOKEN": "ghp_xxx"},
    "created_at": "2026-03-07T07:00:00"
  },
  {
    "id": "660f9511-f40c-52e5-b827-557766551111",
    "name": "weather-api",
    "type": "sse",
    "command": null,
    "url": "http://weather-service:8080/mcp",
    "args": {},
    "headers": {"Authorization": "Bearer token"},
    "env_vars": {},
    "created_at": "2026-03-07T07:01:00"
  }
]
```

---

## 2. Register a New MCP Server (Stdio)

### Request
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "args": {},
    "headers": {},
    "env_vars": {
      "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
    }
  }'
```

### Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "github-mcp",
  "type": "stdio",
  "command": "python -m mcp.server.github",
  "url": null,
  "args": {},
  "headers": {},
  "env_vars": {"GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"},
  "created_at": "2026-03-07T07:00:00"
}
```

---

## 3. Register a New MCP Server (SSE)

### Request
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather-api",
    "type": "sse",
    "url": "http://weather-service:8080/mcp",
    "args": {},
    "headers": {
      "Authorization": "Bearer your_token_here",
      "Content-Type": "application/json"
    },
    "env_vars": {}
  }'
```

### Response (201 Created)
```json
{
  "id": "660f9511-f40c-52e5-b827-557766551111",
  "name": "weather-api",
  "type": "sse",
  "command": null,
  "url": "http://weather-service:8080/mcp",
  "args": {},
  "headers": {
    "Authorization": "Bearer your_token_here",
    "Content-Type": "application/json"
  },
  "env_vars": {},
  "created_at": "2026-03-07T07:01:00"
}
```

---

## 4. Get MCP Server Details

### Request
```bash
curl -X GET http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000
```

### Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "github-mcp",
  "type": "stdio",
  "command": "python -m mcp.server.github",
  "url": null,
  "args": {},
  "headers": {},
  "env_vars": {"GITHUB_TOKEN": "ghp_xxx"},
  "created_at": "2026-03-07T07:00:00"
}
```

---

## 5. Discover Tools from MCP Server ⭐ (Main Endpoint)

### Request - Without Cache Refresh
```bash
curl -X POST http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/discover-tools
```

### Request - With Cache Refresh
```bash
curl -X POST "http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/discover-tools?refresh=true"
```

### Response (200 OK)
```json
{
  "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
  "mcp_name": "github-mcp",
  "mcp_type": "stdio",
  "tools_count": 5,
  "tools": [
    {
      "name": "list_repositories",
      "description": "List repositories for a GitHub user or organization",
      "inputSchema": {
        "type": "object",
        "properties": {
          "owner": {
            "type": "string",
            "description": "GitHub user or organization name"
          },
          "limit": {
            "type": "integer",
            "description": "Maximum number of repositories to return",
            "default": 10
          }
        },
        "required": ["owner"]
      }
    },
    {
      "name": "search_repositories",
      "description": "Search for repositories on GitHub",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Search query"
          },
          "language": {
            "type": "string",
            "description": "Filter by programming language"
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "create_issue",
      "description": "Create a new issue in a GitHub repository",
      "inputSchema": {
        "type": "object",
        "properties": {
          "owner": {"type": "string"},
          "repo": {"type": "string"},
          "title": {"type": "string"},
          "body": {"type": "string"}
        },
        "required": ["owner", "repo", "title"]
      }
    },
    {
      "name": "list_issues",
      "description": "List issues from a GitHub repository",
      "inputSchema": {
        "type": "object",
        "properties": {
          "owner": {"type": "string"},
          "repo": {"type": "string"},
          "state": {
            "type": "string",
            "enum": ["open", "closed", "all"]
          }
        },
        "required": ["owner", "repo"]
      }
    },
    {
      "name": "get_issue_details",
      "description": "Get detailed information about a GitHub issue",
      "inputSchema": {
        "type": "object",
        "properties": {
          "owner": {"type": "string"},
          "repo": {"type": "string"},
          "issue_number": {"type": "integer"}
        },
        "required": ["owner", "repo", "issue_number"]
      }
    }
  ],
  "status": "success"
}
```

### Error Response - MCP Not Found (404)
```json
{
  "detail": "MCP server with ID 00000000-0000-0000-0000-000000000000 not found"
}
```

### Error Response - Invalid Configuration (400)
```json
{
  "detail": "Invalid MCP configuration for type 'stdio'. For 'stdio' type, 'command' is required. For 'sse' type, 'url' is required."
}
```

### Error Response - Discovery Failed (500)
```json
{
  "detail": "Failed to discover tools: Connection timeout"
}
```

---

## 6. List Tools from Database

### Request
```bash
curl -X GET http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/tools
```

### Response (200 OK)
```json
[
  {
    "id": "770g0622-g51d-63f6-c938-668877662222",
    "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
    "tool_name": "list_repositories",
    "description": "List repositories for a GitHub user or organization",
    "input_schema": {
      "type": "object",
      "properties": {"owner": {"type": "string"}}
    }
  }
]
```

---

## 7. Add Tool to MCP (Manual)

### Request
```bash
curl -X POST http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/tools \
  -H "Content-Type: application/json" \
  -d '{
    "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
    "tool_name": "list_issues",
    "description": "List issues from a GitHub repository",
    "input_schema": {
      "type": "object",
      "properties": {
        "owner": {"type": "string"},
        "repo": {"type": "string"}
      },
      "required": ["owner", "repo"]
    }
  }'
```

### Response (201 Created)
```json
{
  "id": "880h1733-h62e-74g7-d049-779988773333",
  "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool_name": "list_issues",
  "description": "List issues from a GitHub repository",
  "input_schema": {
    "type": "object",
    "properties": {
      "owner": {"type": "string"},
      "repo": {"type": "string"}
    },
    "required": ["owner", "repo"]
  }
}
```

---

## 8. Stop MCP Server

### Request
```bash
curl -X POST http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/stop
```

### Response (200 OK)
```json
{
  "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
  "mcp_name": "github-mcp",
  "status": "stopped"
}
```

---

## 9. Clear Tool Cache

### Clear All Cache
```bash
curl -X POST http://localhost:8000/mcps/clear-cache
```

### Response
```json
{
  "status": "success",
  "message": "All MCP tool cache cleared"
}
```

### Clear Specific MCP Cache
```bash
curl -X POST "http://localhost:8000/mcps/clear-cache?mcp_id=550e8400-e29b-41d4-a716-446655440000"
```

### Response
```json
{
  "status": "success",
  "message": "Cache cleared for MCP 550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 10. Update MCP Server

### Request
```bash
curl -X PUT http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python -m mcp.server.github --new-flag",
    "env_vars": {
      "GITHUB_TOKEN": "ghp_new_token"
    }
  }'
```

### Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "github-mcp",
  "type": "stdio",
  "command": "python -m mcp.server.github --new-flag",
  "url": null,
  "args": {},
  "headers": {},
  "env_vars": {"GITHUB_TOKEN": "ghp_new_token"},
  "created_at": "2026-03-07T07:00:00"
}
```

---

## 11. Delete MCP Server

### Request
```bash
curl -X DELETE http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000
```

### Response (204 No Content)
```
(empty response body)
```

---

## Advanced Scenarios

### Scenario 1: Discover, Parse, and Process Tools

```bash
#!/bin/bash

MCP_ID="550e8400-e29b-41d4-a716-446655440000"

# Discover tools and extract names
curl -s -X POST http://localhost:8000/mcps/$MCP_ID/discover-tools | \
  jq -r '.tools | map(.name) | join("\n")'
```

### Scenario 2: Check Tool Availability

```bash
#!/bin/bash

MCP_ID="550e8400-e29b-41d4-a716-446655440000"
EXPECTED_TOOL="list_repositories"

tool_exists=$(curl -s -X POST http://localhost:8000/mcps/$MCP_ID/discover-tools | \
  jq --arg tool "$EXPECTED_TOOL" '.tools | any(.name == $tool)')

if [ "$tool_exists" == "true" ]; then
  echo "✅ Tool '$EXPECTED_TOOL' found"
else
  echo "❌ Tool '$EXPECTED_TOOL' not found"
fi
```

### Scenario 3: Batch Register Multiple MCPs

```bash
#!/bin/bash

MCPs=(
  '{"name":"github","type":"stdio","command":"python -m mcp.server.github"}'
  '{"name":"weather","type":"sse","url":"http://weather:8080/mcp"}'
  '{"name":"slack","type":"stdio","command":"python -m mcp.server.slack"}'
)

for mcp_json in "${MCPs[@]}"; do
  echo "Registering: $(echo $mcp_json | jq -r '.name')"
  curl -X POST http://localhost:8000/mcps \
    -H "Content-Type: application/json" \
    -d "$mcp_json"
  echo ""
done
```

---

## Common Patterns

### Pattern 1: Retry Logic

```bash
retry_discover() {
  local mcp_id=$1
  local max_attempts=3
  local attempt=1
  
  while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt..."
    curl -s -X POST http://localhost:8000/mcps/$mcp_id/discover-tools && return 0
    attempt=$((attempt + 1))
    sleep 2
  done
  
  echo "Failed after $max_attempts attempts"
  return 1
}
```

### Pattern 2: Monitoring

```bash
#!/bin/bash

# Monitor tool discovery every 5 minutes
while true; do
  echo "$(date): Checking MCP tools..."
  curl -s -X POST http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/discover-tools | \
    jq '.tools_count'
  sleep 300
done
```

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Tool discovery completed |
| 201 | Created | MCP server registered |
| 204 | No Content | MCP server deleted |
| 400 | Bad Request | Invalid configuration |
| 404 | Not Found | MCP server doesn't exist |
| 500 | Server Error | Discovery failed |

---

## Best Practices

1. **Use Discovery Refresh Wisely**: Only use `?refresh=true` when needed to reduce server load
2. **Cache Tools**: The system caches results automatically
3. **Error Handling**: Always check response status and handle errors gracefully
4. **Timeout Handling**: Set appropriate timeouts in client applications
5. **Logging**: Log all discovery attempts for debugging
6. **Monitoring**: Monitor tool availability for critical MCPs

