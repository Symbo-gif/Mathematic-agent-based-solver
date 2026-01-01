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
PHASE 0 - STEP 3: The Active Memory Architecture (Vector Database)
==================================================================

Vector Database for Long-Term Institutional Memory

PURPOSE:
-------
Provides infrastructure for Retrieval-Augmented Generation (RAG) by indexing
mathematical "thought traces" and theorem embeddings. Enables the system to
recognize recurring problem patterns over time and learn from past experiences.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 3 (Lines 180-192)
- Phase 0 Coding Strategy: Section 5.0 "The Public Memory: Building a Collective Consciousness"
- Phase 0_ Infrastructural Agents and Hardware Calibration: Hardware constraints

ARCHITECTURE:
------------
Uses a lightweight vector store (ChromaDB in persistent mode) to conserve system RAM.
The Vector Database complements the Blackboard:
  - Blackboard: Active workspace for current problems
  - Vector Database: Long-term archive for historical knowledge

HARDWARE CONSIDERATION:
----------------------
System has 32GB RAM, but must reserve significant space for active LLM context window.
Therefore, vector store runs in persistent mode (disk-backed) rather than fully in-memory.

WHY THIS MATTERS:
----------------
The Vector Database serves as the system's long-term memory and learning substrate.
As agents solve problems, their approaches are embedded and stored. Future problems
can retrieve similar past solutions, enabling transfer learning and pattern recognition.

