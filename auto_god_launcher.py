#!/usr/bin/env python3
"""
Auto God Launcher - No Man's Sky God AI Overseer
Automatic startup without terminal interaction
"""

import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if Redis is running
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        print("✅ Redis server is running")
    except:
        print("❌ Redis not running - starting...")
        try:
            subprocess.Popen(["redis-server"], shell=True)
            time.sleep(3)  # Give Redis time to start
            print("✅ Redis started")
        except:
            print("❌ Failed to start Redis")
            return False
    
    # Check if configuration exists
    config_path = Path("nms_mods/AI_OVERSEER/CONFIGS/god_config.json")
    if config_path.exists():
        print("✅ Configuration found")
    else:
        print("❌ Configuration not found - running setup...")
        try:
            subprocess.run([sys.executable, "nms_god_setup.py"], check=True)
            print("✅ Setup completed")
        except:
            print("❌ Setup failed")
            return False
    
    # Check OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key configured")
    else:
        print("⚠️ OpenAI API key not set - using local AI")
    
    return True

def create_service_files():
    """Create service files for auto-startup"""
    print("🔧 Creating service files...")
    
    # Windows service
    windows_service = """[Unit]
Description=No Man's Sky God AI Overseer
After=network.target

[Service]
Type=simple
User=%USERNAME%
WorkingDirectory=%CD%
ExecStart=%PYTHON% nms_overseer_ai.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=%CD%

[Install]
WantedBy=multi-user.target
"""
    
    # Linux systemd service
    linux_service = """[Unit]
Description=No Man's Sky God AI Overseer
After=network.target

[Service]
Type=simple
User=nms
WorkingDirectory=/opt/nms_god_ai
ExecStart=/usr/bin/python3 nms_overseer_ai.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/nms_god_ai

[Install]
WantedBy=multi-user.target
"""
    
    # Create service directory
    service_dir = Path("services")
    service_dir.mkdir(exist_ok=True)
    
    with open(service_dir / "nms_god_ai.service", "w") as f:
        if os.name == 'nt':
            f.write(windows_service)
        else:
            f.write(linux_service)
    
    print("✅ Service files created")
    return service_dir

def create_auto_start_script():
    """Create auto-start script"""
    print("🚀 Creating auto-start script...")
    
    auto_script = """#!/usr/bin/env python3
\"\"\"
Auto-start script for No Man's Sky God AI Overseer
\"\"\"
import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path

def ensure_redis():
    \"\"\"Ensure Redis is running\"\"\"
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        return True
    except:
        try:
            subprocess.Popen(['redis-server'], shell=True)
            time.sleep(5)
            return True
        except:
            return False

def start_god_ai():
    \"\"\"Start God AI overseer\"\"\"
    print("🌟 Auto-starting No Man's Sky God AI Overseer...")
    
    # Ensure Redis is running
    if not ensure_redis():
        print("❌ Failed to start Redis")
        return
    
    # Change to correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Start the God AI
    try:
        subprocess.run([sys.executable, 'nms_overseer_ai.py'], check=True)
        print("✅ God AI started successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start God AI: {e}")
    except KeyboardInterrupt:
        print("\\n👋 God AI stopped by user")

if __name__ == "__main__":
    start_god_ai()
"""
    
    with open("auto_start_god_ai.py", "w") as f:
        f.write(auto_script)
    
    print("✅ Auto-start script created")
    return "auto_start_god_ai.py"

def main():
    """Main auto-launcher function"""
    print("🌟 No Man's Sky God AI Auto-Launcher")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met")
        return
    
    # Create service files
    service_dir = create_service_files()
    
    # Create auto-start script
    auto_script = create_auto_start_script()
    
    print("\n🎉 Auto-launcher setup complete!")
    print("=" * 50)
    print("📁 Files created:")
    print(f"   📄 Service files: {service_dir}")
    print(f"   🚀 Auto-start script: {auto_script}")
    
    print("\n🚀 Auto-start options:")
    print("1. Run auto-start script now:")
    print(f"   python {auto_script}")
    print("\n2. Install as system service:")
    if os.name == 'nt':
        print("   Windows: Copy service files and use sc create")
    else:
        print("   Linux: Copy nms_god_ai.service to /etc/systemd/system/")
        print("   Then run: sudo systemctl enable nms_god_ai")
    
    print("\n3. Direct start:")
    print("   python nms_overseer_ai.py")
    
    # Ask if user wants to start now
    try:
        choice = input("\n🚀 Start God AI now? (y/n): ").lower()
        if choice in ['y', 'yes', '']:
            print("\n🌟 Starting God AI overseer...")
            os.system(f"python {auto_script}")
    except KeyboardInterrupt:
        print("\n👋 Setup complete. Run manually when ready.")

if __name__ == "__main__":
    main()
