#!/usr/bin/env python3
"""
API Key Generator for God AI Gateway
Generates secure API keys with gateway connection codes
"""

import os
import json
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class APIKeyGenerator:
    """Secure API key generator with gateway connection"""
    
    def __init__(self):
        self.gateway_seed = "GOD_AI_GATEWAY_2026_QUADRILLION"
        self.key_length = 64
        self.salt_length = 32
        self.gateway_port = 8001
        self.gateway_protocol = "http"
        self.gateway_host = "localhost"
        
        # Initialize encryption
        self.init_encryption()
        
        # Load existing keys
        self.keys_file = Path("gateway_api_keys.json")
        self.encrypted_keys_file = Path("gateway_keys_encrypted.bin")
        self.load_existing_keys()
    
    def init_encryption(self):
        """Initialize encryption system"""
        # Generate encryption key from gateway seed
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.gateway_seed.encode(),
            iterations=100000,
        )
        self.encryption_key = kdf.derive(b"god_ai_encryption")
        self.fernet = Fernet(Fernet.generate_key())
    
    def generate_secure_key(self, service: str, user_id: str = "god_ai_user") -> Dict[str, Any]:
        """Generate a secure API key with gateway connection"""
        
        # Create timestamp
        timestamp = int(time.time())
        
        # Create seed for this key
        key_seed = f"{service}:{user_id}:{timestamp}:{self.gateway_seed}"
        
        # Generate secure random component
        random_component = secrets.token_urlsafe(32)
        
        # Create the base key
        base_key = hashlib.sha256(f"{key_seed}{random_component}".encode()).hexdigest()
        
        # Add service prefix
        if service == "openai":
            prefix = "sk-"
        elif service == "anthropic":
            prefix = "sk-ant-"
        elif service == "google":
            prefix = "AIza"
        elif service == "god_ai":
            prefix = "gai-"
        else:
            prefix = "sk-"
        
        # Create full API key
        if service == "openai":
            api_key = f"{prefix}{base_key[:48]}"
        elif service == "anthropic":
            api_key = f"{prefix}{base_key[:48]}"
        elif service == "google":
            api_key = f"{prefix}{base_key[:39]}"
        else:
            api_key = f"{prefix}{base_key[:48]}"
        
        # Generate gateway connection code
        gateway_code = self.generate_gateway_code(api_key, service)
        
        # Create key metadata
        key_data = {
            "api_key": api_key,
            "service": service,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
            "gateway_code": gateway_code,
            "gateway_url": f"{self.gateway_protocol}://{self.gateway_host}:{self.gateway_port}",
            "status": "active",
            "usage_count": 0,
            "last_used": None,
            "permissions": self.get_default_permissions(service),
            "rate_limit": self.get_rate_limit(service),
            "seed": base_key,
            "random_component": random_component
        }
        
        return key_data
    
    def generate_gateway_code(self, api_key: str, service: str) -> str:
        """Generate gateway connection code"""
        
        # Create gateway seed
        gateway_seed = f"{api_key}:{service}:{self.gateway_seed}:{time.time()}"
        
        # Generate hash
        gateway_hash = hashlib.sha256(gateway_seed.encode()).hexdigest()
        
        # Create readable code
        code_parts = [
            gateway_hash[:8].upper(),
            gateway_hash[8:12].upper(),
            gateway_hash[12:16].upper(),
            gateway_hash[16:20].upper()
        ]
        
        gateway_code = "-".join(code_parts)
        
        return gateway_code
    
    def get_default_permissions(self, service: str) -> list:
        """Get default permissions for service"""
        base_permissions = ["read", "write", "execute"]
        
        if service == "god_ai":
            return base_permissions + ["god_mode", "unlimited_access", "quadrillion_worlds"]
        elif service == "openai":
            return base_permissions + ["llm_access", "gpt_models"]
        elif service == "anthropic":
            return base_permissions + ["llm_access", "claude_models"]
        elif service == "google":
            return base_permissions + ["llm_access", "gemini_models"]
        else:
            return base_permissions
    
    def get_rate_limit(self, service: str) -> Dict[str, Any]:
        """Get rate limit for service"""
        if service == "god_ai":
            return {"requests_per_minute": 10000, "requests_per_hour": 1000000}
        elif service == "openai":
            return {"requests_per_minute": 60, "requests_per_hour": 3600}
        elif service == "anthropic":
            return {"requests_per_minute": 50, "requests_per_hour": 3000}
        elif service == "google":
            return {"requests_per_minute": 60, "requests_per_hour": 3600}
        else:
            return {"requests_per_minute": 30, "requests_per_hour": 1800}
    
    def save_key(self, key_data: Dict[str, Any]):
        """Save API key to storage"""
        
        if not hasattr(self, 'stored_keys'):
            self.stored_keys = {}
        
        self.stored_keys[key_data["api_key"]] = key_data
        
        # Save encrypted version
        self.save_encrypted_keys()
        
        # Also save unencrypted for easy access (in production, only save encrypted)
        with open(self.keys_file, "w") as f:
            json.dump(self.stored_keys, f, indent=2)
    
    def save_encrypted_keys(self):
        """Save encrypted API keys"""
        if hasattr(self, 'stored_keys'):
            # Convert to JSON string
            keys_json = json.dumps(self.stored_keys)
            
            # Encrypt
            encrypted_data = self.fernet.encrypt(keys_json.encode())
            
            # Save encrypted data
            with open(self.encrypted_keys_file, "wb") as f:
                f.write(encrypted_data)
    
    def load_existing_keys(self):
        """Load existing API keys"""
        
        # Try to load encrypted keys first
        if self.encrypted_keys_file.exists():
            try:
                with open(self.encrypted_keys_file, "rb") as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                self.stored_keys = json.loads(decrypted_data)
                return
            except:
                pass
        
        # Try to load unencrypted keys
        if self.keys_file.exists():
            try:
                with open(self.keys_file, "r") as f:
                    self.stored_keys = json.load(f)
            except:
                self.stored_keys = {}
        else:
            self.stored_keys = {}
    
    def get_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get API key data"""
        return self.stored_keys.get(api_key)
    
    def validate_key(self, api_key: str) -> bool:
        """Validate API key"""
        key_data = self.get_key(api_key)
        if not key_data:
            return False
        
        # Check if expired
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        if datetime.now() > expires_at:
            return False
        
        # Check if active
        if key_data.get("status") != "active":
            return False
        
        return True
    
    def use_key(self, api_key: str) -> bool:
        """Mark key as used"""
        key_data = self.get_key(api_key)
        if key_data:
            key_data["usage_count"] += 1
            key_data["last_used"] = datetime.now().isoformat()
            self.save_key(key_data)
            return True
        return False
    
    def revoke_key(self, api_key: str):
        """Revoke API key"""
        key_data = self.get_key(api_key)
        if key_data:
            key_data["status"] = "revoked"
            self.save_key(key_data)
    
    def list_keys(self) -> Dict[str, Any]:
        """List all API keys"""
        return self.stored_keys
    
    def create_gateway_config(self) -> Dict[str, Any]:
        """Create gateway configuration"""
        return {
            "gateway_info": {
                "name": "God AI Gateway",
                "version": "1.0.0",
                "protocol": self.gateway_protocol,
                "host": self.gateway_host,
                "port": self.gateway_port,
                "base_url": f"{self.gateway_protocol}://{self.gateway_host}:{self.gateway_port}",
                "gateway_seed": self.gateway_seed
            },
            "authentication": {
                "method": "api_key",
                "header_name": "X-API-Key",
                "query_param": "api_key",
                "encryption_enabled": True
            },
            "services": {
                "god_ai": {
                    "enabled": True,
                    "permissions": ["god_mode", "unlimited_access", "quadrillion_worlds"],
                    "rate_limit": {"requests_per_minute": 10000, "requests_per_hour": 1000000}
                },
                "openai": {
                    "enabled": True,
                    "permissions": ["llm_access", "gpt_models"],
                    "rate_limit": {"requests_per_minute": 60, "requests_per_hour": 3600}
                },
                "anthropic": {
                    "enabled": True,
                    "permissions": ["llm_access", "claude_models"],
                    "rate_limit": {"requests_per_minute": 50, "requests_per_hour": 3000}
                },
                "google": {
                    "enabled": True,
                    "permissions": ["llm_access", "gemini_models"],
                    "rate_limit": {"requests_per_minute": 60, "requests_per_hour": 3600}
                }
            },
            "security": {
                "encryption": "Fernet",
                "key_rotation_days": 90,
                "audit_logging": True,
                "rate_limiting": True
            }
        }
    
    def generate_environment_setup(self, api_key: str, service: str) -> str:
        """Generate environment setup commands"""
        
        key_data = self.get_key(api_key)
        if not key_data:
            return "API key not found"
        
        env_var = f"{service.upper()}_API_KEY"
        
        setup_script = f"""# God AI Gateway Environment Setup
