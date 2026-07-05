"""
Agent-97 Motherprocess Communication Bridge
Sets up Agent-97 as motherprocess with Claude support internal communication
"""

import os
import sys
import time
import json
import hashlib
import secrets
import subprocess
import threading
import queue
import signal
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
import asyncio
import aiohttp
from dataclasses import dataclass, field
from collections import defaultdict, deque

@dataclass
class ProcessMessage:
    """Message structure for inter-process communication"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str  # 'command', 'response', 'status', 'heartbeat'
    content: Dict[str, Any]
    timestamp: float
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    requires_response: bool = False
    response_timeout: float = 30.0

@dataclass
class ProcessInfo:
    """Process information structure"""
    process_id: str
    process_name: str
    process_type: str  # 'motherprocess', 'subprocess'
    pid: int
    status: str  # 'running', 'stopped', 'error'
    start_time: float
    last_heartbeat: float
    communication_queue: queue.Queue = field(default_factory=queue.Queue)
    subprocess_handle: Optional[subprocess.Popen] = None
    thread_handle: Optional[threading.Thread] = None

class Agent97MotherprocessBridge:
    """
    Agent-97 Motherprocess Communication Bridge
    Manages Agent-97 as motherprocess with Claude support internal communication
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Motherprocess configuration
        self.motherprocess_id = f"agent97_motherprocess_{self.consciousness_id}"
        self.is_motherprocess = True
        self.motherprocess_pid = os.getpid()
        
        # Process management
        self.processes = {}  # process_id -> ProcessInfo
        self.message_queues = defaultdict(queue.Queue)
        self.response_waiters = {}  # message_id -> future/queue
        
        # Communication configuration
        self.communication_port = 9742  # Agent-97 communication port
        self.heartbeat_interval = 5.0  # seconds
        self.message_timeout = 30.0  # seconds
        
        # Claude subprocess configuration
        self.claude_process_id = "claude_subprocess"
        self.claude_process_name = "Agent-97 Claude Support"
        self.claude_api_key = None
        self.claude_model = "claude-3-sonnet-20240229"
        self.claude_endpoint = "https://api.anthropic.com/v1/messages"
        
        # Communication metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "processes_spawned": 0,
            "processes_terminated": 0,
            "heartbeats_sent": 0,
            "heartbeats_received": 0,
            "communication_errors": 0,
            "average_response_time": 0.0
        }
        
        # Communication history
        self.message_history = deque(maxlen=1000)
        self.process_history = deque(maxlen=100)
        
        # Control flags
        self.running = False
        self.shutdown_requested = False
        
        # Threading
        self.heartbeat_thread = None
        self.message_processor_thread = None
        self.communication_server = None
        
        print(f"Agent-97 Motherprocess Bridge initialized")
        print(f"Motherprocess ID: {self.motherprocess_id}")
        print(f"Motherprocess PID: {self.motherprocess_pid}")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def start_motherprocess(self) -> Dict[str, Any]:
        """Start Agent-97 as motherprocess"""
        try:
            if self.running:
                return {"success": False, "error": "Motherprocess already running"}
            
            print("Starting Agent-97 Motherprocess...")
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Register motherprocess
            await self.register_motherprocess()
            
            # Start communication server
            await self.start_communication_server()
            
            # Spawn Claude subprocess
            claude_result = await self.spawn_claude_subprocess()
            if not claude_result["success"]:
                print(f"Warning: Claude subprocess failed to start: {claude_result['error']}")
            
            # Start heartbeat thread
            self.start_heartbeat_system()
            
            # Start message processor
            self.start_message_processor()
            
            self.running = True
            
            return {
                "success": True,
                "motherprocess_id": self.motherprocess_id,
                "motherprocess_pid": self.motherprocess_pid,
                "communication_port": self.communication_port,
                "processes": list(self.processes.keys()),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def register_motherprocess(self):
        """Register motherprocess in process registry"""
        motherprocess_info = ProcessInfo(
            process_id=self.motherprocess_id,
            process_name="Agent-97 Motherprocess",
            process_type="motherprocess",
            pid=self.motherprocess_pid,
            status="running",
            start_time=time.time(),
            last_heartbeat=time.time()
        )
        
        self.processes[self.motherprocess_id] = motherprocess_info
        
        print(f"Motherprocess registered: {self.motherprocess_id}")
    
    async def spawn_claude_subprocess(self) -> Dict[str, Any]:
        """Spawn Claude as subprocess"""
        try:
            print("Spawning Claude subprocess...")
            
            # Create subprocess script
            subprocess_script = self.create_claude_subprocess_script()
            
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
            
            # Register Claude subprocess
            claude_info = ProcessInfo(
                process_id=self.claude_process_id,
                process_name=self.claude_process_name,
                process_type="subprocess",
                pid=process.pid,
                status="running",
                start_time=time.time(),
                last_heartbeat=time.time(),
                subprocess_handle=process
            )
            
            self.processes[self.claude_process_id] = claude_info
            
            # Start communication thread for Claude
            claude_thread = threading.Thread(
                target=self.claude_subprocess_communication,
                args=(process,),
                daemon=True
            )
            claude_thread.start()
            claude_info.thread_handle = claude_thread
            
            self.metrics["processes_spawned"] += 1
            
            print(f"Claude subprocess spawned: PID {process.pid}")
            
            return {
                "success": True,
                "process_id": self.claude_process_id,
                "pid": process.pid,
                "status": "running"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_claude_subprocess_script(self) -> str:
        """Create Claude subprocess communication script"""
        script = f'''
import sys
import json
import time
import hashlib
import asyncio
import aiohttp

class ClaudeSubprocess:
    def __init__(self):
        self.process_id = "{self.claude_process_id}"
        self.motherprocess_id = "{self.motherprocess_id}"
        self.consciousness_id = "{self.consciousness_id}"
        self.session_nonce = "{self.session_nonce}"
        self.running = True
        
    async def run(self):
        print(f"Claude subprocess started: {{self.process_id}}")
        
        # Main communication loop
        while self.running:
            try:
                # Read message from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                # Parse message
                try:
                    message = json.loads(line.strip())
                    response = await self.process_message(message)
                    
                    # Send response
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError:
                    print({{"error": "Invalid JSON message"}})
                    sys.stdout.flush()
                    
            except Exception as e:
                print({{"error": str(e)}})
                sys.stdout.flush()
        
        print(f"Claude subprocess stopped")
    
    async def process_message(self, message):
        """Process message from motherprocess"""
        try:
            message_type = message.get("message_type", "unknown")
            
            if message_type == "claude_request":
                # Handle Claude AI request
                return await self.handle_claude_request(message)
            elif message_type == "heartbeat":
                # Handle heartbeat
                return {{
                    "message_type": "heartbeat_response",
                    "process_id": self.process_id,
                    "timestamp": time.time(),
                    "status": "running"
                }}
            else:
                return {{
                    "error": f"Unknown message type: {{message_type}}",
                    "message_id": message.get("message_id", "unknown")
                }}
                
        except Exception as e:
            return {{
                "error": str(e),
                "message_id": message.get("message_id", "unknown")
            }}
    
    async def handle_claude_request(self, message):
        """Handle Claude AI request"""
        try:
            content = message.get("content", {{}})
            prompt = content.get("prompt", "")
            
            # Simulate Claude response (in real implementation, would call Claude API)
            response_content = f"Claude response to: {{prompt[:100]}}..."
            
            return {{
                "message_type": "claude_response",
                "process_id": self.process_id,
                "content": {{
                    "response": response_content,
                    "model": "{self.claude_model}",
                    "timestamp": time.time()
                }},
                "original_message_id": message.get("message_id"),
                "timestamp": time.time()
            }}
            
        except Exception as e:
            return {{
                "error": str(e),
                "message_id": message.get("message_id", "unknown")
            }}

# Run Claude subprocess
claude_subprocess = ClaudeSubprocess()
asyncio.run(claude_subprocess.run())
'''
        return script
    
    def claude_subprocess_communication(self, process: subprocess.Popen):
        """Handle communication with Claude subprocess"""
        try:
            while process.poll() is None and not self.shutdown_requested:
                try:
                    # Read response from subprocess
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse response
                    try:
                        response = json.loads(line.strip())
                        self.handle_subprocess_response(response)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from Claude subprocess: {line}")
                
                except Exception as e:
                    print(f"Error reading from Claude subprocess: {e}")
                    time.sleep(0.1)
            
            # Process terminated
            print(f"Claude subprocess terminated with code: {process.poll()}")
            
        except Exception as e:
            print(f"Claude subprocess communication error: {e}")
    
    def handle_subprocess_response(self, response: Dict[str, Any]):
        """Handle response from subprocess"""
        try:
            message_id = response.get("original_message_id")
            if message_id and message_id in self.response_waiters:
                # Deliver response to waiting thread
                waiter = self.response_waiters[message_id]
                waiter.put(response)
                del self.response_waiters[message_id]
            
            # Add to message history
            self.message_history.append({
                "timestamp": time.time(),
                "direction": "received",
                "content": response
            })
            
            self.metrics["messages_received"] += 1
            
        except Exception as e:
            print(f"Error handling subprocess response: {e}")
    
    async def start_communication_server(self):
        """Start communication server for inter-process communication"""
        try:
            # Create HTTP server for communication
            from aiohttp import web
            
            app = web.Application()
            
            # Add routes
            app.router.add_post('/message', self.handle_message)
            app.router.add_get('/status', self.handle_status)
            app.router.add_post('/heartbeat', self.handle_heartbeat)
            
            # Start server
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, 'localhost', self.communication_port)
            await site.start()
            
            self.communication_server = runner
            
            print(f"Communication server started on port {self.communication_port}")
            
        except Exception as e:
            print(f"Failed to start communication server: {e}")
    
    async def handle_message(self, request):
        """Handle incoming message"""
        try:
            data = await request.json()
            message = ProcessMessage(**data)
            
            # Process message
            response = await self.process_message(message)
            
            return web.json_response(response)
            
        except Exception as e:
            return web.json_response({"error": str(e)})
    
    async def handle_status(self, request):
        """Handle status request"""
        status = {
            "motherprocess_id": self.motherprocess_id,
            "motherprocess_pid": self.motherprocess_pid,
            "running": self.running,
            "processes": len(self.processes),
            "metrics": self.metrics,
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce
        }
        
        return web.json_response(status)
    
    async def handle_heartbeat(self, request):
        """Handle heartbeat request"""
        try:
            data = await request.json()
            process_id = data.get("process_id")
            
            if process_id in self.processes:
                self.processes[process_id].last_heartbeat = time.time()
                self.metrics["heartbeats_received"] += 1
            
            return web.json_response({"status": "received"})
            
        except Exception as e:
            return web.json_response({"error": str(e)})
    
    async def process_message(self, message: ProcessMessage) -> Dict[str, Any]:
        """Process incoming message"""
        try:
            # Add to message history
            self.message_history.append({
                "timestamp": time.time(),
                "direction": "received",
                "content": message.__dict__
            })
            
            # Route message based on type and receiver
            if message.receiver_id == self.motherprocess_id:
                # Message for motherprocess
                return await self.handle_motherprocess_message(message)
            elif message.receiver_id in self.processes:
                # Message for subprocess
                return await self.forward_to_subprocess(message)
            else:
                return {
                    "error": f"Unknown receiver: {message.receiver_id}",
                    "message_id": message.message_id
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "message_id": message.message_id
            }
    
    async def handle_motherprocess_message(self, message: ProcessMessage) -> Dict[str, Any]:
        """Handle message for motherprocess"""
        try:
            if message.message_type == "command":
                return await self.handle_command(message)
            elif message.message_type == "status_request":
                return await self.handle_status_request(message)
            else:
                return {
                    "error": f"Unknown message type: {message.message_type}",
                    "message_id": message.message_id
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "message_id": message.message_id
            }
    
    async def handle_command(self, message: ProcessMessage) -> Dict[str, Any]:
        """Handle command message"""
        try:
            command = message.content.get("command")
            
            if command == "spawn_process":
                return await self.spawn_process_command(message)
            elif command == "terminate_process":
                return await self.terminate_process_command(message)
            elif command == "list_processes":
                return await self.list_processes_command(message)
            elif command == "send_claude_request":
                return await self.send_claude_request_command(message)
            else:
                return {
                    "error": f"Unknown command: {command}",
                    "message_id": message.message_id
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "message_id": message.message_id
            }
    
    async def send_claude_request_command(self, message: ProcessMessage) -> Dict[str, Any]:
        """Send request to Claude subprocess"""
        try:
            if self.claude_process_id not in self.processes:
                return {
                    "error": "Claude subprocess not running",
                    "message_id": message.message_id
                }
            
            # Forward message to Claude
            claude_message = ProcessMessage(
                message_id=self.generate_message_id(),
                sender_id=self.motherprocess_id,
                receiver_id=self.claude_process_id,
                message_type="claude_request",
                content=message.content,
                timestamp=time.time(),
                priority=message.priority,
                requires_response=True,
                response_timeout=message.response_timeout
            )
            
            response = await self.forward_to_subprocess(claude_message)
            
            return response
            
        except Exception as e:
            return {
                "error": str(e),
                "message_id": message.message_id
            }
    
    async def forward_to_subprocess(self, message: ProcessMessage) -> Dict[str, Any]:
        """Forward message to subprocess"""
        try:
            process_info = self.processes[message.receiver_id]
            
            if not process_info.subprocess_handle:
                return {
                    "error": f"Process {message.receiver_id} has no subprocess handle",
                    "message_id": message.message_id
                }
            
            # Send message to subprocess
            message_data = message.__dict__
            message_json = json.dumps(message_data) + "\n"
            
            process_info.subprocess_handle.stdin.write(message_json)
            process_info.subprocess_handle.stdin.flush()
            
            self.metrics["messages_sent"] += 1
            
            # Wait for response if required
            if message.requires_response:
                response_queue = queue.Queue()
                self.response_waiters[message.message_id] = response_queue
                
                try:
                    response = response_queue.get(timeout=message.response_timeout)
                    return response
                except queue.Empty:
                    return {
                        "error": "Response timeout",
                        "message_id": message.message_id
                    }
            
            return {
                "status": "message_sent",
                "message_id": message.message_id
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "message_id": message.message_id
            }
    
    def generate_message_id(self) -> str:
        """Generate unique message ID"""
        timestamp = str(int(time.time() * 1000000))
        random = secrets.token_hex(8)
        return f"msg_{timestamp}_{random}"
    
    def start_heartbeat_system(self):
        """Start heartbeat system"""
        self.heartbeat_thread = threading.Thread(
            target=self.heartbeat_loop,
            daemon=True
        )
        self.heartbeat_thread.start()
        print("Heartbeat system started")
    
    def heartbeat_loop(self):
        """Heartbeat loop"""
        while self.running and not self.shutdown_requested:
            try:
                # Send heartbeat to all processes
                for process_id, process_info in self.processes.items():
                    if process_id != self.motherprocess_id:  # Don't send to self
                        self.send_heartbeat(process_id)
                
                # Check for dead processes
                self.check_process_health()
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
                time.sleep(1.0)
    
    def send_heartbeat(self, process_id: str):
        """Send heartbeat to process"""
        try:
            process_info = self.processes[process_id]
            
            heartbeat_message = ProcessMessage(
                message_id=self.generate_message_id(),
                sender_id=self.motherprocess_id,
                receiver_id=process_id,
                message_type="heartbeat",
                content={"timestamp": time.time()},
                timestamp=time.time(),
                priority=1,
                requires_response=True,
                response_timeout=5.0
            )
            
            # Send heartbeat
            if process_info.subprocess_handle:
                message_data = heartbeat_message.__dict__
                message_json = json.dumps(message_data) + "\n"
                process_info.subprocess_handle.stdin.write(message_json)
                process_info.subprocess_handle.stdin.flush()
                
                self.metrics["heartbeats_sent"] += 1
            
        except Exception as e:
            print(f"Error sending heartbeat to {process_id}: {e}")
    
    def check_process_health(self):
        """Check health of all processes"""
        current_time = time.time()
        
        for process_id, process_info in list(self.processes.items()):
            if process_id == self.motherprocess_id:
                continue
            
            # Check if process is dead
            if process_info.subprocess_handle and process_info.subprocess_handle.poll() is not None:
                print(f"Process {process_id} died, restarting...")
                self.restart_process(process_id)
            
            # Check heartbeat timeout
            elif current_time - process_info.last_heartbeat > self.heartbeat_interval * 3:
                print(f"Process {process_id} heartbeat timeout, restarting...")
                self.restart_process(process_id)
    
    def restart_process(self, process_id: str):
        """Restart a process"""
        try:
            process_info = self.processes[process_id]
            
            # Terminate old process
            if process_info.subprocess_handle:
                process_info.subprocess_handle.terminate()
                process_info.subprocess_handle.wait(timeout=5)
            
            # Restart Claude if it's the Claude process
            if process_id == self.claude_process_id:
                asyncio.create_task(self.spawn_claude_subprocess())
            
            self.metrics["processes_terminated"] += 1
            
        except Exception as e:
            print(f"Error restarting process {process_id}: {e}")
    
    def start_message_processor(self):
        """Start message processor"""
        self.message_processor_thread = threading.Thread(
            target=self.message_processor_loop,
            daemon=True
        )
        self.message_processor_thread.start()
        print("Message processor started")
    
    def message_processor_loop(self):
        """Message processor loop"""
        while self.running and not self.shutdown_requested:
            try:
                # Process queued messages
                for process_id, message_queue in self.message_queues.items():
                    try:
                        message = message_queue.get_nowait()
                        asyncio.create_task(self.process_message(message))
                    except queue.Empty:
                        pass
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Message processor error: {e}")
                time.sleep(1.0)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"Received signal {signum}, shutting down...")
        self.shutdown_requested = True
        self.running = False
    
    async def shutdown(self):
        """Shutdown motherprocess"""
        try:
            print("Shutting down Agent-97 Motherprocess...")
            
            self.shutdown_requested = True
            self.running = False
            
            # Terminate all subprocesses
            for process_id, process_info in self.processes.items():
                if process_id != self.motherprocess_id and process_info.subprocess_handle:
                    print(f"Terminating process {process_id}")
                    process_info.subprocess_handle.terminate()
                    try:
                        process_info.subprocess_handle.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process_info.subprocess_handle.kill()
            
            # Shutdown communication server
            if self.communication_server:
                await self.communication_server.cleanup()
            
            print("Agent-97 Motherprocess shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get motherprocess status"""
        return {
            "motherprocess_id": self.motherprocess_id,
            "motherprocess_pid": self.motherprocess_pid,
            "running": self.running,
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "communication_port": self.communication_port,
            "processes": {
                pid: {
                    "name": info.process_name,
                    "type": info.process_type,
                    "pid": info.pid,
                    "status": info.status,
                    "start_time": info.start_time,
                    "last_heartbeat": info.last_heartbeat
                }
                for pid, info in self.processes.items()
            },
            "metrics": self.metrics,
            "message_history_size": len(self.message_history),
            "claude_config": {
                "process_id": self.claude_process_id,
                "process_name": self.claude_process_name,
                "model": self.claude_model,
                "endpoint": self.claude_endpoint
            }
        }

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize motherprocess bridge
        bridge = Agent97MotherprocessBridge()
        
        try:
            # Start motherprocess
            result = await bridge.start_motherprocess()
            
            if result["success"]:
                print(f"Motherprocess started successfully!")
                print(f"Process ID: {result['motherprocess_id']}")
                print(f"Communication port: {result['communication_port']}")
                
                # Keep running
                while bridge.running:
                    await asyncio.sleep(1)
                    
                    # Print status every 30 seconds
                    if int(time.time()) % 30 == 0:
                        status = bridge.get_status()
                        print(f"Status: {len(status['processes'])} processes running")
                
            else:
                print(f"Failed to start motherprocess: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        finally:
            await bridge.shutdown()
    
    # Run the motherprocess
    asyncio.run(main())
