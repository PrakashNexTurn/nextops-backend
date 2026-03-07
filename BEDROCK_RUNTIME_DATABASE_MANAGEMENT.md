"""
BEDROCK RUNTIME DATABASE MANAGEMENT - IMPLEMENTATION COMPLETE

This document describes the database management system for Bedrock runtime configurations,
enabling database-driven agent initialization and runtime parameter management.
"""

# ============================================================================
# OVERVIEW
# ============================================================================

The implementation provides complete database management for Bedrock agent core runtimes:

1. **BedrockRuntime Model** (app/models/bedrock_runtime.py)
   - Stores runtime configurations in PostgreSQL
   - Manages selected agents, AWS parameters, and runtime settings
   - Includes status tracking and audit information

2. **BedrockRuntimeService** (app/services/bedrock_runtime_service.py)
   - CRUD operations for runtime configurations
   - Selective agent loading support
   - Status management and error tracking
   - Statistics and query methods

3. **Updated bedrock_dynamic_entrypoint.py**
   - Supports three agent loading modes
   - Database-driven runtime configuration
   - Selective agent initialization
   - Full backward compatibility

4. **REST API Endpoints** (app/api/bedrock_runtime_routes.py)
   - Complete CRUD operations
   - Status management
   - Agent assignment
   - Statistics and reporting


# ============================================================================
# KEY FEATURES
# ============================================================================

✅ Database-Managed Runtime Configuration
   - Store runtime settings in database
   - No code changes required for runtime updates
   - Version tracking with timestamps

✅ Selective Agent Initialization
   - Load only specified agents (not all)
   - Reduce memory footprint
   - Improve startup performance
   - Flexible agent selection

✅ Three Agent Loading Modes
   1. Runtime Config Mode: Load agents from database runtime
   2. Selective Mode: Load specific agent IDs or names
   3. Default Mode: Load all enabled agents (fallback)

✅ Complete Runtime Configuration
   - AWS region and account settings
   - Memory, timeout, concurrency parameters
   - VPC networking options
   - Environment variables
   - Logging configuration

✅ Status Management
   - ACTIVE / INACTIVE / ARCHIVED / ERROR states
   - Error tracking with timestamps
   - Easy activation/deactivation


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

Table: bedrock_runtimes

Columns:
  - id (INT PRIMARY KEY)
  - name (STRING UNIQUE) - Runtime name identifier
  - description (TEXT) - Runtime description
  - selected_agent_ids (JSON) - List of agent IDs [1, 2, 3]
  - selected_agent_names (JSON) - List of agent names ["Agent1", "Agent2"]
  - aws_region (STRING) - AWS region (us-east-1, us-west-2, etc.)
  - aws_account_id (STRING) - AWS account ID
  - memory_mb (INT) - Memory allocation (128-10240 MB)
  - timeout_seconds (INT) - Execution timeout in seconds
  - max_concurrency (INT) - Max concurrent executions
  - logging_level (STRING) - Logging level (ERROR, WARN, INFO, DEBUG)
  - vpc_enabled (BOOLEAN) - Enable VPC deployment
  - vpc_id (STRING) - VPC ID
  - subnet_ids (JSON) - List of subnet IDs
  - security_group_ids (JSON) - List of security group IDs
  - environment (STRING) - Environment (dev, staging, prod)
  - environment_variables (JSON) - Custom environment variables
  - status (ENUM) - Status (active, inactive, archived, error)
  - created_at (DATETIME) - Creation timestamp
  - updated_at (DATETIME) - Last update timestamp
  - last_error (TEXT) - Last error message
  - last_error_at (DATETIME) - Last error timestamp
  - tags (JSON) - Tags for categorization
  - metadata (JSON) - Additional metadata


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

Base URL: /bedrock-runtimes

CREATE RUNTIME
POST /bedrock-runtimes
Content-Type: application/json

Request Body:
{
    "name": "production-runtime",
    "description": "Production runtime configuration",
    "selected_agent_ids": [1, 2, 3],
    "selected_agent_names": ["DataProcessor", "ReportGenerator"],
    "aws_region": "us-east-1",
    "memory_mb": 1024,
    "timeout_seconds": 600,
    "max_concurrency": 20,
    "environment": "prod",
    "tags": {"team": "operations", "cost-center": "eng"},
    "metadata": {"version": "1.0"}
}

Response: 201 Created
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "production-runtime",
        "status": "inactive",
        "created_at": "2024-03-07T12:00:00",
        ...
    }
}


LIST RUNTIMES
GET /bedrock-runtimes?status=active&environment=prod&offset=0&limit=100

Query Parameters:
  - status: Filter by status (active, inactive, archived, error)
  - environment: Filter by environment (dev, staging, prod)
  - offset: Pagination offset (default: 0)
  - limit: Pagination limit (default: 100)

