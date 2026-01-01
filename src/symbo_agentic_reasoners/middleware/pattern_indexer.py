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
PHASE 3 - KM-2: PATTERN INDEXER (Tier 3)
========================================

Indexes solution patterns and provides similarity-based retrieval
for pattern matching in mathematical problem solving.

CAPABILITIES:
------------
- Index solution patterns by structure
- Similarity search using embeddings
- Pattern ranking and scoring
- LSH-based approximate nearest neighbor
- Fallback to linear search

ALGORITHMIC BACKING:
-------------------
- Hash-based pattern embeddings
- Cosine similarity for matching
- LSH for approximate search

REFERENCE:
---------
- Agent_System_Audit.docx.md: KM-2 Pattern Indexer
- Phase_3_Meta_Cognition.md: Knowledge Management Team
"""

import sys
import os
import logging
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Try to import numpy for embeddings
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

logger = logging.getLogger('symbo_agentic_reasoners.phase3.pattern_indexer')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class PatternType(Enum):
    """Types of mathematical patterns"""
    ALGEBRAIC = "algebraic"
    CALCULUS = "calculus"
    GEOMETRIC = "geometric"
    COMBINATORIAL = "combinatorial"
    PROOF = "proof"
    TRANSFORM = "transform"
    UNKNOWN = "unknown"


@dataclass
class SolutionPattern:
    """
    Represents an indexed solution pattern.
    
    Attributes:
        pattern_id: Unique identifier
        name: Human-readable name
        pattern_type: Category of pattern
        structure: Structural representation
        embedding: Vector embedding
        usage_count: Number of times used
        success_rate: Success rate when applied
        prerequisites: Required conditions
        examples: Example applications
    """
    pattern_id: str
    name: str
    pattern_type: PatternType
    structure: str
    embedding: Optional[Any] = None  # np.ndarray or List[float]
    usage_count: int = 0
    success_rate: float = 1.0
    prerequisites: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'type': self.pattern_type.value,
            'structure': self.structure[:100] + '...' if len(self.structure) > 100 else self.structure,
            'usage_count': self.usage_count,
            'success_rate': self.success_rate
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        }


@dataclass
class PatternMatch:
    """Result of pattern matching"""
    pattern: SolutionPattern
    similarity_score: float
    relevance_reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'pattern_id': self.pattern.pattern_id,
            'name': self.pattern.name,
            'similarity': self.similarity_score,
            'reason': self.relevance_reason
        }


class PatternIndexer(BDIAgent):
    """
    KM-2: Pattern Indexer
    
    DIRECTIVE:
    ---------
    Index and retrieve solution patterns for mathematical problem solving.
    Provides similarity-based search with LSH optimization.
    
    INPUTS:
    ------
    - Solution pattern data
    - Index search queries
    - Pattern structure specifications
    
    OUTPUTS:
    -------
    - Matching patterns
    - Similarity scoring results
    - Pattern rankings
    
    DEPENDENCIES:
    ------------
    - KM-1 (ContextExtractorAgent): For knowledge base access
    
    FAILURE MODE: DEGRADED - Fallback to linear search
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 404-413
    """
    
    # Embedding dimension
    EMBEDDING_DIM = 64
    
    # Number of LSH hash tables
    LSH_TABLES = 10
    
    def __init__(
        self,
        agent_id: str = 'pattern_indexer_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Pattern Indexer
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Pattern storage
        self.patterns: Dict[str, SolutionPattern] = {}
        
        # LSH index (hash table buckets)
        self.lsh_index: Dict[int, List[str]] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.patterns_indexed = 0
        self.searches_performed = 0
        self.lsh_hits = 0
        self.linear_fallbacks = 0
        
        # Initialize with common patterns
        self._initialize_common_patterns()
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Pattern Indexer initialized")
        print(f"  Embedding dim: {self.EMBEDDING_DIM}")
        print(f"  LSH tables: {self.LSH_TABLES}")
        print(f"  NumPy available: {HAS_NUMPY}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='meta.knowledge.pattern',
            agent_id=self.agent_id,
            algorithm='lsh_indexing',
            cost='medium',
            type='approximate',
            tier='3',
            algorithms='lsh_cosine_similarity'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: meta.knowledge.pattern")
    
    def _initialize_common_patterns(self):
        """Initialize with common mathematical patterns"""
        common_patterns = [
            ("quadratic_formula", "Quadratic Formula", PatternType.ALGEBRAIC,
             "x = (-b ± √(b²-4ac)) / 2a for ax² + bx + c = 0",
             ["polynomial equation", "degree 2"]),
            ("integration_by_parts", "Integration by Parts", PatternType.CALCULUS,
             "∫u dv = uv - ∫v du",
             ["product of functions", "integral"]),
            ("substitution", "U-Substitution", PatternType.CALCULUS,
             "∫f(g(x))g'(x)dx = ∫f(u)du where u = g(x)",
             ["composite function", "integral"]),
            ("chain_rule", "Chain Rule", PatternType.CALCULUS,
             "d/dx[f(g(x))] = f'(g(x)) · g'(x)",
             ["composite function", "derivative"]),
            ("factoring", "Factoring", PatternType.ALGEBRAIC,
             "Factor polynomial into irreducible factors",
             ["polynomial", "factorization"]),
            ("matrix_inverse", "Matrix Inversion", PatternType.ALGEBRAIC,
             "A⁻¹ exists iff det(A) ≠ 0; AA⁻¹ = I",
             ["square matrix", "invertible"]),
            ("eigendecomposition", "Eigendecomposition", PatternType.ALGEBRAIC,
             "A = PDP⁻¹ where D is diagonal of eigenvalues",
             ["diagonalizable matrix"]),
            ("proof_by_induction", "Mathematical Induction", PatternType.PROOF,
             "Base case + inductive step proves ∀n ∈ ℕ",
             ["natural numbers", "universal statement"]),
            ("proof_by_contradiction", "Proof by Contradiction", PatternType.PROOF,
             "Assume ¬P, derive contradiction, conclude P",
             ["logical proof"]),
            ("lhopital_rule", "L'Hôpital's Rule", PatternType.CALCULUS,
             "lim f/g = lim f'/g' for 0/0 or ∞/∞ forms",
             ["indeterminate form", "limit"]),
        ]
        
        for pid, name, ptype, structure, prereqs in common_patterns:
            pattern = SolutionPattern(
                pattern_id=pid,
                name=name,
                pattern_type=ptype,
                structure=structure,
                prerequisites=prereqs
            )
            self.index_pattern(pattern)
    
    def _compute_embedding(self, text: str) -> Any:
        """
        Compute embedding vector for text.
        
        Uses simple hash-based embedding for efficiency.
        """
        if HAS_NUMPY:
            # Hash-based embedding
            embedding = np.zeros(self.EMBEDDING_DIM)
            
            # Use word-level hashing
            words = text.lower().split()
            for i, word in enumerate(words):
                hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
                for j in range(self.EMBEDDING_DIM):
                    if (hash_val >> j) & 1:
                        embedding[j] += 1.0 / (i + 1)  # Position-weighted
                    else:
                        embedding[j] -= 1.0 / (i + 1)
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
        else:
            # Simple list-based embedding
            embedding = [0.0] * self.EMBEDDING_DIM
            words = text.lower().split()
            for i, word in enumerate(words):
                hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
                idx = hash_val % self.EMBEDDING_DIM
                embedding[idx] += 1.0 / (i + 1)
            return embedding
    
    def _compute_similarity(self, emb1: Any, emb2: Any) -> float:
        """Compute cosine similarity between embeddings"""
        if HAS_NUMPY:
            dot = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            if norm1 > 0 and norm2 > 0:
                return float(dot / (norm1 * norm2))
            return 0.0
        else:
            dot = sum(a * b for a, b in zip(emb1, emb2))
            norm1 = sum(a * a for a in emb1) ** 0.5
            norm2 = sum(b * b for b in emb2) ** 0.5
            if norm1 > 0 and norm2 > 0:
                return dot / (norm1 * norm2)
            return 0.0
    
    def _compute_lsh_hash(self, embedding: Any) -> int:
        """Compute LSH hash for embedding"""
        if HAS_NUMPY:
            # Random hyperplane LSH
            hash_val = 0
            for i in range(min(32, len(embedding))):
                if embedding[i] > 0:
                    hash_val |= (1 << i)
            return hash_val
        else:
            hash_val = 0
            for i in range(min(32, len(embedding))):
                if embedding[i] > 0:
                    hash_val |= (1 << i)
            return hash_val
    
    def index_pattern(self, pattern: SolutionPattern) -> str:
        """
        Index a solution pattern.
        
        Args:
            pattern: The pattern to index
            
        Returns:
            Pattern ID
        """
        self.tasks_executed += 1
        self.patterns_indexed += 1
        
        try:
            # Compute embedding
            text = f"{pattern.name} {pattern.structure} {' '.join(pattern.prerequisites)}"
            pattern.embedding = self._compute_embedding(text)
            
            # Store pattern
            self.patterns[pattern.pattern_id] = pattern
            
            # Add to LSH index
            lsh_hash = self._compute_lsh_hash(pattern.embedding)
            if lsh_hash not in self.lsh_index:
                self.lsh_index[lsh_hash] = []
            self.lsh_index[lsh_hash].append(pattern.pattern_id)
            
            self.tasks_succeeded += 1
            return pattern.pattern_id
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Pattern indexing failed: {type(e).__name__}: {e}")
            raise
    
    def search_patterns(
        self,
        query: str,
        top_k: int = 5,
        pattern_type: Optional[PatternType] = None,
        min_similarity: float = 0.1
    ) -> List[PatternMatch]:
        """
        Search for matching patterns.
        
        Args:
            query: Search query string
            top_k: Maximum number of results
            pattern_type: Optional type filter
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of PatternMatch results, sorted by similarity
        """
        self.tasks_executed += 1
        self.searches_performed += 1
        
        try:
            # Compute query embedding
            query_embedding = self._compute_embedding(query)
            
            # Try LSH first
            candidates = self._lsh_search(query_embedding)
            
            if not candidates:
                # Fallback to linear search
                self.linear_fallbacks += 1
                candidates = list(self.patterns.keys())
            else:
                self.lsh_hits += 1
            
            # Score candidates
            matches = []
            for pid in candidates:
                pattern = self.patterns.get(pid)
                if pattern is None:
                    continue
                
                # Apply type filter
                if pattern_type and pattern.pattern_type != pattern_type:
                    continue
                
                # Compute similarity
                similarity = self._compute_similarity(query_embedding, pattern.embedding)
                
                if similarity >= min_similarity:
                    reason = self._generate_relevance_reason(query, pattern)
                    matches.append(PatternMatch(
                        pattern=pattern,
                        similarity_score=similarity,
                        relevance_reason=reason
                    ))
            
            # Sort by similarity (descending)
            matches.sort(key=lambda m: m.similarity_score, reverse=True)
            
            self.tasks_succeeded += 1
            return matches[:top_k]
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Pattern search failed: {type(e).__name__}: {e}")
            return []
    
    def _lsh_search(self, query_embedding: Any) -> List[str]:
        """Search using LSH index"""
        query_hash = self._compute_lsh_hash(query_embedding)
        
        # Get exact matches
        candidates = set()
        if query_hash in self.lsh_index:
            candidates.update(self.lsh_index[query_hash])
        
        # Also check nearby hashes (1-bit differences)
        for i in range(min(8, 32)):
            near_hash = query_hash ^ (1 << i)
            if near_hash in self.lsh_index:
                candidates.update(self.lsh_index[near_hash])
        
        return list(candidates)
    
    def _generate_relevance_reason(self, query: str, pattern: SolutionPattern) -> str:
        """Generate explanation for why pattern matches query"""
        query_words = set(query.lower().split())
        pattern_words = set(pattern.structure.lower().split())
        pattern_words.update(w.lower() for w in pattern.prerequisites)
        
        common = query_words & pattern_words
        if common:
            return f"Matching terms: {', '.join(list(common)[:3])}"
        return f"Structural similarity to {pattern.name}"
    
    def update_pattern_stats(
        self,
        pattern_id: str,
        success: bool
    ):
        """Update pattern usage statistics"""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.usage_count += 1
            
            # Update success rate with exponential decay
            alpha = 0.1
            pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * (1.0 if success else 0.0)
    
    def get_pattern(self, pattern_id: str) -> Optional[SolutionPattern]:
        """Get pattern by ID"""
        return self.patterns.get(pattern_id)
    
    def list_patterns(
        self,
        pattern_type: Optional[PatternType] = None
    ) -> List[SolutionPattern]:
        """List all indexed patterns"""
        patterns = list(self.patterns.values())
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        return patterns
    
    def process(self, task_entry: Any) -> Any:
        """Process pattern indexing/search task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing pattern task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'search')
            
            if operation == 'index':
                pattern_data = metadata.get('pattern', {})
                pattern = SolutionPattern(
                    pattern_id=pattern_data.get('id', f'pattern_{len(self.patterns)}'),
                    name=pattern_data.get('name', 'Unknown'),
                    pattern_type=PatternType(pattern_data.get('type', 'unknown')),
                    structure=pattern_data.get('structure', ''),
                    prerequisites=pattern_data.get('prerequisites', [])
                )
                pid = self.index_pattern(pattern)
                result = {'pattern_id': pid, 'indexed': True}
                
            elif operation == 'search':
                query = metadata.get('query', '')
                top_k = metadata.get('top_k', 5)
                matches = self.search_patterns(query, top_k)
                result = {
                    'matches': [m.to_dict() for m in matches],
                    'count': len(matches)
                }
                
            elif operation == 'list':
                ptype = metadata.get('pattern_type')
                if ptype:
                    ptype = PatternType(ptype)
                patterns = self.list_patterns(ptype)
                result = {
                    'patterns': [p.to_dict() for p in patterns],
                    'count': len(patterns)
                }
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Pattern task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['pattern', 'knowledge'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'pattern'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for pattern tasks"""
        pass
    
    def deliberate(self):
        """Generate indexing plans"""
        return []
    
    def execute_step(self, intention: Intention):
        """Execute indexing step"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get indexer statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'patterns_indexed': self.patterns_indexed,
            'searches_performed': self.searches_performed,
            'lsh_hits': self.lsh_hits,
            'linear_fallbacks': self.linear_fallbacks,
            'lsh_hit_rate': (self.lsh_hits / self.searches_performed * 100)
                           if self.searches_performed > 0 else 0.0
        })
        return stats


