#!/usr/bin/env python3
"""
Simple Agent Server - Working Version without asyncio conflicts
Basic FastAPI server that demonstrates agent platform functionality
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install fastapi pydantic")
    exit(1)

# Data Models
class Agent(BaseModel):
    id: str
    name: str
    status: str = "idle"
    created_at: datetime = Field(default_factory=datetime.now)
    tasks_completed: int = 0

class Task(BaseModel):
    id: str
    agent_id: str
    description: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    result: Dict[str, Any] = Field(default_factory=dict)

# Simple Agent Platform
class SimpleAgentServer:
    """Simple FastAPI-based agent server"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.app = FastAPI(
            title="Simple Agent Platform 2026",
            description="Working agent platform without asyncio conflicts"
        )
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.get("/")
        async def root():
            return {
                "message": "Simple Agent Platform 2026",
                "version": "1.0.0",
                "agents": len(self.agents),
                "tasks": len(self.tasks),
                "endpoints": {
                    "agents": "/agents",
                    "tasks": "/agents/{agent_id}/tasks",
                    "status": "/status"
                }
            }
        
        @self.app.post("/agents")
        async def create_agent(agent_data: Dict[str, Any]):
            """Create a new agent"""
            agent_id = str(uuid.uuid4())
            agent = Agent(
                id=agent_id,
                name=agent_data.get("name", "Unnamed Agent"),
                status="active"
            )
            
            self.agents[agent_id] = agent
            
            return {
                "agent_id": agent_id,
                "name": agent.name,
                "status": "created",
                "message": f"Agent '{agent.name}' created successfully",
                "created_at": agent.created_at.isoformat()
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
                ],
                "total": len(self.agents)
            }
        
        @self.app.post("/agents/{agent_id}/tasks")
        async def create_task(agent_id: str, task_data: Dict[str, Any]):
            """Create a task for an agent"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                agent_id=agent_id,
                description=task_data.get("description", "No description"),
                status="completed"  # Auto-complete for demo
            )
            
            self.tasks[task_id] = task
            
            # Update agent task count
            agent = self.agents[agent_id]
            agent.tasks_completed += 1
            
            return {
                "task_id": task_id,
                "agent_id": agent_id,
                "agent_name": agent.name,
                "description": task.description,
                "status": task.status,
                "message": "Task created and completed successfully",
                "result": task.result,
                "created_at": task.created_at.isoformat()
            }
        
        @self.app.get("/agents/{agent_id}/tasks")
        async def list_agent_tasks(agent_id: str):
            """List tasks for an agent"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
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
                ],
                "total_tasks": len(agent_tasks)
            }
        
        @self.app.get("/status")
        async def platform_status():
            """Get platform status"""
            active_agents = len([a for a in self.agents.values() if a.status == "active"])
            completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
            
            return {
                "platform": "Simple Agent Platform 2026",
                "status": "running",
                "agents": {
                    "total": len(self.agents),
                    "active": active_agents,
                    "idle": len(self.agents) - active_agents
                },
                "tasks": {
                    "total": len(self.tasks),
                    "completed": completed_tasks,
                    "pending": len(self.tasks) - completed_tasks
                },
                "uptime": "Server is running"
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }

def main():
    """Main function - run the server"""
    print("🚀 Starting Simple Agent Platform 2026")
    print("=" * 50)
    
    server = SimpleAgentServer()
    
    # Create demo data
    demo_agent_id = str(uuid.uuid4())
    demo_agent = Agent(
        id=demo_agent_id,
        name="Demo Agent",
        status="active"
    )
    server.agents[demo_agent_id] = demo_agent
    
    demo_task_id = str(uuid.uuid4())
    demo_task = Task(
        id=demo_task_id,
        agent_id=demo_agent_id,
        description="Sample task: Process data and generate report",
        status="completed"
    )
    server.tasks[demo_task_id] = demo_task
    
    print(f"✅ Created demo agent: {demo_agent_id}")
    print(f"✅ Created demo task: {demo_task_id}")
    print(f"🌐 Server starting on http://localhost:8000")
    print(f"📊 Demo agent: http://localhost:8000/agents/{demo_agent_id}")
    print(f"📋 Demo tasks: http://localhost:8000/agents/{demo_agent_id}/tasks")
    
    # Run with uvicorn
    try:
        import uvicorn
        uvicorn.run(server.app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError:
        print("❌ uvicorn not found. Install with: pip install uvicorn")
        print("🔄 Falling back to basic server...")
        import threading
        import time
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        
        def run_server():
            handler = SimpleHTTPRequestHandler
            httpd = HTTPServer(('0.0.0.0', 8000), handler)
            print(f"🌐 Basic server running on http://localhost:8000")
            httpd.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
