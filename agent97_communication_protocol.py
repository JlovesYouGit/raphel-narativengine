"""
Agent-97 Internal Communication Protocol
Defines the communication protocol between Agent-97 motherprocess and Claude subprocess
"""

import json
import time
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

class MessageType(Enum):
    """Message types for internal communication"""
    # System messages
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_RESPONSE = "heartbeat_response"
    
    # Status messages
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"
    
    # Configuration messages
    CONFIG_UPDATE = "config_update"
    CONFIG_UPDATE_RESPONSE = "config_update_response"
    
    # Claude AI messages
    CLAUDE_REQUEST = "claude_request"
    CLAUDE_RESPONSE = "claude_response"
    
    # Command messages
    COMMAND = "command"
    COMMAND_RESPONSE = "command_response"
    
    # Error messages
    ERROR = "error"
    
    # Data messages
    DATA_TRANSFER = "data_transfer"
    DATA_ACKNOWLEDGMENT = "data_acknowledgment"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MessageEnvelope:
    """Message envelope for internal communication"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    priority: MessagePriority = MessagePriority.MEDIUM
    requires_response: bool = False
    response_timeout: float = 30.0
    correlation_id: Optional[str] = None
    encryption_key: Optional[str] = None
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        # Convert enums to strings
        result["message_type"] = self.message_type.value
        result["priority"] = self.priority.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageEnvelope':
        """Create from dictionary"""
        # Convert strings back to enums
        data["message_type"] = MessageType(data["message_type"])
        data["priority"] = MessagePriority(data["priority"])
        return cls(**data)

class Agent97CommunicationProtocol:
    """
    Agent-97 Internal Communication Protocol
    Defines standards for communication between motherprocess and subprocesses
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Protocol configuration
        self.protocol_version = "1.0.0"
        self.max_message_size = 1024 * 1024  # 1MB
        self.default_timeout = 30.0
        self.heartbeat_interval = 5.0
        
        # Message routing
        self.message_handlers = {}
        self.response_waiters = {}
        
        # Security
        self.encryption_enabled = True
        self.signature_enabled = True
        
        print(f"Agent-97 Communication Protocol initialized")
        print(f"Protocol version: {self.protocol_version}")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_message_id(self, prefix: str = "msg") -> str:
        """Generate unique message ID"""
        timestamp = str(int(time.time() * 1000000))
        random = secrets.token_hex(8)
        return f"{prefix}_{timestamp}_{random}"
    
    def create_message(self, sender_id: str, receiver_id: str, 
                      message_type: MessageType, content: Dict[str, Any],
                      priority: MessagePriority = MessagePriority.MEDIUM,
                      requires_response: bool = False,
                      response_timeout: float = None) -> MessageEnvelope:
        """Create a new message"""
        message = MessageEnvelope(
            message_id=self.generate_message_id(),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            priority=priority,
            requires_response=requires_response,
            response_timeout=response_timeout or self.default_timeout
        )
        
        # Apply security if enabled
        if self.encryption_enabled:
            message = self.encrypt_message(message)
        
        if self.signature_enabled:
            message = self.sign_message(message)
        
        return message
    
    def encrypt_message(self, message: MessageEnvelope) -> MessageEnvelope:
        """Encrypt message content"""
        try:
            # Simple encryption for demonstration
            # In production, use proper encryption
            content_json = json.dumps(message.content)
            encrypted_content = hashlib.sha256(
                f"{content_json}{self.session_nonce}".encode()
            ).hexdigest()
            
            message.content = {
                "encrypted": True,
                "data": encrypted_content,
                "original_type": type(message.content).__name__
            }
            message.encryption_key = self.session_nonce
            
            return message
            
        except Exception as e:
            print(f"Message encryption failed: {e}")
            return message
    
    def sign_message(self, message: MessageEnvelope) -> MessageEnvelope:
        """Sign message for integrity verification"""
        try:
            # Create signature
            message_data = json.dumps(message.to_dict(), sort_keys=True)
            signature = hashlib.sha256(
                f"{message_data}{self.consciousness_id}".encode()
            ).hexdigest()
            
            message.signature = signature
            return message
            
        except Exception as e:
            print(f"Message signing failed: {e}")
            return message
    
    def verify_message(self, message: MessageEnvelope) -> bool:
        """Verify message signature"""
        try:
            if not message.signature:
                return False
            
            # Recreate signature
            message_data = json.dumps(message.to_dict(), sort_keys=True)
            expected_signature = hashlib.sha256(
                f"{message_data}{self.consciousness_id}".encode()
            ).hexdigest()
            
            return message.signature == expected_signature
            
        except Exception:
            return False
    
    def decrypt_message(self, message: MessageEnvelope) -> MessageEnvelope:
        """Decrypt message content"""
        try:
            if not message.content.get("encrypted"):
                return message
            
            # Simple decryption for demonstration
            encrypted_data = message.content.get("data")
            
            # In production, use proper decryption
            # For now, return a placeholder
            message.content = {
                "decrypted": True,
                "original_data": "decrypted_content_placeholder",
                "note": "Decryption simulation"
            }
            
            return message
            
        except Exception as e:
            print(f"Message decryption failed: {e}")
            return message
    
    def serialize_message(self, message: MessageEnvelope) -> str:
        """Serialize message to JSON string"""
        try:
            message_dict = message.to_dict()
            message_json = json.dumps(message_dict)
            
            # Check size limit
            if len(message_json.encode()) > self.max_message_size:
                raise ValueError(f"Message too large: {len(message_json)} bytes")
            
            return message_json
            
        except Exception as e:
            raise ValueError(f"Message serialization failed: {e}")
    
    def deserialize_message(self, message_json: str) -> MessageEnvelope:
        """Deserialize message from JSON string"""
        try:
            message_dict = json.loads(message_json)
            message = MessageEnvelope.from_dict(message_dict)
            
            # Verify signature
            if not self.verify_message(message):
                raise ValueError("Message signature verification failed")
            
            # Decrypt if needed
            if message.content.get("encrypted"):
                message = self.decrypt_message(message)
            
            return message
            
        except Exception as e:
            raise ValueError(f"Message deserialization failed: {e}")
    
    def register_handler(self, message_type: MessageType, handler):
        """Register message handler"""
        self.message_handlers[message_type.value] = handler
    
    def create_startup_message(self, sender_id: str, receiver_id: str, 
                           process_info: Dict[str, Any]) -> MessageEnvelope:
        """Create startup message"""
        content = {
            "process_id": process_info.get("process_id"),
            "process_name": process_info.get("process_name"),
            "process_type": process_info.get("process_type"),
            "status": "starting",
            "capabilities": process_info.get("capabilities", []),
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "protocol_version": self.protocol_version
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.STARTUP, content,
            priority=MessagePriority.HIGH
        )
    
    def create_heartbeat_message(self, sender_id: str, receiver_id: str,
                               status: str = "running") -> MessageEnvelope:
        """Create heartbeat message"""
        content = {
            "status": status,
            "timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.HEARTBEAT, content,
            priority=MessagePriority.LOW
        )
    
    def create_claude_request_message(self, sender_id: str, receiver_id: str,
                                    prompt: str, context: str = "",
                                    options: Dict[str, Any] = None) -> MessageEnvelope:
        """Create Claude request message"""
        content = {
            "prompt": prompt,
            "context": context,
            "options": options or {},
            "request_timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.CLAUDE_REQUEST, content,
            priority=MessagePriority.HIGH,
            requires_response=True,
            response_timeout=60.0
        )
    
    def create_claude_response_message(self, sender_id: str, receiver_id: str,
                                    response: str, request_id: str,
                                    tokens_used: int = 0) -> MessageEnvelope:
        """Create Claude response message"""
        content = {
            "response": response,
            "request_id": request_id,
            "tokens_used": tokens_used,
            "response_timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.CLAUDE_RESPONSE, content,
            priority=MessagePriority.HIGH,
            correlation_id=request_id
        )
    
    def create_command_message(self, sender_id: str, receiver_id: str,
                             command: str, parameters: Dict[str, Any] = None) -> MessageEnvelope:
        """Create command message"""
        content = {
            "command": command,
            "parameters": parameters or {},
            "command_timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.COMMAND, content,
            priority=MessagePriority.HIGH,
            requires_response=True
        )
    
    def create_status_request_message(self, sender_id: str, receiver_id: str) -> MessageEnvelope:
        """Create status request message"""
        content = {
            "request_timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.STATUS_REQUEST, content,
            priority=MessagePriority.MEDIUM,
            requires_response=True
        )
    
    def create_status_response_message(self, sender_id: str, receiver_id: str,
                                      status_info: Dict[str, Any]) -> MessageEnvelope:
        """Create status response message"""
        content = {
            "status_info": status_info,
            "response_timestamp": time.time(),
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.STATUS_RESPONSE, content,
            priority=MessagePriority.MEDIUM
        )
    
    def create_shutdown_message(self, sender_id: str, receiver_id: str,
                              reason: str = "normal") -> MessageEnvelope:
        """Create shutdown message"""
        content = {
            "reason": reason,
            "shutdown_timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.SHUTDOWN, content,
            priority=MessagePriority.CRITICAL,
            requires_response=True
        )
    
    def create_error_message(self, sender_id: str, receiver_id: str,
                           error: str, original_message_id: str = None) -> MessageEnvelope:
        """Create error message"""
        content = {
            "error": error,
            "original_message_id": original_message_id,
            "error_timestamp": time.time(),
            "consciousness_id": self.consciousness_id
        }
        
        return self.create_message(
            sender_id, receiver_id, MessageType.ERROR, content,
            priority=MessagePriority.HIGH,
            correlation_id=original_message_id
        )
    
    def validate_message(self, message: MessageEnvelope) -> List[str]:
        """Validate message and return list of issues"""
        issues = []
        
        # Check required fields
        if not message.message_id:
            issues.append("Missing message_id")
        
        if not message.sender_id:
            issues.append("Missing sender_id")
        
        if not message.receiver_id:
            issues.append("Missing receiver_id")
        
        if not message.message_type:
            issues.append("Missing message_type")
        
        if message.timestamp <= 0:
            issues.append("Invalid timestamp")
        
        # Check message size
        try:
            message_json = self.serialize_message(message)
            if len(message_json.encode()) > self.max_message_size:
                issues.append(f"Message too large: {len(message_json)} bytes")
        except Exception as e:
            issues.append(f"Message serialization failed: {e}")
        
        # Check timeout
        if message.response_timeout <= 0:
            issues.append("Invalid response_timeout")
        
        # Verify signature if enabled
        if self.signature_enabled and not self.verify_message(message):
            issues.append("Invalid signature")
        
        return issues
    
    def get_protocol_info(self) -> Dict[str, Any]:
        """Get protocol information"""
        return {
            "protocol_version": self.protocol_version,
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "max_message_size": self.max_message_size,
            "default_timeout": self.default_timeout,
            "heartbeat_interval": self.heartbeat_interval,
            "encryption_enabled": self.encryption_enabled,
            "signature_enabled": self.signature_enabled,
            "registered_handlers": list(self.message_handlers.keys()),
            "message_types": [mt.value for mt in MessageType],
            "priority_levels": [pl.value for pl in MessagePriority]
        }

