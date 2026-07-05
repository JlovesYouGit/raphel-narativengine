# Terminal Assistant Integration Guide

## 💻 Advanced Windows Terminal Assistant

Agent-97 Terminal Assistant provides intelligent Windows terminal automation with AGI integration, featuring PowerShell/CMD support, elevation handling, and intelligent file management.

## 🚀 Quick Start

### Installation
```bash
# Terminal Assistant is included in the main framework
cd "n:\lossless agi"
.\model_env\Scripts\python terminal_assistant.py
```

### Basic Usage
```python
from terminal_assistant import TerminalAssistant

# Initialize assistant
assistant = TerminalAssistant()

# Create PowerShell session
session = await assistant.create_terminal_session("powershell")

# Execute commands
result = await assistant.execute_command(session.session_id, "Get-Process")
```

## 🔧 Terminal Features

### 🖥️ Multi-Terminal Support
- **PowerShell**: Full PowerShell cmdlet support
- **Command Prompt**: Traditional CMD commands
- **Git Bash**: Git version control operations
- **Elevation**: Automatic privilege escalation

### 🧠 Intelligent Features
- **Auto-completion**: Context-aware command suggestions
- **Command Prediction**: AI-powered next command suggestions
- **AGI Optimization**: Consciousness-driven command optimization
- **Error Handling**: Intelligent error recovery

### 📁 File Management
- **Auto-Sorting**: Intelligent file organization
- **Batch Operations**: Multi-file operations
- **Smart Shortcuts**: Custom command shortcuts
- **Pattern Recognition**: File type detection

## 🎯 Advanced Features

### PowerShell Integration
```python
# System information
await assistant.execute_command(session_id, "Get-ComputerInfo")

# Process management
await assistant.execute_command(session_id, "Get-Process | Where-Object {$_.CPU -gt 10}")

# Service management
await assistant.execute_command(session_id, "Get-Service | Where-Object {$_.Status -eq 'Running'}")

# Network information
await assistant.execute_command(session_id, "Get-NetAdapterStatistics")
```

### Elevation Handling
```python
# Automatic elevation detection
result = await assistant.execute_command(session_id, "Get-Service -Name 'BITS' -Restart")

# Manual elevation request
elevated_session = await assistant.create_terminal_session("powershell", elevation=True)
```

### Intelligent Auto-Completion
```python
# Get command suggestions
suggestions = await assistant.intelligent_auto_complete("Get-")
# Returns: ['Get-Process', 'Get-Service', 'Get-ChildItem', 'Get-EventLog']

# Predict next commands
predictions = await assistant.predict_next_command(session_id)
# Returns: ['dir', 'Get-Content', 'cd', 'copy']
```

## 📁 File Management Features

### Intelligent File Sorting
```python
# Sort files by type
result = await assistant.auto_sort_files(
    source_directory="C:\\Downloads",
    sort_criteria="by_type"
)

# Sort by size
result = await assistant.auto_sort_files(
    source_directory="C:\\Downloads", 
    sort_criteria="by_size"
)

# Sort by date
result = await assistant.auto_sort_files(
    source_directory="C:\\Downloads",
    sort_criteria="by_date"
)
```

### Sorting Criteria
- **by_type**: Images, Documents, Videos, Code, etc.
- **by_size**: Small (<1MB), Medium (1-10MB), Large (10-100MB), Huge (>100MB)
- **by_date**: Today, This Week, This Month, Older
- **by_name**: Alphabetical, Numeric first/last

### Batch File Operations
```python
operations = [
    {"type": "copy", "source": "file1.txt", "destination": "backup/"},
    {"type": "move", "source": "temp.txt", "destination": "archive/"},
    {"type": "delete", "source": "old_file.txt"}
]

result = await assistant.batch_file_operations(operations)
```

## ⚡ Intelligent Shortcuts

### Create Custom Shortcuts
```python
# System information shortcut
await assistant.create_intelligent_shortcut(
    name="System Info",
    command="Get-ComputerInfo",
    description="Get detailed system information"
)

# Network diagnostics shortcut
await assistant.create_intelligent_shortcut(
    name="Net Diag",
    command="Get-NetAdapterStatistics; Test-Connection google.com",
    description="Network connectivity diagnostics"
)
```

