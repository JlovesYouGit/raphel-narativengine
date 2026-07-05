#!/usr/bin/env python3
"""
No Man's Sky God AI Launcher
"""
import subprocess
import sys
import os

def main():
    print("🌟 No Man's Sky God AI Launcher")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Start God AI Overseer")
        print("2. View World Status")
        print("3. Manual Intervention")
        print("4. Configuration")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == "1":
            print("\n🚀 Starting God AI Overseer...")
            subprocess.run([sys.executable, "nms_overseer_ai.py"])
        
        elif choice == "2":
            print("\n📊 Getting world status...")
            subprocess.run(["curl", "http://localhost:8001/status"])
        
        elif choice == "3":
            print("\n🎯 Manual Intervention Mode")
            world_id = input("Enter world ID: ")
            intervention_type = input("Enter intervention type (boost/disaster/migration): ")
            
            import subprocess
            subprocess.run([
                "curl", "-X", "POST", 
                f"http://localhost:8001/intervene/{world_id}",
                "-H", "Content-Type: application/json",
                "-d", f'{{"type": "{intervention_type}"}}'
            ])
        
        elif choice == "4":
            print("\n⚙️ Opening configuration...")
            os.system("notepad nms_mods/AI_OVERSEER/CONFIGS/god_config.json")
        
        elif choice == "5":
            print("\n👋 Exiting...")
            break
        
        else:
            print("\n❌ Invalid choice")

if __name__ == "__main__":
    main()
