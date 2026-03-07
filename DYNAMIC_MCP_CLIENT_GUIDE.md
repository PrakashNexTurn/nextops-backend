# Dynamic MCP Client Initialization Guide

## Overview

The MCP client system has been refactored from **hardcoded functions** to a **fully dynamic, database-driven architecture**. This enables:

- ✅ **Zero code changes** to add new MCP servers
- ✅ **Configuration management** via REST API
- ✅ **Scalability** to unlimited MCP server types
- ✅ **Backward compatibility** with existing code
- ✅ **Multi-tenancy support** for different configurations

## Architecture

### Before (Hardcoded - ❌ Not Scalable)

```python
# app/services/mcp_clients.py
def get_github_http_mcp_client():
    """Hardcoded GitHub MCP client"""
    return MCPClient(lambda: streamablehttp_client(
        url="https://api.githubcopilot.com/mcp",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
    ))

# Problem: Each new MCP server requires code changes!
```

### After (Dynamic Database-Driven - ✅ Fully Scalable)

```python
# app/services/mcp_dynamic_client.py
def get_mcp_client_by_name(mcp_name: str, db: Session):
    """Get client from database configuration"""
    service = get_dynamic_mcp_service()
    return service.get_mcp_client_by_name(mcp_name, db)

# Solution: Add MCP servers via API without code changes!
```

## System Components

### 1. **MCP Database Model** (`app/models/mcp.py`)

Stores MCP server configurations:

```python
class MCP(Base):
    id: UUID              # Unique identifier
    name: str             # Unique name (e.g., "github-mcp")
    type: str             # "stdio" | "sse" | "npm"
    command: str          # URL, command, or package name
    url: str              # HTTP endpoint (for HTTP-type servers)
    args: dict            # Command arguments
    headers: dict         # HTTP headers (for auth)
    env_vars: dict        # Environment variables
    created_at: datetime  # Creation timestamp
```

### 2. **Configuration Schema** (`app/schemas/mcp_config.py`)

Validates MCP configuration:

```python
class MCPClientConfig(BaseModel):
    server_type: str                      # "http" | "stdio" | "npm"
    endpoint: Optional[str] = None        # For HTTP servers
    command: Optional[str] = None         # For Stdio servers
    package: Optional[str] = None         # For NPM servers
    args: Optional[List[str]] = []        # Command arguments
    auth_headers: Optional[Dict] = None   # HTTP headers
    env_vars: Optional[Dict] = None       # Environment variables
    timeout: int = 300                    # Request timeout
```

### 3. **Dynamic Client Service** (`app/services/mcp_dynamic_client.py`)

**NEW** - Provides database-driven client creation:

```python
class DynamicMCPClientService:
    def get_mcp_client_by_id(mcp_id: UUID, db: Session)
    def get_mcp_client_by_name(mcp_name: str, db: Session)
    def list_all_mcp_clients(db: Session)
    def validate_mcp_config_in_db(mcp_id: UUID, db: Session)
    def clear_client_cache(mcp_id: Optional[UUID])
```

### 4. **MCP Client Factory** (`app/services/mcp_factory.py`)

Creates clients from configuration:

```python
class MCPClientFactory:
    @staticmethod
    def create(config: MCPClientConfig) -> MCPClient
    @staticmethod
    def validate_config(config: MCPClientConfig) -> tuple[bool, str]
```

## Usage Guide

### Option 1: Dynamic Database-Driven (✅ Recommended)

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service
from app.db.database import get_db

# Initialize service
service = get_dynamic_mcp_service()
db = next(get_db())

# Get client by unique name
github_client = service.get_mcp_client_by_name("github-mcp", db)

# Get client by UUID
client = service.get_mcp_client_by_id(mcp_uuid, db)

# List all MCP servers in database
all_mcps = service.list_all_mcp_clients(db)
```

### Option 2: Factory with Configuration Dict

```python
from app.services.mcp_factory import MCPClientFactory
from app.schemas.mcp_config import MCPClientConfig

# Create config
config = MCPClientConfig(
    server_type="http",
    endpoint="https://api.example.com/mcp",
    auth_headers={"Authorization": "Bearer token"},
    timeout=600
)

# Create client
client = MCPClientFactory.create(config)
```

### Option 3: Backward Compatible Hardcoded (❌ Legacy - Don't use for new code)

```python
from app.services.mcp_clients import get_github_http_mcp_client

