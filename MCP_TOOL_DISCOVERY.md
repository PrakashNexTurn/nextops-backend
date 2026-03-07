# MCP Server Tool Discovery System

## Overview

The MCP Server Tool Discovery System enables you to dynamically discover and list tools available from registered MCP (Model Context Protocol) servers. The system supports both **stdio-based** and **SSE-based** MCP servers.

## Features

✅ **Dual MCP Support**: Works with both stdio and SSE-based MCP servers
✅ **Tool Discovery**: Automatically discovers available tools from MCP servers
✅ **Caching**: Intelligent caching to avoid redundant server queries
✅ **Multiple Interfaces**: 
  - REST API endpoints
  - Python utility script
  - Bash shell script
✅ **Multiple Output Formats**: Table, JSON, CSV
✅ **Process Management**: Automatic startup/shutdown of stdio MCP servers
✅ **Configuration Validation**: Validates MCP configurations before discovery

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface                              │
├──────────────────┬──────────────────┬───────────────────────┤
│   REST API       │  Python Script   │    Bash Script        │
│  (FastAPI)       │ (list_mcp_tools) │ (list_mcp_tools.sh)   │
└──────────┬───────┴────────┬─────────┴──────────┬────────────┘
           │                 │                    │
           └─────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ MCP Discovery   │
                    │  Service        │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼──────┐         ┌───▼──────┐        ┌───▼──────┐
    │  Stdio   │         │   SSE    │        │ Database │
    │ Protocol │         │ Protocol │        │ (Models) │
    │  Manager │         │ Manager  │        │          │
    └──────────┘         └──────────┘        └──────────┘
```

---

## Usage Guide

### 1. REST API Endpoints

#### List All MCP Servers

```bash
curl -X GET http://localhost:8000/mcps
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.stdio",
    "url": null,
    "args": {},
    "headers": {},
    "env_vars": {},
    "created_at": "2026-03-07T07:00:00"
  }
]
```

#### Discover Tools from MCP Server

```bash
# By MCP ID
curl -X POST http://localhost:8000/mcps/{mcp_id}/discover-tools

# With cache refresh
curl -X POST http://localhost:8000/mcps/{mcp_id}/discover-tools?refresh=true
```

**Response:**
```json
{
  "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
  "mcp_name": "github-mcp",
  "mcp_type": "stdio",
  "tools_count": 5,
  "tools": [
    {
      "name": "list_repositories",
      "description": "List repositories from GitHub",
      "inputSchema": {
        "type": "object",
        "properties": {
          "owner": { "type": "string" },
          "limit": { "type": "integer" }
        }
      }
    }
  ],
  "status": "success"
}
```

#### List Tools for MCP (from Database)

```bash
curl -X GET http://localhost:8000/mcps/{mcp_id}/tools
```

#### Stop MCP Server

```bash
curl -X POST http://localhost:8000/mcps/{mcp_id}/stop
```

#### Clear Tool Cache

```bash
# Clear cache for specific MCP
curl -X POST http://localhost:8000/mcps/clear-cache?mcp_id={mcp_id}

# Clear all cache
curl -X POST http://localhost:8000/mcps/clear-cache
```

---

### 2. Python Utility Script

#### Installation

Ensure the project is set up:

```bash
cd /home/ubuntu/work/nextops-backend
source venv/bin/activate
pip install -r requirements.txt
```

#### Usage

**List tools from MCP by ID:**
```bash
python list_mcp_tools.py --mcp-id 550e8400-e29b-41d4-a716-446655440000
```

**List tools from MCP by name:**
```bash
python list_mcp_tools.py --mcp-name "github-mcp"
```

**Force refresh (bypass cache):**
```bash
python list_mcp_tools.py --mcp-id 550e8400-e29b-41d4-a716-446655440000 --refresh
```

**List all registered MCP servers:**
```bash
python list_mcp_tools.py --list-servers
```

**Output formats:**

```bash
# Table format (default)
python list_mcp_tools.py --mcp-name "github-mcp"

# JSON format
python list_mcp_tools.py --mcp-name "github-mcp" --format json

# CSV format
python list_mcp_tools.py --mcp-name "github-mcp" --format csv
```

---

### 3. Bash Shell Script

#### Setup

Make the script executable:
```bash
chmod +x /home/ubuntu/work/nextops-backend/list_mcp_tools.sh
```

#### Usage

```bash
# List tools from MCP
./list_mcp_tools.sh --mcp-id 550e8400-e29b-41d4-a716-446655440000

# List tools by name
./list_mcp_tools.sh --mcp-name "github-mcp"

# List all MCP servers
./list_mcp_tools.sh --list-servers

# Force refresh
./list_mcp_tools.sh --mcp-id 550e8400-e29b-41d4-a716-446655440000 --refresh

# Output as JSON
./list_mcp_tools.sh --mcp-name "github-mcp" --format json

# Show help
./list_mcp_tools.sh --help
```

---

## Setting Up MCP Servers

### Registering a Stdio MCP Server

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "args": {
      "token": "github_pat_xxx"
    },
    "env_vars": {
      "GITHUB_TOKEN": "your_token_here"
    }
  }'
```

### Registering an SSE MCP Server

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "anthropic-mcp",
    "type": "sse",
    "url": "http://localhost:3000/mcp",
    "headers": {
      "Authorization": "Bearer your_token"
    }
  }'
```

---

## Configuration

### Environment Variables

The MCP discovery service reads from the environment:

```bash
# Database connection
DATABASE_URL=postgresql://postgres:password@localhost:5432/nextops

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### MCP Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique name for the MCP server |
| `type` | string | ✅ | Either "stdio" or "sse" |
| `command` | string | For stdio | Command to start the stdio MCP server |
| `url` | string | For SSE | URL of the SSE MCP server |
| `args` | object | Optional | Additional arguments for the server |
| `headers` | object | Optional | HTTP headers for SSE requests |
| `env_vars` | object | Optional | Environment variables for stdio processes |

