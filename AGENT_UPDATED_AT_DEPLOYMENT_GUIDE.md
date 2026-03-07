# ✅ Agent Schema Fix - Deployment & Verification Guide

## 🎯 Overview

This guide walks you through deploying the agent schema fix and verifying it works.

**Status:** Code is fixed ✅ → Ready for API restart

---

## 📋 Pre-Deployment Checklist

- [x] Code fix committed: `fb6bce18e0bb069a904e07ecea9b04a23f1421c0`
- [x] `updated_at` column removed from model
- [x] `updated_at` removed from to_dict() method
- [ ] API server is accessible
- [ ] PostgreSQL database is running
- [ ] You have SSH/console access to restart API

---

## 🚀 Deployment Steps (5 minutes)

### Step 1: Stop Current API (1 minute)

```bash
# Kill the running uvicorn process
pkill -f "uvicorn app.main:app"

# Verify it's stopped (should show empty)
ps aux | grep uvicorn | grep -v grep

# If still running, force kill
pkill -9 -f "uvicorn"

# Wait for cleanup
sleep 2
```

### Step 2: Start API with New Code (2 minutes)

```bash
# Start the API with the fixed code
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for startup
echo "Waiting for API to start..."
sleep 5

# Check if it's running
curl -s http://localhost:8000/docs > /dev/null && echo "✅ API is running" || echo "❌ API failed to start"
```

### Step 3: Verify Logs (1 minute)

```bash
# Check for any error messages (should be clean)
tail -20 app.log 2>/dev/null

# Look for these keywords (should NOT appear):
# - "column agents.updated_at does not exist"
# - "column agents.enabled does not exist"
# - "ProgrammingError"
# - "UndefinedColumn"

# Should see:
# - "Application startup complete"
# - "Uvicorn running"
```

---

## 🧪 Post-Deployment Tests (5 minutes)

### Test 1: Health Check

```bash
curl -i http://localhost:8000/docs
# Expected: 200 OK
```

### Test 2: Create Agent (CRITICAL)

```bash
# Create a test agent
RESPONSE=$(curl -s -X POST 'http://localhost:8000/agents' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "verify-'$(date +%s)'",
    "description": "Test agent for schema verification",
    "system_prompt": "You are a helpful assistant"
  }')

# Check response
echo "$RESPONSE" | jq .
# Expected: Returns 200 OK with agent ID, name, system_prompt, tags, created_at, created_by

# Extract agent ID for later tests
AGENT_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Created agent: $AGENT_ID"
```

### Test 3: List Agents

```bash
curl -s -X GET 'http://localhost:8000/agents' | jq .
# Expected: 200 OK with array of agents
```

### Test 4: Get Specific Agent

```bash
curl -s -X GET "http://localhost:8000/agents/$AGENT_ID" | jq .
# Expected: 200 OK with agent details
```

### Test 5: Update Agent

```bash
curl -s -X PUT "http://localhost:8000/agents/$AGENT_ID" \
  -H 'Content-Type: application/json' \
  -d '{"description": "Updated description"}' | jq .
# Expected: 200 OK with updated agent
```

### Test 6: Delete Agent

```bash
curl -s -X DELETE "http://localhost:8000/agents/$AGENT_ID"
# Expected: 204 No Content
```

### Test 7: Verify Deletion

```bash
curl -s -X GET "http://localhost:8000/agents/$AGENT_ID" | jq .
# Expected: 404 Not Found (agent was deleted)
```

---

## ✅ Success Indicators

You should see:

| Test | Expected | Status |
|------|----------|--------|
| Health Check | 200 OK | ✅ |
| Create Agent | 200 OK with agent data | ✅ |
| List Agents | 200 OK with array | ✅ |
| Get Agent | 200 OK with details | ✅ |
| Update Agent | 200 OK with updates | ✅ |
| Delete Agent | 204 No Content | ✅ |
| Verify Delete | 404 Not Found | ✅ |

---

## ⚠️ Failure Diagnosis

### Symptom 1: API Won't Start
```bash
# Check for errors
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Look for import errors, database connection issues

# Verify Python packages installed
pip list | grep sqlalchemy
pip list | grep fastapi
```

### Symptom 2: Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Symptom 3: Still Getting "column agents.updated_at does not exist"
```bash
# Verify code was actually updated
grep "updated_at" app/models/agent.py
# Should return EMPTY (no output)

# If it shows updated_at:
# 1. Pull latest code: git pull origin main
# 2. Verify commit: git log --oneline | head -5
# 3. Check active branch: git branch -a

# Force restart
pkill -9 -f uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Symptom 4: Database Connection Error
```bash
# Verify PostgreSQL is running
psql -c "SELECT 1"

# Check database credentials in environment
echo $DATABASE_URL

# Test database directly
psql $DATABASE_URL -c "\d agents"
# Should show: agents table with columns (no updated_at)
```

---

## 📊 Performance Check (Optional)

After deployment, verify performance:

```bash
# Create multiple agents quickly
for i in {1..10}; do
  curl -s -X POST 'http://localhost:8000/agents' \
    -H 'Content-Type: application/json' \
    -d "{\"name\":\"perf-test-$i\",\"system_prompt\":\"Test\"}" &
done
wait

# List agents (should all be there)
curl -s 'http://localhost:8000/agents' | jq '.[] | .name'

# Expected: See all 10+ agents listed with no errors
```

---

## 📋 Complete Verification Checklist

- [x] Code commit applied: `fb6bce18e0bb069a904e07ecea9b04a23f1421c0`
- [ ] API stopped: `pkill -f uvicorn`
- [ ] API started: `python -m uvicorn...`
- [ ] Wait 5 seconds for startup
- [ ] Health check passed: `curl http://localhost:8000/docs`
- [ ] Create agent test passed: Status 200 OK
- [ ] List agents test passed: Status 200 OK
- [ ] Get agent test passed: Status 200 OK
- [ ] Update agent test passed: Status 200 OK
- [ ] Delete agent test passed: Status 204
- [ ] No "column agents.updated_at" errors in logs
- [ ] No other ProgrammingError in logs

---

## 🎉 Deployment Complete

When all tests pass:

```
┌─────────────────────────────────────────┐
│ ✅ DEPLOYMENT SUCCESSFUL                 │
├─────────────────────────────────────────┤
│ Schema:     Synchronized                 │
│ Endpoints:  All working                  │
│ Status:     Production ready              │
│ Errors:     None                          │
│ Performance: Normal                       │
└─────────────────────────────────────────┘
```

---

## 📞 If Issues Persist

1. **Review full documentation:** `AGENT_UPDATED_AT_FIX_COMPLETE.md`
2. **Check commit:** `git log --oneline | grep -i agent`
3. **Verify database:** `psql $DATABASE_URL -c "\d agents"`
4. **Check API logs:** `tail -100 app.log | grep -i error`
5. **Contact support:** With the full error message and logs

---

## ✅ Reference

- **Main Fix:** `app/models/agent.py` - Removed `updated_at` column
- **Commit:** `fb6bce18e0bb069a904e07ecea9b04a23f1421c0`
- **Files Changed:** 1 file, 2 lines removed
- **Breaking Changes:** None
- **Rollback:** Simple - restart with previous code
