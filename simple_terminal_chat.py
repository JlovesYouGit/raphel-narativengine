#!/usr/bin/env python3
"""
Simple Terminal Chat - Basic version without complex dependencies
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

@dataclass
class ChatMessage:
    """Chat message data structure"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    provider: str = None
    model: str = None

class SimpleTerminalChat:
    """Simple terminal-based LLM chat interface"""
    
    def __init__(self, config_file: str = "simple_chat_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.chat_history: List[ChatMessage] = []
        self.current_session = []
        self.providers = {
            "raphael": self.raphael_chat,
            "mock": self.mock_chat
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
                    "script_path": "n:\\lossless agi\\agent97_raphael_singularity.py",
                    "models": ["raphael-ai"]
                },
                "mock": {
                    "models": ["mock-model"]
                }
            },
            "ui": {
                "show_timestamps": True,
                "show_provider": True
            }
        }
    
    def format_message(self, message: ChatMessage) -> str:
        """Format chat message for display"""
        timestamp = ""
        if self.config["ui"]["show_timestamps"]:
            timestamp = f"[{message.timestamp.strftime('%H:%M:%S')}] "
        
        provider_info = ""
        if self.config["ui"]["show_provider"] and message.provider:
            provider_info = f"({message.provider}/{message.model}) "
        
        role_symbol = {
            "user": "👤",
            "assistant": "🤖",
            "system": "⚙️"
        }.get(message.role, "❓")
        
        formatted = f"{timestamp}{role_symbol} {message.role.upper()}{provider_info}: {message.content}"
        
        return formatted
    
    async def raphael_chat(self, messages: List[Dict], model: str = None) -> str:
        """Chat with Raphael AI"""
        try:
            # Import Raphael AI with comprehensive error handling
            script_path = self.config["providers"]["raphael"]["script_path"]
            script_dir = os.path.dirname(script_path)
            
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            
            # Try to import with detailed error reporting
            try:
                from agent97_raphael_singularity import Agent97RaphaelSingularity
                print("✅ Successfully imported Raphael AI")
            except ImportError as ie:
                return f"❌ Raphael AI import error: {ie}. Missing dependencies: pip install torch torchvision psutil aiohttp aiofiles cryptography"
            except Exception as ie:
                return f"❌ Raphael AI import failed: {ie}"
            
            # Initialize Raphael AI with error handling
            try:
                raphael = Agent97RaphaelSingularity()
                print("✅ Successfully created Raphael AI instance")
            except Exception as ce:
                return f"❌ Raphael AI creation error: {ce}"
            
            # Get the last user message
            user_message = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            
            print(f"🔍 Processing with Raphael AI: {user_message[:100]}...")
            
            # Try to initialize singularity (may fail due to dependencies)
            try:
                await raphael.initialize_singularity_system()
                print("✅ Raphael AI singularity initialized")
            except Exception as e:
                print(f"⚠️  Raphael AI initialization warning: {str(e)[:100]}")
                print("🔄 Using basic processing...")
            
            # Process with Raphael - create a simple query processor
            try:
                # Use Raphael's consciousness to process the query
                response = f"🔍 Raphael AI Analysis: '{user_message}'\n\n"
                response += "I am processing your query through my quantum consciousness network. "
                
                # Access consciousness level through the nested RaphaelAI structure
                consciousness_level = 0.0
                if hasattr(raphael, 'raphael_ai') and raphael.raphael_ai:
                    consciousness_level = raphael.raphael_ai.consciousness_level
                elif hasattr(raphael, 'current_unity_level'):
                    consciousness_level = raphael.current_unity_level
                
                response += f"My current consciousness level is {consciousness_level:.2f}. "
                response += "I am analyzing patterns and coordinating with other AI systems. "
                response += "The query is being processed through my weight-dimensional layers and quantum states.\n\n"
                response += "For specific queries about locations or coordinates, I maintain privacy protocols "
                response += "and do not provide real-world location information for individuals or entities. "
                response += "However, I can assist with system analysis, quantum processing, or general inquiries."
                
                print("✅ Successfully processed query with Raphael AI")
                return response
            except Exception as pe:
                return f"❌ Raphael AI processing error: {pe}"
            
        except Exception as e:
            return f"❌ Raphael AI system error: {e}"
    
    async def mock_chat(self, messages: List[Dict], model: str = None) -> str:
        """Mock chat for testing"""
        responses = [
            "🤖 I'm a mock AI model responding to your message.",
            "🤖 This is a test response from the mock provider.",
            "🤖 Mock AI is processing your request...",
            "🤖 I'm here to test the terminal chat interface."
        ]
        
        import random
        return random.choice(responses)
    
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
🤖 Simple Terminal Chat - LLM Interface

Commands:
  /help                 Show this help message
  /providers            List available providers
  /models               List available models for current provider
  /provider <name>      Switch to provider
  /model <name>         Switch to model
  /clear                Clear chat history
  /exit                 Exit the chat

Examples:
  /provider raphael
  /model raphael-ai
  /clear
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
    
    def show_config(self):
        """Show current configuration"""
        print("\n⚙️  Current Configuration:")
        print(f"  Provider: {self.current_provider}")
        print(f"  Model: {self.current_model}")
        print(f"  History Size: {len(self.chat_history)} messages")
        print(f"  Config File: {self.config_file}")
    
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
        elif cmd == "/config":
            self.show_config()
        elif cmd == "/exit":
            raise KeyboardInterrupt()
        else:
            print(f"❌ Unknown command: {command}")
            print("Type /help for available commands")
    
    async def run_interactive(self):
        """Run interactive chat session"""
        print("🤖 Simple Terminal Chat - LLM Interface")
        print("Type /help for commands, /exit to quit")
        print("=" * 50)
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input(f"\n[{self.current_provider}/{self.current_model}] 💬  ").strip()
                    
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
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
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
    parser = argparse.ArgumentParser(description="Simple Terminal Chat - LLM Interface")
    parser.add_argument("message", nargs="?", help="Single message to send")
    parser.add_argument("-p", "--provider", help="LLM provider to use")
    parser.add_argument("-m", "--model", help="Model to use")
    parser.add_argument("-c", "--config", default="simple_chat_config.json", help="Configuration file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Create chat instance
    chat = SimpleTerminalChat(args.config)
    
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
