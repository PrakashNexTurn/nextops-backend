# Dynamic MCP Client Factory - Implementation Guide

## Overview

The Dynamic MCP Client Factory system replaces hardcoded MCP client functions with a flexible, configurable approach. This allows you to initialize any MCP server type dynamically from API input without modifying code.

## Key Features

✅ **Three Server Types Supported:**
- **HTTP** (streamable_http) - with optional bearer token authentication
- **Stdio** - Python scripts, local commands, binaries
- **NPM** - npm packages (kubernetes, terraform, postgres, gcp, etc.)

✅ **Dynamic Configuration** - Initialize clients via REST API
✅ **Type Validation** - Pydantic schemas ensure config correctness
✅ **Backward Compatible** - Old functions now use the factory
✅ **Error Handling** - Comprehensive logging and validation
✅ **Environment Variables** - Pass env vars to servers
✅ **Configurable Timeouts** - Per-server timeout settings

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Endpoints                         │
│  /mcps/initialize  /mcps/list  /mcps/{id}/status  etc.      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               MCPClientManager                              │
│  - register_client()  - get_client()                        │
│  - list_clients()     - unregister_client()                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               MCPClientFactory                              │
│  - create()           - validate_config()                   │
│  - _prepare_http_server()    - _prepare_stdio_server()      │
│  - _prepare_npm_server()     - _prepare_gcp_server()        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    MCP Servers                              │
│  HTTP │ Stdio │ NPM │ GCloud │ Kubernetes │ etc.           │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Schema

### MCPClientConfig (Pydantic Model)

```python
class MCPClientConfig(BaseModel):
    server_type: Literal["http", "stdio", "npm"]
    
    # HTTP-specific
    endpoint: Optional[str]
    auth_headers: Optional[Dict[str, str]]
    
    # Stdio-specific
    command: Optional[str]
    args: Optional[List[str]]
    
    # NPM-specific
    package: Optional[str]
    
    # Shared
    env_vars: Optional[Dict[str, str]]
    timeout: int = 600
```

## Usage Examples

### 1. HTTP Server with Bearer Token

```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "github-mcp",
    "config": {
      "server_type": "http",
      "endpoint": "https://api.githubcopilot.com/mcp",
      "auth_headers": {"Authorization": "Bearer ghp_token"},
      "timeout": 600
    }
  }'
```

### 2. Stdio Python Server

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

### 3. NPM Package with Environment Variables

```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "kubernetes-mcp",
    "config": {
      "server_type": "npm",
      "package": "mcp-server-kubernetes",
      "env_vars": {"KUBECONFIG": "/home/user/.kube/config"},
      "timeout": 600
    }
  }'
```

### 4. GCP MCP with Gcloud

```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "gcp-mcp",
    "config": {
      "server_type": "npm",
      "package": "@google-cloud/gcloud-mcp",
      "timeout": 600
    }
  }'
```

## API Endpoints

### POST /mcps/initialize
**Initialize a new MCP client dynamically**

**Request Body:**
```json
{
  "client_id": "optional-custom-id",
  "config": {
    "server_type": "http" | "stdio" | "npm",
    "endpoint": "...",
    "command": "...",
    "package": "...",
    "auth_headers": {...},
    "args": [...],
    "env_vars": {...},
    "timeout": 600
  }
}
```

**Response:**
```json
{
  "success": true,
  "mcp_id": "github-mcp",
  "server_type": "http",
  "endpoint_or_command": "https://api.githubcopilot.com/mcp",
  "message": "MCP client 'github-mcp' initialized successfully"
}
```

### GET /mcps/list
**List all registered MCP clients**

**Response:**
```json
{
  "total": 3,
  "servers": [
    {
      "id": "github-mcp",
      "type": "http",
      "endpoint_or_command": "https://api.githubcopilot.com/mcp"
    },
    {
      "id": "azure-mcp",
      "type": "stdio",
      "endpoint_or_command": "python /app/mcp_servers/azure_mcp_server.py"
    }
  ]
}
```

### GET /mcps/{client_id}/status
**Get status of a specific client**

**Response:**
```json
{
  "client_id": "github-mcp",
  "status": "active",
  "type": "http",
  "endpoint_or_command": "https://api.githubcopilot.com/mcp",
  "message": "Client is registered and ready"
}
```

### DELETE /mcps/{client_id}
**Unregister and remove a client**

**Response:**
```json
{
  "success": true,
  "message": "MCP client 'github-mcp' unregistered successfully"
}
```

### POST /mcps/validate-config
**Validate configuration without creating client**

**Request:**
```json
{
  "server_type": "http",
  "endpoint": "https://api.example.com/mcp",
  "timeout": 600
}
```

**Response:**
```json
{
  "valid": true,
  "error": null,
  "server_type": "http",
  "message": "Configuration is valid"
}
```

## Python Integration

### Using the Factory Directly

```python
from app.schemas.mcp_config import MCPClientConfig
from app.services.mcp_factory import MCPClientFactory

# Create configuration
config = MCPClientConfig(
    server_type="http",
    endpoint="https://api.githubcopilot.com/mcp",
    auth_headers={"Authorization": "Bearer token"},
    timeout=600
)

# Create client
client_func = MCPClientFactory.create(config)

# Use client
async with MCPClient(client_func) as client:
    tools = await client.list_tools()
```

