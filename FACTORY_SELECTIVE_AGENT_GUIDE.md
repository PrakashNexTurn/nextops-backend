# Factory Selective Agent Initialization Guide

## 📋 Overview

The `AgentFactory` has been enhanced to support **selective agent initialization**. Instead of loading all agents from the database, you can now specify exactly which agents to initialize by name or ID.

## 🎯 Key Features

✅ **Selective Loading** - Initialize only the agents you need  
✅ **Flexible Input** - Use agent names or IDs  
✅ **Mixed Selection** - Combine names and IDs in the same request  
✅ **Error Handling** - Gracefully handles missing agents  
✅ **Statistics Tracking** - Get detailed information about initialization  
✅ **Backward Compatible** - Existing code continues to work  

---

## 📝 Updated Method Signature

```python
async def create_agents_from_database(
    actor_id: str,
    session_id: str,
    enabled_only: bool = True,
    hooks: Optional[List[HookProvider]] = None,
    selected_agents: Optional[List[Union[str, int]]] = None
) -> tuple[List[Agent], Dict[str, Any]]:
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `actor_id` | `str` | Actor ID for memory tracking | Required |
| `session_id` | `str` | Session ID for memory tracking | Required |
| `enabled_only` | `bool` | Only load enabled agents (ignored if selected_agents provided) | `True` |
| `hooks` | `Optional[List[HookProvider]]` | Hooks for all agents | `None` |
| `selected_agents` | `Optional[List[Union[str, int]]]` | List of agent names/IDs to load (None = load all) | `None` |

### Return Value

Returns a **tuple** containing:
1. **List[Agent]** - Created agent instances
2. **Dict[str, Any]** - Statistics with keys:
   - `total_available`: Total agents found
   - `total_selected`: Total agents requested
   - `successfully_created`: Successfully created agents
   - `failed`: List of failed agent creations
   - `not_found`: List of requested agents that don't exist
   - `mode`: Either "all" or "selective"

---

## 💡 Usage Examples

### Example 1: Load All Enabled Agents (Backward Compatible)

```python
from app.services.agent_factory import AgentFactory
from app.db.database import get_db

db = next(get_db())
factory = AgentFactory(db=db)

# Load ALL enabled agents (original behavior)
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456"
)

print(f"✅ Created {len(agents)} agents")
print(f"Statistics: {stats}")
```

### Example 2: Load Specific Agents by Name

```python
# Load ONLY specific agents by name
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["DataProcessor", "ReportGenerator", "ApprovalWorkflow"]
)

print(f"✅ Created {len(agents)} agents")
print(f"Not found: {stats['not_found']}")
print(f"Failed: {stats['failed']}")
```

### Example 3: Load Specific Agents by ID

```python
# Load agents by ID
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=[1, 2, 5]
)

print(f"✅ Created {stats['successfully_created']} agents")
```

### Example 4: Mixed Selection (Names and IDs)

```python
# Load agents using mix of names and IDs
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["DataProcessor", 3, "ApprovalWorkflow", 7]
)

print(f"Mode: {stats['mode']}")  # Output: "selective"
print(f"Created: {stats['successfully_created']}")
print(f"Not found: {stats['not_found']}")
```

### Example 5: Load Agents with Custom Hooks

```python
from strands.hooks import HookProvider

custom_hooks = [hook1, hook2]

agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["Agent1", "Agent2"],
    hooks=custom_hooks
)
```

### Example 6: Bedrock Runtime Integration

```python
# Typical usage in Bedrock agent runtime

async def initialize_bedrock_agents():
    db = next(get_db())
    factory = AgentFactory(db=db)
    
    # Get list of agents to use from config
    agents_to_use = ["DataAnalysis", "ReportGeneration", "Approval"]
    
    agents, stats = await factory.create_agents_from_database(
        actor_id=request.user_id,
        session_id=request.session_id,
        selected_agents=agents_to_use
    )
    
    if stats["not_found"]:
        logger.warning(f"⚠️ Requested agents not found: {stats['not_found']}")
    
    if stats["failed"]:
        logger.error(f"❌ Failed to create agents: {stats['failed']}")
    
    return agents
