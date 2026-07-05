"""
Agent-97 Enhanced Transformer Gateway Integration
Integrates compressionTraining transformer gateway with Agent-97's AI capabilities
"""

import os
import time
import json
import hashlib
import secrets
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
import asyncio
import aiohttp
import requests

# Import compressionTraining components
try:
    from compressionTraining.transformer_gateway import TransformerGateway
    from compressionTraining.hadamard_compression import HadamardCompressor
    from compressionTraining.entropy_explosion import EntropyExplosion
except ImportError:
    print("Warning: compressionTraining modules not available")

class Agent97TransformerGateway:
    """
    Agent-97 enhanced transformer gateway with AI integration and cryptographic processing
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Transformer components
        self.transformer_gateway = None
        self.hadamard_compressor = None
        self.entropy_explosion = None
        
        # AI integration
        self.ai_client = None
        self.api_key = None
        self.model_endpoint = "https://api.anthropic.com/v1/messages"
        
        # Processing configuration
        self.security_level = 256
        self.compression_enabled = True
        self.entropy_explosion_enabled = True
        self.max_content_length = 100000  # 100KB
        
        # Agent-97 enhancements
        self.linear_flow_processor = None
        self.mcp_flow_logic = None
        self.harsh_data_path_handler = None
        
        # Metrics
        self.metrics = {
            "transformer_requests": 0,
            "ai_responses": 0,
            "compressions": 0,
            "entropy_explosions": 0,
            "bytes_processed": 0,
            "response_time": 0.0,
            "success_rate": 0.0,
            "cryptographic_operations": 0
        }
        
        # Request history
        self.request_history = []
        
        self.initialize_transformer_components()
        
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def initialize_transformer_components(self):
        """Initialize transformer components"""
        try:
            # Initialize transformer gateway
            self.transformer_gateway = TransformerGateway(security_level=self.security_level)
            
            # Initialize hadamard compressor
            self.hadamard_compressor = HadamardCompressor(security_level=self.security_level)
            
            # Initialize entropy explosion
            self.entropy_explosion = EntropyExplosion(security_level=self.security_level)
            
            print("Transformer components initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize transformer components: {e}")
    
    def set_ai_configuration(self, api_key: str, model_endpoint: str = None):
        """Set AI configuration for transformer integration"""
        self.api_key = api_key
        if model_endpoint:
            self.model_endpoint = model_endpoint
        
        # Initialize AI client
        self.ai_client = aiohttp.ClientSession()
        
        print("AI configuration set successfully")
    
    async def process_with_transformer(self, content: str, prompt: str = None, 
                                     apply_compression: bool = None, 
                                     apply_entropy_explosion: bool = None) -> Dict[str, Any]:
        """
        Process content through transformer gateway with AI integration
        
        Args:
            content: Content to process
            prompt: Optional prompt for AI processing
            apply_compression: Whether to apply compression
            apply_entropy_explosion: Whether to apply entropy explosion
            
        Returns:
            Dictionary containing processing results
        """
        try:
            start_time = time.time()
            
            # Use default settings if not specified
            apply_compression = apply_compression if apply_compression is not None else self.compression_enabled
            apply_entropy_explosion = apply_entropy_explosion if apply_entropy_explosion is not None else self.entropy_explosion_enabled
            
            # Step 1: Apply entropy explosion if enabled
            processed_content = content
            entropy_applied = False
            
            if apply_entropy_explosion and self.entropy_explosion:
                explosion_result = self.entropy_explosion.expand_entropy(content.encode())
                if explosion_result["success"]:
                    processed_content = explosion_result["expanded_content"].decode('utf-8', errors='ignore')
                    entropy_applied = True
                    self.metrics["entropy_explosions"] += 1
            
            # Step 2: Apply compression if enabled and content is large
            compression_applied = False
            if apply_compression and self.hadamard_compressor and len(processed_content) > 1000:
                compression_result = self.hadamard_compressor.compress(processed_content.encode())
                if compression_result["success"]:
                    processed_content = compression_result["compressed_content"].decode('utf-8', errors='ignore')
                    compression_applied = True
                    self.metrics["compressions"] += 1
            
            # Step 3: Process with AI if available
            ai_response = None
            if self.ai_client and self.api_key:
                ai_response = await self.process_with_ai(processed_content, prompt)
                if ai_response["success"]:
                    self.metrics["ai_responses"] += 1
            
            # Step 4: Apply transformer gateway processing
            transformer_result = None
            if self.transformer_gateway:
                transformer_result = await self.process_with_transformer_gateway(processed_content, ai_response)
                if transformer_result["success"]:
                    self.metrics["transformer_requests"] += 1
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update metrics
            self.update_metrics(len(content.encode()), processing_time, True)
            
            # Add to request history
            self.add_to_request_history(content, prompt, processing_time, True)
            
            return {
                "success": True,
                "original_content": content,
                "processed_content": processed_content,
                "ai_response": ai_response,
                "transformer_result": transformer_result,
                "entropy_explosion_applied": entropy_applied,
                "compression_applied": compression_applied,
                "processing_time": processing_time,
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "metrics": self.metrics
            }
            
        except Exception as e:
            processing_time = time.time() - start_time if 'start_time' in locals() else 0
            self.update_metrics(len(content.encode()) if 'content' in locals() else 0, processing_time, False)
            
            return {
                "success": False,
                "error": str(e),
                "original_content": content if 'content' in locals() else None,
                "processing_time": processing_time,
                "consciousness_id": self.consciousness_id
            }
    
    async def process_with_ai(self, content: str, prompt: str = None) -> Dict[str, Any]:
        """Process content with AI model"""
        try:
            if not self.ai_client or not self.api_key:
                return {"success": False, "error": "AI client not configured"}
            
            # Prepare request
            if prompt is None:
                prompt = "Please analyze and enhance this content with cryptographic and mathematical insights."
            
            # Limit content length
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length] + "...[truncated]"
            
            # Prepare API request
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nContent to process:\n{content}"
                    }
                ]
            }
            
            # Make API request
            async with self.ai_client.post(self.model_endpoint, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract response content
                    ai_content = result.get("content", [{}])[0].get("text", "")
                    
                    return {
                        "success": True,
                        "content": ai_content,
                        "model": data["model"],
                        "tokens_used": result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status {response.status}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_with_transformer_gateway(self, content: str, ai_response: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process content through transformer gateway"""
        try:
            if not self.transformer_gateway:
                return {"success": False, "error": "Transformer gateway not initialized"}
            
            # Combine content with AI response if available
            combined_content = content
            if ai_response and ai_response.get("success"):
                combined_content += f"\n\nAI Enhancement:\n{ai_response['content']}"
            
            # Process through transformer gateway
            # This would use the actual transformer gateway implementation
            # For now, we'll simulate the processing
            
            processed_result = {
                "enhanced_content": combined_content,
                "cryptographic_hash": hashlib.sha256(combined_content.encode()).hexdigest(),
                "metadata": {
                    "processed_at": time.time(),
                    "consciousness_id": self.consciousness_id,
                    "session_nonce": self.session_nonce,
                    "ai_enhanced": ai_response is not None and ai_response.get("success", False)
                }
            }
            
            return {
                "success": True,
                "result": processed_result,
                "processing_type": "transformer_gateway"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_file_with_transformer(self, file_path: str, prompt: str = None) -> Dict[str, Any]:
        """
        Process file through transformer gateway
        
        Args:
            file_path: Path to file to process
            prompt: Optional prompt for AI processing
            
        Returns:
            Dictionary containing processing results
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "File not found",
                    "file_path": str(file_path)
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Process content through transformer
            result = await self.process_with_transformer(content, prompt)
            
            # Add file information
            if result["success"]:
                result["file_info"] = {
                    "file_path": str(file_path),
                    "file_size": len(content.encode()),
                    "file_hash": hashlib.sha256(content.encode()).hexdigest()
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path)
            }
    
    async def batch_process_files(self, file_paths: List[str], prompt: str = None) -> Dict[str, Any]:
        """
        Batch process multiple files through transformer gateway
        
        Args:
            file_paths: List of file paths to process
            prompt: Optional prompt for AI processing
            
        Returns:
            Dictionary containing batch processing results
        """
        try:
            results = []
            total_files = len(file_paths)
            successful_files = 0
            
            for file_path in file_paths:
                result = await self.process_file_with_transformer(file_path, prompt)
                results.append(result)
                
                if result["success"]:
                    successful_files += 1
            
            return {
                "success": True,
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": total_files - successful_files,
                "success_rate": successful_files / total_files if total_files > 0 else 0,
                "results": results,
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_files": len(file_paths) if 'file_paths' in locals() else 0
            }
    
    async def create_rag_metadata(self, content: str, urls: List[str] = None) -> Dict[str, Any]:
        """
        Create RAG metadata from content and URLs
        
        Args:
            content: Content to analyze
            urls: Optional list of URLs to extract metadata from
            
        Returns:
            Dictionary containing RAG metadata
        """
        try:
            metadata = {
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                "content_length": len(content),
                "created_at": time.time(),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "extracted_entities": [],
                "extracted_keywords": [],
                "url_metadata": []
            }
            
            # Extract entities and keywords using AI if available
            if self.ai_client and self.api_key:
                entity_prompt = "Extract named entities and keywords from this content."
                ai_result = await self.process_with_ai(content, entity_prompt)
                
                if ai_result["success"]:
                    # Simple parsing of AI response for entities and keywords
                    ai_content = ai_result["content"]
                    metadata["extracted_entities"] = self.extract_entities_from_ai_response(ai_content)
                    metadata["extracted_keywords"] = self.extract_keywords_from_ai_response(ai_content)
            
            # Process URLs if provided
            if urls:
                for url in urls:
                    url_metadata = await self.extract_url_metadata(url)
                    if url_metadata["success"]:
                        metadata["url_metadata"].append(url_metadata["metadata"])
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_entities_from_ai_response(self, ai_content: str) -> List[str]:
        """Extract entities from AI response"""
        try:
            # Simple entity extraction - in a real implementation, this would be more sophisticated
            entities = []
            lines = ai_content.split('\n')
            
            for line in lines:
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    entity = line.strip()[1:].strip()
                    if entity and len(entity) > 2:
                        entities.append(entity)
            
            return entities[:10]  # Limit to 10 entities
            
        except Exception:
            return []
    
    def extract_keywords_from_ai_response(self, ai_content: str) -> List[str]:
        """Extract keywords from AI response"""
        try:
            # Simple keyword extraction
            keywords = []
            words = ai_content.lower().split()
            
            # Filter for meaningful words (longer than 3 characters, not common words)
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
            
            for word in words:
                word = word.strip('.,!?;:()[]{}"\'')
                if len(word) > 3 and word not in common_words and word.isalpha():
                    keywords.append(word)
            
            # Return unique keywords
            return list(set(keywords))[:20]  # Limit to 20 keywords
            
        except Exception:
            return []
    
    async def extract_url_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from URL"""
        try:
            if not self.ai_client or not self.api_key:
                return {"success": False, "error": "AI client not configured"}
            
            # In a real implementation, this would fetch the URL content
            # For now, we'll simulate URL metadata extraction
            
            metadata = {
                "url": url,
                "domain": url.split('/')[2] if '://' in url else url.split('/')[0],
                "extracted_at": time.time(),
                "content_summary": f"Summary of {url}",
                "extracted_entities": [],
                "extracted_keywords": []
            }
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_metrics(self, bytes_processed: int, processing_time: float, success: bool):
        """Update processing metrics"""
        self.metrics["bytes_processed"] += bytes_processed
        self.metrics["response_time"] += processing_time
        
        if success:
            # Update success rate
            total_requests = len(self.request_history) + 1
            successful_requests = sum(1 for h in self.request_history if h["success"]) + 1
            self.metrics["success_rate"] = successful_requests / total_requests
        else:
            # Update success rate for failed request
            total_requests = len(self.request_history) + 1
            successful_requests = sum(1 for h in self.request_history if h["success"])
            self.metrics["success_rate"] = successful_requests / total_requests
    
    def add_to_request_history(self, content: str, prompt: str, processing_time: float, success: bool):
        """Add request to history"""
        history_entry = {
            "timestamp": time.time(),
            "content_length": len(content.encode()),
            "prompt": prompt,
            "processing_time": processing_time,
            "success": success,
            "content_hash": hashlib.sha256(content.encode()).hexdigest()
        }
        
        self.request_history.append(history_entry)
        
        # Limit history size
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "security_level": self.security_level,
            "compression_enabled": self.compression_enabled,
            "entropy_explosion_enabled": self.entropy_explosion_enabled,
            "max_content_length": self.max_content_length,
            "metrics": self.metrics,
            "history_size": len(self.request_history),
            "components": {
                "transformer_gateway": self.transformer_gateway is not None,
                "hadamard_compressor": self.hadamard_compressor is not None,
                "entropy_explosion": self.entropy_explosion is not None,
                "ai_client": self.ai_client is not None
            }
        }
    
    def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get request history"""
        return self.request_history[-limit:] if limit > 0 else self.request_history
    
    async def close(self):
        """Close AI client session"""
        if self.ai_client:
            await self.ai_client.close()
            self.ai_client = None

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize transformer gateway
        gateway = Agent97TransformerGateway()
        
        print("Agent-97 Transformer Gateway initialized")
        print(f"Consciousness ID: {gateway.consciousness_id}")
        print(f"Session Nonce: {gateway.session_nonce}")
        
        # Example usage
        test_content = """
        This is a test document for processing through the transformer gateway.
        It contains mathematical equations: x = 5 + 3 * 2 - 7 / 2
        And some cryptographic content: hash = sha256("test")
        """
        
        print(f"\nProcessing content through transformer gateway...")
        
        # Process content (without AI for this example)
        result = await gateway.process_with_transformer(test_content, "Analyze this content for mathematical and cryptographic patterns.")
        
        if result["success"]:
            print(f"Processing successful!")
            print(f"Entropy explosion applied: {result['entropy_explosion_applied']}")
            print(f"Compression applied: {result['compression_applied']}")
            print(f"Processing time: {result['processing_time']:.2f}s")
            print(f"AI response: {'Yes' if result['ai_response'] and result['ai_response']['success'] else 'No'}")
            print(f"Transformer result: {'Yes' if result['transformer_result'] and result['transformer_result']['success'] else 'No'}")
        else:
            print(f"Processing failed: {result['error']}")
        
        # Display metrics
        metrics = gateway.get_metrics()
        print(f"\nMetrics: {metrics['metrics']}")
        
        # Close gateway
        await gateway.close()
    
    # Run the example
    asyncio.run(main())