### Using the Manager

```python
from app.services.mcp_factory import get_mcp_client_manager
from app.schemas.mcp_config import MCPClientConfig

manager = get_mcp_client_manager()

# Register a client
config = MCPClientConfig(
    server_type="stdio",
    command="python",
    args=["/app/mcp_servers/azure_mcp_server.py"]
)
success, error = manager.register_client("azure-mcp", config)

# Get client
client_func = manager.get_client("azure-mcp")

# List clients
clients = manager.list_clients()

# Unregister
manager.unregister_client("azure-mcp")
```

### Backward Compatibility

```python
# Old code still works!
from app.services.mcp_clients import (
    get_github_http_mcp_client,
    get_azure_mcp,
    get_kubernetes_mcp
)

# These now use the factory internally
github_client = get_github_http_mcp_client()
azure_client = get_azure_mcp()
k8s_client = get_kubernetes_mcp()
```

## Validation Rules

### HTTP Server
- Required: `endpoint`
- Optional: `auth_headers`, `timeout`

### Stdio Server
- Required: `command`
- Optional: `args`, `env_vars`, `timeout`
- Command must be valid executable or Python script

### NPM Server
- Required: `package`
- Optional: `args`, `env_vars`, `timeout`

## Supported Server Types

| Type | Package/Command | Auth | Example |
|------|-----------------|------|---------|
| HTTP | N/A | Bearer Token | GitHub Copilot, ExaAI |
| Stdio | Python | Env Vars | Azure, ServiceNow |
| NPM | kubernetes | Env Vars | Kubernetes |
| NPM | terraform | Env Vars | Terraform |
| NPM | postgres | Env Vars | PostgreSQL |
| NPM | @google-cloud/gcloud-mcp | Gcloud | GCP |

## Error Handling

### Configuration Errors
```json
{
  "detail": "Invalid MCP configuration: 'endpoint' is required when server_type='http'"
}
```

### Registration Errors
```json
{
  "detail": "Failed to initialize MCP client: Command 'python' not found in PATH"
}
```

### Not Found
```json
{
  "detail": "MCP client not found: github-mcp"
}
```

## Testing

### Test HTTP Client
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test-http",
    "config": {
      "server_type": "http",
      "endpoint": "https://mcp.exa.ai/mcp"
    }
  }'
```

### Validate Configuration
```bash
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{
    "server_type": "http",
    "endpoint": "https://api.example.com/mcp"
  }'
```

### List Clients
```bash
curl http://localhost:8000/mcps/list
```

## Migration from Hardcoded Functions

### Before (Hardcoded)
```python
def get_github_http_mcp_client():
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
    return MCPClient(lambda: streamablehttp_client(
        url="https://api.githubcopilot.com/mcp",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        timeout=600
    ))
```

### After (Dynamic)
```python
# Via API
curl -X POST /mcps/initialize -d '{
  "config": {
    "server_type": "http",
    "endpoint": "https://api.githubcopilot.com/mcp",
    "auth_headers": {"Authorization": "Bearer $GITHUB_TOKEN"}
  }
}'

# Or programmatically
config = MCPClientConfig(
    server_type="http",
    endpoint="https://api.githubcopilot.com/mcp",
    auth_headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
)
client = MCPClientFactory.create(config)
```

## Files Created/Modified

| File | Purpose |
|------|---------|
| `app/schemas/mcp_config.py` | Pydantic schemas for configuration |
| `app/services/mcp_factory.py` | Factory implementation & manager |
| `app/services/mcp_clients.py` | Backward-compatible functions |
| `app/api/mcp_dynamic.py` | FastAPI endpoints |

## Environment Variables

### HTTP Servers
- `GITHUB_TOKEN` - For GitHub Copilot API

### Stdio Servers
- Any environment variables needed by the server script

### NPM Servers
- `KUBECONFIG` - For Kubernetes
- `PG_*` - For PostgreSQL
- `GOOGLE_APPLICATION_CREDENTIALS` - For GCP
- `AZURE_*` - For Azure

## Performance Considerations

- **Connection Pooling**: HTTP clients maintain persistent connections
- **Timeout Management**: Each server has configurable timeout
- **Memory**: Clients are cached in manager for reuse
- **Process Management**: Stdio processes started on demand

## Security Best Practices

1. **Never hardcode tokens** - Use environment variables
2. **Validate input** - Configuration is validated before use
3. **Limited file access** - Only specified paths can be executed
4. **Environment isolation** - Each server has isolated env vars
5. **Bearer tokens** - Passed securely via auth headers

## Troubleshooting

### "Command not found"
```bash
# Ensure command is in PATH
which python  # or other command
```

### "ModuleNotFoundError"
```bash
# For stdio Python servers, ensure pythonpath includes project root
export PYTHONPATH=/app:$PYTHONPATH
```

### "Timeout"
```bash
# Increase timeout in config
{
  "timeout": 1200  # 20 minutes
}
```

### "Authorization Failed"
```bash
# Check auth headers format
{
  "auth_headers": {
    "Authorization": "Bearer ghp_xxxx"  # Correct format
  }
}
```

## Summary

The Dynamic MCP Client Factory provides a scalable, flexible solution for managing multiple MCP servers without code changes. All initialization is now configurable via REST API, maintaining full backward compatibility with existing code.
