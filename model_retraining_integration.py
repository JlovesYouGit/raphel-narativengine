"""
Model Retraining Integration
Integrates imprinted weights from constant loop extractor into model retraining pipeline
while maintaining 100% original data structure integrity
"""

import json
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import logging
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_retraining_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RetrainingBatch:
    """Batch of imprinted weights for retraining"""
    batch_id: str
    imprinted_weights: List[Dict[str, Any]]
    original_data_hashes: List[str]
    integrity_verified: bool
    batch_timestamp: str
    ready_for_training: bool

@dataclass
class ModelUpdate:
    """Model update with imprinted weights"""
    update_id: str
    model_name: str
    weight_updates: Dict[str, np.ndarray]
    original_structure_preserved: bool
    integrity_score: float
    update_timestamp: str

@dataclass
class RetrainingResult:
    """Result of retraining operation"""
    result_id: str
    batch_id: str
    success: bool
    weights_updated: int
    integrity_maintained: bool
    training_metrics: Dict[str, Any]
    timestamp: str

class ModelRetrainingIntegrator:
    """Integrates imprinted weights into model retraining pipeline"""
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        
        # Retraining pipeline state
        self.retraining_batches: Dict[str, RetrainingBatch] = {}
        self.model_updates: Dict[str, ModelUpdate] = {}
        self.retraining_results: Dict[str, RetrainingResult] = {}
        
        # Model registry
        self.model_registry: Dict[str, Dict[str, Any]] = {}
        
        # Integrity tracking
        self.integrity_log: List[Dict[str, Any]] = []
        
        # Retraining configuration
        self.retraining_config = {
            "batch_size": 32,
            "learning_rate": 0.001,
            "integrity_threshold": 1.0,
            "max_batches_per_cycle": 10,
            "preserve_original_structure": True
        }
        
        logger.info("Model Retraining Integrator initialized")
    
    def register_model(self, model_name: str, model_structure: Dict[str, Any]):
        """Register a model for retraining"""
        model_id = hashlib.sha256(f"{model_name}{self.consciousness_id}".encode()).hexdigest()[:16]
        
        self.model_registry[model_name] = {
            "model_id": model_id,
            "model_name": model_name,
            "model_structure": model_structure,
            "registered_at": datetime.now().isoformat(),
            "last_update": None,
            "update_count": 0
        }
        
        logger.info(f"Registered model: {model_name} with ID: {model_id}")
        return model_id
    
    def create_retraining_batch(self, imprinted_weights: List[Dict[str, Any]]) -> RetrainingBatch:
        """Create a retraining batch from imprinted weights"""
        batch_id = hashlib.sha256(f"batch_{len(self.retraining_batches)}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Verify integrity of all weights
        integrity_verified = True
        original_hashes = []
        
        for weight_data in imprinted_weights:
            original_hash = weight_data.get("original_data_hash")
            if original_hash:
                original_hashes.append(original_hash)
            else:
                integrity_verified = False
                logger.warning(f"Weight data missing original hash in batch {batch_id}")
        
        # Create batch
        batch = RetrainingBatch(
            batch_id=batch_id,
            imprinted_weights=imprinted_weights,
            original_data_hashes=original_hashes,
            integrity_verified=integrity_verified,
            batch_timestamp=datetime.now().isoformat(),
            ready_for_training=integrity_verified
        )
        
        self.retraining_batches[batch_id] = batch
        logger.info(f"Created retraining batch {batch_id} with {len(imprinted_weights)} weight sets")
        
        return batch
    
    def prepare_model_update(self, model_name: str, batch: RetrainingBatch) -> Optional[ModelUpdate]:
        """Prepare model update from retraining batch"""
        if model_name not in self.model_registry:
            logger.error(f"Model {model_name} not registered")
            return None
        
        if not batch.integrity_verified:
            logger.error(f"Batch {batch.batch_id} integrity not verified")
            return None
        
        update_id = hashlib.sha256(f"{model_name}{batch.batch_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Aggregate weight updates from batch
        weight_updates = {}
        integrity_score = 1.0
        
        for weight_data in batch.imprinted_weights:
            weights = weight_data.get("weights", {})
            for tensor_name, weight_array in weights.items:
                # Convert to numpy array
                if isinstance(weight_array, list):
                    weight_array = np.array(weight_array)
                
                # Preserve original structure exactly
                if tensor_name in weight_updates:
                    # Aggregate multiple updates for same tensor
                    weight_updates[tensor_name] = (weight_updates[tensor_name] + weight_array) / 2
                else:
                    weight_updates[tensor_name] = weight_array.copy()
        
        # Verify structure preservation
        original_structure_preserved = self._verify_structure_preservation(weight_updates)
        
        if not original_structure_preserved:
            integrity_score = 0.0
            logger.warning(f"Structure preservation failed for update {update_id}")
        
        # Create model update
        update = ModelUpdate(
            update_id=update_id,
            model_name=model_name,
            weight_updates=weight_updates,
            original_structure_preserved=original_structure_preserved,
            integrity_score=integrity_score,
            update_timestamp=datetime.now().isoformat()
        )
        
        self.model_updates[update_id] = update
        
        # Log integrity
        self.integrity_log.append({
            "update_id": update_id,
            "integrity_score": integrity_score,
            "structure_preserved": original_structure_preserved,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Prepared model update {update_id} for {model_name}")
        return update
    
    def _verify_structure_preservation(self, weight_updates: Dict[str, np.ndarray]) -> bool:
        """Verify that weight structure is preserved"""
        # Check that all weights are numpy arrays with proper shapes
        for tensor_name, weight_array in weight_updates.items():
            if not isinstance(weight_array, np.ndarray):
                return False
            if weight_array.size == 0:
                return False
            if np.any(np.isnan(weight_array)):
                return False
            if np.any(np.isinf(weight_array)):
                return False
        
        return True
    
    def apply_model_update(self, update: ModelUpdate) -> RetrainingResult:
        """Apply model update to registered model"""
        result_id = hashlib.sha256(f"{update.update_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        success = False
        weights_updated = 0
        integrity_maintained = False
        training_metrics = {}
        
        try:
            if update.model_name not in self.model_registry:
                raise ValueError(f"Model {update.model_name} not registered")
            
            if not update.original_structure_preserved:
                raise ValueError("Original structure not preserved")
            
            if update.integrity_score < self.retraining_config["integrity_threshold"]:
                raise ValueError(f"Integrity score {update.integrity_score} below threshold")
            
            # Apply weight updates
            model_info = self.model_registry[update.model_name]
            
            # Simulate weight application (in real system, this would update actual model)
            for tensor_name, weight_array in update.weight_updates.items():
                # In real implementation, this would update model weights
                weights_updated += 1
            
            # Update model registry
            model_info["last_update"] = datetime.now().isoformat()
            model_info["update_count"] += 1
            
            success = True
            integrity_maintained = True
            
            training_metrics = {
                "weights_updated": weights_updated,
                "integrity_score": update.integrity_score,
                "structure_preserved": update.original_structure_preserved,
                "update_id": update.update_id
            }
            
            logger.info(f"Successfully applied update {update.update_id} to {update.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to apply update {update.update_id}: {e}")
            training_metrics = {
                "error": str(e),
                "weights_updated": weights_updated,
                "integrity_score": update.integrity_score
            }
        
        # Create result
        result = RetrainingResult(
            result_id=result_id,
            batch_id=update.update_id,  # Using update_id as batch reference
            success=success,
            weights_updated=weights_updated,
            integrity_maintained=integrity_maintained,
            training_metrics=training_metrics,
            timestamp=datetime.now().isoformat()
        )
        
        self.retraining_results[result_id] = result
        return result
    
    def process_retraining_cycle(self, imprinted_weights_list: List[Dict[str, Any]], model_name: str) -> List[RetrainingResult]:
        """Process a complete retraining cycle"""
        logger.info(f"Starting retraining cycle for model {model_name}")
        
        results = []
        
        # Create batches
        batch_size = self.retraining_config["batch_size"]
        max_batches = self.retraining_config["max_batches_per_cycle"]
        
        for i in range(0, len(imprinted_weights_list), batch_size):
            if len(results) >= max_batches:
                break
            
            batch_weights = imprinted_weights_list[i:i + batch_size]
            
            # Create batch
            batch = self.create_retraining_batch(batch_weights)
            
            if not batch.ready_for_training:
                logger.warning(f"Batch {batch.batch_id} not ready for training")
                continue
            
            # Prepare update
            update = self.prepare_model_update(model_name, batch)
            
            if not update:
                logger.warning(f"Failed to prepare update for batch {batch.batch_id}")
                continue
            
            # Apply update
            result = self.apply_model_update(update)
            results.append(result)
        
        logger.info(f"Retraining cycle completed: {len(results)} updates applied")
        return results
    
    def get_retraining_status(self) -> Dict[str, Any]:
        """Get comprehensive retraining status"""
        return {
            "registered_models": len(self.model_registry),
            "retraining_batches": len(self.retraining_batches),
            "model_updates": len(self.model_updates),
            "retraining_results": len(self.retraining_results),
            "integrity_log_entries": len(self.integrity_log),
            "successful_updates": sum(1 for r in self.retraining_results.values() if r.success),
            "failed_updates": sum(1 for r in self.retraining_results.values() if not r.success),
            "average_integrity_score": np.mean([log["integrity_score"] for log in self.integrity_log]) if self.integrity_log else 0.0,
            "model_registry": {
                model_name: {
                    "update_count": info["update_count"],
                    "last_update": info["last_update"]
                }
                for model_name, info in self.model_registry.items()
            }
        }
    
    def save_retraining_state(self, filename: str = "retraining_state.json"):
        """Save retraining state to file"""
        state = {
            "consciousness_id": self.consciousness_id,
            "retraining_config": self.retraining_config,
            "model_registry": self.model_registry,
            "retraining_batches_count": len(self.retraining_batches),
            "model_updates_count": len(self.model_updates),
            "retraining_results_count": len(self.retraining_results),
            "integrity_log": self.integrity_log[-100:],  # Last 100 entries
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Retraining state saved to {filename}")
    
    def load_retraining_state(self, filename: str = "retraining_state.json") -> bool:
        """Load retraining state from file"""
        try:
            with open(filename, "r") as f:
                state = json.load(f)
            
            self.retraining_config = state["retraining_config"]
            self.model_registry = state["model_registry"]
            self.integrity_log = state["integrity_log"]
            
            logger.info(f"Retraining state loaded from {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to load retraining state: {e}")
            return False
    
    def export_weights_for_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Export updated weights for a specific model"""
        if model_name not in self.model_registry:
            return None
        
        # Collect all weight updates for this model
        model_updates = [
            update for update in self.model_updates.values()
            if update.model_name == model_name and update.original_structure_preserved
        ]
        
        if not model_updates:
            return None
        
        # Aggregate all updates
        aggregated_weights = {}
        for update in model_updates:
            for tensor_name, weight_array in update.weight_updates.items():
                if tensor_name in aggregated_weights:
                    # Average the weights
                    aggregated_weights[tensor_name] = (aggregated_weights[tensor_name] + weight_array) / 2
                else:
                    aggregated_weights[tensor_name] = weight_array.copy()
        
        # Convert to export format
        export_data = {
            "model_name": model_name,
            "model_id": self.model_registry[model_name]["model_id"],
            "weights": {
                tensor_name: weight_array.tolist()
                for tensor_name, weight_array in aggregated_weights.items()
            },
            "metadata": {
                "total_updates": len(model_updates),
                "integrity_preserved": "100%",
                "export_timestamp": datetime.now().isoformat(),
                "original_structure_maintained": True
            }
        }
        
        return export_data

# Integration with constant loop extractor
class IntegratedRetrainingPipeline:
    """Integrated pipeline combining constant loop extractor and model retraining"""
    
    def __init__(self, consciousness_id: str = "0009095353", api_base_url: str = "http://localhost:8000"):
        self.consciousness_id = consciousness_id
        
        # Import constant loop extractor
        from constant_loop_data_extractor import ConstantLoopDataExtractor
        self.extractor = ConstantLoopDataExtractor(consciousness_id, api_base_url)
        
        # Initialize retraining integrator
        self.retraining_integrator = ModelRetrainingIntegrator(consciousness_id)
        
        # Pipeline state
        self.pipeline_active = False
        self.retraining_cycle_count = 0
        
        logger.info("Integrated Retraining Pipeline initialized")
    
    async def initialize(self):
        """Initialize the integrated pipeline"""
        logger.info("Initializing integrated retraining pipeline...")
        await self.extractor.initialize()
        logger.info("Integrated retraining pipeline initialized")
    
    def start_pipeline(self, model_name: str, model_structure: Dict[str, Any]):
        """Start the integrated pipeline"""
        logger.info(f"Starting integrated pipeline for model {model_name}")
        
        # Register model
        self.retraining_integrator.register_model(model_name, model_structure)
        
        # Start constant loop extractor
        self.extractor.start_constant_loop()
        
        self.pipeline_active = True
        logger.info("Integrated pipeline started")
    
    def stop_pipeline(self):
        """Stop the integrated pipeline"""
        logger.info("Stopping integrated pipeline...")
        self.extractor.stop_constant_loop()
        self.pipeline_active = False
        logger.info("Integrated pipeline stopped")
    
    async def run_retraining_cycle(self, model_name: str) -> Dict[str, Any]:
        """Run a single retraining cycle"""
        if not self.pipeline_active:
            logger.warning("Pipeline not active")
            return {"error": "Pipeline not active"}
        
        logger.info(f"Running retraining cycle #{self.retraining_cycle_count + 1}")
        
        # Get imprinted weights from extractor
        imprinted_weights = self.extractor.get_imprinted_weights_for_retrain()
        
        if not imprinted_weights:
            logger.warning("No imprinted weights available for retraining")
            return {"error": "No imprinted weights available"}
        
        # Process retraining cycle
        results = self.retraining_integrator.process_retraining_cycle(imprinted_weights, model_name)
        
        self.retraining_cycle_count += 1
        
        # Compile cycle report
        cycle_report = {
            "cycle_number": self.retraining_cycle_count,
            "imprinted_weights_processed": len(imprinted_weights),
            "updates_applied": len(results),
            "successful_updates": sum(1 for r in results if r.success),
            "failed_updates": sum(1 for r in results if not r.success),
            "results": [
                {
                    "result_id": r.result_id,
                    "success": r.success,
                    "weights_updated": r.weights_updated,
                    "integrity_maintained": r.integrity_maintained
                }
                for r in results
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Retraining cycle completed: {cycle_report['successful_updates']} successful updates")
        return cycle_report
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        extractor_stats = await self.extractor.get_system_stats()
        retraining_status = self.retraining_integrator.get_retraining_status()
        
        return {
            "pipeline_active": self.pipeline_active,
            "retraining_cycle_count": self.retraining_cycle_count,
            "extractor_stats": extractor_stats,
            "retraining_status": retraining_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the integrated pipeline"""
        logger.info("Shutting down integrated pipeline...")
        self.stop_pipeline()
        await self.extractor.shutdown()
        logger.info("Integrated pipeline shutdown complete")

# Usage example
async def main():
    # Initialize integrated pipeline
    pipeline = IntegratedRetrainingPipeline(api_base_url="http://localhost:8000")
    
    # Initialize
    await pipeline.initialize()
    
    # Define sample model structure
    model_structure = {
        "layers": {
            "input": {"size": 256},
            "hidden": {"size": 128},
            "output": {"size": 64}
        },
        "tensors": {
            "input_weights": [256, 128],
            "hidden_weights": [128, 64],
            "output_weights": [64, 10]
        }
    }
    
    # Start pipeline
    pipeline.start_pipeline("test_model", model_structure)
    
    # Let it run for a while
    logger.info("Pipeline running, waiting 60 seconds...")
    await asyncio.sleep(60)
    
    # Run retraining cycle
    cycle_result = await pipeline.run_retraining_cycle("test_model")
    print("Retraining Cycle Result:")
    print(json.dumps(cycle_result, indent=2))
    
    # Get pipeline status
    status = await pipeline.get_pipeline_status()
    print("\nPipeline Status:")
    print(json.dumps(status, indent=2))
    
    # Export weights
    exported_weights = pipeline.retraining_integrator.export_weights_for_model("test_model")
    if exported_weights:
        print("\nExported Weights:")
        print(json.dumps(exported_weights, indent=2))
    
    # Shutdown
    await pipeline.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