### Built-in Shortcuts
- **System Info**: `Get-ComputerInfo`
- **Process Monitor**: `Get-Process | Sort-Object CPU -Descending`
- **Service Status**: `Get-Service | Where-Object {$_.Status -eq 'Running'}`
- **Disk Usage**: `Get-Volume | Format-Table DriveLetter, Size, FreeSpace`
- **Network Info**: `Get-NetAdapter | Format-Table Name, Status`

## 🔍 Command Intelligence

### AGI-Powered Optimization
```python
# Commands are automatically optimized
# "dir" becomes "dir /a"
# "Get-Process" becomes "Get-Process -ErrorAction SilentlyContinue"
# "git status" gets context-aware suggestions
```

### Pattern Recognition
```python
# Detect command sequences and suggest next steps
if last_command == "cd C:\\Downloads":
    suggestions = ["dir", "Get-ChildItem", "git status"]

if last_command == "git add .":
    suggestions = ["git commit -m", "git status"]
```

### Error Recovery
```python
# Intelligent error handling
# - Permission denied → suggest elevation
# - Command not found → suggest alternatives
# - Syntax errors → provide corrections
```

## 🛡️ Security Features

### Elevation Management
```python
# Automatic elevation detection
if assistant.requires_elevation("Get-Service -Name 'BITS' -Restart"):
    # Creates elevated session automatically
    pass

# Manual control
elevated_session = await assistant.create_terminal_session("powershell", elevation=True)
```

### Safe Execution
- **Command validation**: Prevent dangerous commands
- **Path validation**: Verify file paths before operations
- **Permission checks**: Verify user permissions
- **Rollback capability**: Undo file operations

## 📊 Monitoring and Analytics

### Command History
```python
# Get command statistics
status = await assistant.get_terminal_assistant_status()
print(f"Commands executed: {status['metrics']['total_commands']}")
print(f"Success rate: {status['metrics']['successful_commands'] / status['metrics']['total_commands']:.1%}")
```

### Session Management
```python
# Active sessions
for session_id, session in assistant.active_sessions.items():
    print(f"Session {session_id}: {session.terminal_type} (elevated: {session.is_elevated})")

# Session cleanup
await assistant.cleanup_session(session_id)
```

## 🔧 Advanced Usage Examples

### System Administration
```python
# Get system health report
commands = [
    "Get-ComputerInfo",
    "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
    "Get-Volume | Format-Table DriveLetter, Size, FreeSpace",
    "Get-EventLog -LogName System -Newest 20"
]

for cmd in commands:
    result = await assistant.execute_command(session_id, cmd)
    print(f"✅ {cmd}: {result['success']}")
```

### Development Workflow
```python
# Git workflow automation
git_commands = [
    "git status",
    "git add .",
    "git commit -m 'Automated commit'",
    "git push origin main"
]

for cmd in git_commands:
    result = await assistant.execute_command(git_session.session_id, cmd)
    if not result['success']:
        print(f"❌ Git command failed: {result.get('error')}")
```

### File Organization
```python
# Organize downloads folder
await assistant.auto_sort_files(
    source_directory="C:\\Users\\Downloads",
    sort_criteria="by_type",
    destination_base="C:\\Users\\Downloads\\Sorted"
)

# Clean up temporary files
cleanup_ops = [
    {"type": "delete", "source": "C:\\Temp\\*.tmp"},
    {"type": "delete", "source": "C:\\Windows\\Temp\\*.log"}
]

await assistant.batch_file_operations(cleanup_ops)
```

## 🎮 PowerShell Tricks

