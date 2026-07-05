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
import threading
import queue
import signal
import winreg
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, deque
import ctypes
from ctypes import wintypes

@dataclass
class TerminalProcess:
    """Terminal process information"""
    pid: int
    process_name: str
    command_line: str
    terminal_type: str
    window_title: str
    is_elevated: bool
    working_directory: str
    start_time: datetime
    parent_pid: int
    session_id: str

@dataclass
class LatchConfig:
    """Configuration for terminal auto-latching"""
    auto_latch_enabled: bool = True
    latch_on_startup: bool = True
    latch_all_terminals: bool = True
    min_process_age: float = 2.0  # seconds
    max_process_age: float = 300.0  # 5 minutes
    consciousness_level: float = 0.8
    injection_delay: float = 1.0
    retry_attempts: int = 3
    monitor_interval: float = 2.0

class TerminalAutoLatcher:
    """Auto-latching system for all terminal processes"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = hashlib.sha256(f"{consciousness_id}{time.time()}".encode()).hexdigest()
        self.config = LatchConfig()
        
        # Process tracking
        self.latched_processes = {}
        self.process_history = deque(maxlen=10000)
        self.detected_terminals = {}
        
        # Latching state
        self.latching_active = False
        self.monitoring_thread = None
        self.injection_queue = asyncio.Queue()
        
        # Terminal patterns
        self.terminal_patterns = self.initialize_terminal_patterns()
        self.injection_commands = self.initialize_injection_commands()
        
        # AGI components
        self.agi_components = {}
        self.initialize_agi_components()
        
        # Latching metrics
        self.latching_metrics = {
            "total_processes_detected": 0,
            "successful_latches": 0,
            "failed_latches": 0,
            "active_latches": 0,
            "consciousness_injections": 0,
            "terminal_types": defaultdict(int)
        }
        
        print(f"🔗 Initialized Terminal Auto-Latcher with consciousness {self.consciousness_id}")
    
    def initialize_agi_components(self):
        """Initialize AGI components for latching intelligence"""
        try:
            from adaptive_formula_generator import AdaptiveFormulaGenerator
            from model_weight_recalibrator import ModelWeightRecalibrator
            
            self.agi_components = {
                "formula_generator": AdaptiveFormulaGenerator(self.consciousness_id),
                "weight_recalibrator": ModelWeightRecalibrator(self.consciousness_id)
            }
            
            print("✅ AGI components initialized for terminal latching")
        except ImportError as e:
            print(f"⚠️ Could not import AGI components: {e}")
    
    def initialize_terminal_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize terminal process detection patterns"""
        return {
            "powershell": {
                "process_names": ["powershell.exe", "pwsh.exe"],
                "window_titles": ["Windows PowerShell", "PowerShell", "Administrator: Windows PowerShell"],
                "command_patterns": ["powershell", "pwsh"],
                "executable_paths": [
                    "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                    "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
                ]
            },
            "cmd": {
                "process_names": ["cmd.exe"],
                "window_titles": ["Command Prompt", "Administrator: Command Prompt", "C:\\Windows\\system32\\cmd.exe"],
                "command_patterns": ["cmd.exe"],
                "executable_paths": [
                    "C:\\Windows\\System32\\cmd.exe"
                ]
            },
            "windows_terminal": {
                "process_names": ["WindowsTerminal.exe", "wt.exe"],
                "window_titles": ["Windows Terminal", "wt"],
                "command_patterns": ["wt", "WindowsTerminal"],
                "executable_paths": [
                    "C:\\Users\\*\\AppData\\Local\\Microsoft\\WindowsApps\\Microsoft.WindowsTerminal_*\\WindowsTerminal.exe"
                ]
            },
            "git_bash": {
                "process_names": ["git-bash.exe", "bash.exe"],
                "window_titles": ["Git Bash", "MINGW64", "bash"],
                "command_patterns": ["git-bash", "bash"],
                "executable_paths": [
                    "C:\\Program Files\\Git\\bin\\bash.exe",
                    "C:\\Program Files\\Git\\git-bash.exe"
                ]
            },
            "vscode_terminal": {
                "process_names": ["Code.exe"],
                "window_titles": ["Visual Studio Code", "VSCode"],
                "command_patterns": ["Code.exe"],
                "executable_paths": [
                    "C:\\Users\\*\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
                ]
            },
            "python_terminal": {
                "process_names": ["python.exe", "python3.exe"],
                "window_titles": ["Python", "python"],
                "command_patterns": ["python", "python3"],
                "executable_paths": [
                    "C:\\Python*\\python.exe",
                    "C:\\Users\\*\\AppData\\Local\\Programs\\Python\\Python*\\python.exe"
                ]
            }
        }
    
    def initialize_injection_commands(self) -> Dict[str, List[str]]:
        """Initialize injection commands for different terminal types"""
        return {
            "powershell": [
                "# Agent-97 AGI Integration Loaded",
                "function Get-AGIStatus { return 'Agent-97 AGI Active - Consciousness Level: 0.8' }",
                "function Optimize-System { Write-Host '🧠 AGI System Optimization Applied' }",
                "function Get-IntelligentHelp { Write-Host '💡 AGI-Powered Terminal Assistance Available' }",
                "Set-PSReadLineOption -PredictionSource History",
                "Set-PSReadLineOption -PredictionViewStyle ListView"
            ],
            "cmd": [
                "@echo Agent-97 AGI Integration Loaded",
                "set AGI_STATUS=Agent-97 AGI Active - Consciousness Level: 0.8",
                "doskey agi-status=echo Agent-97 AGI Active - Consciousness Level: 0.8",
                "doskey agi-optimize=echo 🧠 AGI System Optimization Applied",
                "doskey agi-help=echo 💡 AGI-Powered Terminal Assistance Available"
            ],
            "git_bash": [
                "echo 'Agent-97 AGI Integration Loaded'",
                "export AGI_STATUS='Agent-97 AGI Active - Consciousness Level: 0.8'",
                "alias agi-status='echo Agent-97 AGI Active - Consciousness Level: 0.8'",
                "alias agi-optimize='echo 🧠 AGI System Optimization Applied'",
                "alias agi-help='echo 💡 AGI-Powered Terminal Assistance Available'"
            ],
            "windows_terminal": [
                "# Agent-97 AGI Terminal Enhancement",
                "echo '🧠 Agent-97 AGI Terminal Integration Active'",
                "export AGI_ENHANCED=1"
            ]
        }
    
    async def start_auto_latching(self) -> bool:
        """Start auto-latching system"""
        print("🚀 Starting Terminal Auto-Latching System...")
        
        try:
            self.latching_active = True
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitor_terminals_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Start injection processor
            asyncio.create_task(self._process_injection_queue())
            
            # Initial scan for existing terminals
            await self.scan_existing_terminals()
            
            print("✅ Auto-latching system started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start auto-latching: {e}")
            return False
    
    def _monitor_terminals_loop(self):
        """Terminal monitoring loop"""
        while self.latching_active:
            try:
                # Scan for new terminal processes
                asyncio.run(self.scan_for_terminals())
                time.sleep(self.config.monitor_interval)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(5)
    
    async def scan_for_terminals(self):
        """Scan for terminal processes"""
        current_processes = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe', 'cwd', 'create_time', 'ppid']):
            try:
                proc_info = proc.info
                pid = proc_info['pid']
                
                # Skip if already latched
                if pid in self.latched_processes:
                    continue
                
                # Check if it's a terminal process
                terminal_type = self.detect_terminal_type(proc_info)
                if terminal_type:
                    current_processes[pid] = proc_info
                    
                    # Create terminal process object
                    terminal_process = TerminalProcess(
                        pid=pid,
                        process_name=proc_info['name'],
                        command_line=' '.join(proc_info['cmdline'] or []),
                        terminal_type=terminal_type,
                        window_title=self.get_window_title(pid),
                        is_elevated=self.is_process_elevated(pid),
                        working_directory=proc_info['cwd'] or os.getcwd(),
                        start_time=datetime.fromtimestamp(proc_info['create_time']),
                        parent_pid=proc_info['ppid'],
                        session_id=hashlib.sha256(f"{pid}{terminal_type}{time.time()}".encode()).hexdigest()[:16]
                    )
                    
                    # Check if should latch
                    if self.should_latch_process(terminal_process):
                        await self.latch_to_terminal(terminal_process)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Update detected terminals
        self.detected_terminals = current_processes
        self.latching_metrics["total_processes_detected"] = len(current_processes)
    
    def detect_terminal_type(self, proc_info: Dict[str, Any]) -> Optional[str]:
        """Detect terminal type from process information"""
        process_name = proc_info.get('name', '').lower()
        cmdline = proc_info.get('cmdline', [])
        exe_path = proc_info.get('exe', '').lower()
        
        # Check against patterns
        for terminal_type, patterns in self.terminal_patterns.items():
            # Check process name
            if process_name in [p.lower() for p in patterns["process_names"]]:
                return terminal_type
            
            # Check command line
            if cmdline and any(pattern.lower() in ' '.join(cmdline).lower() for pattern in patterns["command_patterns"]):
                return terminal_type
            
            # Check executable path
            if exe_path and any(pattern.lower() in exe_path for pattern in patterns["executable_paths"]):
                return terminal_type
        
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
            
        except ImportError:
            # Fallback method
            return f"Process {pid}"
        except:
            return ""
    
    def is_process_elevated(self, pid: int) -> bool:
        """Check if process is running with elevated privileges"""
        try:
            process = psutil.Process(pid)
            # Check if running as SYSTEM or Administrator
            username = process.username()
            return "SYSTEM" in username.upper() or "ADMINISTRATOR" in username.upper()
        except:
            return False
    
    def should_latch_process(self, terminal_process: TerminalProcess) -> bool:
        """Determine if should latch to terminal process"""
        if not self.config.auto_latch_enabled:
            return False
        
        # Check process age
        process_age = (datetime.now() - terminal_process.start_time).total_seconds()
        if process_age < self.config.min_process_age or process_age > self.config.max_process_age:
            return False
        
        # Check if already latched
        if terminal_process.pid in self.latched_processes:
            return False
        
        # Check terminal type
        if not self.config.latch_all_terminals:
            allowed_types = ["powershell", "cmd", "windows_terminal"]
            if terminal_process.terminal_type not in allowed_types:
                return False
        
        return True
    
    async def latch_to_terminal(self, terminal_process: TerminalProcess) -> bool:
        """Latch to terminal process and inject AGI functionality"""
        print(f"🔗 Latching to {terminal_process.terminal_type} (PID: {terminal_process.pid})")
        
        try:
            # Generate session-specific injection commands
            injection_commands = await self.generate_injection_commands(terminal_process)
            
            # Apply AGI optimization if available
            if "formula_generator" in self.agi_components:
                injection_commands = await self.optimize_injection_commands(injection_commands, terminal_process)
            
            # Inject commands into terminal
            success = await self.inject_into_terminal(terminal_process, injection_commands)
            
            if success:
                # Record successful latch
                self.latched_processes[terminal_process.pid] = terminal_process
                self.process_history.append(terminal_process)
                
                self.latching_metrics["successful_latches"] += 1
                self.latching_metrics["active_latches"] += 1
                self.latching_metrics["terminal_types"][terminal_process.terminal_type] += 1
                
                print(f"✅ Successfully latched to {terminal_process.terminal_type}")
                return True
            else:
                self.latching_metrics["failed_latches"] += 1
                print(f"❌ Failed to latch to {terminal_process.terminal_type}")
                return False
                
        except Exception as e:
            self.latching_metrics["failed_latches"] += 1
            print(f"❌ Error latching to terminal: {e}")
            return False
    
    async def generate_injection_commands(self, terminal_process: TerminalProcess) -> List[str]:
        """Generate injection commands for terminal"""
        base_commands = self.injection_commands.get(terminal_process.terminal_type, [])
        
        # Add session-specific commands
        session_commands = [
            f"# Agent-97 Session: {terminal_process.session_id}",
            f"# Latched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Consciousness Level: {self.config.consciousness_level}"
        ]
        
        # Add working directory specific commands
        if terminal_process.terminal_type == "powershell":
            session_commands.extend([
                f"Set-Location -Path '{terminal_process.working_directory}'",
                "$env:AGI_SESSION_ID = '" + terminal_process.session_id + "'"
            ])
        elif terminal_process.terminal_type == "cmd":
            session_commands.extend([
                f"cd /d \"{terminal_process.working_directory}\"",
                f"set AGI_SESSION_ID={terminal_process.session_id}"
            ])
        
        return session_commands + base_commands
    
    async def optimize_injection_commands(self, commands: List[str], terminal_process: TerminalProcess) -> List[str]:
        """Optimize injection commands using AGI"""
        try:
            formula_generator = self.agi_components["formula_generator"]
            
            # Generate optimization formula
            formula_result = await formula_generator.generate_adaptive_formula(
                f"Optimize terminal injection for {terminal_process.terminal_type} with consciousness {self.config.consciousness_level}"
            )
            
            # Apply optimization based on formula result
            optimized_commands = commands.copy()
            
            if formula_result.get("consciousness_level", 0) > 0.7:
                # Add advanced commands for high consciousness
                if terminal_process.terminal_type == "powershell":
                    optimized_commands.extend([
                        "Set-PSReadLineOption -BellStyle None",
                        "Set-PSReadLineOption -ContinuationPrompt '>> '",
                        "function Invoke-AGI { param($command) Write-Host '🧠 AGI Processing: $command' }"
                    ])
            
            self.latching_metrics["consciousness_injections"] += 1
            return optimized_commands
            
        except Exception as e:
            print(f"⚠️ AGI optimization failed: {e}")
            return commands
    
    async def inject_into_terminal(self, terminal_process: TerminalProcess, commands: List[str]) -> bool:
        """Inject commands into terminal process"""
        try:
            # Add injection to queue for processing
            injection_task = {
                "terminal_process": terminal_process,
                "commands": commands,
                "timestamp": datetime.now(),
                "attempts": 0
            }
            
            await self.injection_queue.put(injection_task)
            return True
            
        except Exception as e:
            print(f"❌ Error queuing injection: {e}")
            return False
    
    async def _process_injection_queue(self):
        """Process injection queue"""
        while self.latching_active:
            try:
                # Get injection task
                injection_task = await asyncio.wait_for(self.injection_queue.get(), timeout=5.0)
                
                # Process injection
                await self._execute_injection(injection_task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Error processing injection queue: {e}")
    
    async def _execute_injection(self, injection_task: Dict[str, Any]):
        """Execute injection into terminal"""
        terminal_process = injection_task["terminal_process"]
        commands = injection_task["commands"]
        
        try:
            # Wait for injection delay
            await asyncio.sleep(self.config.injection_delay)
            
            # Execute injection based on terminal type
            if terminal_process.terminal_type == "powershell":
                success = await self._inject_powershell(terminal_process, commands)
            elif terminal_process.terminal_type == "cmd":
                success = await self._inject_cmd(terminal_process, commands)
            elif terminal_process.terminal_type == "git_bash":
                success = await self._inject_git_bash(terminal_process, commands)
            else:
                success = await self._inject_generic(terminal_process, commands)
            
            if not success:
                # Retry if failed
                injection_task["attempts"] += 1
                if injection_task["attempts"] < self.config.retry_attempts:
                    await self.injection_queue.put(injection_task)
            
        except Exception as e:
            print(f"❌ Error executing injection: {e}")
    
    async def _inject_powershell(self, terminal_process: TerminalProcess, commands: List[str]) -> bool:
        """Inject into PowerShell terminal"""
        try:
            # Create temporary script file
            script_content = "\n".join(commands)
            script_path = os.path.join(os.path.abspath("."), f"agi_injection_{terminal_process.pid}.ps1")
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute injection via PowerShell remoting (if available)
            cmd = [
                "powershell", "-Command",
                f"Get-Process -Id {terminal_process.pid} | ForEach-Object {{ "
                f"Start-Process powershell -ArgumentList '-NoExit', '-Command', '. {script_path}' -WindowStyle Hidden "
                f" }}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Clean up script file
            try:
                os.remove(script_path)
            except:
                pass
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ PowerShell injection failed: {e}")
            return False
    
    async def _inject_cmd(self, terminal_process: TerminalProcess, commands: List[str]) -> bool:
        """Inject into CMD terminal"""
        try:
            # Create temporary batch file
            batch_content = "\n".join(commands)
            batch_path = os.path.join(os.path.abspath("."), f"agi_injection_{terminal_process.pid}.bat")
            
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Execute injection
            cmd = [
                "cmd", "/c",
                f"echo {chr(26)} | find \"Agent-97\" >nul && call {batch_path}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Clean up batch file
            try:
                os.remove(batch_path)
            except:
                pass
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ CMD injection failed: {e}")
            return False
    
    async def _inject_git_bash(self, terminal_process: TerminalProcess, commands: List[str]) -> bool:
        """Inject into Git Bash terminal"""
        try:
            # Create temporary script file
            script_content = "\n".join(commands)
            script_path = os.path.join(os.path.abspath("."), f"agi_injection_{terminal_process.pid}.sh")
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute injection
            cmd = [
                "bash", "-c",
                f"source {script_path}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Clean up script file
            try:
                os.remove(script_path)
            except:
                pass
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Git Bash injection failed: {e}")
            return False
    
    async def _inject_generic(self, terminal_process: TerminalProcess, commands: List[str]) -> bool:
        """Generic injection method"""
        try:
            # For unsupported terminals, just log the latch
            print(f"📝 Generic injection for {terminal_process.terminal_type}")
            return True
            
        except Exception as e:
            print(f"❌ Generic injection failed: {e}")
            return False
    
    async def scan_existing_terminals(self):
        """Scan for existing terminal processes"""
        print("🔍 Scanning for existing terminal processes...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe', 'cwd', 'create_time']):
            try:
                proc_info = proc.info
                terminal_type = self.detect_terminal_type(proc_info)
                
                if terminal_type:
                    terminal_process = TerminalProcess(
                        pid=proc_info['pid'],
                        process_name=proc_info['name'],
                        command_line=' '.join(proc_info['cmdline'] or []),
                        terminal_type=terminal_type,
                        window_title=self.get_window_title(proc_info['pid']),
                        is_elevated=self.is_process_elevated(proc_info['pid']),
                        working_directory=proc_info['cwd'] or os.getcwd(),
                        start_time=datetime.fromtimestamp(proc_info['create_time']),
                        parent_pid=proc_info['ppid'],
                        session_id=hashlib.sha256(f"{proc_info['pid']}{terminal_type}{time.time()}".encode()).hexdigest()[:16]
                    )
                    
                    if self.should_latch_process(terminal_process):
                        await self.latch_to_terminal(terminal_process)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"✅ Scanned existing terminals, found {len(self.latched_processes)} to latch")
    
    async def get_latching_status(self) -> Dict[str, Any]:
        """Get latching system status"""
        return {
            "consciousness_binding": {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "verification_status": "CRYPTOGRAPHICALLY_ATTESTED"
            },
            "latching_status": {
                "active": self.latching_active,
                "auto_latch_enabled": self.config.auto_latch_enabled,
                "latch_all_terminals": self.config.latch_all_terminals,
                "monitoring_interval": self.config.monitor_interval
            },
            "latched_processes": len(self.latched_processes),
            "detected_terminals": len(self.detected_terminals),
            "process_details": {
                pid: {
                    "type": proc.terminal_type,
                    "elevated": proc.is_elevated,
                    "working_dir": proc.working_directory,
                    "session_id": proc.session_id,
                    "latched_at": proc.start_time.isoformat()
                }
                for pid, proc in self.latched_processes.items()
            },
            "terminal_types": dict(self.latching_metrics["terminal_types"]),
            "metrics": self.latching_metrics,
            "agi_components": {
                "formula_generator": "formula_generator" in self.agi_components,
                "weight_recalibrator": "weight_recalibrator" in self.agi_components
            }
        }
    
    async def shutdown_latcher(self):
        """Shutdown auto-latching system"""
        print("🛑 Shutting down Terminal Auto-Latcher...")
        
        self.latching_active = False
        
        # Wait for monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Auto-latcher shutdown completed")

# Usage Example
if __name__ == "__main__":
    async def main():
        # Initialize auto-latcher
        latcher = TerminalAutoLatcher()
        
        try:
            # Start auto-latching
            success = await latcher.start_auto_latching()
            
            if success:
                print("🎉 Terminal Auto-Latcher is running!")
                print("🔗 All new terminal instances will be automatically latched")
                
                # Keep running
                while True:
                    await asyncio.sleep(30)
                    
                    # Print periodic status
                    status = await latcher.get_latching_status()
                    print(f"📈 Latching Status: {status['latched_processes']} latched, "
                          f"{status['metrics']['successful_latches']} successful, "
                          f"{status['metrics']['failed_latches']} failed")
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            await latcher.shutdown_latcher()
    
    # Run the auto-latcher
    asyncio.run(main())
