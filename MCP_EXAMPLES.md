# MCP Tool Discovery - Practical Examples

## Real-World Scenarios

This document provides practical, copy-paste ready examples for common MCP tool discovery tasks.

---

## Scenario 1: GitHub MCP Server Setup

### Register GitHub MCP Server

```bash
# Get GitHub API token from: https://github.com/settings/tokens

curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "env_vars": {
      "GITHUB_TOKEN": "ghp_your_token_here"
    }
  }'

# Response includes: "id": "550e8400-e29b-41d4-a716-446655440000"
```

### Discover GitHub Tools

```bash
# Via API
curl -X POST http://localhost:8000/mcps/550e8400-e29b-41d4-a716-446655440000/discover-tools

# Via Script
python list_mcp_tools.py --mcp-name "github-mcp"

# Via Bash
./list_mcp_tools.sh --mcp-name "github-mcp"
```

### Expected Tools

```
Tool Name                          | Description
------------------------------------------------
list_repositories                  | List user/org repositories
search_repositories                | Search GitHub repositories
get_repository_content             | Get file content from repo
create_issue                       | Create a new issue
list_issues                        | List repository issues
add_issue_comment                  | Comment on an issue
```

---

## Scenario 2: Multiple MCP Servers

### Register Multiple Servers

```bash
#!/bin/bash
# register_mcps.sh - Register multiple MCP servers

# 1. GitHub MCP
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.github",
    "env_vars": {"GITHUB_TOKEN": "ghp_xxx"}
  }'

# 2. Slack MCP
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "slack-mcp",
    "type": "stdio",
    "command": "python -m mcp.server.slack",
    "env_vars": {"SLACK_BOT_TOKEN": "xoxb_xxx"}
  }'

# 3. AWS MCP (SSE-based)
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "aws-mcp",
    "type": "sse",
    "url": "http://localhost:3000/mcp",
    "headers": {
      "Authorization": "Bearer aws_token",
      "X-API-Key": "your_api_key"
    }
  }'

echo "All MCPs registered!"
```

### Discover All Tools

```bash
#!/bin/bash
# discover_all_tools.sh - Discover tools from all MCPs

echo "📋 Discovering tools from all MCP servers..."
echo ""

# Get all MCPs
mcps=$(curl -s http://localhost:8000/mcps | jq -r '.[] | "\(.id)|\(.name)"')

while IFS='|' read -r mcp_id mcp_name; do
  echo "🔍 Discovering tools from: $mcp_name"
  
  # Discover tools
  result=$(curl -s -X POST http://localhost:8000/mcps/$mcp_id/discover-tools)
  
  # Extract and display
  tool_count=$(echo "$result" | jq '.tools_count')
  echo "   Found $tool_count tools"
  
  # List tool names
  echo "$result" | jq -r '.tools | map("     - " + .name) | join("\n")'
  echo ""
done <<< "$mcps"

echo "✅ Discovery complete!"
```

### Output Example

```
📋 Discovering tools from all MCP servers...

🔍 Discovering tools from: github-mcp
   Found 5 tools
     - list_repositories
     - search_repositories
     - create_issue
     - list_issues
     - add_issue_comment

🔍 Discovering tools from: slack-mcp
   Found 3 tools
     - send_message
     - list_channels
     - get_user_info

🔍 Discovering tools from: aws-mcp
   Found 8 tools
     - list_instances
     - describe_instance
     - start_instance
     - stop_instance
     - create_snapshot
     - delete_snapshot
     - list_snapshots
     - describe_snapshot

✅ Discovery complete!
```

---

## Scenario 3: Tool Availability Monitoring

### Monitor Tool Availability

```bash
#!/bin/bash
# monitor_tools.sh - Monitor MCP tool availability

MCP_NAME="github-mcp"
CRITICAL_TOOLS=("list_repositories" "create_issue" "search_repositories")
CHECK_INTERVAL=300  # 5 minutes

while true; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking tool availability..."
  
  # Discover tools
  tools_json=$(python list_mcp_tools.py --mcp-name "$MCP_NAME" --format json)
  tools=$(echo "$tools_json" | jq -r '.tools[].name')
  
  # Check critical tools
  all_available=true
  for tool in "${CRITICAL_TOOLS[@]}"; do
    if echo "$tools" | grep -q "^$tool$"; then
      echo "  ✅ $tool: Available"
    else
      echo "  ❌ $tool: MISSING"
      all_available=false
    fi
  done
  
  if [ "$all_available" == false ]; then
    echo "⚠️  WARNING: Some critical tools are missing!"
    # Send alert (email, Slack, etc.)
  fi
  
  sleep $CHECK_INTERVAL
done
```

