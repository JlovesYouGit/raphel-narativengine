"""
Complete Model Integration System
Integrates GGUF/Agent-97 model loading with constant loop data extraction and weight imprinting
"""

import asyncio
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

# Import existing systems
from constant_loop_data_extractor import ConstantLoopDataExtractor, WeightImprinter
from gguf_model_integration import ModelWeightImprinter, GGUFModelLoader, Agent97ModelIntegration
from model_retraining_integration import ModelRetrainingIntegrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complete_model_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompleteModelIntegration:
    """Complete integration system for model weight imprinting"""
    
    def __init__(self, consciousness_id: str = "0009095353", api_base_url: str = "http://localhost:8000"):
        self.consciousness_id = consciousness_id
        
        # Initialize all components
        self.constant_loop_extractor = ConstantLoopDataExtractor(consciousness_id, api_base_url)
        self.model_weight_imprinter = ModelWeightImprinter()
        self.retraining_integrator = ModelRetrainingIntegrator(consciousness_id)
        
        # Track loaded models
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        
        # Integration status
        self.integration_active = False
        self.imprint_cycle_count = 0
        
        logger.info("Complete Model Integration System initialized")
    
    async def initialize(self):
        """Initialize the complete integration system"""
        logger.info("Initializing complete model integration system...")
        await self.constant_loop_extractor.initialize()
        logger.info("Complete model integration system initialized")
    
    def load_model_for_imprinting(self, model_path: str, model_type: str = 'auto') -> Optional[str]:
        """Load model for weight imprinting"""
        logger.info(f"Loading model for imprinting: {model_path}")
        
        # Auto-detect model type if not specified
        if model_type == 'auto':
            model_type = self._detect_model_type(model_path)
        
        model_id = None
        
        if model_type == 'gguf':
            model_id = self.model_weight_imprinter.load_gguf_model(model_path)
        elif model_type == 'agent97':
            model_id = self.model_weight_imprinter.load_agent97_model(model_path)
        else:
            logger.error(f"Unsupported model type: {model_type}")
            return None
        
        if model_id:
            self.loaded_models[model_id] = {
                'model_id': model_id,
                'model_path': model_path,
                'model_type': model_type,
                'loaded_at': datetime.now().isoformat()
            }
            logger.info(f"Successfully loaded model: {model_id}")
        
        return model_id
    
    def _detect_model_type(self, model_path: str) -> str:
        """Auto-detect model type from file path"""
        path = Path(model_path)
        
        if path.suffix == '.gguf':
            return 'gguf'
        elif path.suffix in ['.json', '.pkl', '.pickle']:
            return 'agent97'
        elif 'agent97' in path.name.lower():
            return 'agent97'
        else:
            return 'gguf'  # Default to GGUF
    
    def start_integration_pipeline(self, model_id: str):
        """Start the complete integration pipeline"""
        if model_id not in self.loaded_models:
            logger.error(f"Model {model_id} not loaded")
            return False
        
        logger.info(f"Starting integration pipeline for model {model_id}")
        
        # Register model in retraining integrator
        model_info = self.loaded_models[model_id]
        model_structure = self._create_model_structure(model_id)
        
        self.retraining_integrator.register_model(
            model_name=model_id,
            model_structure=model_structure
        )
        
        # Start constant loop extractor
        self.constant_loop_extractor.start_constant_loop()
        
        self.integration_active = True
        logger.info("Integration pipeline started")
        return True
    
    def _create_model_structure(self, model_id: str) -> Dict[str, Any]:
        """Create model structure from loaded model"""
        model_info = self.loaded_models[model_id]
        model_type = model_info['model_type']
        
        if model_type == 'gguf':
            # Get tensor info from GGUF loader
            if model_id in self.model_weight_imprinter.gguf_loader.loaded_models:
                model_data = self.model_weight_imprinter.gguf_loader.loaded_models[model_id]
                tensor_names = list(model_data['tensors'].keys())
                
                return {
                    'model_type': 'gguf',
                    'tensor_count': len(tensor_names),
                    'tensor_names': tensor_names[:20],  # First 20 tensors
                    'metadata': model_data['metadata'].metadata_kv
                }
        
        elif model_type == 'agent97':
            # Get model info from Agent-97 loader
            if model_id in self.model_weight_imprinter.agent97_loader.agent97_models:
                model_data = self.model_weight_imprinter.agent97_loader.agent97_models[model_id]
                return {
                    'model_type': 'agent97',
                    'model_data_keys': list(model_data['model_data'].keys()) if isinstance(model_data['model_data'], dict) else []
                }
        
        return {'model_type': model_type}
    
    async def run_imprinting_cycle(self, model_id: str) -> Dict[str, Any]:
        """Run a complete imprinting cycle"""
        if not self.integration_active:
            logger.warning("Integration pipeline not active")
            return {'error': 'Integration pipeline not active'}
        
        if model_id not in self.loaded_models:
            logger.error(f"Model {model_id} not loaded")
            return {'error': 'Model not loaded'}
        
        logger.info(f"Running imprinting cycle #{self.imprint_cycle_count + 1}")
        
        # Get imprinted weights from constant loop extractor
        imprinted_weights = self.constant_loop_extractor.get_imprinted_weights_for_retrain()
        
        if not imprinted_weights:
            logger.warning("No imprinted weights available for imprinting")
            return {'error': 'No imprinted weights available'}
        
        # Convert imprinted weights to numpy arrays
        extracted_weights = {}
        for weight_data in imprinted_weights:
            weights = weight_data.get('weights', {})
            for tensor_name, weight_array in weights.items():
                if isinstance(weight_array, list):
                    extracted_weights[tensor_name] = np.array(weight_array)
                else:
                    extracted_weights[tensor_name] = weight_array
        
        # Imprint weights into model
        model_info = self.loaded_models[model_id]
        imprint_result = self.model_weight_imprinter.imprint_weights(
            model_id=model_id,
            extracted_weights=extracted_weights,
            model_type=model_info['model_type']
        )
        
        # Process through retraining integrator
        retraining_batch = self.retraining_integrator.create_retraining_batch(imprinted_weights)
        update = self.retraining_integrator.prepare_model_update(model_id, retraining_batch)
        if update:
            apply_result = self.retraining_integrator.apply_model_update(update)
        
        self.imprint_cycle_count += 1
        
        cycle_result = {
            'cycle_number': self.imprint_cycle_count,
            'model_id': model_id,
            'weights_extracted': len(extracted_weights),
            'imprint_result': imprint_result,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Imprinting cycle completed: {cycle_result}")
        return cycle_result
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        extractor_stats = await self.constant_loop_extractor.get_system_stats()
        retraining_status = self.retraining_integrator.get_retraining_status()
        
        return {
            'integration_active': self.integration_active,
            'imprint_cycle_count': self.imprint_cycle_count,
            'loaded_models': self.loaded_models,
            'extractor_stats': extractor_stats,
            'retraining_status': retraining_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_imprinted_model(self, model_id: str, output_path: str) -> bool:
        """Save imprinted model to file"""
        if model_id not in self.loaded_models:
            logger.error(f"Model {model_id} not loaded")
            return False
        
        model_info = self.loaded_models[model_id]
        return self.model_weight_imprinter.save_imprinted_model(
            model_id=model_id,
            output_path=output_path,
            model_type=model_info['model_type']
        )
    
    async def shutdown(self):
        """Shutdown the complete integration system"""
        logger.info("Shutting down complete model integration system...")
        self.integration_active = False
        self.constant_loop_extractor.stop_constant_loop()
        await self.constant_loop_extractor.shutdown()
        logger.info("Shutdown complete")

# Usage example
async def main():
    # Initialize complete integration
    integration = CompleteModelIntegration(api_base_url="http://localhost:8000")
    
    # Initialize
    await integration.initialize()
    
    # Try to load the GGUF model (will handle Git LFS pointer gracefully)
    gguf_path = r"n:\lossless agi\installed_models\unified_model_031bd6454a85a28b\wan_t2v.gguf"
    model_id = integration.load_model_for_imprinting(gguf_path, model_type='auto')
    
    if model_id:
        print(f"Successfully loaded model: {model_id}")
        
        # Start integration pipeline
        integration.start_integration_pipeline(model_id)
        
        # Let it run briefly
        logger.info("Integration pipeline running, waiting 30 seconds...")
        await asyncio.sleep(30)
        
        # Run imprinting cycle
        cycle_result = await integration.run_imprinting_cycle(model_id)
        print("Imprinting Cycle Result:")
        print(json.dumps(cycle_result, indent=2))
        
        # Get status
        status = await integration.get_integration_status()
        print("\nIntegration Status:")
        print(json.dumps(status, indent=2))
        
        # Shutdown
        await integration.shutdown()
    else:
        print("Model loading failed (likely Git LFS pointer - needs actual file download)")
        print("The system is ready to work with actual GGUF or Agent-97 model files")

if __name__ == "__main__":
    asyncio.run(main())