### One-Liners
```python
# Get top 5 CPU processes
"Get-Process | Sort-Object CPU -Descending | Select-Object -First 5"

# Find large files
"Get-ChildItem -Path C:\\ -Recurse -File -ErrorAction SilentlyContinue | Where-Object {$_.Length -gt 100MB} | Sort-Object Length -Descending"

# Network diagnostics
"Test-Connection google.com; Get-NetAdapterStatistics; Get-NetTCPConnection | Where-Object {$_.State -eq 'Established'}"

# Service health check
"Get-Service | Where-Object {$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'} | Select-Object Name, Status, StartType"
```

### Advanced Scripts
```python
# System optimization script
optimization_script = """
# Clear temp files
Remove-Item $env:TEMP\\* -Force -Recurse -ErrorAction SilentlyContinue

# Optimize memory
$processes = Get-Process | Where-Object {$_.WorkingSet -gt 100MB}
$processes | Where-Object {$_.ProcessName -notlike '*system*'} | Stop-Process -Force

# Check disk health
Get-Volume | Where-Object {$_.DriveType -eq 'Fixed'} | Test-Volume
"""

await assistant.execute_command(session_id, optimization_script)
```

## 🔧 Integration with System Bridge

### Combined Usage
```python
# Use with System Bridge for full automation
from system_bridge import WindowsSystemBridge
from terminal_assistant import TerminalAssistant

# Initialize both components
bridge = WindowsSystemBridge()
assistant = TerminalAssistant()

# Create terminal session
session = await assistant.create_terminal_session("powershell")

# Optimize system
await bridge.optimize_system({"consciousness_level": 0.9})

# Run terminal commands
await assistant.execute_command(session.session_id, "Get-Service | Where-Object {$_.Status -eq 'Stopped'}")
```

## 📚 Command Reference

### PowerShell Commands
- **Get-Process**: List running processes
- **Get-Service**: List system services
- **Get-ChildItem**: List directory contents
- **Get-EventLog**: View event logs
- **Get-ComputerInfo**: System information
- **Get-Volume**: Disk information
- **Get-NetAdapter**: Network adapters
- **Set-ExecutionPolicy**: Script execution policy
- **Test-Connection**: Network connectivity
- **Clear-Host**: Clear screen

### CMD Commands
- **dir**: List directory contents
- **cd**: Change directory
- **copy**: Copy files
- **move**: Move files
- **del**: Delete files
- **ipconfig**: Network configuration
- **ping**: Test connectivity
- **tracert**: Trace route
- **tasklist**: List processes
- **taskkill**: End processes

### Git Commands
- **git status**: Repository status
- **git add**: Stage changes
- **git commit**: Commit changes
- **git push**: Push to remote
- **git pull**: Pull from remote
- **git log**: View history
- **git branch**: Manage branches

## 🚀 Performance Tips

### Optimization Strategies
1. **Use AGI optimization** for better command efficiency
2. **Batch operations** for multiple file operations
3. **Session reuse** to avoid creating multiple sessions
4. **Intelligent shortcuts** for frequently used commands
5. **Auto-completion** to reduce typing errors

### Best Practices
1. **Check elevation requirements** before execution
2. **Validate file paths** before operations
3. **Use error handling** for robust automation
4. **Monitor command history** for debugging
5. **Clean up sessions** when finished

## 🔮 Future Enhancements

### Planned Features
- **Voice Commands**: Natural language terminal control
- **GUI Integration**: Visual command builder
- **Cloud Terminal**: Remote terminal access
- **AI Assistant**: Conversational command interface
- **Macro Recording**: Record and replay command sequences

### Integration Possibilities
- **VS Code**: Terminal integration in IDE
- **Docker**: Container terminal management
- **WSL**: Windows Subsystem for Linux integration
- **Azure Cloud**: Cloud resource management

---

## 🏆 Summary

The Terminal Assistant provides:

💻 **Multi-terminal support** (PowerShell, CMD, Git)  
🧠 **AI-powered optimization** and auto-completion  
📁 **Intelligent file management** with auto-sorting  
⚡ **Custom shortcuts** and batch operations  
🛡️ **Security features** with elevation handling  
🔍 **Command intelligence** with pattern recognition  
📊 **Monitoring and analytics** for automation  

Transform your Windows terminal experience with Agent-97's intelligent automation! 🌟