---

## Scenario 4: Tool Integration in Automation

### Use Tools in Workflow

```bash
#!/bin/bash
# workflow.sh - Integration example

# 1. Discover GitHub tools
echo "Step 1: Discovering GitHub tools..."
github_tools=$(python list_mcp_tools.py --mcp-name "github-mcp" --format json)

# 2. Extract specific tool info
echo "Step 2: Extracting tool schemas..."
search_tool=$(echo "$github_tools" | jq '.tools[] | select(.name == "search_repositories")')

# 3. Display tool usage
echo "Step 3: Tool details:"
echo "$search_tool" | jq '.'

# 4. Use the tool information for validation
echo "Step 4: Validating requirements..."
has_limit=$(echo "$search_tool" | jq '.inputSchema.properties | has("limit")')
has_query=$(echo "$search_tool" | jq '.inputSchema.properties | has("query")')

if [ "$has_limit" == "true" ] && [ "$has_query" == "true" ]; then
  echo "✅ Tool has required parameters"
else
  echo "❌ Tool missing required parameters"
fi
```

---

## Scenario 5: Batch Tool Export

### Export Tools to CSV

```bash
#!/bin/bash
# export_tools.sh - Export all tools to CSV

OUTPUT_FILE="mcp_tools_$(date +%Y%m%d_%H%M%S).csv"

# CSV Header
echo "MCP Name,Tool Name,Description,Required Params" > "$OUTPUT_FILE"

# Get all MCPs
mcps=$(curl -s http://localhost:8000/mcps | jq -r '.[] | "\(.id)|\(.name)"')

while IFS='|' read -r mcp_id mcp_name; do
  # Discover tools
  tools=$(curl -s -X POST http://localhost:8000/mcps/$mcp_id/discover-tools | \
    jq -r '.tools[] | "\(.name)|\(.description)|\(.inputSchema.required | join(","))"')
  
  while IFS='|' read -r tool_name description required; do
    echo "\"$mcp_name\",\"$tool_name\",\"$description\",\"$required\"" >> "$OUTPUT_FILE"
  done <<< "$tools"
done <<< "$mcps"

echo "✅ Tools exported to: $OUTPUT_FILE"
```

### Export Tools to JSON

```bash
#!/bin/bash
# export_json.sh - Export tools in structured JSON

OUTPUT_FILE="mcp_tools_$(date +%Y%m%d_%H%M%S).json"

# Initialize JSON array
echo "{" > "$OUTPUT_FILE"
echo "  \"exportDate\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$OUTPUT_FILE"
echo "  \"mcpServers\": [" >> "$OUTPUT_FILE"

mcps=$(curl -s http://localhost:8000/mcps | jq -r '.[] | "\(.id)|\(.name)"')
first=true

while IFS='|' read -r mcp_id mcp_name; do
  [ "$first" == false ] && echo "    }," >> "$OUTPUT_FILE"
  first=false
  
  echo "    {" >> "$OUTPUT_FILE"
  echo "      \"name\": \"$mcp_name\"," >> "$OUTPUT_FILE"
  echo "      \"id\": \"$mcp_id\"," >> "$OUTPUT_FILE"
  
  # Get tools
  curl -s -X POST http://localhost:8000/mcps/$mcp_id/discover-tools | \
    jq '.tools' >> "$OUTPUT_FILE"
  
done <<< "$mcps"

echo "    }" >> "$OUTPUT_FILE"
echo "  ]" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo "✅ Tools exported to: $OUTPUT_FILE"
```

---

## Scenario 6: Tool Documentation Generation

### Generate Markdown Documentation

