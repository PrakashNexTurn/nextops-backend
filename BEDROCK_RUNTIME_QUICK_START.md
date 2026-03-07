"""
BEDROCK RUNTIME - QUICK START GUIDE

Get started with database-managed Bedrock runtime configurations in 10 minutes.
"""

# ============================================================================
# QUICK START (10 MINUTES)
# ============================================================================

Step 1: Create Agents (if not already created)
─────────────────────────────────────────────

$ curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DataProcessor",
    "description": "Processes data and generates reports",
    "system_prompt": "You are a data processor. Your role is to...",
    "enabled": true
  }'

Response:
{
    "id": 1,
    "name": "DataProcessor",
    "status": "success"
}

$ curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ReportGenerator",
    "description": "Generates formatted reports",
    "system_prompt": "You are a report generator...",
    "enabled": true
  }'

Response:
{
    "id": 2,
    "name": "ReportGenerator"
}


Step 2: Create Runtime Configuration
──────────────────────────────────────

$ curl -X POST http://localhost:8000/bedrock-runtimes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "prod-runtime",
    "description": "Production data processing",
    "selected_agent_ids": [1, 2],
    "aws_region": "us-east-1",
    "memory_mb": 1024,
    "timeout_seconds": 600,
    "environment": "prod"
  }'

Response:
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "prod-runtime",
        "status": "inactive",
        "selected_agent_ids": [1, 2],
        ...
    }
}


Step 3: Activate Runtime
────────────────────────

$ curl -X POST http://localhost:8000/bedrock-runtimes/1/activate

Response:
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "active"
    }
}


Step 4: Invoke Bedrock with Runtime
────────────────────────────────────

# Option A: Use runtime by ID
$ curl -X POST http://localhost:8000/bedrock/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process the latest tickets",
    "runtime_id": 1,
    "actor_id": "user-123",
    "session_id": "session-456"
  }'

# Option B: Use runtime by name
$ curl -X POST http://localhost:8000/bedrock/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process the latest tickets",
    "runtime_name": "prod-runtime",
    "actor_id": "user-123"
  }'

# Option C: Use selective agents
$ curl -X POST http://localhost:8000/bedrock/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process the latest tickets",
    "selected_agent_ids": [1, 2],
    "actor_id": "user-123"
  }'


Step 5: Monitor Runtime
─────────────────────────

$ curl http://localhost:8000/bedrock-runtimes/1

Response:
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "prod-runtime",
        "status": "active",
        "selected_agent_ids": [1, 2],
        "environment": "prod",
        "created_at": "2024-03-07T12:00:00",
        "updated_at": "2024-03-07T12:05:00",
        "last_error": null
    }
}


# ============================================================================
# COMMON SCENARIOS
# ============================================================================

Scenario 1: Different Runtimes for Different Environments
──────────────────────────────────────────────────────────

# Create DEV runtime
POST /bedrock-runtimes
{
    "name": "dev-runtime",
    "environment": "dev",
    "selected_agent_ids": [1],
    "memory_mb": 512,
    "timeout_seconds": 300
}

# Create STAGING runtime
POST /bedrock-runtimes
{
    "name": "staging-runtime",
    "environment": "staging",
    "selected_agent_ids": [1, 2],
    "memory_mb": 1024,
    "timeout_seconds": 600
}

# Create PROD runtime
POST /bedrock-runtimes
{
    "name": "prod-runtime",
    "environment": "prod",
    "selected_agent_ids": [1, 2, 3],
    "memory_mb": 2048,
    "timeout_seconds": 900
}

# Use in code
if environment == "prod":
    runtime_name = "prod-runtime"
elif environment == "staging":
    runtime_name = "staging-runtime"
else:
    runtime_name = "dev-runtime"

payload = {
    "prompt": message,
    "runtime_name": runtime_name,
    "actor_id": actor_id
}


Scenario 2: Load Only Specific Agents for Task
──────────────────────────────────────────────

# Sometimes you only need specific agents for a task
# Use selective agent loading without creating a runtime

payload = {
    "prompt": "Generate reports for Q1",
    "selected_agent_names": ["ReportGenerator", "DataProcessor"],
    "actor_id": "user-123"
}


Scenario 3: A/B Testing Different Agent Configurations
───────────────────────────────────────────────────────

# Create runtime A (agents 1, 2)
POST /bedrock-runtimes
{
    "name": "runtime-a",
    "selected_agent_ids": [1, 2],
    "tags": {"experiment": "a-b-test", "version": "a"}
}

# Create runtime B (agents 2, 3)
POST /bedrock-runtimes
{
    "name": "runtime-b",
    "selected_agent_ids": [2, 3],
    "tags": {"experiment": "a-b-test", "version": "b"}
}

# In application, randomly select runtime
import random
runtime = random.choice(["runtime-a", "runtime-b"])

payload = {
    "prompt": message,
    "runtime_name": runtime,
    "actor_id": actor_id
}


Scenario 4: Update Runtime Configuration
────────────────────────────────────────

# Add a new agent to runtime
PUT /bedrock-runtimes/1/agents
{
    "agent_ids": [1, 2, 3, 4]
}

# Or update other parameters
PUT /bedrock-runtimes/1
{
    "memory_mb": 2048,
    "timeout_seconds": 900,
    "description": "Updated: now includes Agent 4"
}


# ============================================================================
# MANAGEMENT COMMANDS
# ============================================================================

List all runtimes:
GET /bedrock-runtimes

List active runtimes only:
GET /bedrock-runtimes?status=active

List production runtimes:
GET /bedrock-runtimes?environment=prod

Get runtime details:
GET /bedrock-runtimes/{runtime_id}

