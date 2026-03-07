# ⚡ QUICK START - DYNAMIC AGENT MANAGEMENT

## **In 60 Seconds**

### **Before (Old Way - Hardcoded)**
```python
# ❌ Had to write agent code
# ❌ Had to change Python files
# ❌ Had to redeploy
# ❌ System prompts hardcoded
# ❌ MCPs hardcoded
```

### **After (New Way - Dynamic)**
```
✅ Create agent via API
✅ Agent immediately available
✅ No code changes
✅ System prompts from database
✅ MCPs from database
✅ Tools auto-discovered
```

---

## **3-Step Workflow**

### **Step 1: Create Agent** (30 sec)
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Terraform Agent",
    "description": "Deploy infrastructure",
    "system_prompt": "You are a Terraform expert. Help users deploy cloud infrastructure safely.",
    "agent_type": "terraform",
    "mcp_ids": ["terraform-mcp"],
    "enabled": true
  }'
```

### **Step 2: Agent in Database** (instant)
```
✅ Agent stored with:
   - System prompt from your API call
   - MCPs from your API call
   - Tools auto-discovered from terraform-mcp
   - Everything stored in database
```

### **Step 3: Bedrock Uses It** (automatic)
```python
# On next Bedrock invocation:
factory = AgentFactory(db)
agents = await factory.create_agents_from_database(...)

# agents now includes:
# ✅ Terraform Agent with system_prompt from database
# ✅ All Terraform tools auto-discovered
# ✅ Ready to use immediately
```

---

## **Common Operations**

### **List All Agents**
```bash
curl http://localhost:8000/agents
```

### **Get Specific Agent**
```bash
curl http://localhost:8000/agents/{agent_id}
```

### **Update Agent's System Prompt**
```bash
curl -X PUT http://localhost:8000/agents/{agent_id} \
  -d '{
    "system_prompt": "New prompt here..."
  }'
```

### **Add MCP to Agent**
```bash
curl -X POST http://localhost:8000/agents/{agent_id}/mcps/{mcp_id}
# ✅ All MCP tools automatically linked!
```

### **Remove MCP from Agent**
```bash
curl -X DELETE http://localhost:8000/agents/{agent_id}/mcps/{mcp_id}
# ✅ All MCP tools automatically removed!
```

### **Enable/Disable Agent**
```bash
# Enable
curl -X POST http://localhost:8000/agents/{agent_id}/enable

# Disable (keeps in database, won't load)
curl -X POST http://localhost:8000/agents/{agent_id}/disable
```

### **Delete Agent**
```bash
curl -X DELETE http://localhost:8000/agents/{agent_id}
```

---

## **Key Features**

| Feature | Before | After |
|---------|--------|-------|
| **Add Agent** | Code + redeploy (2h) | API call (30s) |
| **System Prompt** | Hardcoded | Database |
| **MCPs** | Hardcoded | Database |
| **Tools** | Hardcoded | Auto-discovered |
| **Update** | Code change + redeploy | API call |
| **Enable/Disable** | Delete/redeploy | API toggle |
| **Code Changes** | Per agent | Zero |

---

## **Database Schema**

### **agents table**
```
id              → Agent UUID
name            → Agent name
description     → What agent does
system_prompt   → ✅ Agent's instructions (FROM DATABASE)
agent_type      → Type (terraform, azure, etc.)
mcp_ids         → ✅ List of MCPs (FROM DATABASE)
tool_ids        → ✅ Auto-discovered tools
tags            → Custom tags
capabilities    → What agent can do
parameters      → Custom config
enabled         → On/off flag
created_at      → Creation time
updated_at      → Last update
```

---

## **API Quick Reference**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/agents` | Create agent |
| GET | `/agents` | List agents |
| GET | `/agents/{id}` | Get agent |
| PUT | `/agents/{id}` | Update agent |
| DELETE | `/agents/{id}` | Delete agent |
| POST | `/agents/{id}/enable` | Enable agent |
| POST | `/agents/{id}/disable` | Disable agent |
| POST | `/agents/{id}/mcps/{mcp}` | Add MCP |
| DELETE | `/agents/{id}/mcps/{mcp}` | Remove MCP |
| GET | `/agents/{id}/mcps` | List MCPs |

---

## **Example Agents**

### **Terraform Agent**
```json
{
  "name": "Terraform Agent",
  "system_prompt": "You are a Terraform expert...",
  "mcp_ids": ["terraform-mcp"],
  "enabled": true
}
```

### **Azure Agent**
```json
{
  "name": "Azure Agent",
  "system_prompt": "You are an Azure architect...",
  "mcp_ids": ["azure-mcp"],
  "enabled": true
}
```

### **Multi-Cloud Agent**
```json
{
  "name": "Multi-Cloud Agent",
  "system_prompt": "You manage multiple clouds...",
  "mcp_ids": ["terraform-mcp", "azure-mcp", "aws-mcp"],
  "enabled": true
}
```

---

## **What Happens Automatically**

```
You create agent with mcp_ids: ["terraform-mcp"]
              ↓
System finds terraform-mcp in database
              ↓
Gets all tools from terraform-mcp
    (plan, apply, destroy, import, validate, ...)
              ↓
Links all tools to your agent automatically
              ↓
Stores association in agent_tools table
              ↓
Returns complete tool_ids list
              ↓
✅ Agent ready with all tools!

NO MANUAL CONFIGURATION NEEDED!
```

---

## **Status Indicators**

### ✅ **System is Production Ready**
- ✅ All models implemented
- ✅ All API endpoints working
- ✅ Database schema ready
- ✅ Services fully functional
- ✅ Bedrock integration complete
- ✅ Zero hardcoding
- ✅ Fully documented

### ✅ **You Can Start Using It Today**
1. Run database migrations
2. Create agents via API
3. Bedrock loads them automatically
4. Done!

---

## **Remember**

```
OLD WAY:
Code → Redeploy → Agent Available
❌ Slow ❌ Error-prone ❌ Risky

NEW WAY:
API Call → Agent Available
✅ Fast ✅ Safe ✅ Dynamic

All configuration is now in the DATABASE!
```

---

## **Next Steps**

1. ✅ Create first agent via API
2. ✅ Verify it appears in Bedrock
3. ✅ Update system_prompt via API
4. ✅ Verify updated prompt is used
5. ✅ Add more MCPs via API
6. ✅ Verify tools auto-discovered

**System is ready! Start using it now!** 🚀