```bash
#!/bin/bash
# generate_docs.sh - Generate tool documentation in Markdown

OUTPUT_FILE="MCP_TOOLS_REFERENCE.md"

cat > "$OUTPUT_FILE" << 'EOF'
# MCP Tools Reference

This document auto-generated at $(date)

EOF

# Get all MCPs
mcps=$(curl -s http://localhost:8000/mcps | jq -r '.[] | "\(.id)|\(.name)|\(.type)"')

while IFS='|' read -r mcp_id mcp_name mcp_type; do
  echo "## $mcp_name" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "**Type**: $mcp_type" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  
  # Discover tools
  tools=$(curl -s -X POST http://localhost:8000/mcps/$mcp_id/discover-tools | jq '.tools[]')
  
  echo "### Available Tools" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  
  while read -r tool; do
    name=$(echo "$tool" | jq -r '.name')
    desc=$(echo "$tool" | jq -r '.description')
    schema=$(echo "$tool" | jq '.inputSchema')
    
    echo "#### $name" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "$desc" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "**Input Schema**:" >> "$OUTPUT_FILE"
    echo "\`\`\`json" >> "$OUTPUT_FILE"
    echo "$schema" | jq '.' >> "$OUTPUT_FILE"
    echo "\`\`\`" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  done <<< "$tools"
  
done <<< "$mcps"

echo "✅ Documentation generated: $OUTPUT_FILE"
```

---

## Scenario 7: Caching and Performance

### Cache Refresh Strategy

```bash
#!/bin/bash
# cache_refresh.sh - Strategic cache management

MCP_NAME="github-mcp"

echo "📊 Cache Performance Report"
echo ""

# First discovery (no cache)
echo "1️⃣  First discovery (populate cache)..."
start=$(date +%s%N)
python list_mcp_tools.py --mcp-name "$MCP_NAME" > /dev/null
end=$(date +%s%N)
first_time=$((($end - $start) / 1000000))
echo "   Time: ${first_time}ms"

# Cached discovery
echo ""
echo "2️⃣  Cached discovery..."
start=$(date +%s%N)
python list_mcp_tools.py --mcp-name "$MCP_NAME" > /dev/null
end=$(date +%s%N)
cached_time=$((($end - $start) / 1000000))
echo "   Time: ${cached_time}ms"

# Refreshed discovery
echo ""
echo "3️⃣  Refreshed discovery (bypass cache)..."
start=$(date +%s%N)
python list_mcp_tools.py --mcp-name "$MCP_NAME" --refresh > /dev/null
end=$(date +%s%N)
refresh_time=$((($end - $start) / 1000000))
echo "   Time: ${refresh_time}ms"

# Summary
echo ""
echo "📈 Summary:"
echo "   First load:    ${first_time}ms"
echo "   Cached:        ${cached_time}ms ($(( first_time / cached_time ))x faster)"
echo "   Refresh:       ${refresh_time}ms"
echo ""
echo "💾 Cache saves $(( first_time - cached_time ))ms per query"
```

---

## Scenario 8: Error Handling and Recovery

### Robust Discovery Script

```bash
#!/bin/bash
# robust_discovery.sh - With error handling and retry logic

MCP_NAME="github-mcp"
MAX_RETRIES=3
RETRY_DELAY=5

discover_with_retry() {
  local mcp_name=$1
  local attempt=1
  
  while [ $attempt -le $MAX_RETRIES ]; do
    echo "Attempt $attempt/$MAX_RETRIES..."
    
    result=$(python list_mcp_tools.py --mcp-name "$mcp_name" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
      echo "✅ Success!"
      echo "$result"
      return 0
    fi
    
    if [ $attempt -lt $MAX_RETRIES ]; then
      echo "❌ Failed. Retrying in ${RETRY_DELAY}s..."
      sleep $RETRY_DELAY
    fi
    
    attempt=$((attempt + 1))
  done
  
  echo "❌ Failed after $MAX_RETRIES attempts"
  echo "$result"
  return 1
}

# Run with retry logic
discover_with_retry "$MCP_NAME"
```

---

## Scenario 9: API Integration

### Python Integration Example

