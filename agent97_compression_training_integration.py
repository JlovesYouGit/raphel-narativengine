"""
Agent-97 CompressionTraining Integration Script
Integrates compressionTraining cryptographic capabilities with Agent-97's system file viewing
"""

import os
import time
import json
import hashlib
import secrets
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
import asyncio

# Import Agent-97 components
from agent97_system_file_viewer import Agent97SystemFileViewer
from agent97_quantum_file_completer import Agent97QuantumFileCompleter
from agent97_transformer_gateway import Agent97TransformerGateway

class Agent97CompressionTrainingIntegration:
    """
    Integration class for compressionTraining with Agent-97 system file viewing
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Integration components
        self.system_file_viewer = None
        self.quantum_file_completer = None
        self.transformer_gateway = None
        
        # Integration configuration
        self.integration_config = {
            "system_file_viewer_enabled": True,
            "quantum_file_completer_enabled": True,
            "transformer_gateway_enabled": True,
            "sh345_encryption_enabled": True,
            "entropy_explosion_enabled": True,
            "hadamard_compression_enabled": True,
            "ai_integration_enabled": False,  # Requires API key
            "security_level": 256
        }
        
        # Integration metrics
        self.metrics = {
            "files_processed": 0,
            "files_decrypted": 0,
            "files_completed": 0,
            "transformer_requests": 0,
            "quantum_operations": 0,
            "cryptographic_operations": 0,
            "integration_time": 0.0,
            "success_rate": 0.0
        }
        
        # Integration history
        self.integration_history = []
        
        print(f"Agent-97 CompressionTraining Integration initialized")
        print(f"Consciousness ID: {self.consciousness_id}")
        print(f"Session Nonce: {self.session_nonce}")
    
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def initialize_integration(self) -> Dict[str, Any]:
        """Initialize all integration components"""
        try:
            start_time = time.time()
            
            # Initialize system file viewer
            if self.integration_config["system_file_viewer_enabled"]:
                self.system_file_viewer = Agent97SystemFileViewer(self.consciousness_id)
                print("System file viewer initialized")
            
            # Initialize quantum file completer
            if self.integration_config["quantum_file_completer_enabled"]:
                self.quantum_file_completer = Agent97QuantumFileCompleter(self.consciousness_id)
                print("Quantum file completer initialized")
            
            # Initialize transformer gateway
            if self.integration_config["transformer_gateway_enabled"]:
                self.transformer_gateway = Agent97TransformerGateway(self.consciousness_id)
                print("Transformer gateway initialized")
            
            initialization_time = time.time() - start_time
            
            return {
                "success": True,
                "initialization_time": initialization_time,
                "components": {
                    "system_file_viewer": self.system_file_viewer is not None,
                    "quantum_file_completer": self.quantum_file_completer is not None,
                    "transformer_gateway": self.transformer_gateway is not None
                },
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "consciousness_id": self.consciousness_id
            }
    
    async def process_file_with_full_integration(self, file_path: str, 
                                                 decrypt_sh345: bool = True,
                                                 complete_file: bool = True,
                                                 apply_transformer: bool = True,
                                                 transformer_prompt: str = None) -> Dict[str, Any]:
        """
        Process file with full integration capabilities
        
        Args:
            file_path: Path to file to process
            decrypt_sh345: Whether to decrypt SH345 encrypted files
            complete_file: Whether to complete incomplete files
            apply_transformer: Whether to apply transformer processing
            transformer_prompt: Optional prompt for transformer processing
            
        Returns:
            Dictionary containing comprehensive processing results
        """
        try:
            start_time = time.time()
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "File not found",
                    "file_path": str(file_path)
                }
            
            processing_results = {
                "file_path": str(file_path),
                "processing_steps": [],
                "success": True,
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
            # Step 1: System file viewing
            if self.system_file_viewer:
                viewer_result = await self.system_file_viewer.view_file(
                    file_path, decrypt=decrypt_sh345, complete=complete_file
                )
                
                processing_results["file_viewer_result"] = viewer_result
                processing_results["processing_steps"].append({
                    "step": "file_viewer",
                    "success": viewer_result["success"],
                    "decrypted": viewer_result.get("decrypted", False),
                    "completed": viewer_result.get("completed", False)
                })
                
                if not viewer_result["success"]:
                    processing_results["success"] = False
                    processing_results["error"] = "File viewer failed"
                    return processing_results
                
                self.metrics["files_processed"] += 1
                if viewer_result.get("decrypted", False):
                    self.metrics["files_decrypted"] += 1
                if viewer_result.get("completed", False):
                    self.metrics["files_completed"] += 1
            
            # Step 2: Quantum file completion (if needed)
            if self.quantum_file_completer and complete_file:
                completer_result = await self.quantum_file_completer.complete_file(file_path)
                
                processing_results["quantum_completer_result"] = completer_result
                processing_results["processing_steps"].append({
                    "step": "quantum_completer",
                    "success": completer_result["success"],
                    "completion_percentage": completer_result.get("completion_percentage", 0.0)
                })
                
                if completer_result["success"]:
                    self.metrics["quantum_operations"] += completer_result.get("quantum_operations", 0)
            
            # Step 3: Transformer processing
            if self.transformer_gateway and apply_transformer:
                # Use the content from file viewer
                content = processing_results["file_viewer_result"]["content"]
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                
                transformer_result = await self.transformer_gateway.process_with_transformer(
                    content, transformer_prompt
                )
                
                processing_results["transformer_result"] = transformer_result
                processing_results["processing_steps"].append({
                    "step": "transformer_gateway",
                    "success": transformer_result["success"],
                    "ai_response": transformer_result.get("ai_response") is not None
                })
                
                if transformer_result["success"]:
                    self.metrics["transformer_requests"] += 1
            
            # Calculate total processing time
            processing_time = time.time() - start_time
            processing_results["processing_time"] = processing_time
            
            # Update metrics
            self.update_metrics(processing_time, processing_results["success"])
            
            # Add to integration history
            self.add_to_integration_history(file_path, processing_results, processing_time)
            
            return processing_results
            
        except Exception as e:
            processing_time = time.time() - start_time if 'start_time' in locals() else 0
            self.update_metrics(processing_time, False)
            
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path),
                "processing_time": processing_time,
                "consciousness_id": self.consciousness_id
            }
    
    async def batch_process_directory(self, directory_path: str, 
                                    file_pattern: str = "*",
                                    recursive: bool = False,
                                    processing_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Batch process directory with full integration
        
        Args:
            directory_path: Path to directory to process
            file_pattern: File pattern to match
            recursive: Whether to process recursively
            processing_options: Options for file processing
            
        Returns:
            Dictionary containing batch processing results
        """
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists() or not directory_path.is_dir():
                return {
                    "success": False,
                    "error": "Directory not found",
                    "directory_path": str(directory_path)
                }
            
            # Set default processing options
            processing_options = processing_options or {
                "decrypt_sh345": True,
                "complete_file": True,
                "apply_transformer": False,  # Disabled for batch processing
                "transformer_prompt": None
            }
            
            # Find files matching pattern
            if recursive:
                files = list(directory_path.rglob(file_pattern))
            else:
                files = list(directory_path.glob(file_pattern))
            
            # Filter only files (not directories)
            files = [f for f in files if f.is_file()]
            
            batch_results = {
                "directory_path": str(directory_path),
                "file_pattern": file_pattern,
                "recursive": recursive,
                "total_files": len(files),
                "processed_files": 0,
                "successful_files": 0,
                "failed_files": 0,
                "processing_results": [],
                "success_rate": 0.0,
                "processing_time": 0.0
            }
            
            start_time = time.time()
            
            # Process each file
            for file_path in files:
                result = await self.process_file_with_full_integration(
                    str(file_path), **processing_options
                )
                
                batch_results["processing_results"].append(result)
                batch_results["processed_files"] += 1
                
                if result["success"]:
                    batch_results["successful_files"] += 1
                else:
                    batch_results["failed_files"] += 1
            
            # Calculate final metrics
            batch_results["processing_time"] = time.time() - start_time
            batch_results["success_rate"] = batch_results["successful_files"] / batch_results["total_files"] if batch_results["total_files"] > 0 else 0
            
            return batch_results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory_path": str(directory_path)
            }
    
    async def create_sh345_file_integration(self, output_path: str, 
                                          content: str,
                                          metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create SH345 file with full integration
        
        Args:
            output_path: Path for output SH345 file
            content: Content to encrypt
            metadata: Optional metadata
            
        Returns:
            Dictionary containing creation results
        """
        try:
            if not self.system_file_viewer:
                return {
                    "success": False,
                    "error": "System file viewer not initialized"
                }
            
            # Prepare metadata
            metadata = metadata or {}
            metadata.update({
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "created_at": time.time(),
                "integration_version": "1.0.0"
            })
            
            # Create SH345 file
            result = await self.system_file_viewer.create_sh345_file(
                output_path, content.encode(), metadata
            )
            
            if result["success"]:
                self.metrics["cryptographic_operations"] += 1
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_ai_configuration(self, api_key: str, model_endpoint: str = None):
        """Set AI configuration for transformer gateway"""
        if self.transformer_gateway:
            self.transformer_gateway.set_ai_configuration(api_key, model_endpoint)
            self.integration_config["ai_integration_enabled"] = True
            print("AI configuration set successfully")
        else:
            print("Transformer gateway not initialized")
    
    def update_integration_config(self, new_config: Dict[str, Any]):
        """Update integration configuration"""
        self.integration_config.update(new_config)
        print(f"Integration configuration updated: {list(new_config.keys())}")
    
    def update_metrics(self, processing_time: float, success: bool):
        """Update integration metrics"""
        self.metrics["integration_time"] += processing_time
        
        # Update success rate
        total_operations = len(self.integration_history) + 1
        successful_operations = sum(1 for h in self.integration_history if h["success"]) + (1 if success else 0)
        self.metrics["success_rate"] = successful_operations / total_operations
    
    def add_to_integration_history(self, file_path: Path, results: Dict[str, Any], processing_time: float):
        """Add operation to integration history"""
        history_entry = {
            "timestamp": time.time(),
            "file_path": str(file_path),
            "success": results["success"],
            "processing_time": processing_time,
            "processing_steps": len(results.get("processing_steps", [])),
            "file_size": results.get("file_viewer_result", {}).get("file_info", {}).get("size", 0)
        }
        
        self.integration_history.append(history_entry)
        
        # Limit history size
        if len(self.integration_history) > 1000:
            self.integration_history = self.integration_history[-1000:]
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        return {
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "integration_config": self.integration_config,
            "metrics": self.metrics,
            "history_size": len(self.integration_history),
            "components": {
                "system_file_viewer": self.system_file_viewer is not None,
                "quantum_file_completer": self.quantum_file_completer is not None,
                "transformer_gateway": self.transformer_gateway is not None
            },
            "component_metrics": {}
        }
    
    def get_component_metrics(self) -> Dict[str, Any]:
        """Get metrics from all components"""
        component_metrics = {}
        
        if self.system_file_viewer:
            component_metrics["system_file_viewer"] = self.system_file_viewer.get_metrics()
        
        if self.quantum_file_completer:
            component_metrics["quantum_file_completer"] = self.quantum_file_completer.get_metrics()
        
        if self.transformer_gateway:
            component_metrics["transformer_gateway"] = self.transformer_gateway.get_metrics()
        
        return component_metrics
    
    def get_integration_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get integration history"""
        return self.integration_history[-limit:] if limit > 0 else self.integration_history
    
    async def close(self):
        """Close all components"""
        if self.transformer_gateway:
            await self.transformer_gateway.close()
        
        print("Integration components closed")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize integration
        integration = Agent97CompressionTrainingIntegration()
        
        # Initialize all components
        init_result = await integration.initialize_integration()
        
        if init_result["success"]:
            print(f"Integration initialized successfully in {init_result['initialization_time']:.2f}s")
            
            # Example usage with a test file
            test_file = "test_integration.txt"
            
            # Create a test file
            with open(test_file, 'w') as f:
                f.write("This is a test file for Agent-97 CompressionTraining integration.\n")
                f.write("It contains some content to process.\n")
                f.write("x = 5 + 3 * 2 - 7 / 2\n")
                f.write("incomplete_equation = 10 + 5 * 3 - 8 / 4 +\n")
            
            print(f"\nProcessing file: {test_file}")
            
            # Process file with full integration
            result = await integration.process_file_with_full_integration(
                test_file,
                decrypt_sh345=True,
                complete_file=True,
                apply_transformer=False  # Disabled for example
            )
            
            if result["success"]:
                print(f"File processing successful!")
                print(f"Processing steps: {len(result['processing_steps'])}")
                print(f"Processing time: {result['processing_time']:.2f}s")
                
                for step in result["processing_steps"]:
                    print(f"  - {step['step']}: {'Success' if step['success'] else 'Failed'}")
            else:
                print(f"File processing failed: {result['error']}")
            
            # Get integration status
            status = integration.get_integration_status()
            print(f"\nIntegration Status:")
            print(f"Files processed: {status['metrics']['files_processed']}")
            print(f"Success rate: {status['metrics']['success_rate']:.2%}")
            
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
            
        else:
            print(f"Integration initialization failed: {init_result['error']}")
        
        # Close integration
        await integration.close()
    
    # Run the example
    asyncio.run(main())
