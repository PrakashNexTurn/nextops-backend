"""
Dynamic MCP Client Service - Database-Driven Configuration

This module provides database-driven dynamic MCP client creation.
Instead of hardcoded functions, MCP clients are created from configurations
stored in the database, making the system fully scalable and flexible.

Key Features:
- Query MCP configurations from database
- Build MCPClient instances dynamically based on type and config
- Support multiple MCP server types (HTTP, Stdio, NPM)
- Cache client instances for performance
- Auto-discover MCP configurations at startup
"""

import logging
import os
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.mcp import MCP
from app.schemas.mcp_config import MCPClientConfig
from app.services.mcp_factory import MCPClientFactory, MCPClientManager

logger = logging.getLogger(__name__)


class DynamicMCPClientService:
    """
    Service for dynamically creating and managing MCP clients from database configuration.
    
    This service:
    1. Queries the MCP database for stored configurations
    2. Validates configurations
    3. Creates MCPClient instances using the factory
    4. Manages client lifecycle and caching
    5. Provides easy access methods (by ID, by name, list all)
    """
    
    def __init__(self):
        """Initialize the dynamic MCP client service."""
        self._client_manager = MCPClientManager()
        self._mcp_cache: Dict[UUID, Dict] = {}
        logger.info("DynamicMCPClientService initialized")
    
    def _mcp_to_config(self, mcp: MCP) -> MCPClientConfig:
        """
        Convert MCP database model to MCPClientConfig.
        
        Args:
            mcp: MCP database model instance
            
        Returns:
            MCPClientConfig instance
            
        Raises:
            ValueError: If MCP configuration is invalid
        """
        # Determine server type and extract relevant fields
        server_type = mcp.type.lower()
        
        if server_type == "http" or server_type == "sse":
            # HTTP/SSE type - requires URL
            if not mcp.url:
                raise ValueError(
                    f"MCP '{mcp.name}' is type 'http' but no URL provided"
                )
            
            config = MCPClientConfig(
                server_type="http",
                endpoint=mcp.url,
                auth_headers=mcp.headers or None,
                timeout=300  # Default timeout
            )
        
        elif server_type == "stdio":
            # Stdio type - requires command
            if not mcp.command:
                raise ValueError(
                    f"MCP '{mcp.name}' is type 'stdio' but no command provided"
                )
            
            config = MCPClientConfig(
                server_type="stdio",
                command=mcp.command,
                args=mcp.args or [],
                env_vars=mcp.env_vars or {},
                timeout=300  # Default timeout
            )
        
        elif server_type == "npm":
            # NPM type - requires package name
            if not mcp.command:  # Using 'command' field to store package name
                raise ValueError(
                    f"MCP '{mcp.name}' is type 'npm' but no package name provided"
                )
            
            config = MCPClientConfig(
                server_type="npm",
                package=mcp.command,  # Package name stored in command field
                args=mcp.args or [],
                env_vars=mcp.env_vars or {},
                timeout=300  # Default timeout
            )
        
        else:
            raise ValueError(f"Unknown MCP type: {server_type}")
        
        return config
    
    def get_mcp_client_by_id(self, mcp_id: UUID, db: Session) -> Optional[object]:
        """
        Get an MCP client by ID from database configuration.
        
        Process:
        1. Query database for MCP by ID
        2. Convert to MCPClientConfig
        3. Create client using factory
        4. Cache for future use
        
        Args:
            mcp_id: UUID of the MCP server
            db: SQLAlchemy session
            
        Returns:
            MCPClient instance or None if not found
            
        Raises:
            ValueError: If MCP configuration is invalid
        """
        try:
            # Check cache first
            if mcp_id in self._mcp_cache:
                logger.debug(f"Returning cached MCP client for ID: {mcp_id}")
                return self._mcp_cache[mcp_id]["client_func"]
            
            # Query database
            mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
            if not mcp:
                logger.warning(f"MCP not found in database: {mcp_id}")
                return None
            
            # Convert to config and create client
            config = self._mcp_to_config(mcp)
            client_func = MCPClientFactory.create(config)
            
            # Cache the client
            self._mcp_cache[mcp_id] = {
                "mcp": mcp,
                "config": config,
                "client_func": client_func
            }
            
            logger.info(
                f"Created dynamic MCP client for '{mcp.name}' (ID: {mcp_id}) "
                f"with type '{mcp.type}'"
            )
            return client_func
        
        except Exception as e:
            logger.error(
                f"Failed to get MCP client for ID {mcp_id}: {str(e)}"
            )
            raise
    
    def get_mcp_client_by_name(self, mcp_name: str, db: Session) -> Optional[object]:
        """
        Get an MCP client by name from database configuration.
        
        Args:
            mcp_name: Name of the MCP server (unique)
            db: SQLAlchemy session
            
        Returns:
            MCPClient instance or None if not found
            
        Raises:
            ValueError: If MCP configuration is invalid
        """
        try:
            # Query database by name
            mcp = db.query(MCP).filter(MCP.name == mcp_name).first()
            if not mcp:
                logger.warning(f"MCP not found in database: {mcp_name}")
                return None
            
            # Use ID-based method for consistency
            return self.get_mcp_client_by_id(mcp.id, db)
        
        except Exception as e:
            logger.error(
                f"Failed to get MCP client for name '{mcp_name}': {str(e)}"
            )
            raise
    
    def list_all_mcp_clients(self, db: Session) -> List[Dict]:
        """
        List all MCP server configurations from database.
        
        Args:
            db: SQLAlchemy session
            
        Returns:
            List of MCP server information dictionaries
        """
        try:
            mcps = db.query(MCP).all()
            
            result = []
            for mcp in mcps:
                result.append({
                    "id": str(mcp.id),
                    "name": mcp.name,
                    "type": mcp.type,
                    "command": mcp.command,
                    "url": mcp.url,
                    "created_at": mcp.created_at.isoformat() if mcp.created_at else None,
                    "cached": str(mcp.id) in [str(k) for k in self._mcp_cache.keys()]
                })
            
            logger.info(f"Listed {len(result)} MCP servers from database")
            return result
        
        except Exception as e:
            logger.error(f"Failed to list MCP clients: {str(e)}")
            raise
    
    def create_mcp_client_from_dict(self, config_dict: Dict) -> object:
        """
        Create an MCP client from a configuration dictionary.
        
        Useful for creating clients from API input without database dependency.
        
        Args:
            config_dict: Dictionary with MCP configuration
                Example:
                {
                    "server_type": "http",
                    "endpoint": "https://api.githubcopilot.com/mcp",
                    "auth_headers": {"Authorization": "Bearer token"}
                }
            
        Returns:
            MCPClient instance
            
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            config = MCPClientConfig(**config_dict)
            client_func = MCPClientFactory.create(config)
            
            logger.info(
                f"Created dynamic MCP client from dict config: "
                f"type={config.server_type}"
            )
            return client_func
        
        except Exception as e:
            logger.error(f"Failed to create MCP client from dict: {str(e)}")
            raise
    
    def validate_mcp_config_in_db(self, mcp_id: UUID, db: Session) -> tuple[bool, Optional[str]]:
        """
        Validate MCP configuration in database before using.
        
        Args:
            mcp_id: UUID of the MCP server
            db: SQLAlchemy session
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
            if not mcp:
                return False, f"MCP not found: {mcp_id}"
            
            config = self._mcp_to_config(mcp)
            return MCPClientFactory.validate_config(config)
        
        except Exception as e:
            return False, str(e)
    
    def clear_client_cache(self, mcp_id: Optional[UUID] = None) -> Dict:
        """
        Clear cached MCP clients.
        
        Args:
            mcp_id: Optional specific MCP ID to clear. If None, clears all.
            
        Returns:
            Dictionary with cache clearing results
        """
        if mcp_id:
            if mcp_id in self._mcp_cache:
                del self._mcp_cache[mcp_id]
                logger.info(f"Cleared cache for MCP ID: {mcp_id}")
                return {"status": "success", "cleared": str(mcp_id)}
            else:
                logger.warning(f"MCP ID not in cache: {mcp_id}")
                return {"status": "not_found", "mcp_id": str(mcp_id)}
        else:
            count = len(self._mcp_cache)
            self._mcp_cache.clear()
            logger.info(f"Cleared entire MCP client cache ({count} entries)")
            return {"status": "success", "cleared_count": count}
    
    def get_client_manager(self) -> MCPClientManager:
        """Get the underlying MCPClientManager instance."""
        return self._client_manager


