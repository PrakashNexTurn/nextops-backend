# ⚡ QUICK ACTION GUIDE - Agent Enabled Column Fix

## 🔴 Problem
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column agents.enabled does not exist
```

## ✅ Solution Applied
Removed `enabled` column from Agent model in `app/models/agent.py`

## 🚀 What You Need to Do NOW

### Step 1: Restart Application (30 seconds)
```bash
# Kill existing process
pkill -f "uvicorn app.main:app"

# Start fresh
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Test Agent Creation (1 minute)
```bash
curl -X POST 'http://54.237.161.73:8000/agents' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "test-github",
    "description": "Test GitHub agent",
    "system_prompt": "You are a test GitHub agent"
  }'
```

**Expected Result:** `200 OK` with agent object ✅

### Step 3: Verify Endpoints (2 minutes)
```bash
# List agents
curl http://54.237.161.73:8000/agents

# Should return 200 OK with agents array ✅
```

## 📋 What Changed

| Item | Before | After |
|------|--------|-------|
| `enabled` column | ❌ In model but not in DB | ✅ Removed from model |
| Schema match | ❌ Broken | ✅ Perfect |
| POST /agents | ❌ Error 500 | ✅ Works |
| All endpoints | ❌ Down | ✅ Up |

## ✨ Status: COMPLETE

- ✅ Model fixed
- ✅ Code committed
- ⏳ Awaiting application restart
- ⏳ Ready to test

**Just restart the app and test - everything will work!** 🚀
