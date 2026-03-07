#!/bin/bash
#
# MCP Server Tool Listing Script
# 
# This script provides a convenient way to list tools from MCP servers.
# It can be used to query registered MCP servers and discover their available tools.
#
# Usage:
#   ./list_mcp_tools.sh --mcp-id <uuid>
#   ./list_mcp_tools.sh --mcp-name "<name>"
#   ./list_mcp_tools.sh --list-servers
#   ./list_mcp_tools.sh --help
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if we're in the project directory
if [ ! -f "$PROJECT_ROOT/list_mcp_tools.py" ]; then
    echo -e "${RED}❌ Error: list_mcp_tools.py not found in $PROJECT_ROOT${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo -e "${BLUE}📦 Virtual environment activated${NC}"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 not found${NC}"
    exit 1
fi

# Function to display help
show_help() {
    cat << EOF
${BLUE}📋 MCP Server Tool Listing Script${NC}

Usage:
    $0 [OPTIONS]

Options:
    --mcp-id <uuid>           UUID of MCP server to query
    --mcp-name <name>         Name of MCP server to query
    --list-servers            List all registered MCP servers
    --refresh                 Force refresh of tool list (bypass cache)
    --format <format>         Output format: table (default), json, or csv
    --help                    Show this help message

Examples:
    # List tools from MCP server by ID
    $0 --mcp-id 550e8400-e29b-41d4-a716-446655440000

    # List tools from MCP server by name
    $0 --mcp-name "My MCP Server"

    # Force refresh tools
    $0 --mcp-id 550e8400-e29b-41d4-a716-446655440000 --refresh

    # List all MCP servers
    $0 --list-servers

    # Output as JSON
    $0 --mcp-name "My MCP Server" --format json

    # Output as CSV
    $0 --list-servers --format csv

${GREEN}For more information, see the README.md file.${NC}

EOF
}

# Parse arguments
MCP_ID=""
MCP_NAME=""
LIST_SERVERS=false
REFRESH=false
FORMAT="table"

while [[ $# -gt 0 ]]; do
    case $1 in
        --mcp-id)
            MCP_ID="$2"
            shift 2
            ;;
        --mcp-name)
            MCP_NAME="$2"
            shift 2
            ;;
        --list-servers)
            LIST_SERVERS=true
            shift
            ;;
        --refresh)
            REFRESH=true
            shift
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Build Python command
PYTHON_ARGS=""

if [ "$LIST_SERVERS" = true ]; then
    PYTHON_ARGS="--list-servers"
elif [ -n "$MCP_ID" ]; then
    PYTHON_ARGS="--mcp-id $MCP_ID"
elif [ -n "$MCP_NAME" ]; then
    PYTHON_ARGS="--mcp-name '$MCP_NAME'"
else
    echo -e "${RED}❌ Error: Provide either --mcp-id, --mcp-name, or --list-servers${NC}"
    show_help
    exit 1
fi

# Add optional arguments
PYTHON_ARGS="$PYTHON_ARGS --format $FORMAT"

if [ "$REFRESH" = true ]; then
    PYTHON_ARGS="$PYTHON_ARGS --refresh"
fi

# Display command info
echo -e "${BLUE}🚀 Running MCP tool discovery...${NC}"
echo -e "${BLUE}Command: python3 list_mcp_tools.py $PYTHON_ARGS${NC}\n"

# Run Python script
cd "$PROJECT_ROOT"
eval "python3 list_mcp_tools.py $PYTHON_ARGS"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tool discovery completed successfully${NC}"
else
    echo -e "${RED}❌ Tool discovery failed with exit code $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
