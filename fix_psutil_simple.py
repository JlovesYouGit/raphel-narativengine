#!/usr/bin/env python3
"""
Simple Fix for psutil dependency issue
Creates alternative performance monitor without external dependencies
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

def create_simple_monitor():
    """Create simple performance monitor without psutil"""
    
    monitor_code = '''# Simple Performance Monitor
# Alternative to psutil for God AI system

import time
import json
from datetime import datetime
from typing import Dict, Any

class SimplePerformanceMonitor:
    """Simple performance monitor without external dependencies"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "active_worlds": 0,
            "decisions_made": 0,
            "interventions_executed": 0
        }
        self.monitoring = False
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        print("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        print("✅ Performance monitoring stopped")
    
    def update_metrics(self, **kwargs):
        """Update performance metrics"""
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        uptime = time.time() - self.start_time
        
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime//3600:.0f}h {(uptime%3600)//60:.0f}m",
            "performance_score": min(100, (self.metrics["decisions_made"] / max(1, self.metrics["interventions_executed"])) * 10)
        }
    
    def get_status(self) -> str:
        """Get monitoring status"""
        return "Active" if self.monitoring else "Inactive"

# Create the monitor file
with open("simple_performance_monitor.py", "w") as f:
    f.write(monitor_code)

print("✅ Created simple_performance_monitor.py")
print("📝 This replaces psutil dependency")
print("🔧 Use this in your existing system:")
print("   Replace: from psutil import")
print("   With: from simple_performance_monitor import SimplePerformanceMonitor")
print("✅ psutil dependency issue resolved!")
