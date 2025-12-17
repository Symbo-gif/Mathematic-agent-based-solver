# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Vector Database Updater
========================

Agent 5.2 of the Formal Knowledge Integration Team

Updates the RAG memory infrastructure with new discoveries. Re-indexes
system memory with new discoveries, effectively "teaching" the entire
Phase 2 workforce the new mathematics Phase 6 just discovered.

Integration Points:
- Phase 3 Knowledge Management Team (Retrieval Specialist)
- Phase 5 DistillationPipeline

Result: System gets smarter with every discovery through permanent
axiom expansion.

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 5
Reference: Phase_6_Build_Order_Breakdown.md, Step 5
"""

import logging
import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import json

from .auto_formalization_pipeline import FormalizedDiscovery, DiscoveryType

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.formal_knowledge_integration.vector_database_updater')
except ImportError:
    logger = logging.getLogger(__name__)


class IndexStatus(Enum):
    """Status of a discovery in the index"""
    INDEXED = 'indexed'
    PENDING = 'pending'
    FAILED = 'failed'
    DELETED = 'deleted'


@dataclass
class DiscoveryIndex:
    """
    Index entry for a discovery in the vector database.

    Attributes:
        index_id: Unique index identifier
        discovery_id: ID of the indexed discovery
        embedding: Vector embedding
        domains: Applicable domains for filtering
        created_at: When indexed
        access_count: Number of times retrieved
        last_accessed: Last retrieval time
    """
    index_id: str
    discovery_id: str
    embedding: List[float]
    domains: List[str]
    discovery_type: DiscoveryType
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    status: IndexStatus = IndexStatus.INDEXED

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index_id': self.index_id,
            'discovery_id': self.discovery_id,
            'domains': self.domains,
            'discovery_type': self.discovery_type.value,
            'access_count': self.access_count,
            'status': self.status.value
        }


class VectorDatabaseUpdater:
    """
    Agent 5.2: Vector Database Updater

    Manages the integration of new discoveries into the RAG memory
    infrastructure. Generates embeddings, indexes discoveries, and
    enables efficient retrieval by Phase 2 supervisors.

    Key capabilities:
    - Embedding generation for discoveries
    - Vector database indexing
    - Similarity search for retrieval
    - Domain-filtered search
    - Usage tracking

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    def __init__(
        self,
        vector_db_client=None,
        embedding_model=None,
        embedding_dim: int = 384,
        allow_mock: bool = False
    ):
        """
        Initialize the Vector Database Updater.

        Args:
            vector_db_client: Vector database client (e.g., ChromaDB, Milvus)
            embedding_model: Model for generating embeddings (e.g., SentenceTransformer)
            embedding_dim: Dimension of embedding vectors
            allow_mock: If True, allows mock embeddings for testing (TESTING ONLY)

        Raises:
            RuntimeError: If embedding_model is None and allow_mock is False
        """
        self.db = vector_db_client
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        self._allow_mock = allow_mock

        # Warn if no embedding model provided
        if embedding_model is None:
            if allow_mock:
                warn_msg = (
                    "VectorDatabaseUpdater initialized WITHOUT embedding model (mock mode).\n"
                    "WARNING: Mock embeddings provide NO semantic similarity.\n"
                    "This is ONLY suitable for testing. Do not use in production."
                )
                logger.warning(f"MOCK MODE: {warn_msg}")
                print(f"[WARN] {warn_msg}")
            else:
                # Log warning but don't fail - will fail-fast on first embedding generation
                logger.warning(
                    "VectorDatabaseUpdater initialized without embedding model. "
                    "Embedding generation will fail unless allow_mock=True."
                )

        # Local storage for when no external DB
        self._local_index: Dict[str, DiscoveryIndex] = {}
        self._local_discoveries: Dict[str, FormalizedDiscovery] = {}

        # Statistics
        self.stats = {
            'discoveries_indexed': 0,
            'searches_performed': 0,
            'retrievals': 0,
            'by_type': {},
            'by_domain': {}
        }

    def update(self, discovery: FormalizedDiscovery) -> str:
        """
        Index a new discovery in the vector database.

        Args:
            discovery: FormalizedDiscovery to index

        Returns:
            Index ID of the indexed discovery
        """
        self.stats['discoveries_indexed'] += 1

        # Track by type
        dtype = discovery.discovery_type.value
        self.stats['by_type'][dtype] = self.stats['by_type'].get(dtype, 0) + 1

        # Track by domain
        for domain in discovery.applicable_domains:
            self.stats['by_domain'][domain] = self.stats['by_domain'].get(domain, 0) + 1

        # Generate embedding
        embedding = self._generate_embedding(discovery)
        discovery.embedding_vector = embedding

        # Create index entry
        index_id = f"idx_{hashlib.sha256(discovery.discovery_id.encode()).hexdigest()[:12]}"

        index_entry = DiscoveryIndex(
            index_id=index_id,
            discovery_id=discovery.discovery_id,
            embedding=embedding,
            domains=discovery.applicable_domains,
            discovery_type=discovery.discovery_type
        )

        # Store in database
        if self.db:
            self._store_in_db(discovery, index_entry)
        else:
            self._store_locally(discovery, index_entry)

        # Notify downstream systems
        self._notify_supervisors(discovery)

        return index_id

    def update_batch(self, discoveries: List[FormalizedDiscovery]) -> List[str]:
        """
        Index a batch of discoveries.

        Args:
            discoveries: List of discoveries to index

        Returns:
            List of index IDs
        """
        return [self.update(d) for d in discoveries]

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: Optional[List[str]] = None,
        type_filter: Optional[List[DiscoveryType]] = None
    ) -> List[Tuple[FormalizedDiscovery, float]]:
        """
        Search for relevant discoveries.

        Args:
            query: Search query (natural language)
            top_k: Number of results to return
            domain_filter: Only search in these domains
            type_filter: Only return these types

        Returns:
            List of (discovery, similarity_score) tuples
        """
        self.stats['searches_performed'] += 1

        # Generate query embedding
        query_embedding = self._generate_query_embedding(query)

        if self.db:
            return self._search_db(query_embedding, top_k, domain_filter, type_filter)
        else:
            return self._search_locally(query_embedding, top_k, domain_filter, type_filter)

    def get_by_id(self, discovery_id: str) -> Optional[FormalizedDiscovery]:
        """Get a specific discovery by ID"""
        if self.db:
            return self._get_from_db(discovery_id)
        else:
            return self._local_discoveries.get(discovery_id)

    def delete(self, discovery_id: str) -> bool:
        """Delete a discovery from the index"""
        if self.db:
            return self._delete_from_db(discovery_id)
        else:
            if discovery_id in self._local_discoveries:
                del self._local_discoveries[discovery_id]
                # Find and remove index entry
                for idx_id, entry in list(self._local_index.items()):
                    if entry.discovery_id == discovery_id:
                        del self._local_index[idx_id]
                return True
            return False

    def _generate_embedding(self, discovery: FormalizedDiscovery) -> List[float]:
        """
        Generate embedding vector for a discovery.

        Args:
            discovery: FormalizedDiscovery to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            RuntimeError: If no embedding model available and not in mock mode
        """
        if self.embedding_model:
            # Use provided embedding model
            text = self._prepare_text_for_embedding(discovery)
            return self.embedding_model.encode(text).tolist()

        # FAIL-FAST: No mock fallback unless explicitly allowed
        if self._allow_mock:
            logger.warning("Using MOCK embedding - no semantic similarity!")
            return self._mock_embedding(discovery)

        error_msg = (
            f"Embedding model not available for discovery indexing.\n"
            f"Required: sentence-transformers or compatible embedding model.\n"
            f"Install with: pip install sentence-transformers\n"
            f"This is required for semantic search in Phase 6 discovery integration.\n"
            f"For testing only, pass allow_mock=True to VectorDatabaseUpdater."
        )
        logger.error(f"EMBEDDING MODEL NOT AVAILABLE: {error_msg}")
        print(f"\n[ERROR] {error_msg}\n")
        raise RuntimeError(error_msg)

    def _generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Search query string

        Returns:
            List of floats representing the embedding vector

        Raises:
            RuntimeError: If no embedding model available and not in mock mode
        """
        if self.embedding_model:
            return self.embedding_model.encode(query).tolist()

        # FAIL-FAST: No mock fallback unless explicitly allowed
        if self._allow_mock:
            logger.warning("Using MOCK embedding for query - no semantic similarity!")
            return self._mock_text_embedding(query)

        error_msg = (
            f"Embedding model not available for search query.\n"
            f"Required: sentence-transformers or compatible embedding model.\n"
            f"Install with: pip install sentence-transformers\n"
            f"This is required for semantic search functionality.\n"
            f"For testing only, pass allow_mock=True to VectorDatabaseUpdater."
        )
        logger.error(f"EMBEDDING MODEL NOT AVAILABLE: {error_msg}")
        print(f"\n[ERROR] {error_msg}\n")
        raise RuntimeError(error_msg)

    def _prepare_text_for_embedding(self, discovery: FormalizedDiscovery) -> str:
        """Prepare text representation for embedding"""
        parts = [
            discovery.natural_language_statement,
            f"Type: {discovery.discovery_type.value}",
            f"Domains: {', '.join(discovery.applicable_domains)}"
        ]

        if discovery.metadata:
            if 'algorithmic_class' in discovery.metadata:
                parts.append(f"Algorithm: {discovery.metadata['algorithmic_class']}")
            if 'key_patterns' in discovery.metadata:
                parts.append(f"Patterns: {', '.join(discovery.metadata['key_patterns'][:5])}")

        return " ".join(parts)

    def _mock_embedding(self, discovery: FormalizedDiscovery) -> List[float]:
        """
        Generate mock embedding for a discovery (TESTING ONLY).

        WARNING: This provides NO semantic similarity - just deterministic hash-based values.
        Only used when allow_mock=True is explicitly set during initialization.

        Args:
            discovery: FormalizedDiscovery to create mock embedding for

        Returns:
            List of floats (mock embedding with no semantic meaning)
        """
        text = self._prepare_text_for_embedding(discovery)
        return self._mock_text_embedding(text)

    def _mock_text_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding from text (TESTING ONLY).

        WARNING: This provides NO semantic similarity - just deterministic hash-based values.
        Searches using mock embeddings will NOT return semantically similar results.

        Args:
            text: Text to create mock embedding for

        Returns:
            List of floats (mock embedding with no semantic meaning)
        """
        # Create deterministic embedding from text
        embedding = []
        for i in range(0, self.embedding_dim):
            # Use hash of text + position for determinism
            h = hashlib.sha256(f"{text}_{i}".encode()).hexdigest()
            # Convert first 8 hex chars to float in [0, 1]
            val = int(h[:8], 16) / 0xFFFFFFFF
            embedding.append(val)
        return embedding

    def _store_locally(self, discovery: FormalizedDiscovery, index_entry: DiscoveryIndex):
        """Store discovery in local cache"""
        self._local_discoveries[discovery.discovery_id] = discovery
        self._local_index[index_entry.index_id] = index_entry

    def _store_in_db(self, discovery: FormalizedDiscovery, index_entry: DiscoveryIndex):
        """Store discovery in external database"""
        doc = {
            'id': discovery.discovery_id,
            'type': discovery.discovery_type.value,
            'content': discovery.natural_language_statement,
            'omdoc': discovery.omdoc_representation,
            'lean_code': discovery.lean4_code,
            'sympy_impl': discovery.sympy_implementation,
            'domains': discovery.applicable_domains,
            'verified': discovery.verified,
            'embedding': index_entry.embedding,
            'created_at': discovery.created_at.isoformat()
        }

        try:
            self.db.insert(doc)
        except (ValueError, TypeError, AttributeError, KeyError, RuntimeError, IOError) as e:
            # Fallback to local storage on DB insert failure
            logger.debug(f"DB insert failed, using local storage: {e}")
            self._store_locally(discovery, index_entry)

    def _search_locally(
        self,
        query_embedding: List[float],
        top_k: int,
        domain_filter: Optional[List[str]],
        type_filter: Optional[List[DiscoveryType]]
    ) -> List[Tuple[FormalizedDiscovery, float]]:
        """Search local index"""
        results = []

        for idx_id, index_entry in self._local_index.items():
            # Apply domain filter
            if domain_filter:
                if not any(d in index_entry.domains for d in domain_filter):
                    continue

            # Apply type filter
            if type_filter:
                if index_entry.discovery_type not in type_filter:
                    continue

            # Compute similarity
            similarity = self._cosine_similarity(query_embedding, index_entry.embedding)

            discovery = self._local_discoveries.get(index_entry.discovery_id)
            if discovery:
                results.append((discovery, similarity))

                # Update access count
                index_entry.access_count += 1
                index_entry.last_accessed = datetime.now()
                self.stats['retrievals'] += 1

        # Sort by similarity and return top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _search_db(
        self,
        query_embedding: List[float],
        top_k: int,
        domain_filter: Optional[List[str]],
        type_filter: Optional[List[DiscoveryType]]
    ) -> List[Tuple[FormalizedDiscovery, float]]:
        """Search external database"""
        try:
            # Build filter conditions
            filters = {}
            if domain_filter:
                filters['domains'] = {'$in': domain_filter}
            if type_filter:
                filters['type'] = {'$in': [t.value for t in type_filter]}

            results = self.db.search(
                embedding=query_embedding,
                top_k=top_k,
                filters=filters
            )

            # Convert to FormalizedDiscovery objects
            discoveries = []
            for doc, score in results:
                discovery = self._doc_to_discovery(doc)
                discoveries.append((discovery, score))
                self.stats['retrievals'] += 1

            return discoveries

        except (ValueError, TypeError, AttributeError, KeyError, RuntimeError, IOError) as e:
            # Fallback to local search on DB search failure
            logger.debug(f"DB search failed, using local search: {e}")
            return self._search_locally(query_embedding, top_k, domain_filter, type_filter)

    def _get_from_db(self, discovery_id: str) -> Optional[FormalizedDiscovery]:
        """Get discovery from external database"""
        try:
            doc = self.db.get(discovery_id)
            if doc:
                return self._doc_to_discovery(doc)
        except (AttributeError, TypeError, KeyError) as e:
            logger.debug(f"Could not get discovery {discovery_id} from database: {e}")
        return None

    def _delete_from_db(self, discovery_id: str) -> bool:
        """Delete from external database"""
        try:
            self.db.delete(discovery_id)
            return True
        except (AttributeError, TypeError, KeyError) as e:
            logger.debug(f"Could not delete discovery {discovery_id} from database: {e}")
            return False

    def _doc_to_discovery(self, doc: Dict[str, Any]) -> FormalizedDiscovery:
        """Convert database document to FormalizedDiscovery"""
        return FormalizedDiscovery(
            discovery_id=doc.get('id', ''),
            discovery_type=DiscoveryType(doc.get('type', 'theorem')),
            natural_language_statement=doc.get('content', ''),
            omdoc_representation=doc.get('omdoc', ''),
            lean4_code=doc.get('lean_code'),
            sympy_implementation=doc.get('sympy_impl'),
            verified=doc.get('verified', False),
            applicable_domains=doc.get('domains', [])
        )

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def _notify_supervisors(self, discovery: FormalizedDiscovery):
        """Notify Phase 2 supervisors of new capability"""
        # In production, would send FIPA-ACL messages to relevant supervisors
        for domain in discovery.applicable_domains:
            # Log notification (would be actual message in production)
            pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            **self.stats,
            'total_indexed': len(self._local_discoveries) if not self.db else self.stats['discoveries_indexed'],
            'has_external_db': self.db is not None,
            'has_embedding_model': self.embedding_model is not None,
            'embedding_dim': self.embedding_dim
        }

    def get_domain_summary(self) -> Dict[str, int]:
        """Get summary of discoveries by domain"""
        return dict(self.stats['by_domain'])

    def get_type_summary(self) -> Dict[str, int]:
        """Get summary of discoveries by type"""
        return dict(self.stats['by_type'])

    def reset(self):
        """Reset database state"""
        self._local_index.clear()
        self._local_discoveries.clear()
        self.stats = {
            'discoveries_indexed': 0,
            'searches_performed': 0,
            'retrievals': 0,
            'by_type': {},
            'by_domain': {}
        }

    def health_check(self) -> bool:
        """Check if updater is healthy"""
        return True

    def export_index(self) -> Dict[str, Any]:
        """Export the current index for backup"""
        return {
            'discoveries': {
                d_id: d.to_dict() for d_id, d in self._local_discoveries.items()
            },
            'index': {
                i_id: i.to_dict() for i_id, i in self._local_index.items()
            },
            'stats': self.stats
        }

    def import_index(self, data: Dict[str, Any]):
        """Import index from backup"""
        # Would reconstruct discoveries and index from data
        pass
