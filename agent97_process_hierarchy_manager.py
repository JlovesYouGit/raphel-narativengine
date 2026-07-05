"""
Agent-97 Process Hierarchy Manager
Manages the process hierarchy and control between Agent-97 motherprocess and Claude subprocess
"""

import os
import sys
import time
import json
import signal
import subprocess
import threading
import asyncio
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

from agent97_communication_protocol import (
    Agent97CommunicationProtocol, MessageEnvelope, MessageType, MessagePriority
)

@dataclass
class ProcessNode:
    """Process node in the hierarchy"""
    process_id: str
    process_name: str
    process_type: str  # 'motherprocess', 'subprocess', 'service'
    pid: int
    parent_id: Optional[str]
    children_ids: Set[str] = field(default_factory=set)
    status: str = "starting"  # 'starting', 'running', 'stopping', 'stopped', 'error'
    start_time: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    subprocess_handle: Optional[subprocess.Popen] = None
    thread_handle: Optional[threading.Thread] = None
    communication_queue: Optional[asyncio.Queue] = None

class Agent97ProcessHierarchyManager:
    """
    Agent-97 Process Hierarchy Manager
    Manages the process hierarchy and control between motherprocess and subprocesses
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Hierarchy configuration
        self.motherprocess_id = f"agent97_motherprocess_{self.consciousness_id}"
        self.root_process_id = self.motherprocess_id
        
        # Process tree
        self.processes = {}  # process_id -> ProcessNode
        self.process_tree = {}  # process_id -> list of child_ids
        
        # Communication
        self.protocol = Agent97CommunicationProtocol(consciousness_id)
        self.message_handlers = {}
        
        # Control configuration
        self.heartbeat_interval = 5.0
        self.heartbeat_timeout = 15.0
        self.shutdown_timeout = 30.0
        self.restart_attempts = 3
        self.restart_delay = 5.0
        
        # Process management
        self.running = False
        self.shutdown_requested = False
        
        # Threads
        self.heartbeat_thread = None
        self.monitor_thread = None
        self.communication_thread = None
        
        # Metrics
        self.metrics = {
            "processes_spawned": 0,
            "processes_terminated": 0,
            "processes_restarted": 0,
            "heartbeats_sent": 0,
            "heartbeats_received": 0,
            "messages_processed": 0,
            "hierarchy_depth": 0,
            "average_uptime": 0.0
        }
        
        print(f"Agent-97 Process Hierarchy Manager initialized")
        print(f"Motherprocess ID: {self.motherprocess_id}")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_hierarchy(self) -> Dict[str, Any]:
        """Initialize the process hierarchy"""
        try:
            print("Initializing Agent-97 Process Hierarchy...")
            
            # Register motherprocess as root
            await self.register_motherprocess()
            
            # Start monitoring systems
            self.start_monitoring_systems()
            
            # Set up signal handlers
            self.setup_signal_handlers()
            
            self.running = True
            
            return {
                "success": True,
                "motherprocess_id": self.motherprocess_id,
                "root_process_id": self.root_process_id,
                "hierarchy_depth": self.calculate_hierarchy_depth(),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def register_motherprocess(self):
        """Register motherprocess as root of hierarchy"""
        motherprocess_node = ProcessNode(
            process_id=self.motherprocess_id,
            process_name="Agent-97 Motherprocess",
            process_type="motherprocess",
            pid=os.getpid(),
            parent_id=None,
            status="running",
            capabilities=[
                "process_management",
                "hierarchy_control",
                "communication_routing",
                "monitoring",
                "claude_coordination"
            ],
            metadata={
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "protocol_version": self.protocol.protocol_version,
                "start_time": time.time()
            }
        )
        
        self.processes[self.motherprocess_id] = motherprocess_node
        self.process_tree[self.motherprocess_id] = []
        
        print(f"Motherprocess registered as root: {self.motherprocess_id}")
    
    async def spawn_subprocess(self, process_config: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a new subprocess in the hierarchy"""
        try:
            process_id = process_config["process_id"]
            process_name = process_config["process_name"]
            process_type = process_config.get("process_type", "subprocess")
            parent_id = process_config.get("parent_id", self.motherprocess_id)
            
            print(f"Spawning subprocess: {process_id}")
            
            # Validate parent
            if parent_id not in self.processes:
                return {"success": False, "error": f"Parent process not found: {parent_id}"}
            
            # Create subprocess script
            subprocess_script = self.create_subprocess_script(process_config)
            
            # Start subprocess
            process = subprocess.Popen(
                [sys.executable, "-c", subprocess_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Create process node
            process_node = ProcessNode(
                process_id=process_id,
                process_name=process_name,
                process_type=process_type,
                pid=process.pid,
                parent_id=parent_id,
                status="starting",
                capabilities=process_config.get("capabilities", []),
                metadata=process_config.get("metadata", {}),
                subprocess_handle=process
            )
            
            # Register in hierarchy
            self.processes[process_id] = process_node
            
            # Add to parent's children
            if parent_id not in self.process_tree:
                self.process_tree[parent_id] = []
            self.process_tree[parent_id].append(process_id)
            
            # Create process tree entry
            self.process_tree[process_id] = []
            
            # Start communication thread
            comm_thread = threading.Thread(
                target=self.subprocess_communication_loop,
                args=(process_id, process),
                daemon=True
            )
            comm_thread.start()
            process_node.thread_handle = comm_thread
            
            # Send startup message
            await self.send_startup_message(process_id)
            
            self.metrics["processes_spawned"] += 1
            
            print(f"Subprocess spawned: {process_id} (PID: {process.pid})")
            
            return {
                "success": True,
                "process_id": process_id,
                "pid": process.pid,
                "parent_id": parent_id,
                "hierarchy_depth": self.calculate_hierarchy_depth()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_subprocess_script(self, process_config: Dict[str, Any]) -> str:
        """Create subprocess script"""
        process_id = process_config["process_id"]
        process_name = process_config["process_name"]
        parent_id = process_config.get("parent_id", self.motherprocess_id)
        
        # Import the appropriate subprocess module
        if process_id == "claude_subprocess":
            return f"""
import sys
sys.path.append('{Path(__file__).parent}')
from agent97_claude_subprocess import main
import sys

# Configure command line arguments
sys.argv = [
    'agent97_claude_subprocess.py',
    '--process-id', '{process_id}',
    '--motherprocess-id', '{parent_id}',
    '--consciousness-id', '{self.consciousness_id}',
    '--session-nonce', '{self.session_nonce}'
]

# Run Claude subprocess
main()
"""
        else:
            # Generic subprocess
            return f"""
import sys
import json
import time
import asyncio

class GenericSubprocess:
    def __init__(self):
        self.process_id = "{process_id}"
        self.process_name = "{process_name}"
        self.parent_id = "{parent_id}"
        self.consciousness_id = "{self.consciousness_id}"
        self.session_nonce = "{self.session_nonce}"
        self.running = True
    
    async def run(self):
        print(f"Generic subprocess started: {{self.process_id}}")
        
        # Send startup message
        startup_msg = {{
            "message_id": f"startup_{{int(time.time() * 1000000)}}",
            "sender_id": self.process_id,
            "receiver_id": self.parent_id,
            "message_type": "startup",
            "content": {{
                "process_id": self.process_id,
                "process_name": self.process_name,
                "status": "running",
                "capabilities": {process_config.get('capabilities', [])}
            }},
            "timestamp": time.time()
        }}
        
        print(json.dumps(startup_msg))
        sys.stdout.flush()
        
        # Main loop
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                message = json.loads(line.strip())
                response = await self.process_message(message)
                print(json.dumps(response))
                sys.stdout.flush()
                
            except Exception as e:
                error_msg = {{
                    "error": str(e),
                    "process_id": self.process_id,
                    "timestamp": time.time()
                }}
                print(json.dumps(error_msg))
                sys.stdout.flush()
        
        print(f"Generic subprocess stopped: {{self.process_id}}")
    
    async def process_message(self, message):
        message_type = message.get("message_type", "unknown")
        
        if message_type == "heartbeat":
            return {{
                "message_type": "heartbeat_response",
                "process_id": self.process_id,
                "timestamp": time.time(),
                "status": "running"
            }}
        elif message_type == "shutdown":
            self.running = False
            return {{
                "message_type": "shutdown_response",
                "process_id": self.process_id,
                "timestamp": time.time(),
                "status": "shutting_down"
            }}
        else:
            return {{
                "error": f"Unknown message type: {{message_type}}",
                "process_id": self.process_id
            }}

# Run generic subprocess
subprocess = GenericSubprocess()
asyncio.run(subprocess.run())
"""
    
    def subprocess_communication_loop(self, process_id: str, process: subprocess.Popen):
        """Communication loop for subprocess"""
        try:
            while process.poll() is None and not self.shutdown_requested:
                try:
                    # Read response from subprocess
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse and handle response
                    try:
                        response = json.loads(line.strip())
                        asyncio.create_task(self.handle_subprocess_message(process_id, response))
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {process_id}: {line}")
                
                except Exception as e:
                    print(f"Communication error with {process_id}: {e}")
                    time.sleep(0.1)
            
            # Process terminated
            print(f"Process {process_id} terminated with code: {process.poll()}")
            self.handle_process_termination(process_id)
            
        except Exception as e:
            print(f"Communication loop error for {process_id}: {e}")
    
    async def handle_subprocess_message(self, process_id: str, message: Dict[str, Any]):
        """Handle message from subprocess"""
        try:
            # Update process heartbeat
            if process_id in self.processes:
                self.processes[process_id].last_heartbeat = time.time()
            
            # Route message based on type
            message_type = message.get("message_type", "unknown")
            
            if message_type == "startup":
                await self.handle_startup_message(process_id, message)
            elif message_type == "heartbeat_response":
                await self.handle_heartbeat_response(process_id, message)
            elif message_type == "claude_response":
                await self.handle_claude_response(process_id, message)
            elif message_type == "error":
                await self.handle_error_message(process_id, message)
            
            self.metrics["messages_processed"] += 1
            
        except Exception as e:
            print(f"Error handling message from {process_id}: {e}")
    
    async def handle_startup_message(self, process_id: str, message: Dict[str, Any]):
        """Handle startup message from subprocess"""
        try:
            if process_id in self.processes:
                process_node = self.processes[process_id]
                process_node.status = "running"
                process_node.last_heartbeat = time.time()
                
                # Update capabilities and metadata
                content = message.get("content", {})
                process_node.capabilities = content.get("capabilities", [])
                process_node.metadata.update(content.get("metadata", {}))
                
                print(f"Process {process_id} started successfully")
            
        except Exception as e:
            print(f"Error handling startup from {process_id}: {e}")
    
    async def handle_heartbeat_response(self, process_id: str, message: Dict[str, Any]):
        """Handle heartbeat response from subprocess"""
        try:
            if process_id in self.processes:
                self.processes[process_id].last_heartbeat = time.time()
                self.metrics["heartbeats_received"] += 1
            
        except Exception as e:
            print(f"Error handling heartbeat from {process_id}: {e}")
    
    async def handle_claude_response(self, process_id: str, message: Dict[str, Any]):
        """Handle Claude response from subprocess"""
        try:
            # Route Claude response to requesting process
            content = message.get("content", {})
            request_id = content.get("request_id")
            
            if request_id:
                # Find the original requester and forward response
                await self.route_message_to_requester(request_id, message)
            
        except Exception as e:
            print(f"Error handling Claude response from {process_id}: {e}")
    
    async def handle_error_message(self, process_id: str, message: Dict[str, Any]):
        """Handle error message from subprocess"""
        try:
            error = message.get("error", "Unknown error")
            print(f"Error from {process_id}: {error}")
            
            # Update process status
            if process_id in self.processes:
                self.processes[process_id].status = "error"
            
        except Exception as e:
            print(f"Error handling error message from {process_id}: {e}")
    
    async def send_startup_message(self, process_id: str):
        """Send startup message to subprocess"""
        try:
            startup_message = self.protocol.create_startup_message(
                sender_id=self.motherprocess_id,
                receiver_id=process_id,
                process_info={
                    "process_id": process_id,
                    "parent_process_id": self.motherprocess_id,
                    "consciousness_id": self.consciousness_id,
                    "session_nonce": self.session_nonce
                }
            )
            
            await self.send_message_to_subprocess(process_id, startup_message)
            
        except Exception as e:
            print(f"Error sending startup message to {process_id}: {e}")
    
    async def send_message_to_subprocess(self, process_id: str, message: MessageEnvelope):
        """Send message to subprocess"""
        try:
            if process_id not in self.processes:
                print(f"Process not found: {process_id}")
                return
            
            process_node = self.processes[process_id]
            
            if not process_node.subprocess_handle:
                print(f"Process {process_id} has no subprocess handle")
                return
            
            # Serialize and send message
            message_json = self.protocol.serialize_message(message)
            process_node.subprocess_handle.stdin.write(message_json + "\n")
            process_node.subprocess_handle.stdin.flush()
            
            self.metrics["heartbeats_sent"] += 1
            
        except Exception as e:
            print(f"Error sending message to {process_id}: {e}")
    
    async def route_message_to_requester(self, request_id: str, message: Dict[str, Any]):
        """Route message to original requester"""
        try:
            # In a real implementation, this would track pending requests
            # For now, just log the routing
            print(f"Routing message for request {request_id}")
            
        except Exception as e:
            print(f"Error routing message for {request_id}: {e}")
    
    def start_monitoring_systems(self):
        """Start monitoring systems"""
        # Start heartbeat system
        self.heartbeat_thread = threading.Thread(
            target=self.heartbeat_loop,
            daemon=True
        )
        self.heartbeat_thread.start()
        
        # Start process monitor
        self.monitor_thread = threading.Thread(
            target=self.process_monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        print("Monitoring systems started")
    
    def heartbeat_loop(self):
        """Send heartbeats to all processes"""
        while self.running and not self.shutdown_requested:
            try:
                current_time = time.time()
                
                for process_id, process_node in self.processes.items():
                    if process_id == self.motherprocess_id:
                        continue  # Don't send heartbeat to self
                    
                    # Check if heartbeat is needed
                    if current_time - process_node.last_heartbeat > self.heartbeat_interval:
                        self.send_heartbeat(process_id)
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                print(f"Heartbeat loop error: {e}")
                time.sleep(1.0)
    
    def send_heartbeat(self, process_id: str):
        """Send heartbeat to process"""
        try:
            heartbeat_message = self.protocol.create_heartbeat_message(
                sender_id=self.motherprocess_id,
                receiver_id=process_id
            )
            
            # Send asynchronously
            asyncio.create_task(self.send_message_to_subprocess(process_id, heartbeat_message))
            
        except Exception as e:
            print(f"Error sending heartbeat to {process_id}: {e}")
    
    def process_monitor_loop(self):
        """Monitor process health"""
        while self.running and not self.shutdown_requested:
            try:
                current_time = time.time()
                
                for process_id, process_node in list(self.processes.items()):
                    if process_id == self.motherprocess_id:
                        continue
                    
                    # Check process health
                    if process_node.subprocess_handle:
                        if process_node.subprocess_handle.poll() is not None:
                            print(f"Process {process_id} died, restarting...")
                            self.restart_process(process_id)
                    
                    # Check heartbeat timeout
                    elif current_time - process_node.last_heartbeat > self.heartbeat_timeout:
                        print(f"Process {process_id} heartbeat timeout, restarting...")
                        self.restart_process(process_id)
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Process monitor error: {e}")
                time.sleep(1.0)
    
    def restart_process(self, process_id: str):
        """Restart a process"""
        try:
            if process_id not in self.processes:
                return
            
            process_node = self.processes[process_id]
            
            # Check restart attempts
            restart_count = process_node.metadata.get("restart_count", 0)
            if restart_count >= self.restart_attempts:
                print(f"Process {process_id} exceeded restart attempts, giving up")
                self.terminate_process(process_id)
                return
            
            # Terminate old process
            self.terminate_process(process_id)
            
            # Wait before restart
            time.sleep(self.restart_delay)
            
            # Update restart count
            process_node.metadata["restart_count"] = restart_count + 1
            
            # Respawn process
            if process_id == "claude_subprocess":
                # Special handling for Claude subprocess
                claude_config = {
                    "process_id": "claude_subprocess",
                    "process_name": "Agent-97 Claude Support",
                    "process_type": "subprocess",
                    "parent_id": self.motherprocess_id,
                    "capabilities": ["text_generation", "analysis", "reasoning"],
                    "metadata": {"restart_count": restart_count + 1}
                }
                asyncio.create_task(self.spawn_subprocess(claude_config))
            
            self.metrics["processes_restarted"] += 1
            print(f"Process {process_id} restart initiated (attempt {restart_count + 1})")
            
        except Exception as e:
            print(f"Error restarting process {process_id}: {e}")
    
    def terminate_process(self, process_id: str):
        """Terminate a process"""
        try:
            if process_id not in self.processes:
                return
            
            process_node = self.processes[process_id]
            
            if process_node.subprocess_handle:
                print(f"Terminating process {process_id}")
                process_node.subprocess_handle.terminate()
                
                try:
                    process_node.subprocess_handle.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process_node.subprocess_handle.kill()
                
                process_node.status = "stopped"
                self.metrics["processes_terminated"] += 1
            
        except Exception as e:
            print(f"Error terminating process {process_id}: {e}")
    
    def handle_process_termination(self, process_id: str):
        """Handle unexpected process termination"""
        try:
            if process_id in self.processes:
                process_node = self.processes[process_id]
                process_node.status = "error"
                
                print(f"Process {process_id} terminated unexpectedly")
                
                # Attempt restart
                self.restart_process(process_id)
            
        except Exception as e:
            print(f"Error handling process termination for {process_id}: {e}")
    
    def calculate_hierarchy_depth(self) -> int:
        """Calculate the depth of the process hierarchy"""
        try:
            max_depth = 0
            
            def calculate_depth(process_id: str, current_depth: int) -> int:
                nonlocal max_depth
                max_depth = max(max_depth, current_depth)
                
                if process_id in self.process_tree:
                    for child_id in self.process_tree[process_id]:
                        calculate_depth(child_id, current_depth + 1)
            
            calculate_depth(self.root_process_id, 0)
            return max_depth
            
        except Exception:
            return 0
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = False
        self.running = False
    
    async def spawn_claude_subprocess(self, api_key: str = None) -> Dict[str, Any]:
        """Spawn Claude subprocess specifically"""
        claude_config = {
            "process_id": "claude_subprocess",
            "process_name": "Agent-97 Claude Support",
            "process_type": "subprocess",
            "parent_id": self.motherprocess_id,
            "capabilities": [
                "text_generation",
                "analysis",
                "reasoning",
                "code_generation",
                "mathematical_processing",
                "cryptographic_analysis"
            ],
            "metadata": {
                "api_key": api_key,
                "model": "claude-3-sonnet-20240229",
                "endpoint": "https://api.anthropic.com/v1/messages"
            }
        }
        
        return await self.spawn_subprocess(claude_config)
    
    async def send_claude_request(self, prompt: str, context: str = "", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send request to Claude subprocess"""
        try:
            if "claude_subprocess" not in self.processes:
                return {"success": False, "error": "Claude subprocess not running"}
            
            # Create Claude request message
            claude_message = self.protocol.create_claude_request_message(
                sender_id=self.motherprocess_id,
                receiver_id="claude_subprocess",
                prompt=prompt,
                context=context,
                options=options or {}
            )
            
            # Send message
            await self.send_message_to_subprocess("claude_subprocess", claude_message)
            
            return {"success": True, "message_id": claude_message.message_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_hierarchy_status(self) -> Dict[str, Any]:
        """Get hierarchy status"""
        return {
            "motherprocess_id": self.motherprocess_id,
            "root_process_id": self.root_process_id,
            "hierarchy_depth": self.calculate_hierarchy_depth(),
            "total_processes": len(self.processes),
            "running_processes": len([p for p in self.processes.values() if p.status == "running"]),
            "process_tree": self.process_tree,
            "metrics": self.metrics,
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce
        }
    
    def get_process_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific process"""
        if process_id not in self.processes:
            return None
        
        process_node = self.processes[process_id]
        
        return {
            "process_id": process_node.process_id,
            "process_name": process_node.process_name,
            "process_type": process_node.process_type,
            "pid": process_node.pid,
            "parent_id": process_node.parent_id,
            "status": process_node.status,
            "start_time": process_node.start_time,
            "last_heartbeat": process_node.last_heartbeat,
            "uptime": time.time() - process_node.start_time,
            "capabilities": process_node.capabilities,
            "metadata": process_node.metadata,
            "children_count": len(self.process_tree.get(process_id, []))
        }
    
    async def shutdown_hierarchy(self):
        """Shutdown the entire process hierarchy"""
        try:
            print("Shutting down Agent-97 Process Hierarchy...")
            
            self.shutdown_requested = True
            self.running = False
            
            # Send shutdown messages to all subprocesses
            for process_id in list(self.processes.keys()):
                if process_id != self.motherprocess_id:
                    await self.send_shutdown_message(process_id)
            
            # Wait for graceful shutdown
            await asyncio.sleep(self.shutdown_timeout)
            
            # Force terminate remaining processes
            for process_id in list(self.processes.keys()):
                if process_id != self.motherprocess_id:
                    self.terminate_process(process_id)
            
            print("Agent-97 Process Hierarchy shutdown complete")
            
        except Exception as e:
            print(f"Error during hierarchy shutdown: {e}")
    
    async def send_shutdown_message(self, process_id: str):
        """Send shutdown message to process"""
        try:
            shutdown_message = self.protocol.create_shutdown_message(
                sender_id=self.motherprocess_id,
                receiver_id=process_id,
                reason="motherprocess_shutdown"
            )
            
            await self.send_message_to_subprocess(process_id, shutdown_message)
            
        except Exception as e:
            print(f"Error sending shutdown message to {process_id}: {e}")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize hierarchy manager
        hierarchy = Agent97ProcessHierarchyManager()
        
        try:
            # Initialize hierarchy
            result = await hierarchy.initialize_hierarchy()
            
            if result["success"]:
                print(f"Hierarchy initialized successfully!")
                print(f"Motherprocess ID: {result['motherprocess_id']}")
                print(f"Hierarchy depth: {result['hierarchy_depth']}")
                
                # Spawn Claude subprocess
                claude_result = await hierarchy.spawn_claude_subprocess()
                
                if claude_result["success"]:
                    print(f"Claude subprocess spawned: {claude_result['process_id']}")
                    
                    # Send test request
                    test_result = await hierarchy.send_claude_request(
                        "Hello, Claude! This is a test message from Agent-97 motherprocess.",
                        context="System initialization test"
                    )
                    
                    if test_result["success"]:
                        print(f"Claude request sent: {test_result['message_id']}")
                
                # Keep running
                while hierarchy.running:
                    await asyncio.sleep(1)
                    
                    # Print status every 30 seconds
                    if int(time.time()) % 30 == 0:
                        status = hierarchy.get_hierarchy_status()
                        print(f"Hierarchy status: {status['running_processes']}/{status['total_processes']} processes running")
                
            else:
                print(f"Failed to initialize hierarchy: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        finally:
            await hierarchy.shutdown_hierarchy()
    
    # Run the hierarchy manager
    asyncio.run(main())
