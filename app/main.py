from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import engine
from app.db.base import Base

# Import all models to register them with Base
from app.models.tool import Tool
from app.models.mcp import MCP
from app.models.mcp_tool import MCPTool
from app.models.agent import Agent
from app.models.agent_tool import AgentTool
from app.models.planner import Planner
from app.models.planner_agent import PlannerAgent
from app.models.deployment import Deployment
from app.models.session import Session
from app.models.cloud_account import CloudAccount

# Import API routers
from app.api import tools, mcps, agents, planners, sessions, deployments, clouds

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend metadata service for NexTOps dynamic AI agent configuration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tools.router)
app.include_router(mcps.router)
app.include_router(agents.router)
app.include_router(planners.router)
app.include_router(sessions.router)
app.include_router(deployments.router)
app.include_router(clouds.router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
