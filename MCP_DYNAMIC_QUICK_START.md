# Dynamic MCP Client Factory - Quick Start

## 5-Minute Quick Start

### 1. Initialize HTTP MCP Server

```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "github-copilot",
    "config": {
      "server_type": "http",
      "endpoint": "https://api.githubcopilot.com/mcp",
      "auth_headers": {"Authorization": "Bearer ghp_token"},
      "timeout": 600
    }
  }'
```

### 2. Initialize Stdio Python Server

```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "azure-mcp",
    "config": {
      "server_type": "stdio",
      "command": "python",
      "args": ["/app/mcp_servers/azure_mcp_server.py"],
      "env_vars": {"AZURE_TENANT_ID": "xxx"},
      "timeout": 600
    }
  }'
```

### 3. Initialize NPM Package

```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "kubernetes",
    "config": {
      "server_type": "npm",
      "package": "mcp-server-kubernetes",
      "timeout": 600
    }
  }'
```

### 4. List All Clients

```bash
curl http://localhost:8000/mcps/list
```

### 5. Check Client Status

```bash
curl http://localhost:8000/mcps/github-copilot/status
```

### 6. Validate Configuration (Before Creating)

```bash
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{
    "server_type": "http",
    "endpoint": "https://api.example.com/mcp"
  }'
```

### 7. Remove Client

```bash
curl -X DELETE http://localhost:8000/mcps/github-copilot
```

## Common Configurations

### GitHub Copilot (HTTP with Auth)
```json
{
  "server_type": "http",
  "endpoint": "https://api.githubcopilot.com/mcp",
  "auth_headers": {"Authorization": "Bearer YOUR_TOKEN"},
  "timeout": 600
}
```

### Azure (Stdio Python)
```json
{
  "server_type": "stdio",
  "command": "python",
  "args": ["/app/mcp_servers/azure_mcp_server.py"],
  "env_vars": {"AZURE_TENANT_ID": "xxx"},
  "timeout": 600
}
```

### Kubernetes (NPM)
```json
{
  "server_type": "npm",
  "package": "mcp-server-kubernetes",
  "env_vars": {"KUBECONFIG": "/home/user/.kube/config"},
  "timeout": 600
}
```

### PostgreSQL (NPM)
```json
{
  "server_type": "npm",
  "package": "mcp-postgres-server",
  "env_vars": {
    "PG_HOST": "localhost",
    "PG_PORT": "5432",
    "PG_USER": "postgres",
    "PG_PASSWORD": "password",
    "PG_DATABASE": "mydb"
  },
  "timeout": 600
}
```

### Terraform (Stdio Binary)
```json
{
  "server_type": "stdio",
  "command": "/usr/bin/terraform-mcp-server",
  "timeout": 600
}
```

### GCP (NPM with Gcloud)
```json
{
  "server_type": "npm",
  "package": "@google-cloud/gcloud-mcp",
  "timeout": 600
}
```

## Configuration Rules

| Type | Required | Optional |
|------|----------|----------|
| HTTP | `endpoint` | `auth_headers`, `timeout` |
| Stdio | `command` | `args`, `env_vars`, `timeout` |
| NPM | `package` | `args`, `env_vars`, `timeout` |

## Using in Python Code

```python
from app.schemas.mcp_config import MCPClientConfig
from app.services.mcp_factory import MCPClientFactory, get_mcp_client_manager

# Method 1: Factory
config = MCPClientConfig(
    server_type="http",
    endpoint="https://api.example.com/mcp"
)
client = MCPClientFactory.create(config)

# Method 2: Manager
manager = get_mcp_client_manager()
manager.register_client("my-client", config)
client = manager.get_client("my-client")

# Method 3: Backward Compatible (old functions)
from app.services.mcp_clients import get_github_http_mcp_client
client = get_github_http_mcp_client()  # Uses factory internally
```

## API Reference

**POST /mcps/initialize** - Initialize a new MCP client
**GET /mcps/list** - List all clients
**GET /mcps/{id}/status** - Get client status
**DELETE /mcps/{id}** - Remove client
**POST /mcps/validate-config** - Validate configuration

## Error Responses

| Status | Error |
|--------|-------|
| 201 | Success - Client initialized |
| 400 | Invalid configuration |
| 404 | Client not found |
| 500 | Server error |

## Environment Variables

Pass environment variables to MCP servers via the `env_vars` config:

```json
{
  "env_vars": {
    "GITHUB_TOKEN": "ghp_xxx",
    "AZURE_TENANT_ID": "xxx",
    "KUBECONFIG": "/home/user/.kube/config"
  }
}
```

## Tips

✅ Auto-generate client IDs if not provided
✅ Validate config before creating client
✅ Reuse clients via manager for efficiency
✅ All servers support timeout configuration
✅ HTTP servers can use bearer token authentication
✅ Environment variables are passed to stdio/npm servers

## Next Steps

- Read `MCP_DYNAMIC_FACTORY.md` for complete documentation
- Check `app/schemas/mcp_config.py` for schema details
- Review `app/services/mcp_factory.py` for implementation
- See `app/api/mcp_dynamic.py` for endpoint details
