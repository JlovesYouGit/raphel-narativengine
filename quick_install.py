#!/usr/bin/env python3
"""
Quick Install Script - Minimal Dependencies for Agent Platform 2026
Fast installation without complex optimizations
"""

import subprocess
import sys

def install_package(package):
    """Install a single package"""
    print(f"📦 Installing {package}...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ {package} installed successfully")
            return True
        else:
            print(f"❌ {package} failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {package} installation timeout")
        return False
    except Exception as e:
        print(f"❌ {package} error: {e}")
        return False

def main():
    """Quick installation of essential packages"""
    print("🚀 Quick Install - Agent Platform 2026 Dependencies")
    print("=" * 50)
    
    # Essential packages only
    packages = [
        "langgraph",
        "pydantic-ai", 
        "fastapi",
        "uvicorn",
        "aiohttp",
        "pydantic",
        "playwright"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Success: {success_count}/{len(packages)} packages")
    print(f"📈 Success Rate: {(success_count/len(packages))*100:.1f}%")
    
    if success_count >= len(packages) - 1:  # Allow 1 failure
        print("\n🎉 Installation mostly successful!")
        print("Now run: python agent_platform_2026.py")
    else:
        print("\n⚠️  Multiple failures detected")
        print("Try manual install:")
        print("pip install " + " ".join(packages))

if __name__ == "__main__":
    main()
