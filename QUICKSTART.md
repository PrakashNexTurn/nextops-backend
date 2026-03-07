# Quick Start Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Git

## Step 1: Clone Repository
```bash
git clone https://github.com/PrakashNexTurn/nextops-backend.git
cd nextops-backend
```

## Step 2: Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your PostgreSQL credentials
# Example:
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=mypassword
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=nextops
```

## Step 3: Set Up Database
```bash
chmod +x setup_db.sh
./setup_db.sh
```

This will:
- Create Python virtual environment
- Install dependencies
- Create database tables via migrations

## Step 4: Start Development Server
```bash
chmod +x run.sh
./run.sh
```

## Step 5: Access the API

### Web Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "NexTOps Backend",
  "version": "1.0.0"
}
```

## Example API Usage

### 1. Create a Tool
```bash
curl -X POST http://localhost:8000/tools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github_search",
    "description": "Search GitHub repositories",
    "tool_type": "custom",
    "python_code": "def search_repos(query): pass",
    "tags": {"category": "github"}
  }'
```

### 2. List Tools
```bash
curl http://localhost:8000/tools
```

### 3. Create an Agent
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Agent",
    "description": "Handles GitHub operations",
    "system_prompt": "You are a GitHub expert assistant",
    "tools": [],
    "tags": {"type": "github"}
  }'
```

### 4. Register MCP Server
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp-server",
    "type": "sse",
    "url": "https://api.github.com/mcp",
    "headers": {"Authorization": "Bearer YOUR_TOKEN"}
  }'
```

### 5. Create Planner
```bash
curl -X POST http://localhost:8000/planners \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Planner",
    "system_prompt": "Orchestrate GitHub operations",
    "agents": [],
    "tags": {"type": "github"}
  }'
```

## Troubleshooting

### Database Connection Failed
```
Error: could not connect to server
```
**Solution**:
1. Verify PostgreSQL is running: `psql -h localhost -U postgres`
2. Check credentials in `.env`
3. Ensure database exists: `createdb nextops`

### Port 8000 Already in Use
```
OSError: Address already in use
```
**Solution**: Use different port
```bash
python -m uvicorn app.main:app --port 8001 --reload
```

### ModuleNotFoundError
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Make sure you're in the repo root directory and venv is activated

### Alembic Migration Fails
```
Error: Target database is not up to date
```
**Solution**: 
```bash
alembic current
alembic upgrade head
```

## Development Workflow

### Create New Feature
1. Make code changes
2. Server auto-reloads (due to `--reload` flag)
3. Test via Swagger UI or curl
4. Check tests (if any)

### Run Migrations
```bash
# View current migration
alembic current

# Create new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Database Shell
```bash
# Connect to database
psql -h localhost -U postgres -d nextops

# List tables
\dt

# Describe table
\d tools

# Exit
\q
```

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Explore API endpoints in Swagger UI
3. Check [app/schemas/](app/schemas) for request/response formats
4. Review [app/models/](app/models) for database structure

## Documentation Links

- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://www.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev
- Alembic: https://alembic.sqlalchemy.org

## Support

For issues:
1. Check Troubleshooting section above
2. Review README.md
3. Check GitHub issues
4. Create a new issue with details

---

**Happy Coding!** 🚀
