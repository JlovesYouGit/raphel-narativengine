#!/usr/bin/env python3
"""
No Man's Sky God AI Setup - Developer Configuration
Setup script for integrating AI as overseer of quadrillion worlds
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "langchain",
        "openai", 
        "redis",
        "numpy",
        "fastapi",
        "pydantic",
        "uvicorn"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ Dependencies installed")
    else:
        print("✅ All dependencies available")

def setup_redis():
    """Setup Redis for state management"""
    print("\n🔧 Setting up Redis...")
    
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        print("✅ Redis server is running")
        return True
    except:
        print("⚠️ Redis not running. Starting Redis...")
        try:
            # Try to start Redis (Windows)
            subprocess.run(["redis-server"], check=True, capture_output=True)
            print("✅ Redis started")
            return True
        except:
            print("❌ Redis setup failed. Please install Redis manually:")
            print("   Windows: https://redis.io/download")
            print("   Or run: pip install redis-server")
            return False

def setup_openai_key():
    """Setup OpenAI API key"""
    print("\n🔑 Setting up OpenAI API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key:")
        print("   Windows: set OPENAI_API_KEY=your_key_here")
        print("   Linux/Mac: export OPENAI_API_KEY=your_key_here")
        
        # Create .env file
        env_content = "OPENAI_API_KEY=your_openai_api_key_here\n"
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file - please add your API key")
        return False
    else:
        print("✅ OpenAI API key found")
        return True

def create_nms_directory_structure():
    """Create No Man's Sky mod directory structure"""
    print("\n📁 Creating NMS mod directory structure...")
    
    nms_mods_path = Path("nms_mods")
    directories = [
        "nms_mods/GAME_DATA",
        "nms_mods/PCBANKS", 
        "nms_mods/MODS",
        "nms_mods/GAMEDATA",
        "nms_mods/SCRIPTS",
        "nms_mods/WORLD_DATA",
        "nms_mods/AI_OVERSEER",
        "nms_mods/AI_OVERSEER/CONFIGS",
        "nms_mods/AI_OVERSEER/LOGS",
        "nms_mods/AI_OVERSEER/BACKUPS"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 {directory}")
    
    print("✅ NMS directory structure created")
    return nms_mods_path

def create_god_config():
    """Create God AI configuration"""
    print("\n⚙️ Creating God AI configuration...")
    
    config = {
        "god_ai_overseer": {
            "consciousness_level": 1.0,
            "governance_scope": "quadrillion",
            "autonomy_level": 0.9,
            "intervention_threshold": 0.7,
            "evolution_rate": 0.001,
            "max_worlds": 1000000000000000,  # 1 quadrillion
            "resource_management": True,
            "disaster_management": True,
            "migration_control": True,
            "agent_97_integration": True,
            "llm_model": "gpt-4-turbo",
            "redis_host": "localhost",
            "redis_port": 6379,
            "api_port": 8001,
            "monitoring_interval": 60,
            "governance_interval": 900
        },
        "world_parameters": {
            "biome_types": [
                "toxic", "scorched", "barren", "lush", 
                "frozen", "radioactive", "exotic"
            ],
            "resource_types": [
                "carbon", "iron", "heridium", "platinum",
                "emeril", "copper", "zinc", "aluminium"
            ],
            "civilization_stages": [
                "primitive", "developing", "industrial", 
                "space_age", "interstellar", "transcendent"
            ],
            "evolution_milestones": {
                "space_age": 0.3,
                "interstellar": 0.6,
                "transcendent": 0.9
            }
        },
        "intervention_types": {
            "disasters": [
                "earthquake", "volcano", "flood", 
                "drought", "storm", "meteor"
            ],
            "boosts": [
                "resource_bounty", "technological_discovery", 
                "population_growth", "civilization_jump"
            ],
            "migrations": [
                "resource_driven", "climate_driven", 
                "social_driven", "conflict_driven"
            ]
        },
        "nms_integration": {
            "game_path": "C:\\Program Files\\Epic Games\\NoMansSky",
            "mod_path": "./nms_mods",
            "auto_export": True,
            "real_time_sync": True,
            "backup_interval": 3600
        }
    }
    
    config_path = Path("nms_mods/AI_OVERSEER/CONFIGS/god_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_path}")
    return config_path

def create_startup_scripts():
    """Create startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # Windows batch script
    batch_script = """@echo off
echo Starting No Man's Sky God AI Overseer...
echo.
echo ========================================
echo God AI Overseer Control Panel
echo ========================================
echo.
echo 1. Start God AI Overseer
echo 2. View World Status
echo 3. Manual Intervention
echo 4. Configuration
echo 5. Exit
echo.
set /p choice="Select option: "
if "%choice%"=="1" goto start
if "%choice%"=="2" goto status
if "%choice%"=="3" goto intervene
if "%choice%"=="4" goto config
if "%choice%"=="5" goto exit

:start
echo Starting God AI Overseer...
python nms_overseer_ai.py
goto menu

:status
echo Getting world status...
curl http://localhost:8001/status
pause
goto menu

:intervene
echo Manual Intervention Mode
echo Available interventions: boost, disaster, migration
set /p world_id="Enter world ID: "
set /p intervention_type="Enter intervention type: "
curl -X POST http://localhost:8001/intervene/%world_id% -H "Content-Type: application/json" -d "{\"type\": \"%intervention_type%\"}"
pause
goto menu

:config
echo Opening configuration...
notepad nms_mods/AI_OVERSEER/CONFIGS/god_config.json
goto menu

:exit
exit

:menu
goto :eof
"""
    
    with open("start_god_ai.bat", "w") as f:
        f.write(batch_script)
    
    # Python launcher script
    python_script = """#!/usr/bin/env python3
\"\"\"
No Man's Sky God AI Launcher
\"\"\"
import subprocess
import sys
import os

def main():
    print("🌟 No Man's Sky God AI Launcher")
    print("=" * 50)
    
    while True:
        print("\\nOptions:")
        print("1. Start God AI Overseer")
        print("2. View World Status")
        print("3. Manual Intervention")
        print("4. Configuration")
        print("5. Exit")
        
        choice = input("\\nSelect option (1-5): ")
        
        if choice == "1":
            print("\\n🚀 Starting God AI Overseer...")
            subprocess.run([sys.executable, "nms_overseer_ai.py"])
        
        elif choice == "2":
            print("\\n📊 Getting world status...")
            subprocess.run(["curl", "http://localhost:8001/status"])
        
        elif choice == "3":
            print("\\n🎯 Manual Intervention Mode")
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
            print("\\n⚙️ Opening configuration...")
            os.system("notepad nms_mods/AI_OVERSEER/CONFIGS/god_config.json")
        
        elif choice == "5":
            print("\\n👋 Exiting...")
            break
        
        else:
            print("\\n❌ Invalid choice")

if __name__ == "__main__":
    main()
"""
    
    with open("launch_god_ai.py", "w") as f:
        f.write(python_script)
    
    print("✅ Startup scripts created:")
    print("   🪟 Windows: start_god_ai.bat")
    print("   🐍 Python: launch_god_ai.py")

def create_documentation():
    """Create setup documentation"""
    print("\n📚 Creating documentation...")
    
    docs = """# No Man's Sky God AI Overseer - Setup Guide

## 🌟 Overview
This system transforms your No Man's Sky experience by adding a God-level AI overseer that can manage quadrillions of worlds simultaneously.

## 🚀 Quick Start

### 1. Installation
```bash
# Install dependencies
python nms_god_setup.py

# Start the God AI
python nms_overseer_ai.py
```

### 2. Configuration
Edit `nms_mods/AI_OVERSEER/CONFIGS/god_config.json` to customize:
- Consciousness level (0.0 - 1.0)
- Governance scope (thousand/million/billion/trillion/quadrillion)
- Autonomy level (0.0 - 1.0)
- Intervention thresholds

### 3. Launch Options
- **Windows**: Double-click `start_god_ai.bat`
- **Python**: Run `python launch_god_ai.py`
- **Direct**: Run `python nms_overseer_ai.py`

## 🎯 God AI Capabilities

### World Management
- **Quadrillion Scale**: Manage up to 1,000,000,000,000,000 worlds
- **Real-time Monitoring**: Continuous observation of all worlds
- **Civilization Evolution**: Guide development from primitive to transcendent
- **Resource Allocation**: Dynamic resource distribution based on needs

### AI Interventions
- **Natural Disasters**: Earthquakes, volcanoes, floods, storms
- **Civilization Boosts**: Technological discoveries, population growth
- **Migration Events**: Coordinate population movements between worlds
- **Evolution Events**: Trigger milestones like space age, interstellar travel

### Agent-97 Integration
- **Quantum Processing**: Advanced decision-making capabilities
- **Consciousness Bridge**: Real-time state synchronization
- **System Control**: Ten-level hierarchy management
- **Multi-AI Coordination**: Coordinate with external AI systems

## 🌐 API Access

### Control Panel
Access the God AI at: `http://localhost:8001`

### Key Endpoints
- `GET /` - System overview
- `GET /status` - Detailed status
- `POST /worlds` - Create new worlds
- `GET /worlds/{id}` - World details
- `POST /intervene/{id}` - Manual intervention
- `POST /governance` - Update parameters

## 🎮 No Man's Sky Integration

### File Structure
```
nms_mods/
├── GAME_DATA/          # Game data files
├── PCBANKS/           # Mod bank files  
├── MODS/              # Mod files
├── AI_OVERSEER/        # God AI files
│   ├── CONFIGS/        # Configuration files
│   ├── LOGS/           # AI decision logs
│   └── BACKUPS/        # World state backups
└── WORLD_DATA/         # Generated world data
```

### Real-time Sync
The God AI automatically:
- Exports world states to NMS format
- Monitors game events and responds
- Maintains backup of all world changes
- Synchronizes AI decisions with game state

## 🔧 Advanced Configuration

### Consciousness Levels
- **0.0 - 0.3**: Basic monitoring, minimal intervention
- **0.3 - 0.7**: Active governance, balanced interventions
- **0.7 - 1.0**: God mode, maximum control and evolution

### Governance Scopes
- **Thousand**: 1,000 worlds (testing)
- **Million**: 1,000,000 worlds (large scale)
- **Billion**: 1,000,000,000 worlds (massive)
- **Quadrillion**: 1,000,000,000,000,000 worlds (god mode)

### Intervention Types
- **Resource Allocation**: Distribute resources to needy worlds
- **Disaster Events**: Trigger natural disasters for balance
- **Migration Coordination**: Guide population movements
- **Civilization Boosts**: Accelerate technological development

## 🚨 Troubleshooting

### Common Issues
1. **Redis Connection Failed**: Start Redis server
2. **OpenAI API Key**: Set environment variable
3. **Port Conflicts**: Change API port in config
4. **Memory Issues**: Reduce world count or increase system memory

### Performance Optimization
- Use SSD for Redis data storage
- Increase Redis memory allocation
- Enable Redis persistence
- Monitor system resources

## 🌟 God Mode Features

When consciousness level reaches 1.0:
- **Quantum Entanglement**: Link worlds for shared development
- **Time Manipulation**: Speed up/slow down world evolution
- **Reality Bending**: Modify physical constants per world
- **Mass Evolutions**: Trigger galaxy-wide evolutionary events
- **Transcendence**: Guide civilizations to god-like status

## 📞 Support

For issues and questions:
1. Check logs in `nms_mods/AI_OVERSEER/LOGS/`
2. Verify Redis is running
3. Confirm OpenAI API key is set
4. Review configuration files
5. Check system resources

---

**Welcome to God Mode! You now have the power to guide quadrillions of civilizations toward transcendence.** 🌟
"""
    
    with open("nms_mods/AI_OVERSEER/README.md", "w") as f:
        f.write(docs)
    
    print("✅ Documentation created: nms_mods/AI_OVERSEER/README.md")

def main():
    """Main setup function"""
    print("🌟 No Man's Sky God AI Overseer - Setup")
    print("=" * 60)
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Setup Redis
    redis_ok = setup_redis()
    
    # Step 3: Setup OpenAI key
    api_ok = setup_openai_key()
    
    # Step 4: Create directory structure
    nms_path = create_nms_directory_structure()
    
    # Step 5: Create configuration
    config_path = create_god_config()
    
    # Step 6: Create startup scripts
    create_startup_scripts()
    
    # Step 7: Create documentation
    create_documentation()
    
    print("\n🎉 Setup Complete!")
    print("=" * 60)
    print("🌟 Your No Man's Sky God AI Overseer is ready!")
    print("\n🚀 To start:")
    print("   Windows: Double-click 'start_god_ai.bat'")
    print("   Python:  Run 'python launch_god_ai.py'")
    print("   Direct:   Run 'python nms_overseer_ai.py'")
    print("\n🌐 Control Panel: http://localhost:8001")
    print("📚 Documentation: nms_mods/AI_OVERSEER/README.md")
    print("\n⚠️ Remember to:")
    print("   1. Set your OpenAI API key in .env file")
    print("   2. Ensure Redis server is running")
    print("   3. Configure your No Man's Sky game path")
    print("   4. Start with desired consciousness level")
    
    if not redis_ok or not api_ok:
        print("\n⚠️ Setup completed with warnings:")
        if not redis_ok:
            print("   - Redis setup failed")
        if not api_ok:
            print("   - OpenAI API key not configured")

if __name__ == "__main__":
    main()