Response: 200 OK
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "production-runtime",
            "status": "active",
            ...
        }
    ],
    "pagination": {
        "offset": 0,
        "limit": 100,
        "total": 42
    }
}


GET RUNTIME BY ID
GET /bedrock-runtimes/{runtime_id}

Response: 200 OK
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "production-runtime",
        "selected_agent_ids": [1, 2, 3],
        "selected_agent_names": ["DataProcessor", "ReportGenerator"],
        ...
    }
}


GET RUNTIME BY NAME
GET /bedrock-runtimes/by-name/{name}

Response: 200 OK
Same as GET by ID


UPDATE RUNTIME
PUT /bedrock-runtimes/{runtime_id}
Content-Type: application/json

Request Body (only fields to update):
{
    "memory_mb": 2048,
    "timeout_seconds": 900,
    "tags": {"version": "2.0"}
}

Response: 200 OK
{
    "status": "success",
    "data": { ... }
}


UPDATE RUNTIME AGENTS
PUT /bedrock-runtimes/{runtime_id}/agents
Content-Type: application/json

Request Body:
{
    "agent_ids": [1, 4, 5],
    "agent_names": ["NewAgent", "AnotherAgent"]
}

Response: 200 OK
{
    "status": "success",
    "data": { ... }
}


ACTIVATE RUNTIME
POST /bedrock-runtimes/{runtime_id}/activate

Response: 200 OK
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "active",
        "last_error": null,
        ...
    }
}


DEACTIVATE RUNTIME
POST /bedrock-runtimes/{runtime_id}/deactivate

Response: 200 OK
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "inactive",
        ...
    }
}


ARCHIVE RUNTIME
POST /bedrock-runtimes/{runtime_id}/archive

Response: 200 OK
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "archived",
        ...
    }
}


GET RUNTIME AGENTS
GET /bedrock-runtimes/{runtime_id}/agents

Response: 200 OK
{
    "status": "success",
    "data": {
        "runtime_id": 1,
        "runtime_name": "production-runtime",
        "agents": [
            {"id": 1, "name": "DataProcessor"},
            {"id": 2, "name": "ReportGenerator"},
            {"id": 3, "name": "ApprovalWorkflow"}
        ]
    }
}


GET RUNTIME STATISTICS
GET /bedrock-runtimes/stats/summary

Response: 200 OK
{
    "status": "success",
    "data": {
        "total": 42,
        "active": 15,
        "inactive": 20,
        "archived": 5,
        "error": 2,
        "environments": {
            "dev": 15,
            "staging": 10,
            "prod": 17
        }
    }
}


DELETE RUNTIME
DELETE /bedrock-runtimes/{runtime_id}

Response: 204 No Content


# ============================================================================
# BEDROCK ENTRYPOINT AGENT LOADING MODES
# ============================================================================

The bedrock_dynamic_entrypoint.py now supports three agent loading modes:

MODE 1: Database Runtime Configuration
Load agents from BedrockRuntime configuration by ID or name:

Payload:
{
    "prompt": "Process these tickets",
    "runtime_id": 1,  # or "runtime_name": "production-runtime"
    "actor_id": "user-123",
    "session_id": "session-456"
}

Usage:
- Agents specified in runtime config are loaded
- Runtime parameters (memory, timeout, etc.) are available for reference
- Perfect for environment-specific configurations (dev, staging, prod)


MODE 2: Selective Agent Initialization
Load specific agents by ID or name:

Payload:
{
    "prompt": "Process tickets",
    "selected_agent_ids": [1, 2, 3],
    # OR
    "selected_agent_names": ["DataProcessor", "ReportGenerator"],
    "actor_id": "user-123"
}

Usage:
- Only specified agents are initialized
- Reduces memory footprint
- Faster startup time


MODE 3: Default (All Enabled Agents)
Load all enabled agents from database:

Payload:
{
    "prompt": "Process tickets",
    "actor_id": "user-123"
}

Usage:
- Backward compatible behavior
- Loads all agents with enabled=true
- Fallback if no runtime or selection specified


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

Step 1: Create Agents (existing)
POST /agents
{
    "name": "DataProcessor",
    "description": "Processes data",
    "system_prompt": "You are a data processor...",
    "enabled": true
}

Step 2: Create Runtime Configuration (NEW)
POST /bedrock-runtimes
{
    "name": "prod-data-pipeline",
    "description": "Production data processing pipeline",
    "selected_agent_names": ["DataProcessor", "ReportGenerator"],
    "aws_region": "us-east-1",
    "memory_mb": 1024,
    "timeout_seconds": 600,
    "environment": "prod"
}

Response:
{
    "id": 1,
    "name": "prod-data-pipeline",
    "status": "inactive",
    ...
}

Step 3: Activate Runtime
POST /bedrock-runtimes/1/activate

Response:
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "active",
        ...
    }
}

