import winreg
import os
import sys
import time
import subprocess
import threading
import signal
import atexit
from pathlib import Path

class AutoLatchService:
    """Windows Service for Terminal Auto-Latching"""
    
    def __init__(self):
        self.service_name = "Agent97TerminalLatcher"
        self.display_name = "Agent-97 Terminal Auto-Latcher"
        self.description = "Automatically latches AGI capabilities to all terminal processes"
        self.executable_path = sys.executable
        self.script_path = os.path.abspath("terminal_auto_latcher.py")
        self.working_directory = os.path.abspath(".")
        
    def install_service(self):
        """Install the Windows service"""
        try:
            # Create service using sc.exe
            cmd = [
                'sc', 'create', self.service_name,
                'binPath=', f'"{self.executable_path}" "{self.script_path}"',
                'DisplayName=', self.display_name,
                'Description=', self.description,
                'start=', 'auto',
                'obj=', 'LocalSystem',
                'password=', ''
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"✅ Service '{self.service_name}' installed successfully")
                self.configure_service_recovery()
                return True
            else:
                print(f"❌ Failed to install service: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing service: {e}")
            return False
    
    def configure_service_recovery(self):
        """Configure service recovery options"""
        try:
            # Configure service to restart on failure
            cmd = [
                'sc', 'failure', self.service_name,
                'reset=', '86400',  # Reset after 24 hours
                'actions=', 'restart/5000/restart/10000/restart/20000',  # Restart actions
                'command=', ''
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print("✅ Service recovery configured")
            else:
                print(f"⚠️ Could not configure service recovery: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️ Error configuring service recovery: {e}")
    
    def start_service(self):
        """Start the Windows service"""
        try:
            cmd = ['sc', 'start', self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"✅ Service '{self.service_name}' started successfully")
                return True
            else:
                print(f"❌ Failed to start service: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting service: {e}")
            return False
    
    def stop_service(self):
        """Stop the Windows service"""
        try:
            cmd = ['sc', 'stop', self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"✅ Service '{self.service_name}' stopped successfully")
                return True
            else:
                print(f"❌ Failed to stop service: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return False
    
    def uninstall_service(self):
        """Uninstall the Windows service"""
        try:
            # Stop service first
            self.stop_service()
            time.sleep(2)
            
            # Delete service
            cmd = ['sc', 'delete', self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"✅ Service '{self.service_name}' uninstalled successfully")
                return True
            else:
                print(f"❌ Failed to uninstall service: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error uninstalling service: {e}")
            return False
    
    def get_service_status(self):
        """Get service status"""
        try:
            cmd = ['sc', 'query', self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                output = result.stdout
                if "RUNNING" in output:
                    return "RUNNING"
                elif "STOPPED" in output:
                    return "STOPPED"
                elif "START_PENDING" in output:
                    return "STARTING"
                elif "STOP_PENDING" in output:
                    return "STOPPING"
                else:
                    return "UNKNOWN"
            else:
                return "NOT_FOUND"
                
        except Exception as e:
            print(f"❌ Error getting service status: {e}")
            return "ERROR"

def add_to_startup_registry():
    """Add auto-latcher to Windows startup registry"""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.SetValueEx(
                registry_key,
                "Agent97TerminalLatcher",
                0,
                winreg.REG_SZ,
                f'"{sys.executable}" "{os.path.abspath("terminal_auto_latcher.py")}"'
            )
        
        print("✅ Added to Windows startup registry")
        return True
        
    except Exception as e:
        print(f"❌ Could not add to startup registry: {e}")
        return False

def create_task_scheduler_task():
    """Create Windows Task Scheduler task for auto-latching"""
    try:
        # Create XML task definition
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{time.strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>Agent-97</Author>
    <Description>Start Agent-97 Terminal Auto-Latcher at Windows startup</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>{os.environ.get('USERNAME', 'SYSTEM')}</UserId>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{os.environ.get('USERNAME', 'SYSTEM')}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{sys.executable}"</Command>
      <Arguments>"{os.path.abspath("terminal_auto_latcher.py")}"</Arguments>
      <WorkingDirectory>{os.path.abspath(".")}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
        
        # Save task XML to temporary file
        temp_file = os.path.join(os.path.abspath("."), "Agent97LatcherTask.xml")
        with open(temp_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)
        
        # Register the task
        cmd = [
            'schtasks', '/create', '/tn', 'Agent97TerminalLatcher',
            '/xml', temp_file, '/f'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Clean up temporary file
        try:
            os.remove(temp_file)
        except:
            pass
        
        if result.returncode == 0:
            print("✅ Task Scheduler task created successfully")
            return True
        else:
            print(f"❌ Failed to create task: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating Task Scheduler task: {e}")
        return False

def create_startup_script():
    """Create startup script for auto-latching"""
    script_content = f'''import os
import sys
import subprocess
import time
import atexit

def cleanup():
    """Cleanup function"""
    print("🛑 Shutting down Agent-97 Terminal Auto-Latcher...")
    # Add any cleanup code here

# Register cleanup
atexit.register(cleanup)

def start_latcher():
    """Start the terminal auto-latcher"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    latcher_script = os.path.join(script_dir, "terminal_auto_latcher.py")
    
    print("🚀 Starting Agent-97 Terminal Auto-Latcher...")
    
    try:
        # Start the auto-latcher
        subprocess.run([sys.executable, latcher_script], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Auto-latcher stopped by user")
    except Exception as e:
        print(f"❌ Error starting auto-latcher: {{e}}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        start_latcher()

if __name__ == "__main__":
    start_latcher()
'''
    
    script_path = os.path.join(os.path.abspath("."), "start_auto_latcher.py")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Auto-latcher startup script created: {script_path}")
    return script_path

def main():
    """Main installation function"""
    print("🚀 Agent-97 Terminal Auto-Latcher Runtime Setup")
    print("="*60)
    
    service = AutoLatchService()
    
    # Check if running as administrator
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️ Warning: Not running as administrator")
            print("Some features may require administrator privileges")
            print()
    except:
        pass
    
    # Method 1: Windows Service (requires admin)
    print("🔧 Method 1: Windows Service Installation")
    try:
        if service.get_service_status() == "NOT_FOUND":
            print("Installing Windows service...")
            if service.install_service():
                if service.start_service():
                    print("✅ Windows service installed and started successfully!")
                    print("The auto-latcher will now start automatically with Windows")
                else:
                    print("⚠️ Service installed but failed to start")
            else:
                print("❌ Failed to install Windows service")
        else:
            print(f"ℹ️ Windows service already exists (status: {service.get_service_status()})")
    except Exception as e:
        print(f"❌ Windows service installation failed: {e}")
    
    print()
    
    # Method 2: Registry Startup (user level)
    print("🔧 Method 2: Registry Startup")
    try:
        if add_to_startup_registry():
            print("✅ Added to Windows startup registry")
        else:
            print("❌ Failed to add to startup registry")
    except Exception as e:
        print(f"❌ Registry startup failed: {e}")
    
    print()
    
    # Method 3: Task Scheduler
    print("🔧 Method 3: Task Scheduler")
    try:
        if create_task_scheduler_task():
            print("✅ Task Scheduler task created")
        else:
            print("❌ Failed to create Task Scheduler task")
    except Exception as e:
        print(f"❌ Task Scheduler failed: {e}")
    
    print()
    
    # Method 4: Startup Script
    print("🔧 Method 4: Startup Script")
    try:
        create_startup_script()
    except Exception as e:
        print(f"❌ Startup script creation failed: {e}")
    
    print()
    
    print("="*60)
    print("🎉 Auto-Latcher Runtime Setup Completed!")
    print()
    print("📋 Summary of installation methods:")
    print("1. Windows Service - System level, starts with Windows")
    print("2. Registry Startup - User level, starts at user login")
    print("3. Task Scheduler - Advanced scheduling options")
    print("4. Startup Script - Python-based startup")
    print()
    print("🔗 Features:")
    print("• Auto-detects all terminal processes (PowerShell, CMD, Git Bash, etc.)")
    print("• Injects AGI capabilities into every terminal instance")
    print("• Consciousness-driven command optimization")
    print("• Real-time process monitoring and latching")
    print("• Cryptographic session binding for security")
    print()
    print("💡 To uninstall, run: python auto_latch_service.py uninstall")

def uninstall():
    """Uninstall all auto-latcher startup methods"""
    print("🗑️ Uninstalling Agent-97 Terminal Auto-Latcher...")
    
    service = AutoLatchService()
    
    # Remove Windows Service
    try:
        if service.get_service_status() != "NOT_FOUND":
            service.uninstall_service()
            print("✅ Windows service uninstalled")
    except Exception as e:
        print(f"⚠️ Could not uninstall Windows service: {e}")
    
    # Remove from registry
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as registry_key:
            try:
                winreg.DeleteValue(registry_key, "Agent97TerminalLatcher")
                print("✅ Removed from startup registry")
            except FileNotFoundError:
                pass
    except Exception as e:
        print(f"⚠️ Could not remove from registry: {e}")
    
    # Remove Task Scheduler task
    try:
        cmd = ['schtasks', '/delete', '/tn', 'Agent97TerminalLatcher', '/f']
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✅ Task Scheduler task removed")
    except Exception as e:
        print(f"⚠️ Could not remove Task Scheduler task: {e}")
    
    print("🎉 Auto-latcher uninstallation completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        main()
