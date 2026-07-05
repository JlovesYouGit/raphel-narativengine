"""
Test Agent-97 Autonomous Tool Usage
Test script for autonomous tool selection and execution
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from agent97_autonomous_tool_usage import Agent97AutonomousToolUsage

async def test_autonomous_tool_usage():
    """Test the autonomous tool usage system"""
    print("=== Agent-97 Autonomous Tool Usage Test ===\n")
    
    # Initialize autonomous system
    print("1. Initializing autonomous tool usage system...")
    autonomous = Agent97AutonomousToolUsage()
    
    try:
        # Initialize the system
        result = await autonomous.initialize_autonomous_system()
        
        if not result["success"]:
            print(f"   FAILED: {result['error']}")
            return False
        
        print(f"   SUCCESS: Autonomous system initialized")
        print(f"   MCP tools: {result['mcp_tools']}")
        print(f"   Pipeline tools: {result['pipeline_tools']}")
        print(f"   Total tools: {result['total_tools']}")
        
        # Test 1: Add search task
        print("\n2. Testing autonomous search task...")
        search_task = await autonomous.add_autonomous_task(
            "search for information about quantum computing",
            {"query": "quantum computing developments", "max_results": 5}
        )
        
        if search_task["success"]:
            print(f"   SUCCESS: Search task queued (ID: {search_task['task_id'][:8]}...)")
        else:
            print(f"   FAILED: {search_task['error']}")
        
        # Test 2: Add domain discovery task
        print("\n3. Testing autonomous domain discovery task...")
        domain_task = await autonomous.add_autonomous_task(
            "discover and analyze domains for security testing",
            {"domains": ["example.com", "test.com"], "analysis_type": "security"}
        )
        
        if domain_task["success"]:
            print(f"   SUCCESS: Domain task queued (ID: {domain_task['task_id'][:8]}...)")
        else:
            print(f"   FAILED: {domain_task['error']}")
        
        # Test 3: Add cache operation task
        print("\n4. Testing autonomous cache operation task...")
        cache_task = await autonomous.add_autonomous_task(
            "store important data in cache for later use",
            {
                "cache_key": "test_data",
                "cache_value": {"important": "data", "timestamp": "2024-04-07"},
                "ttl": 3600
            }
        )
        
        if cache_task["success"]:
            print(f"   SUCCESS: Cache task queued (ID: {cache_task['task_id'][:8]}...)")
        else:
            print(f"   FAILED: {cache_task['error']}")
        
        # Test 4: Add web fetch task
        print("\n5. Testing autonomous web fetch task...")
        fetch_task = await autonomous.add_autonomous_task(
            "fetch content from a website for analysis",
            {"url": "https://example.com", "include_screenshot": False}
        )
        
        if fetch_task["success"]:
            print(f"   SUCCESS: Fetch task queued (ID: {fetch_task['task_id'][:8]}...)")
        else:
            print(f"   FAILED: {fetch_task['error']}")
        
        # Wait for autonomous processing
        print("\n6. Waiting for autonomous processing...")
        await asyncio.sleep(20)  # Give time for processing
        
        # Test 5: Check autonomous status
        print("\n7. Testing autonomous status...")
        status = await autonomous.get_autonomous_status()
        
        if "error" not in status:
            print(f"   SUCCESS: Status retrieved")
            print(f"   - Running: {status['running']}")
            print(f"   - Autonomous decisions: {status['metrics']['autonomous_decisions']}")
            print(f"   - Successful executions: {status['metrics']['successful_executions']}")
            print(f"   - Failed executions: {status['metrics']['failed_executions']}")
            print(f"   - Tools used: {len(status['metrics']['tools_used'])}")
            print(f"   - Decision history size: {status['decision_history_size']}")
            print(f"   - Learning data size: {status['learning_data_size']}")
            print(f"   - Active tasks: {status['active_tasks']}")
            print(f"   - Queued tasks: {status['queued_tasks']}")
            
            if status['metrics']['tools_used']:
                print(f"   - Tools used: {', '.join(status['metrics']['tools_used'])}")
        else:
            print(f"   FAILED: {status['error']}")
        
        # Test 6: Check tool performance
        print("\n8. Testing tool performance analysis...")
        if status.get("tool_performance"):
            print(f"   SUCCESS: Tool performance data available")
            for tool_name, perf in status["tool_performance"].items():
                print(f"   - {tool_name}: {perf['success_rate']:.2%} success rate, "
                      f"{perf['avg_response_time']:.2f}s avg time")
        else:
            print("   INFO: No tool performance data yet (needs more executions)")
        
        # Test 7: Test learning adaptation
        print("\n9. Testing learning adaptation...")
        learning_improvements = status['metrics']['learning_improvements']
        print(f"   Learning improvements: {learning_improvements}")
        
        if learning_improvements > 0:
            print("   SUCCESS: Learning adaptation is working")
        else:
            print("   INFO: Learning adaptation needs more data")
        
        print("\n=== Test Summary ===")
        print("Autonomous Tool Usage test completed!")
        print("The system should have:")
        print("- Automatically selected appropriate tools for each task")
        print("- Executed tools based on context and requirements")
        print("- Learned from execution results")
        print("- Adapted decision thresholds")
        
        return True
        
    except Exception as e:
        print(f"   FAILED: {str(e)}")
        return False
    
    finally:
        # Cleanup
        print("\n10. Cleaning up...")
        await autonomous.shutdown_autonomous_system()
        print("    SUCCESS: Autonomous system shutdown complete")

async def test_context_analysis():
    """Test context analysis capabilities"""
    print("\n=== Context Analysis Test ===\n")
    
    autonomous = Agent97AutonomousToolUsage()
    
    try:
        # Test different contexts
        test_contexts = [
            {
                "name": "Search Intent",
                "context": {
                    "user_input": "I need to find information about machine learning",
                    "current_task": "research on AI topics"
                }
            },
            {
                "name": "Analysis Intent",
                "context": {
                    "user_input": "Analyze the security of this domain",
                    "current_task": "security assessment"
                }
            },
            {
                "name": "Storage Intent",
                "context": {
                    "user_input": "Save this data for later use",
                    "current_task": "data persistence"
                }
            },
            {
                "name": "Domain Discovery",
                "context": {
                    "user_input": "Find subdomains for example.com",
                    "current_task": "domain enumeration"
                }
            }
        ]
        
        for test_case in test_contexts:
            print(f"Testing {test_case['name']}...")
            
            # Initialize context analyzer
            await autonomous.initialize_context_analyzer()
            
            # Analyze intent
            intent = autonomous.analyze_user_intent(test_case["context"])
            print(f"   Detected intent: {intent}")
            
            # Analyze requirements
            requirements = autonomous.analyze_task_requirements(test_case["context"])
            print(f"   Requirements: {', '.join(requirements) if requirements else 'None'}")
            
            print(f"   SUCCESS: Context analyzed\n")
        
        return True
        
    except Exception as e:
        print(f"   FAILED: {str(e)}")
        return False

async def test_tool_selection():
    """Test tool selection logic"""
    print("\n=== Tool Selection Test ===\n")
    
    autonomous = Agent97AutonomousToolUsage()
    
    try:
        # Initialize components
        await autonomous.initialize_context_analyzer()
        await autonomous.register_available_tools()
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Web Search Scenario",
                "context": {
                    "user_input": "Search for latest AI news",
                    "query": "artificial intelligence news 2024"
                }
            },
            {
                "name": "Domain Analysis Scenario",
                "context": {
                    "user_input": "Analyze the security of example.com",
                    "domains": ["example.com"]
                }
            },
            {
                "name": "Cache Operation Scenario",
                "context": {
                    "user_input": "Store analysis results in cache",
                    "cache_key": "analysis_results",
                    "cache_value": {"data": "test"}
                }
            }
        ]
        
        for scenario in test_scenarios:
            print(f"Testing {scenario['name']}...")
            
            # Make tool decision
            decision = await autonomous.make_autonomous_tool_decision(scenario["context"])
            
            if decision:
                print(f"   Selected tool: {decision.tool_name}")
                print(f"   Confidence: {decision.confidence:.2f}")
                print(f"   Reasoning: {decision.reasoning}")
                print(f"   Parameters: {decision.parameters}")
                print(f"   Expected outcome: {decision.expected_outcome}")
                print(f"   SUCCESS: Tool decision made\n")
            else:
                print(f"   FAILED: No tool decision made\n")
        
        return True
        
    except Exception as e:
        print(f"   FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Agent-97 Autonomous Tool Usage Tests...\n")
    
    async def run_all_tests():
        """Run all tests"""
        tests = [
            ("Autonomous Tool Usage", test_autonomous_tool_usage),
            ("Context Analysis", test_context_analysis),
            ("Tool Selection", test_tool_selection)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"Running {test_name} Test")
            print('='*50)
            
            try:
                result = await test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"\n=== {test_name} PASSED ===")
                else:
                    print(f"\n=== {test_name} FAILED ===")
                    
            except Exception as e:
                print(f"\n=== {test_name} ERROR ===\n{e}")
                results.append((test_name, False))
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print('='*50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASSED" if result else "FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("=== ALL TESTS PASSED ===")
            return True
        else:
            print("=== SOME TESTS FAILED ===")
            return False
    
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n=== TESTS INTERRUPTED ===")
        sys.exit(1)
    except Exception as e:
        print(f"\n=== TEST ERROR ===\n{e}")
        sys.exit(1)
