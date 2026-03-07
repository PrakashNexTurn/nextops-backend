# Dynamic MCP Client - API Examples

## HTTP Examples with curl

### 1. Register HTTP-based MCP (GitHub Copilot)

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp",
    "headers": {
      "Authorization": "Bearer ghp_xxxxxxxxxxxx"
    }
  }'
```

**Response:**
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

---

### 2. Register Stdio-based MCP (Local Python Script)

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "azure-mcp",
    "type": "stdio",
    "command": "/usr/bin/python3",
    "args": ["/app/mcp_servers/azure_mcp_server.py"],
    "env_vars": {
      "AZURE_CLIENT_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "AZURE_TENANT_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "AZURE_CLIENT_SECRET": "your-secret-here"
    }
  }'
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "azure-mcp",
  "type": "stdio",
  "url": null,
  "command": "/usr/bin/python3",
  "args": ["/app/mcp_servers/azure_mcp_server.py"],
  "headers": {},
  "env_vars": {
    "AZURE_CLIENT_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "AZURE_TENANT_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "AZURE_CLIENT_SECRET": "your-secret-here"
  },
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

### 3. Register NPM-based MCP (Kubernetes)

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "kubernetes-mcp",
    "type": "npm",
    "command": "mcp-server-kubernetes",
    "env_vars": {
      "KUBECONFIG": "/home/user/.kube/config"
    }
  }'
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "name": "kubernetes-mcp",
  "type": "npm",
  "url": null,
  "command": "mcp-server-kubernetes",
  "args": [],
  "headers": {},
  "env_vars": {
    "KUBECONFIG": "/home/user/.kube/config"
  },
  "created_at": "2024-01-15T10:40:00Z"
}
```

---

### 4. Register Terraform MCP

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "terraform-mcp",
    "type": "npm",
    "command": "mcp-server-terraform",
    "env_vars": {
      "TF_VAR_region": "us-east-1"
    }
  }'
```

---

### 5. Register PostgreSQL MCP

```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres-mcp",
    "type": "npm",
    "command": "mcp-postgres-server",
    "env_vars": {
      "PG_HOST": "localhost",
      "PG_PORT": "5432",
      "PG_USER": "postgres",
      "PG_PASSWORD": "postgres_password",
      "PG_DATABASE": "mydb"
    }
  }'
```

---

### 6. List All MCPs

```bash
curl http://localhost:8000/mcps
```

**Response:**
```json
[
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
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "azure-mcp",
    "type": "stdio",
    "url": null,
    "command": "/usr/bin/python3",
    "args": ["/app/mcp_servers/azure_mcp_server.py"],
    "headers": {},
    "env_vars": {...},
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

### 7. Get Specific MCP by ID

```bash
curl http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
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

---

### 8. Update MCP Configuration

#### Update Authentication Token

```bash
curl -X PUT http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "headers": {
      "Authorization": "Bearer new_ghp_token"
    }
  }'
```

#### Update Environment Variables

```bash
curl -X PUT http://localhost:8000/mcps/660e8400-e29b-41d4-a716-446655440001 \
  -H "Content-Type: application/json" \
  -d '{
    "env_vars": {
      "AZURE_CLIENT_ID": "new-client-id",
      "AZURE_TENANT_ID": "new-tenant-id"
    }
  }'
```

#### Update Command Arguments

```bash
curl -X PUT http://localhost:8000/mcps/770e8400-e29b-41d4-a716-446655440002 \
  -H "Content-Type: application/json" \
  -d '{
    "args": ["--kubeconfig", "/path/to/kubeconfig"]
  }'
```

---

### 9. Delete MCP

```bash
curl -X DELETE http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000
```

**Response:** 204 No Content

---

### 10. Discover Tools from MCP

```bash
curl -X POST http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/discover-tools
```

**Response:**
```json
{
  "mcp_id": "550e8400-e29b-41d4-a716-446655440000",
  "mcp_name": "github-mcp",
  "mcp_type": "http",
  "tools_count": 5,
  "tools": [
    {
      "name": "search_code",
      "description": "Search GitHub code repositories",
      "inputSchema": {...}
    },
    ...
  ],
  "status": "success"
}
```

---

### 11. Stop MCP Server

```bash
curl -X POST http://localhost:8000/mcps/660e8400-e29b-41d4-a716-446655440001/stop
```

**Response:**
```json
{
  "mcp_id": "660e8400-e29b-41d4-a716-446655440001",
  "mcp_name": "azure-mcp",
  "status": "stopped"
}
```

---

### 12. Clear Cache

#### Clear Cache for Specific MCP

```bash
curl -X POST "http://localhost:8000/mcps/clear-cache?mcp_id=550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared for MCP 550e8400-e29b-41d4-a716-446655440000"
}
```

#### Clear All Caches

```bash
curl -X POST http://localhost:8000/mcps/clear-cache
```

**Response:**
```json
{
  "status": "success",
  "message": "All MCP tool cache cleared"
}
```

---

## Python Examples

### 1. Get Client by Name

```python
from app.services.mcp_dynamic_client import get_mcp_client_by_name
from app.db.database import get_db

# Get database session
db = next(get_db())

# Get client by unique name
github_client = get_mcp_client_by_name("github-mcp", db)

# Use the client
if github_client:
    print("GitHub MCP client ready!")