# Global singleton instance
_dynamic_mcp_service = DynamicMCPClientService()


def get_dynamic_mcp_service() -> DynamicMCPClientService:
    """Get the global DynamicMCPClientService instance."""
    return _dynamic_mcp_service


# ============================================================================
# Convenience functions for backward compatibility and easy access
# ============================================================================

def get_mcp_client_by_id(mcp_id: UUID, db: Session) -> Optional[object]:
    """
    Convenience function to get MCP client by ID.
    
    Args:
        mcp_id: UUID of the MCP server
        db: SQLAlchemy session
        
    Returns:
        MCPClient instance or None
    """
    service = get_dynamic_mcp_service()
    return service.get_mcp_client_by_id(mcp_id, db)


def get_mcp_client_by_name(mcp_name: str, db: Session) -> Optional[object]:
    """
    Convenience function to get MCP client by name.
    
    Args:
        mcp_name: Name of the MCP server
        db: SQLAlchemy session
        
    Returns:
        MCPClient instance or None
    """
    service = get_dynamic_mcp_service()
    return service.get_mcp_client_by_name(mcp_name, db)


def list_all_mcp_clients(db: Session) -> List[Dict]:
    """
    Convenience function to list all MCP clients.
    
    Args:
        db: SQLAlchemy session
        
    Returns:
        List of MCP server information dictionaries
    """
    service = get_dynamic_mcp_service()
    return service.list_all_mcp_clients(db)


# Export all functions and classes
__all__ = [
    "DynamicMCPClientService",
    "get_dynamic_mcp_service",
    "get_mcp_client_by_id",
    "get_mcp_client_by_name",
    "list_all_mcp_clients",
]
