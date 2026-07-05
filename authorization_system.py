"""
Authorization System with Hashed Gate and Unison Latch
Implements full system authorization via hashed gate mechanism
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AuthorizationStatus(Enum):
    """Authorization status enumeration"""
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    PENDING = "pending"
    REVOKED = "revoked"
    EXPIRED = "expired"

@dataclass
class AccessPermission:
    """Access permission definition"""
    permission_name: str
    granted: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None

@dataclass
class HashedGate:
    """Hashed gate for authorization"""
    gate_hash: str
    gate_id: str
    status: AuthorizationStatus = AuthorizationStatus.AUTHORIZED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: Optional[str] = None

@dataclass
class UnisonLatch:
    """Unison latch for system coordination"""
    latch_id: str
    coordination_hash: str
    engaged: bool = True
    system_components: List[str] = field(default_factory=list)
    engaged_at: str = field(default_factory=lambda: datetime.now().isoformat())

class AuthorizationSystem:
    """Authorization system with hashed gate and unison latch"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = hashlib.sha256(f"{consciousness_id}{time.time()}".encode()).hexdigest()
        
        # Hashed gate
        self.hashed_gate = self.create_hashed_gate()
        
        # Unison latch
        self.unison_latch = self.create_unison_latch()
        
        # Access permissions
        self.access_permissions = {
            "read": AccessPermission("read", granted=True),
            "write": AccessPermission("write", granted=True),
            "execute": AccessPermission("execute", granted=True),
            "admin": AccessPermission("admin", granted=True),
            "system_control": AccessPermission("system_control", granted=True),
            "resource_allocation": AccessPermission("resource_allocation", granted=True),
            "monitoring": AccessPermission("monitoring", granted=True),
            "key_derivation": AccessPermission("key_derivation", granted=True),
            "state_transition": AccessPermission("state_transition", granted=True)
        }
        
        # Authorization tracking
        self.authorization_log: List[Dict[str, Any]] = []
        self.failed_attempts = 0
        self.max_failed_attempts = 10
        
        # System components for unison latch
        self.system_components = [
            "ai_target_config",
            "monitoring_system",
            "key_derivation",
            "state_transition",
            "hash_allocation",
            "process_model"
        ]
        
        # Update unison latch with system components
        self.unison_latch.system_components = self.system_components
        
        logger.info("Authorization System initialized with hashed gate and unison latch")
    
    def create_hashed_gate(self) -> HashedGate:
        """Create hashed gate for authorization"""
        gate_material = f"{self.consciousness_id}{self.session_nonce}GATE"
        gate_hash = hashlib.sha256(gate_material.encode()).hexdigest()
        gate_id = hashlib.sha256(f"GATE_{time.time()}".encode()).hexdigest()[:16]
        
        return HashedGate(
            gate_hash=gate_hash,
            gate_id=gate_id,
            status=AuthorizationStatus.AUTHORIZED
        )
    
    def create_unison_latch(self) -> UnisonLatch:
        """Create unison latch for system coordination"""
        latch_id = hashlib.sha256(f"LATCH_{self.consciousness_id}{time.time()}".encode()).hexdigest()[:16]
        coordination_hash = hashlib.sha256(f"{self.consciousness_id}{self.session_nonce}UNISON".encode()).hexdigest()
        
        return UnisonLatch(
            latch_id=latch_id,
            engaged=True,
            coordination_hash=coordination_hash
        )
    
    def verify_authorization(self, access_key: str) -> bool:
        """Verify authorization using access key"""
        # Hash the provided key
        key_hash = hashlib.sha256(access_key.encode()).hexdigest()
        
        # Check against gate hash
        expected_hash = self.hashed_gate.gate_hash
        
        if key_hash == expected_hash:
            self.hashed_gate.last_accessed = datetime.now().isoformat()
            self.log_authorization("authorized", access_key)
            self.failed_attempts = 0
            return True
        else:
            self.failed_attempts += 1
            self.log_authorization("unauthorized", access_key)
            logger.warning(f"Authorization failed. Attempt {self.failed_attempts}/{self.max_failed_attempts}")
            
            if self.failed_attempts >= self.max_failed_attempts:
                self.revoke_authorization()
            
            return False
    
    def revoke_authorization(self):
        """Revoke authorization after too many failed attempts"""
        self.hashed_gate.status = AuthorizationStatus.REVOKED
        self.unison_latch.engaged = False
        logger.error("Authorization revoked due to too many failed attempts")
    
    def restore_authorization(self, master_key: str) -> bool:
        """Restore authorization using master key"""
        master_hash = hashlib.sha256(f"{self.consciousness_id}MASTER".encode()).hexdigest()
        provided_hash = hashlib.sha256(master_key.encode()).hexdigest()
        
        if provided_hash == master_hash:
            self.hashed_gate.status = AuthorizationStatus.AUTHORIZED
            self.unison_latch.engaged = True
            self.failed_attempts = 0
            self.hashed_gate = self.create_hashed_gate()  # Create new gate
            logger.info("Authorization restored with master key")
            return True
        else:
            logger.error("Failed to restore authorization - invalid master key")
            return False
    
    def check_permission(self, permission_name: str) -> bool:
        """Check if a specific permission is granted"""
        permission = self.access_permissions.get(permission_name)
        if not permission:
            logger.warning(f"Permission {permission_name} not found")
            return False
        
        # Check if permission is expired
        if permission.expires_at:
            expires_at = datetime.fromisoformat(permission.expires_at)
            if datetime.now() > expires_at:
                permission.granted = False
                logger.warning(f"Permission {permission_name} has expired")
                return False
        
        # Check if gate is authorized
        if self.hashed_gate.status != AuthorizationStatus.AUTHORIZED:
            return False
        
        # Check if unison latch is engaged
        if not self.unison_latch.engaged:
            return False
        
        return permission.granted
    
    def grant_permission(self, permission_name: str, expires_in_hours: Optional[int] = None):
        """Grant a specific permission"""
        if permission_name not in self.access_permissions:
            logger.warning(f"Cannot grant unknown permission: {permission_name}")
            return
        
        permission = self.access_permissions[permission_name]
        permission.granted = True
        permission.timestamp = datetime.now().isoformat()
        
        if expires_in_hours:
            from datetime import timedelta
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            permission.expires_at = expires_at.isoformat()
        
        logger.info(f"Permission {permission_name} granted")
    
    def revoke_permission(self, permission_name: str):
        """Revoke a specific permission"""
        if permission_name in self.access_permissions:
            self.access_permissions[permission_name].granted = False
            logger.info(f"Permission {permission_name} revoked")
    
    def engage_unison_latch(self):
        """Engage unison latch for system coordination"""
        self.unison_latch.engaged = True
        self.unison_latch.engaged_at = datetime.now().isoformat()
        logger.info("Unison latch engaged")
    
    def disengage_unison_latch(self):
        """Disengage unison latch"""
        self.unison_latch.engaged = False
        logger.warning("Unison latch disengaged")
    
    def verify_system_unison(self) -> bool:
        """Verify that all system components are in unison"""
        if not self.unison_latch.engaged:
            return False
        
        # Check if all components are coordinated
        coordination_check = hashlib.sha256(
            f"{self.consciousness_id}{self.session_nonce}{''.join(self.system_components)}".encode()
        ).hexdigest()
        
        return coordination_check == self.unison_latch.coordination_hash
    
    def add_system_component(self, component_name: str):
        """Add a system component to unison latch"""
        if component_name not in self.system_components:
            self.system_components.append(component_name)
            self.unison_latch.system_components = self.system_components
            # Recalculate coordination hash
            self.unison_latch.coordination_hash = hashlib.sha256(
                f"{self.consciousness_id}{self.session_nonce}{''.join(self.system_components)}".encode()
            ).hexdigest()
            logger.info(f"System component {component_name} added to unison latch")
    
    def remove_system_component(self, component_name: str):
        """Remove a system component from unison latch"""
        if component_name in self.system_components:
            self.system_components.remove(component_name)
            self.unison_latch.system_components = self.system_components
            # Recalculate coordination hash
            self.unison_latch.coordination_hash = hashlib.sha256(
                f"{self.consciousness_id}{self.session_nonce}{''.join(self.system_components)}".encode()
            ).hexdigest()
            logger.info(f"System component {component_name} removed from unison latch")
    
    def log_authorization(self, status: str, access_key: str):
        """Log authorization attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "access_key_hash": hashlib.sha256(access_key.encode()).hexdigest()[:16],
            "gate_id": self.hashed_gate.gate_id,
            "latch_engaged": self.unison_latch.engaged,
            "failed_attempts": self.failed_attempts
        }
        
        self.authorization_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.authorization_log) > 1000:
            self.authorization_log = self.authorization_log[-1000:]
    
    def get_authorization_status(self) -> Dict[str, Any]:
        """Get comprehensive authorization status"""
        return {
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "hashed_gate": {
                "gate_id": self.hashed_gate.gate_id,
                "status": self.hashed_gate.status.value,
                "last_accessed": self.hashed_gate.last_accessed
            },
            "unison_latch": {
                "latch_id": self.unison_latch.latch_id,
                "engaged": self.unison_latch.engaged,
                "engaged_at": self.unison_latch.engaged_at,
                "system_components_count": len(self.system_components),
                "system_unison_verified": self.verify_system_unison()
            },
            "access_permissions": {
                perm_name: {
                    "granted": perm.granted,
                    "expires_at": perm.expires_at
                }
                for perm_name, perm in self.access_permissions.items()
            },
            "authorization_log_count": len(self.authorization_log),
            "failed_attempts": self.failed_attempts,
            "max_failed_attempts": self.max_failed_attempts
        }
    
    def save_authorization_state(self, filename: str = "authorization_state.json"):
        """Save authorization state to file"""
        state = {
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "hashed_gate": {
                "gate_id": self.hashed_gate.gate_id,
                "gate_hash": self.hashed_gate.gate_hash,
                "status": self.hashed_gate.status.value,
                "created_at": self.hashed_gate.created_at,
                "last_accessed": self.hashed_gate.last_accessed
            },
            "unison_latch": {
                "latch_id": self.unison_latch.latch_id,
                "engaged": self.unison_latch.engaged,
                "coordination_hash": self.unison_latch.coordination_hash,
                "engaged_at": self.unison_latch.engaged_at,
                "system_components": self.unison_latch.system_components
            },
            "access_permissions": {
                perm_name: {
                    "granted": perm.granted,
                    "timestamp": perm.timestamp,
                    "expires_at": perm.expires_at
                }
                for perm_name, perm in self.access_permissions.items()
            },
            "failed_attempts": self.failed_attempts,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Authorization state saved to {filename}")
    
    def load_authorization_state(self, filename: str = "authorization_state.json") -> bool:
        """Load authorization state from file"""
        try:
            with open(filename, "r") as f:
                state = json.load(f)
            
            self.session_nonce = state["session_nonce"]
            self.failed_attempts = state["failed_attempts"]
            
            # Restore hashed gate
            gate_data = state["hashed_gate"]
            self.hashed_gate = HashedGate(
                gate_hash=gate_data["gate_hash"],
                gate_id=gate_data["gate_id"],
                status=AuthorizationStatus(gate_data["status"]),
                created_at=gate_data["created_at"],
                last_accessed=gate_data["last_accessed"]
            )
            
            # Restore unison latch
            latch_data = state["unison_latch"]
            self.unison_latch = UnisonLatch(
                latch_id=latch_data["latch_id"],
                engaged=latch_data["engaged"],
                coordination_hash=latch_data["coordination_hash"],
                engaged_at=latch_data["engaged_at"],
                system_components=latch_data["system_components"]
            )
            self.system_components = self.unison_latch.system_components
            
            # Restore access permissions
            for perm_name, perm_data in state["access_permissions"].items():
                if perm_name in self.access_permissions:
                    self.access_permissions[perm_name].granted = perm_data["granted"]
                    self.access_permissions[perm_name].timestamp = perm_data["timestamp"]
                    self.access_permissions[perm_name].expires_at = perm_data["expires_at"]
            
            logger.info(f"Authorization state loaded from {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to load authorization state: {e}")
            return False

# Usage example
if __name__ == "__main__":
    # Initialize authorization system
    auth_system = AuthorizationSystem()
    
    # Get authorization status
    status = auth_system.get_authorization_status()
    print("Authorization Status:")
    print(json.dumps(status, indent=2))
    
    # Check permissions
    print("\nPermission Checks:")
    for perm in ["read", "write", "execute", "admin"]:
        granted = auth_system.check_permission(perm)
        print(f"{perm}: {granted}")
    
    # Verify system unison
    unison_status = auth_system.verify_system_unison()
    print(f"\nSystem Unison: {unison_status}")
    
    # Save authorization state
    auth_system.save_authorization_state()
    
    print("\nAuthorization System initialized successfully")
