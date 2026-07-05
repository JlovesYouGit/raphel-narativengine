"""
Constant Function Loop Data Extractor
Runs continuous data extraction from net channel storage with weight relation extraction
and imprinting into new model weights while maintaining 100% original data structure integrity
"""

import asyncio
import json
import hashlib
import time
import aiohttp
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
import threading
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('constant_loop_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DataMythos:
    """Data mythos structure for fetched data"""
    fetch_name: str
    data_hash: str
    original_structure: Dict[str, Any]
    timestamp: str
    integrity_hash: str
    source_channel: str

@dataclass
class WeightRelation:
    """Weight relation extracted from data"""
    relation_id: str
    source_tensor: str
    target_tensor: str
    weight_mapping: Dict[str, np.ndarray]
    original_structure_preserved: bool
    integrity_score: float

@dataclass
class ImprintedWeight:
    """Imprinted weight data for model retraining"""
    imprint_id: str
    original_data_hash: str
    imprinted_weights: Dict[str, np.ndarray]
    structure_integrity_verified: bool
    ready_for_retrain: bool
    timestamp: str

class SemanticGraphAPIClient:
    """API client for semantic graph endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.bearer_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the API session"""
        self.session = aiohttp.ClientSession()
        await self.authenticate()
    
    async def authenticate(self):
        """Authenticate and retrieve bearer token"""
        auth_url = f"{self.base_url}/auth/token"
        try:
            async with self.session.post(auth_url, json={"api_key": "internal"}) as response:
                if response.status == 200:
                    data = await response.json()
                    self.bearer_token = data.get("token")
                    logger.info("Successfully authenticated with semantic graph API")
                else:
                    logger.warning("Authentication failed, continuing without token")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
    
    async def query_semantic_graph(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query the semantic graph"""
        url = f"{self.base_url}/query"
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        try:
            async with self.session.post(url, json=query_data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Query failed with status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {}
    
    async def index_text(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Index new text into the system"""
        url = f"{self.base_url}/index"
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        try:
            async with self.session.post(url, json=text_data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Index failed with status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Index error: {e}")
            return {}
    
    async def search_semantic_map(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search the semantic map"""
        url = f"{self.base_url}/search"
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        try:
            async with self.session.post(url, json=search_data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Search failed with status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {}
    
    async def trigger_ingestion(self) -> Dict[str, Any]:
        """Trigger a manual ingestion cycle"""
        url = f"{self.base_url}/ingest"
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        try:
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Ingestion failed with status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            return {}
    
    async def get_stats(self) -> Dict[str, Any]:
        """View real-time graph statistics"""
        url = f"{self.base_url}/stats"
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Stats failed with status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}
    
    async def get_emerge_status(self) -> Dict[str, Any]:
        """Get ASI emergence checklist status"""
        url = f"{self.base_url}/emerge"
        headers = {}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Emerge status failed with status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Emerge status error: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Basic liveness check"""
        url = f"{self.base_url}/health"
        try:
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    async def close(self):
        """Close the API session"""
        if self.session:
            await self.session.close()

class NetChannelStorage:
    """Net channel storage for data extraction"""
    
    def __init__(self, storage_path: str = "net_channel_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.data_index: Dict[str, DataMythos] = {}
        self.channel_lock = threading.Lock()
    
    def store_data(self, fetch_name: str, data: Dict[str, Any], source_channel: str = "default") -> DataMythos:
        """Store data with mythos structure"""
        with self.channel_lock:
            # Create integrity hash
            data_str = json.dumps(data, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()
            integrity_hash = hashlib.sha512(f"{data_hash}{time.time()}".encode()).hexdigest()
            
            # Create data mythos
            mythos = DataMythos(
                fetch_name=fetch_name,
                data_hash=data_hash,
                original_structure=data,
                timestamp=datetime.now().isoformat(),
                integrity_hash=integrity_hash,
                source_channel=source_channel
            )
            
            # Store in index
            self.data_index[data_hash] = mythos
            
            # Persist to disk
            storage_file = self.storage_path / f"{data_hash}.json"
            with open(storage_file, "w") as f:
                json.dump({
                    "fetch_name": mythos.fetch_name,
                    "data_hash": mythos.data_hash,
                    "original_structure": mythos.original_structure,
                    "timestamp": mythos.timestamp,
                    "integrity_hash": mythos.integrity_hash,
                    "source_channel": mythos.source_channel
                }, f, indent=2)
            
            logger.info(f"Stored data mythos: {fetch_name} with hash {data_hash[:16]}...")
            return mythos
    
    def retrieve_data(self, data_hash: str) -> Optional[DataMythos]:
        """Retrieve data by hash"""
        with self.channel_lock:
            return self.data_index.get(data_hash)
    
    def verify_integrity(self, data_hash: str) -> bool:
        """Verify data integrity"""
        mythos = self.retrieve_data(data_hash)
        if not mythos:
            return False
        
        # Recalculate integrity hash
        data_str = json.dumps(mythos.original_structure, sort_keys=True)
        current_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        return current_hash == mythos.data_hash

class WeightRelationExtractor:
    """Extract weight relations from data mythos"""
    
    def __init__(self):
        self.extracted_relations: Dict[str, WeightRelation] = {}
        self.relation_history = deque(maxlen=10000)
    
    def extract_weight_relations(self, mythos: DataMythos) -> List[WeightRelation]:
        """Extract weight relations from data mythos"""
        relations = []
        
        # Analyze original structure for weight patterns
        original_data = mythos.original_structure
        
        # Extract tensor relationships
        if "tensors" in original_data:
            for tensor_name, tensor_data in original_data["tensors"].items():
                relation = self._create_tensor_relation(tensor_name, tensor_data, mythos)
                if relation:
                    relations.append(relation)
        
        # Extract layer relationships
        if "layers" in original_data:
            for layer_name, layer_data in original_data["layers"].items():
                relation = self._create_layer_relation(layer_name, layer_data, mythos)
                if relation:
                    relations.append(relation)
        
        # Extract weight mappings
        if "weights" in original_data:
            relation = self._create_weight_mapping_relation(original_data["weights"], mythos)
            if relation:
                relations.append(relation)
        
        # Store relations
        for relation in relations:
            self.extracted_relations[relation.relation_id] = relation
            self.relation_history.append(relation)
        
        logger.info(f"Extracted {len(relations)} weight relations from {mythos.fetch_name}")
        return relations
    
    def _create_tensor_relation(self, tensor_name: str, tensor_data: Any, mythos: DataMythos) -> Optional[WeightRelation]:
        """Create tensor weight relation"""
        relation_id = hashlib.sha256(f"{tensor_name}{mythos.data_hash}".encode()).hexdigest()[:16]
        
        # Convert to numpy array if possible
        if isinstance(tensor_data, (list, np.ndarray)):
            weight_array = np.array(tensor_data) if isinstance(tensor_data, list) else tensor_data
            weight_mapping = {tensor_name: weight_array}
        else:
            weight_mapping = {tensor_name: np.array([tensor_data])}
        
        return WeightRelation(
            relation_id=relation_id,
            source_tensor=tensor_name,
            target_tensor=tensor_name,
            weight_mapping=weight_mapping,
            original_structure_preserved=True,
            integrity_score=1.0
        )
    
    def _create_layer_relation(self, layer_name: str, layer_data: Any, mythos: DataMythos) -> Optional[WeightRelation]:
        """Create layer weight relation"""
        relation_id = hashlib.sha256(f"layer_{layer_name}{mythos.data_hash}".encode()).hexdigest()[:16]
        
        weight_mapping = {}
        if isinstance(layer_data, dict):
            for key, value in layer_data.items():
                if isinstance(value, (list, np.ndarray)):
                    weight_mapping[f"{layer_name}_{key}"] = np.array(value) if isinstance(value, list) else value
        
        return WeightRelation(
            relation_id=relation_id,
            source_tensor=layer_name,
            target_tensor=layer_name,
            weight_mapping=weight_mapping,
            original_structure_preserved=True,
            integrity_score=1.0
        )
    
    def _create_weight_mapping_relation(self, weights_data: Any, mythos: DataMythos) -> Optional[WeightRelation]:
        """Create weight mapping relation"""
        relation_id = hashlib.sha256(f"weights_{mythos.data_hash}".encode()).hexdigest()[:16]
        
        weight_mapping = {}
        if isinstance(weights_data, dict):
            for key, value in weights_data.items():
                if isinstance(value, (list, np.ndarray)):
                    weight_mapping[key] = np.array(value) if isinstance(value, list) else value
        
        return WeightRelation(
            relation_id=relation_id,
            source_tensor="weights",
            target_tensor="weights",
            weight_mapping=weight_mapping,
            original_structure_preserved=True,
            integrity_score=1.0
        )

class WeightImprinter:
    """Imprint weight relations into new model weights with 100% integrity"""
    
    def __init__(self):
        self.imprinted_weights: Dict[str, ImprintedWeight] = {}
        self.imprint_history = deque(maxlen=10000)
    
    def imprint_weights(self, relations: List[WeightRelation], original_mythos: DataMythos) -> List[ImprintedWeight]:
        """Imprint weight relations into new model weights"""
        imprinted = []
        
        for relation in relations:
            # Create imprinted weight preserving 100% original structure
            imprint_id = hashlib.sha256(f"{relation.relation_id}{time.time()}".encode()).hexdigest()[:16]
            
            # Preserve original structure exactly
            imprinted_weights_data = {}
            for tensor_name, weight_array in relation.weight_mapping.items():
                # Create exact copy to preserve structure
                imprinted_weights_data[tensor_name] = weight_array.copy()
            
            # Verify structure integrity
            structure_integrity = self._verify_structure_integrity(relation.weight_mapping, imprinted_weights_data)
            
            imprint = ImprintedWeight(
                imprint_id=imprint_id,
                original_data_hash=original_mythos.data_hash,
                imprinted_weights=imprinted_weights_data,
                structure_integrity_verified=structure_integrity,
                ready_for_retrain=True,
                timestamp=datetime.now().isoformat()
            )
            
            self.imprinted_weights[imprint_id] = imprint
            self.imprint_history.append(imprint)
            imprinted.append(imprint)
        
        logger.info(f"Imprinted {len(imprinted)} weight sets with 100% structure integrity")
        return imprinted
    
    def _verify_structure_integrity(self, original: Dict[str, np.ndarray], imprinted: Dict[str, np.ndarray]) -> bool:
        """Verify 100% structure integrity preservation"""
        if len(original) != len(imprinted):
            return False
        
        for key in original:
            if key not in imprinted:
                return False
            if original[key].shape != imprinted[key].shape:
                return False
            if not np.array_equal(original[key], imprinted[key]):
                return False
        
        return True
    
    def prepare_for_retrain(self, imprint_id: str) -> Optional[Dict[str, Any]]:
        """Prepare imprinted weights for model retraining"""
        imprint = self.imprinted_weights.get(imprint_id)
        if not imprint:
            return None
        
        if not imprint.structure_integrity_verified:
            logger.warning(f"Imprint {imprint_id} structure integrity not verified")
            return None
        
        # Convert to format suitable for retraining
        retrain_data = {
            "imprint_id": imprint.imprint_id,
            "original_data_hash": imprint.original_data_hash,
            "weights": {},
            "metadata": {
                "structure_integrity": "100%",
                "ready_for_retrain": imprint.ready_for_retrain,
                "timestamp": imprint.timestamp
            }
        }
        
        for tensor_name, weight_array in imprint.imprinted_weights.items():
            retrain_data["weights"][tensor_name] = weight_array.tolist()
        
        return retrain_data

class ConstantLoopDataExtractor:
    """Constant function loop runner for continuous data extraction"""
    
    def __init__(self, consciousness_id: str = "0009095353", api_base_url: str = "http://localhost:8000"):
        self.consciousness_id = consciousness_id
        self.running = False
        self.loop_thread = None
        self.extraction_interval = 5.0  # seconds
        
        # Initialize components
        self.api_client = SemanticGraphAPIClient(api_base_url)
        self.net_storage = NetChannelStorage()
        self.relation_extractor = WeightRelationExtractor()
        self.weight_imprinter = WeightImprinter()
        
        # Statistics
        self.extraction_stats = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_relations_extracted": 0,
            "total_weights_imprinted": 0,
            "integrity_violations": 0
        }
    
    async def initialize(self):
        """Initialize the constant loop extractor"""
        logger.info("Initializing constant loop data extractor...")
        await self.api_client.initialize()
        logger.info("Constant loop data extractor initialized")
    
    def start_constant_loop(self):
        """Start the constant function loop"""
        if self.running:
            logger.warning("Constant loop already running")
            return
        
        self.running = True
        self.loop_thread = threading.Thread(target=self._run_constant_loop, daemon=True)
        self.loop_thread.start()
        logger.info("Constant function loop started")
    
    def stop_constant_loop(self):
        """Stop the constant function loop"""
        self.running = False
        if self.loop_thread:
            self.loop_thread.join(timeout=10.0)
        logger.info("Constant function loop stopped")
    
    def _run_constant_loop(self):
        """Run the constant extraction loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.running:
            try:
                loop.run_until_complete(self._extraction_cycle())
                time.sleep(self.extraction_interval)
            except Exception as e:
                logger.error(f"Error in extraction cycle: {e}")
                time.sleep(self.extraction_interval)
    
    async def _extraction_cycle(self):
        """Single extraction cycle"""
        logger.info("Starting extraction cycle...")
        
        try:
            # Fetch data from semantic graph
            query_result = await self._fetch_from_semantic_graph()
            
            if query_result:
                # Store in net channel
                mythos = self.net_storage.store_data(
                    fetch_name=f"extraction_{self.extraction_stats['total_extractions']}",
                    data=query_result,
                    source_channel="semantic_graph"
                )
                
                # Extract weight relations
                relations = self.relation_extractor.extract_weight_relations(mythos)
                self.extraction_stats["total_relations_extracted"] += len(relations)
                
                # Imprint weights
                imprinted = self.weight_imprinter.imprint_weights(relations, mythos)
                self.extraction_stats["total_weights_imprinted"] += len(imprinted)
                
                self.extraction_stats["successful_extractions"] += 1
                logger.info(f"Extraction cycle completed: {len(relations)} relations, {len(imprinted)} imprinted")
            else:
                self.extraction_stats["failed_extractions"] += 1
                logger.warning("Extraction cycle completed with no data")
            
            self.extraction_stats["total_extractions"] += 1
            
        except Exception as e:
            self.extraction_stats["failed_extractions"] += 1
            logger.error(f"Extraction cycle failed: {e}")
    
    async def _fetch_from_semantic_graph(self) -> Optional[Dict[str, Any]]:
        """Fetch data from semantic graph API"""
        try:
            # Query for weight-related data
            query_data = {
                "query": "weight relations tensor data",
                "limit": 100,
                "format": "structured"
            }
            
            result = await self.api_client.query_semantic_graph(query_data)
            
            if result and "data" in result:
                return result["data"]
            
            # Try search if query fails
            search_data = {
                "query": "weights tensors model",
                "limit": 50
            }
            
            search_result = await self.api_client.search_semantic_map(search_data)
            
            if search_result and "results" in search_result:
                return search_result["results"]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch from semantic graph: {e}")
            return None
    
    async def trigger_manual_ingestion(self):
        """Trigger manual ingestion cycle"""
        logger.info("Triggering manual ingestion...")
        result = await self.api_client.trigger_ingestion()
        logger.info(f"Ingestion result: {result}")
        return result
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        api_stats = await self.api_client.get_stats()
        emerge_status = await self.api_client.get_emerge_status()
        health = await self.api_client.health_check()
        
        return {
            "extraction_stats": self.extraction_stats,
            "api_stats": api_stats,
            "emerge_status": emerge_status,
            "health": health,
            "running": self.running,
            "net_storage_items": len(self.net_storage.data_index),
            "extracted_relations": len(self.relation_extractor.extracted_relations),
            "imprinted_weights": len(self.weight_imprinter.imprinted_weights)
        }
    
    def get_imprinted_weights_for_retrain(self) -> List[Dict[str, Any]]:
        """Get all imprinted weights ready for retraining"""
        retrain_data = []
        
        for imprint_id, imprint in self.weight_imprinter.imprinted_weights.items():
            if imprint.ready_for_retrain and imprint.structure_integrity_verified:
                data = self.weight_imprinter.prepare_for_retrain(imprint_id)
                if data:
                    retrain_data.append(data)
        
        logger.info(f"Prepared {len(retrain_data)} weight sets for retraining")
        return retrain_data
    
    async def shutdown(self):
        """Shutdown the constant loop extractor"""
        logger.info("Shutting down constant loop data extractor...")
        self.stop_constant_loop()
        await self.api_client.close()
        logger.info("Shutdown complete")

# Usage example
async def main():
    # Initialize constant loop extractor
    extractor = ConstantLoopDataExtractor(api_base_url="http://localhost:8000")
    
    # Initialize
    await extractor.initialize()
    
    # Start constant loop
    extractor.start_constant_loop()
    
    # Let it run for a while
    logger.info("Constant loop running, waiting 30 seconds...")
    await asyncio.sleep(30)
    
    # Get statistics
    stats = await extractor.get_system_stats()
    print("System Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get imprinted weights for retraining
    retrain_data = extractor.get_imprinted_weights_for_retrain()
    print(f"\nImprinted weights ready for retraining: {len(retrain_data)}")
    
    # Shutdown
    await extractor.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
