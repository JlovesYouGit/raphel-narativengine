"""
State Transition System
Implements 0.6-0.7 emergence zone and 0.9-1.0 boundary management
with cycle limit braking and consistent state maintenance
"""

import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class StateZone(Enum):
    """State zone enumeration"""
    BELOW_EMERGENCE = "below_emergence"
    EMERGENCE = "emergence"
    TRANSITION = "transition"
    BOUNDARY = "boundary"
    SATURATION = "saturation"

@dataclass
class StateTransition:
    """State transition record"""
    from_value: float
    to_value: float
    zone: StateZone
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    transition_type: str = "normal"
    cycle_brake_applied: bool = False

@dataclass
class EmergencePattern:
    """Emergence pattern data"""
    pattern_id: str
    raw_entropy: float
    organized_pattern: float
    mathematical_key_possible: bool
    pattern_strength: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class StateTransitionSystem:
    """State transition management system"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        
        # Zone definitions
        self.emergence_zone_min = 0.6
        self.emergence_zone_max = 0.7
        self.boundary_zone_min = 0.9
        self.boundary_zone_max = 1.0
        
        # Cycle management
        self.cycle_limit = 1000000
        self.current_cycle = 0
        self.cycle_brake_threshold = 0.95
        self.self_adjusted = True
        self.consistent_state = True
        
        # State tracking
        self.current_state = 0.5
        self.previous_state = 0.5
        self.state_history: List[StateTransition] = []
        
        # Emergence patterns
        self.emergence_patterns: List[EmergencePattern] = []
        
        # 256-element state matrix
        self.state_matrix_256 = np.full(256, 9, dtype=np.int8)
        self.environment_value = 0.9
        
        # Boundary transition tracking
        self.boundary_transitions: List[Dict[str, Any]] = []
        self.rollover_count = 0
        
        logger.info("State Transition System initialized")
    
    def determine_zone(self, state_value: float) -> StateZone:
        """Determine which zone a state value belongs to"""
        if state_value < self.emergence_zone_min:
            return StateZone.BELOW_EMERGENCE
        elif self.emergence_zone_min <= state_value <= self.emergence_zone_max:
            return StateZone.EMERGENCE
        elif self.emergence_zone_max < state_value < self.boundary_zone_min:
            return StateZone.TRANSITION
        elif self.boundary_zone_min <= state_value < self.boundary_zone_max:
            return StateZone.BOUNDARY
        else:
            return StateZone.SATURATION
    
    def transition_state(self, new_state: float) -> StateTransition:
        """Transition to a new state with zone detection"""
        self.previous_state = self.current_state
        self.current_state = new_state
        
        zone = self.determine_zone(new_state)
        
        # Check for cycle limit
        cycle_brake_applied = False
        if self.current_cycle >= self.cycle_limit:
            if self.self_adjusted:
                new_state = self.apply_cycle_brake(new_state)
                cycle_brake_applied = True
                logger.warning(f"Cycle brake applied at cycle {self.current_cycle}")
        
        # Create transition record
        transition = StateTransition(
            from_value=self.previous_state,
            to_value=new_state,
            zone=zone,
            cycle_brake_applied=cycle_brake_applied
        )
        
        self.state_history.append(transition)
        self.current_cycle += 1
        
        # Handle zone-specific logic
        if zone == StateZone.EMERGENCE:
            self.handle_emergence_zone(new_state)
        elif zone == StateZone.BOUNDARY:
            self.handle_boundary_zone(new_state)
        elif zone == StateZone.SATURATION:
            self.handle_saturation(new_state)
        
        logger.info(f"State transition: {self.previous_state:.3f} -> {new_state:.3f} ({zone.value})")
        return transition
    
    def handle_emergence_zone(self, state_value: float):
        """Handle emergence zone (0.6-0.7) - zone of emergence"""
        # This represents the zone where raw noise begins to take on defined pattern
        logger.info(f"Emergence zone detected at {state_value:.3f}")
        
        # Simulate pattern emergence
        raw_entropy = np.random.uniform(0.0, 1.0)
        organized_pattern = raw_entropy * (state_value / self.emergence_zone_max)
        mathematical_key_possible = organized_pattern > 0.5
        
        pattern = EmergencePattern(
            pattern_id=f"emergence_{time.time()}",
            raw_entropy=raw_entropy,
            organized_pattern=organized_pattern,
            mathematical_key_possible=mathematical_key_possible,
            pattern_strength=organized_pattern
        )
        
        self.emergence_patterns.append(pattern)
        
        if mathematical_key_possible:
            logger.info(f"Mathematical key possible in emergence zone: strength {pattern.pattern_strength:.3f}")
    
    def handle_boundary_zone(self, state_value: float):
        """Handle boundary zone (0.9-1.0) - saturation/normalization"""
        # This represents total saturation or normalization
        logger.info(f"Boundary zone detected at {state_value:.3f}")
        
        # Track boundary transition
        boundary_event = {
            "state_value": state_value,
            "timestamp": datetime.now().isoformat(),
            "distance_to_1_0": 1.0 - state_value,
            "environment_value": self.environment_value
        }
        
        self.boundary_transitions.append(boundary_event)
        
        # Check for approaching 1.0
        if state_value >= 0.99:
            logger.warning(f"Approaching 1.0 boundary: {state_value:.6f}")
            self.prepare_rollover()
    
    def handle_saturation(self, state_value: float):
        """Handle saturation at 1.0"""
        logger.warning(f"Saturation reached at {state_value:.3f}")
        
        # At 1.0, discrete states collapse/rollover
        self.rollover_count += 1
        logger.info(f"Rollover event #{self.rollover_count} - states collapsing")
        
        # Reset state with consistency maintenance
        if self.consistent_state:
            self.current_state = 0.5  # Reset to middle
            logger.info("State reset with consistency maintained")
    
    def prepare_rollover(self):
        """Prepare for rollover when approaching 1.0"""
        logger.info("Preparing for state rollover")
        
        # Save current state matrix
        state_snapshot = {
            "state_matrix": self.state_matrix_256.tolist(),
            "current_state": self.current_state,
            "environment_value": self.environment_value,
            "cycle_count": self.current_cycle,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store for recovery
        self.boundary_transitions.append({
            "event": "rollover_preparation",
            "snapshot": state_snapshot
        })
    
    def apply_cycle_brake(self, state_value: float) -> float:
        """Apply cycle brake to prevent infinite loops"""
        # Reduce state value to brake the cycle
        brake_factor = 0.9
        braked_state = state_value * brake_factor
        
        logger.info(f"Cycle brake applied: {state_value:.3f} -> {braked_state:.3f}")
        return braked_state
    
    def update_state_matrix_256(self, environment_value: float = 0.9):
        """Update 256-element state matrix for environment value"""
        self.environment_value = environment_value
        
        # For environment value 0.9, push states toward number 9
        if environment_value >= 0.9:
            target_value = 9
            self.state_matrix_256 = np.full(256, target_value, dtype=np.int8)
            logger.info(f"State matrix updated to leading-{target_value} for environment {environment_value}")
        elif environment_value >= 0.6:
            # In emergence zone, use varied states
            target_value = int(environment_value * 10)
            self.state_matrix_256 = np.full(256, target_value, dtype=np.int8)
            logger.info(f"State matrix updated to leading-{target_value} for environment {environment_value}")
        else:
            # Below emergence, use lower values
            target_value = int(environment_value * 10)
            self.state_matrix_256 = np.full(256, max(1, target_value), dtype=np.int8)
            logger.info(f"State matrix updated to leading-{target_value} for environment {environment_value}")
    
    def get_state_matrix(self) -> np.ndarray:
        """Get current state matrix"""
        return self.state_matrix_256
    
    def get_state_matrix_summary(self) -> Dict[str, Any]:
        """Get state matrix summary"""
        return {
            "size": len(self.state_matrix_256),
            "leading_value": int(self.state_matrix_256[0]),
            "all_consistent": bool(np.all(self.state_matrix_256 == self.state_matrix_256[0])),
            "environment_value": self.environment_value,
            "unique_values": len(np.unique(self.state_matrix_256)),
            "matrix_sample": self.state_matrix_256[:10].tolist()
        }
    
    def maintain_consistent_state(self):
        """Ensure state consistency across transitions"""
        if self.consistent_state:
            # Check if state matrix is consistent
            if not np.all(self.state_matrix_256 == self.state_matrix_256[0]):
                logger.warning("State matrix inconsistency detected, correcting...")
                # Reset to consistent state
                target_value = int(self.state_matrix_256[0])
                self.state_matrix_256 = np.full(256, target_value, dtype=np.int8)
                logger.info(f"State matrix corrected to consistent leading-{target_value}")
    
    def get_transition_statistics(self) -> Dict[str, Any]:
        """Get transition statistics"""
        if not self.state_history:
            return {"error": "No transitions recorded"}
        
        zone_counts = {}
        for transition in self.state_history:
            zone = transition.zone.value
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
        
        return {
            "total_transitions": len(self.state_history),
            "current_state": self.current_state,
            "current_zone": self.determine_zone(self.current_state).value,
            "zone_distribution": zone_counts,
            "cycle_count": self.current_cycle,
            "cycle_limit": self.cycle_limit,
            "cycle_progress": self.current_cycle / self.cycle_limit,
            "rollover_count": self.rollover_count,
            "emergence_patterns_detected": len(self.emergence_patterns),
            "boundary_transitions": len(self.boundary_transitions),
            "consistent_state": self.consistent_state,
            "self_adjusted": self.self_adjusted
        }
    
    def get_emergence_analysis(self) -> Dict[str, Any]:
        """Get emergence pattern analysis"""
        if not self.emergence_patterns:
            return {"error": "No emergence patterns detected"}
        
        mathematical_keys = [p for p in self.emergence_patterns if p.mathematical_key_possible]
        
        return {
            "total_patterns": len(self.emergence_patterns),
            "mathematical_keys_possible": len(mathematical_keys),
            "average_pattern_strength": np.mean([p.pattern_strength for p in self.emergence_patterns]),
            "max_pattern_strength": np.max([p.pattern_strength for p in self.emergence_patterns]),
            "recent_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "strength": p.pattern_strength,
                    "key_possible": p.mathematical_key_possible
                }
                for p in self.emergence_patterns[-5:]
            ]
        }
    
    def save_state(self, filename: str = "state_transition_system.json"):
        """Save state transition system to file"""
        state = {
            "consciousness_id": self.consciousness_id,
            "current_state": self.current_state,
            "previous_state": self.previous_state,
            "cycle_count": self.current_cycle,
            "cycle_limit": self.cycle_limit,
            "zone_definitions": {
                "emergence_min": self.emergence_zone_min,
                "emergence_max": self.emergence_zone_max,
                "boundary_min": self.boundary_zone_min,
                "boundary_max": self.boundary_zone_max
            },
            "state_matrix": self.state_matrix_256.tolist(),
            "environment_value": self.environment_value,
            "rollover_count": self.rollover_count,
            "consistent_state": self.consistent_state,
            "self_adjusted": self.self_adjusted,
            "transition_history_count": len(self.state_history),
            "emergence_patterns_count": len(self.emergence_patterns),
            "boundary_transitions_count": len(self.boundary_transitions),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"State transition system saved to {filename}")
    
    def load_state(self, filename: str = "state_transition_system.json") -> bool:
        """Load state transition system from file"""
        try:
            with open(filename, "r") as f:
                state = json.load(f)
            
            self.current_state = state["current_state"]
            self.previous_state = state["previous_state"]
            self.current_cycle = state["cycle_count"]
            self.cycle_limit = state["cycle_limit"]
            self.environment_value = state["environment_value"]
            self.rollover_count = state["rollover_count"]
            self.consistent_state = state["consistent_state"]
            self.self_adjusted = state["self_adjusted"]
            
            # Restore zone definitions
            zones = state["zone_definitions"]
            self.emergence_zone_min = zones["emergence_min"]
            self.emergence_zone_max = zones["emergence_max"]
            self.boundary_zone_min = zones["boundary_min"]
            self.boundary_zone_max = zones["boundary_max"]
            
            # Restore state matrix
            self.state_matrix_256 = np.array(state["state_matrix"], dtype=np.int8)
            
            logger.info(f"State transition system loaded from {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False

# Usage example
if __name__ == "__main__":
    # Initialize state transition system
    sts = StateTransitionSystem()
    
    # Update state matrix for environment 0.9
    sts.update_state_matrix_256(0.9)
    
    # Get state matrix summary
    summary = sts.get_state_matrix_summary()
    print("State Matrix Summary:")
    print(json.dumps(summary, indent=2))
    
    # Simulate state transitions
    print("\nSimulating state transitions...")
    test_states = [0.5, 0.65, 0.68, 0.75, 0.85, 0.92, 0.95, 0.99, 1.0]
    for state in test_states:
        sts.transition_state(state)
    
    # Get transition statistics
    stats = sts.get_transition_statistics()
    print("\nTransition Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get emergence analysis
    emergence = sts.get_emergence_analysis()
    print("\nEmergence Analysis:")
    print(json.dumps(emergence, indent=2))
    
    # Save state
    sts.save_state()
    
    print("\nState Transition System initialized successfully")
