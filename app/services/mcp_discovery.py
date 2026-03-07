import asyncio
import json
import subprocess
import aiohttp
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class MCPDiscoveryService:
    """
    Service for MCP (Model Context Protocol) discovery.
    
    This service handles:
    - Starting MCP servers (stdio or SSE)
    - Discovering available tools from MCP servers
    - Querying tools via MCP protocol
    - Caching tool definitions
    - Validating MCP configurations
    """

    def __init__(self):
        self.tools_cache: Dict[UUID, List[Dict[str, Any]]] = {}
        self.server_processes: Dict[UUID, subprocess.Popen] = {}

    async def discover_tools(
        self, 
        mcp_id: UUID, 
        mcp_config: Dict[str, Any],
        refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Discover tools from an MCP server.
        
        Args:
            mcp_id: UUID of the MCP server
            mcp_config: Configuration dict with 'type', 'url', 'command', etc.
            refresh: Force refresh cache
        
        Returns:
            List of discovered tools with schemas
        """
        # Check cache first
        if not refresh and mcp_id in self.tools_cache:
            logger.info(f"Returning cached tools for MCP {mcp_id}")
            return self.tools_cache[mcp_id]

        discovered_tools = []
        
        try:
            mcp_type = mcp_config.get("type", "stdio")
            
            if mcp_type == "sse":
                # SSE-based discovery
                discovered_tools = await self._discover_sse_tools(mcp_id, mcp_config)
            elif mcp_type == "stdio":
                # Stdio-based discovery
                discovered_tools = await self._discover_stdio_tools(mcp_id, mcp_config)
            else:
                logger.error(f"Unknown MCP type: {mcp_type}")
                return []

            # Cache results
            self.tools_cache[mcp_id] = discovered_tools
            logger.info(f"Discovered {len(discovered_tools)} tools for MCP {mcp_id}")
            
        except Exception as e:
            logger.error(f"Error discovering tools for MCP {mcp_id}: {str(e)}")
            return []
            
        return discovered_tools

    async def _parse_sse_stream(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse Server-Sent Events (SSE) format and extract JSON data.
        
        SSE Format Example:
            data: {"tool": {"name": "search", "description": "Search"}}
            data: {"tool": {"name": "code", "description": "Code"}}
        
        Args:
            content: Raw SSE stream content
        
        Returns:
            List of parsed JSON objects
        """
        tools = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith(':'):
                continue
            
            # Parse SSE data lines
            if line.startswith('data: '):
                json_str = line[6:]  # Remove 'data: ' prefix
                try:
                    data = json.loads(json_str)
                    # SSE streams may wrap the tool in a 'tool' field
                    if 'tool' in data:
                        tools.append(data['tool'])
                    else:
                        tools.append(data)
                    logger.debug(f"Parsed SSE data: {data}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse SSE JSON line: {json_str[:100]} - {str(e)}")
                    continue
        
        return tools

    async def _discover_sse_tools(
        self, 
        mcp_id: UUID, 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Discover tools via SSE (Server-Sent Events) MCP server.
        
        Handles both JSON-RPC responses and SSE streaming format.
        
        Args:
            mcp_id: UUID of the MCP server
            config: Configuration with 'url' field
        
        Returns:
            List of discovered tools
        """
        url = config.get("url")
        if not url:
            logger.error("SSE MCP configuration missing 'url' field")
            return []
        
        tools = []
        try:
            headers = config.get("headers", {})
            
            # Connect to MCP server and request tool list
            async with aiohttp.ClientSession() as session:
                # Initialize connection
                init_url = f"{url}/initialize"
                init_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "nextops-mcp-discovery",
                            "version": "1.0.0"
                        }
                    }
                }
                
                async with session.post(
                    init_url,
                    json=init_payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to initialize MCP server: {response.status}")
                        return []
                    logger.debug(f"MCP server initialized: {response.status}")
                
                # List available tools
                tools_url = f"{url}/tools/list"
                tools_payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                async with session.post(
                    tools_url,
                    json=tools_payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    content_type = response.content_type or ""
                    logger.info(f"MCP tools response: {response.status}, content-type: {content_type}")
                    
                    if response.status == 200:
                        # Handle SSE streaming format
                        if "text/event-stream" in content_type:
                            logger.info("Parsing SSE stream format")
                            content = await response.text()
                            tools = await self._parse_sse_stream(content)
                            logger.info(f"Retrieved {len(tools)} tools from SSE stream")
                        else:
                            # Handle regular JSON response
                            try:
                                data = await response.json()
                                tools = data.get("result", {}).get("tools", [])
                                logger.info(f"Retrieved {len(tools)} tools from JSON response")
                            except aiohttp.ContentTypeError as e:
                                # Fallback: try parsing as text/SSE if JSON parsing fails
                                logger.warning(f"JSON parse failed, attempting SSE parse: {str(e)}")
                                content = await response.text()
                                tools = await self._parse_sse_stream(content)
                                logger.info(f"Retrieved {len(tools)} tools from SSE stream (fallback)")
                    else:
                        logger.error(f"Failed to list tools: {response.status}")
                        content = await response.text()
                        logger.error(f"Response: {content[:200]}")
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout connecting to SSE MCP server: {url}")
        except Exception as e:
            logger.error(f"Error discovering SSE tools: {type(e).__name__}: {str(e)}")
        
        return tools

    async def _discover_stdio_tools(
        self, 
        mcp_id: UUID, 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Discover tools via Stdio MCP server.
        
        Args:
            mcp_id: UUID of the MCP server
            config: Configuration with 'command' field
        
        Returns:
            List of discovered tools
        """
        command = config.get("command")
        if not command:
            logger.error("Stdio MCP configuration missing 'command' field")
            return []
        
        tools = []
        process = None
        
        try:
            # Parse command and args
            cmd_parts = command.split()
            args = config.get("args", {})
            env_vars = config.get("env_vars", {})
            
            # Build command with arguments
            if args:
                cmd_parts.extend([f"--{k}={v}" for k, v in args.items()])
            
            # Start MCP server process
            logger.info(f"Starting stdio MCP server: {command}")
            process = subprocess.Popen(
                cmd_parts,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**env_vars} if env_vars else None
            )
            
            # Store process reference
            self.server_processes[mcp_id] = process
            
            # Send MCP protocol messages to get tools list
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "nextops-mcp-discovery",
                        "version": "1.0.0"
                    }
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialization response
            init_response = process.stdout.readline()
            if init_response:
                logger.debug(f"MCP init response: {init_response}")
            
            # Request tool list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()
            
            # Read tools response
            tools_response = process.stdout.readline()
            if tools_response:
                response_data = json.loads(tools_response)
                tools = response_data.get("result", {}).get("tools", [])
                logger.info(f"Retrieved {len(tools)} tools from stdio MCP server")
            
            # Graceful shutdown
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.server_processes[mcp_id]
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MCP response: {str(e)}")
        except Exception as e:
            logger.error(f"Error discovering stdio tools: {str(e)}")
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
        
        return tools

    def validate_mcp_config(self, mcp_type: str, config: Dict[str, Any]) -> bool:
        """
        Validate MCP configuration.
        
        Args:
            mcp_type: Type of MCP (stdio or sse)
            config: Configuration dictionary
        
        Returns:
            True if valid, False otherwise
        """
        if mcp_type == "sse":
            return "url" in config and config["url"]
        elif mcp_type == "stdio":
            return "command" in config and config["command"]
        return False

    def clear_cache(self, mcp_id: Optional[UUID] = None):
        """
        Clear discovery cache.
        
        Args:
            mcp_id: If provided, clears only this MCP's cache. Otherwise clears all.
        """
        if mcp_id:
            self.tools_cache.pop(mcp_id, None)
            logger.info(f"Cleared cache for MCP {mcp_id}")
        else:
            self.tools_cache.clear()
            logger.info("Cleared all MCP tool cache")

    def stop_server(self, mcp_id: UUID):
        """
        Stop a running stdio MCP server process.
        
        Args:
            mcp_id: UUID of the MCP server
        """
        if mcp_id in self.server_processes:
            process = self.server_processes[mcp_id]
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
            del self.server_processes[mcp_id]
            logger.info(f"Stopped MCP server process for {mcp_id}")

    def stop_all_servers(self):
        """Stop all running stdio MCP server processes."""
        for mcp_id in list(self.server_processes.keys()):
            self.stop_server(mcp_id)
        logger.info("Stopped all MCP server processes")
