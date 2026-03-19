# SQLAlchemy models package
# Import order is critical: junction tables must be imported before parent models

# Base models first (no dependencies)
from app.models.cloud_account import CloudAccount
from app.models.session import Session
from app.models.tool import Tool

# Junction tables BEFORE their parent models
# (MCP has relationship to MCPTool)
from app.models.mcp_tool import MCPTool
# (Agent has relationships to AgentTool and AgentMCP)
from app.models.agent_tool import AgentTool
from app.models.agent_mcp import AgentMCP

# Parent models that reference junction tables
from app.models.mcp import MCP
from app.models.agent import Agent, AgentTemplate

# Higher-level models
from app.models.planner import Planner
from app.models.planner_agent import PlannerAgent
from app.models.deployment import Deployment
from app.models.bedrock_runtime import BedrockRuntime

__all__ = [
    "CloudAccount",
    "Session",
    "Tool",
    "MCPTool",
    "AgentTool",
    "AgentMCP",
    "MCP",
    "Agent",
    "AgentTemplate",
    "Planner",
    "PlannerAgent",
    "Deployment",
    "BedrockRuntime",
]
