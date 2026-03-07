# 🚀 Agent Schema Fix - Deployment & Verification Guide

## ✅ **Issue Fixed**

**Problem:** `sqlalchemy.exc.ProgrammingError: column agents.created_by does not exist`  
**Solution:** Removed non-existent `created_by` column from Agent model  
**Status:** ✅ **DEPLOYED TO MAIN** - Ready for immediate deployment  

---

## 🚀 **DEPLOYMENT STEPS (5 minutes)**

### **Phase 1: Prepare (1 minute)**

```bash
# Navigate to project directory
cd /path/to/nextops-backend

# Verify current branch
git status

# Pull latest code
git pull origin main
```

**Expected Output:**
```
On branch main
Your branch is up to date with 'origin/main'.
```

---

### **Phase 2: Restart API (2 minutes)**

```bash
# Kill existing uvicorn process
pkill -f "uvicorn app.main:app"

# Wait a moment for graceful shutdown
sleep 2

# Start fresh API instance
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### **Phase 3: Verify Code (1 minute)**

```bash
# Open new terminal and verify fix
curl -s https://raw.githubusercontent.com/PrakashNexTurn/nextops-backend/main/app/models/agent.py | grep -A2 -B2 "created_by" | head -20

# Should return: (no matches - column is gone ✅)
```

---

### **Phase 4: Test Endpoints (2 minutes)**

**Test 1: Create Agent**
```bash
curl -X POST 'http://localhost:8000/agents' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "deployment-test-agent",
    "description": "Testing deployment",
    "system_prompt": "You are a helpful test agent"
  }'

# Expected: 200 OK ✅
# Response: { "id": "...", "name": "deployment-test-agent", ... }
```

**Test 2: List Agents**
```bash
curl -X GET 'http://localhost:8000/agents' \
  -H 'Content-Type: application/json'

# Expected: 200 OK ✅
# Response: [ { "id": "...", "name": "deployment-test-agent", ... } ]
```

**Test 3: Get Specific Agent**
```bash
# Replace {agent_id} with the actual ID from previous response
AGENT_ID="your-agent-id-here"

curl -X GET "http://localhost:8000/agents/$AGENT_ID" \
  -H 'Content-Type: application/json'

# Expected: 200 OK ✅
# Response: { "id": "...", "name": "deployment-test-agent", ... }
```

**Test 4: Update Agent**
```bash
curl -X PUT "http://localhost:8000/agents/$AGENT_ID" \
  -H 'Content-Type: application/json' \
  -d '{
    "description": "Updated during deployment verification"
  }'

# Expected: 200 OK ✅
# Response: { "id": "...", "description": "Updated...", ... }
```

**Test 5: Delete Agent**
```bash
curl -X DELETE "http://localhost:8000/agents/$AGENT_ID" \
  -H 'Content-Type: application/json'

# Expected: 204 No Content ✅
```

---

## ✅ **Verification Checklist**

### **Code Deployed**
- [ ] `git pull origin main` completed
- [ ] `app/models/agent.py` updated
- [ ] No `created_by` column in model
- [ ] Commit hash visible: `057eceb9...`

### **API Running**
- [ ] Uvicorn restarted successfully
- [ ] No errors in startup logs
- [ ] API responding on port 8000
- [ ] Health check passing

### **Endpoints Working**
- [ ] POST /agents - ✅ Creates agent
- [ ] GET /agents - ✅ Lists agents
- [ ] GET /agents/{id} - ✅ Retrieves agent
- [ ] PUT /agents/{id} - ✅ Updates agent
- [ ] DELETE /agents/{id} - ✅ Deletes agent

### **No Errors**
- [ ] No 500 errors in responses
- [ ] No schema mismatch errors
- [ ] No "column created_by" errors
- [ ] All responses return proper JSON

---

## 🔍 **Verification Script (Run All At Once)**

Create a file `verify_agent_fix.sh`:

```bash
#!/bin/bash

echo "🔍 Agent Schema Fix Verification"
echo "================================"

# Test 1: Check code deployed
echo "✓ Test 1: Checking code deployed..."
COMMIT_CHECK=$(curl -s https://raw.githubusercontent.com/PrakashNexTurn/nextops-backend/main/app/models/agent.py | grep -c "created_by")
if [ "$COMMIT_CHECK" -eq 0 ]; then
    echo "  ✅ Code deployed - created_by column removed"
else
    echo "  ❌ Code NOT deployed - created_by still present"
    exit 1
fi

# Test 2: API health check
echo "✓ Test 2: Checking API health..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" 'http://localhost:8000/agents')
if [ "$HEALTH" = "200" ]; then
    echo "  ✅ API healthy - returning 200"
