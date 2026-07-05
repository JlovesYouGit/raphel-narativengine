#!/usr/bin/env python3
"""
Minimal Agent Platform 2026 - Working Version
Stripped-down version that actually works
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid

# Only essential imports
try:
    from fastapi import FastAPI
    import uvicorn
    from pydantic import BaseModel, Field
except ImportError as e:
    print(f"Missing essential dependencies: {e}")
    print("Install with: pip install fastapi uvicorn pydantic")
    sys.exit(1)

@dataclass
class SimpleAgent:
    """Simple agent definition"""
    id: str
    name: str
    status: str = "idle"
    created_at: datetime = field(default_factory=datetime.now)
    tasks_completed: int = 0

@dataclass
class AgentTask:
    """Simple task definition"""
    id: str
    agent_id: str
    description: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    result: Optional[Dict[str, Any]] = None

class MinimalAgentPlatform:
    """Minimal working agent platform"""
    
    def __init__(self):
        self.agents: Dict[str, SimpleAgent] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.app = FastAPI(title="Minimal Agent Platform 2026")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup basic FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "Minimal Agent Platform 2026",
                "agents": len(self.agents),
                "tasks": len(self.tasks),
                "status": "running"
            }
        
        @self.app.post("/agents")
        async def create_agent_route(agent_data: Dict[str, Any]):
            """Create a new agent"""
            agent_id = str(uuid.uuid4())
            agent = SimpleAgent(
                id=agent_id,
                name=agent_data.get("name", "Unnamed Agent"),
                status="active"
            )
            
            self.agents[agent_id] = agent
            
            return {
                "agent_id": agent_id,
                "name": agent.name,
                "status": "created",
                "message": f"Agent '{agent.name}' created successfully"
            }
        
        @self.app.get("/agents")
        async def list_agents():
            """List all agents"""
            return {
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "status": agent.status,
                        "created_at": agent.created_at.isoformat(),
                        "tasks_completed": agent.tasks_completed
                    }
                    for agent in self.agents.values()
                ]
            }
        
        @self.app.post("/agents/{agent_id}/tasks")
        async def create_task(agent_id: str, task_data: Dict[str, Any]):
            """Create a task for an agent"""
            if agent_id not in self.agents:
                return {"error": "Agent not found"}
            
            task_id = str(uuid.uuid4())
            task = AgentTask(
                id=task_id,
                agent_id=agent_id,
                description=task_data.get("description", "No description"),
                status="pending"
            )
            
            self.tasks[task_id] = task
            
            # Simulate task execution
            await self.execute_task(task_id)
            
            return {
                "task_id": task_id,
                "agent_id": agent_id,
                "description": task.description,
                "status": task.status,
                "message": "Task created and executed"
            }
        
        @self.app.get("/agents/{agent_id}/tasks")
        async def list_agent_tasks(agent_id: str):
            """List tasks for an agent"""
            if agent_id not in self.agents:
                return {"error": "Agent not found"}
            
            agent_tasks = [
                task for task in self.tasks.values() 
                if task.agent_id == agent_id
            ]
            
            return {
                "agent_id": agent_id,
                "tasks": [
                    {
                        "id": task.id,
                        "description": task.description,
                        "status": task.status,
                        "created_at": task.created_at.isoformat(),
                        "result": task.result
                    }
                    for task in agent_tasks
                ]
            }
        
        @self.app.get("/status")
        async def platform_status():
            """Get platform status"""
            return {
                "platform": "Minimal Agent Platform 2026",
                "status": "running",
                "agents": {
                    "total": len(self.agents),
                    "active": len([a for a in self.agents.values() if a.status == "active"]),
                    "idle": len([a for a in self.agents.values() if a.status == "idle"])
                },
                "tasks": {
                    "total": len(self.tasks),
                    "pending": len([t for t in self.tasks.values() if t.status == "pending"]),
                    "completed": len([t for t in self.tasks.values() if t.status == "completed"])
                }
            }
    
    async def execute_task(self, task_id: str):
        """Simulate task execution"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        agent = self.agents.get(task.agent_id)
        
        if not agent:
            task.status = "failed"
            task.result = {"error": "Agent not found"}
            return
        
        # Update agent status
        agent.status = "working"
        task.status = "executing"
        
        # Simulate work
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Complete task
        task.status = "completed"
        task.result = {
            "message": f"Task '{task.description}' completed successfully",
            "execution_time": "0.1s",
            "agent": agent.name
        }
        
        agent.status = "idle"
        agent.tasks_completed += 1
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the FastAPI server"""
        print(f"🚀 Starting Minimal Agent Platform 2026")
        print(f"📍 Server: http://{host}:{port}")
        print(f"🤖 Agents: {len(self.agents)}")
        print(f"📋 Tasks: {len(self.tasks)}")
        
        await uvicorn.run(self.app, host=host, port=port)

async def main():
    """Main function"""
    platform = MinimalAgentPlatform()
    
    # Create a demo agent using the class method
    agent_id = str(uuid.uuid4())
    demo_agent = SimpleAgent(
        id=agent_id,
        name="Demo Agent",
        status="active"
    )
    platform.agents[agent_id] = demo_agent
    print(f"✅ Created demo agent: {agent_id}")
    
    # Create a demo task
    task_id = str(uuid.uuid4())
    demo_task = AgentTask(
        id=task_id,
        agent_id=agent_id,
        description="Test task execution",
        status="completed"
    )
    platform.tasks[task_id] = demo_task
    print(f"✅ Created demo task: {task_id}")
    
    # Start server
    await platform.start_server()

if __name__ == "__main__":
    asyncio.run(main())
