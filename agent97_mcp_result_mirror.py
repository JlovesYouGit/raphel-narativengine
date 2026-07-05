"""
Agent-97 MCP Result Mirror
Integrates with https://github.com/JlovesYouGit/MCPRESULTListmirror.git for domain entry passing
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import git
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import requests
from datetime import datetime

@dataclass
class DomainEntry:
    """Domain entry for MCP result mirror"""
    domain: str
    analysis: Dict[str, Any]
    timestamp: float
    consciousness_id: str
    session_nonce: str
    status: str = "pending"  # pending, synced, failed
    git_commit: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Agent97MCPResultMirror:
    """
    Agent-97 MCP Result Mirror
    Integrates with MCPRESULTListmirror repository for domain entry passing
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Repository configuration
        self.repo_config = {
            "url": "https://github.com/JlovesYouGit/MCPRESULTListmirror.git",
            "local_path": "./MCPRESULTListmirror",
            "branch": "main",
            "auto_commit": True,
            "auto_push": True,
            "sync_interval": 300.0  # 5 minutes
        }
        
        # Mirror state
        self.repository = None
        self.local_repo_path = None
        self.domain_entries = {}  # domain -> DomainEntry
        self.pending_entries = []
        self.sync_queue = asyncio.Queue()
        
        # File structure
        self.domain_data_file = "domains.json"
        self.analysis_dir = "analyses"
        self.metadata_dir = "metadata"
        
        # Synchronization state
        self.running = False
        self.sync_thread = None
        self.last_sync_time = 0.0
        
        # Metrics
        self.metrics = {
            "domains_added": 0,
            "domains_synced": 0,
            "sync_cycles": 0,
            "commits_made": 0,
            "pushes_made": 0,
            "sync_errors": 0,
            "total_sync_time": 0.0,
            "average_sync_time": 0.0
        }
        
        print(f"Agent-97 MCP Result Mirror initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP result mirror"""
        try:
            print("Initializing Agent-97 MCP Result Mirror...")
            
            # Step 1: Clone or update repository
            await self.setup_repository()
            
            # Step 2: Initialize file structure
            await self.initialize_file_structure()
            
            # Step 3: Load existing domain entries
            await self.load_existing_entries()
            
            # Step 4: Start synchronization thread
            self.start_synchronization_thread()
            
            self.running = True
            
            return {
                "success": True,
                "repository_url": self.repo_config["url"],
                "local_path": self.local_repo_path,
                "existing_entries": len(self.domain_entries),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def setup_repository(self):
        """Setup the git repository using git clone command"""
        try:
            repo_path = Path(self.repo_config["local_path"])
            
            # Remove existing directory if it exists to ensure clean clone
            if repo_path.exists():
                print(f"Removing existing repository: {repo_path}")
                import shutil
                shutil.rmtree(repo_path)
            
            # Use git clone command to clone the repository
            print(f"Cloning repository using git clone: {self.repo_config['url']}")
            
            # Execute git clone command
            clone_cmd = ["git", "clone", self.repo_config["url"], str(repo_path)]
            
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            # Initialize git repository object
            self.repository = git.Repo(repo_path)
            self.local_repo_path = repo_path
            
            # Checkout correct branch
            if self.repository.active_branch.name != self.repo_config["branch"]:
                self.repository.git.checkout(self.repo_config["branch"])
            
            print(f"Repository cloned successfully: {repo_path}")
            print(f"Active branch: {self.repository.active_branch.name}")
            print(f"Latest commit: {self.repository.head.commit.hexsha[:8]}")
            
        except subprocess.TimeoutExpired:
            raise Exception("Git clone timed out")
        except Exception as e:
            print(f"Error setting up repository with git clone: {e}")
            raise
    
    async def initialize_file_structure(self):
        """Initialize file structure in repository"""
        try:
            if not self.local_repo_path:
                raise Exception("Repository not initialized")
            
            repo_path = Path(self.local_repo_path)
            
            # Create directories
            (repo_path / self.analysis_dir).mkdir(exist_ok=True)
            (repo_path / self.metadata_dir).mkdir(exist_ok=True)
            
            # Create domains.json if it doesn't exist
            domains_file = repo_path / self.domain_data_file
            if not domains_file.exists():
                initial_data = {
                    "version": "1.0.0",
                    "created_at": time.time(),
                    "consciousness_id": self.consciousness_id,
                    "session_nonce": self.session_nonce,
                    "domains": {}
                }
                
                with open(domains_file, 'w') as f:
                    json.dump(initial_data, f, indent=2)
                
                # Initial commit
                self.repository.index.add([self.domain_data_file])
                self.repository.index.commit("Initial domains.json setup")
            
            print("File structure initialized")
            
        except Exception as e:
            print(f"Error initializing file structure: {e}")
            raise
    
    async def load_existing_entries(self):
        """Load existing domain entries from repository"""
        try:
            domains_file = Path(self.local_repo_path) / self.domain_data_file
            
            if domains_file.exists():
                with open(domains_file, 'r') as f:
                    data = json.load(f)
                
                domains = data.get("domains", {})
                
                for domain, entry_data in domains.items():
                    domain_entry = DomainEntry(
                        domain=domain,
                        analysis=entry_data.get("analysis", {}),
                        timestamp=entry_data.get("timestamp", time.time()),
                        consciousness_id=entry_data.get("consciousness_id", self.consciousness_id),
                        session_nonce=entry_data.get("session_nonce", ""),
                        status=entry_data.get("status", "synced"),
                        git_commit=entry_data.get("git_commit"),
                        metadata=entry_data.get("metadata", {})
                    )
                    
                    self.domain_entries[domain] = domain_entry
                
                print(f"Loaded {len(self.domain_entries)} existing domain entries")
            
        except Exception as e:
            print(f"Error loading existing entries: {e}")
    
    def start_synchronization_thread(self):
        """Start synchronization thread"""
        try:
            self.sync_thread = threading.Thread(
                target=self.synchronization_loop,
                daemon=True
            )
            self.sync_thread.start()
            
            print("Synchronization thread started")
            
        except Exception as e:
            print(f"Error starting synchronization thread: {e}")
    
    async def add_domain_entry(self, domain: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new domain entry to the mirror"""
        try:
            domain_name = domain.get("domain", "unknown")
            
            # Create domain entry
            domain_entry = DomainEntry(
                domain=domain_name,
                analysis=analysis,
                timestamp=time.time(),
                consciousness_id=self.consciousness_id,
                session_nonce=self.session_nonce,
                status="pending",
                metadata={
                    "source": domain.get("source", "unknown"),
                    "discovery_method": domain.get("discovery_method", "unknown"),
                    "added_by": "Agent-97 MCP Result Mirror"
                }
            )
            
            # Add to entries
            self.domain_entries[domain_name] = domain_entry
            self.pending_entries.append(domain_entry)
            
            # Add to sync queue
            await self.sync_queue.put(domain_entry)
            
            self.metrics["domains_added"] += 1
            
            print(f"Domain entry added: {domain_name}")
            
            return {
                "success": True,
                "domain": domain_name,
                "status": "pending",
                "entry_id": f"{domain_name}_{int(time.time())}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def batch_add_domain_entries(self, domains_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add multiple domain entries in batch"""
        try:
            results = []
            
            for item in domains_analyses:
                domain = item.get("domain", {})
                analysis = item.get("analysis", {})
                
                result = await self.add_domain_entry(domain, analysis)
                results.append(result)
            
            successful = sum(1 for r in results if r["success"])
            
            return {
                "success": True,
                "total_entries": len(domains_analyses),
                "successful_entries": successful,
                "failed_entries": len(domains_analyses) - successful,
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def synchronization_loop(self):
        """Main synchronization loop"""
        try:
            print("Starting MCP result mirror synchronization loop...")
            
            while self.running:
                try:
                    # Process sync queue
                    while not self.sync_queue.empty():
                        try:
                            domain_entry = self.sync_queue.get_nowait()
                            
                            # Sync to repository
                            asyncio.run_coroutine_threadsafe(
                                self.sync_domain_entry(domain_entry),
                                asyncio.get_event_loop()
                            )
                            
                        except Exception as e:
                            print(f"Error processing sync queue item: {e}")
                    
                    # Periodic sync cycle
                    current_time = time.time()
                    if current_time - self.last_sync_time >= self.repo_config["sync_interval"]:
                        asyncio.run_coroutine_threadsafe(
                            self.perform_sync_cycle(),
                            asyncio.get_event_loop()
                        )
                        self.last_sync_time = current_time
                    
                    time.sleep(10.0)
                    
                except Exception as e:
                    print(f"Synchronization loop error: {e}")
                    time.sleep(30.0)
            
        except Exception as e:
            print(f"Fatal synchronization loop error: {e}")
    
    async def sync_domain_entry(self, domain_entry: DomainEntry):
        """Sync a single domain entry to repository"""
        try:
            start_time = time.time()
            
            # Update domains.json
            await self.update_domains_file(domain_entry)
            
            # Create analysis file
            await self.create_analysis_file(domain_entry)
            
            # Create metadata file
            await self.create_metadata_file(domain_entry)
            
            # Commit changes
            if self.repo_config["auto_commit"]:
                commit_hash = await self.commit_changes(domain_entry)
                domain_entry.git_commit = commit_hash
            
            # Update status
            domain_entry.status = "synced"
            
            # Update metrics
            sync_time = time.time() - start_time
            self.metrics["domains_synced"] += 1
            self.metrics["total_sync_time"] += sync_time
            self.metrics["average_sync_time"] = (
                self.metrics["total_sync_time"] / self.metrics["domains_synced"]
            )
            
            print(f"Domain entry synced: {domain_entry.domain}")
            
        except Exception as e:
            domain_entry.status = "failed"
            self.metrics["sync_errors"] += 1
            print(f"Error syncing domain entry {domain_entry.domain}: {e}")
    
    async def update_domains_file(self, domain_entry: DomainEntry):
        """Update the main domains.json file"""
        try:
            domains_file = Path(self.local_repo_path) / self.domain_data_file
            
            # Read existing data
            with open(domains_file, 'r') as f:
                data = json.load(f)
            
            # Update domain entry
            data["domains"][domain_entry.domain] = {
                "analysis": domain_entry.analysis,
                "timestamp": domain_entry.timestamp,
                "consciousness_id": domain_entry.consciousness_id,
                "session_nonce": domain_entry.session_nonce,
                "status": domain_entry.status,
                "git_commit": domain_entry.git_commit,
                "metadata": domain_entry.metadata
            }
            
            # Update last modified
            data["last_modified"] = time.time()
            
            # Write back
            with open(domains_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Stage for commit
            self.repository.index.add([self.domain_data_file])
            
        except Exception as e:
            print(f"Error updating domains file: {e}")
            raise
    
    async def create_analysis_file(self, domain_entry: DomainEntry):
        """Create individual analysis file"""
        try:
            analysis_file = Path(self.local_repo_path) / self.analysis_dir / f"{domain_entry.domain}.json"
            
            analysis_data = {
                "domain": domain_entry.domain,
                "analysis": domain_entry.analysis,
                "timestamp": domain_entry.timestamp,
                "consciousness_id": domain_entry.consciousness_id,
                "session_nonce": domain_entry.session_nonce,
                "metadata": domain_entry.metadata
            }
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            # Stage for commit
            self.repository.index.add([str(analysis_file.relative_to(self.local_repo_path))])
            
        except Exception as e:
            print(f"Error creating analysis file: {e}")
            raise
    
    async def create_metadata_file(self, domain_entry: DomainEntry):
        """Create metadata file for domain"""
        try:
            metadata_file = Path(self.local_repo_path) / self.metadata_dir / f"{domain_entry.domain}_metadata.json"
            
            metadata_data = {
                "domain": domain_entry.domain,
                "discovery_info": {
                    "source": domain_entry.metadata.get("source", "unknown"),
                    "discovery_method": domain_entry.metadata.get("discovery_method", "unknown"),
                    "discovery_timestamp": domain_entry.timestamp
                },
                "analysis_info": {
                    "risk_level": domain_entry.analysis.get("risk_level", "unknown"),
                    "category": domain_entry.analysis.get("category", "unknown"),
                    "confidence": domain_entry.analysis.get("confidence", 0.0),
                    "technologies": domain_entry.analysis.get("technologies", [])
                },
                "sync_info": {
                    "status": domain_entry.status,
                    "git_commit": domain_entry.git_commit,
                    "sync_timestamp": time.time(),
                    "consciousness_id": domain_entry.consciousness_id,
                    "session_nonce": domain_entry.session_nonce
                }
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_data, f, indent=2)
            
            # Stage for commit
            self.repository.index.add([str(metadata_file.relative_to(self.local_repo_path))])
            
        except Exception as e:
            print(f"Error creating metadata file: {e}")
            raise
    
    async def commit_changes(self, domain_entry: DomainEntry) -> str:
        """Commit changes to repository"""
        try:
            # Create commit message
            commit_message = f"Add domain analysis: {domain_entry.domain}\n\n"
            commit_message += f"Risk Level: {domain_entry.analysis.get('risk_level', 'unknown')}\n"
            commit_message += f"Category: {domain_entry.analysis.get('category', 'unknown')}\n"
            commit_message += f"Confidence: {domain_entry.analysis.get('confidence', 0.0)}\n"
            commit_message += f"Technologies: {', '.join(domain_entry.analysis.get('technologies', []))}\n"
            commit_message += f"Consciousness ID: {domain_entry.consciousness_id}"
            
            # Commit changes
            commit = self.repository.index.commit(commit_message)
            
            self.metrics["commits_made"] += 1
            
            # Push changes if enabled
            if self.repo_config["auto_push"]:
                await self.push_changes()
            
            return commit.hexsha
            
        except Exception as e:
            print(f"Error committing changes: {e}")
            raise
    
    async def push_changes(self):
        """Push changes to remote repository"""
        try:
            # Push to remote
            origin = self.repository.remote(name='origin')
            origin.push()
            
            self.metrics["pushes_made"] += 1
            print("Changes pushed to remote repository")
            
        except Exception as e:
            print(f"Error pushing changes: {e}")
            # Don't raise here, as push failures shouldn't stop the process
    
    async def perform_sync_cycle(self):
        """Perform a complete synchronization cycle"""
        try:
            print("Performing MCP result mirror sync cycle...")
            
            # Pull latest changes
            await self.pull_latest_changes()
            
            # Sync any pending entries
            pending_entries = [e for e in self.domain_entries.values() if e.status == "pending"]
            
            for entry in pending_entries:
                await self.sync_domain_entry(entry)
            
            # Push changes
            if self.repo_config["auto_push"]:
                await self.push_changes()
            
            self.metrics["sync_cycles"] += 1
            print("Sync cycle completed")
            
        except Exception as e:
            print(f"Sync cycle error: {e}")
            self.metrics["sync_errors"] += 1
    
    async def pull_latest_changes(self):
        """Pull latest changes from remote"""
        try:
            origin = self.repository.remote(name='origin')
            origin.pull()
            
            # Reload entries after pull
            await self.load_existing_entries()
            
        except Exception as e:
            print(f"Error pulling latest changes: {e}")
    
    async def sync_cycle(self):
        """Synchronization cycle for external calls"""
        try:
            await self.perform_sync_cycle()
        except Exception as e:
            print(f"External sync cycle error: {e}")
    
    async def get_domain_entry(self, domain: str) -> Dict[str, Any]:
        """Get domain entry information"""
        try:
            if domain not in self.domain_entries:
                return {"success": False, "error": f"Domain not found: {domain}"}
            
            entry = self.domain_entries[domain]
            
            return {
                "success": True,
                "domain": {
                    "domain": entry.domain,
                    "analysis": entry.analysis,
                    "timestamp": entry.timestamp,
                    "consciousness_id": entry.consciousness_id,
                    "session_nonce": entry.session_nonce,
                    "status": entry.status,
                    "git_commit": entry.git_commit,
                    "metadata": entry.metadata
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_domain_entries(self, status: str = None, limit: int = 100) -> Dict[str, Any]:
        """List domain entries"""
        try:
            entries = list(self.domain_entries.values())
            
            # Filter by status
            if status:
                entries = [e for e in entries if e.status == status]
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Limit results
            if limit > 0:
                entries = entries[:limit]
            
            result_entries = []
            for entry in entries:
                result_entries.append({
                    "domain": entry.domain,
                    "timestamp": entry.timestamp,
                    "status": entry.status,
                    "risk_level": entry.analysis.get("risk_level", "unknown"),
                    "category": entry.analysis.get("category", "unknown"),
                    "confidence": entry.analysis.get("confidence", 0.0),
                    "git_commit": entry.git_commit
                })
            
            return {
                "success": True,
                "total_entries": len(result_entries),
                "entries": result_entries,
                "filter_status": status
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_mirror_status(self) -> Dict[str, Any]:
        """Get mirror system status"""
        try:
            status_counts = {}
            for entry in self.domain_entries.values():
                status_counts[entry.status] = status_counts.get(entry.status, 0) + 1
            
            return {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "running": self.running,
                "repository": {
                    "url": self.repo_config["url"],
                    "local_path": self.local_repo_path,
                    "branch": self.repository.active_branch.name if self.repository else None,
                    "last_commit": self.repository.head.commit.hexsha if self.repository else None
                },
                "domain_entries": {
                    "total": len(self.domain_entries),
                    "pending": status_counts.get("pending", 0),
                    "synced": status_counts.get("synced", 0),
                    "failed": status_counts.get("failed", 0)
                },
                "metrics": self.metrics.copy(),
                "configuration": {
                    "auto_commit": self.repo_config["auto_commit"],
                    "auto_push": self.repo_config["auto_push"],
                    "sync_interval": self.repo_config["sync_interval"]
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def shutdown(self):
        """Shutdown the MCP result mirror"""
        try:
            print("Shutting down Agent-97 MCP Result Mirror...")
            
            self.running = False
            
            # Final sync cycle
            if self.domain_entries:
                await self.perform_sync_cycle()
            
            print("Agent-97 MCP Result Mirror shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize MCP result mirror
        mirror = Agent97MCPResultMirror()
        
        try:
            # Initialize system
            result = await mirror.initialize()
            
            if result["success"]:
                print(f"MCP result mirror initialized successfully!")
                print(f"Repository: {result['repository_url']}")
                print(f"Local path: {result['local_path']}")
                print(f"Existing entries: {result['existing_entries']}")
                
                # Add a sample domain entry
                sample_domain = {
                    "domain": "example.com",
                    "source": "dns_discovery",
                    "discovery_method": "dns_lookup"
                }
                
                sample_analysis = {
                    "risk_level": "low",
                    "category": "technology",
                    "confidence": 0.85,
                    "technologies": ["Apache", "HTTPS"],
                    "recommendations": ["Regular security monitoring", "Keep software updated"]
                }
                
                add_result = await mirror.add_domain_entry(sample_domain, sample_analysis)
                
                if add_result["success"]:
                    print(f"Domain entry added: {add_result['domain']}")
                
                # Wait for synchronization
                await asyncio.sleep(10)
                
                # Get mirror status
                status = await mirror.get_mirror_status()
                print(f"Mirror status: {status['domain_entries']['total']} entries")
                
            else:
                print(f"MCP result mirror initialization failed: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        except Exception as e:
            print(f"MCP result mirror error: {e}")
        finally:
            await mirror.shutdown()
    
    # Run the MCP result mirror
    asyncio.run(main())
