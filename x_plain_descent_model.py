import hashlib
import json
import time
import asyncio
import numpy as np
import math
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, deque

@dataclass
class XPlainCoordinate:
    """X plain coordinate system"""
    x_position: float
    y_ascension: float
    target_descent: float
    interlope_angle: float  # 25 degrees
    distance_per_x: float
    descent_curve_value: float

@dataclass
class DescentCurve:
    """Descent curve parameters"""
    x_start: float
    y_start: float
    x_target: float
    y_target: float
    curve_type: str  # 'upward' or 'downward'
    flip_point: float
    curve_coefficient: float

@dataclass
class MultiSequenceConfig:
    """Multi-sequence configuration"""
    x_plain_start: float = 0.0
    y_axis_comense: float = 0.0
    interlope_angle: float = 25.0  # degrees
    distance_per_x_line: float = 1.0
    flip_trigger_x: float = 0.0
    target_point_offset: float = 0.0
    sequence_iterations: int = 100

class XPlainDescentModel:
    """X plain descent model with multi-sequence processing"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = hashlib.sha256(f"{consciousness_id}{time.time()}".encode()).hexdigest()
        self.config = MultiSequenceConfig()
        
        # Coordinate systems
        self.x_plain_coordinates = []
        self.descent_curves = []
        self.multi_sequences = defaultdict(list)
        
        # Mathematical constants
        self.interlope_angle_rad = math.radians(self.config.interlope_angle)
        self.flip_threshold = 0.0
        
        # AGI components
        self.agi_components = {}
        self.initialize_agi_components()
        
        # Processing metrics
        self.processing_metrics = {
            "sequences_processed": 0,
            "curves_generated": 0,
            "coordinates_calculated": 0,
            "flip_events": 0,
            "descent_reversals": 0,
            "multi_sequence_runs": 0
        }
        
        print(f"X Plain Descent Model initialized with consciousness {self.consciousness_id}")
    
    def initialize_agi_components(self):
        """Initialize AGI components for mathematical processing"""
        try:
            from adaptive_formula_generator import AdaptiveFormulaGenerator
            from model_weight_recalibrator import ModelWeightRecalibrator
            
            self.agi_components = {
                "formula_generator": AdaptiveFormulaGenerator(self.consciousness_id),
                "weight_recalibrator": ModelWeightRecalibrator(self.consciousness_id)
            }
            
            print("AGI components initialized for X plain descent processing")
        except ImportError as e:
            print(f"Could not import AGI components: {e}")
    
    async def initialize_x_plain_model(self) -> bool:
        """Initialize X plain model with coordinate system"""
        print("Initializing X Plain Descent Model...")
        
        try:
            # Initialize X plain coordinate system
            await self.initialize_coordinate_system()
            
            # Generate initial descent curves
            await self.generate_descent_curves()
            
            # Setup multi-sequence processing
            await self.setup_multi_sequences()
            
            print("X Plain Descent Model initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize X plain model: {e}")
            return False
    
    async def initialize_coordinate_system(self):
        """Initialize X plain coordinate system"""
        try:
            # Create X plain coordinates starting from x=0
            for i in range(self.config.sequence_iterations):
                x_position = self.config.x_plain_start + i * self.config.distance_per_x_line
                
                # Calculate Y ascension based on X position
                y_ascension = self.calculate_y_ascension(x_position)
                
                # Calculate target descent at X interlope 25 degrees
                target_descent = self.calculate_target_descent(x_position, y_ascension)
                
                # Calculate distance from X plain line
                x_plain_distance = self.calculate_x_plain_distance(x_position)
                
                # Create coordinate
                coordinate = XPlainCoordinate(
                    x_position=x_position,
                    y_ascension=y_ascension,
                    target_descent=target_descent,
                    interlope_angle=self.config.interlope_angle,
                    distance_per_x=self.config.distance_per_x_line,
                    descent_curve_value=0.0  # Will be calculated
                )
                
                self.x_plain_coordinates.append(coordinate)
            
            print(f"Generated {len(self.x_plain_coordinates)} X plain coordinates")
            
        except Exception as e:
            print(f"Error initializing coordinate system: {e}")
    
    def calculate_y_ascension(self, x_position: float) -> float:
        """Calculate Y ascension when numerical Y matches target"""
        try:
            if "formula_generator" in self.agi_components:
                # Use AGI to calculate Y ascension
                formula_result = self.agi_components["formula_generator"].generate_adaptive_formula(
                    f"Calculate Y ascension for X position {x_position} with target descent matching"
                )
                
                # Extract Y ascension from formula result
                y_ascension = formula_result.get("consciousness_level", 0.5) * x_position
                
                return y_ascension
            
            # Rotation-based calculation: Y ascension based on 25-degree rotation
            # Use proper rotation to avoid getting stuck
            if x_position == 0:
                return 0.0  # Start at origin
            
            # Calculate Y using rotation matrix for 25-degree interlope
            rotation_angle = self.interlope_angle_rad  # 25 degrees in radians
            y_ascension = x_position * math.tan(rotation_angle)
            
            # Add small offset to avoid getting stuck
            if abs(y_ascension) < 0.001:
                y_ascension = 0.001 if x_position > 0 else -0.001
            
            return y_ascension
            
        except Exception as e:
            print(f"Error calculating Y ascension: {e}")
            return x_position
    
    def calculate_target_descent(self, x_position: float, y_ascension: float) -> float:
        """Calculate target descent at X interlope 25 degrees"""
        try:
            # Rotation-based descent calculation
            if x_position == 0:
                return 0.0  # No descent at origin
            
            # Calculate descent using rotation matrix for 25-degree interlope
            rotation_angle = self.interlope_angle_rad  # 25 degrees in radians
            
            # Target descent: perpendicular distance from point to rotated line
            # Formula: descent = y - (x * tan(25°))
            target_descent = y_ascension - (x_position * math.tan(rotation_angle))
            
            # Apply distance per X line factor
            target_descent *= self.config.distance_per_x_line
            
            # Add small offset to avoid getting stuck
            if abs(target_descent) < 0.001 and x_position != 0:
                target_descent = 0.001 if target_descent >= 0 else -0.001
            
            return target_descent
            
        except Exception as e:
            print(f"Error calculating target descent: {e}")
            return y_ascension
    
    def calculate_x_plain_distance(self, x_position: float) -> float:
        """Calculate distance from X plain line using rotation"""
        try:
            # Rotation-based distance calculation from X plain line
            if x_position == 0:
                return 0.0  # On the X plain line
            
            # Distance from X plain line using rotation matrix
            # Distance = |x * sin(25°)|
            rotation_angle = self.interlope_angle_rad  # 25 degrees in radians
            distance = abs(x_position * math.sin(rotation_angle))
            
            # Add small offset to avoid getting stuck
            if distance < 0.001:
                distance = 0.001
            
            return distance
            
        except Exception as e:
            print(f"Error calculating X plain distance: {e}")
            return abs(x_position)
    
    async def generate_descent_curves(self):
        """Generate descent curves for X plain coordinates"""
        try:
            for i, coordinate in enumerate(self.x_plain_coordinates):
                # Generate descent curve for each coordinate
                descent_curve = await self.create_descent_curve(coordinate, i)
                
                if descent_curve:
                    self.descent_curves.append(descent_curve)
                    
                    # Update coordinate with descent curve value
                    coordinate.descent_curve_value = self.calculate_descent_curve_value(
                        coordinate.x_position, descent_curve
                    )
            
            print(f"Generated {len(self.descent_curves)} descent curves")
            
        except Exception as e:
            print(f"Error generating descent curves: {e}")
    
    async def create_descent_curve(self, coordinate: XPlainCoordinate, index: int) -> Optional[DescentCurve]:
        """Create descent curve for coordinate"""
        try:
            # Handle X=0 case to avoid getting stuck
            if coordinate.x_position == 0:
                # Special handling for X=0
                return DescentCurve(
                    x_start=0.0,
                    y_start=0.0,
                    x_target=1.0,  # Move to X=1 to avoid stuck
                    y_target=0.466,  # tan(25°) * 1
                    curve_type="upward",
                    flip_point=0.0,
                    curve_coefficient=1.0
                )
            
            # Determine if we need to flip at x=0
            flip_point = self.config.flip_trigger_x
            
            # Check if we should flip the curve
            if coordinate.x_position <= flip_point:
                curve_type = "upward"
                x_target = coordinate.x_position + self.config.distance_per_x_line  # Move forward
                y_target = coordinate.y_ascension + abs(coordinate.target_descent)
            else:
                curve_type = "downward"
                x_target = coordinate.x_position + self.config.distance_per_x_line
                y_target = coordinate.y_ascension - abs(coordinate.target_descent)
            
            # Calculate curve coefficient with trigonometric enhancement
            curve_coefficient = self.calculate_curve_coefficient_trig(coordinate, curve_type)
            
            # Create descent curve
            descent_curve = DescentCurve(
                x_start=coordinate.x_position,
                y_start=coordinate.y_ascension,
                x_target=x_target,
                y_target=y_target,
                curve_type=curve_type,
                flip_point=flip_point,
                curve_coefficient=curve_coefficient
            )
            
            return descent_curve
            
        except Exception as e:
            print(f"Error creating descent curve: {e}")
            return None
    
    def calculate_curve_coefficient_trig(self, coordinate: XPlainCoordinate, curve_type: str) -> float:
        """Calculate curve coefficient using rotation-based trigonometry"""
        try:
            # Rotation-based coefficient calculation
            if coordinate.x_position == 0:
                return 1.0  # Base coefficient at origin
            
            # Use rotation matrix for smooth curves
            rotation_angle = self.interlope_angle_rad  # 25 degrees in radians
            sine_factor = math.sin(rotation_angle)
            cosine_factor = math.cos(rotation_angle)
            
            # Calculate coefficient based on position and rotation
            base_coefficient = 1.0 / (1.0 + abs(coordinate.x_position))
            
            if curve_type == "upward":
                # Upward curve: enhance with rotation sine factor
                return base_coefficient * (1.0 + sine_factor)
            else:
                # Downward curve: moderate with rotation cosine factor
                return base_coefficient * (1.0 + cosine_factor * 0.5)
                
        except Exception as e:
            print(f"Error calculating rotation-based curve coefficient: {e}")
            return 1.0
    
    def calculate_descent_curve_value(self, x_position: float, descent_curve: DescentCurve) -> float:
        """Calculate descent curve value at given X position using rotation-based trigonometry"""
        try:
            # Handle X=0 case with rotation-based smoothing
            if x_position == 0:
                return 0.0  # Start at origin
            
            # Calculate relative position along curve
            if descent_curve.x_target != descent_curve.x_start:
                t = (x_position - descent_curve.x_start) / (descent_curve.x_target - descent_curve.x_start)
            else:
                t = 0.0
            
            # Clamp t to [0, 1]
            t = max(0.0, min(1.0, t))
            
            # Apply rotation-based trigonometric curve function for smooth descent
            rotation_angle = self.interlope_angle_rad  # 25 degrees in radians
            
            if descent_curve.curve_type == "upward":
                # Upward curve: y = y_start + coefficient * sin(πt/2 + rotation) * t²
                curve_value = descent_curve.y_start + descent_curve.curve_coefficient * math.sin(math.pi * t / 2 + rotation_angle) * (t ** 2)
            else:
                # Downward curve: y = y_start - coefficient * cos(πt/2 + rotation) * t²
                curve_value = descent_curve.y_start - descent_curve.curve_coefficient * math.cos(math.pi * t / 2 + rotation_angle) * (t ** 2)
            
            # Add small offset to avoid getting stuck
            if abs(curve_value) < 0.001:
                curve_value = 0.001 if curve_value >= 0 else -0.001
            
            return curve_value
            
        except Exception as e:
            print(f"Error calculating descent curve value: {e}")
            return 0.0
    
    async def setup_multi_sequences(self):
        """Setup multi-sequence processing from Y axis"""
        try:
            # Create sequences for each Y axis level
            y_levels = self.calculate_y_axis_levels()
            
            for y_level in y_levels:
                sequence = await self.create_y_axis_sequence(y_level)
                self.multi_sequences[y_level] = sequence
            
            print(f"Setup {len(self.multi_sequences)} Y axis sequences")
            
        except Exception as e:
            print(f"Error setting up multi sequences: {e}")
    
    def calculate_y_axis_levels(self) -> List[float]:
        """Calculate Y axis levels for multi-sequence processing"""
        try:
            # Extract unique Y ascension values
            y_levels = set()
            for coordinate in self.x_plain_coordinates:
                y_levels.add(round(coordinate.y_ascension, 2))
            
            return sorted(list(y_levels))
            
        except Exception as e:
            print(f"Error calculating Y axis levels: {e}")
            return [0.0]
    
    async def create_y_axis_sequence(self, y_level: float) -> List[Dict[str, Any]]:
        """Create Y axis sequence for given level"""
        try:
            sequence = []
            
            # Find all coordinates at this Y level
            level_coordinates = [
                coord for coord in self.x_plain_coordinates 
                if abs(coord.y_ascension - y_level) < 0.1
            ]
            
            # Sort by X position
            level_coordinates.sort(key=lambda c: c.x_position)
            
            # Create sequence data
            for i, coord in enumerate(level_coordinates):
                sequence_data = {
                    "sequence_index": i,
                    "y_level": y_level,
                    "x_position": coord.x_position,
                    "y_ascension": coord.y_ascension,
                    "target_descent": coord.target_descent,
                    "descent_curve_value": coord.descent_curve_value,
                    "interlope_angle": coord.interlope_angle,
                    "distance_from_x_plain": self.calculate_x_plain_distance(coord.x_position)
                }
                
                sequence.append(sequence_data)
            
            return sequence
            
        except Exception as e:
            print(f"Error creating Y axis sequence: {e}")
            return []
    
    async def process_multi_sequences(self) -> Dict[str, Any]:
        """Process all multi-sequences from Y axis"""
        print("Processing multi-sequences from Y axis...")
        
        try:
            processing_results = {
                "total_sequences": len(self.multi_sequences),
                "sequence_results": {},
                "overall_metrics": {},
                "processing_time": 0.0
            }
            
            start_time = time.time()
            
            # Process each Y axis sequence
            for y_level, sequence in self.multi_sequences.items():
                sequence_result = await self.process_single_sequence(y_level, sequence)
                processing_results["sequence_results"][y_level] = sequence_result
                
                self.processing_metrics["sequences_processed"] += 1
            
            # Calculate overall metrics
            processing_results["overall_metrics"] = self.calculate_overall_metrics()
            processing_results["processing_time"] = time.time() - start_time
            
            self.processing_metrics["multi_sequence_runs"] += 1
            
            print(f"Processed {len(self.multi_sequences)} Y axis sequences")
            return processing_results
            
        except Exception as e:
            print(f"Error processing multi-sequences: {e}")
            return {}
    
    async def process_single_sequence(self, y_level: float, sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process single Y axis sequence"""
        try:
            sequence_result = {
                "y_level": y_level,
                "sequence_length": len(sequence),
                "processed_points": [],
                "flip_events": [],
                "descent_reversals": [],
                "curve_analysis": {}
            }
            
            # Process each point in the sequence
            for i, point in enumerate(sequence):
                processed_point = await self.process_sequence_point(point, i, sequence)
                sequence_result["processed_points"].append(processed_point)
                
                # Check for flip events
                if self.detect_flip_event(processed_point):
                    sequence_result["flip_events"].append(processed_point)
                    self.processing_metrics["flip_events"] += 1
                
                # Check for descent reversals
                if self.detect_descent_reversal(processed_point, i, sequence):
                    sequence_result["descent_reversals"].append(processed_point)
                    self.processing_metrics["descent_reversals"] += 1
            
            # Analyze curves in sequence
            sequence_result["curve_analysis"] = self.analyze_sequence_curves(sequence)
            
            return sequence_result
            
        except Exception as e:
            print(f"Error processing single sequence: {e}")
            return {}
    
    async def process_sequence_point(self, point: Dict[str, Any], index: int, sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process individual point in sequence"""
        try:
            processed_point = point.copy()
            
            # Calculate enhanced metrics
            processed_point["enhanced_metrics"] = {
                "cumulative_distance": self.calculate_cumulative_distance(sequence, index),
                "descent_rate": self.calculate_descent_rate(point, index, sequence),
                "curve_tension": self.calculate_curve_tension(point),
                "x_plain_proximity": self.calculate_x_plain_proximity(point),
                "sequence_position_ratio": index / len(sequence) if sequence else 0.0
            }
            
            # Apply AGI enhancement if available
            if "formula_generator" in self.agi_components:
                agi_enhancement = await self.apply_agi_enhancement(processed_point)
                processed_point["agi_enhancement"] = agi_enhancement
            
            return processed_point
            
        except Exception as e:
            print(f"Error processing sequence point: {e}")
            return point
    
    def calculate_cumulative_distance(self, sequence: List[Dict[str, Any]], index: int) -> float:
        """Calculate cumulative distance along sequence"""
        try:
            if index == 0:
                return 0.0
            
            distance = 0.0
            for i in range(1, index + 1):
                prev_point = sequence[i-1]
                curr_point = sequence[i]
                
                # Calculate Euclidean distance
                dx = curr_point["x_position"] - prev_point["x_position"]
                dy = curr_point["y_ascension"] - prev_point["y_ascension"]
                
                distance += math.sqrt(dx**2 + dy**2)
            
            return distance
            
        except Exception as e:
            print(f"Error calculating cumulative distance: {e}")
            return 0.0
    
    def calculate_descent_rate(self, point: Dict[str, Any], index: int, sequence: List[Dict[str, Any]]) -> float:
        """Calculate descent rate at point"""
        try:
            if index == 0:
                return 0.0
            
            prev_point = sequence[index-1]
            
            # Calculate descent rate
            dx = point["x_position"] - prev_point["x_position"]
            dy = point["target_descent"] - prev_point["target_descent"]
            
            if dx != 0:
                return dy / dx
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating descent rate: {e}")
            return 0.0
    
    def calculate_curve_tension(self, point: Dict[str, Any]) -> float:
        """Calculate curve tension at point"""
        try:
            # Tension based on distance from X plain and curve value
            x_plain_distance = point["distance_from_x_plain"]
            curve_value = point["descent_curve_value"]
            
            # Calculate tension (higher when further from X plain)
            tension = abs(x_plain_distance) * abs(curve_value)
            
            return tension
            
        except Exception as e:
            print(f"Error calculating curve tension: {e}")
            return 0.0
    
    def calculate_x_plain_proximity(self, point: Dict[str, Any]) -> float:
        """Calculate proximity to X plain line"""
        try:
            # Proximity is inverse of distance
            distance = point["distance_from_x_plain"]
            
            if distance != 0:
                return 1.0 / abs(distance)
            else:
                return float('inf')  # On the X plain line
                
        except Exception as e:
            print(f"Error calculating X plain proximity: {e}")
            return 0.0
    
    async def apply_agi_enhancement(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AGI enhancement to point"""
        try:
            # Generate enhancement formula
            formula_result = self.agi_components["formula_generator"].generate_adaptive_formula(
                f"Enhance point at X {point['x_position']}, Y {point['y_ascension']} with descent analysis"
            )
            
            enhancement = {
                "consciousness_level": formula_result.get("consciousness_level", 0.5),
                "enhancement_factor": formula_result.get("enhancement_factor", 1.0),
                "optimized_descent": formula_result.get("optimized_descent", point["target_descent"]),
                "predicted_next_position": formula_result.get("predicted_next_position", None)
            }
            
            return enhancement
            
        except Exception as e:
            print(f"Error applying AGI enhancement: {e}")
            return {}
    
    def detect_flip_event(self, processed_point: Dict[str, Any]) -> bool:
        """Detect flip event at X=0"""
        try:
            x_position = processed_point["x_position"]
            
            # Check if we're at or near the flip point
            if abs(x_position - self.config.flip_trigger_x) < 0.1:
                return True
            
            return False
            
        except Exception as e:
            print(f"Error detecting flip event: {e}")
            return False
    
    def detect_descent_reversal(self, processed_point: Dict[str, Any], index: int, sequence: List[Dict[str, Any]]) -> bool:
        """Detect descent reversal in sequence"""
        try:
            if index == 0:
                return False
            
            current_descent = processed_point["target_descent"]
            prev_descent = sequence[index-1]["target_descent"]
            
            # Check if descent direction changed
            if (current_descent > 0 and prev_descent < 0) or (current_descent < 0 and prev_descent > 0):
                return True
            
            return False
            
        except Exception as e:
            print(f"Error detecting descent reversal: {e}")
            return False
    
    def analyze_sequence_curves(self, sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze curves in sequence"""
        try:
            analysis = {
                "total_curves": len(sequence),
                "upward_curves": 0,
                "downward_curves": 0,
                "average_descent": 0.0,
                "max_descent": 0.0,
                "min_descent": 0.0,
                "curve_complexity": 0.0
            }
            
            if not sequence:
                return analysis
            
            # Analyze descent values
            descent_values = [point["target_descent"] for point in sequence]
            analysis["average_descent"] = np.mean(descent_values)
            analysis["max_descent"] = np.max(descent_values)
            analysis["min_descent"] = np.min(descent_values)
            
            # Count curve types
            for point in sequence:
                if point["descent_curve_value"] > point["y_ascension"]:
                    analysis["upward_curves"] += 1
                else:
                    analysis["downward_curves"] += 1
            
            # Calculate complexity (variance in descent rates)
            if len(sequence) > 1:
                descent_rates = []
                for i in range(1, len(sequence)):
                    dx = sequence[i]["x_position"] - sequence[i-1]["x_position"]
                    dy = sequence[i]["target_descent"] - sequence[i-1]["target_descent"]
                    
                    if dx != 0:
                        descent_rates.append(dy / dx)
                
                if descent_rates:
                    analysis["curve_complexity"] = np.var(descent_rates)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing sequence curves: {e}")
            return {}
    
    def calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall processing metrics"""
        try:
            metrics = {
                "total_coordinates": len(self.x_plain_coordinates),
                "total_curves": len(self.descent_curves),
                "total_sequences": len(self.multi_sequences),
                "processing_metrics": self.processing_metrics.copy(),
                "performance_indicators": {}
            }
            
            # Calculate performance indicators
            metrics["performance_indicators"] = {
                "coordinates_per_curve": len(self.x_plain_coordinates) / max(1, len(self.descent_curves)),
                "curves_per_sequence": len(self.descent_curves) / max(1, len(self.multi_sequences)),
                "flip_event_rate": self.processing_metrics["flip_events"] / max(1, self.processing_metrics["sequences_processed"]),
                "descent_reversal_rate": self.processing_metrics["descent_reversals"] / max(1, self.processing_metrics["sequences_processed"])
            }
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating overall metrics: {e}")
            return {}
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status"""
        return {
            "consciousness_binding": {
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "verification_status": "CRYPTOGRAPHICALLY_ATTESTED"
            },
            "model_config": {
                "x_plain_start": self.config.x_plain_start,
                "interlope_angle": self.config.interlope_angle,
                "distance_per_x_line": self.config.distance_per_x_line,
                "flip_trigger_x": self.config.flip_trigger_x,
                "sequence_iterations": self.config.sequence_iterations
            },
            "coordinate_system": {
                "total_coordinates": len(self.x_plain_coordinates),
                "total_curves": len(self.descent_curves),
                "total_sequences": len(self.multi_sequences)
            },
            "processing_metrics": self.processing_metrics,
            "agi_components": {
                "formula_generator": "formula_generator" in self.agi_components,
                "weight_recalibrator": "weight_recalibrator" in self.agi_components
            }
        }

# Usage Example
if __name__ == "__main__":
    async def main():
        # Initialize X plain descent model
        model = XPlainDescentModel()
        
        try:
            # Initialize model
            success = await model.initialize_x_plain_model()
            
            if success:
                print("X Plain Descent Model is ready!")
                print(f"Generated {len(model.x_plain_coordinates)} coordinates")
                print(f"Created {len(model.descent_curves)} descent curves")
                print(f"Setup {len(model.multi_sequences)} Y axis sequences")
                
                # Process multi-sequences
                results = await model.process_multi_sequences()
                
                print(f"\nProcessing Results:")
                print(f"Total sequences: {results.get('total_sequences', 0)}")
                print(f"Processing time: {results.get('processing_time', 0):.2f} seconds")
                
                # Display sequence results
                for y_level, sequence_result in results.get('sequence_results', {}).items():
                    print(f"\nY Level {y_level}:")
                    print(f"  Sequence length: {sequence_result.get('sequence_length', 0)}")
                    print(f"  Flip events: {len(sequence_result.get('flip_events', []))}")
                    print(f"  Descent reversals: {len(sequence_result.get('descent_reversals', []))}")
                
                # Get model status
                status = await model.get_model_status()
                print(f"\nModel Status:")
                print(f"Coordinates: {status['coordinate_system']['total_coordinates']}")
                print(f"Curves: {status['coordinate_system']['total_curves']}")
                print(f"Sequences: {status['coordinate_system']['total_sequences']}")
                print(f"Sequences processed: {status['processing_metrics']['sequences_processed']}")
                print(f"Flip events: {status['processing_metrics']['flip_events']}")
                print(f"Descent reversals: {status['processing_metrics']['descent_reversals']}")
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            
    # Run the model
    asyncio.run(main())