```python
#!/usr/bin/env python3
# integrate_mcp_tools.py - Integrate MCP tools in Python application

import requests
import json
from typing import Dict, List

class MCPClient:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
    
    def list_mcps(self) -> List[Dict]:
        """List all registered MCP servers"""
        response = requests.get(f"{self.api_url}/mcps")
        return response.json()
    
    def discover_tools(self, mcp_id: str, refresh: bool = False) -> Dict:
        """Discover tools from MCP server"""
        url = f"{self.api_url}/mcps/{mcp_id}/discover-tools"
        params = {"refresh": refresh}
        response = requests.post(url, params=params)
        return response.json()
    
    def get_tool(self, mcp_id: str, tool_name: str) -> Dict:
        """Get specific tool details"""
        tools_data = self.discover_tools(mcp_id)
        tools = tools_data.get("tools", [])
        return next((t for t in tools if t.get("name") == tool_name), None)
    
    def validate_tool_input(self, tool: Dict, input_data: Dict) -> bool:
        """Validate input against tool schema"""
        schema = tool.get("inputSchema", {})
        required = schema.get("required", [])
        
        for field in required:
            if field not in input_data:
                return False
        return True

# Usage
client = MCPClient()

# List all MCPs
mcps = client.list_mcps()
print(f"Found {len(mcps)} MCP servers")

# Discover tools from GitHub MCP
github_mcp = next((m for m in mcps if m["name"] == "github-mcp"), None)
if github_mcp:
    tools_data = client.discover_tools(github_mcp["id"])
    print(f"Found {tools_data['tools_count']} tools")
    
    # Get specific tool
    search_tool = client.get_tool(github_mcp["id"], "search_repositories")
    print(f"Tool: {search_tool['name']}")
    print(f"Description: {search_tool['description']}")
    print(f"Schema: {json.dumps(search_tool['inputSchema'], indent=2)}")
    
    # Validate input
    test_input = {"query": "python", "language": "python"}
    is_valid = client.validate_tool_input(search_tool, test_input)
    print(f"Input valid: {is_valid}")
```

---

## Scenario 10: Integration with Cron Jobs

### Scheduled Tool Availability Check

```bash
#!/bin/bash
# cron_job.sh - Run periodic tool availability checks

# Add to crontab: 0 * * * * /path/to/cron_job.sh

LOG_FILE="/var/log/mcp_tools_check.log"
ALERT_EMAIL="admin@example.com"
MCP_SERVERS=("github-mcp" "slack-mcp" "aws-mcp")

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting MCP tools check" >> "$LOG_FILE"

failed_servers=""

for mcp_name in "${MCP_SERVERS[@]}"; do
  echo "Checking $mcp_name..." >> "$LOG_FILE"
  
  if python list_mcp_tools.py --mcp-name "$mcp_name" > /dev/null 2>&1; then
    echo "  ✅ OK" >> "$LOG_FILE"
  else
    echo "  ❌ FAILED" >> "$LOG_FILE"
    failed_servers="$failed_servers\n- $mcp_name"
  fi
done

if [ -n "$failed_servers" ]; then
  # Send alert
  message="MCP Tools Check Failed:$failed_servers"
  echo -e "$message" | mail -s "MCP Alert" "$ALERT_EMAIL"
  echo "Alert sent!" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Check complete" >> "$LOG_FILE"
```

---

## Quick Copy-Paste Commands

### List Tools Quickly
```bash
python list_mcp_tools.py --mcp-name "github-mcp"
./list_mcp_tools.sh --mcp-name "github-mcp"
```

### JSON Output
```bash
python list_mcp_tools.py --mcp-name "github-mcp" --format json | jq '.tools'
```

### List All MCPs
```bash
python list_mcp_tools.py --list-servers
```

### Force Refresh
```bash
python list_mcp_tools.py --mcp-name "github-mcp" --refresh
```

### Check Tool Exists
```bash
python list_mcp_tools.py --mcp-name "github-mcp" --format json | jq '.tools | map(.name)'
```

---

## Summary

These practical examples cover:
- ✅ Setting up MCP servers
- ✅ Discovering tools
- ✅ Monitoring availability
- ✅ Exporting documentation
- ✅ Caching strategies
- ✅ Error handling
- ✅ Integration patterns
- ✅ Automation workflows

For more information, see the other documentation files:
- `MCP_QUICK_START.md` - Quick start guide
- `MCP_TOOL_DISCOVERY.md` - Full documentation
- `MCP_API_GUIDE.md` - API reference
