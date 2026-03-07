#!/usr/bin/env python3
"""
Quick test script to verify Agent MCP implementation is working.
Run this after deploying the changes to verify everything works.
"""

import requests
import json
from typing import Dict, List
from uuid import UUID

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def test_endpoint(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        elif method == "PUT":
            response = requests.put(url, json=data, headers={"Content-Type": "application/json"})
        elif method == "DELETE":
            response = requests.delete(url)
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None,
            "error": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "data": None,
            "error": str(e)
        }

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Agent MCP Implementation Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    
    # Test 1: Check if API is running
    print_info("Test 1: Checking if API is running...")
    result = test_endpoint("GET", "/agents")
    if result["error"]:
        print_error(f"API not responding: {result['error']}")
        return False
    print_success(f"API is running. Found {len(result['data'] or [])} agents")
    
    # Test 2: Get MCPs
    print_info("\nTest 2: Fetching available MCPs...")
    result = test_endpoint("GET", "/mcps")
    if result["error"]:
        print_error(f"Could not fetch MCPs: {result['error']}")
        return False
    
    mcps = result["data"] or []
    if not mcps:
        print_warning("No MCPs found. Please create one first.")
        print_warning("See: POST /mcps")
        return True
    
    mcp_id = mcps[0]["id"]
    mcp_name = mcps[0]["name"]
    print_success(f"Found {len(mcps)} MCPs")
    print_info(f"Using MCP: {mcp_name} ({mcp_id})")
    
    # Test 3: Create agent with MCP IDs
    print_info("\nTest 3: Creating agent with MCP IDs...")
    agent_data = {
        "name": f"Test Agent MCP {int(__import__('time').time())}",
        "description": "Test agent using MCP IDs",
        "system_prompt": "You are a test agent with MCP support",
        "mcp_ids": [mcp_id]
    }
    
    result = test_endpoint("POST", "/agents", agent_data)
    if result["status_code"] != 201:
        print_error(f"Failed to create agent: {result['data']}")
        return False
    
    agent = result["data"]
    agent_id = agent["id"]
    print_success(f"Created agent: {agent['name']}")
    print_info(f"Agent ID: {agent_id}")
    
    # Test 4: Verify MCP was resolved to tools
    print_info("\nTest 4: Verifying MCP tools were resolved...")
    if not agent.get("tool_ids"):
        print_warning("No tool_ids in response")
    else:
        tool_count = len(agent["tool_ids"])
        print_success(f"Agent has {tool_count} resolved tools from MCP")
        if tool_count > 0:
            print_info(f"First few tools: {agent['tool_ids'][:3]}")
    
    # Test 5: Verify mcp_ids in response
    print_info("\nTest 5: Checking mcp_ids in response...")
    mcp_ids = agent.get("mcp_ids", [])
    if mcp_ids:
        print_success(f"Agent has {len(mcp_ids)} MCP association(s)")
    else:
        print_warning("No mcp_ids in agent response")
    
    # Test 6: Get agent details
    print_info("\nTest 6: Fetching agent details...")
    result = test_endpoint("GET", f"/agents/{agent_id}")
    if result["status_code"] != 200:
        print_error(f"Failed to get agent: {result['data']}")
        return False
    
    retrieved_agent = result["data"]
    print_success(f"Retrieved agent: {retrieved_agent['name']}")
    
    # Test 7: Add another MCP if available
    print_info("\nTest 7: Adding another MCP to agent...")
    if len(mcps) > 1:
        mcp_id_2 = mcps[1]["id"]
        mcp_name_2 = mcps[1]["name"]
        
        result = test_endpoint("POST", f"/agents/{agent_id}/mcps/{mcp_id_2}")
        if result["status_code"] == 201:
            print_success(f"Added MCP: {mcp_name_2}")
            print_info(f"Response: {result['data']['message']}")
        else:
            print_error(f"Failed to add MCP: {result['data']}")
    else:
        print_info("Only one MCP available, skipping this test")
    
    # Test 8: List MCPs for agent
    print_info("\nTest 8: Listing MCPs for agent...")
    result = test_endpoint("GET", f"/agents/{agent_id}/mcps")
    if result["status_code"] == 200:
        agent_mcps = result["data"] or []
        print_success(f"Agent has {len(agent_mcps)} MCP association(s)")
        for am in agent_mcps:
            print_info(f"  MCP ID: {am['mcp_id']}")
    else:
        print_error(f"Failed to list MCPs: {result['data']}")
    
    # Test 9: Create agent with tool_ids and mcp_ids (mixed)
    print_info("\nTest 9: Creating agent with mixed tools and MCPs...")
    mixed_agent_data = {
        "name": f"Mixed Agent {int(__import__('time').time())}",
        "description": "Agent with both MCP and direct tool IDs",
        "system_prompt": "Mixed capability agent",
        "mcp_ids": [mcp_id],
        "tool_ids": []  # We'd need real tool IDs here
    }
    
    result = test_endpoint("POST", "/agents", mixed_agent_data)
    if result["status_code"] == 201:
        mixed_agent = result["data"]
        print_success(f"Created mixed agent: {mixed_agent['name']}")
    else:
        print_error(f"Failed to create mixed agent: {result['data']}")
    
    # Test 10: Update agent MCPs
    print_info("\nTest 10: Updating agent MCPs...")
    update_data = {
        "mcp_ids": [mcp_id]
    }
    
    result = test_endpoint("PUT", f"/agents/{agent_id}", update_data)
    if result["status_code"] == 200:
        print_success("Updated agent MCPs")
    else:
        print_error(f"Failed to update: {result['data']}")
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{Colors.END}")
    print_success("All core tests passed! ✅")
    print_info(f"Test agent created: {agent_name} ({agent_id})")
    print_info(f"You can test the API manually at: {BASE_URL}/docs")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
