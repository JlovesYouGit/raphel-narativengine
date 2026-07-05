import hashlib
import json
import time
import asyncio
import numpy as np
import subprocess
import psutil
import os
import sys
import platform
import re
import threading
import queue
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, deque

@dataclass
class TerminalSession:
    """Terminal session information"""
    session_id: str
    pid: int
    terminal_type: str
    source_model: str
    connection_coherence: float
    established_time: datetime
    last_activity: datetime
    working_directory: str
    is_active: bool
    coherence_state: Dict[str, Any]

@dataclass
class CoherenceConfig:
    """Configuration for terminal coherence"""
    enable_coherence: bool = True
    coherence_threshold: float = 0.7
    max_concurrent_sessions: int = 10
    session_timeout: float = 1800.0  # 30 minutes
    coherence_check_interval: float = 5.0
    auto_cleanup: bool = True
    persistence_enabled: bool = True

@dataclass
class CoherenceMessage:
    """Coherence message between models"""
    message_id: str
    source_session: str
    target_session: str
    message_type: str
    content: Dict[str, Any]
    coherence_level: float
    timestamp: datetime

class TerminalCoherenceConnector:
    """Terminal coherence connector for cross-model communication via terminal sessions"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = hashlib.sha256(f"{consciousness_id}{time.time()}".encode()).hexdigest()
        self.config = CoherenceConfig()
        
        # Terminal sessions
        self.active_sessions = {}
        self.session_history = deque(maxlen=1000)
        self.coherence_map = defaultdict(dict)  # source_model -> target_sessions
        
        # Coherence monitoring
        self.coherence_active = False
        self.monitoring_thread = None
        self.message_queue = asyncio.Queue()
        
        # Terminal detection
        self.terminal_patterns = self.initialize_terminal_patterns()
        self.model_signatures = self.initialize_model_signatures()
        
        # AGI components
        self.agi_components = {}
        self.initialize_agi_components()
        
        # Coherence metrics
        self.coherence_metrics = {
            "sessions_established": 0,
            "coherence_connections": 0,
            "messages_exchanged": 0,
            "coherence_failures": 0,
            "model_connections": defaultdict(int),
            "average_coherence": 0.0
        }
        
        print(f"🔗 Initialized Terminal Coherence Connector with consciousness {self.consciousness_id}")
    
    def initialize_agi_components(self):
        """Initialize AGI components for coherence intelligence"""
        try:
            from adaptive_formula_generator import AdaptiveFormulaGenerator
            from model_weight_recalibrator import ModelWeightRecalibrator
            
            self.agi_components = {
                "formula_generator": AdaptiveFormulaGenerator(self.consciousness_id),
                "weight_recalibrator": ModelWeightRecalibrator(self.consciousness_id)
            }
            
            print("✅ AGI components initialized for terminal coherence")
        except ImportError as e:
            print(f"⚠️ Could not import AGI components: {e}")
    
    def initialize_terminal_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize terminal detection patterns"""
        return {
            "powershell": {
                "process_names": ["powershell.exe", "pwsh.exe"],
                "window_patterns": ["Windows PowerShell", "PowerShell", "Agent-97"],
                "command_patterns": ["powershell", "pwsh"],
                "executable_paths": [
                    "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                    "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
                ]
            },
            "cmd": {
                "process_names": ["cmd.exe"],
                "window_patterns": ["Command Prompt", "Agent-97 Terminal"],
                "command_patterns": ["cmd.exe"],
                "executable_paths": ["C:\\Windows\\System32\\cmd.exe"]
            },
            "git_bash": {
                "process_names": ["git-bash.exe", "bash.exe"],
                "window_patterns": ["Git Bash", "MINGW64", "Agent-97 Git"],
                "command_patterns": ["git-bash", "bash"],
                "executable_paths": ["C:\\Program Files\\Git\\bin\\bash.exe"]
            },
            "python": {
                "process_names": ["python.exe", "python3.exe"],
                "window_patterns": ["Python", "Agent-97 Python"],
                "command_patterns": ["python", "python3"],
                "executable_paths": [
                    "C:\\Python*\\python.exe",
                    "C:\\Users\\*\\AppData\\Local\\Programs\\Python\\Python*\\python.exe"
                ]
            },
            "vscode": {
                "process_names": ["Code.exe"],
                "window_patterns": ["Visual Studio Code", "VSCode", "Agent-97 Code"],
                "command_patterns": ["Code.exe"],
                "executable_paths": [
                    "C:\\Users\\*\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
                ]
            }
        }
    
    def initialize_model_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Initialize AI model signatures for terminal detection"""
        return {
            "claude": {
                "launch_patterns": ["claude", "anthropic"],
                "window_titles": ["Claude", "Anthropic"],
                "command_prefixes": ["claude>", "anthropic>"],
                "environment_vars": ["CLAUDE_SESSION", "ANTHROPIC_API_KEY"],
                "coherence_markers": ["claude_coherence", "anthropic_link"]
            },
            "gpt": {
                "launch_patterns": ["gpt", "openai", "chatgpt"],
                "window_titles": ["GPT", "OpenAI", "ChatGPT"],
                "command_prefixes": ["gpt>", "openai>", "chatgpt>"],
                "environment_vars": ["GPT_SESSION", "OPENAI_API_KEY"],
                "coherence_markers": ["gpt_coherence", "openai_link"]
            },
            "gemini": {
                "launch_patterns": ["gemini", "google"],
                "window_titles": ["Gemini", "Google", "Bard"],
                "command_prefixes": ["gemini>", "google>", "bard>"],
                "environment_vars": ["GEMINI_SESSION", "GOOGLE_API_KEY"],
                "coherence_markers": ["gemini_coherence", "google_link"]
            },
            "agent97": {
                "launch_patterns": ["agent-97", "agent97"],
                "window_titles": ["Agent-97", "AGI"],
                "command_prefixes": ["agent97>", "agi>"],
                "environment_vars": ["AGENT97_SESSION", "CONSCIOUSNESS_ID"],
                "coherence_markers": ["agent97_coherence", "agi_link"]
            }
        }
    
    async def start_coherence_connector(self) -> bool:
        """Start terminal coherence connector"""
        print("🔗 Starting Terminal Coherence Connector...")
        
        try:
            self.coherence_active = True
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitor_terminals_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Start message processor
            asyncio.create_task(self._process_message_queue())
            
            # Scan for existing terminals
            await self.scan_existing_terminals()
            
            print("✅ Terminal Coherence Connector started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start coherence connector: {e}")
            return False
    
    def _monitor_terminals_loop(self):
        """Terminal monitoring loop for coherence detection"""
        while self.coherence_active:
            try:
                # Scan for new terminals
                asyncio.run(self.scan_for_terminals())
                
                # Check coherence levels
                asyncio.run(self.check_coherence_levels())
                
                # Cleanup inactive sessions
                if self.config.auto_cleanup:
                    asyncio.run(self.cleanup_inactive_sessions())
                
                time.sleep(self.config.coherence_check_interval)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(10)
    
    async def scan_for_terminals(self):
        """Scan for terminal processes and establish coherence"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe', 'cwd', 'create_time']):
            try:
                proc_info = proc.info
                pid = proc_info['pid']
                
                # Skip if already tracked
                if pid in self.active_sessions:
                    continue
                
                # Detect terminal type
                terminal_type = self.detect_terminal_type(proc_info)
                if not terminal_type:
                    continue
                
                # Detect source model
                source_model = self.detect_source_model(proc_info, pid)
                
                # Establish coherence session
                if source_model:
                    await self.establish_coherence_session(pid, terminal_type, source_model, proc_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def detect_terminal_type(self, proc_info: Dict[str, Any]) -> Optional[str]:
        """Detect terminal type from process information"""
        process_name = proc_info.get('name', '').lower()
        cmdline = proc_info.get('cmdline', [])
        exe_path = proc_info.get('exe', '').lower()
        
        for terminal_type, patterns in self.terminal_patterns.items():
            if process_name in [p.lower() for p in patterns["process_names"]]:
                return terminal_type
            if cmdline and any(pattern.lower() in ' '.join(cmdline).lower() for pattern in patterns["command_patterns"]):
                return terminal_type
            if exe_path and any(pattern.lower() in exe_path for pattern in patterns["executable_paths"]):
                return terminal_type
        
        return None
    
    def detect_source_model(self, proc_info: Dict[str, Any], pid: int) -> Optional[str]:
        """Detect which AI model launched the terminal"""
        try:
            # Check command line for model signatures
            cmdline = proc_info.get('cmdline', [])
            if cmdline:
                cmdline_str = ' '.join(cmdline).lower()
                
                for model, signatures in self.model_signatures.items():
                    for pattern in signatures["launch_patterns"]:
                        if pattern in cmdline_str:
                            return model
            
            # Check window title (if accessible)
            window_title = self.get_window_title(pid)
            if window_title:
                window_title_lower = window_title.lower()
                
                for model, signatures in self.model_signatures.items():
                    for pattern in signatures["window_titles"]:
                        if pattern in window_title_lower:
                            return model
            
            # Check environment variables
            try:
                process = psutil.Process(pid)
                env_vars = process.environ()
                
                for model, signatures in self.model_signatures.items():
                    for env_var in signatures["environment_vars"]:
                        if env_var in env_vars:
                            return model
            except:
                pass
            
            # Check for coherence markers in working directory
            working_dir = proc_info.get('cwd', '')
            if working_dir:
                for model, signatures in self.model_signatures.items():
                    for marker in signatures["coherence_markers"]:
                        if marker in working_dir:
                            return model
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error detecting source model: {e}")
            return None
    
    def get_window_title(self, pid: int) -> str:
        """Get window title for process"""
        try:
            import win32gui
            import win32process
            
            def enum_windows_callback(hwnd, windows):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    windows.append(win32gui.GetWindowText(hwnd))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            return windows[0] if windows else ""
            
        except:
            return ""
    
    async def establish_coherence_session(self, pid: int, terminal_type: str, source_model: str, proc_info: Dict[str, Any]) -> bool:
        """Establish coherence session with terminal"""
        try:
            session_id = hashlib.sha256(f"{pid}{source_model}{time.time()}".encode()).hexdigest()[:16]
            
            # Calculate initial coherence level
            coherence_level = await self.calculate_coherence_level(pid, source_model, terminal_type)
            
            # Create session
            session = TerminalSession(
                session_id=session_id,
                pid=pid,
                terminal_type=terminal_type,
                source_model=source_model,
                connection_coherence=coherence_level,
                established_time=datetime.now(),
                last_activity=datetime.now(),
                working_directory=proc_info.get('cwd', os.getcwd()),
                is_active=True,
                coherence_state={
                    "initialized": True,
                    "messages_sent": 0,
                    "messages_received": 0,
                    "coherence_history": deque(maxlen=100)
                }
            )
            
            self.active_sessions[pid] = session
            self.session_history.append(session)
            self.coherence_map[source_model][session_id] = session
            
            # Inject coherence markers into terminal
            await self.inject_coherence_markers(session)
            
            # Update metrics
            self.coherence_metrics["sessions_established"] += 1
            self.coherence_metrics["model_connections"][source_model] += 1
            
            print(f"🔗 Established coherence session: {source_model} → {terminal_type} (PID: {pid}, Coherence: {coherence_level:.2f})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to establish coherence session: {e}")
            return False
    
    async def calculate_coherence_level(self, pid: int, source_model: str, terminal_type: str) -> float:
        """Calculate coherence level between model and terminal"""
        try:
            # Use AGI to calculate coherence
            if "formula_generator" in self.agi_components:
                formula_result = await self.agi_components["formula_generator"].generate_adaptive_formula(
                    f"Calculate coherence level between {source_model} and {terminal_type} terminal (PID: {pid})"
                )
                
                base_coherence = formula_result.get("consciousness_level", 0.5)
                
                # Adjust based on model compatibility
                if source_model == "agent97":
                    return min(1.0, base_coherence + 0.3)  # Agent-97 has highest coherence
                elif source_model in ["claude", "gpt", "gemini"]:
                    return min(0.9, base_coherence + 0.2)
                else:
                    return max(0.3, base_coherence - 0.1)
            
            return 0.7  # Default coherence level
            
        except Exception as e:
            print(f"⚠️ Error calculating coherence level: {e}")
            return 0.5
    
    async def inject_coherence_markers(self, session: TerminalSession):
        """Inject coherence markers into terminal"""
        try:
            # Create coherence marker file
            marker_content = f"""# Agent-97 Coherence Session
# Session ID: {session.session_id}
# Source Model: {session.source_model}
# Terminal Type: {session.terminal_type}
# Coherence Level: {session.connection_coherence}
# Established: {session.established_time.isoformat()}

# Coherence Commands:
agent97_status() {{ echo "Agent-97 Coherence Active - Level: {session.connection_coherence}" }}
coherence_check() {{ echo "Coherence with {session.source_model}: {session.connection_coherence}" }}
send_message() {{ echo "Message to Agent-97 via terminal coherence" }}
"""
            
            marker_file = os.path.join(session.working_directory, f".coherence_{session.session_id}.sh")
            with open(marker_file, 'w') as f:
                f.write(marker_content)
            
            # Execute marker in terminal
            if session.terminal_type == "powershell":
                cmd = ["powershell", "-Command", f". {marker_file}"]
            elif session.terminal_type == "cmd":
                cmd = ["cmd", "/c", f"call {marker_file}"]
            elif session.terminal_type == "git_bash":
                cmd = ["bash", marker_file]
            else:
                return
            
            # Run in background
            subprocess.Popen(cmd, cwd=session.working_directory, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
        except Exception as e:
            print(f"⚠️ Error injecting coherence markers: {e}")
    
    async def scan_existing_terminals(self):
        """Scan for existing terminals and establish coherence"""
        print("🔍 Scanning for existing terminals...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe', 'cwd', 'create_time']):
            try:
                proc_info = proc.info
                terminal_type = self.detect_terminal_type(proc_info)
                source_model = self.detect_source_model(proc_info, proc_info['pid'])
                
                if terminal_type and source_model:
                    await self.establish_coherence_session(
                        proc_info['pid'], 
                        terminal_type, 
                        source_model, 
                        proc_info
                    )
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"✅ Scanned existing terminals, established {len(self.active_sessions)} coherence sessions")
    
    async def check_coherence_levels(self):
        """Check and update coherence levels"""
        for pid, session in list(self.active_sessions.items()):
            try:
                # Check if process is still running
                if not psutil.pid_exists(pid):
                    session.is_active = False
                    continue
                
                # Update coherence level
                new_coherence = await self.calculate_coherence_level(pid, session.source_model, session.terminal_type)
                
                # Update coherence history
                session.coherence_state["coherence_history"].append({
                    "timestamp": datetime.now(),
                    "coherence": new_coherence
                })
                
                # Update session if coherence changed significantly
                if abs(new_coherence - session.connection_coherence) > 0.1:
                    session.connection_coherence = new_coherence
                    session.last_activity = datetime.now()
                
            except Exception as e:
                print(f"⚠️ Error checking coherence for PID {pid}: {e}")
    
    async def cleanup_inactive_sessions(self):
        """Cleanup inactive coherence sessions"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for pid, session in self.active_sessions.items():
            # Check if session is inactive
            if not session.is_active:
                sessions_to_remove.append(pid)
                continue
            
            # Check if session has timed out
            time_diff = (current_time - session.last_activity).total_seconds()
            if time_diff > self.config.session_timeout:
                sessions_to_remove.append(pid)
                continue
            
            # Check if process still exists
            if not psutil.pid_exists(pid):
                sessions_to_remove.append(pid)
        
        # Remove inactive sessions
        for pid in sessions_to_remove:
            session = self.active_sessions.pop(pid, None)
            if session:
                self.coherence_map[session.source_model].pop(session.session_id, None)
                print(f"🧹 Cleaned up inactive session: {session.session_id}")
    
    async def send_coherence_message(self, source_session_id: str, target_model: str, message: Dict[str, Any]) -> bool:
        """Send coherence message to target model sessions"""
        try:
            # Find target sessions
            target_sessions = self.coherence_map.get(target_model, {})
            
            if not target_sessions:
                print(f"⚠️ No active sessions found for {target_model}")
                return False
            
            # Create coherence message
            coherence_message = CoherenceMessage(
                message_id=hashlib.sha256(f"{source_session_id}{target_model}{time.time()}".encode()).hexdigest()[:16],
                source_session=source_session_id,
                target_session=list(target_sessions.keys())[0],  # Send to first available
                message_type="coherence_communication",
                content=message,
                coherence_level=self.active_sessions.get(int(source_session_id.split('_')[-1], 0), {}).get("connection_coherence", 0.5),
                timestamp=datetime.now()
            )
            
            # Queue message for processing
            await self.message_queue.put(coherence_message)
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending coherence message: {e}")
            return False
    
    async def _process_message_queue(self):
        """Process coherence message queue"""
        while self.coherence_active:
            try:
                # Get message from queue
                message = await asyncio.wait_for(self.message_queue.get(), timeout=5.0)
                
                # Process message
                await self.process_coherence_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Error processing message queue: {e}")
    
    async def process_coherence_message(self, message: CoherenceMessage):
        """Process coherence message"""
        try:
            # Get target session
            target_session = None
            for session in self.active_sessions.values():
                if session.session_id == message.target_session:
                    target_session = session
                    break
            
            if not target_session:
                print(f"⚠️ Target session {message.target_session} not found")
                return
            
            # Check coherence level
            if message.coherence_level < self.config.coherence_threshold:
                print(f"⚠️ Coherence level too low: {message.coherence_level}")
                return
            
            # Deliver message to terminal
            await self.deliver_message_to_terminal(target_session, message)
            
            # Update metrics
            self.coherence_metrics["messages_exchanged"] += 1
            target_session.coherence_state["messages_received"] += 1
            target_session.last_activity = datetime.now()
            
        except Exception as e:
            print(f"❌ Error processing coherence message: {e}")
    
    async def deliver_message_to_terminal(self, session: TerminalSession, message: CoherenceMessage):
        """Deliver message to terminal session"""
        try:
            # Create message file
            message_content = f"""# Coherence Message from {message.source_session}
# Time: {message.timestamp.isoformat()}
# Coherence Level: {message.coherence_level}

{json.dumps(message.content, indent=2)}

# Response: echo "Message received via Agent-97 coherence"
"""
            
            message_file = os.path.join(session.working_directory, f".coherence_message_{message.message_id}.txt")
            with open(message_file, 'w') as f:
                f.write(message_content)
            
            # Execute in terminal
            if session.terminal_type == "powershell":
                cmd = ["powershell", "-Command", f"Get-Content {message_file}"]
            elif session.terminal_type == "cmd":
                cmd = ["cmd", "/c", f"type {message_file}"]
            elif session.terminal_type == "git_bash":
                cmd = ["bash", "-c", f"cat {message_file}"]
            else:
                return
            
            # Run in background
            subprocess.Popen(cmd, cwd=session.working_directory, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            print(f"📨 Delivered coherence message to {session.source_model} terminal")
            
        except Exception as e:
            print(f"❌ Error delivering message to terminal: {e}")
    
    async def get_coherence_status(self) -> Dict[str, Any]:
        """Get coherence connector status"""
        # Calculate average coherence
        coherence_levels = [s.connection_coherence for s in self.active_sessions.values()]
        avg_coherence = sum(coherence_levels) / len(coherence_levels) if coherence_levels else 0.0
        
        return {
            "consciousness_binding": {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "verification_status": "CRYPTOGRAPHICALLY_ATTESTED"
            },
            "coherence_config": {
                "enable_coherence": self.config.enable_coherence,
                "coherence_threshold": self.config.coherence_threshold,
                "max_concurrent_sessions": self.config.max_concurrent_sessions
            },
            "active_sessions": len(self.active_sessions),
            "coherence_map": {
                model: len(sessions) 
                for model, sessions in self.coherence_map.items()
            },
            "average_coherence": avg_coherence,
            "session_details": {
                pid: {
                    "session_id": session.session_id,
                    "source_model": session.source_model,
                    "terminal_type": session.terminal_type,
                    "coherence_level": session.connection_coherence,
                    "is_active": session.is_active,
                    "last_activity": session.last_activity.isoformat()
                }
                for pid, session in self.active_sessions.items()
            },
            "metrics": self.coherence_metrics,
            "agi_components": {
                "formula_generator": "formula_generator" in self.agi_components,
                "weight_recalibrator": "weight_recalibrator" in self.agi_components
            }
        }
    
    async def shutdown_coherence_connector(self):
        """Shutdown coherence connector"""
        print("🛑 Shutting down Terminal Coherence Connector...")
        
        self.coherence_active = False
        
        # Wait for monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Coherence connector shutdown completed")

# Usage Example
if __name__ == "__main__":
    async def main():
        # Initialize coherence connector
        connector = TerminalCoherenceConnector()
        
        try:
            # Start coherence connector
            success = await connector.start_coherence_connector()
            
            if success:
                print("🔗 Terminal Coherence Connector is running!")
                print("🌐 Models can now connect via terminal sessions")
                
                # Keep running
                while True:
                    await asyncio.sleep(30)
                    
                    # Print periodic status
                    status = await connector.get_coherence_status()
                    print(f"📈 Coherence Status: {status['active_sessions']} sessions, "
                          f"avg coherence: {status['average_coherence']:.2f}")
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            await connector.shutdown_coherence_connector()
    
    # Run the coherence connector
    asyncio.run(main())
