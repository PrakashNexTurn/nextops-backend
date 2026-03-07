"""
INTEGRATION GUIDE - Register Bedrock Runtime API Routes

This guide shows how to integrate the new Bedrock Runtime API endpoints
into your FastAPI application.
"""

# ============================================================================
# INTEGRATION STEPS
# ============================================================================

Step 1: Add Router Import to app/main.py
─────────────────────────────────────────

Open app/main.py and add the import:

from app.api.bedrock_runtime_routes import router as bedrock_runtime_router

# Example app/main.py structure:
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api import agents_routes, mcp_routes, bedrock_runtime_routes

# Create FastAPI app
app = FastAPI(
    title="NextOps Backend API",
    description="API for managing agents, MCPs, and Bedrock runtimes",
    version="1.0.0"
)

# Include routers
app.include_router(agents_routes.router)
app.include_router(mcp_routes.router)
app.include_router(bedrock_runtime_routes.router)  # ADD THIS LINE
"""


Step 2: Register Bedrock Runtime Router
────────────────────────────────────────

In app/main.py, find the router inclusion section and add:

from app.api.bedrock_runtime_routes import router as bedrock_runtime_router

app = FastAPI(...)

# Include existing routers
app.include_router(agents_routes.router)
app.include_router(mcp_routes.router)

# Add Bedrock Runtime router (NEW)
app.include_router(bedrock_runtime_router)

Complete example:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all routers
from app.api.agents_routes import router as agents_router
from app.api.mcp_routes import router as mcp_router
from app.api.bedrock_runtime_routes import router as bedrock_runtime_router
from app.db.database import Base, engine

# Create app
app = FastAPI(
    title="NextOps Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(agents_router, prefix="/api/v1", tags=["Agents"])
app.include_router(mcp_router, prefix="/api/v1", tags=["MCPs"])
app.include_router(bedrock_runtime_router, prefix="/api/v1", tags=["Bedrock Runtime"])

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```


Step 3: Create Alembic Migration (Optional but Recommended)
──────────────────────────────────────────────────────────

Generate migration:

$ alembic revision --autogenerate -m "Add bedrock_runtimes table"

This creates a new migration file in migrations/versions/

Run migration:

$ alembic upgrade head

Or manually create migration file migrations/versions/xxx_add_bedrock_runtimes.py:

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'bedrock_runtimes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('selected_agent_ids', postgresql.JSON, default=list),
        sa.Column('selected_agent_names', postgresql.JSON, default=list),
        sa.Column('aws_region', sa.String(50), default='us-east-1'),
        sa.Column('aws_account_id', sa.String(12)),
        sa.Column('memory_mb', sa.Integer(), default=512),
        sa.Column('timeout_seconds', sa.Integer(), default=300),
        sa.Column('max_concurrency', sa.Integer(), default=10),
        sa.Column('logging_level', sa.String(20), default='INFO'),
        sa.Column('vpc_enabled', sa.Boolean(), default=False),
        sa.Column('vpc_id', sa.String(50)),
        sa.Column('subnet_ids', postgresql.JSON, default=list),
        sa.Column('security_group_ids', postgresql.JSON, default=list),
        sa.Column('environment', sa.String(20), default='dev'),
        sa.Column('environment_variables', postgresql.JSON, default=dict),
        sa.Column('status', sa.Enum('active', 'inactive', 'archived', 'error', name='runtimestatus')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_error', sa.Text()),
        sa.Column('last_error_at', sa.DateTime()),
        sa.Column('tags', postgresql.JSON, default=dict),
        sa.Column('metadata', postgresql.JSON, default=dict),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.Index('ix_bedrock_runtimes_name', 'name'),
        sa.Index('ix_bedrock_runtimes_status', 'status'),
        sa.Index('ix_bedrock_runtimes_environment', 'environment'),
    )

def downgrade():
    op.drop_table('bedrock_runtimes')
```


Step 4: Update database.py if using Direct Table Creation
──────────────────────────────────────────────────────────

If you're using Base.metadata.create_all() instead of migrations:

In app/db/database.py:

```python
from app.models.agent import Agent
from app.models.mcp import MCP
from app.models.bedrock_runtime import BedrockRuntime  # ADD THIS

# Create all tables
Base.metadata.create_all(bind=engine)
```


Step 5: Verify Installation
────────────────────────────

Test the new endpoints:

$ curl http://localhost:8000/bedrock-runtimes

Expected response:
{
    "status": "success",
    "data": [],
    "pagination": {
        "offset": 0,
        "limit": 100,
        "total": 0
    }
}


# ============================================================================
# API ENDPOINT STRUCTURE
# ============================================================================

After registration, the following endpoints are available:

PREFIX: /bedrock-runtimes

POST   /bedrock-runtimes                      Create runtime
GET    /bedrock-runtimes                      List runtimes
GET    /bedrock-runtimes/{runtime_id}         Get runtime
GET    /bedrock-runtimes/by-name/{name}       Get runtime by name
PUT    /bedrock-runtimes/{runtime_id}         Update runtime
DELETE /bedrock-runtimes/{runtime_id}         Delete runtime

POST   /bedrock-runtimes/{runtime_id}/activate      Activate runtime
POST   /bedrock-runtimes/{runtime_id}/deactivate    Deactivate runtime
POST   /bedrock-runtimes/{runtime_id}/archive       Archive runtime

GET    /bedrock-runtimes/{runtime_id}/agents  Get agents
PUT    /bedrock-runtimes/{runtime_id}/agents  Update agents

GET    /bedrock-runtimes/stats/summary        Get statistics


# ============================================================================
# TESTING THE INTEGRATION
# ============================================================================

Step 1: Start Application
─────────────────────────

$ python -m uvicorn app.main:app --reload

Output:
INFO:     Uvicorn running on http://127.0.0.1:8000


Step 2: Verify Endpoints are Available
──────────────────────────────────────

Check OpenAPI docs:
Visit http://localhost:8000/docs

You should see:
- Bedrock Runtimes section
- All endpoints listed
- Full request/response schemas


Step 3: Create a Test Runtime
──────────────────────────────

$ curl -X POST http://localhost:8000/bedrock-runtimes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-runtime",
    "description": "Test runtime",
    "environment": "dev"
  }'

Expected response (201 Created):
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "test-runtime",
        "description": "Test runtime",
        "status": "inactive",
        ...
    }
}


Step 4: Verify Database Storage
────────────────────────────────

$ psql -U postgres -d nextops_db

postgres=# SELECT id, name, status FROM bedrock_runtimes;

Should show:
 id |      name      | status
----+----------------+-----------
  1 | test-runtime   | inactive

(1 row)


# ============================================================================
# DOCKER INTEGRATION
# ============================================================================

If using Docker, update your docker-compose.yml:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: nextops_db
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/nextops_db
      BEDROCK_AGENTCORE_MEMORY_ID: your_memory_id
      AWS_REGION: us-east-1
    depends_on:
      - postgres
    volumes:
      - .:/app

volumes:
  postgres_data:
```

Build and run:

$ docker-compose up --build


# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

Required (for existing functionality):
  - DATABASE_URL: PostgreSQL connection string
  - BEDROCK_AGENTCORE_MEMORY_ID: Bedrock memory ID
  - AWS_REGION: AWS region (default: us-east-1)

Optional (for new runtime feature):
  - BEDROCK_RUNTIME_DEFAULT_MEMORY: Default memory (default: 512)
  - BEDROCK_RUNTIME_DEFAULT_TIMEOUT: Default timeout (default: 300)
  - BEDROCK_RUNTIME_MAX_MEMORY: Max memory (default: 10240)


# ============================================================================
# TROUBLESHOOTING INTEGRATION
# ============================================================================

Issue: "ModuleNotFoundError: No module named 'app.api.bedrock_runtime_routes'"
Solution:
  - Verify file exists: app/api/bedrock_runtime_routes.py
  - Check imports in file
  - Restart application

Issue: "404 Not Found" for /bedrock-runtimes endpoints
Solution:
  - Verify router is included in app/main.py
  - Check router prefix setting
  - Restart application with --reload

Issue: "Table bedrock_runtimes does not exist"
Solution:
  - Run Alembic migration: alembic upgrade head
  - Or ensure Base.metadata.create_all() is called
  - Verify PostgreSQL is running

Issue: "Column status does not exist"
Solution:
  - Run database migration
  - Drop and recreate tables if using create_all()
  - Check SQLAlchemy model definition

Issue: API returns 500 error
Solution:
  - Check application logs for traceback
  - Verify database connection
  - Verify agent IDs are valid
  - Check required fields are provided


# ============================================================================
# FILES TO VERIFY
# ============================================================================

After integration, verify these files exist and are correct:

✓ app/models/bedrock_runtime.py
  - Contains BedrockRuntime model
  - Contains RuntimeStatus enum
  - Contains bedrock_runtime_agents association table

✓ app/services/bedrock_runtime_service.py
  - Contains BedrockRuntimeService class
  - Implements all CRUD methods
  - Implements status management methods

✓ app/api/bedrock_runtime_routes.py
  - Contains API routes
  - Includes all endpoint handlers
  - Includes error handling

✓ bedrock_dynamic_entrypoint.py (updated)
  - Contains _load_agents_from_runtime()
  - Supports three agent loading modes
  - Properly integrated with runtime service

✓ app/main.py
  - Imports bedrock_runtime_router
  - Includes router in app.include_router()

✓ Database migrations (if using Alembic)
  - Migration file in migrations/versions/
  - Contains create bedrock_runtimes table


# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

Before deploying to production:

☐ All files created and updated
☐ Database migration created and tested
☐ API endpoints tested locally
☐ Error handling verified
☐ Documentation complete
☐ README updated with new endpoints
☐ Environment variables configured
☐ CORS settings appropriate for deployment
☐ API authentication/authorization (if needed)
☐ Rate limiting configured (if needed)
☐ Monitoring/logging set up
☐ Backup strategy for database


# ============================================================================
# SUCCESS INDICATORS
# ============================================================================

You'll know integration is successful when:

✅ Bedrock Runtime endpoints appear in OpenAPI docs
✅ You can create a runtime via POST /bedrock-runtimes
✅ Runtime appears in database table
✅ You can list runtimes via GET /bedrock-runtimes
✅ You can update and activate runtimes
✅ Bedrock entrypoint accepts runtime_id/runtime_name in payload
✅ Agents load correctly from runtime configuration
✅ No errors in application logs


# ============================================================================
# NEXT STEPS AFTER INTEGRATION
# ============================================================================

1. Create initial runtime configurations
2. Test with your existing agents
3. Update application code to use runtime_id
4. Monitor performance and error logs
5. Optimize agent selections based on usage
6. Document your runtime configurations
7. Train team on new capabilities
"""
