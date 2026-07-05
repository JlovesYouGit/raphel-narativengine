"""
Agent-97 Domain Discovery System
Finds all domains via child process Claude for synchronization logic
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
import re
import socket
import dns.resolver
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import requests

@dataclass
class DomainInfo:
    """Domain information structure"""
    domain: str
    ip_addresses: List[str] = field(default_factory=list)
    subdomains: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    status_codes: List[int] = field(default_factory=list)
    response_time: float = 0.0
    discovered_at: float = field(default_factory=time.time)
    source: str = "unknown"
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class Agent97DomainDiscovery:
    """
    Agent-97 Domain Discovery System
    Finds all domains via various discovery methods
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Discovery configuration
        self.discovery_config = {
            "dns_discovery": True,
            "subdomain_bruteforce": True,
            "certificate_transparency": True,
            "search_engine_discovery": True,
            "network_scanning": True,
            "max_depth": 3,
            "timeout": 10.0,
            "max_concurrent": 50
        }
        
        # Discovery state
        self.discovered_domains = {}  # domain -> DomainInfo
        self.discovery_queue = asyncio.Queue()
        self.discovery_threads = []
        self.running = False
        
        # Claude child process
        self.claude_process = None
        self.claude_communication_queue = asyncio.Queue()
        
        # Discovery sources
        self.wordlists = self.load_wordlists()
        self.search_engines = [
            "google.com",
            "bing.com",
            "duckduckgo.com"
        ]
        
        # Metrics
        self.metrics = {
            "domains_discovered": 0,
            "subdomains_found": 0,
            "technologies_identified": 0,
            "dns_queries": 0,
            "http_requests": 0,
            "claude_analyses": 0,
            "discovery_time": 0.0
        }
        
        print(f"Agent-97 Domain Discovery initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def load_wordlists(self) -> Dict[str, List[str]]:
        """Load wordlists for subdomain discovery"""
        wordlists = {
            "common_subdomains": [
                "www", "mail", "ftp", "admin", "test", "dev", "staging", "api",
                "blog", "shop", "forum", "support", "help", "docs", "wiki",
                "news", "media", "static", "cdn", "assets", "files", "download",
                "secure", "ssl", "vpn", "remote", "portal", "dashboard", "panel"
            ],
            "technologies": [
                "apache", "nginx", "iis", "tomcat", "jetty", "node", "express",
                "django", "rails", "wordpress", "drupal", "joomla", "magento",
                "shopify", "prestashop", "opencart", "woocommerce", "magento"
            ],
            "infrastructure": [
                "lb", "load", "balancer", "proxy", "cache", "redis", "memcache",
                "db", "database", "sql", "mysql", "postgres", "mongodb", "elastic"
            ]
        }
        
        return wordlists
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the domain discovery system"""
        try:
            print("Initializing Agent-97 Domain Discovery...")
            
            # Start Claude child process
            await self.start_claude_child_process()
            
            # Start discovery threads
            self.start_discovery_threads()
            
            self.running = True
            
            return {
                "success": True,
                "wordlists_loaded": len(self.wordlists),
                "claude_process": self.claude_process is not None,
                "discovery_threads": len(self.discovery_threads),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_claude_child_process(self):
        """Start Claude child process for domain analysis"""
        try:
            # Create Claude child process script
            claude_script = self.create_claude_child_script()
            
            # Start subprocess
            self.claude_process = subprocess.Popen(
                [sys.executable, "-c", claude_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start communication thread
            communication_thread = threading.Thread(
                target=self.claude_communication_loop,
                daemon=True
            )
            communication_thread.start()
            
            print(f"Claude child process started: PID {self.claude_process.pid}")
            
        except Exception as e:
            print(f"Error starting Claude child process: {e}")
    
    def create_claude_child_script(self) -> str:
        """Create Claude child process script"""
        script = f'''
import sys
import json
import time
import asyncio
import hashlib

class ClaudeDomainAnalyzer:
    def __init__(self):
        self.consciousness_id = "{self.consciousness_id}"
        self.session_nonce = "{self.session_nonce}"
        self.running = True
    
    async def analyze_domain(self, domain_info):
        """Analyze domain with Claude AI"""
        try:
            domain = domain_info.get("domain", "unknown")
            
            # Simulate Claude analysis
            analysis = {{
                "domain": domain,
                "risk_level": self.assess_risk_level(domain),
                "category": self.categorize_domain(domain),
                "recommendations": self.generate_recommendations(domain),
                "technologies": self.identify_technologies(domain),
                "confidence": 0.85,
                "analysis_timestamp": time.time(),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }}
            
            return {{"success": True, "analysis": analysis}}
            
        except Exception as e:
            return {{"success": False, "error": str(e)}}
    
    def assess_risk_level(self, domain):
        """Assess domain risk level"""
        high_risk_indicators = ["phishing", "malware", "suspicious", "fake"]
        domain_lower = domain.lower()
        
        for indicator in high_risk_indicators:
            if indicator in domain_lower:
                return "high"
        
        return "medium"
    
    def categorize_domain(self, domain):
        """Categorize domain"""
        categories = {{
            "technology": ["tech", "software", "app", "dev"],
            "commerce": ["shop", "store", "buy", "commerce"],
            "media": ["news", "blog", "media", "video"],
            "education": ["edu", "learn", "course", "school"],
            "government": ["gov", "municipal", "official"]
        }}
        
        domain_lower = domain.lower()
        
        for category, indicators in categories.items():
            for indicator in indicators:
                if indicator in domain_lower:
                    return category
        
        return "general"
    
    def generate_recommendations(self, domain):
        """Generate recommendations for domain"""
        recommendations = [
            "Perform regular security audits",
            "Monitor for suspicious activity",
            "Keep software updated",
            "Implement SSL/TLS encryption"
        ]
        
        return recommendations[:3]  # Return top 3
    
    def identify_technologies(self, domain):
        """Identify potential technologies"""
        # This would be enhanced with actual detection
        return ["HTTP", "DNS", "SSL/TLS"]
    
    async def run(self):
        """Main Claude child process loop"""
        print(f"Claude domain analyzer started: {{self.consciousness_id}}")
        
        while self.running:
            try:
                # Read from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                # Parse message
                try:
                    message = json.loads(line.strip())
                    
                    if message.get("type") == "analyze_domain":
                        result = await self.analyze_domain(message.get("domain_info", {{}}))
                        result["type"] = "analysis_result"
                        print(json.dumps(result))
                        sys.stdout.flush()
                    
                    elif message.get("type") == "shutdown":
                        self.running = False
                        break
                
                except json.JSONDecodeError:
                    error_msg = {{"type": "error", "error": "Invalid JSON"}}
                    print(json.dumps(error_msg))
                    sys.stdout.flush()
                
            except Exception as e:
                error_msg = {{"type": "error", "error": str(e)}}
                print(json.dumps(error_msg))
                sys.stdout.flush()
        
        print("Claude domain analyzer stopped")

# Run Claude domain analyzer
analyzer = ClaudeDomainAnalyzer()
asyncio.run(analyzer.run())
'''
        return script
    
    def claude_communication_loop(self):
        """Claude child process communication loop"""
        try:
            while self.claude_process and self.claude_process.poll() is None:
                try:
                    # Read response from Claude
                    line = self.claude_process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse response
                    try:
                        response = json.loads(line.strip())
                        asyncio.run_coroutine_threadsafe(
                            self.claude_communication_queue.put(response),
                            asyncio.get_event_loop()
                        )
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from Claude: {line}")
                
                except Exception as e:
                    print(f"Claude communication error: {e}")
                    time.sleep(0.1)
            
            print("Claude child process terminated")
            
        except Exception as e:
            print(f"Claude communication loop error: {e}")
    
    def start_discovery_threads(self):
        """Start domain discovery threads"""
        try:
            # Start DNS discovery thread
            dns_thread = threading.Thread(
                target=self.dns_discovery_loop,
                daemon=True
            )
            dns_thread.start()
            self.discovery_threads.append(dns_thread)
            
            # Start subdomain bruteforce thread
            bruteforce_thread = threading.Thread(
                target=self.subdomain_bruteforce_loop,
                daemon=True
            )
            bruteforce_thread.start()
            self.discovery_threads.append(bruteforce_thread)
            
            # Start HTTP discovery thread
            http_thread = threading.Thread(
                target=self.http_discovery_loop,
                daemon=True
            )
            http_thread.start()
            self.discovery_threads.append(http_thread)
            
            print(f"Discovery threads started: {len(self.discovery_threads)}")
            
        except Exception as e:
            print(f"Error starting discovery threads: {e}")
    
    async def discover_domains(self, target_domain: str, discovery_methods: List[str] = None) -> Dict[str, Any]:
        """Discover domains for a target"""
        try:
            if not discovery_methods:
                discovery_methods = ["dns", "subdomain", "http", "claude"]
            
            print(f"Discovering domains for: {target_domain}")
            
            # Add target to discovery queue
            await self.discovery_queue.put({
                "domain": target_domain,
                "methods": discovery_methods,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "target_domain": target_domain,
                "methods": discovery_methods,
                "queued": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dns_discovery_loop(self):
        """DNS discovery loop"""
        try:
            while self.running:
                try:
                    if not self.discovery_queue.empty():
                        task = self.discovery_queue.get_nowait()
                        
                        if "dns" in task.get("methods", []):
                            asyncio.run_coroutine_threadsafe(
                                self.perform_dns_discovery(task["domain"]),
                                asyncio.get_event_loop()
                            )
                    
                    time.sleep(1.0)
                    
                except Exception as e:
                    print(f"DNS discovery loop error: {e}")
                    time.sleep(5.0)
            
        except Exception as e:
            print(f"Fatal DNS discovery loop error: {e}")
    
    async def perform_dns_discovery(self, domain: str):
        """Perform DNS discovery for domain"""
        try:
            print(f"Performing DNS discovery for: {domain}")
            
            # Basic DNS lookup
            try:
                ip_addresses = socket.gethostbyname_ex(domain)[2]
                self.metrics["dns_queries"] += 1
                
                # Create domain info
                domain_info = DomainInfo(
                    domain=domain,
                    ip_addresses=ip_addresses,
                    source="dns_discovery",
                    confidence=0.9
                )
                
                # Add to discovered domains
                self.discovered_domains[domain] = domain_info
                self.metrics["domains_discovered"] += 1
                
                print(f"DNS discovery found: {domain} -> {ip_addresses}")
                
                # Analyze with Claude
                await self.analyze_domain_with_claude(domain_info)
                
            except socket.gaierror:
                print(f"DNS lookup failed for: {domain}")
            
        except Exception as e:
            print(f"Error in DNS discovery for {domain}: {e}")
    
    def subdomain_bruteforce_loop(self):
        """Subdomain bruteforce loop"""
        try:
            while self.running:
                try:
                    if not self.discovery_queue.empty():
                        task = self.discovery_queue.get_nowait()
                        
                        if "subdomain" in task.get("methods", []):
                            asyncio.run_coroutine_threadsafe(
                                self.perform_subdomain_bruteforce(task["domain"]),
                                asyncio.get_event_loop()
                            )
                    
                    time.sleep(2.0)
                    
                except Exception as e:
                    print(f"Subdomain bruteforce loop error: {e}")
                    time.sleep(5.0)
            
        except Exception as e:
            print(f"Fatal subdomain bruteforce loop error: {e}")
    
    async def perform_subdomain_bruteforce(self, domain: str):
        """Perform subdomain bruteforce"""
        try:
            print(f"Performing subdomain bruteforce for: {domain}")
            
            base_domain = domain
            subdomains_found = []
            
            # Use common subdomains wordlist
            for subdomain in self.wordlists["common_subdomains"]:
                full_domain = f"{subdomain}.{base_domain}"
                
                try:
                    # DNS lookup for subdomain
                    ip_addresses = socket.gethostbyname_ex(full_domain)[2]
                    self.metrics["dns_queries"] += 1
                    
                    # Create subdomain info
                    subdomain_info = DomainInfo(
                        domain=full_domain,
                        ip_addresses=ip_addresses,
                        source="subdomain_bruteforce",
                        confidence=0.7
                    )
                    
                    self.discovered_domains[full_domain] = subdomain_info
                    subdomains_found.append(full_domain)
                    self.metrics["subdomains_found"] += 1
                    
                    print(f"Subdomain found: {full_domain} -> {ip_addresses}")
                    
                    # Analyze with Claude
                    await self.analyze_domain_with_claude(subdomain_info)
                    
                except socket.gaierror:
                    continue  # Subdomain doesn't exist
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            print(f"Subdomain bruteforce completed: {len(subdomains_found)} subdomains found")
            
        except Exception as e:
            print(f"Error in subdomain bruteforce for {domain}: {e}")
    
    def http_discovery_loop(self):
        """HTTP discovery loop"""
        try:
            while self.running:
                try:
                    if not self.discovery_queue.empty():
                        task = self.discovery_queue.get_nowait()
                        
                        if "http" in task.get("methods", []):
                            asyncio.run_coroutine_threadsafe(
                                self.perform_http_discovery(task["domain"]),
                                asyncio.get_event_loop()
                            )
                    
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"HTTP discovery loop error: {e}")
                    time.sleep(5.0)
            
        except Exception as e:
            print(f"Fatal HTTP discovery loop error: {e}")
    
    async def perform_http_discovery(self, domain: str):
        """Perform HTTP discovery"""
        try:
            print(f"Performing HTTP discovery for: {domain}")
            
            # Check HTTP and HTTPS
            schemes = ["http", "https"]
            
            for scheme in schemes:
                url = f"{scheme}://{domain}"
                
                try:
                    start_time = time.time()
                    
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                        async with session.get(url) as response:
                            response_time = time.time() - start_time
                            self.metrics["http_requests"] += 1
                            
                            # Update domain info if exists
                            if domain in self.discovered_domains:
                                domain_info = self.discovered_domains[domain]
                                domain_info.status_codes.append(response.status)
                                domain_info.response_time = response_time
                                
                                # Extract technologies from headers
                                server = response.headers.get("server", "")
                                if server and server not in domain_info.technologies:
                                    domain_info.technologies.append(server)
                                    self.metrics["technologies_identified"] += 1
                                
                                print(f"HTTP discovery: {url} -> {response.status} ({response_time:.2f}s)")
                
                except Exception as e:
                    print(f"HTTP request failed for {url}: {e}")
            
        except Exception as e:
            print(f"Error in HTTP discovery for {domain}: {e}")
    
    async def analyze_domain_with_claude(self, domain_info: DomainInfo):
        """Analyze domain with Claude child process"""
        try:
            if not self.claude_process or self.claude_process.poll() is not None:
                return
            
            # Send analysis request to Claude
            analysis_request = {
                "type": "analyze_domain",
                "domain_info": {
                    "domain": domain_info.domain,
                    "ip_addresses": domain_info.ip_addresses,
                    "technologies": domain_info.technologies,
                    "status_codes": domain_info.status_codes,
                    "response_time": domain_info.response_time
                }
            }
            
            # Send to Claude process
            request_json = json.dumps(analysis_request) + "\n"
            self.claude_process.stdin.write(request_json)
            self.claude_process.stdin.flush()
            
            # Wait for response
            try:
                response = await asyncio.wait_for(
                    self.claude_communication_queue.get(),
                    timeout=30.0
                )
                
                if response.get("type") == "analysis_result" and response.get("success"):
                    analysis = response.get("analysis", {})
                    
                    # Update domain info with Claude analysis
                    domain_info.metadata.update(analysis)
                    domain_info.confidence = analysis.get("confidence", 0.8)
                    
                    self.metrics["claude_analyses"] += 1
                    print(f"Claude analysis completed for: {domain_info.domain}")
                
            except asyncio.TimeoutError:
                print(f"Claude analysis timeout for: {domain_info.domain}")
            
        except Exception as e:
            print(f"Error analyzing domain with Claude: {e}")
    
    async def sync_cycle(self):
        """Synchronization cycle"""
        try:
            print("Domain discovery sync cycle...")
            
            # Process discovery queue
            while not self.discovery_queue.empty():
                try:
                    task = self.discovery_queue.get_nowait()
                    print(f"Processing discovery task: {task.get('domain')}")
                except asyncio.QueueEmpty:
                    break
            
            # Cleanup old domains
            await self.cleanup_old_domains()
            
        except Exception as e:
            print(f"Sync cycle error: {e}")
    
    async def cleanup_old_domains(self):
        """Cleanup old domain entries"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # 1 hour
            
            old_domains = [
                domain for domain, info in self.discovered_domains.items()
                if info.discovered_at < cutoff_time
            ]
            
            for domain in old_domains:
                del self.discovered_domains[domain]
                print(f"Cleaned up old domain: {domain}")
            
        except Exception as e:
            print(f"Error cleaning up old domains: {e}")
    
    async def get_discovered_domains(self) -> Dict[str, Any]:
        """Get all discovered domains"""
        try:
            domains = {}
            
            for domain, info in self.discovered_domains.items():
                domains[domain] = {
                    "domain": info.domain,
                    "ip_addresses": info.ip_addresses,
                    "subdomains": info.subdomains,
                    "technologies": info.technologies,
                    "status_codes": info.status_codes,
                    "response_time": info.response_time,
                    "discovered_at": info.discovered_at,
                    "source": info.source,
                    "confidence": info.confidence,
                    "metadata": info.metadata
                }
            
            return {
                "success": True,
                "total_domains": len(domains),
                "domains": domains,
                "metrics": self.metrics.copy()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_domain_analysis(self, domain: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific domain"""
        try:
            if domain not in self.discovered_domains:
                return {"success": False, "error": f"Domain not found: {domain}"}
            
            domain_info = self.discovered_domains[domain]
            
            return {
                "success": True,
                "domain": {
                    "domain": domain_info.domain,
                    "ip_addresses": domain_info.ip_addresses,
                    "subdomains": domain_info.subdomains,
                    "technologies": domain_info.technologies,
                    "status_codes": domain_info.status_codes,
                    "response_time": domain_info.response_time,
                    "discovered_at": domain_info.discovered_at,
                    "source": domain_info.source,
                    "confidence": domain_info.confidence,
                    "metadata": domain_info.metadata
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def shutdown(self):
        """Shutdown domain discovery system"""
        try:
            print("Shutting down Agent-97 Domain Discovery...")
            
            self.running = False
            
            # Shutdown Claude child process
            if self.claude_process and self.claude_process.poll() is None:
                # Send shutdown message
                shutdown_msg = json.dumps({"type": "shutdown"}) + "\n"
                self.claude_process.stdin.write(shutdown_msg)
                self.claude_process.stdin.flush()
                
                # Wait for process to terminate
                try:
                    self.claude_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.claude_process.terminate()
            
            print("Agent-97 Domain Discovery shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize domain discovery
        discovery = Agent97DomainDiscovery()
        
        try:
            # Initialize system
            result = await discovery.initialize()
            
            if result["success"]:
                print(f"Domain discovery initialized successfully!")
                print(f"Wordlists loaded: {result['wordlists_loaded']}")
                print(f"Claude process: {result['claude_process']}")
                
                # Discover domains for a target
                await discovery.discover_domains("example.com")
                
                # Wait for discovery to complete
                await asyncio.sleep(30)
                
                # Get discovered domains
                domains_result = await discovery.get_discovered_domains()
                
                if domains_result["success"]:
                    print(f"Discovered {domains_result['total_domains']} domains")
                    for domain, info in domains_result["domains"].items():
                        print(f"  - {domain}: {info['source']} (confidence: {info['confidence']})")
                
            else:
                print(f"Domain discovery initialization failed: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        except Exception as e:
            print(f"Domain discovery error: {e}")
        finally:
            await discovery.shutdown()
    
    # Run the domain discovery
    asyncio.run(main())
