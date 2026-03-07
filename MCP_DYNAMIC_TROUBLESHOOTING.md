# Dynamic MCP Client Factory - Troubleshooting Guide

## Common Issues and Solutions

### 1. Configuration Validation Errors

#### Error: "endpoint' is required when server_type='http'"
**Problem:** Missing endpoint for HTTP server
**Solution:**
```json
{
  "server_type": "http",
  "endpoint": "https://api.example.com/mcp"  ← Add this
}
```

#### Error: "'command' is required when server_type='stdio'"
**Problem:** Missing command for Stdio server
**Solution:**
```json
{
  "server_type": "stdio",
  "command": "python",  ← Add this
  "args": ["/path/to/server.py"]
}
```

#### Error: "'package' is required when server_type='npm'"
**Problem:** Missing package name for NPM server
**Solution:**
```json
{
  "server_type": "npm",
  "package": "mcp-server-kubernetes"  ← Add this
}
```

---

### 2. Command Not Found Errors

#### Error: "Command 'python' not found in PATH"
**Problem:** Python interpreter not found
**Solutions:**

```bash
# Option 1: Use absolute path
{
  "command": "/usr/bin/python3"
}

# Option 2: Add to PATH
export PATH="/usr/bin:$PATH"

# Option 3: Use which to find path
which python3
# /usr/bin/python3
{
  "command": "/usr/bin/python3"
}
```

#### Error: "Command 'npx' not found"
**Problem:** Node.js/npm not installed
**Solutions:**

```bash
# Option 1: Install Node.js
sudo apt-get install nodejs npm

# Option 2: Use absolute path if installed elsewhere
which npx
{
  "command": "/path/to/npx"
}

# Option 3: Check if in PATH
echo $PATH
```

---

### 3. Connection/Timeout Issues

#### Error: "Connection timeout"
**Problem:** Server taking too long or not responding
**Solution:**

```json
{
  "timeout": 1200  ← Increase from default 600
}
```

#### Error: "Connection refused"
**Problem:** Server not running or wrong port
**Solutions:**

```bash
# For HTTP servers, test endpoint
curl https://api.example.com/mcp

# For Stdio servers, test command
python /path/to/server.py

# Check port if applicable
netstat -tuln | grep 3000
```

---

### 4. Authentication Issues

#### Error: "401 Unauthorized"
**Problem:** Invalid or missing bearer token
**Solution:**

```bash
# Verify token
export TOKEN="ghp_YOUR_TOKEN"

# Test with curl
curl -H "Authorization: Bearer $TOKEN" https://api.githubcopilot.com/mcp

# Fix configuration
{
  "server_type": "http",
  "endpoint": "https://api.githubcopilot.com/mcp",
  "auth_headers": {
    "Authorization": "Bearer ghp_YOUR_TOKEN"
  }
}
```

#### Error: "403 Forbidden"
**Problem:** Token lacks required permissions
**Solution:**

```bash
# Generate new token with required scopes
# For GitHub: repo, gist, workflow scopes

# For Azure: Ensure service principal has required roles
az role assignment create --assignee <client-id> --role "Contributor"

# Test permissions
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/mcp/health
```

---

### 5. Environment Variable Issues

#### Error: "KeyError: 'AZURE_TENANT_ID'"
**Problem:** Required environment variable not set
**Solution:**

```json
{
  "env_vars": {
    "AZURE_TENANT_ID": "your-tenant-id",
    "AZURE_CLIENT_ID": "your-client-id",
    "AZURE_CLIENT_SECRET": "your-secret"
  }
}
```

#### Error: "env_vars are empty"
**Problem:** Variables not passed to server
**Solution:**

```bash
# Verify env_vars in configuration
curl http://localhost:8000/mcps/azure/status | jq .

# Set environment before testing
export AZURE_TENANT_ID="your-id"

# Configuration
{
  "env_vars": {
    "AZURE_TENANT_ID": "your-id"  ← Must be explicit
  }
}
```

---

### 6. Database/Connection Issues

#### Error: "PG_HOST not set for PostgreSQL"
**Problem:** Missing PostgreSQL configuration
**Solution:**

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
  }
}
```

#### Error: "KUBECONFIG not found"
**Problem:** Kubernetes config file missing
**Solution:**

```bash
# Find kubeconfig
ls ~/.kube/config

# Set environment
export KUBECONFIG="/home/user/.kube/config"

# Configuration
{
  "server_type": "npm",
  "package": "mcp-server-kubernetes",
  "env_vars": {
    "KUBECONFIG": "/home/user/.kube/config"
  }
}
```

---

### 7. Process/Runtime Issues

#### Error: "ModuleNotFoundError: No module named 'X'"
**Problem:** Python dependency not installed
**Solution:**

```bash
# Install dependencies
pip install -r requirements.txt

# Or specific package
pip install package-name

# Verify installation
python -c "import package_name"

# Check PYTHONPATH if script is in non-standard location
export PYTHONPATH="/app:/app/mcp_servers:$PYTHONPATH"
```

#### Error: "Permission denied" when running script
**Problem:** Script not executable or wrong permissions
**Solution:**

```bash
# Make script executable
chmod +x /path/to/server.py

# Check permissions
ls -la /path/to/server.py
# Should show: -rwxr-xr-x

