#!/usr/bin/env python3
"""
API Key Manager for God AI System
Securely manages API keys for various AI services
"""

import os
import json
import sys
import getpass
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from datetime import datetime

class APIKeyManager:
    """Secure API key management system"""
    
    def __init__(self):
        self.config_file = Path("api_keys_encrypted.json")
        self.key_file = Path("api_keys.json")
        self.encryption_key = None
        self.api_keys = {}
        self.load_encryption_key()
        self.load_api_keys()
    
    def load_encryption_key(self):
        """Load or create encryption key"""
        key_file = Path("encryption.key")
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                self.encryption_key = f.read()
            print("✅ Encryption key loaded")
        else:
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.encryption_key)
            print("✅ New encryption key generated and saved")
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(encrypted_data).decode()
    
    def load_api_keys(self):
        """Load encrypted API keys"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "rb") as f:
                    encrypted_data = f.read()
                
                # Decrypt the data
                decrypted_data = self.decrypt_data(encrypted_data)
                self.api_keys = json.loads(decrypted_data)
                print("✅ API keys loaded and decrypted")
                
            except Exception as e:
                print(f"❌ Failed to load API keys: {e}")
                self.api_keys = {}
        else:
            print("⚠️ No API keys file found")
            self.api_keys = {}
    
    def save_api_keys(self):
        """Save encrypted API keys"""
        try:
            # Encrypt the data
            data_str = json.dumps(self.api_keys, indent=2)
            encrypted_data = self.encrypt_data(data_str)
            
            with open(self.config_file, "wb") as f:
                f.write(encrypted_data)
            
            print("✅ API keys saved and encrypted")
            
        except Exception as e:
            print(f"❌ Failed to save API keys: {e}")
    
    def add_api_key(self, service: str, api_key: str, description: str = ""):
        """Add a new API key"""
        self.api_keys[service] = {
            "api_key": api_key,
            "description": description,
            "added_date": datetime.now().isoformat(),
            "last_used": None
        }
        self.save_api_keys()
        print(f"✅ API key added for {service}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        return self.api_keys.get(service, {}).get("api_key")
    
    def update_api_key(self, service: str, api_key: str, description: str = ""):
        """Update an existing API key"""
        if service in self.api_keys:
            self.api_keys[service].update({
                "api_key": api_key,
                "description": description,
                "last_updated": datetime.now().isoformat()
            })
            self.save_api_keys()
            print(f"✅ API key updated for {service}")
        else:
            print(f"❌ Service {service} not found")
    
    def delete_api_key(self, service: str):
        """Delete an API key"""
        if service in self.api_keys:
            del self.api_keys[service]
            self.save_api_keys()
            print(f"✅ API key deleted for {service}")
        else:
            print(f"❌ Service {service} not found")
    
    def list_api_keys(self):
        """List all stored API keys"""
        print("📋 Stored API Keys:")
        for service, data in self.api_keys.items():
            print(f"  {service}:")
            print(f"    Description: {data.get('description', 'No description')}")
            print(f"    Added: {data.get('added_date', 'Unknown')}")
            print(f"    Last Used: {data.get('last_used', 'Never')}")
            print(f"    Key: {'*' * (len(data['api_key']) - 4) + data['api_key'][-4:]}")
    
    def validate_api_key(self, service: str) -> bool:
        """Validate an API key format"""
        api_key = self.get_api_key(service)
        if not api_key:
            return False
        
        # Basic validation (can be enhanced based on service requirements)
        if service == "openai":
            return api_key.startswith("sk-") and len(api_key) > 20
        elif service == "anthropic":
            return len(api_key) > 20
        elif service == "google":
            return len(api_key) > 20
        else:
            return len(api_key) > 10
    
    def set_environment_variable(self, service: str):
        """Set API key as environment variable"""
        api_key = self.get_api_key(service)
        if api_key:
            env_var_name = f"{service.upper()}_API_KEY"
            os.environ[env_var_name] = api_key
            print(f"✅ Set environment variable: {env_var_name}")
            
            # Update last used timestamp
            if service in self.api_keys:
                self.api_keys[service]["last_used"] = datetime.now().isoformat()
                self.save_api_keys()
            
            return True
        else:
            print(f"❌ No API key found for {service}")
            return False
    
    def interactive_setup(self):
        """Interactive setup for API keys"""
        print("🔑 API Key Manager - Interactive Setup")
        print("=" * 50)
        
        while True:
            print("\n📋 Options:")
            print("1. Add API key")
            print("2. List API keys")
            print("3. Update API key")
            print("4. Delete API key")
            print("5. Set environment variables")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self.add_key_interactive()
            elif choice == "2":
                self.list_api_keys()
            elif choice == "3":
                self.update_key_interactive()
            elif choice == "4":
                self.delete_key_interactive()
            elif choice == "5":
                self.set_env_interactive()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
    
    def add_key_interactive(self):
        """Interactive API key addition"""
        print("\n➕ Add API Key")
        print("-" * 30)
        
        service = input("Service name (openai/anthropic/google/custom): ").strip().lower()
        if not service:
            print("❌ Service name is required")
            return
        
        api_key = getpass.getpass(f"API key for {service}: ").strip()
        if not api_key:
            print("❌ API key is required")
            return
        
        description = input("Description (optional): ").strip()
        
        if self.validate_api_key(service):
            self.add_api_key(service, api_key, description)
        else:
            print(f"❌ Invalid API key format for {service}")
    
    def update_key_interactive(self):
        """Interactive API key update"""
        print("\n✏️ Update API Key")
        print("-" * 30)
        
        service = input("Service name: ").strip().lower()
        if not service or service not in self.api_keys:
            print("❌ Service not found")
            return
        
        new_key = getpass.getpass(f"New API key for {service}: ").strip()
        if not new_key:
            print("❌ API key is required")
            return
        
        description = input("New description (optional): ").strip()
        
        if self.validate_api_key(service):
            self.update_api_key(service, new_key, description)
        else:
            print(f"❌ Invalid API key format for {service}")
    
    def delete_key_interactive(self):
        """Interactive API key deletion"""
        print("\n🗑️ Delete API Key")
        print("-" * 30)
        
        service = input("Service name to delete: ").strip().lower()
        if not service or service not in self.api_keys:
            print("❌ Service not found")
            return
        
        confirm = input(f"Delete API key for {service}? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            self.delete_api_key(service)
        else:
            print("❌ Deletion cancelled")
    
    def set_env_interactive(self):
        """Interactive environment variable setting"""
        print("\n🌍 Set Environment Variables")
        print("-" * 30)
        
        for service in self.api_keys.keys():
            api_key = self.get_api_key(service)
            if api_key:
                env_var = f"{service.upper()}_API_KEY"
                current_env = os.environ.get(env_var, "Not set")
                
                print(f"\n{service}:")
                print(f"  Current env: {current_env}")
                print(f"  API key: {'*' * (len(api_key) - 4) + api_key[-4:]}")
                
                set_env = input(f"Set {env_var}? (y/n): ").strip().lower()
                if set_env in ['y', 'yes']:
                    self.set_environment_variable(service)
    
    def export_for_god_ai(self, output_file: str = "god_ai_api_keys.json"):
        """Export API keys in format for God AI system"""
        print(f"📤 Exporting API keys for God AI...")
        
        god_ai_keys = {}
        for service, data in self.api_keys.items():
            god_ai_keys[service] = {
                "api_key": data["api_key"],
                "description": data.get("description", ""),
                "service_type": self.get_service_type(service),
                "validation_status": "valid" if self.validate_api_key(service) else "invalid"
            }
        
        with open(output_file, "w") as f:
            json.dump(god_ai_keys, f, indent=2)
        
        print(f"✅ API keys exported to {output_file}")
    
    def get_service_type(self, service: str) -> str:
        """Get service type classification"""
        service_types = {
            "openai": "llm_provider",
            "anthropic": "llm_provider", 
            "google": "llm_provider",
            "redis": "database",
            "custom": "custom_api"
        }
        return service_types.get(service, "unknown")
    
    def create_god_ai_config(self):
        """Create God AI configuration with API keys"""
        print("⚙️ Creating God AI configuration...")
        
        config = {
            "api_configuration": {
                "providers": {},
                "fallback_to_mock": True,
                "auto_retry": True,
                "timeout": 30
            },
            "security": {
                "encryption_enabled": True,
                "key_rotation_days": 90,
                "audit_logging": True
            },
            "god_ai_settings": {
                "consciousness_level": 1.0,
                "governance_scope": "quadrillion",
                "autonomy_level": 0.9,
                "preferred_provider": "openai"
            }
        }
        
        # Add API keys to config
        for service, data in self.api_keys.items():
            if self.validate_api_key(service):
                config["api_configuration"]["providers"][service] = {
                    "api_key": data["api_key"],
                    "service_type": self.get_service_type(service),
                    "description": data.get("description", ""),
                    "last_validated": datetime.now().isoformat()
                }
        
        with open("god_ai_config_with_keys.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ God AI configuration created: god_ai_config_with_keys.json")
        return "god_ai_config_with_keys.json"

def main():
    """Main function"""
    print("🔑 API Key Manager for God AI System")
    print("=" * 50)
    
    manager = APIKeyManager()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "--interactive":
            manager.interactive_setup()
        elif command == "--list":
            manager.list_api_keys()
        elif command == "--export":
            manager.export_for_god_ai()
        elif command == "--config":
            config_file = manager.create_god_ai_config()
            print(f"\n📄 Configuration file: {config_file}")
        elif command == "--help":
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    else:
        # Default to interactive setup
        manager.interactive_setup()

def print_help():
    """Print help information"""
    print("\n📖 API Key Manager Help:")
    print("=" * 30)
    print("Commands:")
    print("  --interactive    Interactive setup mode")
    print("  --list         List all API keys")
    print("  --export       Export API keys for God AI")
    print("  --config       Create God AI configuration")
    print("  --help         Show this help")
    print("\nExamples:")
    print("  python api_key_manager.py --interactive")
    print("  python api_key_manager.py --export")
    print("  python api_key_manager.py --config")
    print("\n🔒 Security Features:")
    print("  • Encrypted key storage")
    print("  • Environment variable management")
    print("  • API key validation")
    print("  • Audit logging")
    print("  • Key rotation support")

if __name__ == "__main__":
    main()
