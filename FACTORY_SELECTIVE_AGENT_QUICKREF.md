# Selective Agent Factory - Quick Reference

## 🎯 Quick Start (30 seconds)

```python
from app.services.agent_factory import AgentFactory

factory = AgentFactory(db=db)

# Load only specific agents
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["Agent1", "Agent2"]  # ← SPECIFY AGENTS
)

print(f"✅ Created {len(agents)} agents")
```

---

## 📋 Cheat Sheet

| Use Case | Code |
|----------|------|
| **Load all enabled agents** | `selected_agents=None` (default) |
| **Load by names** | `selected_agents=["Agent1", "Agent2"]` |
| **Load by IDs** | `selected_agents=[1, 2, 3]` |
| **Mixed names & IDs** | `selected_agents=["Agent1", 2, "Agent3"]` |
| **Single agent** | `selected_agents=["Agent1"]` |
| **Get statistics** | `agents, stats = await factory...` |
| **Check not found** | `stats["not_found"]` |
| **Check failures** | `stats["failed"]` |

---

## 🔍 Understanding Stats

```python
stats = {
    "total_available": 5,           # Matched in database
    "total_selected": 3,            # Requested
    "successfully_created": 3,      # Created successfully
    "failed": [],                   # Failed creations
    "not_found": [],                # Requested but not in DB
    "mode": "selective"             # "all" or "selective"
}
```

---

## 💡 Common Patterns

### Pattern 1: With Error Handling
```python
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["Agent1", "Agent2"]
)

if stats["not_found"]:
    logger.warning(f"Not found: {stats['not_found']}")
if stats["failed"]:
    logger.error(f"Failed: {stats['failed']}")
```

### Pattern 2: Config-Driven
```python
config = {"agents": ["Agent1", "Agent2"]}
agents, stats = await factory.create_agents_from_database(
    actor_id="user",
    session_id="session",
    selected_agents=config["agents"]
)
```

### Pattern 3: Runtime Class
```python
class MyRuntime:
    async def init(self, agent_names):
        self.agents, self.stats = await factory.create_agents_from_database(
            actor_id="user",
            session_id="session",
            selected_agents=agent_names
        )
```

---

## 🚀 Use Cases

| Scenario | Implementation |
|----------|----------------|
| Microservice A needs only 3 agents | `selected_agents=["A1", "A2", "A3"]` |
| Multi-tenant: load tenant-specific | `selected_agents=[f"tenant_{id}_*"]` |
| Workflow: load workflow agents | `selected_agents=WORKFLOW_AGENTS[type]` |
| Performance: batch load | Loop with `selected_agents=batch` |
| A/B Testing: different agents per group | `selected_agents=GROUP_AGENTS[group]` |

---

## ⚠️ Important Notes

✅ **Backward Compatible** - Old code works unchanged  
✅ **Mixed Types OK** - Use names and IDs together  
✅ **Order Matters** - Results may differ from request order  
✅ **Async Only** - Must use `await`  
✅ **Returns Tuple** - `(agents, stats)` not just `agents`  

❌ **Empty List** - `[]` loads ALL agents (not zero)  
❌ **Case Sensitive** - Agent names are case-sensitive  
❌ **Duplicates** - Automatically deduplicated  

---

## 🔧 Method Signature

```python
async def create_agents_from_database(
    actor_id: str,                           # Required
    session_id: str,                         # Required
    enabled_only: bool = True,               # Optional
    hooks: Optional[List] = None,            # Optional
    selected_agents: Optional[List] = None   # ← NEW
) -> tuple[List[Agent], Dict[str, Any]]:
```

---

## 📊 Examples at a Glance

### Load Everything
```python
await factory.create_agents_from_database(
    actor_id="user", session_id="sess"
)
```

### Load Specific 
```python
await factory.create_agents_from_database(
    actor_id="user", session_id="sess",
    selected_agents=["Agent1", "Agent2"]
)
```

### Get Stats
```python
agents, stats = await factory.create_agents_from_database(...)
created = stats["successfully_created"]
not_found = stats["not_found"]
failed = stats["failed"]
```

---

## 🎯 Query Behavior

When you request specific agents:

```python
selected_agents = ["Agent1", 2, "Agent3"]
```

The factory constructs:
```sql
WHERE (name IN ["Agent1", "Agent3"]) OR (id IN [2])
```

- **String items** → matched by `name`
- **Int items** → matched by `id`
- **OR logic** → find any match
- **No duplicates** → each agent returned once

---

## 📈 Performance Tips

✅ Load only needed agents (faster)  
✅ Use IDs instead of names when possible  
✅ Parallel creation (async)  
✅ Batch multiple requests  
✅ Cache results if needed  

---

## 🔗 Links

- **Full Guide**: `FACTORY_SELECTIVE_AGENT_GUIDE.md`
- **Examples**: `FACTORY_SELECTIVE_AGENT_EXAMPLES.py`
- **Code**: `app/services/agent_factory.py`
- **Method**: `create_agents_from_database()`

---

**Version**: 1.0  
**Last Updated**: 2024-03-07  
**Status**: ✅ Production Ready