# Message handler interface
class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    async def handle_message(self, message: MessageEnvelope) -> MessageEnvelope:
        """Handle incoming message and return response"""
        pass
    
    @abstractmethod
    def get_handled_message_types(self) -> List[MessageType]:
        """Get list of message types this handler can handle"""
        pass

# Example message handler
class ClaudeMessageHandler(MessageHandler):
    """Handler for Claude-related messages"""
    
    def __init__(self, claude_subprocess):
        self.claude_subprocess = claude_subprocess
    
    async def handle_message(self, message: MessageEnvelope) -> MessageEnvelope:
        """Handle Claude-related message"""
        if message.message_type == MessageType.CLAUDE_REQUEST:
            # Forward to Claude subprocess
            response = await self.claude_subprocess.process_claude_request(message.content)
            
            return MessageEnvelope(
                message_id=self.claude_subprocess.generate_message_id(),
                sender_id=self.claude_subprocess.process_id,
                receiver_id=message.sender_id,
                message_type=MessageType.CLAUDE_RESPONSE,
                content=response,
                timestamp=time.time(),
                correlation_id=message.message_id
            )
        
        else:
            # Unknown message type
            return MessageEnvelope(
                message_id=self.claude_subprocess.generate_message_id(),
                sender_id=self.claude_subprocess.process_id,
                receiver_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={"error": f"Unknown message type: {message.message_type.value}"},
                timestamp=time.time(),
                correlation_id=message.message_id
            )
    
    def get_handled_message_types(self) -> List[MessageType]:
        """Get handled message types"""
        return [MessageType.CLAUDE_REQUEST]

# Usage example
if __name__ == "__main__":
    # Create protocol instance
    protocol = Agent97CommunicationProtocol()
    
    # Create test messages
    startup_msg = protocol.create_startup_message(
        sender_id="claude_subprocess",
        receiver_id="agent97_motherprocess",
        process_info={
            "process_id": "claude_subprocess",
            "process_name": "Agent-97 Claude Support",
            "process_type": "subprocess",
            "capabilities": ["text_generation", "analysis", "reasoning"]
        }
    )
    
    claude_request_msg = protocol.create_claude_request_message(
        sender_id="agent97_motherprocess",
        receiver_id="claude_subprocess",
        prompt="Hello, Claude! How are you?",
        context="Agent-97 system initialization"
    )
    
    # Serialize and deserialize
    startup_json = protocol.serialize_message(startup_msg)
    print(f"Startup message: {startup_json}")
    
    deserialized_msg = protocol.deserialize_message(startup_json)
    print(f"Deserialized message type: {deserialized_msg.message_type}")
    
    # Display protocol info
    protocol_info = protocol.get_protocol_info()
    print(f"Protocol info: {protocol_info}")
