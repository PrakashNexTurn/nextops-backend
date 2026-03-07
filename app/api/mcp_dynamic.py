"""
FastAPI endpoints for dynamic MCP client initialization and management.

Provides REST API for:
- Creating dynamic MCP clients from configuration
- Listing registered MCP clients
- Managing MCP server lifecycle
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.schemas.mcp_config import MCPClientConfig, MCPClientResponse, MCPClientListResponse
from app.services.mcp_factory import get_mcp_client_manager, MCPClientFactory

router = APIRouter(prefix="/mcps", tags=["mcps"])


# Request/Response Models
class MCPInitializeRequest(BaseModel):
    """Request to initialize a new MCP client."""
    client_id: Optional[str] = None  # Auto-generated if not provided
    config: MCPClientConfig


class MCPInitializeResponse(MCPClientResponse):
    """Response from MCP initialization."""
    pass


class MCPListRequest(BaseModel):
    """Request to list MCP clients."""
    include_config: bool = False


# Endpoints
@router.post("/initialize", response_model=MCPInitializeResponse, status_code=status.HTTP_201_CREATED)
async def initialize_mcp_client(request: MCPInitializeRequest) -> MCPInitializeResponse:
    """
    Initialize a new MCP client dynamically based on configuration.
    
    Supports:
    - HTTP servers (streamable_http) with optional bearer token auth
    - Stdio servers (Python scripts, local commands)
    - NPM package servers (kubernetes, terraform, postgres, gcp)
    
    Example requests:
    
    **HTTP Server:**
    ```json
    {
        "client_id": "github-mcp",
        "config": {
            "server_type": "http",
            "endpoint": "https://api.githubcopilot.com/mcp",
            "auth_headers": {"Authorization": "Bearer ghp_token"},
            "timeout": 600
        }
    }
    ```
    
    **Stdio Server:**
    ```json
    {
        "client_id": "azure-mcp",
        "config": {
            "server_type": "stdio",
            "command": "python",
            "args": ["/app/mcp_servers/azure_mcp_server.py"],
            "env_vars": {"AZURE_TENANT_ID": "xxx"},
            "timeout": 600
        }
    }
    ```
    
    **NPM Package:**
    ```json
    {
        "client_id": "kubernetes-mcp",
        "config": {
            "server_type": "npm",
            "package": "mcp-server-kubernetes",
            "env_vars": {"KUBECONFIG": "/home/user/.kube/config"},
            "timeout": 600
        }
    }
    ```
    """
    try:
        # Generate client ID if not provided
        client_id = request.client_id or f"mcp_{request.config.server_type}_{id(request)}"
        
        # Get the client manager
        manager = get_mcp_client_manager()
        
        # Register the client
        success, error_msg = manager.register_client(client_id, request.config)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to initialize MCP client: {error_msg}"
            )
        
        # Determine endpoint or command string for response
        endpoint_or_cmd = (
            request.config.endpoint 
            or f"{request.config.command} {' '.join(request.config.args or [])}"
            or request.config.package
        )
        
        return MCPInitializeResponse(
            success=True,
            mcp_id=client_id,
            server_type=request.config.server_type,
            endpoint_or_command=endpoint_or_cmd,
            message=f"MCP client '{client_id}' initialized successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing MCP client: {str(e)}"
        )


@router.get("/list", response_model=MCPClientListResponse)
async def list_mcp_clients() -> MCPClientListResponse:
    """
    List all registered MCP clients.
    
    Returns:
    - Total number of clients
    - List of client IDs, types, and endpoints/commands
    """
    try:
        manager = get_mcp_client_manager()
        clients = manager.list_clients()
        
        servers = [
            {
                "id": client_id,
                "type": info["type"],
                "endpoint_or_command": info["endpoint_or_command"]
            }
            for client_id, info in clients.items()
        ]
        
        return MCPClientListResponse(
            total=len(servers),
            servers=servers
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing MCP clients: {str(e)}"
        )


@router.get("/{client_id}/status")
async def get_client_status(client_id: str):
    """
    Get the status of a specific MCP client.
    
    Returns:
    - Client configuration
    - Creation timestamp
    - Connection status
    """
    try:
        manager = get_mcp_client_manager()
        clients = manager.list_clients()
        
        if client_id not in clients:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP client not found: {client_id}"
            )
        
        client_info = clients[client_id]
        
        return {
            "client_id": client_id,
            "status": "active",
            "type": client_info["type"],
            "endpoint_or_command": client_info["endpoint_or_command"],
            "message": "Client is registered and ready"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting client status: {str(e)}"
        )


@router.delete("/{client_id}")
async def unregister_mcp_client(client_id: str):
    """
    Unregister and remove an MCP client.
    
    Args:
        client_id: ID of the client to remove
    """
    try:
        manager = get_mcp_client_manager()
        
        if not manager.unregister_client(client_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP client not found: {client_id}"
            )
        
        return {
            "success": True,
            "message": f"MCP client '{client_id}' unregistered successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unregistering MCP client: {str(e)}"
        )


@router.post("/validate-config")
async def validate_mcp_config(config: MCPClientConfig):
    """
    Validate MCP configuration without creating a client.
    
    Returns validation result and any errors.
    """
    try:
        is_valid, error_msg = MCPClientFactory.validate_config(config)
        
        return {
            "valid": is_valid,
            "error": error_msg,
            "server_type": config.server_type,
            "message": "Configuration is valid" if is_valid else f"Configuration is invalid: {error_msg}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating MCP configuration: {str(e)}"
        )