else:
    print("GitHub MCP not found in database")
```

---

### 2. Get Client by ID

```python
from app.services.mcp_dynamic_client import get_mcp_client_by_id
from app.db.database import get_db
from uuid import UUID

db = next(get_db())
mcp_id = UUID("550e8400-e29b-41d4-a716-446655440000")

azure_client = get_mcp_client_by_id(mcp_id, db)

if azure_client:
    print("Azure MCP client ready!")
```

---

### 3. List All MCPs

```python
from app.services.mcp_dynamic_client import list_all_mcp_clients
from app.db.database import get_db

db = next(get_db())
all_mcps = list_all_mcp_clients(db)

for mcp_info in all_mcps:
    print(f"  {mcp_info['name']} ({mcp_info['type']})")
    print(f"  Created: {mcp_info['created_at']}")
    print(f"  Cached: {mcp_info['cached']}")
    print()
```

---

### 4. Create Client from Dictionary

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service

service = get_dynamic_mcp_service()

config_dict = {
    "server_type": "http",
    "endpoint": "https://api.example.com/mcp",
    "auth_headers": {"Authorization": "Bearer token"},
    "timeout": 600
}

try:
    client = service.create_mcp_client_from_dict(config_dict)
    print("Client created successfully!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

---

### 5. Validate Configuration

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service
from app.db.database import get_db
from uuid import UUID

service = get_dynamic_mcp_service()
db = next(get_db())
mcp_id = UUID("550e8400-e29b-41d4-a716-446655440000")

is_valid, error_msg = service.validate_mcp_config_in_db(mcp_id, db)

if is_valid:
    print("MCP configuration is valid!")
else:
    print(f"Configuration error: {error_msg}")
```

---

### 6. Clear Cache

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service
from uuid import UUID

service = get_dynamic_mcp_service()

# Clear specific MCP cache
mcp_id = UUID("550e8400-e29b-41d4-a716-446655440000")
result = service.clear_client_cache(mcp_id)
print(result)  # {"status": "success", "cleared": "..."}

# Clear all caches
result = service.clear_client_cache()
print(result)  # {"status": "success", "cleared_count": 3}
```

---

### 7. Full Integration Example

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service
from app.db.database import get_db

# Get service and database session
service = get_dynamic_mcp_service()
db = next(get_db())

# List all available MCPs
print("Available MCP Servers:")
mcps = service.list_all_mcp_clients(db)
for mcp in mcps:
    print(f"  - {mcp['name']} ({mcp['type']})")

# Get specific client
if mcps:
    client = service.get_mcp_client_by_name(mcps[0]['name'], db)
    if client:
        print(f"\nConnected to {mcps[0]['name']}")
        # Use client here
    else:
        print("Failed to create client")

# Update cache
service.clear_client_cache()
print("\nCache cleared")
```

---

## Error Handling

### Handle Missing MCP

```python
from app.services.mcp_dynamic_client import get_mcp_client_by_name
from app.db.database import get_db

db = next(get_db())
client = get_mcp_client_by_name("nonexistent", db)

if client is None:
    print("MCP not found - register it first!")
else:
    # Use client
    pass
```

---

### Handle Configuration Errors

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service

service = get_dynamic_mcp_service()

config_dict = {
    "server_type": "http",
    # Missing 'endpoint' - will cause error
}

try:
    client = service.create_mcp_client_from_dict(config_dict)
except ValueError as e:
    print(f"Configuration validation failed: {e}")
    # endpoint is required for HTTP servers
```

---

## Batch Operations

### Register Multiple MCPs

```bash
#!/bin/bash

mcps=(
  '{"name": "github", "type": "http", "url": "https://api.githubcopilot.com/mcp"}'
  '{"name": "azure", "type": "stdio", "command": "/usr/bin/python3", "args": ["/path/to/azure_mcp_server.py"]}'
  '{"name": "k8s", "type": "npm", "command": "mcp-server-kubernetes"}'
)

for mcp_json in "${mcps[@]}"; do
  echo "Registering: $mcp_json"
  curl -X POST http://localhost:8000/mcps \
    -H "Content-Type: application/json" \
    -d "$mcp_json"
  echo ""
done
```

---

## Performance Testing

### Check Cache Performance

```python
import time
from app.services.mcp_dynamic_client import get_mcp_client_by_name
from app.db.database import get_db

db = next(get_db())

# First call (creates and caches)
start = time.time()
client1 = get_mcp_client_by_name("github-mcp", db)
first_time = (time.time() - start) * 1000  # ms

# Second call (returns from cache)
start = time.time()
client2 = get_mcp_client_by_name("github-mcp", db)
second_time = (time.time() - start) * 1000  # ms

print(f"First call (create + cache): {first_time:.2f}ms")
print(f"Second call (from cache): {second_time:.2f}ms")
print(f"Speedup: {first_time/second_time:.1f}x faster")
```

---

## References

- **API Documentation:** http://localhost:8000/docs
- **Full Guide:** `DYNAMIC_MCP_CLIENT_GUIDE.md`
- **Quick Reference:** `DYNAMIC_MCP_CLIENT_QUICKREF.md`
- **Implementation Details:** `DYNAMIC_MCP_CLIENT_IMPLEMENTATION.md`

---

**Last Updated:** 2024-01-15
**Status:** ✅ Complete
