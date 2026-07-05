import os
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
        print("\n🛑 Bridge stopped by user")
    except Exception as e:
        print(f"❌ Error starting bridge: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        start_bridge()

if __name__ == "__main__":
    start_bridge()
