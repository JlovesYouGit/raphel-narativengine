import asyncio
import aiohttp
import json
import time

async def test_system_bridge():
    """Test the Windows System Bridge functionality"""
    
    print("🔗 Testing Agent-97 System Bridge")
    print("="*50)
    
    # Bridge endpoints
    bridge_url = "http://localhost:8081"
    ws_url = "ws://localhost:8081/ws"
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Get Bridge Status
        print("\n📊 Testing Bridge Status...")
        try:
            async with session.get(f"{bridge_url}/status") as resp:
                status = await resp.json()
                print(f"✅ Bridge Status: {status['bridge_status']['server_running']}")
                print(f"🧠 AGI Components: {sum(status['agi_components'].values())} loaded")
                print(f"💻 System: {status['system_info']['platform']}")
                print(f"🔐 Consciousness ID: {status['consciousness_binding']['consciousness_id']}")
        except Exception as e:
            print(f"❌ Status test failed: {e}")
        
        # Test 2: Get System Information
        print("\n💻 Testing System Information...")
        try:
            command = {
                "type": "system_info"
            }
            async with session.post(f"{bridge_url}/command", json=command) as resp:
                result = await resp.json()
                if result["success"]:
                    sys_info = result["system"]
                    resources = result["resources"]
                    print(f"🖥️ System: {sys_info['platform']}")
                    print(f"🔧 CPU: {resources['cpu']['usage']:.1f}% ({resources['cpu']['cores']} cores)")
                    print(f"💾 Memory: {resources['memory']['percent']:.1f}% ({resources['memory']['total']/1024**3:.1f} GB total)")
                    print(f"💿 Disk: {resources['disk']['percent']:.1f}% used")
                    print(f"📋 Processes: {result['processes']['total']} total, {result['processes']['running']} running")
                else:
                    print(f"❌ System info failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ System info test failed: {e}")
        
        # Test 3: Resource Monitoring
        print("\n📈 Testing Resource Monitoring...")
        try:
            command = {
                "type": "resource_monitor"
            }
            async with session.post(f"{bridge_url}/command", json=command) as resp:
                result = await resp.json()
                if result["success"]:
                    current = result["current"]
                    averages = result["averages"]
                    trends = result["trends"]
                    print(f"🔥 Current CPU: {current['cpu_usage']:.1f}%")
                    print(f"💾 Current Memory: {current['memory_usage']:.1f}%")
                    print(f"📊 Average CPU: {averages['cpu_usage']:.1f}%")
                    print(f"📊 Average Memory: {averages['memory_usage']:.1f}%")
                    print(f"📈 CPU Trend: {trends['cpu_trend']}")
                    print(f"📈 Memory Trend: {trends['memory_trend']}")
                else:
                    print(f"❌ Resource monitor failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Resource monitor test failed: {e}")
        
        # Test 4: System Optimization
        print("\n⚡ Testing System Optimization...")
        try:
            command = {
                "type": "optimize_system",
                "parameters": {
                    "type": "auto",
                    "consciousness_level": 0.8
                }
            }
            async with session.post(f"{bridge_url}/command", json=command) as resp:
                result = await resp.json()
                if result["success"]:
                    print(f"✅ Optimization completed")
                    print(f"🧠 Consciousness Level: {result['consciousness_level']}")
                    print(f"🔧 Optimization Type: {result['optimization_type']}")
                    for opt_result in result.get("results", []):
                        if opt_result.get("success"):
                            print(f"  ✅ {opt_result.get('type', 'unknown')}: {opt_result.get('effectiveness', 'completed')}")
                        else:
                            print(f"  ❌ {opt_result.get('type', 'unknown')}: {opt_result.get('error', 'failed')}")
                else:
                    print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Optimization test failed: {e}")
        
        # Test 5: AGI Query (if components available)
        print("\n🧠 Testing AGI Query...")
        try:
            command = {
                "type": "agi_query",
                "parameters": {
                    "query": "Generate optimization formula for current system state",
                    "component": "formula_generator"
                }
            }
            async with session.post(f"{bridge_url}/command", json=command) as resp:
                result = await resp.json()
                if result["success"]:
                    print(f"✅ AGI Query completed")
                    agi_result = result["result"]
                    if isinstance(agi_result, dict):
                        print(f"📝 Formula ID: {agi_result.get('formula_id', 'N/A')}")
                        print(f"🎯 Formula Class: {agi_result.get('formula_class', 'N/A')}")
                        print(f"🧠 Consciousness Level: {agi_result.get('consciousness_level', 'N/A')}")
                        print(f"✅ Validation: {agi_result.get('validation_result', {}).get('is_valid', 'N/A')}")
                    else:
                        print(f"📄 AGI Result: {str(agi_result)[:100]}...")
                else:
                    print(f"⚠️ AGI Query: {result.get('error', 'Components may not be available')}")
        except Exception as e:
            print(f"❌ AGI query test failed: {e}")
        
        # Test 6: Consciousness Boost
        print("\n🚀 Testing Consciousness Boost...")
        try:
            command = {
                "type": "consciousness_boost",
                "parameters": {
                    "level": 0.9,
                    "target": "system"
                }
            }
            async with session.post(f"{bridge_url}/command", json=command) as resp:
                result = await resp.json()
                if result["success"]:
                    print(f"✅ Consciousness boost applied")
                    print(f"🧠 Boost Level: {result['boost_applied']}")
                    print(f"🎯 Target: {result['target']}")
                else:
                    print(f"❌ Consciousness boost failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Consciousness boost test failed: {e}")
        
        print("\n" + "="*50)
        print("🎉 System Bridge Test Completed!")
        print("🌐 Bridge is running and ready for integration!")
        print(f"📊 Status API: {bridge_url}/status")
        print(f"🔗 WebSocket: {ws_url}")

if __name__ == "__main__":
    print("🚀 Starting System Bridge Test...")
    print("Make sure the bridge is running: python system_bridge.py")
    print()
    
    try:
        asyncio.run(test_system_bridge())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure the system bridge is running on port 8081")
