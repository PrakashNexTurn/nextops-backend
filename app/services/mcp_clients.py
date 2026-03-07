"""
Backward-compatible MCP client functions using the dynamic factory.

Provides the same functions as before but now using MCPClientFactory internally.
This maintains API compatibility while enabling dynamic configuration.
"""

import os
import sys
from pathlib import Path

from app.schemas.mcp_config import MCPClientConfig
from app.services.mcp_factory import MCPClientFactory


def get_streamable_http_mcp_client():
    """
    Returns an MCP Client compatible with Strands for ExaAI.
    Uses dynamic factory with HTTP configuration.
    """
    config = MCPClientConfig(
        server_type="http",
        endpoint="https://mcp.exa.ai/mcp",
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_github_http_mcp_client():
    """
    Returns an MCP Client compatible with Strands for GitHub Copilot API.
    Uses dynamic factory with HTTP + bearer token authentication.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    config = MCPClientConfig(
        server_type="http",
        endpoint="https://api.githubcopilot.com/mcp",
        auth_headers={"Authorization": f"Bearer {github_token}"},
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_azure_mcp():
    """
    Returns an Azure MCP Client that runs the local azure_mcp_server.py.
    Uses dynamic factory with stdio Python script.
    """
    server_path = Path(__file__).parent.parent / "mcp_servers" / "azure_mcp_server.py"
    
    if not server_path.exists():
        raise ValueError(f"Azure MCP server not found at: {server_path}")
    
    config = MCPClientConfig(
        server_type="stdio",
        command=sys.executable,
        args=[str(server_path)],
        env_vars={k: v for k, v in os.environ.items()},
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_servicenow_mcp():
    """
    Returns a ServiceNow MCP Client that runs the local servicenow_mcp_server.py.
    Uses dynamic factory with stdio Python script.
    """
    server_path = Path(__file__).parent.parent / "mcp_servers" / "servicenow_mcp_server.py"
    
    if not server_path.exists():
        raise ValueError(f"ServiceNow MCP server not found at: {server_path}")
    
    config = MCPClientConfig(
        server_type="stdio",
        command=sys.executable,
        args=[str(server_path)],
        env_vars={k: v for k, v in os.environ.items()},
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_kubernetes_mcp():
    """
    Returns a Kubernetes MCP Client using NPM package.
    Uses dynamic factory with npm stdio.
    """
    config = MCPClientConfig(
        server_type="npm",
        package="mcp-server-kubernetes",
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_terraform_mcp():
    """
    Returns a Terraform MCP Client.
    Uses dynamic factory with terraform-mcp-server binary.
    """
    config = MCPClientConfig(
        server_type="stdio",
        command="/usr/bin/terraform-mcp-server",
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_postgres_mcp():
    """
    Returns a Postgres MCP Client using NPM package.
    Uses dynamic factory with npm stdio and environment variables.
    """
    config = MCPClientConfig(
        server_type="npm",
        package="mcp-postgres-server",
        env_vars={
            "PG_HOST": os.getenv("PG_HOST", ""),
            "PG_PORT": os.getenv("PG_PORT", "5432"),
            "PG_USER": os.getenv("PG_USER", ""),
            "PG_PASSWORD": os.getenv("PG_PASSWORD", ""),
            "PG_DATABASE": os.getenv("PG_DATABASE", ""),
        },
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_gcp_mcp():
    """
    Returns a GCP MCP Client backed by @google-cloud/gcloud-mcp via npx.
    Uses dynamic factory with npm stdio and gcloud authentication.
    """
    config = MCPClientConfig(
        server_type="npm",
        package="@google-cloud/gcloud-mcp",
        timeout=600
    )
    return MCPClientFactory.create(config)


# Export all functions for backward compatibility
__all__ = [
    "get_streamable_http_mcp_client",
    "get_github_http_mcp_client",
    "get_azure_mcp",
    "get_servicenow_mcp",
    "get_kubernetes_mcp",
    "get_terraform_mcp",
    "get_postgres_mcp",
    "get_gcp_mcp",
]