Step 4: Use Runtime in Bedrock Invocation
Invoke Bedrock with runtime_id:
{
    "prompt": "Process all pending tickets",
    "runtime_id": 1,
    "actor_id": "user-123"
}

Step 5: Monitor Runtime
GET /bedrock-runtimes/1

Check:
- status: active/inactive/archived/error
- last_error: Any error messages
- selected_agents: Which agents are configured
- timestamps: Creation and last update time


# ============================================================================
# SELECTIVE AGENT FACTORY INTEGRATION
# ============================================================================

The factory.create_agents_from_database() now supports selective initialization:

from app.services.agent_factory import AgentFactory

# Load specific agents by ID
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=[1, 2, 3],  # Load only agents with IDs 1, 2, 3
    enabled_only=True
)

# Load specific agents by name
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    selected_agents=["DataProcessor", "ReportGenerator"],
    enabled_only=True
)

# Load all enabled agents (default)
agents, stats = await factory.create_agents_from_database(
    actor_id="user-123",
    session_id="session-456",
    enabled_only=True
)

Returns:
- agents: List of initialized Agent objects
- stats: Dictionary with initialization statistics
  {
      "total": 10,
      "loaded": 3,
      "failed": 0,
      "not_found": 0,
      "errors": []
  }


# ============================================================================
# IMPLEMENTATION DETAILS
# ============================================================================

Files Created/Modified:

1. app/models/bedrock_runtime.py (NEW)
   - BedrockRuntime SQLAlchemy model
   - RuntimeStatus enum
   - Association table for runtime-agent relationship

2. app/services/bedrock_runtime_service.py (NEW)
   - BedrockRuntimeService class
   - CRUD operations
   - Query and filtering methods
   - Status management

3. bedrock_dynamic_entrypoint.py (UPDATED)
   - _load_agents_from_runtime() helper function
   - Support for runtime_id/runtime_name in payload
   - Support for selected_agent_ids/names in payload
   - Backward compatibility with default mode

4. app/api/bedrock_runtime_routes.py (NEW)
   - REST API router for runtime management
   - All CRUD endpoints
   - Status management endpoints
   - Statistics endpoint

Database Migration:
- Run Alembic migration to create bedrock_runtimes table
- Command: alembic upgrade head


# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

✅ Database
  [ ] Create bedrock_runtimes table
  [ ] Verify relationships with agents table
  [ ] Test permissions

✅ Application Code
  [ ] Deploy updated bedrock_dynamic_entrypoint.py
  [ ] Deploy BedrockRuntime model
  [ ] Deploy BedrockRuntimeService
  [ ] Deploy API routes

✅ API Routes
  [ ] Register /bedrock-runtimes router in app/main.py
  [ ] Test all endpoints
  [ ] Verify authentication/authorization

✅ Testing
  [ ] Create runtime configurations
  [ ] Activate/deactivate runtimes
  [ ] Test agent loading from runtime
  [ ] Test selective agent loading
  [ ] Test backward compatibility (no runtime param)

✅ Monitoring
  [ ] Monitor runtime statistics
  [ ] Track error occurrences
  [ ] Monitor agent initialization
  [ ] Log runtime activations/deactivations


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

Issue: "Runtime not found"
- Verify runtime_id or runtime_name exists
- Check runtime status is not ARCHIVED

Issue: "Agent with ID X not found"
- Verify agent IDs exist in database
- Use GET /agents to list available agents
- Check agent enabled status

Issue: "Memory must be between 128 and 10240 MB"
- Adjust memory_mb parameter to valid range
- Consult AWS documentation for recommended values

Issue: Agents not loading from runtime
- Verify runtime is in ACTIVE status
- Check selected_agent_ids or selected_agent_names
- Review bedrock_dynamic_entrypoint logs

Issue: Database connection error
- Verify DATABASE_URL environment variable
- Check PostgreSQL is running
- Verify database permissions


# ============================================================================
# NEXT STEPS
# ============================================================================

1. Create Database Migration
   - Generate Alembic migration for bedrock_runtimes table
   - Run migration in target environment

2. Register API Routes
   - Add router to app/main.py
   - Test endpoints locally

3. Create Initial Runtimes
   - Create runtime configurations for each environment
   - Activate production runtime

4. Update Documentation
   - Document runtime creation workflow
   - Document agent selection best practices
   - Create troubleshooting guide

5. Monitor and Optimize
   - Track runtime performance
   - Monitor agent loading times
   - Optimize agent selection based on usage patterns


# ============================================================================
# SUMMARY
# ============================================================================

The Bedrock Runtime Database Management system provides:

✅ Database-driven runtime configuration
✅ Selective agent initialization (reduce overhead)
✅ Three flexible agent loading modes
✅ Complete REST API for runtime management
✅ Status tracking and error handling
✅ Full backward compatibility
✅ Comprehensive logging and monitoring support

This enables DevOps teams to manage Bedrock agent configurations without code
changes, improving agility, security, and operational efficiency.
"""
