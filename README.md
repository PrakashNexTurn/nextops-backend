# NexTOps Backend Metadata Service

A FastAPI backend service for the NexTOps platform that stores and manages metadata required to dynamically create AI agents. This backend acts as a configuration control plane without executing agents.

## Overview

The NexTOps Backend serves as a metadata repository for:
- **Custom Tools** - Executable capabilities with Python implementation
- **MCP Servers** - Model Context Protocol server definitions
- **MCP Tools** - Tools exposed by MCP servers
- **Cloud Accounts** - Multi-cloud provider credentials management
- **AI Agents** - Agent definitions with assigned tools
- **Planner Agents** - Orchestrator agents that coordinate multiple agents
- **Agent Deployments** - Deployment configuration and status tracking
- **Sessions** - User sessions associated with planner agents

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI 0.109.0 |
| Language | Python 3.11 |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Schema Validation | Pydantic 2.5 |
| Database Migrations | Alembic 1.13 |
| API Documentation | Swagger/OpenAPI |

## Project Structure

```
nextops-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── api/
│   │   ├── tools.py            # Tools endpoints
│   │   ├── mcps.py             # MCP servers endpoints
│   │   ├── agents.py           # Agents endpoints
│   │   ├── planners.py         # Planners endpoints
│   │   ├── sessions.py         # Sessions endpoints
│   │   ├── deployments.py      # Deployments endpoints
│   │   └── clouds.py           # Cloud accounts endpoints
│   ├── models/
│   │   ├── tool.py             # Tool SQLAlchemy model
│   │   ├── mcp.py              # MCP SQLAlchemy model
│   │   ├── mcp_tool.py         # MCP Tool SQLAlchemy model
│   │   ├── agent.py            # Agent SQLAlchemy model
│   │   ├── agent_tool.py       # Agent-Tool association model
│   │   ├── planner.py          # Planner SQLAlchemy model
│   │   ├── planner_agent.py    # Planner-Agent association model
│   │   ├── deployment.py       # Deployment SQLAlchemy model
│   │   ├── session.py          # Session SQLAlchemy model
│   │   └── cloud_account.py    # Cloud Account SQLAlchemy model
│   ├── schemas/
│   │   ├── tool_schema.py      # Tool Pydantic schemas
│   │   ├── mcp_schema.py       # MCP Pydantic schemas
│   │   ├── agent_schema.py     # Agent Pydantic schemas
│   │   ├── planner_schema.py   # Planner Pydantic schemas
│   │   └── session_schema.py   # Session, Cloud, Deployment schemas
│   ├── services/
│   │   └── mcp_discovery.py    # MCP tool discovery service
│   └── db/
│       ├── database.py         # Database connection & session
│       └── base.py             # SQLAlchemy declarative base
├── migrations/
│   ├── env.py                  # Alembic environment configuration
│   ├── script.py.mako          # Migration template
│   └── versions/
│       └── 001_initial.py      # Initial schema migration
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Database Schema

### Tools Table
```sql
CREATE TABLE tools (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  tool_type ENUM('custom', 'mcp') NOT NULL,
  python_code TEXT,
  mcp_id UUID FOREIGN KEY,
  tags JSON,
  created_at TIMESTAMP
);
```

### MCPs Table
```sql
CREATE TABLE mcps (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  type ENUM('stdio', 'sse') NOT NULL,
  command VARCHAR(255),
  url VARCHAR(255),
  args JSON,
  headers JSON,
  env_vars JSON,
  created_at TIMESTAMP
);
```

### MCP Tools Table
```sql
CREATE TABLE mcp_tools (
  id UUID PRIMARY KEY,
  mcp_id UUID NOT NULL FOREIGN KEY,
  tool_name VARCHAR(255) NOT NULL,
  description VARCHAR(255),
  input_schema JSON
);
```

### Cloud Accounts Table
```sql
CREATE TABLE cloud_accounts (
  id UUID PRIMARY KEY,
  provider ENUM('aws', 'azure', 'gcp') NOT NULL,
  name VARCHAR(255) UNIQUE NOT NULL,
  credentials JSON,
  region VARCHAR(255),
  created_at TIMESTAMP
);
```

### Agents Table
```sql
CREATE TABLE agents (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  system_prompt TEXT NOT NULL,
  tags JSON,
  created_at TIMESTAMP
);
```

### Agent Tools Association
```sql
CREATE TABLE agent_tools (
  id UUID PRIMARY KEY,
  agent_id UUID NOT NULL FOREIGN KEY,
  tool_id UUID NOT NULL FOREIGN KEY,
  created_at TIMESTAMP
);
```

### Planners Table
```sql
CREATE TABLE planners (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  system_prompt TEXT NOT NULL,
  tags JSON,
  created_at TIMESTAMP
);
```

### Planner Agents Association
```sql
CREATE TABLE planner_agents (
  id UUID PRIMARY KEY,
  planner_id UUID NOT NULL FOREIGN KEY,
  agent_id UUID NOT NULL FOREIGN KEY,
  created_at TIMESTAMP
);
```

### Deployments Table
```sql
CREATE TABLE deployments (
  id UUID PRIMARY KEY,
  agent_id UUID NOT NULL FOREIGN KEY,
  bedrock_agent_id VARCHAR(255),
  deployment_type ENUM('new', 'existing') NOT NULL,
  status ENUM('pending', 'deployed') NOT NULL,
  created_at TIMESTAMP
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  planner_id UUID NOT NULL FOREIGN KEY,
  tags JSON,
  created_at TIMESTAMP
);
```

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- pip or conda

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/PrakashNexTurn/nextops-backend.git
cd nextops-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nextops
APP_NAME=NexTOps Backend
APP_VERSION=1.0.0
DEBUG=True
```

