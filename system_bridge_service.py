import winreg
import os
import sys
import time
import subprocess
import threading
import signal
import atexit
from pathlib import Path

class SystemBridgeService:
    """Windows Service for Agent-97 System Bridge"""
    
    def __init__(self):
        self.service_name = "Agent97SystemBridge"
        self.display_name = "Agent-97 AGI System Bridge"
        self.description = "Advanced AGI system integration and optimization service"
        self.executable_path = sys.executable
        self.script_path = os.path.abspath("system_bridge.py")
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

def create_startup_shortcut():
    """Create startup shortcut for user-level auto-start"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Agent-97 System Bridge.lnk")
        target = sys.executable
        args = f'"{os.path.abspath("system_bridge.py")}"'
        wDir = os.path.abspath(".")
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = args
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print(f"✅ Startup shortcut created: {path}")
        return True
        
    except ImportError:
        # Fallback method without winshell
        try:
            import win32com.client
            
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop_path, "Agent-97 System Bridge.lnk")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{os.path.abspath("system_bridge.py")}"'
            shortcut.WorkingDirectory = os.path.abspath(".")
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print(f"✅ Startup shortcut created: {shortcut_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not create shortcut: {e}")
            return False
    except Exception as e:
        print(f"⚠️ Could not create startup shortcut: {e}")
        return False

def add_to_startup_registry():
    """Add to Windows startup registry"""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.SetValueEx(
                registry_key,
                "Agent97SystemBridge",
                0,
                winreg.REG_SZ,
                f'"{sys.executable}" "{os.path.abspath("system_bridge.py")}"'
            )
        
        print("✅ Added to Windows startup registry")
        return True
        
    except Exception as e:
        print(f"❌ Could not add to startup registry: {e}")
        return False

def create_task_scheduler_task():
    """Create Windows Task Scheduler task"""
    try:
        # Create XML task definition
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{time.strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>Agent-97</Author>
    <Description>Start Agent-97 System Bridge at Windows startup</Description>
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
      <Arguments>"{os.path.abspath("system_bridge.py")}"</Arguments>
      <WorkingDirectory>{os.path.abspath(".")}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
        
        # Save task XML to temporary file
        temp_file = os.path.join(os.path.abspath("."), "Agent97BridgeTask.xml")
        with open(temp_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)
        
        # Register the task
        cmd = [
            'schtasks', '/create', '/tn', 'Agent97SystemBridge',
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

def main():
    """Main installation function"""
    print("🚀 Agent-97 System Bridge Runtime Setup")
    print("="*50)
    
    service = SystemBridgeService()
    
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
                    print("The bridge will now start automatically with Windows")
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
    
    # Method 4: Desktop Shortcut (manual start)
    print("🔧 Method 4: Desktop Shortcut")
    try:
        if create_startup_shortcut():
            print("✅ Desktop shortcut created")
        else:
            print("❌ Failed to create desktop shortcut")
    except Exception as e:
        print(f"❌ Shortcut creation failed: {e}")
    
    print()
    
    # Create auto-start script
    create_autostart_script()
    
    print("="*50)
    print("🎉 Runtime Setup Completed!")
    print()
    print("📋 Summary of installation methods:")
    print("1. Windows Service - System level, starts with Windows")
    print("2. Registry Startup - User level, starts at user login")
    print("3. Task Scheduler - Advanced scheduling options")
    print("4. Desktop Shortcut - Manual start option")
    print("5. Auto-start Script - Python-based startup")
    print()
    print("🌐 The bridge will be available at:")
    print("   WebSocket: ws://localhost:8081/ws")
    print("   HTTP API: http://localhost:8081/status")
    print()
    print("💡 To uninstall, run: python system_bridge_service.py uninstall")

def create_autostart_script():
    """Create a Python auto-start script"""
    script_content = f'''import os
import sys
import subprocess
import time
import atexit

def cleanup():
    """Cleanup function"""
    print("🛑 Shutting down Agent-97 System Bridge...")
    # Add any cleanup code here

# Register cleanup
atexit.register(cleanup)

def start_bridge():
    """Start the system bridge"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bridge_script = os.path.join(script_dir, "system_bridge.py")
    
    print("🚀 Starting Agent-97 System Bridge...")
    
    try:
        # Start the bridge
        subprocess.run([sys.executable, bridge_script], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Bridge stopped by user")
    except Exception as e:
        print(f"❌ Error starting bridge: {{e}}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        start_bridge()

if __name__ == "__main__":
    start_bridge()
'''
    
    script_path = os.path.join(os.path.abspath("."), "start_bridge.py")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Auto-start script created: {script_path}")

def uninstall():
    """Uninstall all startup methods"""
    print("🗑️ Uninstalling Agent-97 System Bridge Runtime...")
    
    service = SystemBridgeService()
    
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
                winreg.DeleteValue(registry_key, "Agent97SystemBridge")
                print("✅ Removed from startup registry")
            except FileNotFoundError:
                pass
    except Exception as e:
        print(f"⚠️ Could not remove from registry: {e}")
    
    # Remove Task Scheduler task
    try:
        cmd = ['schtasks', '/delete', '/tn', 'Agent97SystemBridge', '/f']
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✅ Task Scheduler task removed")
    except Exception as e:
        print(f"⚠️ Could not remove Task Scheduler task: {e}")
    
    # Remove desktop shortcut
    try:
        import winshell
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Agent-97 System Bridge.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("✅ Desktop shortcut removed")
    except:
        pass
    
    print("🎉 Uninstallation completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        main()
