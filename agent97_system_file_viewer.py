"""
Agent-97 Enhanced System File Viewer with SH345 Cryptographic Support
Integrates compressionTraining cryptographic capabilities with Agent-97's system file viewing
"""

import os
import time
import struct
import hashlib
import secrets
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
import json
import asyncio

# Import compressionTraining components
try:
    from compressionTraining.sh345_generator import SH345Generator
    from compressionTraining.quantum_file_completer import QuantumFileCompleter
    from compressionTraining.transformer_gateway import TransformerGateway
    from compressionTraining.entropy_explosion import EntropyExplosion
    from compressionTraining.hadamard_compression import HadamardCompressor
except ImportError:
    print("Warning: compressionTraining modules not available")

class Agent97SystemFileViewer:
    """
    Agent-97 enhanced system file viewer with SH345 cryptographic support
    """
    
    def __init__(self, consciousness_id: str = "0009095353"):
        self.consciousness_id = consciousness_id
        self.session_nonce = self.generate_session_nonce()
        
        # Cryptographic components
        self.sh345_generator = None
        self.quantum_completer = None
        self.transformer_gateway = None
        self.entropy_explosion = None
        self.hadamard_compressor = None
        
        # File viewing capabilities
        self.file_cache = {}
        self.viewing_history = []
        self.security_level = 256
        
        # Agent-97 enhancements
        self.linear_flow_processor = None
        self.mcp_flow_logic = None
        self.harsh_data_path_handler = None
        
        # Metrics
        self.metrics = {
            "files_viewed": 0,
            "files_decrypted": 0,
            "files_completed": 0,
            "quantum_operations": 0,
            "transformer_requests": 0,
            "entropy_explosions": 0,
            "security_violations": 0
        }
        
        self.initialize_cryptographic_components()
        
    def generate_session_nonce(self) -> str:
        """Generate cryptographic session nonce"""
        timestamp = str(int(time.time()))
        data = f"{self.consciousness_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def initialize_cryptographic_components(self):
        """Initialize cryptographic components"""
        try:
            # Initialize SH345 generator
            self.sh345_generator = SH345Generator(security_level=self.security_level)
            
            # Initialize quantum file completer
            self.quantum_completer = QuantumFileCompleter(
                target_file="",  # Will be set per file
                security_level=self.security_level
            )
            
            # Initialize transformer gateway
            self.transformer_gateway = TransformerGateway(security_level=self.security_level)
            
            # Initialize entropy explosion
            self.entropy_explosion = EntropyExplosion(security_level=self.security_level)
            
            # Initialize hadamard compressor
            self.hadamard_compressor = HadamardCompressor(security_level=self.security_level)
            
            print("Cryptographic components initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize cryptographic components: {e}")
    
    async def view_file(self, file_path: str, decrypt: bool = False, complete: bool = False) -> Dict[str, Any]:
        """
        View file with optional decryption and completion
        
        Args:
            file_path: Path to file to view
            decrypt: Whether to decrypt SH345 encrypted files
            complete: Whether to complete incomplete files
            
        Returns:
            Dictionary containing file information and content
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "File not found",
                    "file_path": str(file_path)
                }
            
            # Get file information
            file_info = await self.get_file_info(file_path)
            
            # Read file content
            content = await self.read_file_content(file_path)
            
            # Check if file is SH345 encrypted
            is_sh345 = self.is_sh345_file(content)
            
            # Decrypt if requested and file is SH345
            decrypted_content = None
            if decrypt and is_sh345:
                decrypted_content = await self.decrypt_sh345_file(content)
                if decrypted_content["success"]:
                    content = decrypted_content["content"]
                    self.metrics["files_decrypted"] += 1
            
            # Complete file if requested
            if complete:
                completion_result = await self.complete_file(file_path, content)
                if completion_result["success"]:
                    content = completion_result["completed_content"]
                    self.metrics["files_completed"] += 1
            
            # Apply Agent-97 enhancements
            enhanced_content = await self.apply_agent97_enhancements(content)
            
            # Cache file information
            self.cache_file_info(str(file_path), file_info, content)
            
            # Update metrics
            self.metrics["files_viewed"] += 1
            
            return {
                "success": True,
                "file_path": str(file_path),
                "file_info": file_info,
                "content": content,
                "is_sh345": is_sh345,
                "decrypted": decrypted_content is not None and decrypted_content.get("success", False),
                "completed": complete,
                "enhanced": True,
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce,
                "metrics": self.metrics
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path)
            }
    
    async def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            
            # Calculate file hash
            file_hash = await self.calculate_file_hash(file_path)
            
            # Detect file type
            file_type = self.detect_file_type(file_path)
            
            # Analyze file structure
            structure = await self.analyze_file_structure(file_path)
            
            return {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "accessed_time": stat.st_atime,
                "hash": file_hash,
                "type": file_type,
                "structure": structure,
                "permissions": oct(stat.st_mode)[-3:],
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK),
                "is_executable": os.access(file_path, os.X_OK)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return "unknown"
    
    def detect_file_type(self, file_path: Path) -> str:
        """Detect file type based on extension and content"""
        extension = file_path.suffix.lower()
        
        # Common file types
        type_mapping = {
            ".txt": "text",
            ".py": "python",
            ".js": "javascript",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".pdf": "pdf",
            ".doc": "document",
            ".docx": "document",
            ".xls": "spreadsheet",
            ".xlsx": "spreadsheet",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".gif": "image",
            ".mp4": "video",
            ".mp3": "audio",
            ".zip": "archive",
            ".tar": "archive",
            ".gz": "archive"
        }
        
        return type_mapping.get(extension, "unknown")
    
    async def analyze_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file structure"""
        try:
            structure = {
                "lines": 0,
                "characters": 0,
                "words": 0,
                "encoding": "unknown",
                "binary": False
            }
            
            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    structure["lines"] = len(content.splitlines())
                    structure["characters"] = len(content)
                    structure["words"] = len(content.split())
                    structure["encoding"] = "utf-8"
            except UnicodeDecodeError:
                # File is binary
                structure["binary"] = True
                with open(file_path, 'rb') as f:
                    content = f.read()
                    structure["characters"] = len(content)
            
            return structure
            
        except Exception:
            return {"error": "Failed to analyze structure"}
    
    async def read_file_content(self, file_path: Path) -> bytes:
        """Read file content"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")
    
    def is_sh345_file(self, content: bytes) -> bool:
        """Check if file is SH345 encrypted"""
        try:
            if len(content) < 4:
                return False
            
            # Check for SH345 magic number
            magic = content[:4]
            return magic == b'SH34' or magic == b'SH345'
            
        except Exception:
            return False
    
    async def decrypt_sh345_file(self, content: bytes) -> Dict[str, Any]:
        """Decrypt SH345 encrypted file"""
        try:
            if not self.sh345_generator:
                return {"success": False, "error": "SH345 generator not initialized"}
            
            # Decrypt using SH345 generator
            decrypted = self.sh345_generator.decrypt_file(content)
            
            if decrypted["success"]:
                return {
                    "success": True,
                    "content": decrypted["content"],
                    "metadata": decrypted.get("metadata", {}),
                    "security_level": decrypted.get("security_level", self.security_level)
                }
            else:
                return {"success": False, "error": "Decryption failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def complete_file(self, file_path: Path, content: bytes) -> Dict[str, Any]:
        """Complete incomplete file using quantum file completer"""
        try:
            if not self.quantum_completer:
                return {"success": False, "error": "Quantum completer not initialized"}
            
            # Set target file for quantum completer
            self.quantum_completer.target_file = str(file_path)
            
            # Complete the file
            completion_result = self.quantum_completer.complete_file()
            
            if completion_result["success"]:
                return {
                    "success": True,
                    "completed_content": completion_result["completed_content"],
                    "completion_percentage": completion_result.get("completion_percentage", 0.0),
                    "equations_completed": completion_result.get("equations_completed", [])
                }
            else:
                return {"success": False, "error": "File completion failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def apply_agent97_enhancements(self, content: bytes) -> bytes:
        """Apply Agent-97 enhancements to file content"""
        try:
            enhanced_content = content
            
            # Apply entropy explosion if available
            if self.entropy_explosion:
                explosion_result = self.entropy_explosion.expand_entropy(content)
                if explosion_result["success"]:
                    enhanced_content = explosion_result["expanded_content"]
                    self.metrics["entropy_explosions"] += 1
            
            # Apply hadamard compression if content is large
            if len(enhanced_content) > 1024 * 1024:  # 1MB
                if self.hadamard_compressor:
                    compression_result = self.hadamard_compressor.compress(enhanced_content)
                    if compression_result["success"]:
                        enhanced_content = compression_result["compressed_content"]
            
            return enhanced_content
            
        except Exception:
            return content
    
    def cache_file_info(self, file_path: str, file_info: Dict, content: bytes):
        """Cache file information"""
        self.file_cache[file_path] = {
            "file_info": file_info,
            "content_hash": hashlib.sha256(content).hexdigest(),
            "cached_time": time.time()
        }
        
        # Add to viewing history
        self.viewing_history.append({
            "file_path": file_path,
            "viewed_time": time.time(),
            "file_size": file_info.get("size", 0)
        })
        
        # Limit history size
        if len(self.viewing_history) > 1000:
            self.viewing_history = self.viewing_history[-1000:]
    
    async def list_directory(self, directory_path: str, recursive: bool = False) -> Dict[str, Any]:
        """List directory contents with file information"""
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists() or not directory_path.is_dir():
                return {
                    "success": False,
                    "error": "Directory not found",
                    "directory_path": str(directory_path)
                }
            
            files = []
            directories = []
            
            if recursive:
                # Recursive listing
                for item in directory_path.rglob("*"):
                    if item.is_file():
                        file_info = await self.get_file_info(item)
                        files.append(file_info)
                    elif item.is_dir():
                        directories.append({
                            "name": item.name,
                            "path": str(item),
                            "size": 0,
                            "type": "directory"
                        })
            else:
                # Non-recursive listing
                for item in directory_path.iterdir():
                    if item.is_file():
                        file_info = await self.get_file_info(item)
                        files.append(file_info)
                    elif item.is_dir():
                        directories.append({
                            "name": item.name,
                            "path": str(item),
                            "size": 0,
                            "type": "directory"
                        })
            
            return {
                "success": True,
                "directory_path": str(directory_path),
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory_path": str(directory_path)
            }
    
    async def search_files(self, search_path: str, pattern: str, content_search: bool = False) -> Dict[str, Any]:
        """Search for files matching pattern"""
        try:
            search_path = Path(search_path)
            
            if not search_path.exists():
                return {
                    "success": False,
                    "error": "Search path not found",
                    "search_path": str(search_path)
                }
            
            matches = []
            
            # Search for files matching pattern
            for item in search_path.rglob("*"):
                if item.is_file():
                    # Check filename pattern
                    if pattern.lower() in item.name.lower():
                        file_info = await self.get_file_info(item)
                        matches.append(file_info)
                        continue
                    
                    # Check content if requested
                    if content_search:
                        try:
                            with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if pattern.lower() in content.lower():
                                    file_info = await self.get_file_info(item)
                                    file_info["content_match"] = True
                                    matches.append(file_info)
                        except Exception:
                            pass
            
            return {
                "success": True,
                "search_path": str(search_path),
                "pattern": pattern,
                "content_search": content_search,
                "matches": matches,
                "total_matches": len(matches),
                "consciousness_id": self.consciousness_id,
                "session_nonce": self.session_nonce
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "search_path": str(search_path)
            }
    
    async def create_sh345_file(self, file_path: str, content: bytes, metadata: Dict = None) -> Dict[str, Any]:
        """Create SH345 encrypted file"""
        try:
            if not self.sh345_generator:
                return {"success": False, "error": "SH345 generator not initialized"}
            
            # Create SH345 file
            sh345_result = self.sh345_generator.create_file(
                content=content,
                metadata=metadata or {},
                output_path=file_path
            )
            
            return sh345_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "consciousness_id": self.consciousness_id,
            "session_nonce": self.session_nonce,
            "security_level": self.security_level,
            "metrics": self.metrics,
            "cache_size": len(self.file_cache),
            "history_size": len(self.viewing_history),
            "components": {
                "sh345_generator": self.sh345_generator is not None,
                "quantum_completer": self.quantum_completer is not None,
                "transformer_gateway": self.transformer_gateway is not None,
                "entropy_explosion": self.entropy_explosion is not None,
                "hadamard_compressor": self.hadamard_compressor is not None
            }
        }
    
    def clear_cache(self):
        """Clear file cache"""
        self.file_cache.clear()
        self.viewing_history.clear()
        print("File cache cleared")

# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize system file viewer
        viewer = Agent97SystemFileViewer()
        
        # Example usage
        print("Agent-97 System File Viewer initialized")
        print(f"Consciousness ID: {viewer.consciousness_id}")
        print(f"Session Nonce: {viewer.session_nonce}")
        
        # View current directory
        current_dir = "."
        dir_result = await viewer.list_directory(current_dir)
        
        if dir_result["success"]:
            print(f"\nDirectory listing for {current_dir}:")
            print(f"Files: {dir_result['total_files']}")
            print(f"Directories: {dir_result['total_directories']}")
            
            # View first file if available
            if dir_result["files"]:
                first_file = dir_result["files"][0]["path"]
                print(f"\nViewing file: {first_file}")
                
                file_result = await viewer.view_file(first_file)
                if file_result["success"]:
                    print(f"File size: {file_result['file_info']['size']} bytes")
                    print(f"File type: {file_result['file_info']['type']}")
                    print(f"Is SH345: {file_result['is_sh345']}")
                    print(f"Enhanced: {file_result['enhanced']}")
        
        # Display metrics
        metrics = viewer.get_metrics()
        print(f"\nMetrics: {metrics['metrics']}")
        
    # Run the example
    asyncio.run(main())