# Still works, but now uses factory internally
client = get_github_http_mcp_client()
```

## REST API Endpoints

### 1. Register a New MCP Server

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
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. List All MCP Servers

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
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### 3. Get Specific MCP Server

```bash
curl http://localhost:8000/mcps/{mcp_id}
```

### 4. Update MCP Configuration

```bash
curl -X PUT http://localhost:8000/mcps/{mcp_id} \
  -H "Content-Type: application/json" \
  -d '{
    "headers": {
      "Authorization": "Bearer new_token"
    }
  }'
```

### 5. Delete MCP Server

```bash
curl -X DELETE http://localhost:8000/mcps/{mcp_id}
```

## Database Setup

### MCP Table Schema

```sql
CREATE TABLE mcps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,  -- enum: 'stdio', 'sse', 'npm'
    command VARCHAR(255),        -- For stdio: command path; for npm: package name
    url VARCHAR(255),            -- For HTTP/SSE: endpoint URL
    args JSON DEFAULT '{}',      -- Command arguments
    headers JSON DEFAULT '{}',   -- HTTP headers
    env_vars JSON DEFAULT '{}',  -- Environment variables
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Example Configurations

### HTTP MCP Server (GitHub Copilot)

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

### Stdio MCP Server (Local Python Script)

```json
{
  "name": "azure-mcp",
  "type": "stdio",
  "command": "/usr/bin/python3",
  "args": ["/app/mcp_servers/azure_mcp_server.py"],
  "env_vars": {
    "AZURE_CLIENT_ID": "...",
    "AZURE_TENANT_ID": "..."
  }
}
```

### NPM MCP Server (Kubernetes)

```json
{
  "name": "kubernetes-mcp",
  "type": "npm",
  "command": "mcp-server-kubernetes",
  "args": [],
  "env_vars": {
    "KUBECONFIG": "/home/user/.kube/config"
  }
}
```

## Migration Guide

### From Hardcoded to Dynamic

**Before:**
```python
# Old way - hardcoded
from app.services.mcp_clients import get_github_http_mcp_client

client = get_github_http_mcp_client()
```

**After:**
```python
# New way - database-driven
from app.services.mcp_dynamic_client import get_mcp_client_by_name
from app.db.database import get_db

db = next(get_db())
client = get_mcp_client_by_name("github-mcp", db)
```

## Performance Optimization

### Client Caching

The system automatically caches client instances:

```python
# First call: Creates and caches
client1 = service.get_mcp_client_by_name("github-mcp", db)

# Subsequent calls: Returns from cache
client2 = service.get_mcp_client_by_name("github-mcp", db)  # Instant!
```

### Clear Cache When Needed

```python
service = get_dynamic_mcp_service()

# Clear specific MCP cache
service.clear_client_cache(mcp_id)

# Clear all caches
service.clear_client_cache()
```

## Error Handling

```python
from app.services.mcp_dynamic_client import get_dynamic_mcp_service

service = get_dynamic_mcp_service()

try:
    client = service.get_mcp_client_by_name("nonexistent", db)
    if not client:
        print("MCP server not found in database")
except ValueError as e:
    print(f"Invalid MCP configuration: {e}")
except Exception as e:
    print(f"Error creating client: {e}")
```

## Troubleshooting

### Issue: "MCP not found in database"

**Solution:** Register the MCP server first via API:
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{"name": "...", "type": "...", ...}'
```

### Issue: "Invalid MCP configuration"

**Checklist:**
- ✓ For HTTP: `url` field is required
- ✓ For Stdio: `command` field is required
- ✓ For NPM: `command` field contains package name
- ✓ Environment variables exist if referenced
- ✓ Commands/binaries are in PATH

### Issue: Connection timeout

**Solution:** Adjust timeout in database configuration:
```bash
curl -X PUT http://localhost:8000/mcps/{mcp_id} \
  -H "Content-Type: application/json" \
  -d '{"timeout": 900}'  # Increase timeout in seconds
```

## Key Features

| Feature | Old (Hardcoded) | New (Dynamic) |
|---------|---|---|
| **Add new MCP** | Edit code + deploy | API call |
| **Scale** | Limited | Unlimited |
| **Configuration** | Hardcoded | Database |
| **Multi-tenancy** | No | Yes |
| **Hot-reload** | No | Yes (cache clear) |
| **Backward compat** | N/A | 100% |

## References

- **Models:** `app/models/mcp.py`
- **Schemas:** `app/schemas/mcp_config.py`, `app/schemas/mcp_schema.py`
- **Services:** `app/services/mcp_factory.py`, `app/services/mcp_dynamic_client.py`
- **API:** `app/api/mcps.py`
- **Tests:** Use `/mcps` endpoint to verify

---

**Status:** ✅ Implementation Complete
**Backward Compatibility:** ✅ 100%
**Documentation:** ✅ Complete
