# Selective Agent Factory - Migration Guide

## 🔄 Upgrading Existing Code

This guide helps you update existing code to use the new selective agent initialization feature.

---

## 📊 Before vs After

### Before (Original)
```python
agents = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456"
)
# Returns: List[Agent]
# Loads ALL agents
```

### After (New)
```python
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["Agent1", "Agent2"]  # ← NEW
)
# Returns: (List[Agent], Dict[str, Any])
# Loads ONLY specified agents
```

---

## ✅ Backward Compatibility

**Good news**: Your existing code still works!

### Option 1: Keep Using Old Way (Recommended if not changing)
```python
# This still works - loads all enabled agents
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456"
)
# Just unpack the tuple
agents = agents  # First element
```

### Option 2: Ignore Stats (If you don't need them)
```python
# You can still use unpacking, just ignore stats
agents, _ = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456"
)
```

---

## 🚀 Migration Steps

### Step 1: Identify Agent Factory Usage

Find all places using `create_agents_from_database()`:

```bash
# Search your codebase
grep -r "create_agents_from_database" .
```

### Step 2: Update Return Value Handling

#### Old Code
```python
agents = await factory.create_agents_from_database(actor_id, session_id)
```

#### Option A: Unpack Both (Recommended)
```python
agents, stats = await factory.create_agents_from_database(actor_id, session_id)

# Handle statistics
if stats["not_found"]:
    logger.warning(f"Not found: {stats['not_found']}")
```

#### Option B: Ignore Stats
```python
agents, _ = await factory.create_agents_from_database(actor_id, session_id)
```

### Step 3: Add Selective Loading Where Needed

#### Example Migration

**Before:**
```python
class DataPipeline:
    async def run(self, user_id: str):
        # Load ALL agents (wasteful)
        agents = await factory.create_agents_from_database(
            actor_id=user_id,
            session_id="pipeline"
        )
        
        # Only use 2 of them
        data_agent = agents[0]
        report_agent = agents[1]
```

**After:**
```python
class DataPipeline:
    async def run(self, user_id: str):
        # Load ONLY needed agents (efficient)
        agents, stats = await factory.create_agents_from_database(
            actor_id=user_id,
            session_id="pipeline",
            selected_agents=["DataProcessor", "ReportGenerator"]  # ← NEW
        )
        
        if stats["not_found"]:
            raise ValueError(f"Missing agents: {stats['not_found']}")
        
        # Safe to use
        data_agent = agents[0]
        report_agent = agents[1]
```

---

## 📋 Migration Scenarios

### Scenario 1: Simple Load-All Usage

**Original:**
```python
async def initialize_agents(user_id: str):
    agents = await factory.create_agents_from_database(
        actor_id=user_id,
        session_id="init"
    )
    return agents
```

**Updated:**
```python
async def initialize_agents(user_id: str):
    agents, stats = await factory.create_agents_from_database(
        actor_id=user_id,
        session_id="init"
    )
    return agents  # Still returns same list
```

**Status**: ✅ Works as-is, just unpack tuple

---

### Scenario 2: Filter by Type

**Original:**
```python
async def get_data_agents(user_id: str):
    agents = await factory.create_agents_from_database(
        actor_id=user_id,
        session_id="data"
    )
    # Filter manually
    return [a for a in agents if "Data" in a.name]
```

**Updated:**
```python
async def get_data_agents(user_id: str):
    # Load only data agents directly
    agents, stats = await factory.create_agents_from_database(
        actor_id=user_id,
        session_id="data",
        selected_agents=["DataProcessor", "DataValidator", "DataExtractor"]
    )
    return agents
```

**Status**: ✅ More efficient - no filtering needed

---

### Scenario 3: Bedrock Runtime

**Original:**
```python
class BedrockRuntime:
    async def init(self, user_id: str):
        # Load everything
        agents = await factory.create_agents_from_database(
            actor_id=user_id,
            session_id="runtime"
        )
        self.agents = agents
```

**Updated:**
```python
class BedrockRuntime:
    async def init(self, user_id: str, agent_list: List[str]):
        # Load selectively
        agents, stats = await factory.create_agents_from_database(
            actor_id=user_id,
            session_id="runtime",
            selected_agents=agent_list  # ← NEW
        )
        
        # Handle errors
        if stats["not_found"]:
            logger.error(f"Missing agents: {stats['not_found']}")
        
        self.agents = agents
        self.stats = stats
```

**Status**: ✅ Better error handling and efficiency

---

### Scenario 4: With Error Handling

**Original:**
```python
async def safe_initialize(user_id: str):
    try:
        agents = await factory.create_agents_from_database(
            actor_id=user_id,
            session_id="safe"
        )
        return agents
    except Exception as e:
        logger.error(f"Failed to load agents: {e}")
        return []
```

**Updated:**
```python
async def safe_initialize(user_id: str, needed_agents: List[str] = None):
    try:
        agents, stats = await factory.create_agents_from_database(
            actor_id=user_id,
            session_id="safe",
            selected_agents=needed_agents
        )
        
        # More granular error handling
        if stats["not_found"]:
            logger.error(f"Missing agents: {stats['not_found']}")
            return []
        
        if stats["failed"]:
            logger.error(f"Failed agents: {stats['failed']}")
            return agents  # Return partial success
        
        return agents
        
    except Exception as e:
        logger.error(f"Failed to load agents: {e}")
        return []
```

**Status**: ✅ Better error reporting with new stats

---

## 🔄 Common Patterns

### Pattern 1: Required Agents

