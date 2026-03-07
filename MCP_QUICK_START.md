# MCP Tool Discovery - Quick Reference

## TL;DR - 5 Minute Setup

### 1. Start the API Server

```bash
cd /home/ubuntu/work/nextops-backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Register an MCP Server

```bash
# Stdio-based (like GitHub, Claude tools)
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.myserver"
  }'

# SSE-based (like web services)
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-service",
    "type": "sse",
    "url": "http://localhost:3000/mcp"
  }'
```

### 3. List Tools

**Via API:**
```bash
# First get the MCP ID
curl http://localhost:8000/mcps

# Then discover tools
curl -X POST http://localhost:8000/mcps/{MCP_ID}/discover-tools
```

**Via Python Script:**
```bash
# By name
python list_mcp_tools.py --mcp-name "my-mcp"

# By ID
python list_mcp_tools.py --mcp-id "550e8400-e29b-41d4-a716-446655440000"

# List all servers
python list_mcp_tools.py --list-servers
```

**Via Bash Script:**
```bash
chmod +x list_mcp_tools.sh

./list_mcp_tools.sh --mcp-name "my-mcp"
./list_mcp_tools.sh --list-servers
./list_mcp_tools.sh --help
```

---

## Complete Command Reference

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/mcps` | List all MCP servers |
| POST | `/mcps` | Register new MCP server |
| GET | `/mcps/{id}` | Get MCP details |
| POST | `/mcps/{id}/discover-tools` | **Discover and list tools** ⭐ |
| GET | `/mcps/{id}/tools` | List tools from database |
| POST | `/mcps/{id}/stop` | Stop MCP server process |
| POST | `/mcps/clear-cache` | Clear tool cache |

### Python Script Options

```bash
python list_mcp_tools.py \
  --mcp-id <uuid>          # UUID of MCP
  --mcp-name <name>        # Name of MCP
  --list-servers           # List all MCPs
  --refresh                # Bypass cache
  --format json|csv|table  # Output format
```

### Bash Script Options

```bash
./list_mcp_tools.sh \
  --mcp-id <uuid>          # UUID of MCP
  --mcp-name <name>        # Name of MCP
  --list-servers           # List all MCPs
  --refresh                # Bypass cache
  --format json|csv|table  # Output format
  --help                   # Show help
```

---

## Real-World Examples

### Example 1: List GitHub MCP Tools

```bash
# Register
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "env_vars": {"GITHUB_TOKEN": "ghp_xxx"}
  }'

# Discover tools
./list_mcp_tools.sh --mcp-name "github-mcp"
```

### Example 2: List Tools with JSON Output

```bash
python list_mcp_tools.py --mcp-name "github-mcp" --format json | jq '.tools'
```

### Example 3: Force Refresh (Skip Cache)

```bash
./list_mcp_tools.sh --mcp-name "my-service" --refresh
```

### Example 4: Process with Custom Filters

```bash
python list_mcp_tools.py --mcp-name "my-mcp" --format json | \
  jq '.tools | map(select(.name | startswith("read")))'
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "MCP not found" | Check ID/name with `--list-servers` |
| "Invalid configuration" | Ensure `command` (stdio) or `url` (sse) is set |
| "Timeout" | Verify server is running and network is accessible |
| "Bad response" | Check server implements correct MCP protocol |
| "No tools returned" | Server may not support tool listing or tools list is empty |

---

## Output Examples

### Table Format (Default)
```
Tool Name                          | Description
-----------------------------------|---
list_repositories                  | List repositories from GitHub
search_repositories                | Search GitHub repositories
create_issue                       | Create a new GitHub issue
```

### JSON Format
```json
{
  "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
  "mcp_name": "github-mcp",
  "tools_count": 3,
  "tools": [
    {
      "name": "list_repositories",
      "description": "List repositories from GitHub",
      "inputSchema": {...}
    }
  ]
}
```

### CSV Format
```csv
Tool Name,Description,Input Schema
list_repositories,"List repositories","{...}"
search_repositories,"Search GitHub","{...}"
```

---

## Environment Setup

### Required Dependencies

```bash
pip install fastapi==0.109.0
pip install sqlalchemy==2.0.25
pip install psycopg2-binary==2.9.9
pip install aiohttp  # For SSE support (add to requirements.txt)
```

### Database Configuration

```bash
# .env file
DATABASE_URL=postgresql://postgres:password@localhost:5432/nextops
```

### Start Services

```bash
# Terminal 1: Start database
sudo service postgresql start

# Terminal 2: Start API server
cd /home/ubuntu/work/nextops-backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Run discovery
./list_mcp_tools.sh --list-servers
```

---

## Features at a Glance

✅ **Discover tools from MCP servers**
✅ **Support for stdio and SSE protocols**
✅ **Multiple output formats (table, JSON, CSV)**
✅ **Tool caching for performance**
✅ **REST API and CLI interfaces**
✅ **Automatic process management**
✅ **Error handling and validation**
✅ **Configuration management**

---

## What's New

| Component | Status | Purpose |
|-----------|--------|---------|
| `MCPDiscoveryService` | ✅ Enhanced | Real MCP protocol implementation |
| `/mcps/{id}/discover-tools` | ✅ New | Main discovery endpoint |
| `list_mcp_tools.py` | ✅ New | Python utility script |
| `list_mcp_tools.sh` | ✅ New | Bash wrapper |
| `MCP_TOOL_DISCOVERY.md` | ✅ New | Full documentation |

---

## Next Steps

1. ✅ Review the full documentation: `MCP_TOOL_DISCOVERY.md`
2. ✅ Register your first MCP server
3. ✅ Run tool discovery: `./list_mcp_tools.sh --list-servers`
4. ✅ Integrate into your workflows
5. ✅ Monitor tool availability

---

**For detailed documentation**, see **`MCP_TOOL_DISCOVERY.md`**

