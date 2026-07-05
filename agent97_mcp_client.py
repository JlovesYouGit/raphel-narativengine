"""
Agent-97 MCP Client for qoder-openclaw-simple
Integrates Agent-97 with the qoder-openclaw-simple MCP server
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import uuid
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import websockets

@dataclass
class MCPServerConfig:
    """MCP Server configuration"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    disabled: bool = False
    timeout: float = 30.0
    max_retries: int = 3

@dataclass
class MCPMessage:
    """MCP message structure"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class Agent97MCPClient:
    """
    Agent-97 MCP Client for qoder-openclaw-simple
    Handles communication with MCP servers
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # MCP server configuration
        self.mcp_servers = {
            "qoder-openclaw-simple": MCPServerConfig(
                name="qoder-openclaw-simple",
                command="node",
                args=["N:\\Windsurf\\simple-mcp-server.js"],
                env={
                    "AUTO_ACCESSIBLE": "true",
                    "NO_SDK_REQUIRED": "true",
                    "OPENCLAW_SIMPLE_MODE": "true",
                    "QODER_SIMPLE_MODE": "true"
                },
                disabled=False
            )
        }
        
        # Connection state
        self.connections = {}  # server_name -> connection info
        self.processes = {}  # server_name -> subprocess handle
        self.websockets = {}  # server_name -> websocket connection
        
        # Communication
        self.message_handlers = {}
        self.pending_requests = {}  # request_id -> future
        self.server_capabilities = {}  # server_name -> capabilities
        
        # Metrics
        self.metrics = {
            "connections_established": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "retries": 0,
            "total_response_time": 0.0,
            "average_response_time": 0.0
        }
        
        # Agent-97 integration
        self.agent97_tools = {}
        self.tool_registry = {}
        
        print(f"Agent-97 MCP Client initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_mcp_connections(self) -> Dict[str, Any]:
        """Initialize connections to all MCP servers"""
        try:
            print("Initializing Agent-97 MCP connections...")
            
            results = {}
            
            for server_name, server_config in self.mcp_servers.items():
                if server_config.disabled:
                    print(f"Skipping disabled server: {server_name}")
                    results[server_name] = {"success": False, "error": "Server disabled"}
                    continue
                
                try:
                    result = await self.connect_to_mcp_server(server_name, server_config)
                    results[server_name] = result
                    
                    if result["success"]:
                        print(f"Connected to MCP server: {server_name}")
                    else:
                        print(f"Failed to connect to {server_name}: {result['error']}")
                
                except Exception as e:
                    results[server_name] = {"success": False, "error": str(e)}
                    print(f"Error connecting to {server_name}: {e}")
            
            # Initialize Agent-97 tools after connections
            await self.initialize_agent97_tools()
            
            return {
                "success": True,
                "results": results,
                "connected_servers": [name for name, result in results.items() if result["success"]],
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def connect_to_mcp_server(self, server_name: str, server_config: MCPServerConfig) -> Dict[str, Any]:
        """Connect to a specific MCP server"""
        try:
            print(f"Connecting to MCP server: {server_name}")
            
            # Start MCP server process
            process = await self.start_mcp_server_process(server_name, server_config)
            
            if not process:
                return {"success": False, "error": "Failed to start server process"}
            
            # Wait for server to start
            await asyncio.sleep(2.0)
            
            # Establish communication (stdio-based for MCP)
            connection_info = {
                "process": process,
                "server_name": server_name,
                "connected_at": time.time(),
                "message_count": 0
            }
            
            self.connections[server_name] = connection_info
            self.processes[server_name] = process
            
            # Initialize MCP session
            init_result = await self.initialize_mcp_session(server_name)
            
            if not init_result["success"]:
                # Cleanup on failure
                await self.disconnect_from_mcp_server(server_name)
                return init_result
            
            # Get server capabilities
            capabilities_result = await self.get_server_capabilities(server_name)
            
            if capabilities_result["success"]:
                self.server_capabilities[server_name] = capabilities_result["capabilities"]
            
            self.metrics["connections_established"] += 1
            
            return {
                "success": True,
                "server_name": server_name,
                "pid": process.pid,
                "capabilities": self.server_capabilities.get(server_name),
                "connected_at": connection_info["connected_at"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_mcp_server_process(self, server_name: str, server_config: MCPServerConfig) -> Optional[subprocess.Popen]:
        """Start MCP server process"""
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(server_config.env)
            
            # Start process
            process = subprocess.Popen(
                [server_config.command] + server_config.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
            print(f"MCP server process started: {server_name} (PID: {process.pid})")
            
            return process
            
        except Exception as e:
            print(f"Failed to start MCP server {server_name}: {e}")
            return None
    
    async def initialize_mcp_session(self, server_name: str) -> Dict[str, Any]:
        """Initialize MCP session with server"""
        try:
            # Send initialize request
            init_message = MCPMessage(
                id=str(uuid.uuid4()),
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        },
                        "roots": {
                            "listChanged": True
                        }
                    },
                    "clientInfo": {
                        "name": "Agent-97 MCP Client",
                        "version": "1.0.0"
                    }
                }
            )
            
            response = await self.send_mcp_message(server_name, init_message)
            
            if response and "result" in response:
                # Send initialized notification
                initialized_message = MCPMessage(
                    method="notifications/initialized",
                    params={}
                )
                
                await self.send_mcp_message(server_name, initialized_message)
                
                return {"success": True, "server_info": response["result"]}
            else:
                return {"success": False, "error": "Initialize failed", "response": response}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_server_capabilities(self, server_name: str) -> Dict[str, Any]:
        """Get server capabilities"""
        try:
            # List available tools
            tools_message = MCPMessage(
                id=str(uuid.uuid4()),
                method="tools/list",
                params={}
            )
            
            response = await self.send_mcp_message(server_name, tools_message)
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                
                # Register tools
                for tool in tools:
                    await self.register_mcp_tool(server_name, tool)
                
                return {
                    "success": True,
                    "capabilities": {
                        "tools": tools,
                        "tool_count": len(tools)
                    }
                }
            else:
                return {"success": False, "error": "Failed to get tools", "response": response}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def register_mcp_tool(self, server_name: str, tool_info: Dict[str, Any]):
        """Register an MCP tool with Agent-97"""
        try:
            tool_name = tool_info["name"]
            tool_description = tool_info.get("description", "")
            
            # Create Agent-97 tool wrapper
            async def tool_wrapper(arguments: Dict[str, Any]) -> Dict[str, Any]:
                return await self.call_mcp_tool(server_name, tool_name, arguments)
            
            # Register with Agent-97
            self.agent97_tools[tool_name] = {
                "name": tool_name,
                "description": tool_description,
                "server": server_name,
                "schema": tool_info.get("inputSchema", {}),
                "handler": tool_wrapper
            }
            
            self.tool_registry[tool_name] = server_name
            
            print(f"Registered MCP tool: {tool_name} from {server_name}")
            
        except Exception as e:
            print(f"Error registering tool {tool_info.get('name', 'unknown')}: {e}")
    
    async def call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        try:
            # Create tool call message
            tool_message = MCPMessage(
                id=str(uuid.uuid4()),
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            
            response = await self.send_mcp_message(server_name, tool_message)
            
            if response and "result" in response:
                return {
                    "success": True,
                    "result": response["result"],
                    "tool_name": tool_name,
                    "server": server_name
                }
            elif response and "error" in response:
                return {
                    "success": False,
                    "error": response["error"],
                    "tool_name": tool_name,
                    "server": server_name
                }
            else:
                return {
                    "success": False,
                    "error": "No response received",
                    "tool_name": tool_name,
                    "server": server_name
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "server": server_name
            }
    
    async def send_mcp_message(self, server_name: str, message: MCPMessage) -> Optional[Dict[str, Any]]:
        """Send message to MCP server"""
        try:
            if server_name not in self.connections:
                print(f"No connection to server: {server_name}")
                return None
            
            connection = self.connections[server_name]
            process = connection["process"]
            
            if not process or process.poll() is not None:
                print(f"Process not running for server: {server_name}")
                return None
            
            # Serialize message
            message_json = json.dumps(message.__dict__)
            
            # Send to process stdin
            process.stdin.write(message_json + "\n")
            process.stdin.flush()
            
            self.metrics["messages_sent"] += 1
            connection["message_count"] += 1
            
            # Wait for response if it's a request (has id)
            if message.id:
                response = await self.wait_for_response(server_name, message.id)
                self.metrics["messages_received"] += 1
                return response
            
            return None
            
        except Exception as e:
            self.metrics["errors"] += 1
            print(f"Error sending message to {server_name}: {e}")
            return None
    
    async def wait_for_response(self, server_name: str, message_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Wait for response from MCP server"""
        try:
            if server_name not in self.connections:
                return None
            
            connection = self.connections[server_name]
            process = connection["process"]
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if not process or process.poll() is not None:
                    break
                
                # Read response
                line = process.stdout.readline()
                if not line:
                    break
                
                try:
                    response = json.loads(line.strip())
                    
                    if response.get("id") == message_id:
                        # Update response time metrics
                        response_time = time.time() - start_time
                        self.metrics["total_response_time"] += response_time
                        self.metrics["average_response_time"] = (
                            self.metrics["total_response_time"] / self.metrics["messages_received"]
                        )
                        
                        return response
                
                except json.JSONDecodeError:
                    continue
                
                await asyncio.sleep(0.01)
            
            print(f"Timeout waiting for response from {server_name}")
            return None
            
        except Exception as e:
            print(f"Error waiting for response from {server_name}: {e}")
            return None
    
    async def initialize_agent97_tools(self):
        """Initialize Agent-97 tools integration"""
        try:
            print("Initializing Agent-97 tools integration...")
            
            # Create tool categories
            self.tool_categories = {
                "qoder_tools": [],
                "openclaw_tools": [],
                "agent97_tools": []
            }
            
            # Categorize tools
            for tool_name, tool_info in self.agent97_tools.items():
                server_name = tool_info["server"]
                
                if "qoder" in server_name.lower():
                    self.tool_categories["qoder_tools"].append(tool_name)
                elif "openclaw" in server_name.lower():
                    self.tool_categories["openclaw_tools"].append(tool_name)
                else:
                    self.tool_categories["agent97_tools"].append(tool_name)
            
            print(f"Agent-97 tools initialized: {len(self.agent97_tools)} tools")
            
        except Exception as e:
            print(f"Error initializing Agent-97 tools: {e}")
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """List all available MCP tools"""
        try:
            tools_by_server = {}
            
            for server_name in self.connections:
                if server_name in self.server_capabilities:
                    capabilities = self.server_capabilities[server_name]
                    tools = capabilities.get("tools", [])
                    tools_by_server[server_name] = tools
            
            return {
                "success": True,
                "total_tools": len(self.agent97_tools),
                "tools_by_server": tools_by_server,
                "tool_categories": self.tool_categories,
                "agent97_tools": list(self.agent97_tools.keys()),
                "connected_servers": list(self.connections.keys())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool"""
        try:
            if tool_name not in self.agent97_tools:
                return {"success": False, "error": f"Tool not found: {tool_name}"}
            
            tool_info = self.agent97_tools[tool_name]
            handler = tool_info["handler"]
            
            # Execute tool
            result = await handler(arguments)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_qoder_status(self) -> Dict[str, Any]:
        """Get QODER server status"""
        try:
            server_name = "qoder-openclaw-simple"
            
            if server_name not in self.connections:
                return {"success": False, "error": "QODER server not connected"}
            
            connection = self.connections[server_name]
            process = connection["process"]
            
            status = {
                "connected": True,
                "pid": process.pid,
                "connected_at": connection["connected_at"],
                "message_count": connection["message_count"],
                "process_alive": process.poll() is None,
                "capabilities": self.server_capabilities.get(server_name, {}),
                "tools_count": len(self.server_capabilities.get(server_name, {}).get("tools", []))
            }
            
            return {"success": True, "status": status}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def disconnect_from_mcp_server(self, server_name: str):
        """Disconnect from MCP server"""
        try:
            if server_name in self.processes:
                process = self.processes[server_name]
                
                if process and process.poll() is None:
                    # Send close notification
                    close_message = MCPMessage(
                        method="notifications/exit",
                        params={}
                    )
                    
                    await self.send_mcp_message(server_name, close_message)
                    
                    # Terminate process
                    process.terminate()
                    
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                
                del self.processes[server_name]
            
            if server_name in self.connections:
                del self.connections[server_name]
            
            if server_name in self.server_capabilities:
                del self.server_capabilities[server_name]
            
            print(f"Disconnected from MCP server: {server_name}")
            
        except Exception as e:
            print(f"Error disconnecting from {server_name}: {e}")
    
    async def shutdown_all_connections(self):
        """Shutdown all MCP connections"""
        try:
            print("Shutting down all MCP connections...")
            
            for server_name in list(self.connections.keys()):
                await self.disconnect_from_mcp_server(server_name)
            
            print("All MCP connections shutdown")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
    
    def get_client_status(self) -> Dict[str, Any]:
        """Get MCP client status"""
        return {
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "connected_servers": list(self.connections.keys()),
            "total_tools": len(self.agent97_tools),
            "tool_categories": self.tool_categories,
            "metrics": self.metrics,
            "server_capabilities": self.server_capabilities,
            "agent97_tools": list(self.agent97_tools.keys())
        }

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize MCP client
        client = Agent97MCPClient()
        
        try:
            # Initialize connections
            result = await client.initialize_mcp_connections()
            
            if result["success"]:
                print(f"MCP connections initialized successfully!")
                print(f"Connected servers: {result['connected_servers']}")
                
                # List available tools
                tools_result = await client.list_available_tools()
                
                if tools_result["success"]:
                    print(f"Available tools: {tools_result['total_tools']}")
                    print(f"QODER tools: {tools_result['tool_categories']['qoder_tools']}")
                
                # Get QODER status
                qoder_status = await client.get_qoder_status()
                
                if qoder_status["success"]:
                    print(f"QODER status: {qoder_status['status']}")
                
                # Example tool execution (if tools are available)
                if client.agent97_tools:
                    tool_name = list(client.agent97_tools.keys())[0]
                    print(f"Executing tool: {tool_name}")
                    
                    tool_result = await client.execute_tool(tool_name, {})
                    print(f"Tool result: {tool_result['success']}")
                
                # Keep running
                print("MCP client running. Press Ctrl+C to stop...")
                while True:
                    await asyncio.sleep(10)
                    
                    # Print status every 60 seconds
                    if int(time.time()) % 60 == 0:
                        status = client.get_client_status()
                        print(f"Status: {len(status['connected_servers'])} servers, {status['total_tools']} tools")
                
            else:
                print(f"MCP connections failed: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        except Exception as e:
            print(f"MCP client error: {e}")
        finally:
            await client.shutdown_all_connections()
    
    # Run the MCP client
    asyncio.run(main())
