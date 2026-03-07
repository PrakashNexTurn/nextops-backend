# Dynamic MCP Client Factory - curl Examples

Collection of ready-to-use curl commands for testing and using the Dynamic MCP Client Factory API.

## 1. HTTP Server Examples

### 1.1 Initialize ExaAI HTTP Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "exaai-mcp",
    "config": {
      "server_type": "http",
      "endpoint": "https://mcp.exa.ai/mcp",
      "timeout": 600
    }
  }'
```

### 1.2 Initialize GitHub Copilot with Bearer Token
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "github-copilot",
    "config": {
      "server_type": "http",
      "endpoint": "https://api.githubcopilot.com/mcp",
      "auth_headers": {
        "Authorization": "Bearer ghp_YOUR_TOKEN_HERE"
      },
      "timeout": 600
    }
  }'
```

### 1.3 Initialize HTTP Server with Custom Timeout
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "custom-http",
    "config": {
      "server_type": "http",
      "endpoint": "https://api.example.com/mcp",
      "auth_headers": {
        "Authorization": "Bearer custom_token",
        "X-Custom-Header": "value"
      },
      "timeout": 1200
    }
  }'
```

## 2. Stdio Server Examples

### 2.1 Initialize Azure Python Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "azure-mcp",
    "config": {
      "server_type": "stdio",
      "command": "python",
      "args": ["/app/mcp_servers/azure_mcp_server.py"],
      "env_vars": {
        "AZURE_TENANT_ID": "your-tenant-id",
        "AZURE_SUBSCRIPTION_ID": "your-subscription-id",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_CLIENT_SECRET": "your-client-secret"
      },
      "timeout": 600
    }
  }'
```

### 2.2 Initialize ServiceNow Python Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "servicenow-mcp",
    "config": {
      "server_type": "stdio",
      "command": "python",
      "args": ["/app/mcp_servers/servicenow_mcp_server.py"],
      "env_vars": {
        "SERVICENOW_INSTANCE": "your-instance.service-now.com",
        "SERVICENOW_USERNAME": "your-username",
        "SERVICENOW_PASSWORD": "your-password"
      },
      "timeout": 600
    }
  }'
```

### 2.3 Initialize Terraform MCP Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "terraform-mcp",
    "config": {
      "server_type": "stdio",
      "command": "/usr/bin/terraform-mcp-server",
      "timeout": 600
    }
  }'
```

### 2.4 Initialize Custom Python Script
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "custom-python",
    "config": {
      "server_type": "stdio",
      "command": "python",
      "args": ["/path/to/custom/server.py", "--config", "/path/to/config.yml"],
      "env_vars": {
        "CUSTOM_VAR1": "value1",
        "CUSTOM_VAR2": "value2"
      },
      "timeout": 600
    }
  }'
```

## 3. NPM Package Examples

### 3.1 Initialize Kubernetes NPM Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "kubernetes-mcp",
    "config": {
      "server_type": "npm",
      "package": "mcp-server-kubernetes",
      "env_vars": {
        "KUBECONFIG": "/home/user/.kube/config"
      },
      "timeout": 600
    }
  }'
```

### 3.2 Initialize PostgreSQL NPM Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "postgres-mcp",
    "config": {
      "server_type": "npm",
      "package": "mcp-postgres-server",
      "env_vars": {
        "PG_HOST": "localhost",
        "PG_PORT": "5432",
        "PG_USER": "postgres",
        "PG_PASSWORD": "your-password",
        "PG_DATABASE": "your-database"
      },
      "timeout": 600
    }
  }'
```

### 3.3 Initialize Terraform NPM Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "terraform-npm",
    "config": {
      "server_type": "npm",
      "package": "mcp-server-terraform",
      "args": ["--config", "/path/to/terraform"],
      "timeout": 600
    }
  }'
```

### 3.4 Initialize GCP Gcloud NPM Server
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "gcp-mcp",
    "config": {
      "server_type": "npm",
      "package": "@google-cloud/gcloud-mcp",
      "env_vars": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
        "CLOUDSDK_CORE_PROJECT": "your-project-id"
      },
      "timeout": 600
    }
  }'
```

## 4. Management Commands

### 4.1 List All Registered MCP Clients
```bash
curl http://localhost:8000/mcps/list
```

**Expected Response:**
```json
{
  "total": 3,
  "servers": [
    {
      "id": "github-copilot",
      "type": "http",
      "endpoint_or_command": "https://api.githubcopilot.com/mcp"
    },
    {
      "id": "azure-mcp",
      "type": "stdio",
      "endpoint_or_command": "python /app/mcp_servers/azure_mcp_server.py"
    },
    {
      "id": "kubernetes-mcp",
      "type": "npm",
      "endpoint_or_command": "mcp-server-kubernetes"
    }
  ]
}
```

### 4.2 Get Status of Specific Client
```bash
curl http://localhost:8000/mcps/github-copilot/status
```

**Expected Response:**
```json
{
  "client_id": "github-copilot",
  "status": "active",
  "type": "http",
  "endpoint_or_command": "https://api.githubcopilot.com/mcp",
  "message": "Client is registered and ready"
}
```

### 4.3 Remove/Unregister Client
```bash
curl -X DELETE http://localhost:8000/mcps/github-copilot
```

**Expected Response:**
```json
{
  "success": true,
  "message": "MCP client 'github-copilot' unregistered successfully"
}
```

## 5. Configuration Validation Examples

### 5.1 Validate HTTP Configuration
```bash
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{
    "server_type": "http",
    "endpoint": "https://api.example.com/mcp",
    "timeout": 600
  }'
