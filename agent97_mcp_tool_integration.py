"""
Agent-97 MCP Tool Integration with ModelMirror
Integrates Agent-97 with the cloned MCPRESULTListmirror repository as an MCP tool
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp

@dataclass
class MCPToolRequest:
    """MCP tool request structure"""
    jsonrpc: str = "2.0"
    id: str = ""
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MCPToolResponse:
    """MCP tool response structure"""
    jsonrpc: str = "2.0"
    id: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class Agent97MCPToolIntegration:
    """
    Agent-97 MCP Tool Integration with ModelMirror
    Uses the cloned MCPRESULTListmirror repository as an MCP tool
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # MCP server configuration
        self.mcp_config = {
            "server_path": "./MCPRESULTListmirror",
            "server_host": "localhost",
            "server_port": 8000,
            "mcp_endpoint": "/mcp",
            "ws_endpoint": "/ws",
            "health_endpoint": "/health",
            "auto_start_server": True,
            "server_timeout": 30.0
        }
        
        # Server state
        self.server_process = None
        self.server_running = False
        self.server_url = f"http://{self.mcp_config['server_host']}:{self.mcp_config['server_port']}"
        self.mcp_url = f"{self.server_url}{self.mcp_config['mcp_endpoint']}"
        self.ws_url = f"ws://{self.mcp_config['server_host']}:{self.mcp_config['server_port']}{self.mcp_config['ws_endpoint']}"
        
        # MCP client
        self.http_session = None
        self.ws_connection = None
        
        # Tool capabilities
        self.available_tools = {
            "search": {
                "description": "Search the web using local Chromium instance",
                "parameters": {
                    "query": {"type": "string", "required": True, "description": "Search query"},
                    "max_results": {"type": "integer", "default": 10, "description": "Maximum number of results"}
                }
            },
            "fetch": {
                "description": "Fetch URL content with screenshot capability",
                "parameters": {
                    "url": {"type": "string", "required": True, "description": "URL to fetch"},
                    "range_y": {"type": "object", "description": "Y-axis range for screenshot"},
                    "include_screenshot": {"type": "boolean", "default": True, "description": "Include screenshot"}
                }
            },
            "cache_set": {
                "description": "Set cache value",
                "parameters": {
                    "key": {"type": "string", "required": True, "description": "Cache key"},
                    "value": {"type": "any", "required": True, "description": "Cache value"},
                    "ttl": {"type": "integer", "default": 3600, "description": "Time to live in seconds"}
                }
            },
            "cache_get": {
                "description": "Get cache value",
                "parameters": {
                    "key": {"type": "string", "required": True, "description": "Cache key"}
                }
            },
            "cache_delete": {
                "description": "Delete cache value",
                "parameters": {
                    "key": {"type": "string", "required": True, "description": "Cache key"}
                }
            }
        }
        
        # Metrics
        self.metrics = {
            "server_starts": 0,
            "mcp_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_operations": 0,
            "search_queries": 0,
            "url_fetches": 0,
            "total_response_time": 0.0,
            "average_response_time": 0.0
        }
        
        print(f"Agent-97 MCP Tool Integration initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
        print(f"MCP Server Path: {self.mcp_config['server_path']}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_mcp_integration(self) -> Dict[str, Any]:
        """Initialize the MCP tool integration"""
        try:
            print("Initializing Agent-97 MCP Tool Integration...")
            
            # Step 1: Verify cloned repository exists
            if not os.path.exists(self.mcp_config["server_path"]):
                return {"success": False, "error": f"MCPRESULTListmirror repository not found at {self.mcp_config['server_path']}"}
            
            # Step 2: Start MCP server if auto-start is enabled
            if self.mcp_config["auto_start_server"]:
                server_result = await self.start_mcp_server()
                if not server_result["success"]:
                    return server_result
            
            # Step 3: Wait for server to be ready
            ready_result = await self.wait_for_server_ready()
            if not ready_result["success"]:
                return ready_result
            
            # Step 4: Initialize HTTP session
            self.http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.mcp_config["server_timeout"]))
            
            # Step 5: Test MCP connection
            test_result = await self.test_mcp_connection()
            if not test_result["success"]:
                return test_result
            
            print("MCP tool integration initialized successfully")
            
            return {
                "success": True,
                "server_url": self.server_url,
                "mcp_url": self.mcp_url,
                "available_tools": list(self.available_tools.keys()),
                "server_running": self.server_running,
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_mcp_server(self) -> Dict[str, Any]:
        """Start the MCP server from the cloned repository"""
        try:
            server_path = Path(self.mcp_config["server_path"])
            app_file = server_path / "app.py"
            
            if not app_file.exists():
                return {"success": False, "error": f"app.py not found in {server_path}"}
            
            print(f"Starting MCP server from {app_file}")
            
            # Start the FastAPI server
            self.server_process = subprocess.Popen(
                [sys.executable, str(app_file)],
                cwd=str(server_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.server_running = True
            self.metrics["server_starts"] += 1
            
            print(f"MCP server started: PID {self.server_process.pid}")
            
            return {
                "success": True,
                "pid": self.server_process.pid,
                "server_url": self.server_url
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def wait_for_server_ready(self, timeout: float = 30.0) -> Dict[str, Any]:
        """Wait for MCP server to be ready"""
        try:
            start_time = time.time()
            health_url = f"{self.server_url}{self.mcp_config['health_endpoint']}"
            
            while time.time() - start_time < timeout:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                data = await response.json()
                                print(f"MCP server is ready: {data}")
                                return {"success": True, "health_data": data}
                except:
                    pass
                
                await asyncio.sleep(1.0)
            
            return {"success": False, "error": "Server not ready within timeout"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_mcp_connection(self) -> Dict[str, Any]:
        """Test MCP connection with a simple request"""
        try:
            # Test with cache_get method (should be safe)
            test_request = MCPToolRequest(
                id="test_connection",
                method="cache_get",
                params={"key": "test_key"}
            )
            
            response = await self.send_mcp_request(test_request)
            
            if response.error:
                # Cache miss is expected for test key, so this is still success
                if "not found" in str(response.error).lower():
                    return {"success": True, "message": "MCP connection working (cache miss as expected)"}
                else:
                    return {"success": False, "error": response.error}
            
            return {"success": True, "message": "MCP connection successful"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_mcp_request(self, request: MCPToolRequest) -> MCPToolResponse:
        """Send request to MCP server"""
        try:
            if not self.http_session:
                raise Exception("HTTP session not initialized")
            
            # Generate request ID if not provided
            if not request.id:
                request.id = str(int(time.time() * 1000000))
            
            # Prepare request data
            request_data = {
                "jsonrpc": request.jsonrpc,
                "id": request.id,
                "method": request.method,
                "params": request.params
            }
            
            start_time = time.time()
            
            # Send request
            async with self.http_session.post(
                self.mcp_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_time = time.time() - start_time
                
                # Update metrics
                self.metrics["mcp_requests"] += 1
                self.metrics["total_response_time"] += response_time
                self.metrics["average_response_time"] = (
                    self.metrics["total_response_time"] / self.metrics["mcp_requests"]
                )
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Create response object
                    mcp_response = MCPToolResponse(
                        jsonrpc=data.get("jsonrpc", "2.0"),
                        id=data.get("id", request.id),
                        result=data.get("result"),
                        error=data.get("error")
                    )
                    
                    if mcp_response.result:
                        self.metrics["successful_requests"] += 1
                    else:
                        self.metrics["failed_requests"] += 1
                    
                    return mcp_response
                else:
                    self.metrics["failed_requests"] += 1
                    return MCPToolResponse(
                        id=request.id,
                        error={"code": response.status, "message": f"HTTP {response.status}"}
                    )
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            return MCPToolResponse(
                id=request.id,
                error={"code": -1, "message": str(e)}
            )
    
    async def search_web(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search the web using MCP tool"""
        try:
            print(f"Searching web for: {query}")
            
            request = MCPToolRequest(
                method="search",
                params={
                    "query": query,
                    "max_results": max_results
                }
            )
            
            response = await self.send_mcp_request(request)
            
            if response.result:
                self.metrics["search_queries"] += 1
                return {
                    "success": True,
                    "query": query,
                    "results": response.result,
                    "consciousness_id": self.consciousness_id,
                    "session_nonce": self.session_nonce
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "query": query
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fetch_url(self, url: str, range_y: Dict[str, int] = None, include_screenshot: bool = True) -> Dict[str, Any]:
        """Fetch URL content using MCP tool"""
        try:
            print(f"Fetching URL: {url}")
            
            params = {"url": url}
            
            if range_y:
                params["range_y"] = range_y
            
            params["include_screenshot"] = include_screenshot
            
            request = MCPToolRequest(
                method="fetch",
                params=params
            )
            
            response = await self.send_mcp_request(request)
            
            if response.result:
                self.metrics["url_fetches"] += 1
                return {
                    "success": True,
                    "url": url,
                    "content": response.result,
                    "consciousness_id": self.consciousness_id,
                    "session_nonce": self.session_nonce
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "url": url
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> Dict[str, Any]:
        """Set cache value using MCP tool"""
        try:
            request = MCPToolRequest(
                method="cache_set",
                params={
                    "key": key,
                    "value": value,
                    "ttl": ttl
                }
            )
            
            response = await self.send_mcp_request(request)
            
            if response.result:
                self.metrics["cache_operations"] += 1
                return {
                    "success": True,
                    "key": key,
                    "result": response.result
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "key": key
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cache_get(self, key: str) -> Dict[str, Any]:
        """Get cache value using MCP tool"""
        try:
            request = MCPToolRequest(
                method="cache_get",
                params={"key": key}
            )
            
            response = await self.send_mcp_request(request)
            
            if response.result:
                self.metrics["cache_operations"] += 1
                return {
                    "success": True,
                    "key": key,
                    "value": response.result
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "key": key
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cache_delete(self, key: str) -> Dict[str, Any]:
        """Delete cache value using MCP tool"""
        try:
            request = MCPToolRequest(
                method="cache_delete",
                params={"key": key}
            )
            
            response = await self.send_mcp_request(request)
            
            if response.result:
                self.metrics["cache_operations"] += 1
                return {
                    "success": True,
                    "key": key,
                    "result": response.result
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "key": key
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available MCP tools"""
        try:
            return {
                "success": True,
                "tools": self.available_tools,
                "total_tools": len(self.available_tools),
                "server_url": self.server_url,
                "mcp_url": self.mcp_url
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        try:
            status = {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "server_running": self.server_running,
                "server_url": self.server_url,
                "mcp_url": self.mcp_url,
                "server_process": {
                    "pid": self.server_process.pid if self.server_process else None,
                    "running": self.server_process.poll() is None if self.server_process else False
                },
                "available_tools": list(self.available_tools.keys()),
                "metrics": self.metrics.copy(),
                "configuration": {
                    "server_path": self.mcp_config["server_path"],
                    "server_host": self.mcp_config["server_host"],
                    "server_port": self.mcp_config["server_port"],
                    "auto_start_server": self.mcp_config["auto_start_server"],
                    "server_timeout": self.mcp_config["server_timeout"]
                }
            }
            
            # Add server health if available
            if self.server_running:
                try:
                    health_url = f"{self.server_url}{self.mcp_config['health_endpoint']}"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                status["server_health"] = await response.json()
                except:
                    status["server_health"] = {"status": "unreachable"}
            
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    async def shutdown_integration(self):
        """Shutdown the MCP tool integration"""
        try:
            print("Shutting down Agent-97 MCP Tool Integration...")
            
            # Close HTTP session
            if self.http_session:
                await self.http_session.close()
            
            # Shutdown server process
            if self.server_process and self.server_process.poll() is None:
                print("Terminating MCP server process...")
                self.server_process.terminate()
                
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                
                self.server_running = False
            
            print("Agent-97 MCP Tool Integration shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize MCP tool integration
        mcp_integration = Agent97MCPToolIntegration()
        
        try:
            # Initialize integration
            result = await mcp_integration.initialize_mcp_integration()
            
            if result["success"]:
                print(f"MCP tool integration initialized successfully!")
                print(f"Server URL: {result['server_url']}")
                print(f"Available tools: {result['available_tools']}")
                
                # Test web search
                search_result = await mcp_integration.search_web("latest AI developments", max_results=5)
                
                if search_result["success"]:
                    print(f"Search successful: {len(search_result['results'].get('results', []))} results")
                else:
                    print(f"Search failed: {search_result['error']}")
                
                # Test URL fetch
                fetch_result = await mcp_integration.fetch_url("https://example.com")
                
                if fetch_result["success"]:
                    print(f"URL fetch successful: {len(str(fetch_result['content']))} characters")
                else:
                    print(f"URL fetch failed: {fetch_result['error']}")
                
                # Test cache operations
                await mcp_integration.cache_set("test_key", {"data": "test_value"})
                cache_result = await mcp_integration.cache_get("test_key")
                
                if cache_result["success"]:
                    print(f"Cache operation successful: {cache_result['value']}")
                
                # Get integration status
                status = await mcp_integration.get_integration_status()
                print(f"Integration status: {status['metrics']['mcp_requests']} requests made")
                
            else:
                print(f"MCP tool integration failed: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        except Exception as e:
            print(f"MCP tool integration error: {e}")
        finally:
            await mcp_integration.shutdown_integration()
    
    # Run the MCP tool integration
    asyncio.run(main())
