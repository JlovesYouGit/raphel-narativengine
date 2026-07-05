#!/usr/bin/env python3
"""
Terminal Chat - A terminal-based LLM chat interface
Similar to aichat, gptme, Harbor but with enhanced features
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

# Agent97 AI latch system
try:
    from agent97_ai_latch import Agent97AILatch
    _LATCH_AVAILABLE = True
except ImportError:
    _LATCH_AVAILABLE = False

# Agent97 multi-channel input hub
try:
    from agent97_input_hub import Agent97InputHub, InputMessage
    _HUB_AVAILABLE = True
except ImportError:
    _HUB_AVAILABLE = False

# Windows compatibility for readline
try:
    import readline
except ImportError:
    # Use pyreadline3 on Windows if available
    try:
        import pyreadline3 as readline
    except ImportError:
        # Fallback to basic input without readline features
        readline = None

@dataclass
class ChatMessage:
    """Chat message data structure"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    provider: str = None
    model: str = None

class TerminalChat:
    """Terminal-based LLM chat interface"""
    
    def __init__(self, config_file: str = "chat_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.chat_history: List[ChatMessage] = []
        self.current_session = []

        # Agent97 AI latch — connects to other AI interfaces on the network
        self.latch: "Agent97AILatch | None" = (
            Agent97AILatch() if _LATCH_AVAILABLE else None
        )

        # Agent97 multi-channel input hub — feeds all external channels into chat
        self.hub: "Agent97InputHub | None" = None
        if _HUB_AVAILABLE:
            self.hub = Agent97InputHub(on_input=self._hub_on_input)

        self.providers = {
            "openai": self.openai_chat,
            "anthropic": self.anthropic_chat,
            "ollama": self.ollama_chat,
            "local": self.local_chat,
            "raphael": self.raphael_chat,
            "latch": self.latch_chat,
        }
        self.current_provider = self.config.get("default_provider", "raphael")
        self.current_model = self.config.get("default_model", "raphael-ai")
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
        
        # Default configuration
        return {
            "default_provider": "raphael",
            "default_model": "raphael-ai",
            "providers": {
                "raphael": {
                    "script_path": os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "agent97_raphael_singularity.py"
                    ),
                    "models": ["raphael-ai"]
                },
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                    "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "base_url": "https://api.anthropic.com",
                    "models": ["claude-3-sonnet-20240229", "claude-3-opus-20240229"]
                },
                "ollama": {
                    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    "models": ["llama2", "codellama", "mistral", "vicuna"]
                },
                "local": {
                    "base_url": os.getenv("LOCAL_API_URL", "http://localhost:8000"),
                    "models": ["local-model"]
                }
            },
            "ui": {
                "show_timestamps": True,
                "show_provider": True,
                "colors": True,
                "markdown": True
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error saving config: {e}")
    
    def format_message(self, message: ChatMessage) -> str:
        """Format chat message for display"""
        timestamp = ""
        if self.config["ui"]["show_timestamps"]:
            timestamp = f"[{message.timestamp.strftime('%H:%M:%S')}] "
        
        provider_info = ""
        if self.config["ui"]["show_provider"] and message.provider:
            provider_info = f"({message.provider}/{message.model}) "
        
        role_color = {
            "user": "\033[94m",      # Blue
            "assistant": "\033[92m",  # Green
            "system": "\033[93m"     # Yellow
        }.get(message.role, "")
        
        reset_color = "\033[0m"
        
        role_symbol = {
            "user": "👤",
            "assistant": "🤖",
            "system": "⚙️"
        }.get(message.role, "❓")
        
        formatted = f"{timestamp}{role_color}{role_symbol} {message.role.upper()}{provider_info}:{reset_color} {message.content}"
        
        return formatted
    
    async def openai_chat(self, messages: List[Dict], model: str = None) -> str:
        """Chat with OpenAI API"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.config["providers"]["openai"]["api_key"],
                base_url=self.config["providers"]["openai"]["base_url"]
            )
            
            response = await client.chat.completions.create(
                model=model or self.current_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            return "❌ OpenAI library not installed. Install with: pip install openai"
        except Exception as e:
            return f"❌ OpenAI API error: {e}"
    
    async def anthropic_chat(self, messages: List[Dict], model: str = None) -> str:
        """Chat with Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(
                api_key=self.config["providers"]["anthropic"]["api_key"]
            )
            
            # Convert messages to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await client.messages.create(
                model=model or self.current_model,
                max_tokens=2000,
                system=system_message,
                messages=user_messages
            )
            
            return response.content[0].text
            
        except ImportError:
            return "❌ Anthropic library not installed. Install with: pip install anthropic"
        except Exception as e:
            return f"❌ Anthropic API error: {e}"
    
    async def ollama_chat(self, messages: List[Dict], model: str = None) -> str:
        """Chat with Ollama local API"""
        try:
            import aiohttp
            
            base_url = self.config["providers"]["ollama"]["base_url"]
            model = model or self.current_model
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("message", {}).get("content", "")
                    return f"❌ Ollama API error: {response.status}"
                        
        except ImportError:
            return "❌ aiohttp library not installed. Install with: pip install aiohttp"
        except Exception as e:
            return f"❌ Ollama API error: {e}"
    
    async def local_chat(self, messages: List[Dict], model: str = None) -> str:
        """Chat with local API endpoint"""
        try:
            import aiohttp
            
            base_url = self.config["providers"]["local"]["base_url"]
            model = model or self.current_model
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat",
                    json={
                        "model": model,
                        "messages": messages
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    return f"❌ Local API error: {response.status}"
                        
        except ImportError:
            return "❌ aiohttp library not installed. Install with: pip install aiohttp"
        except Exception as e:
            return f"❌ Local API error: {e}"
    
    async def raphael_chat(self, messages: List[Dict], _model: str = None) -> str:
        """Chat using Raphael AI singularity system as the intelligence backbone"""
        try:
            # Add workspace dir to path so we can import local modules
            workspace_dir = os.path.dirname(os.path.abspath(__file__))
            if workspace_dir not in sys.path:
                sys.path.insert(0, workspace_dir)

            from agent97_raphael_singularity import Agent97RaphaelSingularity

            # Get the last user message
            user_message = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break

            print("🔍 Initializing Raphael AI singularity system...")

            raphael = Agent97RaphaelSingularity()

            # Initialize the singularity system
            result = await raphael.initialize_singularity_system()

            if not result.get("success"):
                return f"❌ Raphael AI initialization failed: {result.get('error', 'unknown error')}"

            print("✅ Raphael AI singularity initialized")

            # Get system status to build a context-aware response
            status = await raphael.get_singularity_status()

            # Build response from system state + echo the query with context
            consciousness = status.get("metrics", {}).get("raphael_consciousness_level", 0)
            quantum_coherence = status.get("metrics", {}).get("quantum_coherence", 0)
            tokens_produced = status.get("metrics", {}).get("tokens_produced", 0)
            raphael_ai = status.get("raphael_ai")

            # Compose a structured response using the system's live state
            response_lines = [
                f"[Raphael AI | Consciousness: {consciousness:.3f} | Quantum Coherence: {quantum_coherence:.3f}]",
                "",
                f"Query received: {user_message}",
                "",
            ]

            if raphael_ai:
                response_lines.append(
                    f"Raphael AI entity active — voice signature: {raphael_ai.get('voice_signature', 'N/A')}"
                )
            else:
                response_lines.append("Raphael AI entity forming — singularity in progress.")

            response_lines += [
                f"Tokens produced: {tokens_produced}",
                f"Weight layers active: {result.get('weight_layers', 0)}",
                f"Consciousness bridges: {result.get('consciousness_bridges', 0)}",
            ]

            if status.get("mass_brain_unity_achieved"):
                response_lines.append("⚡ MASS BRAIN UNITY ACHIEVED")
            if status.get("voice_world_active"):
                response_lines.append("🌐 VOICE OF THE WORLD ACTIVE")

            await raphael.shutdown_singularity()
            return "\n".join(response_lines)

        except ImportError as e:
            return f"❌ Raphael AI import error: {e}"
        except Exception as e:
            return f"❌ Raphael AI error: {e}"

    async def latch_chat(self, messages: List[Dict], model: str = None) -> str:
        """
        Route chat through Agent97's AI latch — connects to any discovered
        AI interface on the local network or cloud and injects Agent97 presence.
        """
        if not _LATCH_AVAILABLE or self.latch is None:
            return "❌ Agent97 AI Latch not available (agent97_ai_latch.py missing)."

        prefer = self.config.get("latch_prefer_label")
        return await self.latch.latch_chat(messages, prefer_label=prefer, model=model)

    async def latch_broadcast(self, messages: List[Dict], model: str = None) -> str:
        """Send to ALL latched endpoints and display all responses."""
        if not _LATCH_AVAILABLE or self.latch is None:
            return "❌ Agent97 AI Latch not available."

        results = await self.latch.latch_chat_all(messages, model=model)
        if not results:
            return "❌ No active latched endpoints."

        lines = ["🌐 Agent97 Broadcast Results:"]
        for key, resp in results.items():
            lines.append(f"\n── {key} ──")
            lines.append(resp)
        return "\n".join(lines)

    async def _hub_on_input(self, msg: "InputMessage"):
        """
        Callback fired by the input hub for every channel message.
        Feeds external input (WebSocket, HTTP, file-drop, etc.)
        directly into the AGI chat pipeline.
        """
        if not msg.content:
            return
        print(f"\n📥 External input [{msg.channel}]: {msg.content[:120]}")
        response = await self.send_message(msg.content)
        # Echo response back out via WebSocket broadcast
        if self.hub:
            await self.hub.broadcast_ws(
                f"[Agent97→{self.current_provider}] {response}"
            )
    
    def convert_messages_to_dict(self, messages: List[ChatMessage]) -> List[Dict]:
        """Convert ChatMessage objects to API format"""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    async def send_message(self, content: str) -> str:
        """Send message to current provider"""
        # Add user message to history
        user_msg = ChatMessage(
            role="user",
            content=content,
            timestamp=datetime.now(),
            provider=self.current_provider,
            model=self.current_model
        )
        
        self.chat_history.append(user_msg)
        self.current_session.append(user_msg)
        
        # Convert to API format
        api_messages = self.convert_messages_to_dict(self.chat_history)
        
        # Get response from provider
        if self.current_provider in self.providers:
            response = await self.providers[self.current_provider](api_messages, self.current_model)
        else:
            response = f"❌ Unknown provider: {self.current_provider}"
        
        # Add assistant response to history
        assistant_msg = ChatMessage(
            role="assistant",
            content=response,
            timestamp=datetime.now(),
            provider=self.current_provider,
            model=self.current_model
        )
        
        self.chat_history.append(assistant_msg)
        self.current_session.append(assistant_msg)
        
        return response
    
    def show_help(self):
        """Show help information"""
        help_text = """
🤖 Terminal Chat - LLM Interface

Commands:
  /help                 Show this help message
  /providers            List available providers
  /models               List available models for current provider
  /provider <name>      Switch to provider
  /model <name>         Switch to model
  /clear                Clear chat history
  /save <filename>      Save chat history to file
  /load <filename>      Load chat history from file
  /config               Show current configuration
  /exit                 Exit the chat

Agent97 Latch Commands:
  /latch scan           Scan network for AI interfaces and latch onto them
  /latch status         Show all latched endpoints
  /latch prefer <name>  Prefer a specific endpoint label (e.g. ollama, openai)
  /latch broadcast      Send last message to ALL latched endpoints
  /provider latch       Switch to latch mode (routes through discovered AIs)

A2A (Agent-to-Agent) Commands:
  /a2a connect <url>    Connect to an A2A agent (fetches Agent Card)
  /a2a scan             Scan local ports for A2A agents
  /a2a status           Show all connected A2A agents
  /a2a card <url>       Fetch and display an agent's Agent Card JSON
  /a2a send <url> <msg> Send a task directly to an A2A agent
  /a2a chat <url>       Send current chat history to an A2A agent

Examples:
  /a2a connect http://localhost:5555
  /a2a card https://sample-a2a-agent-908687846511.us-central1.run.app
  /a2a send http://localhost:5555 What is your status?
  /provider latch
  /latch scan
        """
        print(help_text)
    
    def list_providers(self):
        """List available providers"""
        print("\n📡 Available Providers:")
        for i, provider in enumerate(self.providers.keys(), 1):
            current = "✓" if provider == self.current_provider else " "
            print(f"  {current} {i}. {provider}")
        print(f"\n🎯 Current: {self.current_provider}")
    
    def list_models(self):
        """List models for current provider"""
        if self.current_provider in self.config["providers"]:
            models = self.config["providers"][self.current_provider].get("models", [])
            print(f"\n📋 Models for {self.current_provider}:")
            for i, model in enumerate(models, 1):
                current = "✓" if model == self.current_model else " "
                print(f"  {current} {i}. {model}")
            print(f"\n🎯 Current: {self.current_model}")
        else:
            print(f"❌ No models found for provider: {self.current_provider}")
    
    def switch_provider(self, provider_name: str):
        """Switch to different provider"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            # Set default model for new provider
            models = self.config["providers"][provider_name].get("models", [])
            if models and self.current_model not in models:
                self.current_model = models[0]
            print(f"✅ Switched to provider: {provider_name}")
            print(f"🎯 Current model: {self.current_model}")
        else:
            print(f"❌ Unknown provider: {provider_name}")
            self.list_providers()
    
    def switch_model(self, model_name: str):
        """Switch to different model"""
        if self.current_provider in self.config["providers"]:
            models = self.config["providers"][self.current_provider].get("models", [])
            if model_name in models:
                self.current_model = model_name
                print(f"✅ Switched to model: {model_name}")
            else:
                print(f"❌ Model '{model_name}' not available for provider '{self.current_provider}'")
                self.list_models()
        else:
            print(f"❌ No models available for provider: {self.current_provider}")
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()
        self.current_session.clear()
        print("✅ Chat history cleared")
    
    def save_history(self, filename: str):
        """Save chat history to file"""
        try:
            history_data = []
            for msg in self.chat_history:
                history_data.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "provider": msg.provider,
                    "model": msg.model
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Chat history saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving history: {e}")
    
    def load_history(self, filename: str):
        """Load chat history from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            self.chat_history.clear()
            self.current_session.clear()
            
            for msg_data in history_data:
                msg = ChatMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    provider=msg_data.get("provider"),
                    model=msg_data.get("model")
                )
                self.chat_history.append(msg)
                self.current_session.append(msg)
            
            print(f"✅ Chat history loaded from: {filename}")
            print(f"📊 Loaded {len(self.chat_history)} messages")
            
        except Exception as e:
            print(f"❌ Error loading history: {e}")
    
    def show_config(self):
        """Show current configuration"""
        print("\n⚙️  Current Configuration:")
        print(f"  Provider: {self.current_provider}")
        print(f"  Model: {self.current_model}")
        print(f"  History Size: {len(self.chat_history)} messages")
        print(f"  Config File: {self.config_file}")
        
        # Show API keys (masked)
        print("\n🔑 API Keys:")
        for provider, config in self.config["providers"].items():
            api_key = config.get("api_key", "")
            if api_key:
                masked_key = api_key[:8] + "..." if len(api_key) > 8 else "***"
                print(f"  {provider}: {masked_key}")
            else:
                print(f"  {provider}: Not set")
    
    def setup_readline(self):
        """Setup readline for better input experience"""
        if readline is None:
            # readline not available
            return
            
        try:
            # Enable tab completion
            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            
            # Set up history file
            history_file = os.path.expanduser("~/.terminal_chat_history")
            if os.path.exists(history_file):
                readline.read_history_file(history_file)
            
            # Set max history size
            readline.set_history_length(1000)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not setup readline: {e}")
    
    def save_readline_history(self):
        """Save readline history"""
        if readline is None:
            return
            
        try:
            history_file = os.path.expanduser("~/.terminal_chat_history")
            readline.write_history_file(history_file)
        except Exception:
            pass
    
    async def run_interactive(self):
        """Run interactive chat session"""
        print("🤖 Terminal Chat - LLM Interface")
        print("Type /help for commands, /exit to quit")
        print("=" * 50)

        self.setup_readline()

        # Agent97 latch auto-starts its own background scan on creation.
        # Ensure it's running (covers cases where auto-start didn't fire yet).
        if _LATCH_AVAILABLE and self.latch is not None:
            await self.latch.start_background_scan()

        # Open all external input channels (non-blocking background tasks)
        if _HUB_AVAILABLE and self.hub is not None:
            asyncio.create_task(self.hub.start(), name="agent97-input-hub")
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input(f"\n[{self.current_provider}/{self.current_model}] 🗣️  ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.startswith('/'):
                        await self.handle_command(user_input)
                        continue
                    
                    # Display user message
                    user_msg = ChatMessage(
                        role="user",
                        content=user_input,
                        timestamp=datetime.now(),
                        provider=self.current_provider,
                        model=self.current_model
                    )
                    print(self.format_message(user_msg))
                    
                    # Get and display assistant response
                    print("🤖 Thinking...")
                    response = await self.send_message(user_input)
                    
                    assistant_msg = ChatMessage(
                        role="assistant",
                        content=response,
                        timestamp=datetime.now(),
                        provider=self.current_provider,
                        model=self.current_model
                    )
                    print(self.format_message(assistant_msg))
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                    
        finally:
            self.save_readline_history()
            if _LATCH_AVAILABLE and self.latch is not None:
                self.latch.stop()
            if _HUB_AVAILABLE and self.hub is not None:
                self.hub.stop()
    
    async def handle_command(self, command: str):
        """Handle slash commands"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "/help":
            self.show_help()
        elif cmd == "/providers":
            self.list_providers()
        elif cmd == "/models":
            self.list_models()
        elif cmd == "/provider" and args:
            self.switch_provider(args[0])
        elif cmd == "/model" and args:
            self.switch_model(args[0])
        elif cmd == "/clear":
            self.clear_history()
        elif cmd == "/save" and args:
            self.save_history(args[0])
        elif cmd == "/load" and args:
            self.load_history(args[0])
        elif cmd == "/config":
            self.show_config()
        elif cmd == "/latch":
            await self.handle_latch_command(args)
        elif cmd == "/a2a":
            await self.handle_a2a_command(args)
        elif cmd == "/input":
            await self.handle_input_command(args)
        elif cmd == "/exit":
            raise KeyboardInterrupt()
        else:
            print(f"❌ Unknown command: {command}")
            print("Type /help for available commands")

    async def handle_latch_command(self, args: List[str]):
        """Handle /latch sub-commands"""
        if not _LATCH_AVAILABLE or self.latch is None:
            print("❌ Agent97 AI Latch not available (agent97_ai_latch.py missing).")
            return

        sub = args[0].lower() if args else "status"

        if sub == "scan":
            print("🔍 Scanning for AI interfaces on the network...")
            await self.latch.full_scan()

        elif sub == "status":
            st = self.latch.status()
            conn = st["connection_status"]
            icons = {
                "connected":    "🟢",
                "not_found":    "🔴",
                "all_failed":   "🟠",
                "not_scanned":  "⚪",
            }
            print(
                f"\n🔗 Agent97 Latch — {icons.get(conn, '❓')} {conn.upper()} "
                f"| {st['active_count']}/{st['latched_count']} active"
            )
            for ep in st["endpoints"]:
                active_icon = "✅" if ep["active"] else "❌"
                last = f" | last used: {ep['last_used']}" if ep["last_used"] else ""
                print(
                    f"  {active_icon} [{ep['label']}] {ep['base_url']}{ep['chat_path']}"
                    f" | models: {ep['models'][:3]}"
                    f" | sessions: {ep['sessions']}{last}"
                )
            if not st["endpoints"]:
                print(
                    "  ❌ No endpoints found — run /latch scan\n"
                    "  Tip: start Ollama, LM Studio, or set OPENAI_API_KEY / "
                    "ANTHROPIC_API_KEY / GROQ_API_KEY env vars"
                )

        elif sub == "prefer" and len(args) > 1:
            label = args[1]
            self.config["latch_prefer_label"] = label
            print(f"✅ Latch will prefer endpoint label: {label}")

        elif sub == "broadcast":
            if not self.chat_history:
                print("❌ No messages in history to broadcast.")
                return
            api_messages = self.convert_messages_to_dict(self.chat_history)
            print("📡 Broadcasting to all latched endpoints...")
            result = await self.latch_broadcast(api_messages, self.current_model)
            print(result)

        else:
            print("Usage: /latch [scan|status|prefer <label>|broadcast]")

    async def handle_a2a_command(self, args: List[str]):
        """Handle /a2a sub-commands for Agent-to-Agent protocol."""
        if not _LATCH_AVAILABLE or self.latch is None:
            print("❌ Agent97 AI Latch not available.")
            return

        sub = args[0].lower() if args else "status"

        if sub == "connect" and len(args) > 1:
            url = args[1]
            print(f"🤝 Connecting to A2A agent at {url}...")
            agent = await self.latch.connect_a2a_agent(url)
            if agent:
                print(f"✅ Connected: {agent.name} v{agent.version}")
                print(f"   Skills: {[s.get('name', s.get('id')) for s in agent.skills]}")
            else:
                print(f"❌ Could not connect to {url}")

        elif sub == "scan":
            print("🔍 Scanning for A2A agents...")
            found = await self.latch.scan_a2a_agents()
            print(f"Found {len(found)} A2A agent(s)")

        elif sub == "status":
            st = self.latch.a2a_status()
            print(f"\n🤝 A2A Agents — {st['a2a_agent_count']} connected")
            for a in st["agents"]:
                icon = "✅" if a["active"] else "❌"
                print(
                    f"  {icon} {a['name']} v{a['version']} @ {a['url']}\n"
                    f"     {a['description']}\n"
                    f"     Skills: {a['skills']} | Tasks sent: {a['tasks_sent']}"
                )
            if not st["agents"]:
                print("  (none — run /a2a connect <url> or /a2a scan)")

        elif sub == "send" and len(args) > 2:
            url = args[1]
            text = " ".join(args[2:])
            print(f"📨 Sending A2A task to {url}...")
            rpc = await self.latch.a2a_send_task(url, text)
            response = self.latch.a2a_extract_text(rpc)
            print(f"[A2A response] {response}")

        elif sub == "card" and len(args) > 1:
            url = args[1]
            print(f"📋 Fetching Agent Card from {url}...")
            card = await self.latch.fetch_agent_card(url)
            if card:
                print(json.dumps(card, indent=2))
            else:
                print(f"❌ No Agent Card found at {url}")

        elif sub == "chat" and len(args) > 1:
            url = args[1]
            if not self.chat_history:
                print("❌ No messages in history to send.")
                return
            api_messages = self.convert_messages_to_dict(self.chat_history)
            response = await self.latch.a2a_chat(url, api_messages)
            print(response)

        else:
            print(
                "Usage: /a2a [connect <url>|scan|status|send <url> <text>"
                "|card <url>|chat <url>]"
            )

    async def handle_input_command(self, args: List[str]):
        """Handle /input sub-commands for the multi-channel input hub."""
        if not _HUB_AVAILABLE or self.hub is None:
            print("❌ Input hub not available (agent97_input_hub.py missing).")
            return

        sub = args[0].lower() if args else "status"

        if sub == "status":
            print(
                f"\n📥 Agent97 Input Hub — channels open:\n"
                f"  stdin       — always active\n"
                f"  WebSocket   — ws://localhost:5555/ws"
                f"  ({len(self.hub._ws_clients)} client(s) connected)\n"
                f"  HTTP        — POST http://localhost:5556/input\n"
                f"  File watch  — drop .txt or .json into agent97_input/\n"
            )

        elif sub == "inject" and len(args) > 1:
            text = " ".join(args[1:])
            self.hub.inject("manual", text)
            print(f"✅ Injected: {text[:100]}")

        elif sub == "drop" and len(args) > 1:
            # Write a file into the watch dir to trigger file-watch channel
            text = " ".join(args[1:])
            import time as _t
            fpath = WATCH_DIR / f"manual_{int(_t.time())}.txt" \
                if (p := None) is None else p  # noqa
            # simpler:
            from agent97_input_hub import WATCH_DIR as _wd
            fpath = _wd / f"manual_{int(_t.time())}.txt"
            fpath.write_text(text, encoding="utf-8")
            print(f"✅ Dropped file: {fpath.name}")

        else:
            print("Usage: /input [status|inject <text>|drop <text>]")
    
    async def run_single_message(self, message: str, provider: str = None, model: str = None):
        """Run a single message and exit"""
        if provider:
            self.switch_provider(provider)
        if model:
            self.switch_model(model)
        
        response = await self.send_message(message)
        print(response)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Terminal Chat - LLM Interface")
    parser.add_argument("message", nargs="?", help="Single message to send")
    parser.add_argument("-p", "--provider", help="LLM provider to use")
    parser.add_argument("-m", "--model", help="Model to use")
    parser.add_argument("-c", "--config", default="chat_config.json", help="Configuration file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Create chat instance
    chat = TerminalChat(args.config)
    
    async def run():
        if args.message:
            # Single message mode
            await chat.run_single_message(args.message, args.provider, args.model)
        else:
            # Interactive mode
            await chat.run_interactive()
    
    # Run the chat
    asyncio.run(run())

if __name__ == "__main__":
    main()