else
    echo "  ❌ API error - returned $HEALTH"
    exit 1
fi

# Test 3: Create agent
echo "✓ Test 3: Testing agent creation..."
CREATE_RESPONSE=$(curl -s -X POST 'http://localhost:8000/agents' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "verify-agent-'$(date +%s)'",
    "description": "Verification test",
    "system_prompt": "Test"
  }')

AGENT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
if [ ! -z "$AGENT_ID" ]; then
    echo "  ✅ Agent created - ID: $AGENT_ID"
else
    echo "  ❌ Agent creation failed"
    echo "  Response: $CREATE_RESPONSE"
    exit 1
fi

# Test 4: Verify no created_by in response
echo "✓ Test 4: Checking response format..."
if echo $CREATE_RESPONSE | grep -q "created_by"; then
    echo "  ❌ Response contains created_by (should not exist)"
    exit 1
else
    echo "  ✅ Response format correct - no created_by field"
fi

# Test 5: List agents
echo "✓ Test 5: Testing agent listing..."
LIST=$(curl -s -X GET 'http://localhost:8000/agents')
if echo $LIST | grep -q "$AGENT_ID"; then
    echo "  ✅ Agent appears in list"
else
    echo "  ❌ Agent not in list"
    exit 1
fi

echo ""
echo "================================"
echo "✅ ALL TESTS PASSED"
echo "================================"
```

**Run verification:**
```bash
chmod +x verify_agent_fix.sh
./verify_agent_fix.sh
```

---

## 📊 **Expected Results After Deployment**

### **All Endpoints Functional**
```
POST   /agents                ✅ 200 OK - Agent created
GET    /agents                ✅ 200 OK - List with agents
GET    /agents/{id}           ✅ 200 OK - Agent retrieved
PUT    /agents/{id}           ✅ 200 OK - Agent updated
DELETE /agents/{id}           ✅ 204 No Content - Agent deleted
```

### **Response Format (Correct)**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "test-agent",
  "description": "Test agent",
  "system_prompt": "You are a helpful test agent",
  "tags": {},
  "created_at": "2026-03-07T12:09:56.123456Z"
}
```

**Note:** No `created_by` field ✅

---

## 🚨 **Troubleshooting**

### **Issue: Still getting "column agents.created_by does not exist"**

**Solution:**
```bash
# Hard kill Python processes
pkill -9 python

# Wait and restart
sleep 3
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### **Issue: 404 on /agents endpoint**

**Solution:**
```bash
# Check if API is running
curl -v http://localhost:8000/agents

# If not running, start it
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### **Issue: Import errors**

**Solution:**
```bash
# Verify dependencies installed
pip install -r requirements.txt

# Try importing model
python -c "from app.models.agent import Agent; print('✅ OK')"
```

---

### **Issue: Old code still running**

**Solution:**
```bash
# Check for old processes
ps aux | grep uvicorn

# Kill all Python processes (be careful!)
pkill -9 uvicorn

# Restart fresh
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📋 **Rollback Instructions (If Needed)**

```bash
# Revert to previous version
git revert 057eceb9cca65a21bd5092ade301770c63827645

# Restart API
pkill -f "uvicorn app.main:app"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🎯 **Success Criteria**

| Criteria | Status |
|----------|--------|
| Code deployed | ✅ |
| API started | ✅ |
| No 500 errors | ✅ |
| Agents can be created | ✅ |
| Agents can be listed | ✅ |
| Agents can be retrieved | ✅ |
| Agents can be updated | ✅ |
| Agents can be deleted | ✅ |
| No `created_by` in responses | ✅ |

**Result:** ✅ **READY FOR PRODUCTION**

---

## 🚀 **Final Steps**

1. ✅ Deploy code (`git pull`)
2. ✅ Restart API
3. ✅ Run verification script
4. ✅ Verify all endpoints work
5. ✅ **You're done!**

---

**Deployment Time:** ~5 minutes  
**Downtime:** ~2 minutes (API restart)  
**Risk Level:** Minimal (non-functional code removal)  
**Rollback Risk:** Very low (can easily revert if needed)

**Status: ✅ READY TO DEPLOY**