```

---

## 📊 Statistics Response Examples

### Success Case
```python
stats = {
    "total_available": 3,
    "total_selected": 3,
    "successfully_created": 3,
    "failed": [],
    "not_found": [],
    "mode": "selective"
}
```

### Partial Success Case
```python
stats = {
    "total_available": 2,
    "total_selected": 3,
    "successfully_created": 2,
    "failed": ["Agent1: Connection timeout"],
    "not_found": ["NonExistentAgent"],
    "mode": "selective"
}
```

---

## 🔄 Migration Guide

### Before (Load All Agents)
```python
agents = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456"
)
```

### After (Selective Loading)
```python
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["Agent1", "Agent2", "Agent3"]
)

# Unpack if you need just the agents
agents = agents  # First element of tuple
```

---

## 🛡️ Error Handling

### Handle Missing Agents

```python
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["Agent1", "NonExistent"]
)

if stats["not_found"]:
    logger.warning(f"⚠️ Not found: {', '.join(stats['not_found'])}")
    # Take action: log, alert, or use fallback
```

### Handle Failed Creations

```python
if stats["failed"]:
    logger.error(f"❌ Failures: {stats['failed']}")
    # Retry logic or notification
```

---

## 🚀 Advanced Usage

### Selective Loading with Bedrock Agent Runtime

```python
class BedrockAgentRuntime:
    def __init__(self, db: Session):
        self.factory = AgentFactory(db=db)
        self.agents = {}
    
    async def initialize_runtime(
        self, 
        requested_agents: List[str],
        actor_id: str,
        session_id: str
    ):
        """Initialize runtime with selected agents"""
        
        agents, stats = await self.factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            selected_agents=requested_agents
        )
        
        # Store agents by name
        for agent in agents:
            self.agents[agent.name] = agent
        
        # Log initialization result
        print(f"🚀 Runtime initialized with {len(agents)} agents")
        print(f"   - Successfully created: {stats['successfully_created']}")
        print(f"   - Failed: {len(stats['failed'])}")
        print(f"   - Not found: {len(stats['not_found'])}")
        
        return agents, stats
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get agent by name from runtime"""
        return self.agents.get(agent_name)
```

---

## ⚙️ Implementation Details

### Query Construction

The factory builds a dynamic SQL query using SQLAlchemy's `or_` operator:

```python
# For selected_agents = ["Agent1", "Agent2", 3, 4]
# Generated query filters by:
# (Agent.name IN ["Agent1", "Agent2"]) OR (Agent.id IN [3, 4])
```

### Validation

- Empty `selected_agents` list loads all agents
- Mixed types (strings and ints) are automatically sorted
- Duplicate entries are handled (no duplicates in output)
- Missing agents are logged but don't cause exceptions

### Async Execution

All agent creation happens in parallel using `asyncio.gather()`:

```python
# All agents created concurrently, not sequentially
results = await asyncio.gather(*tasks, return_exceptions=True)
```

---

## 📋 Backward Compatibility

**Existing code continues to work unchanged:**

```python
# Old code (still works)
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456"
)
# Will load all enabled agents (same as before)
```

The `selected_agents` parameter is optional, so existing calls are unaffected.

---

## 🧪 Testing

### Unit Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_selective_agent_initialization():
    db = test_db_session
    factory = AgentFactory(db=db)
    
    # Test selective loading
    agents, stats = await factory.create_agents_from_database(
        actor_id="test-user",
        session_id="test-session",
        selected_agents=["Agent1", "Agent2"]
    )
    
    assert len(agents) == 2
    assert stats["mode"] == "selective"
    assert stats["successfully_created"] == 2
    assert stats["not_found"] == []
```

---

## 📚 Related Documentation

- [Agent Factory Architecture](./ARCHITECTURE_OVERVIEW.md)
- [Dynamic MCP Loading Guide](./DYNAMIC_MCP_CLIENT_GUIDE.md)
- [Agent Management](./AGENT_MANAGEMENT_COMPLETE_SUMMARY.md)

---

## 🔗 Quick Links

- **File**: `app/services/agent_factory.py`
- **Method**: `create_agents_from_database()`
- **Commit**: `7787706f8e63846184360babed411015add77a2e`

---

**Last Updated**: 2024-03-07  
**Version**: 1.0 (Selective Agent Initialization)
