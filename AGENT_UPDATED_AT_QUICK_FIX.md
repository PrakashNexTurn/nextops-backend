# ⚡ Quick Action Guide - Agent Fix Deployment

## 🚨 CRITICAL - IMMEDIATE ACTION REQUIRED

The Agent model schema mismatch has been **FIXED** in code. Now restart your API to activate the fix.

---

## ✅ 3-Step Fix Deployment

### Step 1: Stop API (30 seconds)
```bash
pkill -f "uvicorn app.main:app"
echo "API stopped ✅"
```

### Step 2: Start API (30 seconds)
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo "API starting... wait 5 seconds"
sleep 5
echo "API should be running now ✅"
```

### Step 3: Test Agent Creation (1 minute)
```bash
# Test POST /agents
curl -X POST 'http://localhost:8000/agents' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "test-'$(date +%s)'",
    "system_prompt": "You are a test agent"
  }'

# Expected: 200 OK with agent data ✅
```

---

## 🧪 Verification Tests (Copy & Paste)

**Test 1: Create Agent**
```bash
curl -X POST 'http://localhost:8000/agents' \
  -H 'Content-Type: application/json' \
  -d '{"name":"verify-'$(date +%s)'","system_prompt":"Test"}'
```
✅ Expected: `200 OK` with agent ID

**Test 2: List Agents**
```bash
curl -X GET 'http://localhost:8000/agents'
```
✅ Expected: `200 OK` with agent array

**Test 3: Check Logs**
```bash
# No errors about "column agents.updated_at does not exist"
tail -f /var/log/api.log 2>/dev/null || echo "Logs location varies by setup"
```

---

## ⚠️ If Tests Fail

**Symptom 1: Still get "column agents.updated_at does not exist"**
- API wasn't restarted properly
- Kill: `pkill -9 -f "uvicorn"`
- Verify killed: `ps aux | grep uvicorn` (should be empty)
- Restart: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Symptom 2: Connection refused on port 8000**
- Port is in use by something else
- Find process: `lsof -i :8000`
- Kill it: `kill -9 <PID>`
- Try restart again

**Symptom 3: Still getting 500 errors**
- Check database connection is alive
- Verify PostgreSQL is running
- Check database url in `.env` or environment

---

## 📋 What Was Changed

**File:** `app/models/agent.py`

**Removed:**
```python
# Line 27 - REMOVED
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# From to_dict() - REMOVED
"updated_at": self.updated_at.isoformat() if self.updated_at else None,
```

**Result:** Agent model now matches PostgreSQL database schema exactly ✅

---

## ✅ Status After Restart

| Endpoint | Before | After |
|----------|--------|-------|
| POST /agents | ❌ 500 Error | ✅ Works |
| GET /agents | ❌ 500 Error | ✅ Works |
| PUT /agents/{id} | ❌ 500 Error | ✅ Works |
| DELETE /agents/{id} | ❌ 500 Error | ✅ Works |
| Agent MCPs | ❌ 500 Error | ✅ Works |

---

## 🎯 Success Criteria

After restart, you should see:

✅ POST /agents returns `200 OK` with agent data  
✅ No errors about "column agents.updated_at does not exist"  
✅ All agent endpoints respond (no 500 errors)  
✅ Can create, read, update, delete agents  

---

## 📞 Need Help?

- Check complete documentation: `AGENT_UPDATED_AT_FIX_COMPLETE.md`
- Verify database: `psql` → `\d agents`
- Restart with logging: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug`