```

### 5.2 Validate Stdio Configuration
```bash
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{
    "server_type": "stdio",
    "command": "python",
    "args": ["/app/server.py"],
    "timeout": 600
  }'
```

### 5.3 Validate NPM Configuration
```bash
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{
    "server_type": "npm",
    "package": "mcp-server-kubernetes",
    "timeout": 600
  }'
```

## 6. Error Handling Examples

### 6.1 Missing Required Field
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "server_type": "http"
    }
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid MCP configuration: 'endpoint' is required when server_type='http'"
}
```

### 6.2 Invalid Server Type
```bash
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "server_type": "invalid",
      "endpoint": "https://api.example.com"
    }
  }'
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "config", "server_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

### 6.3 Client Not Found
```bash
curl http://localhost:8000/mcps/nonexistent/status
```

**Response (404 Not Found):**
```json
{
  "detail": "MCP client not found: nonexistent"
}
```

## 7. Using jq for Pretty Output

### 7.1 List Clients with Pretty Output
```bash
curl http://localhost:8000/mcps/list | jq .
```

### 7.2 Extract Just the Server IDs
```bash
curl http://localhost:8000/mcps/list | jq '.servers[].id'
```

### 7.3 Format as Table
```bash
curl http://localhost:8000/mcps/list | jq '.servers | .[] | "\(.id) (\(.type)): \(.endpoint_or_command)"'
```

## 8. Batch Operations

### 8.1 Initialize Multiple Clients
```bash
#!/bin/bash

CLIENTS=(
  'github-copilot|http|https://api.githubcopilot.com/mcp'
  'kubernetes|npm|mcp-server-kubernetes'
  'postgres|npm|mcp-postgres-server'
)

for client in "${CLIENTS[@]}"; do
  IFS='|' read -r id type endpoint <<< "$client"
  echo "Initializing $id ($type)..."
  
  if [ "$type" = "http" ]; then
    curl -X POST http://localhost:8000/mcps/initialize \
      -H "Content-Type: application/json" \
      -d "{
        \"client_id\": \"$id\",
        \"config\": {
          \"server_type\": \"$type\",
          \"endpoint\": \"$endpoint\"
        }
      }"
  fi
done
```

### 8.2 Remove All Clients
```bash
#!/bin/bash

# Get all client IDs
CLIENTS=$(curl -s http://localhost:8000/mcps/list | jq -r '.servers[].id')

# Remove each client
for client_id in $CLIENTS; do
  echo "Removing $client_id..."
  curl -X DELETE http://localhost:8000/mcps/$client_id
done
```

## 9. Advanced Examples

### 9.1 Using Environment Variables
```bash
# Set auth token
export AUTH_TOKEN="ghp_YOUR_TOKEN"
export CLIENT_ID="github-$(date +%s)"

curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": \"$CLIENT_ID\",
    \"config\": {
      \"server_type\": \"http\",
      \"endpoint\": \"https://api.githubcopilot.com/mcp\",
      \"auth_headers\": {
        \"Authorization\": \"Bearer $AUTH_TOKEN\"
      }
    }
  }"
```

### 9.2 Read Configuration from File
```bash
# config.json
{
  "server_type": "stdio",
  "command": "python",
  "args": ["/app/mcp_servers/azure_mcp_server.py"],
  "env_vars": {
    "AZURE_TENANT_ID": "xxx"
  }
}

# Use with curl
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": \"azure-from-file\",
    \"config\": $(cat config.json)
  }"
```

### 9.3 Store and Reuse Response
```bash
# Initialize and save response
RESPONSE=$(curl -s -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "server_type": "http",
      "endpoint": "https://api.example.com/mcp"
    }
  }')

# Extract client ID
CLIENT_ID=$(echo $RESPONSE | jq -r '.mcp_id')

# Check status using the ID
curl http://localhost:8000/mcps/$CLIENT_ID/status

# Remove using the ID
curl -X DELETE http://localhost:8000/mcps/$CLIENT_ID
```

## Tips & Tricks

✅ **Use -s flag** for silent mode (no progress bar)
✅ **Use -w "%{http_code}\n"** to see HTTP status code
✅ **Use -v** for verbose output (headers, body, etc.)
✅ **Pipe to jq** for pretty JSON formatting
✅ **Store in variables** for dynamic values
✅ **Use environment variables** for secrets
✅ **Test with -X OPTIONS** to see CORS headers

## Testing with Postman

1. Create new request collection
2. Import these curl examples
3. Set Postman variables for auth tokens
4. Test all endpoints
5. Export results

Or import this cURL collection directly into Postman!