Get runtime by name:
GET /bedrock-runtimes/by-name/prod-runtime

Get agents for runtime:
GET /bedrock-runtimes/{runtime_id}/agents

Activate runtime:
POST /bedrock-runtimes/{runtime_id}/activate

Deactivate runtime:
POST /bedrock-runtimes/{runtime_id}/deactivate

Archive runtime:
POST /bedrock-runtimes/{runtime_id}/archive

Get statistics:
GET /bedrock-runtimes/stats/summary

Delete runtime:
DELETE /bedrock-runtimes/{runtime_id}


# ============================================================================
# BEST PRACTICES
# ============================================================================

1. Use Runtime Configurations for Persistent Settings
   ✅ DO:
      - Create runtimes for each environment (dev, staging, prod)
      - Store optimal agent configurations in database
      - Use runtime_id for consistent behavior
   
   ❌ DON'T:
      - Change agent selections frequently without runtime config
      - Use different agents for same task across invocations

2. Naming Conventions
   ✅ DO:
      - Use descriptive names: "prod-data-pipeline"
      - Include environment: "{env}-{purpose}"
      - Use hyphens for readability
   
   ❌ DON'T:
      - Use generic names: "runtime1", "config"
      - Mix case styles: "ProdRuntime", "prod-Runtime"

3. Tag Runtimes for Organization
   ✅ DO:
      - Tag by purpose: {"purpose": "data-processing"}
      - Tag by team: {"team": "operations"}
      - Tag by cost-center: {"cost-center": "eng-1"}
   
   ❌ DON'T:
      - Use tags for frequently changing data
      - Create too many tag types

4. Agent Selection
   ✅ DO:
      - Load only needed agents (selective mode)
      - Group related agents in runtimes
      - Document which agents do what
   
   ❌ DON'T:
      - Always load all agents (wastes memory)
      - Mix unrelated agents in same runtime

5. Error Handling
   ✅ DO:
      - Check runtime status before using
      - Monitor last_error field
      - Deactivate failed runtimes
   
   ❌ DON'T:
      - Ignore runtime errors
      - Use ERROR status runtimes without fixing


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

Problem: Agents not loading from runtime

Debug Steps:
1. Check runtime exists and is ACTIVE
   GET /bedrock-runtimes/{runtime_id}
   
2. Verify agents are assigned
   GET /bedrock-runtimes/{runtime_id}/agents
   
3. Check agent enabled status
   GET /agents
   
4. Look at logs for specific errors
   Check bedrock_dynamic_entrypoint logs
   
Solution:
- Activate runtime: POST /bedrock-runtimes/{runtime_id}/activate
- Add agents: PUT /bedrock-runtimes/{runtime_id}/agents
- Enable agents: PUT /agents/{agent_id}


Problem: "Memory must be between 128 and 10240 MB"

Debug Steps:
1. Check memory_mb value in request
2. Verify it's within valid range

Solution:
- For development: use 512-1024 MB
- For production: use 1024-2048 MB
- Never exceed 10240 MB


Problem: Runtime in ERROR status

Debug Steps:
1. Check last_error field
   GET /bedrock-runtimes/{runtime_id}
   
2. Review bedrock logs for error details

Solution:
- Fix the error (e.g., add missing agent)
- Deactivate runtime: POST /bedrock-runtimes/{runtime_id}/deactivate
- Make corrections
- Reactivate: POST /bedrock-runtimes/{runtime_id}/activate


# ============================================================================
# PYTHON EXAMPLES
# ============================================================================

Example 1: Load from Runtime Configuration

import requests

runtime_id = 1

payload = {
    "prompt": "Process latest tickets",
    "runtime_id": runtime_id,
    "actor_id": "user-123",
    "session_id": "session-456"
}

response = requests.post(
    "http://localhost:8000/bedrock/invoke",
    json=payload
)

result = response.json()
print(f"Result: {result}")


Example 2: Selective Agent Loading

payload = {
    "prompt": "Generate reports",
    "selected_agent_names": ["ReportGenerator", "DataAnalyzer"],
    "actor_id": "user-456"
}

response = requests.post(
    "http://localhost:8000/bedrock/invoke",
    json=payload
)


Example 3: Create and Manage Runtimes

import requests

# Create runtime
runtime_data = {
    "name": "my-runtime",
    "description": "My runtime configuration",
    "selected_agent_ids": [1, 2],
    "environment": "prod"
}

response = requests.post(
    "http://localhost:8000/bedrock-runtimes",
    json=runtime_data
)

runtime = response.json()["data"]
print(f"Created runtime: {runtime['id']}")

# Activate runtime
response = requests.post(
    f"http://localhost:8000/bedrock-runtimes/{runtime['id']}/activate"
)

# Use runtime
invoke_payload = {
    "prompt": "Do something",
    "runtime_id": runtime["id"],
    "actor_id": "user-123"
}

response = requests.post(
    "http://localhost:8000/bedrock/invoke",
    json=invoke_payload
)


# ============================================================================
# NEXT STEPS
# ============================================================================

1. ✅ Understand the three agent loading modes
   - Runtime config (database-driven)
   - Selective agents (ad-hoc selection)
   - Default (all enabled agents)

2. ✅ Create runtime configurations for your use cases
   - Create one for each environment
   - Create one for each workflow

3. ✅ Test agent loading
   - Verify agents load correctly
   - Monitor performance
   - Optimize agent selection

4. ✅ Integrate into your application
   - Update application code
   - Test end-to-end workflows
   - Monitor in production

5. ✅ Optimize based on usage
   - Track which agents are used
   - Remove unused agents from runtimes
   - Adjust memory and timeout settings

For more details, see BEDROCK_RUNTIME_DATABASE_MANAGEMENT.md
"""