**Before:**
```python
agents = await factory.create_agents_from_database(actor_id, session_id)
assert len(agents) >= 3, "Need at least 3 agents"
```

**After:**
```python
required = ["Agent1", "Agent2", "Agent3"]
agents, stats = await factory.create_agents_from_database(
    actor_id=actor_id,
    session_id=session_id,
    selected_agents=required
)
if stats["not_found"]:
    raise ValueError(f"Required agents missing: {stats['not_found']}")
```

---

### Pattern 2: Optional Agents

**Before:**
```python
agents = await factory.create_agents_from_database(actor_id, session_id)
feature_agents = [a for a in agents if "Feature" in a.name] or []
```

**After:**
```python
feature_agents = ["FeatureAgent1", "FeatureAgent2"]
agents, stats = await factory.create_agents_from_database(
    actor_id=actor_id,
    session_id=session_id,
    selected_agents=feature_agents
)
# Use what was found
available = agents
```

---

### Pattern 3: Conditional Loading

**Before:**
```python
agents = await factory.create_agents_from_database(actor_id, session_id)
if premium_user:
    agents = agents  # Use all
else:
    agents = agents[:3]  # Limit to first 3
```

**After:**
```python
if premium_user:
    selected = None  # Load all
else:
    selected = ["Agent1", "Agent2", "Agent3"]  # Limited set

agents, stats = await factory.create_agents_from_database(
    actor_id=actor_id,
    session_id=session_id,
    selected_agents=selected
)
```

---

## 🛠️ Automated Migration Script

If you have many files to update:

```python
import re
import os

def migrate_file(filepath):
    """Migrate a file from old to new API"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find patterns like:
    # agents = await factory.create_agents_from_database(
    pattern = r'(\w+)\s*=\s*await\s+factory\.create_agents_from_database\('
    
    # Replace with:
    # agents, stats = await factory.create_agents_from_database(
    replacement = r'\1, stats = await factory.create_agents_from_database('
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"✅ Migrated: {filepath}")
    else:
        print(f"⏭️  Skipped: {filepath}")

# Run on all Python files
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            migrate_file(os.path.join(root, file))
```

---

## 📝 Checklist for Migration

- [ ] Identify all `create_agents_from_database()` calls
- [ ] Update return value handling (unpack tuple)
- [ ] Add selective agent loading where applicable
- [ ] Update error handling to use stats
- [ ] Test backward compatibility
- [ ] Test new selective loading features
- [ ] Update unit tests
- [ ] Update integration tests
- [ ] Document changes in code comments
- [ ] Update API documentation if needed

---

## 🧪 Testing Your Migration

### Test Case 1: Backward Compatible
```python
async def test_backward_compat():
    # Old code should still work
    agents, stats = await factory.create_agents_from_database(
        actor_id="test",
        session_id="test"
    )
    assert len(agents) >= 0
    assert isinstance(stats, dict)
```

### Test Case 2: New Features
```python
async def test_selective():
    agents, stats = await factory.create_agents_from_database(
        actor_id="test",
        session_id="test",
        selected_agents=["Agent1", "Agent2"]
    )
    assert stats["mode"] == "selective"
```

---

## 📚 Documentation Updates

Update your documentation:

**Before:**
```
## Agent Factory

Usage:
agents = await factory.create_agents_from_database(actor_id, session_id)
```

**After:**
```
## Agent Factory

### Load All Agents
agents, stats = await factory.create_agents_from_database(actor_id, session_id)

### Load Specific Agents
agents, stats = await factory.create_agents_from_database(
    actor_id=actor_id,
    session_id=session_id,
    selected_agents=["Agent1", "Agent2"]
)

### Returns
- agents: List of initialized Agent instances
- stats: Dictionary with creation statistics
```

---

## 🎯 Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Planning** | 1 day | Identify usage, plan approach |
| **Migration** | 2-3 days | Update code, add features |
| **Testing** | 2-3 days | Unit tests, integration tests |
| **Validation** | 1 day | Production validation |
| **Documentation** | 1 day | Update docs, create guides |

---

## ⚠️ Common Issues

### Issue 1: UnpackingError
```python
# ❌ Wrong
agents = await factory.create_agents_from_database(...)

# ✅ Correct
agents, stats = await factory.create_agents_from_database(...)
```

### Issue 2: Ignoring Statistics
```python
# ⚠️ May miss errors
agents, _ = await factory.create_agents_from_database(...)

# ✅ Better
agents, stats = await factory.create_agents_from_database(...)
if stats["not_found"]:
    handle_missing()
```

### Issue 3: Type Hints
```python
# ❌ Old type hint
def process(agents: List[Agent]): ...

# ✅ Updated
def process(agents_result: Tuple[List[Agent], Dict]): ...
    agents, stats = agents_result
```

---

## 🚀 Final Steps

1. ✅ Update return value handling
2. ✅ Add selective loading
3. ✅ Test thoroughly
4. ✅ Update documentation
5. ✅ Deploy confidently

---

## 📞 Getting Help

- Check: `FACTORY_SELECTIVE_AGENT_QUICKREF.md`
- Read: `FACTORY_SELECTIVE_AGENT_GUIDE.md`
- Review: `FACTORY_SELECTIVE_AGENT_EXAMPLES.py`
- Test: `FACTORY_SELECTIVE_AGENT_TESTING.md`

---

**Migration Guide Version**: 1.0  
**Last Updated**: 2024-03-07  
**Difficulty**: ⭐⭐ (Easy)
