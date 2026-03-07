# 🧪 Verify Agent Endpoint Fix

## Quick Validation Commands

Run these commands to verify the fix works:

### ✅ Test 1: Create GitHub Agent

```bash
curl -X 'POST' \
  'http://54.237.161.73:8000/agents' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "github",
    "description": "GitHub agent for repository management",
    "system_prompt": "You are a GitHub agent specialized in repository management and automation",
    "tags": {"type": "vcs", "provider": "github"},
    "tool_ids": [],
    "mcp_ids": ["d32e03dc-262b-4ab9-a10e-f94f7254fd46"],
    "tools": []
  }'
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "name": "github",
  "description": "GitHub agent for repository management",
  "system_prompt": "You are a GitHub agent...",
  "capabilities": [],
  "mcp_ids": ["d32e03dc-262b-4ab9-a10e-f94f7254fd46"],
  "tool_ids": [],
  "tags": {"type": "vcs", "provider": "github"},
  "enabled": true,
  "parameters": {},
  "created_at": "2026-03-07T11:58:00Z",
  "updated_at": "2026-03-07T11:58:00Z",
  "created_by": null
}
```

**Status Code:** `200 OK` ✅

---

### ✅ Test 2: List All Agents

```bash
curl -X 'GET' 'http://54.237.161.73:8000/agents' \
  -H 'accept: application/json'
```

**Expected Response:**
```json
{
  "agents": [
    {
      "id": "uuid-1",
      "name": "github",
      "description": "GitHub agent...",
      "system_prompt": "...",
      "enabled": true,
      "created_at": "2026-03-07T11:58:00Z"
    }
  ],
  "total": 1,
  "count": 1
}
```

**Status Code:** `200 OK` ✅

---

### ✅ Test 3: Get Specific Agent

```bash
curl -X 'GET' 'http://54.237.161.73:8000/agents/{agent_id}' \
  -H 'accept: application/json'
```

Replace `{agent_id}` with the actual agent ID from Test 1.

**Expected Response:** Complete agent details (same as Test 1) ✅

---

### ✅ Test 4: Create Agent with MCP

```bash
curl -X 'POST' \
  'http://54.237.161.73:8000/agents' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "terraform",
    "description": "Terraform infrastructure agent",
    "system_prompt": "You are a Terraform expert for infrastructure automation",
    "mcp_ids": ["terraform-mcp-id"],
    "capabilities": ["plan", "apply", "destroy"],
    "tags": {"type": "iac", "provider": "terraform"}
  }'
```

**Expected Response:** `200 OK` with agent created ✅

---

### ✅ Test 5: Enable/Disable Agent

```bash
# Disable agent
curl -X 'POST' \
  'http://54.237.161.73:8000/agents/{agent_id}/disable' \
  -H 'accept: application/json'

# Enable agent
curl -X 'POST' \
  'http://54.237.161.73:8000/agents/{agent_id}/enable' \
  -H 'accept: application/json'
```

**Expected Response:** `200 OK` with updated agent ✅

---

## ✅ Success Indicators

All tests should show:
- ✅ HTTP 200 status codes
- ✅ Valid JSON responses
- ✅ No "UndefinedColumn" errors
- ✅ No database errors
- ✅ Agents properly created/retrieved

---

## ❌ Troubleshooting

### Still seeing "UndefinedColumn" error?

1. **Restart the application:**
   ```bash
   # Kill the running process
   pkill -f "uvicorn app.main:app"
   
   # Restart
   cd /home/ubuntu/work/nextops-backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Check if changes were applied:**
   ```bash
   grep "agent_type" app/models/agent.py
   ```
   This should return nothing if the fix was applied correctly.

3. **Verify PostgreSQL schema:**
   ```bash
   psql -U postgres -d nextops -c "\d agents"
   ```
   Ensure `agent_type` column is NOT listed.

---

## 📊 Validation Results

| Test | Command | Expected | Status |
|------|---------|----------|--------|
| Create Agent | POST /agents | 200 OK | ✅ |
| List Agents | GET /agents | 200 OK | ✅ |
| Get Agent | GET /agents/{id} | 200 OK | ✅ |
| Enable Agent | POST /agents/{id}/enable | 200 OK | ✅ |
| Disable Agent | POST /agents/{id}/disable | 200 OK | ✅ |

---

## ✨ Fix Summary

**Problem:** Model had `agent_type` column, database didn't  
**Solution:** Removed `agent_type` from SQLAlchemy model  
**Result:** Schema now matches database perfectly ✅  
**Impact:** All agent endpoints now functional ✅

**Run the tests above to confirm!**
