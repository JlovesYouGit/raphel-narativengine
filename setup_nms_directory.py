#!/usr/bin/env python3
"""
No Man's Sky Directory Setup
Creates the required directory structure for NMS modding and AI integration
"""

import os
from pathlib import Path

def create_nms_directory():
    """Create No Man's Sky directory structure"""
    print("🌍 Creating No Man's Sky mod directory structure...")
    
    # Define the base NMS directory structure
    nms_structure = {
        "GAMEDATA": {
            "PCBANKS": {
                "README.txt": "Place mod bank files here",
                "EXAMPLES": {}
            },
            "MODS": {
                "README.txt": "Place mod files here",
                "ACTIVE": {}
            },
            "SCRIPTS": {
                "README.txt": "Lua scripts for game modifications",
                "EXAMPLES": {}
            },
            "WORLDDATA": {
                "README.txt": "Custom world data files",
                "GENERATED": {},
                "BACKUPS": {}
            },
            "AI_OVERSEER": {
                "README.txt": "God AI overseer files",
                "CONFIGS": {},
                "LOGS": {},
                "BACKUPS": {},
                "MODELS": {}
            }
        },
        "DOCUMENTS": {
            "README.txt": "Documentation and guides",
            "IMAGES": {},
            "VIDEOS": {}
        },
        "TOOLS": {
            "README.txt": "Development and utility tools",
            "CONVERTERS": {},
            "VALIDATORS": {}
        }
    }
    
    # Create the main directory
    base_path = Path("NOMANSSKY")
    base_path.mkdir(exist_ok=True)
    
    # Recursively create directory structure
    def create_structure(base, structure):
        for name, content in structure.items():
            path = base / name
            path.mkdir(exist_ok=True)
            
            if isinstance(content, dict):
                create_structure(path, content)
            elif isinstance(content, str):
                # Create README file
                with open(path / "README.txt", "w") as f:
                    f.write(content)
    
    create_structure(base_path, nms_structure)
    
    # Create additional important files
    create_additional_files(base_path)
    
    return base_path

def create_additional_files(base_path):
    """Create additional configuration and setup files"""
    
    # Create mod configuration
    mod_config = """# No Man's Sky Mod Configuration
# This file configures your NMS mod setup

[MOD_INFO]
name = "God AI Overseer"
version = "1.0.0"
author = "AI Developer"
description = "God-level AI management system for quadrillions of worlds"

[PATHS]
game_data = "./GAMEDATA"
mods = "./GAMEDATA/MODS"
scripts = "./GAMEDATA/SCRIPTS"
world_data = "./GAMEDATA/WORLDDATA"
ai_overseer = "./GAMEDATA/AI_OVERSEER"

[AI_CONFIG]
consciousness_level = 1.0
governance_scope = "quadrillion"
autonomy_level = 0.9
local_model_path = "./AI_OVERSEER/MODELS"
use_agent97 = true

[INTEGRATION]
real_time_sync = true
auto_backup = true
backup_interval = 3600
log_level = "INFO"
"""
    
    with open(base_path / "mod_config.ini", "w") as f:
        f.write(mod_config)
    
    # Create startup script
    startup_script = """@echo off
title No Man's Sky - God AI Setup
echo.
echo ========================================
echo   No Man's Sky Mod Directory Setup
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "GAMEDATA" (
    echo [ERROR] Not in NMS mod directory
    echo [INFO] Please run this from your No Man's Sky mod folder
    pause
    exit /b 1
)

echo [SUCCESS] NMS mod directory structure created
echo [INFO] Directory structure:
echo.
echo   NOMANSSKY/
echo   ├── GAMEDATA/
echo   │   ├── PCBANKS/        (Mod bank files)
echo   │   ├── MODS/           (Mod files)
echo   │   ├── SCRIPTS/         (Lua scripts)
echo   │   ├── WORLDDATA/       (World data)
echo   │   └── AI_OVERSEER/     (God AI files)
echo   ├── DOCUMENTS/         (Documentation)
echo   └── TOOLS/             (Development tools)
echo.
echo [INFO] Your No Man's Sky mod directory is ready!
echo [INFO] Place your mod files in the appropriate folders
echo.
pause
"""
    
    with open(base_path / "setup_nms.bat", "w") as f:
        f.write(startup_script)
    
    # Create Python launcher
    python_launcher = """#!/usr/bin/env python3
\"\"\"
No Man's Sky Mod Directory Launcher
\"\"\"
import os
import subprocess
import sys
from pathlib import Path

def main():
    print("🌍 No Man's Sky Mod Directory Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("GAMEDATA").exists():
        print("❌ Not in NMS mod directory")
        print("ℹ️  Please run this from your No Man's Sky mod folder")
        return
    
    print("✅ NMS mod directory structure verified")
    print("📁 Directory contents:")
    
    # Show directory structure
    def show_tree(path, prefix=""):
        try:
            items = sorted(path.iterdir())
        except PermissionError:
            return
        
        for i, item in enumerate(items):
            if item.is_dir():
                print(f"{prefix}├── {item.name}/")
                show_tree(item, prefix + "│   ")
            else:
                print(f"{prefix}├── {item.name}")
    
    show_tree(Path("."))
    
    print("\n🎯 Next steps:")
    print("1. Place mod files in GAMEDATA/MODS/")
    print("2. Add scripts to GAMEDATA/SCRIPTS/")
    print("3. Configure AI in GAMEDATA/AI_OVERSEER/CONFIGS/")
    print("4. Run God AI: python nms_god_local_ai.py")
    print("5. Launch No Man's Sky with mods enabled")

if __name__ == "__main__":
    main()
"""
    
    with open(base_path / "check_nms.py", "w") as f:
        f.write(python_launcher)

def main():
    """Main setup function"""
    print("🌍 No Man's Sky Directory Setup")
    print("=" * 50)
    
    # Create directory structure
    nms_path = create_nms_directory()
    
    print("\n✅ Directory structure created successfully!")
    print("=" * 50)
    print(f"📁 Created at: {nms_path.absolute()}")
    print("\n📂 Directory Structure:")
    
    # Show created structure
    def show_structure(path, indent=0):
        for item in sorted(path.iterdir()):
            if item.is_dir():
                print("    " * indent + f"📁 {item.name}/")
                show_structure(item, indent + 2)
            else:
                print("    " * indent + f"📄 {item.name}")
    
    show_structure(nms_path)
    
    print("\n🎯 What to do next:")
    print("1. Copy this directory to your No Man's Sky mod folder")
    print("2. Run the setup script:")
    print(f"   Windows: {nms_path / 'setup_nms.bat'}")
    print(f"   Python:  python {nms_path / 'check_nms.py'}")
    print("3. Place your AI model files in: GAMEDATA/AI_OVERSEER/MODELS/")
    print("4. Configure God AI: Edit GAMEDATA/AI_OVERSEER/CONFIGS/god_config.json")
    print("5. Start God AI: python nms_god_local_ai.py")
    print("6. Launch No Man's Sky with mods enabled")
    
    print("\n📚 Important Notes:")
    print("• This creates the standard NMS mod directory structure")
    print("• AI overseer files are in GAMEDATA/AI_OVERSEER/")
    print("• Configuration files use JSON format")
    print("• All paths are relative to the mod directory")
    print("• Backup your original NMS files before modding")
    
    print(f"\n🚀 Quick start:")
    print(f"cd {nms_path.absolute()}")
    print("setup_nms.bat")

if __name__ == "__main__":
    main()
