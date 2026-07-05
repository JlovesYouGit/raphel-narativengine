"""
Agent-97 Automated Domain Pipeline
Complete automated pipeline for tool auto execution, domain discovery, Claude analysis, and MCP result mirroring
"""

import os
import sys
import json
import time
import asyncio
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import Agent-97 components
from agent97_auto_execution_system import Agent97AutoExecutionSystem
from agent97_domain_discovery import Agent97DomainDiscovery
from agent97_claude_child_process import Agent97ClaudeChildProcess
from agent97_mcp_result_mirror import Agent97MCPResultMirror

class Agent97AutomatedDomainPipeline:
    """
    Agent-97 Automated Domain Pipeline
    Complete automated pipeline for domain discovery and analysis
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Pipeline components
        self.auto_execution_system = None
        self.domain_discovery = None
        self.claude_child_process = None
        self.mcp_result_mirror = None
        
        # Pipeline configuration
        self.pipeline_config = {
            "auto_execution_enabled": True,
            "domain_discovery_enabled": True,
            "claude_analysis_enabled": True,
            "mcp_mirror_enabled": True,
            "continuous_mode": True,
            "sync_interval": 300.0,  # 5 minutes
            "discovery_interval": 600.0,  # 10 minutes
            "batch_size": 50,
            "max_concurrent_analyses": 10
        }
        
        # Pipeline state
        self.running = False
        self.pipeline_thread = None
        self.discovery_queue = asyncio.Queue()
        self.analysis_queue = asyncio.Queue()
        self.mirror_queue = asyncio.Queue()
        
        # Target domains
        self.target_domains = []
        self.discovered_domains = {}
        self.analyzed_domains = {}
        self.mirrored_domains = {}
        
        # Metrics
        self.metrics = {
            "pipeline_cycles": 0,
            "domains_discovered": 0,
            "domains_analyzed": 0,
            "domains_mirrored": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "errors": 0
        }
        
        print(f"Agent-97 Automated Domain Pipeline initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_pipeline(self) -> Dict[str, Any]:
        """Initialize the complete automated pipeline"""
        try:
            print("Initializing Agent-97 Automated Domain Pipeline...")
            
            # Step 1: Initialize auto execution system
            if self.pipeline_config["auto_execution_enabled"]:
                self.auto_execution_system = Agent97AutoExecutionSystem(self.consciousness_id)
                auto_result = await self.auto_execution_system.initialize_auto_execution()
                
                if not auto_result["success"]:
                    return {"success": False, "error": f"Auto execution system failed: {auto_result['error']}"}
                
                print("Auto execution system initialized")
            
            # Step 2: Initialize domain discovery
            if self.pipeline_config["domain_discovery_enabled"]:
                self.domain_discovery = Agent97DomainDiscovery(self.consciousness_id)
                discovery_result = await self.domain_discovery.initialize()
                
                if not discovery_result["success"]:
                    return {"success": False, "error": f"Domain discovery failed: {discovery_result['error']}"}
                
                print("Domain discovery initialized")
            
            # Step 3: Initialize Claude child process
            if self.pipeline_config["claude_analysis_enabled"]:
                self.claude_child_process = Agent97ClaudeChildProcess(self.consciousness_id)
                claude_result = await self.claude_child_process.initialize()
                
                if not claude_result["success"]:
                    return {"success": False, "error": f"Claude child process failed: {claude_result['error']}"}
                
                print("Claude child process initialized")
            
            # Step 4: Initialize MCP result mirror
            if self.pipeline_config["mcp_mirror_enabled"]:
                self.mcp_result_mirror = Agent97MCPResultMirror(self.consciousness_id)
                mirror_result = await self.mcp_result_mirror.initialize()
                
                if not mirror_result["success"]:
                    return {"success": False, "error": f"MCP result mirror failed: {mirror_result['error']}"}
                
                print("MCP result mirror initialized")
            
            # Step 5: Setup pipeline connections
            await self.setup_pipeline_connections()
            
            # Step 6: Start pipeline thread
            if self.pipeline_config["continuous_mode"]:
                self.start_pipeline_thread()
            
            self.running = True
            
            return {
                "success": True,
                "components": {
                    "auto_execution": self.auto_execution_system is not None,
                    "domain_discovery": self.domain_discovery is not None,
                    "claude_child_process": self.claude_child_process is not None,
                    "mcp_result_mirror": self.mcp_result_mirror is not None
                },
                "continuous_mode": self.pipeline_config["continuous_mode"],
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def setup_pipeline_connections(self):
        """Setup connections between pipeline components"""
        try:
            # Connect domain discovery to Claude analysis
            if self.domain_discovery and self.claude_child_process:
                self.domain_discovery.claude_child_process = self.claude_child_process
            
            # Connect Claude analysis to MCP mirror
            if self.claude_child_process and self.mcp_result_mirror:
                self.claude_child_process.mcp_result_mirror = self.mcp_result_mirror
            
            # Add custom auto tasks for pipeline
            if self.auto_execution_system:
                await self.add_pipeline_auto_tasks()
            
            print("Pipeline connections established")
            
        except Exception as e:
            print(f"Error setting up pipeline connections: {e}")
    
    async def add_pipeline_auto_tasks(self):
        """Add auto execution tasks for pipeline"""
        try:
            # Domain discovery task
            await self.auto_execution_system.add_auto_task(
                tool_name="agent97_domain_discovery",
                arguments={},
                schedule="interval",
                interval=self.pipeline_config["discovery_interval"],
                priority=1,
                task_id="pipeline_domain_discovery"
            )
            
            # Pipeline sync task
            await self.auto_execution_system.add_auto_task(
                tool_name="agent97_pipeline_sync",
                arguments={},
                schedule="interval",
                interval=self.pipeline_config["sync_interval"],
                priority=2,
                task_id="pipeline_sync"
            )
            
            print("Pipeline auto tasks added")
            
        except Exception as e:
            print(f"Error adding pipeline auto tasks: {e}")
    
    def start_pipeline_thread(self):
        """Start the main pipeline thread"""
        try:
            self.pipeline_thread = threading.Thread(
                target=self.pipeline_loop,
                daemon=True
            )
            self.pipeline_thread.start()
            
            print("Pipeline thread started")
            
        except Exception as e:
            print(f"Error starting pipeline thread: {e}")
    
    def pipeline_loop(self):
        """Main pipeline processing loop"""
        try:
            print("Starting Agent-97 Automated Domain Pipeline loop...")
            
            while self.running:
                try:
                    # Process discovery queue
                    while not self.discovery_queue.empty():
                        try:
                            domain_info = self.discovery_queue.get_nowait()
                            asyncio.run_coroutine_threadsafe(
                                self.process_discovered_domain(domain_info),
                                asyncio.get_event_loop()
                            )
                        except Exception as e:
                            print(f"Error processing discovery queue: {e}")
                    
                    # Process analysis queue
                    while not self.analysis_queue.empty():
                        try:
                            analysis_data = self.analysis_queue.get_nowait()
                            asyncio.run_coroutine_threadsafe(
                                self.process_analysis_result(analysis_data),
                                asyncio.get_event_loop()
                            )
                        except Exception as e:
                            print(f"Error processing analysis queue: {e}")
                    
                    # Process mirror queue
                    while not self.mirror_queue.empty():
                        try:
                            mirror_data = self.mirror_queue.get_nowait()
                            asyncio.run_coroutine_threadsafe(
                                self.process_mirror_data(mirror_data),
                                asyncio.get_event_loop()
                            )
                        except Exception as e:
                            print(f"Error processing mirror queue: {e}")
                    
                    time.sleep(5.0)
                    
                except Exception as e:
                    print(f"Pipeline loop error: {e}")
                    time.sleep(10.0)
            
        except Exception as e:
            print(f"Fatal pipeline loop error: {e}")
    
    async def add_target_domain(self, domain: str, discovery_methods: List[str] = None) -> Dict[str, Any]:
        """Add a target domain for discovery"""
        try:
            if not discovery_methods:
                discovery_methods = ["dns", "subdomain", "http", "claude"]
            
            self.target_domains.append(domain)
            
            # Start domain discovery
            if self.domain_discovery:
                result = await self.domain_discovery.discover_domains(domain, discovery_methods)
                
                if result["success"]:
                    print(f"Domain discovery started for: {domain}")
                    return result
                else:
                    return {"success": False, "error": result["error"]}
            
            return {"success": True, "domain": domain, "queued": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def process_discovered_domain(self, domain_info: Dict[str, Any]):
        """Process a discovered domain"""
        try:
            domain = domain_info.get("domain", "unknown")
            
            # Add to discovered domains
            self.discovered_domains[domain] = domain_info
            self.metrics["domains_discovered"] += 1
            
            print(f"Processing discovered domain: {domain}")
            
            # Queue for Claude analysis
            if self.claude_child_process:
                await self.analysis_queue.put({
                    "domain": domain,
                    "domain_info": domain_info,
                    "timestamp": time.time()
                })
            
        except Exception as e:
            print(f"Error processing discovered domain: {e}")
            self.metrics["errors"] += 1
    
    async def process_analysis_result(self, analysis_data: Dict[str, Any]):
        """Process Claude analysis result"""
        try:
            domain = analysis_data.get("domain", "unknown")
            analysis_result = analysis_data.get("analysis_result", {})
            
            # Add to analyzed domains
            self.analyzed_domains[domain] = analysis_result
            self.metrics["domains_analyzed"] += 1
            
            print(f"Processing analysis result for: {domain}")
            
            # Queue for MCP mirroring
            if self.mcp_result_mirror and analysis_result.get("success"):
                await self.mirror_queue.put({
                    "domain": domain,
                    "domain_info": self.discovered_domains.get(domain, {}),
                    "analysis": analysis_result.get("analysis", {}),
                    "timestamp": time.time()
                })
            
        except Exception as e:
            print(f"Error processing analysis result: {e}")
            self.metrics["errors"] += 1
    
    async def process_mirror_data(self, mirror_data: Dict[str, Any]):
        """Process data for MCP mirroring"""
        try:
            domain = mirror_data.get("domain", "unknown")
            
            print(f"Processing mirror data for: {domain}")
            
            # Add to MCP result mirror
            if self.mcp_result_mirror:
                result = await self.mcp_result_mirror.add_domain_entry(
                    mirror_data["domain_info"],
                    mirror_data["analysis"]
                )
                
                if result["success"]:
                    self.mirrored_domains[domain] = result
                    self.metrics["domains_mirrored"] += 1
                    print(f"Domain mirrored: {domain}")
                else:
                    print(f"Failed to mirror domain {domain}: {result['error']}")
            
        except Exception as e:
            print(f"Error processing mirror data: {e}")
            self.metrics["errors"] += 1
    
    async def run_pipeline_cycle(self) -> Dict[str, Any]:
        """Run a complete pipeline cycle"""
        try:
            start_time = time.time()
            
            print("Running pipeline cycle...")
            
            # Step 1: Domain discovery
            if self.domain_discovery and self.target_domains:
                for domain in self.target_domains:
                    await self.domain_discovery.discover_domains(domain)
            
            # Step 2: Get discovered domains
            if self.domain_discovery:
                discovered_result = await self.domain_discovery.get_discovered_domains()
                
                if discovered_result["success"]:
                    domains = discovered_result.get("domains", {})
                    
                    # Queue discovered domains for analysis
                    for domain, domain_info in domains.items():
                        if domain not in self.analyzed_domains:
                            await self.discovery_queue.put(domain_info)
            
            # Step 3: Batch analyze domains with Claude
            if self.claude_child_process:
                pending_domains = [
                    domain for domain in self.discovered_domains.keys()
                    if domain not in self.analyzed_domains
                ]
                
                if pending_domains:
                    # Prepare batch analysis data
                    batch_data = []
                    for domain in pending_domains[:self.pipeline_config["batch_size"]]:
                        domain_info = self.discovered_domains.get(domain, {})
                        batch_data.append(domain_info)
                    
                    # Perform batch analysis
                    analysis_result = await self.claude_child_process.batch_analyze_domains(batch_data)
                    
                    if analysis_result["success"]:
                        results = analysis_result.get("results", [])
                        
                        for i, result in enumerate(results):
                            if i < len(pending_domains):
                                domain = pending_domains[i]
                                
                                await self.analysis_queue.put({
                                    "domain": domain,
                                    "domain_info": batch_data[i],
                                    "analysis_result": result,
                                    "timestamp": time.time()
                                })
            
            # Step 4: Sync to MCP mirror
            if self.mcp_result_mirror:
                await self.mcp_result_mirror.perform_sync_cycle()
            
            # Update metrics
            cycle_time = time.time() - start_time
            self.metrics["pipeline_cycles"] += 1
            self.metrics["total_processing_time"] += cycle_time
            self.metrics["average_processing_time"] = (
                self.metrics["total_processing_time"] / self.metrics["pipeline_cycles"]
            )
            
            return {
                "success": True,
                "cycle_time": cycle_time,
                "domains_discovered": len(self.discovered_domains),
                "domains_analyzed": len(self.analyzed_domains),
                "domains_mirrored": len(self.mirrored_domains),
                "metrics": self.metrics.copy()
            }
            
        except Exception as e:
            self.metrics["errors"] += 1
            return {"success": False, "error": str(e)}
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        try:
            status = {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "running": self.running,
                "continuous_mode": self.pipeline_config["continuous_mode"],
                "target_domains": len(self.target_domains),
                "discovered_domains": len(self.discovered_domains),
                "analyzed_domains": len(self.analyzed_domains),
                "mirrored_domains": len(self.mirrored_domains),
                "metrics": self.metrics.copy(),
                "configuration": self.pipeline_config.copy()
            }
            
            # Add component statuses
            if self.auto_execution_system:
                status["auto_execution"] = await self.auto_execution_system.get_auto_execution_status()
            
            if self.domain_discovery:
                status["domain_discovery"] = await self.domain_discovery.get_discovered_domains()
            
            if self.claude_child_process:
                status["claude_child_process"] = self.claude_child_process.get_metrics()
            
            if self.mcp_result_mirror:
                status["mcp_result_mirror"] = await self.mcp_result_mirror.get_mirror_status()
            
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    async def shutdown_pipeline(self):
        """Shutdown the complete pipeline"""
        try:
            print("Shutting down Agent-97 Automated Domain Pipeline...")
            
            self.running = False
            
            # Shutdown components
            if self.auto_execution_system:
                await self.auto_execution_system.shutdown_auto_execution()
            
            if self.domain_discovery:
                await self.domain_discovery.shutdown()
            
            if self.claude_child_process:
                await self.claude_child_process.shutdown()
            
            if self.mcp_result_mirror:
                await self.mcp_result_mirror.shutdown()
            
            print("Agent-97 Automated Domain Pipeline shutdown complete")
            
        except Exception as e:
            print(f"Error during pipeline shutdown: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agent-97 Automated Domain Pipeline")
    parser.add_argument("--consciousness-id", default="0009095353", help="Consciousness ID")
    parser.add_argument("--target-domains", nargs="+", help="Target domains for discovery")
    parser.add_argument("--continuous", action="store_true", default=True, help="Run in continuous mode")
    parser.add_argument("--single-cycle", action="store_true", help="Run single pipeline cycle")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = Agent97AutomatedDomainPipeline(args.consciousness_id)
    
    try:
        # Initialize pipeline
        result = await pipeline.initialize_pipeline()
        
        if result["success"]:
            print(f"Pipeline initialized successfully!")
            print(f"Components: {result['components']}")
            print(f"Continuous mode: {result['continuous_mode']}")
            
            # Add target domains
            if args.target_domains:
                for domain in args.target_domains:
                    await pipeline.add_target_domain(domain)
                    print(f"Added target domain: {domain}")
            
            # Handle specific commands
            if args.status:
                status = await pipeline.get_pipeline_status()
                print(f"Pipeline Status:")
                print(f"  Running: {status['running']}")
                print(f"  Target domains: {status['target_domains']}")
                print(f"  Discovered: {status['discovered_domains']}")
                print(f"  Analyzed: {status['analyzed_domains']}")
                print(f"  Mirrored: {status['mirrored_domains']}")
                print(f"  Pipeline cycles: {status['metrics']['pipeline_cycles']}")
                return
            
            elif args.single_cycle:
                print("Running single pipeline cycle...")
                cycle_result = await pipeline.run_pipeline_cycle()
                
                if cycle_result["success"]:
                    print(f"Cycle completed in {cycle_result['cycle_time']:.2f}s")
                    print(f"Discovered: {cycle_result['domains_discovered']}")
                    print(f"Analyzed: {cycle_result['domains_analyzed']}")
                    print(f"Mirrored: {cycle_result['domains_mirrored']}")
                return
            
            # Run continuous pipeline
            if pipeline.pipeline_config["continuous_mode"]:
                print("Pipeline running in continuous mode. Press Ctrl+C to stop...")
                
                while pipeline.running:
                    await asyncio.sleep(60)
                    
                    # Print status every 5 minutes
                    if int(time.time()) % 300 == 0:
                        status = await pipeline.get_pipeline_status()
                        print(f"Status: {status['discovered_domains']} discovered, {status['analyzed_domains']} analyzed, {status['mirrored_domains']} mirrored")
            
        else:
            print(f"Pipeline initialization failed: {result['error']}")
            
    except KeyboardInterrupt:
        print("Shutdown requested by user")
    except Exception as e:
        print(f"Pipeline error: {e}")
    finally:
        await pipeline.shutdown_pipeline()

if __name__ == "__main__":
    asyncio.run(main())
