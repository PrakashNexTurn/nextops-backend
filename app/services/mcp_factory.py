"""
Dynamic MCP Client Factory Service

Provides a flexible factory pattern for creating MCP clients based on configuration.
Supports:
- HTTP servers (streamable_http) with optional bearer token auth
- Stdio servers (Python scripts, local commands)
- NPM package servers (kubernetes, terraform, postgres, gcp, gcloud)

This replaces hardcoded MCP client functions with configurable, dynamic initialization.
"""

import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Optional

from mcp import StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client

from app.schemas.mcp_config import MCPClientConfig

logger = logging.getLogger(__name__)


class MCPClientFactory:
    """
    Factory for dynamically creating MCP clients from configuration.
    
    Example usage:
        config = MCPClientConfig(
            server_type="http",
            endpoint="https://mcp.exa.ai/mcp",
            auth_headers={"Authorization": "Bearer token"}
        )
        mcp_client = MCPClientFactory.create(config)
    """
    
    @staticmethod
    def validate_config(config: MCPClientConfig) -> tuple[bool, Optional[str]]:
        """
        Validate MCP configuration before creating client.
        
        Args:
            config: MCPClientConfig instance
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if config.server_type == "http":
                if not config.endpoint:
                    return False, "HTTP server requires 'endpoint' parameter"
            
            elif config.server_type == "stdio":
                if not config.command:
                    return False, "Stdio server requires 'command' parameter"
                
                # Validate command exists
                if config.command not in ["python", "node", "npx", "/usr/bin/terraform-mcp-server"]:
                    if not shutil.which(config.command) and not os.path.exists(config.command):
                        logger.warning(f"Command '{config.command}' not found in PATH or as absolute path")
            
            elif config.server_type == "npm":
                if not config.package:
                    return False, "NPM server requires 'package' parameter"
            
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _prepare_http_server(config: MCPClientConfig) -> Callable:
        """Create HTTP server client function."""
        headers = config.auth_headers or {}
        timeout = config.timeout
        endpoint = config.endpoint
        
        def get_http_client():
            return streamablehttp_client(
                url=endpoint,
                headers=headers if headers else None,
                timeout=timeout
            )
        
        return get_http_client
    
    @staticmethod
    def _prepare_stdio_server(config: MCPClientConfig) -> Callable:
        """Create Stdio server client function."""
        command = config.command
        args = config.args or []
        timeout = config.timeout
        
        # Prepare environment variables
        env = {**os.environ}
        if config.env_vars:
            env.update(config.env_vars)
        
        def get_stdio_client():
            # Use current Python interpreter if command is "python"
            cmd = sys.executable if command == "python" else command
            
            return stdio_client(
                StdioServerParameters(
                    command=cmd,
                    args=args,
                    timeout=timeout,
                    env=env
                )
            )
        
        return get_stdio_client
    
    @staticmethod
    def _prepare_npm_server(config: MCPClientConfig) -> Callable:
        """Create NPM package server client function."""
        package = config.package
        args = ["-y", package] + (config.args or [])
        timeout = config.timeout
        
        # Prepare environment variables
        env = {**os.environ}
        if config.env_vars:
            env.update(config.env_vars)
        
        def get_npm_client():
            return stdio_client(
                StdioServerParameters(
                    command="npx",
                    args=args,
                    timeout=timeout,
                    env=env
                )
            )
        
        return get_npm_client
    
    @staticmethod
    def _prepare_gcp_auth(credentials_path: Path, project_id: str) -> dict:
        """
        Prepare non-interactive gcloud authentication from service-account key.
        
        Args:
            credentials_path: Path to GCP service account JSON key
            project_id: GCP project ID
            
        Returns:
            Environment dictionary with gcloud auth configured
            
        Raises:
            ValueError: If gcloud auth setup fails
        """
        gcloud_config_dir = Path("/tmp/gcloud-config")
        gcloud_config_dir.mkdir(parents=True, exist_ok=True)
        
        auth_env = {
            **os.environ,
            "GOOGLE_APPLICATION_CREDENTIALS": str(credentials_path),
            "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE": str(credentials_path),
            "CLOUDSDK_CORE_PROJECT": project_id,
            "CLOUDSDK_CONFIG": str(gcloud_config_dir),
            "CLOUDSDK_CORE_DISABLE_PROMPTS": "1",
        }
        
        try:
            subprocess.run(
                [
                    "gcloud",
                    "auth",
                    "activate-service-account",
                    f"--key-file={credentials_path}",
                    "--quiet",
                ],
                env=auth_env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                ["gcloud", "config", "set", "project", project_id, "--quiet"],
                env=auth_env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(
                "Failed to initialize gcloud auth with service-account key: "
                f"{(e.stderr or e.stdout or str(e)).strip()}"
            ) from e
        
        return auth_env
    
    @staticmethod
    def _prepare_gcp_server(config: MCPClientConfig) -> Callable:
        """
        Create GCP MCP server client function.
        Requires gcloud CLI and GCP credentials.
        """
        if shutil.which("gcloud") is None:
            raise ValueError(
                "gcloud executable not found. Install Google Cloud CLI."
            )
        
        # Find GCP credentials
        credentials_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        project_env = os.getenv("CLOUDSDK_CORE_PROJECT", "").strip()
        
        candidate_paths = [
            Path(credentials_env) if credentials_env else None,
            Path.cwd() / "gcp-key.json",
            Path("/app/gcp-key.json"),
        ]
        
        credentials_path = next(
            (path for path in candidate_paths if path and path.exists()),
            None,
        )
        
        if credentials_path is None:
            raise ValueError(
                "GCP key file not found. Set GOOGLE_APPLICATION_CREDENTIALS or place gcp-key.json."
            )
        
        # Extract project ID
        project_id = project_env
        if not project_id:
            try:
                key_data = json.loads(credentials_path.read_text(encoding="utf-8"))
                project_id = str(key_data.get("project_id", "")).strip()
            except Exception as e:
                raise ValueError(
                    f"Failed to read project_id from {credentials_path}: {e}"
                ) from e
        
        if not project_id:
            raise ValueError(
                "Unable to determine GCP project. Set CLOUDSDK_CORE_PROJECT or include project_id in key file."
            )
        
        # Prepare gcloud auth
        gcp_env = MCPClientFactory._prepare_gcp_auth(credentials_path, project_id)
        
        timeout = config.timeout
        args = config.args or []
        
        def get_gcp_client():
            return stdio_client(
                StdioServerParameters(
                    command="npx",
                    args=["-y", "@google-cloud/gcloud-mcp"] + args,
                    timeout=timeout,
                    env=gcp_env
                )
            )
        
        return get_gcp_client
    
    @staticmethod
    def create(config: MCPClientConfig):
        """
        Create an MCP client based on configuration.
        
        Args:
            config: MCPClientConfig instance with server configuration
            
        Returns:
            MCPClient instance ready for use
            
        Raises:
            ValueError: If configuration is invalid or client creation fails
        """
        # Validate configuration
        is_valid, error_msg = MCPClientFactory.validate_config(config)
        if not is_valid:
            raise ValueError(f"Invalid MCP configuration: {error_msg}")
        
        logger.info(f"Creating MCP client with config: server_type={config.server_type}")
        
        try:
            if config.server_type == "http":
                client_func = MCPClientFactory._prepare_http_server(config)
                logger.info(f"HTTP MCP client created for endpoint: {config.endpoint}")
            
            elif config.server_type == "stdio":
                client_func = MCPClientFactory._prepare_stdio_server(config)
                logger.info(f"Stdio MCP client created for command: {config.command}")
            
            elif config.server_type == "npm":
                if config.package == "@google-cloud/gcloud-mcp":
                    client_func = MCPClientFactory._prepare_gcp_server(config)
                    logger.info("GCP MCP client created")
                else:
                    client_func = MCPClientFactory._prepare_npm_server(config)
                    logger.info(f"NPM MCP client created for package: {config.package}")
            
            else:
                raise ValueError(f"Unknown server type: {config.server_type}")
            
            # Return the client function (will be wrapped by MCPClient if needed)
            return client_func
        
        except Exception as e:
            logger.error(f"Failed to create MCP client: {str(e)}")
            raise


class MCPClientManager:
    """
    Manages multiple MCP clients with caching and lifecycle management.
    """
    
    def __init__(self):
        """Initialize the client manager."""
        self._clients: Dict[str, Dict] = {}
        logger.info("MCP Client Manager initialized")
    
    def register_client(
        self,
        client_id: str,
        config: MCPClientConfig
    ) -> tuple[bool, Optional[str]]:
        """
        Register and create a new MCP client.
        
        Args:
            client_id: Unique identifier for the client
            config: MCPClientConfig instance
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            client_func = MCPClientFactory.create(config)
            self._clients[client_id] = {
                "config": config,
                "client_func": client_func,
                "created_at": str(Path(__file__).stat().st_mtime)
            }
            logger.info(f"MCP client registered: {client_id}")
            return True, None
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to register client {client_id}: {error_msg}")
            return False, error_msg
    
    def get_client(self, client_id: str):
        """
        Get a registered MCP client function.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Client function or None if not found
        """
        if client_id in self._clients:
            return self._clients[client_id]["client_func"]
        
        logger.warning(f"Client not found: {client_id}")
        return None
    
    def list_clients(self) -> Dict[str, Dict]:
        """Get all registered clients."""
        return {
            cid: {
                "type": c["config"].server_type,
                "endpoint_or_command": c["config"].endpoint or c["config"].command or c["config"].package
            }
            for cid, c in self._clients.items()
        }
    
    def unregister_client(self, client_id: str) -> bool:
        """Unregister and remove a client."""
        if client_id in self._clients:
            del self._clients[client_id]
            logger.info(f"MCP client unregistered: {client_id}")
            return True
        
        return False


# Global client manager instance
_mcp_client_manager = MCPClientManager()


def get_mcp_client_manager() -> MCPClientManager:
    """Get the global MCP client manager instance."""
    return _mcp_client_manager
