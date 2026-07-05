"""
Agent-97 Claude Motherprocess Integration Script
Comprehensive integration script for Agent-97 as motherprocess with Claude subprocess support
"""

import os
import sys
import time
import json
import asyncio
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import Agent-97 components
from agent97_motherprocess_bridge import Agent97MotherprocessBridge
from agent97_process_hierarchy_manager import Agent97ProcessHierarchyManager
from agent97_communication_protocol import Agent97CommunicationProtocol

class Agent97ClaudeMotherprocessIntegration:
    """
    Agent-97 Claude Motherprocess Integration
    Comprehensive integration for Agent-97 as motherprocess with Claude subprocess support
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Core components
        self.motherprocess_bridge = None
        self.hierarchy_manager = None
        self.communication_protocol = None
        
        # Integration configuration
        self.integration_config = {
            "motherprocess_enabled": True,
            "claude_subprocess_enabled": True,
            "hierarchy_management_enabled": True,
            "communication_protocol_enabled": True,
            "auto_restart_enabled": True,
            "monitoring_enabled": True,
            "security_enabled": True
        }
        
        # Claude configuration
        self.claude_config = {
            "api_key": None,
            "model": "claude-3-sonnet-20240229",
            "endpoint": "https://api.anthropic.com/v1/messages",
            "max_tokens": 1000,
            "timeout": 30.0,
            "auto_spawn": True
        }
        
        # Process configuration
        self.process_config = {
            "heartbeat_interval": 5.0,
            "heartbeat_timeout": 15.0,
            "shutdown_timeout": 30.0,
            "restart_attempts": 3,
            "restart_delay": 5.0
        }
        
        # Communication configuration
        self.communication_config = {
            "port": 9742,
            "max_message_size": 1024 * 1024,  # 1MB
            "default_timeout": 30.0,
            "encryption_enabled": True,
            "signature_enabled": True
        }
        
        # Integration state
        self.running = False
        self.initialized = False
        
        # Metrics
        self.metrics = {
            "integration_start_time": 0.0,
            "processes_spawned": 0,
            "messages_processed": 0,
            "claude_requests": 0,
            "errors": 0,
            "uptime": 0.0
        }
        
        print(f"Agent-97 Claude Motherprocess Integration initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_integration(self) -> Dict[str, Any]:
        """Initialize the complete integration"""
        try:
            start_time = time.time()
            
            print("Initializing Agent-97 Claude Motherprocess Integration...")
            
            # Step 1: Initialize communication protocol
            if self.integration_config["communication_protocol_enabled"]:
                self.communication_protocol = Agent97CommunicationProtocol(self.consciousness_id)
                print("Communication protocol initialized")
            
            # Step 2: Initialize motherprocess bridge
            if self.integration_config["motherprocess_enabled"]:
                self.motherprocess_bridge = Agent97MotherprocessBridge(self.consciousness_id)
                bridge_result = await self.motherprocess_bridge.start_motherprocess()
                
                if not bridge_result["success"]:
                    return {"success": False, "error": f"Motherprocess bridge failed: {bridge_result['error']}"}
                
                print("Motherprocess bridge initialized")
            
            # Step 3: Initialize hierarchy manager
            if self.integration_config["hierarchy_management_enabled"]:
                self.hierarchy_manager = Agent97ProcessHierarchyManager(self.consciousness_id)
                hierarchy_result = await self.hierarchy_manager.initialize_hierarchy()
                
                if not hierarchy_result["success"]:
                    return {"success": False, "error": f"Hierarchy manager failed: {hierarchy_result['error']}"}
                
                print("Hierarchy manager initialized")
            
            # Step 4: Configure Claude subprocess
            if self.integration_config["claude_subprocess_enabled"] and self.claude_config["auto_spawn"]:
                claude_result = await self.spawn_claude_subprocess()
                
                if not claude_result["success"]:
                    print(f"Warning: Claude subprocess spawn failed: {claude_result['error']}")
                else:
                    print("Claude subprocess spawned successfully")
            
            # Step 5: Configure component interconnections
            await self.configure_interconnections()
            
            # Update state
            self.initialized = True
            self.running = True
            self.metrics["integration_start_time"] = time.time()
            
            initialization_time = time.time() - start_time
            
            return {
                "success": True,
                "initialization_time": initialization_time,
                "components": {
                    "motherprocess_bridge": self.motherprocess_bridge is not None,
                    "hierarchy_manager": self.hierarchy_manager is not None,
                    "communication_protocol": self.communication_protocol is not None,
                    "claude_subprocess": "claude_subprocess" in (self.hierarchy_manager.processes if self.hierarchy_manager else {})
                },
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "integration_config": self.integration_config
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def configure_interconnections(self):
        """Configure interconnections between components"""
        try:
            # Connect motherprocess bridge to hierarchy manager
            if self.motherprocess_bridge and self.hierarchy_manager:
                # Share process information
                self.motherprocess_bridge.processes = self.hierarchy_manager.processes
                
                # Configure communication
                if self.communication_protocol:
                    self.motherprocess_bridge.protocol = self.communication_protocol
                    self.hierarchy_manager.protocol = self.communication_protocol
            
            print("Component interconnections configured")
            
        except Exception as e:
            print(f"Error configuring interconnections: {e}")
    
    async def spawn_claude_subprocess(self, api_key: str = None) -> Dict[str, Any]:
        """Spawn Claude subprocess with configuration"""
        try:
            if not self.hierarchy_manager:
                return {"success": False, "error": "Hierarchy manager not initialized"}
            
            # Use provided API key or default
            api_key = api_key or self.claude_config["api_key"]
            
            # Spawn Claude subprocess
            result = await self.hierarchy_manager.spawn_claude_subprocess(api_key)
            
            if result["success"]:
                self.metrics["processes_spawned"] += 1
                
                # Update Claude configuration
                if "claude_subprocess" in self.hierarchy_manager.processes:
                    claude_process = self.hierarchy_manager.processes["claude_subprocess"]
                    claude_process.metadata.update(self.claude_config)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_claude_request(self, prompt: str, context: str = "", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send request to Claude subprocess"""
        try:
            if not self.hierarchy_manager:
                return {"success": False, "error": "Hierarchy manager not initialized"}
            
            result = await self.hierarchy_manager.send_claude_request(prompt, context, options)
            
            if result["success"]:
                self.metrics["claude_requests"] += 1
            
            return result
            
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
                "integration_config": self.integration_config.copy(),
                "claude_config": self.claude_config.copy(),
                "process_config": self.process_config.copy(),
                "communication_config": self.communication_config.copy()
            }
            
            # Add component statuses
            if self.motherprocess_bridge:
                status["motherprocess_bridge"] = self.motherprocess_bridge.get_status()
            
            if self.hierarchy_manager:
                status["hierarchy_manager"] = self.hierarchy_manager.get_hierarchy_status()
            
            if self.communication_protocol:
                status["communication_protocol"] = self.communication_protocol.get_protocol_info()
            
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    async def update_claude_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update Claude configuration"""
        try:
            # Update local configuration
            self.claude_config.update(new_config)
            
            # Update running Claude subprocess if available
            if self.hierarchy_manager and "claude_subprocess" in self.hierarchy_manager.processes:
                claude_process = self.hierarchy_manager.processes["claude_subprocess"]
                claude_process.metadata.update(new_config)
                
                # Send config update message
                if self.communication_protocol:
                    config_message = self.communication_protocol.create_message(
                        sender_id=self.hierarchy_manager.motherprocess_id,
                        receiver_id="claude_subprocess",
                        message_type=self.communication_protocol.MessageType.CONFIG_UPDATE,
                        content={"config": new_config}
                    )
                    
                    await self.hierarchy_manager.send_message_to_subprocess("claude_subprocess", config_message)
            
            return {"success": True, "updated_config": self.claude_config}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def spawn_custom_subprocess(self, process_config: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a custom subprocess"""
        try:
            if not self.hierarchy_manager:
                return {"success": False, "error": "Hierarchy manager not initialized"}
            
            result = await self.hierarchy_manager.spawn_subprocess(process_config)
            
            if result["success"]:
                self.metrics["processes_spawned"] += 1
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def terminate_subprocess(self, process_id: str) -> Dict[str, Any]:
        """Terminate a specific subprocess"""
        try:
            if not self.hierarchy_manager:
                return {"success": False, "error": "Hierarchy manager not initialized"}
            
            if process_id not in self.hierarchy_manager.processes:
                return {"success": False, "error": f"Process not found: {process_id}"}
            
            self.hierarchy_manager.terminate_process(process_id)
            
            return {"success": True, "terminated_process": process_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_processes(self) -> Dict[str, Any]:
        """List all processes in the hierarchy"""
        try:
            if not self.hierarchy_manager:
                return {"success": False, "error": "Hierarchy manager not initialized"}
            
            processes = {}
            for process_id in self.hierarchy_manager.processes:
                process_info = self.hierarchy_manager.get_process_info(process_id)
                if process_info:
                    processes[process_id] = process_info
            
            return {
                "success": True,
                "processes": processes,
                "total_count": len(processes),
                "hierarchy_depth": self.hierarchy_manager.calculate_hierarchy_depth()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_integration_loop(self):
        """Main integration loop"""
        try:
            print("Starting Agent-97 Claude Motherprocess Integration loop...")
            
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
            # Check motherprocess bridge
            if self.motherprocess_bridge and not self.motherprocess_bridge.running:
                print("Motherprocess bridge not running, attempting restart...")
                # Attempt restart logic here
            
            # Check hierarchy manager
            if self.hierarchy_manager and not self.hierarchy_manager.running:
                print("Hierarchy manager not running, attempting restart...")
                # Attempt restart logic here
            
            # Check Claude subprocess
            if self.hierarchy_manager and "claude_subprocess" in self.hierarchy_manager.processes:
                claude_process = self.hierarchy_manager.processes["claude_subprocess"]
                if claude_process.status != "running":
                    print(f"Claude subprocess status: {claude_process.status}")
            
        except Exception as e:
            print(f"Health check error: {e}")
    
    async def shutdown_integration(self):
        """Shutdown the complete integration"""
        try:
            print("Shutting down Agent-97 Claude Motherprocess Integration...")
            
            self.running = False
            
            # Shutdown hierarchy manager
            if self.hierarchy_manager:
                await self.hierarchy_manager.shutdown_hierarchy()
            
            # Shutdown motherprocess bridge
            if self.motherprocess_bridge:
                await self.motherprocess_bridge.shutdown()
            
            print("Agent-97 Claude Motherprocess Integration shutdown complete")
            
        except Exception as e:
            print(f"Error during integration shutdown: {e}")
    
    def set_claude_api_key(self, api_key: str):
        """Set Claude API key"""
        self.claude_config["api_key"] = api_key
        print("Claude API key set")
    
    def enable_auto_restart(self, enabled: bool = True):
        """Enable or disable auto-restart"""
        self.integration_config["auto_restart_enabled"] = enabled
        print(f"Auto-restart {'enabled' if enabled else 'disabled'}")
    
    def set_heartbeat_interval(self, interval: float):
        """Set heartbeat interval"""
        self.process_config["heartbeat_interval"] = interval
        if self.hierarchy_manager:
            self.hierarchy_manager.heartbeat_interval = interval
        print(f"Heartbeat interval set to {interval}s")

def create_default_config_file() -> str:
    """Create default configuration file"""
    config = {
        "consciousness_id": "0009095353",
        "claude_config": {
            "api_key": None,
            "model": "claude-3-sonnet-20240229",
            "endpoint": "https://api.anthropic.com/v1/messages",
            "max_tokens": 1000,
            "timeout": 30.0,
            "auto_spawn": True
        },
        "process_config": {
            "heartbeat_interval": 5.0,
            "heartbeat_timeout": 15.0,
            "shutdown_timeout": 30.0,
            "restart_attempts": 3,
            "restart_delay": 5.0
        },
        "communication_config": {
            "port": 9742,
            "max_message_size": 1048576,
            "default_timeout": 30.0,
            "encryption_enabled": True,
            "signature_enabled": True
        },
        "integration_config": {
            "motherprocess_enabled": True,
            "claude_subprocess_enabled": True,
            "hierarchy_management_enabled": True,
            "communication_protocol_enabled": True,
            "auto_restart_enabled": True,
            "monitoring_enabled": True,
            "security_enabled": True
        }
    }
    
    return json.dumps(config, indent=2)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agent-97 Claude Motherprocess Integration")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--api-key", help="Claude API key")
    parser.add_argument("--consciousness-id", default="0009095353", help="Consciousness ID")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration file")
    parser.add_argument("--port", type=int, default=9742, help="Communication port")
    parser.add_argument("--no-claude", action="store_true", help="Disable Claude subprocess")
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        config_content = create_default_config_file()
        config_file = "agent97_claude_config.json"
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"Default configuration created: {config_file}")
        return
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize integration
    integration = Agent97ClaudeMotherprocessIntegration(
        consciousness_id=args.consciousness_id
    )
    
    # Apply configuration
    if config:
        integration.claude_config.update(config.get("claude_config", {}))
        integration.process_config.update(config.get("process_config", {}))
        integration.communication_config.update(config.get("communication_config", {}))
        integration.integration_config.update(config.get("integration_config", {}))
    
    # Override with command line arguments
    if args.api_key:
        integration.set_claude_api_key(args.api_key)
    
    if args.no_claude:
        integration.integration_config["claude_subprocess_enabled"] = False
    
    if args.port:
        integration.communication_config["port"] = args.port
    
    try:
        # Initialize integration
        result = await integration.initialize_integration()
        
        if result["success"]:
            print(f"Integration initialized successfully in {result['initialization_time']:.2f}s")
            
            # Display status
            status = await integration.get_integration_status()
            print(f"Motherprocess ID: {status.get('motherprocess_bridge', {}).get('motherprocess_id', 'unknown')}")
            print(f"Processes running: {status.get('hierarchy_manager', {}).get('running_processes', 0)}")
            print(f"Claude subprocess: {'Yes' if result['components'].get('claude_subprocess') else 'No'}")
            
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
