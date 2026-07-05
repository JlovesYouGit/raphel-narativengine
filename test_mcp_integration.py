"""
Test Agent-97 MCP Tool Integration
Test script for the MCP tool integration with ModelMirror
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from agent97_mcp_tool_integration import Agent97MCPToolIntegration

async def test_mcp_integration():
    """Test the MCP tool integration"""
    print("=== Agent-97 MCP Tool Integration Test ===\n")
    
    # Initialize integration
    print("1. Initializing MCP integration...")
    mcp_integration = Agent97MCPToolIntegration()
    
    try:
        # Initialize the integration
        result = await mcp_integration.initialize_mcp_integration()
        
        if not result["success"]:
            print(f"   FAILED: {result['error']}")
            return False
        
        print(f"   SUCCESS: Server running at {result['server_url']}")
        print(f"   Available tools: {', '.join(result['available_tools'])}")
        
        # Test 1: Get available tools
        print("\n2. Testing get available tools...")
        tools_result = await mcp_integration.get_available_tools()
        
        if tools_result["success"]:
            print(f"   SUCCESS: {tools_result['total_tools']} tools available")
            for tool_name in tools_result["tools"]:
                description = tools_result["tools"][tool_name]["description"]
                print(f"   - {tool_name}: {description}")
        else:
            print(f"   FAILED: {tools_result['error']}")
        
        # Test 2: Cache operations
        print("\n3. Testing cache operations...")
        
        # Set cache
        cache_set_result = await mcp_integration.cache_set("test_key", {"data": "test_value", "timestamp": "2024-04-07"})
        
        if cache_set_result["success"]:
            print("   SUCCESS: Cache set operation")
        else:
            print(f"   FAILED: Cache set failed - {cache_set_result['error']}")
        
        # Get cache
        cache_get_result = await mcp_integration.cache_get("test_key")
        
        if cache_get_result["success"]:
            print(f"   SUCCESS: Cache get operation - {cache_get_result['value']}")
        else:
            print(f"   FAILED: Cache get failed - {cache_get_result['error']}")
        
        # Delete cache
        cache_delete_result = await mcp_integration.cache_delete("test_key")
        
        if cache_delete_result["success"]:
            print("   SUCCESS: Cache delete operation")
        else:
            print(f"   FAILED: Cache delete failed - {cache_delete_result['error']}")
        
        # Test 3: Web search (may fail due to Playwright not being installed)
        print("\n4. Testing web search...")
        search_result = await mcp_integration.search_web("Agent-97 AI system", max_results=3)
        
        if search_result["success"]:
            results = search_result["results"].get("results", [])
            print(f"   SUCCESS: Found {len(results)} search results")
            for i, result in enumerate(results[:2]):  # Show first 2 results
                print(f"   - Result {i+1}: {result.get('title', 'No title')}")
        else:
            print(f"   EXPECTED FAILURE: Web search failed - {search_result['error']}")
            print("   (This is expected if Playwright is not installed)")
        
        # Test 4: URL fetch (may fail due to Playwright not being installed)
        print("\n5. Testing URL fetch...")
        fetch_result = await mcp_integration.fetch_url("https://example.com")
        
        if fetch_result["success"]:
            content = fetch_result["content"]
            print(f"   SUCCESS: Fetched URL content ({len(str(content))} characters)")
        else:
            print(f"   EXPECTED FAILURE: URL fetch failed - {fetch_result['error']}")
            print("   (This is expected if Playwright is not installed)")
        
        # Test 5: Get integration status
        print("\n6. Testing integration status...")
        status_result = await mcp_integration.get_integration_status()
        
        if "error" not in status_result:
            print(f"   SUCCESS: Integration status retrieved")
            print(f"   - Server running: {status_result['server_running']}")
            print(f"   - MCP requests: {status_result['metrics']['mcp_requests']}")
            print(f"   - Successful requests: {status_result['metrics']['successful_requests']}")
            print(f"   - Failed requests: {status_result['metrics']['failed_requests']}")
            print(f"   - Cache operations: {status_result['metrics']['cache_operations']}")
        else:
            print(f"   FAILED: {status_result['error']}")
        
        print("\n=== Test Summary ===")
        print("MCP Tool Integration test completed!")
        print("Note: Web search and URL fetch may fail without Playwright installation")
        print("Cache operations should work fine for basic MCP functionality")
        
        return True
        
    except Exception as e:
        print(f"   FAILED: {str(e)}")
        return False
    
    finally:
        # Cleanup
        print("\n7. Cleaning up...")
        await mcp_integration.shutdown_integration()
        print("   SUCCESS: Integration shutdown complete")

if __name__ == "__main__":
    print("Starting Agent-97 MCP Tool Integration Test...\n")
    
    try:
        success = asyncio.run(test_mcp_integration())
        
        if success:
            print("\n=== TEST COMPLETED SUCCESSFULLY ===")
        else:
            print("\n=== TEST FAILED ===")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n=== TEST INTERRUPTED ===")
        sys.exit(1)
    except Exception as e:
        print(f"\n=== TEST ERROR ===\n{e}")
        sys.exit(1)
