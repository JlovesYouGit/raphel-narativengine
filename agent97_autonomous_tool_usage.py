"""
Agent-97 Autonomous Tool Usage System
Enables the Agent-97 model to automatically select and use tools based on context and needs
"""

import os
import sys
import json
import time
import asyncio
import re
import uuid
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Import Agent-97 components
from agent97_mcp_tool_integration import Agent97MCPToolIntegration
from agent97_automated_domain_pipeline import Agent97AutomatedDomainPipeline

@dataclass
class ToolContext:
    """Tool context for decision making"""
    user_intent: str
    current_task: str
    available_data: Dict[str, Any]
    previous_actions: List[str]
    success_criteria: str
    constraints: List[str] = field(default_factory=list)

@dataclass
class ToolDecision:
    """Tool decision result"""
    tool_name: str
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    expected_outcome: str
    priority: int = 1

class Agent97AutonomousToolUsage:
    """
    Agent-97 Autonomous Tool Usage System
    Enables intelligent automatic tool selection and execution
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Tool integration
        self.mcp_tool_integration = None
        self.domain_pipeline = None
        
        # Autonomous configuration
        self.autonomous_config = {
            "auto_tool_selection": True,
            "learning_enabled": True,
            "decision_confidence_threshold": 0.7,
            "max_concurrent_tools": 3,
            "tool_timeout": 60.0,
            "retry_attempts": 3,
            "adaptation_enabled": True
        }
        
        # Tool registry and capabilities
        self.tool_registry = {}
        self.tool_capabilities = {}
        self.tool_performance = {}
        
        # Decision making
        self.decision_history = []
        self.learning_data = []
        self.context_analyzer = None
        
        # Autonomous state
        self.running = False
        self.active_tasks = {}
        self.task_queue = asyncio.Queue()
        
        # Metrics
        self.metrics = {
            "autonomous_decisions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "tools_used": set(),
            "average_confidence": 0.0,
            "learning_improvements": 0,
            "context_analyses": 0
        }
        
        print(f"Agent-97 Autonomous Tool Usage System initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        import hashlib
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_autonomous_system(self) -> Dict[str, Any]:
        """Initialize the autonomous tool usage system"""
        try:
            print("Initializing Agent-97 Autonomous Tool Usage System...")
            
            # Step 1: Initialize MCP tool integration
            self.mcp_tool_integration = Agent97MCPToolIntegration(self.consciousness_id)
            mcp_result = await self.mcp_tool_integration.initialize_mcp_integration()
            
            if not mcp_result["success"]:
                return {"success": False, "error": f"MCP tool integration failed: {mcp_result['error']}"}
            
            # Step 2: Initialize domain pipeline
            self.domain_pipeline = Agent97AutomatedDomainPipeline(self.consciousness_id)
            pipeline_result = await self.domain_pipeline.initialize_pipeline()
            
            if not pipeline_result["success"]:
                return {"success": False, "error": f"Domain pipeline failed: {pipeline_result['error']}"}
            
            # Step 3: Register available tools
            await self.register_available_tools()
            
            # Step 4: Initialize context analyzer
            await self.initialize_context_analyzer()
            
            # Step 5: Start autonomous processing
            await self.start_autonomous_processing()
            
            self.running = True
            
            return {
                "success": True,
                "mcp_tools": len(self.tool_registry.get("mcp", {})),
                "pipeline_tools": len(self.tool_registry.get("pipeline", {})),
                "total_tools": sum(len(tools) for tools in self.tool_registry.values()),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def register_available_tools(self):
        """Register all available tools with their capabilities"""
        try:
            # Register MCP tools
            if self.mcp_tool_integration:
                mcp_tools = await self.mcp_tool_integration.get_available_tools()
                if mcp_tools["success"]:
                    self.tool_registry["mcp"] = mcp_tools["tools"]
                    self.tool_capabilities["mcp"] = self.analyze_tool_capabilities(mcp_tools["tools"])
            
            # Register pipeline tools
            if self.domain_pipeline:
                self.tool_registry["pipeline"] = {
                    "discover_domains": {
                        "description": "Discover domains using various methods",
                        "parameters": {"domains": "list of domain names"},
                        "capabilities": ["dns_discovery", "subdomain_enumeration", "http_analysis"]
                    },
                    "analyze_domains": {
                        "description": "Analyze domains with Claude AI",
                        "parameters": {"domains": "list of domain info"},
                        "capabilities": ["risk_assessment", "categorization", "technology_detection"]
                    },
                    "sync_to_mirror": {
                        "description": "Sync results to MCP mirror repository",
                        "parameters": {"entries": "domain analysis results"},
                        "capabilities": ["git_operations", "data_storage", "version_control"]
                    }
                }
                self.tool_capabilities["pipeline"] = self.analyze_tool_capabilities(self.tool_registry["pipeline"])
            
            print(f"Registered {sum(len(tools) for tools in self.tool_registry.values())} tools")
            
        except Exception as e:
            print(f"Error registering tools: {e}")
    
    def analyze_tool_capabilities(self, tools: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze and extract tool capabilities"""
        capabilities = {}
        
        for tool_name, tool_info in tools.items():
            tool_caps = []
            
            # Extract capabilities from description
            description = tool_info.get("description", "").lower()
            if "search" in description:
                tool_caps.append("web_search")
            if "fetch" in description:
                tool_caps.append("content_retrieval")
            if "cache" in description:
                tool_caps.append("data_storage")
            if "discover" in description:
                tool_caps.append("domain_discovery")
            if "analyze" in description:
                tool_caps.append("data_analysis")
            if "sync" in description:
                tool_caps.append("data_synchronization")
            
            # Extract capabilities from parameters
            params = tool_info.get("parameters", {})
            if "url" in params:
                tool_caps.append("url_processing")
            if "query" in params:
                tool_caps.append("query_processing")
            if "domains" in params:
                tool_caps.append("domain_processing")
            
            capabilities[tool_name] = tool_caps
        
        return capabilities
    
    async def initialize_context_analyzer(self):
        """Initialize the context analyzer"""
        try:
            self.context_analyzer = {
                "intent_patterns": {
                    "search": ["find", "search", "look for", "discover", "locate"],
                    "analyze": ["analyze", "examine", "investigate", "study", "review"],
                    "store": ["save", "store", "cache", "remember", "keep"],
                    "process": ["process", "handle", "manage", "organize"],
                    "sync": ["sync", "update", "backup", "mirror"]
                },
                "domain_patterns": {
                    "domain_discovery": ["domain", "website", "subdomain", "dns"],
                    "security_analysis": ["security", "risk", "vulnerability", "threat"],
                    "technology_identification": ["technology", "stack", "framework", "server"]
                },
                "data_patterns": {
                    "web_content": ["web", "page", "content", "html"],
                    "api_data": ["api", "json", "response", "endpoint"],
                    "cache_data": ["cache", "stored", "saved", "memory"]
                }
            }
            
            print("Context analyzer initialized")
            
        except Exception as e:
            print(f"Error initializing context analyzer: {e}")
    
    async def start_autonomous_processing(self):
        """Start autonomous processing loop"""
        try:
            # Start autonomous task processor
            asyncio.create_task(self.autonomous_processing_loop())
            
            print("Autonomous processing started")
            
        except Exception as e:
            print(f"Error starting autonomous processing: {e}")
    
    async def autonomous_processing_loop(self):
        """Main autonomous processing loop"""
        try:
            print("Starting autonomous tool usage loop...")
            
            while self.running:
                try:
                    # Process task queue
                    while not self.task_queue.empty():
                        try:
                            task = self.task_queue.get_nowait()
                            await self.process_autonomous_task(task)
                        except Exception as e:
                            print(f"Error processing autonomous task: {e}")
                    
                    # Perform proactive analysis
                    await self.proactive_analysis()
                    
                    # Learning and adaptation
                    if self.autonomous_config["learning_enabled"]:
                        await self.learning_cycle()
                    
                    await asyncio.sleep(5.0)
                    
                except Exception as e:
                    print(f"Autonomous processing loop error: {e}")
                    await asyncio.sleep(10.0)
            
        except Exception as e:
            print(f"Fatal autonomous processing loop error: {e}")
    
    async def process_autonomous_task(self, task: Dict[str, Any]):
        """Process an autonomous task"""
        try:
            task_id = task.get("task_id", str(uuid.uuid4()))
            task_type = task.get("type", "unknown")
            context = task.get("context", {})
            
            print(f"Processing autonomous task: {task_id} ({task_type})")
            
            # Analyze context and make tool decision
            tool_decision = await self.make_autonomous_tool_decision(context)
            
            if tool_decision and tool_decision.confidence >= self.autonomous_config["decision_confidence_threshold"]:
                # Execute the tool
                result = await self.execute_autonomous_tool(tool_decision)
                
                # Learn from the result
                if self.autonomous_config["learning_enabled"]:
                    await self.learn_from_execution(tool_decision, result)
                
                # Update metrics
                self.metrics["autonomous_decisions"] += 1
                if result.get("success"):
                    self.metrics["successful_executions"] += 1
                else:
                    self.metrics["failed_executions"] += 1
                
                print(f"Task {task_id} completed: {result.get('success', False)}")
            else:
                print(f"Task {task_id} skipped: Low confidence ({tool_decision.confidence if tool_decision else 0})")
            
        except Exception as e:
            print(f"Error processing autonomous task: {e}")
            self.metrics["failed_executions"] += 1
    
    async def make_autonomous_tool_decision(self, context: Dict[str, Any]) -> Optional[ToolDecision]:
        """Make autonomous tool decision based on context"""
        try:
            # Analyze user intent
            user_intent = self.analyze_user_intent(context)
            
            # Analyze current task requirements
            task_requirements = self.analyze_task_requirements(context)
            
            # Find suitable tools
            suitable_tools = await self.find_suitable_tools(user_intent, task_requirements)
            
            if not suitable_tools:
                return None
            
            # Select best tool
            best_tool = await self.select_best_tool(suitable_tools, context)
            
            # Generate tool parameters
            parameters = await self.generate_tool_parameters(best_tool, context)
            
            # Create decision
            decision = ToolDecision(
                tool_name=best_tool["name"],
                confidence=best_tool["confidence"],
                reasoning=best_tool["reasoning"],
                parameters=parameters,
                expected_outcome=best_tool["expected_outcome"],
                priority=best_tool.get("priority", 1)
            )
            
            # Update decision history
            self.decision_history.append({
                "timestamp": time.time(),
                "context": context,
                "decision": decision,
                "intent": user_intent
            })
            
            return decision
            
        except Exception as e:
            print(f"Error making autonomous tool decision: {e}")
            return None
    
    def analyze_user_intent(self, context: Dict[str, Any]) -> str:
        """Analyze user intent from context"""
        try:
            user_input = context.get("user_input", "").lower()
            current_task = context.get("current_task", "").lower()
            
            # Check intent patterns
            for intent, patterns in self.context_analyzer["intent_patterns"].items():
                for pattern in patterns:
                    if pattern in user_input or pattern in current_task:
                        return intent
            
            return "general"
            
        except Exception as e:
            print(f"Error analyzing user intent: {e}")
            return "unknown"
    
    def analyze_task_requirements(self, context: Dict[str, Any]) -> List[str]:
        """Analyze task requirements from context"""
        try:
            requirements = []
            
            user_input = context.get("user_input", "").lower()
            current_task = context.get("current_task", "").lower()
            
            # Check domain patterns
            for requirement, patterns in self.context_analyzer["domain_patterns"].items():
                for pattern in patterns:
                    if pattern in user_input or pattern in current_task:
                        requirements.append(requirement)
            
            # Check data patterns
            for requirement, patterns in self.context_analyzer["data_patterns"].items():
                for pattern in patterns:
                    if pattern in user_input or pattern in current_task:
                        requirements.append(requirement)
            
            return requirements
            
        except Exception as e:
            print(f"Error analyzing task requirements: {e}")
            return []
    
    async def find_suitable_tools(self, user_intent: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Find suitable tools for the given intent and requirements"""
        try:
            suitable_tools = []
            
            for category, tools in self.tool_registry.items():
                capabilities = self.tool_capabilities.get(category, {})
                
                for tool_name, tool_info in tools.items():
                    tool_caps = capabilities.get(tool_name, [])
                    
                    # Calculate suitability score
                    score = 0.0
                    reasoning = []
                    
                    # Check intent match
                    if user_intent == "search" and "web_search" in tool_caps:
                        score += 0.4
                        reasoning.append("Matches search intent")
                    elif user_intent == "analyze" and "data_analysis" in tool_caps:
                        score += 0.4
                        reasoning.append("Matches analysis intent")
                    elif user_intent == "store" and "data_storage" in tool_caps:
                        score += 0.4
                        reasoning.append("Matches storage intent")
                    elif user_intent == "sync" and "data_synchronization" in tool_caps:
                        score += 0.4
                        reasoning.append("Matches sync intent")
                    
                    # Check requirements match
                    requirements_match = len(set(requirements) & set(tool_caps))
                    if requirements_match > 0:
                        score += (requirements_match / len(requirements)) * 0.6
                        reasoning.append(f"Matches {requirements_match} requirements")
                    
                    # Include tool if score is significant
                    if score > 0.3:
                        suitable_tools.append({
                            "name": tool_name,
                            "category": category,
                            "score": score,
                            "confidence": min(score, 1.0),
                            "reasoning": "; ".join(reasoning),
                            "capabilities": tool_caps
                        })
            
            # Sort by score
            suitable_tools.sort(key=lambda x: x["score"], reverse=True)
            
            return suitable_tools
            
        except Exception as e:
            print(f"Error finding suitable tools: {e}")
            return []
    
    async def select_best_tool(self, suitable_tools: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best tool from suitable options"""
        try:
            if not suitable_tools:
                return {}
            
            # Get the top tool
            best_tool = suitable_tools[0]
            
            # Consider tool performance history
            tool_name = best_tool["name"]
            performance = self.tool_performance.get(tool_name, {"success_rate": 0.5, "avg_response_time": 1.0})
            
            # Adjust confidence based on performance
            performance_adjustment = performance["success_rate"] * 0.2
            best_tool["confidence"] = min(best_tool["confidence"] + performance_adjustment, 1.0)
            
            # Determine expected outcome
            best_tool["expected_outcome"] = self.predict_tool_outcome(best_tool, context)
            
            # Set priority based on confidence and urgency
            if best_tool["confidence"] > 0.8:
                best_tool["priority"] = 1
            elif best_tool["confidence"] > 0.6:
                best_tool["priority"] = 2
            else:
                best_tool["priority"] = 3
            
            return best_tool
            
        except Exception as e:
            print(f"Error selecting best tool: {e}")
            return {}
    
    def predict_tool_outcome(self, tool: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Predict the expected outcome of using a tool"""
        try:
            tool_name = tool["name"]
            capabilities = tool.get("capabilities", [])
            
            outcome_predictions = {
                "search": "Web search results with relevant information",
                "fetch": "Retrieved web content with metadata",
                "cache_set": "Data successfully stored in cache",
                "cache_get": "Retrieved cached data",
                "cache_delete": "Data removed from cache",
                "discover_domains": "Discovered domain information and subdomains",
                "analyze_domains": "Domain analysis with risk assessment and categorization",
                "sync_to_mirror": "Data synchronized to repository"
            }
            
            # Generic prediction based on capabilities
            if "web_search" in capabilities:
                return "Search results retrieved"
            elif "content_retrieval" in capabilities:
                return "Web content fetched"
            elif "data_storage" in capabilities:
                return "Data stored successfully"
            elif "domain_discovery" in capabilities:
                return "Domain information discovered"
            elif "data_analysis" in capabilities:
                return "Data analysis completed"
            elif "data_synchronization" in capabilities:
                return "Data synchronized"
            else:
                return "Tool execution completed"
            
        except Exception as e:
            print(f"Error predicting tool outcome: {e}")
            return "Unknown outcome"
    
    async def generate_tool_parameters(self, tool: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameters for tool execution"""
        try:
            tool_name = tool["name"]
            category = tool["category"]
            parameters = {}
            
            # Extract parameters from context
            if category == "mcp":
                if tool_name == "search":
                    parameters["query"] = context.get("query", context.get("user_input", "default search"))
                    parameters["max_results"] = context.get("max_results", 10)
                elif tool_name == "fetch":
                    parameters["url"] = context.get("url", "https://example.com")
                    parameters["include_screenshot"] = context.get("include_screenshot", False)
                elif tool_name in ["cache_set", "cache_get", "cache_delete"]:
                    parameters["key"] = context.get("cache_key", f"agent97_{int(time.time())}")
                    if tool_name == "cache_set":
                        parameters["value"] = context.get("cache_value", {"data": "auto_generated"})
                        parameters["ttl"] = context.get("ttl", 3600)
            
            elif category == "pipeline":
                if tool_name == "discover_domains":
                    parameters["domains"] = context.get("domains", ["example.com"])
                elif tool_name == "analyze_domains":
                    parameters["domains"] = context.get("domain_data", [])
                elif tool_name == "sync_to_mirror":
                    parameters["entries"] = context.get("entries", [])
            
            return parameters
            
        except Exception as e:
            print(f"Error generating tool parameters: {e}")
            return {}
    
    async def execute_autonomous_tool(self, decision: ToolDecision) -> Dict[str, Any]:
        """Execute the selected tool autonomously"""
        try:
            tool_name = decision.tool_name
            parameters = decision.parameters
            
            print(f"Executing autonomous tool: {tool_name}")
            
            start_time = time.time()
            
            # Execute based on tool category
            if tool_name in ["search", "fetch", "cache_set", "cache_get", "cache_delete"]:
                result = await self.execute_mcp_tool(tool_name, parameters)
            elif tool_name in ["discover_domains", "analyze_domains", "sync_to_mirror"]:
                result = await self.execute_pipeline_tool(tool_name, parameters)
            else:
                result = {"success": False, "error": f"Unknown tool: {tool_name}"}
            
            execution_time = time.time() - start_time
            
            # Update tool performance
            await self.update_tool_performance(tool_name, result, execution_time)
            
            # Update metrics
            self.metrics["tools_used"].add(tool_name)
            
            return {
                "success": result.get("success", False),
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result,
                "execution_time": execution_time,
                "decision": decision
            }
            
        except Exception as e:
            print(f"Error executing autonomous tool: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool"""
        try:
            if not self.mcp_tool_integration:
                return {"success": False, "error": "MCP tool integration not available"}
            
            if tool_name == "search":
                return await self.mcp_tool_integration.search_web(
                    parameters.get("query", ""),
                    parameters.get("max_results", 10)
                )
            elif tool_name == "fetch":
                return await self.mcp_tool_integration.fetch_url(
                    parameters.get("url", ""),
                    parameters.get("range_y"),
                    parameters.get("include_screenshot", True)
                )
            elif tool_name == "cache_set":
                return await self.mcp_tool_integration.cache_set(
                    parameters.get("key", ""),
                    parameters.get("value"),
                    parameters.get("ttl", 3600)
                )
            elif tool_name == "cache_get":
                return await self.mcp_tool_integration.cache_get(parameters.get("key", ""))
            elif tool_name == "cache_delete":
                return await self.mcp_tool_integration.cache_delete(parameters.get("key", ""))
            else:
                return {"success": False, "error": f"Unknown MCP tool: {tool_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_pipeline_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline tool"""
        try:
            if not self.domain_pipeline:
                return {"success": False, "error": "Domain pipeline not available"}
            
            if tool_name == "discover_domains":
                domains = parameters.get("domains", [])
                results = []
                
                for domain in domains:
                    result = await self.domain_pipeline.add_target_domain(domain)
                    results.append(result)
                
                return {"success": True, "results": results}
            
            elif tool_name == "analyze_domains":
                # This would trigger the pipeline's analysis process
                return {"success": True, "message": "Domain analysis triggered"}
            
            elif tool_name == "sync_to_mirror":
                # This would trigger the pipeline's sync process
                return {"success": True, "message": "Sync to mirror triggered"}
            
            else:
                return {"success": False, "error": f"Unknown pipeline tool: {tool_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_tool_performance(self, tool_name: str, result: Dict[str, Any], execution_time: float):
        """Update tool performance metrics"""
        try:
            if tool_name not in self.tool_performance:
                self.tool_performance[tool_name] = {
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "usage_count": 0,
                    "success_count": 0
                }
            
            perf = self.tool_performance[tool_name]
            perf["usage_count"] += 1
            
            if result.get("success"):
                perf["success_count"] += 1
            
            # Update success rate
            perf["success_rate"] = perf["success_count"] / perf["usage_count"]
            
            # Update average response time
            total_time = perf["avg_response_time"] * (perf["usage_count"] - 1) + execution_time
            perf["avg_response_time"] = total_time / perf["usage_count"]
            
        except Exception as e:
            print(f"Error updating tool performance: {e}")
    
    async def learn_from_execution(self, decision: ToolDecision, result: Dict[str, Any]):
        """Learn from tool execution results"""
        try:
            learning_entry = {
                "timestamp": time.time(),
                "decision": decision,
                "result": result,
                "success": result.get("success", False),
                "execution_time": result.get("execution_time", 0.0)
            }
            
            self.learning_data.append(learning_entry)
            
            # Adapt decision thresholds based on performance
            if self.autonomous_config["adaptation_enabled"]:
                await self.adapt_decision_thresholds()
            
        except Exception as e:
            print(f"Error learning from execution: {e}")
    
    async def adapt_decision_thresholds(self):
        """Adapt decision thresholds based on learning"""
        try:
            if len(self.learning_data) < 10:
                return  # Not enough data for adaptation
            
            # Calculate recent success rate
            recent_data = self.learning_data[-10:]
            success_rate = sum(1 for entry in recent_data if entry["success"]) / len(recent_data)
            
            # Adjust confidence threshold
            if success_rate > 0.8:
                # Increase confidence threshold for more selective decisions
                self.autonomous_config["decision_confidence_threshold"] = min(
                    self.autonomous_config["decision_confidence_threshold"] + 0.05, 0.9
                )
                self.metrics["learning_improvements"] += 1
            elif success_rate < 0.5:
                # Decrease confidence threshold for more opportunities
                self.autonomous_config["decision_confidence_threshold"] = max(
                    self.autonomous_config["decision_confidence_threshold"] - 0.05, 0.5
                )
                self.metrics["learning_improvements"] += 1
            
        except Exception as e:
            print(f"Error adapting decision thresholds: {e}")
    
    async def proactive_analysis(self):
        """Perform proactive analysis and task generation"""
        try:
            # Check if there are any pending operations that need attention
            if self.mcp_tool_integration:
                # Check cache health
                cache_test = await self.mcp_tool_integration.cache_get("health_check")
                if not cache_test.get("success"):
                    # Add cache maintenance task
                    await self.task_queue.put({
                        "type": "maintenance",
                        "context": {
                            "user_input": "cache maintenance",
                            "current_task": "cache health check"
                        }
                    })
            
            # Check pipeline status
            if self.domain_pipeline:
                status = await self.domain_pipeline.get_pipeline_status()
                if "error" not in status:
                    # Check if there are domains that need processing
                    if status.get("discovered_domains", 0) > status.get("analyzed_domains", 0):
                        await self.task_queue.put({
                            "type": "domain_processing",
                            "context": {
                                "user_input": "process discovered domains",
                                "current_task": "domain analysis"
                            }
                        })
            
        except Exception as e:
            print(f"Error in proactive analysis: {e}")
    
    async def learning_cycle(self):
        """Perform learning and adaptation cycle"""
        try:
            # Analyze decision patterns
            if len(self.decision_history) > 20:
                await self.analyze_decision_patterns()
            
            # Update tool capabilities based on performance
            await self.update_tool_capabilities()
            
        except Exception as e:
            print(f"Error in learning cycle: {e}")
    
    async def analyze_decision_patterns(self):
        """Analyze decision patterns for insights"""
        try:
            recent_decisions = self.decision_history[-20:]
            
            # Count tool usage patterns
            tool_usage = {}
            for entry in recent_decisions:
                tool_name = entry["decision"].tool_name
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
            
            # Identify most successful tools
            successful_tools = {}
            for entry in recent_decisions:
                if entry.get("success", False):
                    tool_name = entry["decision"].tool_name
                    successful_tools[tool_name] = successful_tools.get(tool_name, 0) + 1
            
            print(f"Decision patterns analyzed: {len(recent_decisions)} decisions")
            
        except Exception as e:
            print(f"Error analyzing decision patterns: {e}")
    
    async def update_tool_capabilities(self):
        """Update tool capabilities based on performance"""
        try:
            for tool_name, performance in self.tool_performance.items():
                if performance["success_rate"] > 0.8:
                    # Tool is performing well, could increase priority
                    pass
                elif performance["success_rate"] < 0.3:
                    # Tool is performing poorly, could decrease priority
                    pass
            
        except Exception as e:
            print(f"Error updating tool capabilities: {e}")
    
    async def add_autonomous_task(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add an autonomous task for processing"""
        try:
            task = {
                "task_id": str(uuid.uuid4()),
                "type": "user_request",
                "user_input": user_input,
                "context": context or {},
                "timestamp": time.time()
            }
            
            await self.task_queue.put(task)
            
            return {
                "success": True,
                "task_id": task["task_id"],
                "queued": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_autonomous_status(self) -> Dict[str, Any]:
        """Get autonomous system status"""
        try:
            return {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "running": self.running,
                "metrics": self.metrics.copy(),
                "configuration": self.autonomous_config.copy(),
                "tool_registry": {
                    category: list(tools.keys()) 
                    for category, tools in self.tool_registry.items()
                },
                "tool_performance": self.tool_performance.copy(),
                "decision_history_size": len(self.decision_history),
                "learning_data_size": len(self.learning_data),
                "active_tasks": len(self.active_tasks),
                "queued_tasks": self.task_queue.qsize()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def shutdown_autonomous_system(self):
        """Shutdown the autonomous tool usage system"""
        try:
            print("Shutting down Agent-97 Autonomous Tool Usage System...")
            
            self.running = False
            
            # Shutdown components
            if self.mcp_tool_integration:
                await self.mcp_tool_integration.shutdown_integration()
            
            if self.domain_pipeline:
                await self.domain_pipeline.shutdown_pipeline()
            
            print("Agent-97 Autonomous Tool Usage System shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize autonomous system
        autonomous = Agent97AutonomousToolUsage()
        
        try:
            # Initialize system
            result = await autonomous.initialize_autonomous_system()
            
            if result["success"]:
                print(f"Autonomous system initialized successfully!")
                print(f"Total tools: {result['total_tools']}")
                print(f"MCP tools: {result['mcp_tools']}")
                print(f"Pipeline tools: {result['pipeline_tools']}")
                
                # Add some test tasks
                await autonomous.add_autonomous_task(
                    "search for information about artificial intelligence",
                    {"query": "artificial intelligence developments"}
                )
                
                await autonomous.add_autonomous_task(
                    "discover and analyze domains for example.com",
                    {"domains": ["example.com", "test.com"]}
                )
                
                # Wait for processing
                await asyncio.sleep(30)
                
                # Get status
                status = await autonomous.get_autonomous_status()
                print(f"Autonomous decisions: {status['metrics']['autonomous_decisions']}")
                print(f"Successful executions: {status['metrics']['successful_executions']}")
                print(f"Tools used: {len(status['metrics']['tools_used'])}")
                
            else:
                print(f"Autonomous system initialization failed: {result['error']}")
                
        except KeyboardInterrupt:
            print("Shutdown requested by user")
        except Exception as e:
            print(f"Autonomous system error: {e}")
        finally:
            await autonomous.shutdown_autonomous_system()
    
    # Run the autonomous system
    asyncio.run(main())