---

## How It Works

### Stdio MCP Discovery Process

1. **Startup**: Spawns the MCP server process using the configured command
2. **Initialize**: Sends MCP initialize message to establish connection
3. **Query Tools**: Requests available tools via MCP protocol
4. **Parse**: Extracts tool names, descriptions, and input schemas
5. **Shutdown**: Gracefully terminates the server process
6. **Cache**: Stores results for performance optimization

### SSE MCP Discovery Process

1. **Connect**: Establishes HTTP/SSE connection to the MCP server
2. **Authenticate**: Sends authorization headers if configured
3. **Initialize**: Initiates MCP protocol with server
4. **Query Tools**: Requests available tools via HTTP POST
5. **Parse**: Extracts tool information from response
6. **Cache**: Stores results for performance optimization

---

## Examples

### Example 1: GitHub MCP Server

**Register:**
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "env_vars": {
      "GITHUB_TOKEN": "ghp_xxx"
    }
  }'
```

**Discover tools:**
```bash
./list_mcp_tools.sh --mcp-name "github-mcp"
```

**Expected output:**
```
🔍 Discovering tools from MCP: github-mcp (550e8400-e29b-41d4-a716-446655440000)
   Type: stdio
   Command: python -m mcp.server.github

Tool Name                          | Description
-----------------------------------|---
list_repositories                  | List repositories for a GitHub user or org
search_repositories                | Search GitHub repositories
create_issue                       | Create a new GitHub issue
list_issues                        | List issues from a repository

✅ Total tools discovered: 4
```

### Example 2: Weather MCP Server (SSE)

**Register:**
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather-api",
    "type": "sse",
    "url": "http://weather-service:8080/mcp",
    "headers": {
      "Authorization": "Bearer weather_token"
    }
  }'
```

**Discover tools:**
```bash
./list_mcp_tools.sh --mcp-name "weather-api" --format json
```

---

## Troubleshooting

### Issue: "MCP server not found"

**Solution:** 
1. Verify MCP is registered: `./list_mcp_tools.sh --list-servers`
2. Check the ID or name is correct
3. Ensure database has the MCP entry

### Issue: "Invalid MCP configuration"

**Solution:**
- For stdio: Ensure `command` field is set
- For SSE: Ensure `url` field is set
- Verify the server configuration using API: `curl http://localhost:8000/mcps/{mcp_id}`

### Issue: "Timeout connecting to MCP server"

**Solution:**
1. Verify the MCP server is running
2. Check command syntax or SSE URL
3. Verify network connectivity
4. Increase timeout if server is slow

### Issue: "Failed to parse MCP response"

**Solution:**
1. Verify MCP server implements the correct protocol
2. Check server logs for errors
3. Ensure proper JSON formatting in responses

---

## Performance Considerations

### Caching Strategy

- Tool lists are cached in memory for performance
- Cache is invalidated when:
  - Explicit `--refresh` flag is used
  - Server is stopped
  - Cache is manually cleared
- Each MCP server has its own cache entry

### Process Management

- Stdio MCP servers are started on-demand
- Processes are terminated after tool discovery
- Failed processes are automatically cleaned up
- Multiple simultaneous discoveries are supported

---

## Security Considerations

1. **Environment Variables**: Sensitive data (tokens, passwords) should be in env_vars
2. **Headers**: Use for authentication tokens in SSE servers
3. **Database**: Use PostgreSQL authentication for database access
4. **Process Isolation**: Stdio servers run in isolated processes
5. **Timeouts**: Requests timeout after 10 seconds to prevent hanging

---

## Advanced Usage

### Custom Output Processing

Process JSON output with jq:

```bash
python list_mcp_tools.py --mcp-name "github-mcp" --format json | \
  jq '.tools | map(.name)'
```

### Batch Operations

List tools for all MCP servers:

```bash
python list_mcp_tools.py --list-servers --format json | \
  jq -r '.[] | .id' | \
  while read mcp_id; do
    echo "==== $mcp_id ===="
    python list_mcp_tools.py --mcp-id "$mcp_id"
  done
```

### Integration with Scripts

```bash
#!/bin/bash
mcp_id="550e8400-e29b-41d4-a716-446655440000"
tools_json=$(python list_mcp_tools.py --mcp-id "$mcp_id" --format json)
tool_count=$(echo "$tools_json" | jq '.tools_count')
echo "Found $tool_count tools in MCP server"
```

---

## API Documentation

### Complete API Reference

See FastAPI auto-generated docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Files Modified/Created

| File | Type | Purpose |
|------|------|---------|
| `app/services/mcp_discovery.py` | Modified | Enhanced discovery service with real protocol implementation |
| `app/api/mcps.py` | Modified | Added new discovery endpoints |
| `list_mcp_tools.py` | Created | Standalone Python utility script |
| `list_mcp_tools.sh` | Created | Bash wrapper script |
| `MCP_TOOL_DISCOVERY.md` | Created | This documentation |

---

## Next Steps

1. **Register your MCP servers** using the REST API or curl
2. **Test discovery** with your preferred interface (API/script)
3. **Integrate** tool discovery into your automation workflows
4. **Monitor** tool availability for dynamic configuration

---

## Support

For issues or questions:
1. Check troubleshooting section
2. Review FastAPI docs at `/docs`
3. Check server logs: `tail -f /var/log/nextops/mcp.log`
4. Create an issue on GitHub