# Or use python interpreter explicitly
{
  "command": "python",
  "args": ["/path/to/server.py"]
}
```

---

### 8. API Response Issues

#### Error: "422 Unprocessable Entity"
**Problem:** Invalid JSON or schema violation
**Solution:**

```bash
# Check JSON syntax
echo '{"server_type": "http", "endpoint": "..."}' | jq .

# Validate against schema
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{...your config...}'

# Common issues:
# - Missing closing brace
# - Unquoted strings
# - Invalid enum values
```

#### Error: "404 Client not found"
**Problem:** Client ID doesn't exist
**Solution:**

```bash
# List all clients to find IDs
curl http://localhost:8000/mcps/list | jq '.servers[].id'

# Use correct ID
curl http://localhost:8000/mcps/CORRECT_ID/status
```

#### Error: "500 Internal Server Error"
**Problem:** Server-side error
**Solution:**

```bash
# Check server logs
tail -f app.log

# Validate configuration first
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{...config...}'

# Try with simpler config
{
  "server_type": "http",
  "endpoint": "https://httpbin.org/status/200"
}
```

---

### 9. Testing and Debugging

#### How to Debug Configuration Issues

```bash
# Step 1: Validate configuration
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{
    "server_type": "stdio",
    "command": "python",
    "args": ["/app/server.py"]
  }'

# Step 2: Test command directly
python /app/server.py

# Step 3: Try initialization with verbose output
curl -v -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{...config...}'

# Step 4: Check server logs
tail -100 /var/log/app.log
```

#### How to Debug Connection Issues

```bash
# For HTTP servers
curl -v https://api.example.com/mcp
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/mcp

# For Stdio servers
/usr/bin/python /path/to/server.py
echo $?  # Check exit code

# Check if server is listening (if TCP)
netstat -tuln | grep LISTEN
```

---

### 10. Performance Issues

#### Server is slow/timing out
**Problem:** Server performance or network latency
**Solutions:**

```json
{
  "timeout": 1200  ← Increase timeout
}
```

```bash
# For network issues
ping api.example.com
traceroute api.example.com

# For server performance
top  # Check CPU/memory
ps aux | grep server

# For I/O issues
iostat -x 1
```

#### Too many clients causing memory issues
**Problem:** Creating too many long-lived connections
**Solution:**

```bash
# Monitor memory
free -h

# Remove unused clients
curl -X DELETE http://localhost:8000/mcps/old-client-id

# List and cleanup
curl http://localhost:8000/mcps/list | jq '.servers[] | select(.created_at < "2024-01-01")'
```

---

## Quick Diagnostic Checklist

When something isn't working, check:

- [ ] Configuration is valid JSON
- [ ] All required fields are present for server type
- [ ] Command/endpoint/package exists and is accessible
- [ ] Authorization tokens are valid and not expired
- [ ] Environment variables are set correctly
- [ ] File paths are absolute (not relative)
- [ ] Required dependencies are installed
- [ ] Network connectivity exists (for HTTP servers)
- [ ] Ports are not already in use (for Stdio servers)
- [ ] Logs show actual error message (not just timeout)

---

## Getting Detailed Error Information

### Enable Verbose Logging

```python
# In app/services/mcp_factory.py
import logging
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

### Check API Responses Carefully

```bash
# See full error response
curl -X POST http://localhost:8000/mcps/initialize \
  -H "Content-Type: application/json" \
  -d '{...config...}' | jq '.detail'

# Check validation errors
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{...config...}' | jq .
```

### Test Components Individually

```bash
# Test HTTP endpoint
curl https://api.example.com/mcp

# Test Stdio command
/usr/bin/python /path/to/server.py

# Test environment variables
echo $AZURE_TENANT_ID
echo $KUBECONFIG
```

---

## Getting Help

**Issue:** Configuration error
→ Review `MCP_DYNAMIC_QUICK_START.md` section on Common Configurations

**Issue:** API usage
→ Check `MCP_DYNAMIC_CURL_EXAMPLES.md` for similar example

**Issue:** Implementation question
→ Read `MCP_DYNAMIC_FACTORY.md` Architecture section

**Issue:** Still stuck?
→ Check server logs and error message carefully
→ Try simpler configuration first
→ Test individual components separately

---

## Useful Commands

```bash
# List all clients
curl http://localhost:8000/mcps/list

# Validate configuration
curl -X POST http://localhost:8000/mcps/validate-config \
  -H "Content-Type: application/json" \
  -d '{...}'

# Check single client
curl http://localhost:8000/mcps/CLIENT_ID/status

# Get pretty JSON output
curl http://localhost:8000/mcps/list | jq .

# Extract just IDs
curl http://localhost:8000/mcps/list | jq '.servers[].id'

# Watch for changes
watch -n 1 'curl -s http://localhost:8000/mcps/list | jq .'

# Test with different methods
curl -X OPTIONS http://localhost:8000/mcps/initialize -v
```

---

## Common Success Signs

- ✅ Configuration validates successfully
- ✅ Client initializes with status 201
- ✅ Client appears in list
- ✅ Status check returns "active"
- ✅ Proper error messages (not 500)
- ✅ Logs show successful operations

---

**Remember:** Most issues are configuration-related. Always validate before creating, and test individual components separately!
