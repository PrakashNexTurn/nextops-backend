"""
Backward-compatible MCP client functions using the dynamic factory.

IMPORTANT: This module now uses database-driven dynamic configuration.
For new implementations, use DynamicMCPClientService instead of these functions.

Provides the same functions as before but now using:
1. MCPClientFactory - for hardcoded configurations (backward compat)
2. DynamicMCPClientService - for database-driven configurations (recommended)

Migration Path:
- Old: get_github_http_mcp_client() → hardcoded
- New: get_mcp_client_by_name("github-mcp", db) → from database

This maintains API compatibility while enabling dynamic configuration.
"""

import os
import sys
from pathlib import Path

from app.schemas.mcp_config import MCPClientConfig
from app.services.mcp_factory import MCPClientFactory


# ============================================================================
# LEGACY HARDCODED FUNCTIONS - DEPRECATED
# For backward compatibility only. Use dynamic service instead.
# ============================================================================

def get_streamable_http_mcp_client():
    """
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns an MCP Client compatible with Strands for ExaAI.
    Uses hardcoded HTTP configuration.
    """
    config = MCPClientConfig(
        server_type="http",
        endpoint="https://mcp.exa.ai/mcp",
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_github_http_mcp_client():
    """
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns an MCP Client compatible with Strands for GitHub Copilot API.
    Uses hardcoded HTTP configuration with bearer token authentication.
    
    Example of migrating to dynamic:
        from app.services.mcp_dynamic_client import get_mcp_client_by_name
        from app.db.database import get_db
        
        db = next(get_db())
        client = get_mcp_client_by_name("github-mcp", db)
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
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns an Azure MCP Client that runs the local azure_mcp_server.py.
    Uses hardcoded stdio Python script configuration.
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
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns a ServiceNow MCP Client that runs the local servicenow_mcp_server.py.
    Uses hardcoded stdio Python script configuration.
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
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns a Kubernetes MCP Client using NPM package.
    Uses hardcoded npm stdio configuration.
    """
    config = MCPClientConfig(
        server_type="npm",
        package="mcp-server-kubernetes",
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_terraform_mcp():
    """
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns a Terraform MCP Client.
    Uses hardcoded terraform-mcp-server binary.
    """
    config = MCPClientConfig(
        server_type="stdio",
        command="/usr/bin/terraform-mcp-server",
        timeout=600
    )
    return MCPClientFactory.create(config)


def get_postgres_mcp():
    """
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns a Postgres MCP Client using NPM package.
    Uses hardcoded npm stdio with environment variables.
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
    ⚠️  DEPRECATED: Use DynamicMCPClientService instead.
    
    Returns a GCP MCP Client backed by @google-cloud/gcloud-mcp via npx.
    Uses hardcoded npm stdio with gcloud authentication.
    """
    config = MCPClientConfig(
        server_type="npm",
        package="@google-cloud/gcloud-mcp",
        timeout=600
    )
    return MCPClientFactory.create(config)


# ============================================================================
# NEW RECOMMENDED APPROACH - Use Dynamic Service
# ============================================================================

def get_mcp_client_factory():
    """
    Get the MCPClientFactory for creating clients from configuration dicts.
    
    Recommended for:
    - Creating clients from API input
    - Dynamic configuration without database
    - Testing and development
    
    Example:
        config_dict = {
            "server_type": "http",
            "endpoint": "https://api.example.com/mcp",
            "timeout": 600
        }
        client = MCPClientFactory.create(
            MCPClientConfig(**config_dict)
        )
    """
    return MCPClientFactory


def get_dynamic_mcp_service():
    """
    Get the DynamicMCPClientService for database-driven client creation.
    
    Recommended for:
    - Production systems
    - Managing multiple MCP servers
    - Persistent configurations
    - Scalable, maintainable code
    
    Example:
        from app.db.database import get_db
        service = get_dynamic_mcp_service()
        db = next(get_db())
        
        # Get client by ID
        client = service.get_mcp_client_by_id(mcp_id, db)
        
        # Get client by name
        client = service.get_mcp_client_by_name("github-mcp", db)
        
        # List all available MCPs
        mcps = service.list_all_mcp_clients(db)
    """
    from app.services.mcp_dynamic_client import get_dynamic_mcp_service as _get_service
    return _get_service()


# ============================================================================
# EXPORTS
# ============================================================================

# Export all legacy functions for backward compatibility
__all__ = [
    # Legacy hardcoded functions (deprecated)
    "get_streamable_http_mcp_client",
    "get_github_http_mcp_client",
    "get_azure_mcp",
    "get_servicenow_mcp",
    "get_kubernetes_mcp",
    "get_terraform_mcp",
    "get_postgres_mcp",
    "get_gcp_mcp",
    
    # New recommended functions
    "get_mcp_client_factory",
    "get_dynamic_mcp_service",
    
    # Direct imports for convenience
    "MCPClientFactory",
]

# Import for direct access
MCPClientFactory = MCPClientFactory
