#!/usr/bin/env python3
"""
Standalone utility to list MCP server tools.

Usage:
    # List tools from a registered MCP server
    python list_mcp_tools.py --mcp-id <mcp_uuid>
    
    # List tools with refresh (bypass cache)
    python list_mcp_tools.py --mcp-id <mcp_uuid> --refresh
    
    # Use custom API endpoint
    python list_mcp_tools.py --mcp-id <mcp_uuid> --api-url http://localhost:8000
    
    # List all registered MCP servers
    python list_mcp_tools.py --list-servers
    
    # Specify MCP by name instead of ID
    python list_mcp_tools.py --mcp-name <mcp_name>

Requirements:
    - fastapi, sqlalchemy, psycopg2-binary, pydantic, pydantic-settings
    - Access to nextops-backend database
"""

import sys
import os
import asyncio
import argparse
import json
from typing import Optional
from uuid import UUID
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import database and models
from app.db.database import SessionLocal
from app.models.mcp import MCP
from app.services.mcp_discovery import MCPDiscoveryService


async def list_tools_from_mcp(
    mcp_id: Optional[UUID] = None,
    mcp_name: Optional[str] = None,
    refresh: bool = False,
    output_format: str = "table"
) -> bool:
    """
    List tools from a specific MCP server.
    
    Args:
        mcp_id: UUID of MCP server (or name if mcp_name is provided)
        mcp_name: Name of MCP server (alternative to mcp_id)
        refresh: Force refresh of tool list
        output_format: Output format ('table', 'json', 'csv')
    
    Returns:
        True if successful, False otherwise
    """
    db = SessionLocal()
    discovery_service = MCPDiscoveryService()
    
    try:
        # Find MCP server
        mcp = None
        if mcp_id:
            mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
        elif mcp_name:
            mcp = db.query(MCP).filter(MCP.name == mcp_name).first()
        
        if not mcp:
            identifier = mcp_id or mcp_name
            print(f"❌ Error: MCP server '{identifier}' not found")
            return False
        
        print(f"\n🔍 Discovering tools from MCP: {mcp.name} ({mcp.id})")
        print(f"   Type: {mcp.type}")
        if mcp.type == "stdio":
            print(f"   Command: {mcp.command}")
        elif mcp.type == "sse":
            print(f"   URL: {mcp.url}")
        print()
        
        # Prepare MCP configuration
        mcp_config = {
            "type": mcp.type,
            "command": mcp.command,
            "url": mcp.url,
            "args": mcp.args or {},
            "headers": mcp.headers or {},
            "env_vars": mcp.env_vars or {}
        }
        
        # Validate configuration
        if not discovery_service.validate_mcp_config(mcp.type, mcp_config):
            print(f"❌ Error: Invalid MCP configuration")
            print(f"   For 'stdio' type, 'command' is required")
            print(f"   For 'sse' type, 'url' is required")
            return False
        
        # Discover tools
        tools = await discovery_service.discover_tools(
            mcp.id,
            mcp_config,
            refresh=refresh
        )
        
        if not tools:
            print("⚠️  No tools found")
            return True
        
        # Format and display output
        if output_format == "json":
            _print_json_format(mcp, tools)
        elif output_format == "csv":
            _print_csv_format(mcp, tools)
        else:  # table
            _print_table_format(mcp, tools)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def list_all_mcp_servers(output_format: str = "table") -> bool:
    """
    List all registered MCP servers.
    
    Args:
        output_format: Output format ('table', 'json', 'csv')
    
    Returns:
        True if successful, False otherwise
    """
    db = SessionLocal()
    
    try:
        mcps = db.query(MCP).all()
        
        if not mcps:
            print("No MCP servers registered")
            return True
        
        print(f"\n📋 Registered MCP Servers ({len(mcps)} total)\n")
        
        if output_format == "json":
            data = [
                {
                    "id": str(mcp.id),
                    "name": mcp.name,
                    "type": mcp.type,
                    "command": mcp.command,
                    "url": mcp.url,
                    "created_at": mcp.created_at.isoformat()
                }
                for mcp in mcps
            ]
            print(json.dumps(data, indent=2))
        elif output_format == "csv":
            print("ID,Name,Type,Command,URL,CreatedAt")
            for mcp in mcps:
                cmd = mcp.command or ""
                url = mcp.url or ""
                print(f'"{mcp.id}","{mcp.name}","{mcp.type}","{cmd}","{url}","{mcp.created_at}"')
        else:  # table
            print(f"{'ID':<36} | {'Name':<20} | {'Type':<8} | {'Config':<30}")
            print("-" * 105)
            for mcp in mcps:
                config = mcp.command or mcp.url or "N/A"
                config = config[:30] if len(config) > 30 else config
                print(f"{str(mcp.id):<36} | {mcp.name:<20} | {mcp.type:<8} | {config:<30}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        db.close()


def _print_table_format(mcp, tools):
    """Print tools in table format."""
    print(f"{'Tool Name':<30} | {'Description':<50}")
    print("-" * 82)
    for tool in tools:
        name = tool.get("name", "N/A")
        desc = tool.get("description", "N/A")
        # Truncate description if too long
        if isinstance(desc, str) and len(desc) > 50:
            desc = desc[:47] + "..."
        print(f"{name:<30} | {str(desc):<50}")
    
    print(f"\n✅ Total tools discovered: {len(tools)}\n")


def _print_json_format(mcp, tools):
    """Print tools in JSON format."""
    data = {
        "mcp": {
            "id": str(mcp.id),
            "name": mcp.name,
            "type": mcp.type
        },
        "tools_count": len(tools),
        "tools": tools
    }
    print(json.dumps(data, indent=2))


def _print_csv_format(mcp, tools):
    """Print tools in CSV format."""
    print("Tool Name,Description,Input Schema")
    for tool in tools:
        name = tool.get("name", "")
        desc = tool.get("description", "").replace('"', '""')
        schema = json.dumps(tool.get("inputSchema", {})).replace('"', '""')
        print(f'"{name}","{desc}","{schema}"')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="List tools from MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List tools from MCP by ID
  python list_mcp_tools.py --mcp-id 550e8400-e29b-41d4-a716-446655440000
  
  # List tools from MCP by name
  python list_mcp_tools.py --mcp-name "My MCP Server"
  
  # Force refresh (bypass cache)
  python list_mcp_tools.py --mcp-id 550e8400-e29b-41d4-a716-446655440000 --refresh
  
  # List all registered MCP servers
  python list_mcp_tools.py --list-servers
  
  # Output as JSON
  python list_mcp_tools.py --mcp-id 550e8400-e29b-41d4-a716-446655440000 --format json
        """
    )
    
    parser.add_argument(
        "--mcp-id",
        type=str,
        help="UUID of MCP server"
    )
    parser.add_argument(
        "--mcp-name",
        type=str,
        help="Name of MCP server (alternative to --mcp-id)"
    )
    parser.add_argument(
        "--list-servers",
        action="store_true",
        help="List all registered MCP servers"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh of tool list (bypass cache)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.list_servers:
        success = list_all_mcp_servers(output_format=args.format)
    elif args.mcp_id or args.mcp_name:
        mcp_id = UUID(args.mcp_id) if args.mcp_id else None
        success = asyncio.run(
            list_tools_from_mcp(
                mcp_id=mcp_id,
                mcp_name=args.mcp_name,
                refresh=args.refresh,
                output_format=args.format
            )
        )
    else:
        parser.print_help()
        print("\n❌ Error: Provide either --mcp-id, --mcp-name, or --list-servers")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