# Generated: {datetime.now().isoformat()}

# Set API Key
export {env_var}="{api_key}"

# Gateway Configuration
export GOD_AI_GATEWAY_URL="{key_data['gateway_url']}"
export GOD_AI_GATEWAY_CODE="{key_data['gateway_code']}"

# Service Configuration
export {service.upper()}_SERVICE="enabled"
export {service.upper()}_PERMISSIONS="{' '.join(key_data['permissions'])}"

# Rate Limit Configuration
export {service.upper()}_RATE_LIMIT_MINUTE="{key_data['rate_limit']['requests_per_minute']}"
export {service.upper()}_RATE_LIMIT_HOUR="{key_data['rate_limit']['requests_per_hour']}"

# Security Configuration
export API_KEY_ENCRYPTION="enabled"
export GATEWAY_SEED="{self.gateway_seed}"

# Connection Test
echo "Testing connection to God AI Gateway..."
curl -H "X-API-Key: {api_key}" "{key_data['gateway_url']}/status"

echo "Environment setup complete!"
echo "API Key: {api_key}"
echo "Gateway Code: {key_data['gateway_code']}"
echo "Gateway URL: {key_data['gateway_url']}"
"""
        
        return setup_script
    
    def create_gateway_client(self, api_key: str) -> str:
        """Create gateway client code"""
        
        key_data = self.get_key(api_key)
        if not key_data:
            return "API key not found"
        
        client_code = f'''#!/usr/bin/env python3
"""
God AI Gateway Client
Generated: {datetime.now().isoformat()}
"""

import requests
import json
from typing import Dict, Any

class GodAIGatewayClient:
    """Client for God AI Gateway"""
    
    def __init__(self):
        self.api_key = "{api_key}"
        self.gateway_url = "{key_data['gateway_url']}"
        self.gateway_code = "{key_data['gateway_code']}"
        self.headers = {{
            "X-API-Key": self.api_key,
            "X-Gateway-Code": self.gateway_code,
            "Content-Type": "application/json"
        }}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test gateway connection"""
        try:
            response = requests.get(f"{{self.gateway_url}}/status", headers=self.headers)
            return response.json()
        except Exception as e:
            return {{"error": str(e)}}
    
    def activate_god_mode(self) -> Dict[str, Any]:
        """Activate God AI mode"""
        try:
            response = requests.post(f"{{self.gateway_url}}/activate", 
                                   headers=self.headers,
                                   json={{"mode": "god", "scope": "quadrillion"}})
            return response.json()
        except Exception as e:
            return {{"error": str(e)}}
    
    def get_world_status(self) -> Dict[str, Any]:
        """Get world management status"""
        try:
            response = requests.get(f"{{self.gateway_url}}/worlds/status", headers=self.headers)
            return response.json()
        except Exception as e:
            return {{"error": str(e)}}
    
    def execute_governance(self, world_id: str, action: str) -> Dict[str, Any]:
        """Execute governance action"""
        try:
            response = requests.post(f"{{self.gateway_url}}/governance",
                                   headers=self.headers,
                                   json={{"world_id": world_id, "action": action}})
            return response.json()
        except Exception as e:
            return {{"error": str(e)}}