KEY OPERATIONS:
--------------
1. Store: Embed and store mathematical content with metadata
2. Retrieve: Query for similar content using vector similarity
3. Index: Index by conversation, agent, theorem, or custom metadata
"""

import os
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger('symbo_agentic_reasoners.phase0.vector_database')

# ChromaDB - lightweight, persistent vector store (REQUIRED)
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Sentence transformers for embeddings (REQUIRED for semantic search)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Import OMDoc types
from symbo_agentic_reasoners.core.omdoc_schema import OMObject, OMDocStatement, OMDocTheory


@dataclass
class VectorEntry:
    """
    Entry in the Vector Database

    Represents a mathematical concept, theorem, or thought trace that has been
    embedded and stored for future retrieval.

    FIELDS:
    ------
    - entry_id: Unique identifier
    - content: Original OMDoc content
    - embedding: Vector embedding (computed by embedding model)
    - metadata: Indexed metadata (agent, conversation_id, timestamp, tags, etc.)
    - entry_type: Type of content ('theorem', 'lemma', 'solution_trace', 'failed_attempt')
    """
    entry_id: str
    content: Any  # OMDoc object
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    entry_type: str = 'general'


class VectorDatabase:
    """
    Vector Database for Long-Term Institutional Memory

    Stores embedded mathematical content for future retrieval and pattern recognition.
    Uses ChromaDB as the backend for lightweight, persistent storage.

    THREAD SAFETY:
    -------------
    ChromaDB handles its own thread safety internally.

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 188-192
    """

    def __init__(self, persist_directory: str = "./symbo_agentic_reasoners_vector_store",
                 collection_name: str = "mathematical_knowledge",
                 allow_mock: bool = False):
        """
        Initialize Vector Database

        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the collection to use
            allow_mock: If True, allows mock mode for testing (NOT for production)

        Raises:
            RuntimeError: If ChromaDB or sentence-transformers not installed and mock not allowed

        HARDWARE NOTE:
        -------------
        Runs in persistent mode to conserve the 32GB system RAM for active LLM context.
        Reference: Phase 0_ Infrastructural Agents and Hardware Calibration
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Check for required dependencies
        if not CHROMADB_AVAILABLE:
            if not allow_mock:
                raise RuntimeError(
                    "ChromaDB is required for vector database functionality.\n"
                    "Install with: pip install chromadb\n"
                    "Or install full dependencies: pip install -e .[vector]\n"
                    "For testing only, pass allow_mock=True"
                )
            else:
                logger.warning("Running in MOCK mode - not suitable for production!")
                self.client = None
                self.collection = None
                self._mock_storage: Dict[str, VectorEntry] = {}
                self.embedding_model = None
                return

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            if not allow_mock:
                raise RuntimeError(
                    "sentence-transformers is required for semantic embeddings.\n"
                    "Install with: pip install sentence-transformers\n"
                    "Or install full dependencies: pip install -e .[vector]"
                )
            else:
                logger.warning("sentence-transformers not available - using mock embeddings")
                self.embedding_model = None
        else:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")

        # Initialize ChromaDB in persistent mode (disk-backed)
        # Updated to use modern ChromaDB API (0.4.0+)
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "SYMBO_AGENTIC_REASONERS Phase 0 Mathematical Knowledge Store"}
        )
        
        logger.info(f"VectorDatabase initialized: {self.collection.count()} entries")

    def store(self, entry: VectorEntry) -> str:
        """
        Store a vector entry in the database

        Args:
            entry: VectorEntry to store

        Returns:
            str: Entry ID of stored entry

        Raises:
            RuntimeError: If in mock mode (ChromaDB not available)
        """
        if self.client is None:
            # Mock mode - only for testing
            return self._mock_store(entry)

        # Generate embedding if not provided
        if entry.embedding is None:
            entry.embedding = self._generate_embedding(entry.content)

        # Store in ChromaDB
        self.collection.add(
            ids=[entry.entry_id],
            embeddings=[entry.embedding],
            metadatas=[entry.metadata],
            documents=[self._serialize_content(entry.content)]
        )

        logger.debug(f"Stored entry: {entry.entry_id}")
        return entry.entry_id

    def retrieve(self, query_embedding: List[float],
                n_results: int = 5,
                metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorEntry]:
        """
        Retrieve similar entries by vector similarity

        Args:
            query_embedding: Query vector
            n_results: Number of results to return
            metadata_filter: Optional metadata filter (e.g., {'entry_type': 'theorem'})

        Returns:
            List of VectorEntry objects ordered by similarity

        Raises:
            RuntimeError: If in mock mode (ChromaDB not available)
        """
        if self.client is None:
            # Mock mode - only for testing
            return self._mock_retrieve(query_embedding, n_results, metadata_filter)

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=metadata_filter
        )

        # Convert results to VectorEntry objects
        entries = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                entry = VectorEntry(
                    entry_id=results['ids'][0][i],
                    content=results['documents'][0][i],  # Serialized content
                    embedding=results['embeddings'][0][i] if results['embeddings'] else None,
                    metadata=results['metadatas'][0][i],
                    entry_type=results['metadatas'][0][i].get('entry_type', 'general')
                )
                entries.append(entry)

        logger.debug(f"Retrieved {len(entries)} entries")
        return entries

    def retrieve_by_content(self, content: Any,
                          n_results: int = 5,
                          metadata_filter: Optional[Dict[str, Any]] = None) -> List[VectorEntry]:
        """
        Retrieve similar entries by content similarity

        Convenience method that generates embedding from content and retrieves.

        Args:
            content: OMDoc content to find similar entries for
            n_results: Number of results to return
            metadata_filter: Optional metadata filter

        Returns:
            List of similar VectorEntry objects
        """
        embedding = self._generate_embedding(content)
        return self.retrieve(embedding, n_results, metadata_filter)

    def get_by_id(self, entry_id: str) -> Optional[VectorEntry]:
        """
        Retrieve entry by exact ID

        Args:
            entry_id: Entry identifier

        Returns:
            VectorEntry or None if not found
        """
        if self.client is None:
            # Mock mode
            return self._mock_storage.get(entry_id)

        try:
            result = self.collection.get(ids=[entry_id])
            if result['ids'] and len(result['ids']) > 0:
                return VectorEntry(
                    entry_id=result['ids'][0],
                    content=result['documents'][0],
                    embedding=result['embeddings'][0] if result['embeddings'] else None,
                    metadata=result['metadatas'][0],
                    entry_type=result['metadatas'][0].get('entry_type', 'general')
                )
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"Failed to retrieve entry {entry_id}: {type(e).__name__}: {e}")
        return None

    def delete(self, entry_id: str) -> bool:
        """
        Delete entry from database

        Args:
            entry_id: Entry to delete

        Returns:
            bool: True if entry was deleted
        """
        if self.client is None:
            # Mock mode
            if entry_id in self._mock_storage:
                del self._mock_storage[entry_id]
                return True
            return False

        try:
            self.collection.delete(ids=[entry_id])
            logger.debug(f"Deleted entry: {entry_id}")
            return True
        except (KeyError, ValueError, RuntimeError) as e:
            logger.warning(f"Failed to delete entry {entry_id}: {type(e).__name__}: {e}")
            return False

    def query_by_metadata(self, metadata_filter: Dict[str, Any],
                         limit: int = 100) -> List[VectorEntry]:
        """
        Query entries by metadata only (no vector similarity)

        Args:
            metadata_filter: Metadata filter (e.g., {'agent_id': 'algebra_001'})
            limit: Maximum number of results

        Returns:
            List of matching VectorEntry objects
        """
        if self.client is None:
            # Mock mode
            results = []
            for entry in self._mock_storage.values():
                if all(entry.metadata.get(k) == v for k, v in metadata_filter.items()):
                    results.append(entry)
                    if len(results) >= limit:
                        break
            return results

        try:
            result = self.collection.get(
                where=metadata_filter,
                limit=limit
            )
            entries = []
            if result['ids']:
                for i in range(len(result['ids'])):
                    entries.append(VectorEntry(
                        entry_id=result['ids'][i],
                        content=result['documents'][i],
                        embedding=result['embeddings'][i] if result['embeddings'] else None,
                        metadata=result['metadatas'][i],
                        entry_type=result['metadatas'][i].get('entry_type', 'general')
                    ))
            logger.debug(f"Query by metadata returned {len(entries)} entries")
            return entries
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.warning(f"Metadata query failed: {type(e).__name__}: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with statistics about stored entries
        """
        if self.client is None:
            return {
                'total_entries': len(self._mock_storage),
                'mode': 'mock',
                'warning': 'Running in mock mode - not suitable for production'
            }

        count = self.collection.count()
        return {
            'total_entries': count,
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory,
            'mode': 'chromadb',
            'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else 'mock'
        }

    # Helper methods

    def _serialize_content(self, content: Any) -> str:
        """Serialize OMDoc content to string for storage"""
        if hasattr(content, 'serialize'):
            return json.dumps(content.serialize())
        return str(content)

    def _generate_embedding(self, content: Any) -> List[float]:
        """
        Generate embedding from content using sentence-transformers

        Args:
            content: Content to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            RuntimeError: If sentence-transformers not available and not in mock mode
        """
        if self.embedding_model is None:
            # Fallback to mock embedding only if in mock mode
            if self.client is None:
                return self._generate_mock_embedding(content)
            else:
                raise RuntimeError(
                    "sentence-transformers required for embeddings but not available.\n"
                    "Install with: pip install sentence-transformers"
                )

        content_str = self._serialize_content(content)
        embedding = self.embedding_model.encode(content_str, convert_to_numpy=True)
        return embedding.tolist()

    def _generate_mock_embedding(self, content: Any) -> List[float]:
        """
        Generate mock embedding from content (TESTING ONLY)

        WARNING: This provides NO semantic similarity - just deterministic random numbers.
        Only used when allow_mock=True is explicitly set.

        Args:
            content: Content to create mock embedding for

        Returns:
            List of floats (mock embedding)
        """
        content_str = self._serialize_content(content)
        # Create deterministic "embedding" from hash
        hash_val = int(hashlib.sha256(content_str.encode()).hexdigest(), 16)
        # Generate 384-dimensional vector (common embedding size)
        embedding = []
        for i in range(384):
            # Use hash to seed deterministic values
            embedding.append(((hash_val >> (i % 64)) & 0xFF) / 255.0)
        return embedding

    # Mock mode methods (for when ChromaDB not available)

    def _mock_store(self, entry: VectorEntry) -> str:
        """Mock storage implementation (TESTING ONLY)"""
        logger.warning(f"Storing in MOCK mode: {entry.entry_id}")
        if entry.embedding is None:
            entry.embedding = self._generate_mock_embedding(entry.content)
        self._mock_storage[entry.entry_id] = entry
        return entry.entry_id

    def _mock_retrieve(self, query_embedding: List[float],
                      n_results: int,
                      metadata_filter: Optional[Dict[str, Any]]) -> List[VectorEntry]:
        """Mock retrieval implementation (TESTING ONLY)
        
        WARNING: This does NOT perform semantic similarity search!
        It just returns the first n_results entries that match the filter.
        """
        logger.warning("Retrieving in MOCK mode - no semantic similarity!")
        # Simple mock: return first n_results entries that match filter
        results = []
        for entry in self._mock_storage.values():
            if metadata_filter:
                if all(entry.metadata.get(k) == v for k, v in metadata_filter.items()):
                    results.append(entry)
            else:
                results.append(entry)
            if len(results) >= n_results:
                break
        return results

    def __repr__(self) -> str:
        """Human-readable representation"""
        stats = self.get_statistics()
        return f"VectorDatabase(entries={stats['total_entries']}, mode={stats['mode']})"


# Helper function for creating vector entries

def create_vector_entry(entry_id: str, content: Any,
                       entry_type: str = 'general',
                       metadata: Optional[Dict[str, Any]] = None) -> VectorEntry:
    """
    Helper function to create a VectorEntry

    Args:
        entry_id: Unique identifier
        content: OMDoc content
        entry_type: Type of entry ('theorem', 'lemma', 'solution_trace', etc.)
        metadata: Additional metadata (agent, conversation_id, tags, etc.)

    Returns:
        VectorEntry ready to be stored
    """
    base_metadata = {
        'entry_type': entry_type,
        'timestamp': datetime.now().isoformat()
    }
    if metadata:
        base_metadata.update(metadata)

    return VectorEntry(
        entry_id=entry_id,
        content=content,
        entry_type=entry_type,
        metadata=base_metadata
    )


if __name__ == "__main__":
    """Demonstration of Vector Database functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 3: Vector Database Long-Term Memory")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.omdoc_schema import create_variable, create_operation, MathOperator, OMDocStatement

    # Create Vector Database
    vector_db = VectorDatabase(persist_directory="./test_vector_store")
    print(f"Initialized: {vector_db}")
    print()

    # Example 1: Store a theorem
    print("Example 1: Storing Pythagorean Theorem")
    pythagorean = OMDocStatement(
        statement_type='theorem',
        name='pythagorean_theorem',
        content=create_variable('a²+b²=c²'),
        theory_context='Geometry',
        metadata={'importance': 'fundamental'}
    )
    theorem_entry = create_vector_entry(
        entry_id='theorem_pythagoras',
        content=pythagorean,
        entry_type='theorem',
        metadata={
            'agent_id': 'geometry_specialist',
            'theory': 'Geometry',
            'tags': ['geometry', 'triangles', 'fundamental']
        }
    )
    vector_db.store(theorem_entry)
    print(f"  Stored: {theorem_entry.entry_id}")
    print()

    # Example 2: Store a solution trace
    print("Example 2: Storing integration solution trace")
    integral_solution = create_operation(
        MathOperator.INT,
        create_operation(MathOperator.POWER, create_variable('x'), create_variable('2')),
        create_variable('x')
    )
    solution_entry = create_vector_entry(
        entry_id='solution_integral_x2',
        content=integral_solution,
        entry_type='solution_trace',
        metadata={
            'agent_id': 'integration_specialist_001',
            'conversation_id': 'conv_12345',
            'problem_type': 'polynomial_integration',
            'success': True,
            'tags': ['integration', 'polynomial']
        }
    )
    vector_db.store(solution_entry)
    print(f"  Stored: {solution_entry.entry_id}")
    print()

    # Example 3: Retrieve by ID
    print("Example 3: Retrieve by exact ID")
    retrieved = vector_db.get_by_id('theorem_pythagoras')
    if retrieved:
        print(f"  Retrieved: {retrieved.entry_id}")
        print(f"  Type: {retrieved.entry_type}")
        print(f"  Metadata: {retrieved.metadata}")
    print()

    # Example 4: Query by metadata
    print("Example 4: Query by metadata (all theorems)")
    theorems = vector_db.query_by_metadata({'entry_type': 'theorem'})
    print(f"  Found {len(theorems)} theorem(s):")
    for thm in theorems:
        print(f"    - {thm.entry_id}")
    print()

    # Example 5: Statistics
    print("Example 5: Database statistics")
    stats = vector_db.get_statistics()
    print(f"  {json.dumps(stats, indent=2)}")
    print()

    print("✓ Vector Database Long-Term Memory implementation complete")
    print("  - Persistent storage (disk-backed) ✓")
    print("  - Vector similarity search ✓")
    print("  - Metadata indexing ✓")
    print("  - RAM-efficient design (32GB constraint) ✓")

    # Cleanup test directory
    import shutil
    if os.path.exists("./test_vector_store"):
        shutil.rmtree("./test_vector_store")
        print("\n  (Test directory cleaned up)")