5. **Run database migrations**
```bash
alembic upgrade head
```

## Running the Application

### Development Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

## API Endpoints

### Tools Endpoints
```
POST   /tools                    # Create tool
GET    /tools                    # List all tools
GET    /tools/{id}               # Get tool by ID
PUT    /tools/{id}               # Update tool
DELETE /tools/{id}               # Delete tool
```

### MCP Endpoints
```
POST   /mcps                     # Register MCP server
GET    /mcps                     # List all MCPs
GET    /mcps/{id}                # Get MCP by ID
PUT    /mcps/{id}                # Update MCP
DELETE /mcps/{id}                # Delete MCP
POST   /mcps/{id}/tools          # Add tool to MCP
GET    /mcps/{id}/tools          # List MCP tools
```

### Agents Endpoints
```
POST   /agents                   # Create agent
GET    /agents                   # List all agents
GET    /agents/{id}              # Get agent by ID
PUT    /agents/{id}              # Update agent
DELETE /agents/{id}              # Delete agent
POST   /agents/{id}/tools/{tid}  # Add tool to agent
DELETE /agents/{id}/tools/{tid}  # Remove tool from agent
```

### Planners Endpoints
```
POST   /planners                 # Create planner
GET    /planners                 # List all planners
GET    /planners/{id}            # Get planner by ID
PUT    /planners/{id}            # Update planner
DELETE /planners/{id}            # Delete planner
POST   /planners/{id}/agents/{aid}     # Add agent to planner
DELETE /planners/{id}/agents/{aid}     # Remove agent from planner
```

### Sessions Endpoints
```
POST   /sessions                 # Create session
GET    /sessions                 # List all sessions
GET    /sessions/{id}            # Get session by ID
PUT    /sessions/{id}            # Update session
DELETE /sessions/{id}            # Delete session
```

### Cloud Accounts Endpoints
```
POST   /clouds                   # Register cloud account
GET    /clouds                   # List all cloud accounts
GET    /clouds/{id}              # Get cloud account by ID
PUT    /clouds/{id}              # Update cloud account
DELETE /clouds/{id}              # Delete cloud account
```

### Deployments Endpoints
```
POST   /deployments              # Create deployment
GET    /deployments              # List all deployments
GET    /deployments/{id}         # Get deployment by ID
PUT    /deployments/{id}         # Update deployment
DELETE /deployments/{id}         # Delete deployment
```

## API Examples

### Create a Tool
```bash
curl -X POST http://localhost:8000/tools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_repo",
    "description": "Create GitHub repository",
    "tool_type": "custom",
    "python_code": "def create_repo(): pass",
    "tags": {"category": "github"}
  }'
```

