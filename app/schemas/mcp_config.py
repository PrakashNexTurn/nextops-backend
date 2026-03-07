"""
Pydantic schemas for dynamic MCP client configuration.
Supports HTTP (Streamable, with auth), Stdio (Python, NPM), and other MCP server types.
"""

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field, validator


class MCPClientConfig(BaseModel):
    """
    Dynamic MCP client configuration.
    
    Supports:
    - HTTP servers (streamable_http) with optional bearer token auth
    - Stdio servers (Python scripts, local commands)
    - NPM package servers (kubernetes, terraform, postgres, gcp)
    
    Examples:
        # HTTP with bearer token
        {
            "server_type": "http",
            "endpoint": "https://mcp.exa.ai/mcp",
            "auth_headers": {"Authorization": "Bearer token_here"}
        }
        
        # Stdio Python server
        {
            "server_type": "stdio",
            "command": "python",
            "args": ["/path/to/server.py"],
            "env_vars": {"GITHUB_TOKEN": "ghp_xxx"}
        }
        
        # NPM package
        {
            "server_type": "npm",
            "package": "mcp-server-kubernetes",
            "args": ["--config", "/path/to/config"],
            "env_vars": {"K8S_CONFIG": "/path/to/kubeconfig"}
        }
    """
    
    server_type: Literal["http", "stdio", "npm"] = Field(
        ...,
        description="Type of MCP server: 'http' (streamable_http), 'stdio' (local command), 'npm' (npm package)"
    )
    
    # HTTP Server Configuration
    endpoint: Optional[str] = Field(
        None,
        description="HTTP endpoint URL for streamable_http servers (required for server_type='http')"
    )
    auth_headers: Optional[Dict[str, str]] = Field(
        None,
        description="Optional authentication headers for HTTP servers (e.g., {'Authorization': 'Bearer token'})"
    )
    
    # Stdio Server Configuration
    command: Optional[str] = Field(
        None,
        description="Command to execute for stdio servers (required for server_type='stdio'). Examples: 'python', '/usr/bin/node', 'npx'"
    )
    args: Optional[List[str]] = Field(
        None,
        description="Command arguments for stdio servers. Examples: ['/path/to/script.py', '--config', 'file.yml']"
    )
    
    # NPM Server Configuration
    package: Optional[str] = Field(
        None,
        description="NPM package name for npm servers (required for server_type='npm'). Examples: 'mcp-server-kubernetes', 'mcp-postgres-server'"
    )
    
    # Environment Variables (shared across all types)
    env_vars: Optional[Dict[str, str]] = Field(
        None,
        description="Environment variables to pass to the MCP server"
    )
    
    # Timeout Configuration
    timeout: int = Field(
        600,
        ge=1,
        description="Timeout in seconds for MCP server communication (default: 600)"
    )
    
    # Validation
    class Config:
        schema_extra = {
            "examples": [
                {
                    "server_type": "http",
                    "endpoint": "https://mcp.exa.ai/mcp",
                    "auth_headers": {"Authorization": "Bearer your_token"},
                    "timeout": 600
                },
                {
                    "server_type": "stdio",
                    "command": "python",
                    "args": ["/app/mcp_servers/azure_mcp_server.py"],
                    "env_vars": {"AZURE_TENANT_ID": "xxx"},
                    "timeout": 600
                },
                {
                    "server_type": "npm",
                    "package": "mcp-server-kubernetes",
                    "env_vars": {"KUBECONFIG": "/home/user/.kube/config"},
                    "timeout": 600
                }
            ]
        }
    
    @validator("endpoint")
    def endpoint_required_for_http(cls, v, values):
        """Ensure endpoint is provided for HTTP servers."""
        if values.get("server_type") == "http" and not v:
            raise ValueError("'endpoint' is required when server_type='http'")
        return v
    
    @validator("command")
    def command_required_for_stdio(cls, v, values):
        """Ensure command is provided for Stdio servers."""
        if values.get("server_type") == "stdio" and not v:
            raise ValueError("'command' is required when server_type='stdio'")
        return v
    
    @validator("package")
    def package_required_for_npm(cls, v, values):
        """Ensure package is provided for NPM servers."""
        if values.get("server_type") == "npm" and not v:
            raise ValueError("'package' is required when server_type='npm'")
        return v


class MCPClientResponse(BaseModel):
    """Response from dynamic MCP client initialization."""
    
    success: bool = Field(..., description="Whether client initialization was successful")
    mcp_id: Optional[str] = Field(None, description="MCP server ID (if created in database)")
    server_type: str = Field(..., description="Type of MCP server initialized")
    endpoint_or_command: str = Field(..., description="HTTP endpoint or command used")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if initialization failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "mcp_id": "123e4567-e89b-12d3-a456-426614174000",
                "server_type": "http",
                "endpoint_or_command": "https://mcp.exa.ai/mcp",
                "message": "MCP client initialized successfully"
            }
        }


class MCPClientListResponse(BaseModel):
    """List of available MCP clients/servers."""
    
    total: int = Field(..., description="Total number of MCP servers")
    servers: List[Dict[str, str]] = Field(..., description="List of available servers with their IDs and types")
    
    class Config:
        schema_extra = {
            "example": {
                "total": 4,
                "servers": [
                    {
                        "id": "github-mcp",
                        "type": "http",
                        "endpoint_or_command": "https://api.githubcopilot.com/mcp"
                    },
                    {
                        "id": "azure-mcp",
                        "type": "stdio",
                        "endpoint_or_command": "python /app/mcp_servers/azure_mcp_server.py"
                    }
                ]
            }
        }
