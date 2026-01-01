# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Mock VectorDatabase for Testing

This is a mock implementation of VectorDatabase for use in tests ONLY.
It provides the same interface but uses in-memory storage without requiring
ChromaDB or sentence-transformers.

WARNING: This mock does NOT provide semantic similarity search!
It should NEVER be used in production code.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class MockVectorEntry:
    """Mock VectorEntry for testing"""
    def __init__(self, entry_id: str, content: Any, embedding: Optional[List[float]] = None,
                 metadata: Optional[Dict[str, Any]] = None, entry_type: str = 'general'):
        self.entry_id = entry_id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.entry_type = entry_type


class MockVectorDatabase:
    """
    Mock VectorDatabase for Testing
    
    Provides the same interface as VectorDatabase but uses in-memory storage.
    Does NOT provide semantic similarity - just returns entries in order.
    
    Use this in tests by passing it as a fixture or dependency injection.
    """
    
    def __init__(self, persist_directory: str = "./test_vector_store",
                 collection_name: str = "test_collection"):
        """Initialize mock vector database"""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._storage: Dict[str, MockVectorEntry] = {}
        self.embedding_model = None
        
    def store(self, entry: MockVectorEntry) -> str:
        """Store entry in mock storage"""
        if entry.embedding is None:
            entry.embedding = self._generate_mock_embedding(entry.content)
        self._storage[entry.entry_id] = entry
        return entry.entry_id
    
    def retrieve(self, query_embedding: List[float],
                n_results: int = 5,
                metadata_filter: Optional[Dict[str, Any]] = None) -> List[MockVectorEntry]:
        """
        Mock retrieval - returns first n_results entries matching filter
        
        WARNING: Does NOT perform semantic similarity search!
        """
        results = []
        for entry in self._storage.values():
            if metadata_filter:
                if all(entry.metadata.get(k) == v for k, v in metadata_filter.items()):
                    results.append(entry)
            else:
                results.append(entry)
            if len(results) >= n_results:
                break
        return results
    
    def retrieve_by_content(self, content: Any,
                          n_results: int = 5,
                          metadata_filter: Optional[Dict[str, Any]] = None) -> List[MockVectorEntry]:
        """Mock retrieval by content"""
        embedding = self._generate_mock_embedding(content)
        return self.retrieve(embedding, n_results, metadata_filter)
    
    def get_by_id(self, entry_id: str) -> Optional[MockVectorEntry]:
        """Get entry by ID"""
        return self._storage.get(entry_id)
    
    def delete(self, entry_id: str) -> bool:
        """Delete entry"""
        if entry_id in self._storage:
            del self._storage[entry_id]
            return True
        return False
    
    def query_by_metadata(self, metadata_filter: Dict[str, Any],
                         limit: int = 100) -> List[MockVectorEntry]:
        """Query by metadata only"""
        results = []
        for entry in self._storage.values():
            if all(entry.metadata.get(k) == v for k, v in metadata_filter.items()):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get mock statistics"""
        return {
            'total_entries': len(self._storage),
            'mode': 'mock',
            'collection_name': self.collection_name,
            'warning': 'Mock mode - for testing only'
        }
    
    def _serialize_content(self, content: Any) -> str:
        """Serialize content to string"""
        if hasattr(content, 'serialize'):
            return json.dumps(content.serialize())
        return str(content)
    
    def _generate_mock_embedding(self, content: Any) -> List[float]:
        """Generate deterministic mock embedding from content hash"""
        content_str = self._serialize_content(content)
        hash_val = int(hashlib.sha256(content_str.encode()).hexdigest(), 16)
        embedding = []
        for i in range(384):
            embedding.append(((hash_val >> (i % 64)) & 0xFF) / 255.0)
        return embedding
    
    def __repr__(self) -> str:
        return f"MockVectorDatabase(entries={len(self._storage)}, mode=mock)"


def create_mock_vector_entry(entry_id: str, content: Any,
                             entry_type: str = 'general',
                             metadata: Optional[Dict[str, Any]] = None) -> MockVectorEntry:
    """Helper to create mock vector entry"""
    base_metadata = {
        'entry_type': entry_type,
        'timestamp': datetime.now().isoformat()
    }
    if metadata:
        base_metadata.update(metadata)
    
    return MockVectorEntry(
        entry_id=entry_id,
        content=content,
        entry_type=entry_type,
        metadata=base_metadata
    )