### Create an Agent
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Terraform Agent",
    "description": "Handles terraform operations",
    "system_prompt": "You are a Terraform expert",
    "tools": ["tool_id_1", "tool_id_2"],
    "tags": {"category": "infrastructure"}
  }'
```

### Register an MCP Server
```bash
curl -X POST http://localhost:8000/mcps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-mcp",
    "type": "sse",
    "url": "https://api.github.com/mcp",
    "headers": {"Authorization": "Bearer TOKEN"}
  }'
```

### Create a Planner
```bash
curl -X POST http://localhost:8000/planners \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Infra Planner",
    "system_prompt": "You orchestrate infrastructure tasks",
    "agents": ["agent_id_1", "agent_id_2", "agent_id_3"],
    "tags": {"category": "infrastructure"}
  }'
```

### Create a Session
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Infra Session",
    "planner_id": "planner_id",
    "tags": {"environment": "production"}
  }'
```

## Database Migrations

### View Migration Status
```bash
alembic current
```

### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migrations
```bash
alembic downgrade -1
```

## Services

### MCP Discovery Service
Located in `app/services/mcp_discovery.py`, this service handles:
- MCP tool discovery from registered servers
- Tool definition caching
- MCP configuration validation
- Future auto-discovery capabilities

**Current Implementation**: Placeholder for manual tool input
**Future Enhancement**: Automatic tool discovery via MCP protocol

Usage:
```python
from app.services.mcp_discovery import MCPDiscoveryService

discovery = MCPDiscoveryService()
tools = await discovery.discover_tools(mcp_id, mcp_config)
is_valid = discovery.validate_mcp_config(mcp_type, config)
```

## Non-Functional Requirements

| Requirement | Target |
|------------|--------|
| API Response Time | < 300ms |
| Scalability | Support 500+ agents |
| Database Connections | 10 pool size, 20 overflow |
| Extensibility | New MCPs, cloud providers, agent types |

## Testing

### Run Tests (when test suite is added)
```bash
pytest tests/ -v
```

### Test with Swagger UI
1. Navigate to http://localhost:8000/docs
2. Try out endpoints directly in the browser

## Troubleshooting

### Database Connection Error
```
Error: could not translate host name "localhost" to address
```
**Solution**: Verify PostgreSQL is running and credentials in `.env` are correct

### Alembic Not Finding Models
```
Error: Target database is not up to date
```
**Solution**: Run `alembic upgrade head`

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: Use different port: `uvicorn app.main:app --port 8001`

## Performance Optimization

- Connection pooling: 10 pool size, 20 max overflow
- `pool_pre_ping=True` ensures connection validity
- UUID primary keys for distributed scalability
- JSON fields for flexible metadata storage
- Indexed unique constraints on entity names

## Security Considerations

- Cloud credentials stored in encrypted JSON fields
- All timestamps in UTC
- No sensitive data in logs
- Environment-based configuration
- CORS enabled for cross-origin requests

## Future Enhancements

1. **MCP Auto-Discovery**: Implement automatic tool discovery from MCP servers
2. **Agent Execution Runtime**: Build agent execution engine
3. **Audit Logging**: Track all configuration changes
4. **Role-Based Access Control**: User permissions and roles
5. **API Rate Limiting**: Prevent abuse
6. **Webhook Support**: Real-time notifications for changes
7. **Advanced Filtering**: Complex queries on metadata
8. **Tool Versioning**: Support multiple tool versions
9. **Agent Templates**: Pre-built agent configurations
10. **Performance Monitoring**: Metrics and observability

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add enhancement'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

## License

[Add appropriate license]

## Support

For issues and questions:
- Create an issue in GitHub
- Contact the development team
- Check documentation at http://localhost:8000/docs

## Deployment

### Docker (Future)
```bash
docker build -t nextops-backend .
docker run -e DATABASE_URL=postgresql://... -p 8000:8000 nextops-backend
```

### Kubernetes (Future)
See `k8s/` directory for Kubernetes manifests

### Environment Variables
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=nextops
APP_NAME=NexTOps Backend
APP_VERSION=1.0.0
DEBUG=False
```

---

**Version**: 1.0.0
**Last Updated**: 2026-03-07
**Status**: Production Ready