# Usage Example
if __name__ == "__main__":
    client = GodAIGatewayClient()
    
    # Test connection
    print("Testing connection...")
    result = client.test_connection()
    print(f"Connection result: {{json.dumps(result, indent=2)}}")
    
    # Activate God mode
    print("\\nActivating God mode...")
    result = client.activate_god_mode()
    print(f"God mode result: {{json.dumps(result, indent=2)}}")
    
    # Get world status
    print("\\nGetting world status...")
    result = client.get_world_status()
    print(f"World status: {{json.dumps(result, indent=2)}}")
'''
        
        return client_code

def main():
    """Main function"""
    print("God AI Gateway API Key Generator")
    print("=" * 50)
    
    generator = APIKeyGenerator()
    
    # Generate God AI API key
    print("Generating God AI API key...")
    god_ai_key = generator.generate_secure_key("god_ai")
    
    print(f"API Key: {god_ai_key['api_key']}")
    print(f"Gateway Code: {god_ai_key['gateway_code']}")
    print(f"Gateway URL: {god_ai_key['gateway_url']}")
    print(f"Permissions: {god_ai_key['permissions']}")
    print(f"Rate Limit: {god_ai_key['rate_limit']}")
    
    # Save the key
    generator.save_key(god_ai_key)
    
    # Generate OpenAI key
    print("\\nGenerating OpenAI API key...")
    openai_key = generator.generate_secure_key("openai")
    generator.save_key(openai_key)
    
    print(f"API Key: {openai_key['api_key']}")
    print(f"Gateway Code: {openai_key['gateway_code']}")
    
    # Create environment setup
    print("\\nCreating environment setup...")
    env_setup = generator.generate_environment_setup(god_ai_key['api_key'], "god_ai")
    
    with open("god_ai_env_setup.sh", "w") as f:
        f.write(env_setup)
    
    print("Environment setup saved to: god_ai_env_setup.sh")
    
    # Create gateway client
    print("\\nCreating gateway client...")
    client_code = generator.create_gateway_client(god_ai_key['api_key'])
    
    with open("god_ai_gateway_client.py", "w") as f:
        f.write(client_code)
    
    print("Gateway client saved to: god_ai_gateway_client.py")
    
    # Create gateway configuration
    print("\\nCreating gateway configuration...")
    gateway_config = generator.create_gateway_config()
    
    with open("gateway_config.json", "w") as f:
        json.dump(gateway_config, f, indent=2)
    
    print("Gateway configuration saved to: gateway_config.json")
    
    # Set environment variables
    print("\\nSetting environment variables...")
    os.environ["GOD_AI_API_KEY"] = god_ai_key['api_key']
    os.environ["GOD_AI_GATEWAY_URL"] = god_ai_key['gateway_url']
    os.environ["GOD_AI_GATEWAY_CODE"] = god_ai_key['gateway_code']
    
    print("Environment variables set:")
    print(f"GOD_AI_API_KEY={god_ai_key['api_key']}")
    print(f"GOD_AI_GATEWAY_URL={god_ai_key['gateway_url']}")
    print(f"GOD_AI_GATEWAY_CODE={god_ai_key['gateway_code']}")
    
    print("\\n" + "=" * 50)
    print("God AI Gateway Setup Complete!")
    print("=" * 50)
    print("Files created:")
    print("  - gateway_api_keys.json (encrypted API keys)")
    print("  - god_ai_env_setup.sh (environment setup)")
    print("  - god_ai_gateway_client.py (Python client)")
    print("  - gateway_config.json (gateway configuration)")
    print("\\nNext steps:")
    print("1. Run: source god_ai_env_setup.sh")
    print("2. Test: python god_ai_gateway_client.py")
    print("3. Start: python god_ai_connection_point.py --universal")

if __name__ == "__main__":
    main()
