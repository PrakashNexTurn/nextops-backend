# Dynamic MCP Client Quick Reference

## Quick Start (5 minutes)

### 1. Register an MCP Server

```bash
# HTTP-based MCP (e.g., GitHub Copilot)
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp",
    "headers": {"Authorization": "Bearer ghp_token"}
  }'

# Stdio-based MCP (e.g., Local Python script)
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "azure-mcp",
    "type": "stdio",
    "command": "/usr/bin/python3",
    "args": ["/app/mcp_servers/azure_mcp_server.py"],
    "env_vars": {"AZURE_CLIENT_ID": "..."}
  }'

# NPM-based MCP (e.g., Kubernetes)
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "kubernetes-mcp",
    "type": "npm",
    "command": "mcp-server-kubernetes",
    "env_vars": {"KUBECONFIG": "/home/user/.kube/config"}
  }'
```

### 2. Get MCP by ID

```bash
# List all MCPs (get IDs)
curl http://localhost:8000/mcps

# Get specific MCP
curl http://localhost:8000/mcps/{mcp_id}
```

### 3. Use in Python Code

```python
from app.services.mcp_dynamic_client import get_mcp_client_by_name, get_mcp_client_by_id
from app.db.database import get_db

# Get database session
db = next(get_db())

# Method 1: By name (recommended)
github_client = get_mcp_client_by_name("github-mcp", db)

# Method 2: By ID
azure_client = get_mcp_client_by_id(mcp_uuid, db)

# Use the client
# ...
```

## Common Operations

### List All MCP Servers

```bash
curl http://localhost:8000/mcps
```

### Create MCP Server

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{"name": "...", "type": "...", ...}'
```

### Update MCP Configuration

```bash
curl -X PUT http://localhost:8000/mcps/{mcp_id} \
  -H "Content-Type: application/json" \
  -d '{"headers": {"Authorization": "Bearer new_token"}}'
```

### Delete MCP Server

```bash
curl -X DELETE http://localhost:8000/mcps/{mcp_id}
```

### Clear Client Cache

```bash
curl -X POST http://localhost:8000/mcps/clear-cache?mcp_id={mcp_id}
```

## Python Code Examples

### Get Client by Name

```python
from app.services.mcp_dynamic_client import get_mcp_client_by_name
from app.db.database import get_db

db = next(get_db())
client = get_mcp_client_by_name("github-mcp", db)
```

### Get Client by ID

```python
from app.services.mcp_dynamic_client import get_mcp_client_by_id
from app.db.database import get_db
from uuid import UUID

db = next(get_db())
mcp_id = UUID("550e8400-e29b-41d4-a716-446655440000")
client = get_mcp_client_by_id(mcp_id, db)
```

### List All MCPs

```python
from app.services.mcp_dynamic_client import list_all_mcp_clients
from app.db.database import get_db

db = next(get_db())
all_mcps = list_all_mcp_clients(db)

for mcp_info in all_mcps:
    print(f"{mcp_info['name']} ({mcp_info['type']})")
```

### Create Client from Dict

```python
from app.services.mcp_factory import MCPClientFactory
from app.schemas.mcp_config import MCPClientConfig

config_dict = {
    "server_type": "http",
    "endpoint": "https://api.example.com/mcp",
    "timeout": 600
}

config = MCPClientConfig(**config_dict)
client = MCPClientFactory.create(config)
```

### Validate Configuration

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service
from app.db.database import get_db
from uuid import UUID

service = get_dynamic_mcp_service()
db = next(get_db())
mcp_id = UUID("...")

is_valid, error_msg = service.validate_mcp_config_in_db(mcp_id, db)

if not is_valid:
    print(f"Configuration error: {error_msg}")
```

## Database Configuration Schema

### HTTP Server Type

```json
{
  "name": "github-mcp",
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp",
  "headers": {
    "Authorization": "Bearer ghp_xxxxxxxxxxxx"
  }
}
```

### Stdio Server Type

```json
{
  "name": "azure-mcp",
  "type": "stdio",
  "command": "/usr/bin/python3",
  "args": ["/app/mcp_servers/azure_mcp_server.py"],
  "env_vars": {
    "AZURE_CLIENT_ID": "client-id",
    "AZURE_TENANT_ID": "tenant-id"
  }
}
```

### NPM Server Type

```json
{
  "name": "kubernetes-mcp",
  "type": "npm",
  "command": "mcp-server-kubernetes",
  "env_vars": {
    "KUBECONFIG": "/home/user/.kube/config"
  }
}
```

## Environment Variable Configuration

For sensitive data, use environment variables:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export PG_PASSWORD=postgres_password
```

Then use in MCP configuration:

```json
{
  "name": "github-mcp",
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp",
  "headers": {
    "Authorization": "Bearer ${GITHUB_TOKEN}"
  }
}
```

## Troubleshooting

### MCP Server Not Found

```python
# Check if MCP exists
client = get_mcp_client_by_name("nonexistent-mcp", db)
if client is None:
    print("MCP not registered in database")
    # Register it first via API
```

### Configuration Validation Error

```python
# Validate before use
service = get_dynamic_mcp_service()
is_valid, error_msg = service.validate_mcp_config_in_db(mcp_id, db)

if not is_valid:
    print(f"Invalid config: {error_msg}")
    # Fix the configuration
```

### Clear Cache and Reload

```python
service = get_dynamic_mcp_service()

# Clear specific MCP cache
service.clear_client_cache(mcp_id)

# Clear all caches
service.clear_client_cache()

# Re-create client from latest database config
client = service.get_mcp_client_by_name("mcp-name", db)
```

## API Response Examples

### Create MCP (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "github-mcp",
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp",
  "command": null,
  "args": {},
  "headers": {
    "Authorization": "Bearer ghp_xxxxxxxxxxxx"
  },
  "env_vars": {},
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List MCPs (200 OK)

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "github-mcp",
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "azure-mcp",
    "type": "stdio",
    "command": "/usr/bin/python3",
    "created_at": "2024-01-15T11:00:00Z"
  }
]
```

### Error Response (404 Not Found)

```json
{
  "detail": "MCP not found"
}
```

## Files and Locations

| File | Purpose |
|------|---------|
| `app/models/mcp.py` | Database model for MCP servers |
| `app/schemas/mcp_config.py` | Configuration validation schema |
| `app/schemas/mcp_schema.py` | API schema for MCP endpoints |
| `app/services/mcp_factory.py` | Factory for creating clients |
| `app/services/mcp_dynamic_client.py` | Database-driven service |
| `app/services/mcp_clients.py` | Backward-compatible functions |
| `app/api/mcps.py` | REST API endpoints |

## Next Steps

1. ✅ Register MCP servers via API
2. ✅ Use `get_mcp_client_by_name()` in your code
3. ✅ Update configuration via REST API without redeployment
4. ✅ Scale to multiple MCP servers easily

---

**Last Updated:** 2024-01-15
**Status:** ✅ Production Ready