if __name__ == "__main__":
    """Test Pattern Indexer"""
    print("=" * 80)
    print("PHASE 3 - PATTERN INDEXER TEST")
    print("=" * 80)
    print()
    
    # Initialize indexer
    indexer = PatternIndexer()
    print()
    
    # Test 1: List patterns
    print("Test 1: List Indexed Patterns")
    patterns = indexer.list_patterns()
    print(f"  Total patterns: {len(patterns)}")
    for p in patterns[:3]:
        print(f"    - {p.name} ({p.pattern_type.value})")
    print()
    
    # Test 2: Search for patterns
    print("Test 2: Search Patterns")
    query = "solve quadratic equation polynomial"
    matches = indexer.search_patterns(query, top_k=3)
    print(f"  Query: '{query}'")
    print(f"  Results: {len(matches)}")
    for m in matches:
        print(f"    - {m.pattern.name}: {m.similarity_score:.3f}")
    print()
    
    # Test 3: Search for calculus patterns
    print("Test 3: Search Calculus Patterns")
    query = "integrate product of functions"
    matches = indexer.search_patterns(query, pattern_type=PatternType.CALCULUS)
    print(f"  Query: '{query}'")
    for m in matches:
        print(f"    - {m.pattern.name}: {m.similarity_score:.3f}")
    print()
    
    # Test 4: Add custom pattern
    print("Test 4: Index Custom Pattern")
    custom = SolutionPattern(
        pattern_id="taylor_series",
        name="Taylor Series Expansion",
        pattern_type=PatternType.CALCULUS,
        structure="f(x) = Σ f^(n)(a)/n! (x-a)^n",
        prerequisites=["infinitely differentiable", "convergence"]
    )
    indexer.index_pattern(custom)
    print(f"  Indexed: {custom.name}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(indexer.get_statistics(), indent=2))
