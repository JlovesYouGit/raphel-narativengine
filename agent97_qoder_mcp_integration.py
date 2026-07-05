"""
Agent-97 QODER MCP Integration Script
Comprehensive integration script for Agent-97 with qoder-openclaw-simple MCP server
"""

import os
import sys
import json
import time
import asyncio
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import Agent-97 components
from agent97_mcp_client import Agent97MCPClient
from agent97_mcp_tools_integration import Agent97MCPToolsIntegration

class Agent97QODERMCPIntegration:
    """
    Agent-97 QODER MCP Integration
    Comprehensive integration for Agent-97 with qoder-openclaw-simple MCP server
    """
    
    def __init__(self, config_file: str = None, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Load configuration
        self.config_file = config_file or "agent97_qoder_mcp_config.json"
        self.config = self.load_configuration()
        
        # Core components
        self.mcp_client = None
        self.tools_integration = None
        
        # Integration state
        self.running = False
        self.initialized = False
        
        # Metrics
        self.metrics = {
            "integration_start_time": 0.0,
            "mcp_connections": 0,
            "tools_registered": 0,
            "tools_executed": 0,
            "errors": 0,
            "uptime": 0.0
        }
        
        print(f"Agent-97 QODER MCP Integration initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
        print(f"Configuration: {self.config_file}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"Configuration loaded from {self.config_file}")
                return config
            else:
                print(f"Configuration file not found: {self.config_file}")
                return self.get_default_configuration()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return self.get_default_configuration()
    
    def get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "consciousness_id": self.consciousness_id,
            "integration_name": "Agent-97 QODER MCP Integration",
            "version": "1.0.0",
            "mcp_servers": {
                "qoder-openclaw-simple": {
                    "name": "qoder-openclaw-simple",
                    "command": "node",
                    "args": ["N:\\Windsurf\\simple-mcp-server.js"],
                    "env": {
                        "AUTO_ACCESSIBLE": "true",
                        "NO_SDK_REQUIRED": "true",
                        "OPENCLAW_SIMPLE_MODE": "true",
                        "QODER_SIMPLE_MODE": "true"
                    },
                    "disabled": False,
                    "timeout": 30.0,
                    "max_retries": 3
                }
            },
            "agent97_components": {
                "mcp_client": {"enabled": True},
                "system_file_viewer": {"enabled": True},
                "quantum_file_completer": {"enabled": True},
                "transformer_gateway": {"enabled": True}
            },
            "tool_categories": {
                "file_operations": {"enabled": True},
                "quantum_processing": {"enabled": True},
                "ai_analysis": {"enabled": True},
                "system_monitoring": {"enabled": True},
                "cryptographic_operations": {"enabled": True}
            }
        }
    
    async def initialize_integration(self) -> Dict[str, Any]:
        """Initialize the complete QODER MCP integration"""
        try:
            start_time = time.time()
            
            print("Initializing Agent-97 QODER MCP Integration...")
            
            # Step 1: Initialize MCP client
            if self.config["agent97_components"]["mcp_client"]["enabled"]:
                self.mcp_client = Agent97MCPClient(self.consciousness_id)
                
                # Configure MCP servers
                await self.configure_mcp_client()
                
                # Initialize connections
                mcp_result = await self.mcp_client.initialize_mcp_connections()
                
                if not mcp_result["success"]:
                    return {"success": False, "error": f"MCP client failed: {mcp_result['error']}"}
                
                self.metrics["mcp_connections"] = len(mcp_result["connected_servers"])
                print(f"MCP client connected to {len(mcp_result['connected_servers'])} servers")
            
            # Step 2: Initialize tools integration
            self.tools_integration = Agent97MCPToolsIntegration(self.consciousness_id)
            
            # Configure tools integration
            await self.configure_tools_integration()
            
            # Initialize tools
            tools_result = await self.tools_integration.initialize_integration()
            
            if not tools_result["success"]:
                return {"success": False, "error": f"Tools integration failed: {tools_result['error']}"}
            
            self.metrics["tools_registered"] = tools_result["agent97_tools"]
            print(f"Tools integration registered {tools_result['agent97_tools']} tools")
            
            # Step 3: Setup inter-component communication
            await self.setup_component_communication()
            
            # Update state
            self.initialized = True
            self.running = True
            self.metrics["integration_start_time"] = time.time()
            
            initialization_time = time.time() - start_time
            
            return {
                "success": True,
                "initialization_time": initialization_time,
                "mcp_connections": self.metrics["mcp_connections"],
                "tools_registered": self.metrics["tools_registered"],
                "connected_servers": mcp_result.get("connected_servers", []),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def configure_mcp_client(self):
        """Configure MCP client with configuration"""
        try:
            # Update MCP server configurations
            for server_name, server_config in self.config["mcp_servers"].items():
                if server_name in self.mcp_client.mcp_servers:
                    mcp_server_config = self.mcp_client.mcp_servers[server_name]
                    
                    # Update configuration
                    mcp_server_config.disabled = server_config.get("disabled", False)
                    mcp_server_config.timeout = server_config.get("timeout", 30.0)
                    mcp_server_config.max_retries = server_config.get("max_retries", 3)
                    
                    # Update environment
                    if "env" in server_config:
                        mcp_server_config.env.update(server_config["env"])
                    
                    # Add Agent-97 specific environment variables
                    mcp_server_config.env.update({
                        "AGENT97_CONSCIOUSNESS_ID": self.consciousness_id,
                        "AGENT97_SESSION_NONCE": self.session_nonce
                    })
            
            print("MCP client configured")
            
        except Exception as e:
            print(f"Error configuring MCP client: {e}")
    
    async def configure_tools_integration(self):
        """Configure tools integration with configuration"""
        try:
            # Update integration configuration
            integration_config = self.config.get("agent97_components", {})
            
            for component, config in integration_config.items():
                if hasattr(self.tools_integration, "integration_config"):
                    self.tools_integration.integration_config[f"{component}_enabled"] = config.get("enabled", True)
            
            # Update tool categories
            tool_categories = self.config.get("tool_categories", {})
            
            for category, config in tool_categories.items():
                if category in self.tools_integration.tool_categories:
                    self.tools_integration.tool_categories[category] = config.get("tools", [])
            
            print("Tools integration configured")
            
        except Exception as e:
            print(f"Error configuring tools integration: {e}")
    
    async def setup_component_communication(self):
        """Setup communication between components"""
        try:
            # Share MCP client with tools integration
            if self.mcp_client and self.tools_integration:
                self.tools_integration.mcp_client = self.mcp_client
            
            print("Component communication setup complete")
            
        except Exception as e:
            print(f"Error setting up component communication: {e}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool through the integration"""
        try:
            if not self.tools_integration:
                return {"success": False, "error": "Tools integration not initialized"}
            
            result = await self.tools_integration.execute_tool(tool_name, arguments)
            
            if result["success"]:
                self.metrics["tools_executed"] += 1
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            return {"success": False, "error": str(e)}
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        try:
            if not self.tools_integration:
                return {"success": False, "error": "Tools integration not initialized"}
            
            return await self.tools_integration.list_tools()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        try:
            status = {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "initialized": self.initialized,
                "running": self.running,
                "uptime": time.time() - self.metrics["integration_start_time"] if self.metrics["integration_start_time"] > 0 else 0,
                "metrics": self.metrics.copy(),
                "configuration": self.config_file
            }
            
            # Add MCP client status
            if self.mcp_client:
                status["mcp_client"] = self.mcp_client.get_client_status()
            
            # Add tools integration status
            if self.tools_integration:
                tools_status = await self.tools_integration.get_system_status()
                if tools_status["success"]:
                    status["tools_integration"] = tools_status["status"]
            
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_qoder_status(self) -> Dict[str, Any]:
        """Get QODER server specific status"""
        try:
            if not self.mcp_client:
                return {"success": False, "error": "MCP client not initialized"}
            
            return await self.mcp_client.get_qoder_status()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_integration_loop(self):
        """Main integration loop"""
        try:
            print("Starting Agent-97 QODER MCP Integration loop...")
            
            while self.running:
                try:
                    # Update metrics
                    if self.metrics["integration_start_time"] > 0:
                        self.metrics["uptime"] = time.time() - self.metrics["integration_start_time"]
                    
                    # Perform health checks
                    await self.perform_health_checks()
                    
                    # Sleep for a short interval
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    print(f"Integration loop error: {e}")
                    self.metrics["errors"] += 1
                    await asyncio.sleep(1.0)
            
        except Exception as e:
            print(f"Fatal integration loop error: {e}")
    
    async def perform_health_checks(self):
        """Perform health checks on all components"""
        try:
            # Check MCP client
            if self.mcp_client:
                qoder_status = await self.get_qoder_status()
                if not qoder_status["success"]:
                    print(f"QODER health check failed: {qoder_status['error']}")
            
            # Check tools integration
            if self.tools_integration:
                tools_status = await self.tools_integration.get_system_status()
                if not tools_status["success"]:
                    print(f"Tools integration health check failed: {tools_status['error']}")
            
        except Exception as e:
            print(f"Health check error: {e}")
    
    async def shutdown_integration(self):
        """Shutdown the complete integration"""
        try:
            print("Shutting down Agent-97 QODER MCP Integration...")
            
            self.running = False
            
            # Shutdown tools integration
            if self.tools_integration:
                await self.tools_integration.shutdown_integration()
            
            # Shutdown MCP client
            if self.mcp_client:
                await self.mcp_client.shutdown_all_connections()
            
            print("Agent-97 QODER MCP Integration shutdown complete")
            
        except Exception as e:
            print(f"Error during integration shutdown: {e}")
    
    def create_default_config_file(self, file_path: str = None):
        """Create default configuration file"""
        try:
            config_file = file_path or "agent97_qoder_mcp_config.json"
            
            default_config = self.get_default_configuration()
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"Default configuration created: {config_file}")
            return config_file
            
        except Exception as e:
            print(f"Error creating configuration file: {e}")
            return None

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agent-97 QODER MCP Integration")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--consciousness-id", default="0009095353", help="Consciousness ID")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration file")
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
    parser.add_argument("--execute-tool", help="Execute a specific tool")
    parser.add_argument("--tool-args", help="JSON arguments for tool execution")
    parser.add_argument("--status", action="store_true", help="Show integration status and exit")
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        integration = Agent97QODERMCPIntegration(args.config, args.consciousness_id)
        integration.create_default_config_file()
        return
    
    # Initialize integration
    integration = Agent97QODERMCPIntegration(args.config, args.consciousness_id)
    
    try:
        # Initialize integration
        result = await integration.initialize_integration()
        
        if result["success"]:
            print(f"Integration initialized successfully in {result['initialization_time']:.2f}s")
            print(f"MCP connections: {result['mcp_connections']}")
            print(f"Tools registered: {result['tools_registered']}")
            print(f"Connected servers: {result['connected_servers']}")
            
            # Handle specific commands
            if args.list_tools:
                tools_result = await integration.list_available_tools()
                
                if tools_result["success"]:
                    print(f"\nAvailable Tools ({tools_result['total_tools']}):")
                    for tool_name, tool_info in tools_result["tools"].items():
                        print(f"  - {tool_name}: {tool_info['description']}")
                        print(f"    Category: {tool_info['category']}")
                        print(f"    Component: {tool_info['agent97_component']}")
                return
            
            elif args.execute_tool:
                tool_args = {}
                if args.tool_args:
                    tool_args = json.loads(args.tool_args)
                
                print(f"Executing tool: {args.execute_tool}")
                tool_result = await integration.execute_tool(args.execute_tool, tool_args)
                
                if tool_result["success"]:
                    print("Tool execution successful!")
                    print(f"Result: {json.dumps(tool_result, indent=2)}")
                else:
                    print(f"Tool execution failed: {tool_result['error']}")
                return
            
            elif args.status:
                status = await integration.get_integration_status()
                print(f"Integration Status:")
                print(f"  Initialized: {status['initialized']}")
                print(f"  Running: {status['running']}")
                print(f"  Uptime: {status['uptime']:.2f}s")
                print(f"  Tools executed: {status['metrics']['tools_executed']}")
                print(f"  Errors: {status['metrics']['errors']}")
                return
            
            # Run integration loop
            await integration.run_integration_loop()
            
        else:
            print(f"Integration initialization failed: {result['error']}")
            
    except KeyboardInterrupt:
        print("Shutdown requested by user")
    except Exception as e:
        print(f"Integration error: {e}")
    finally:
        await integration.shutdown_integration()

if __name__ == "__main__":
    asyncio.run(main())
