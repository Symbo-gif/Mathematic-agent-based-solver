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
KNOWLEDGE MANAGEMENT TEAM - "The Librarians"
=============================================

Phase 3: Meta-Cognitive Middleware - Memory Gap Resolution

PURPOSE:
-------
Construct the knowledge infrastructure that transforms the system from
stateless isolation to collective consciousness. This team manages the
flow of information between the active Blackboard (short-term memory)
and the Vector Database (long-term memory), implementing Retrieval-Augmented
Generation (RAG) to short-circuit solving when known theorems exist.

WHY THIS MATTERS:
----------------
Without shared memory, the system suffers from the "Tower of Babel" problem:
Agent A solves a lemma that Agent B needs but cannot see. The system wastes
resources re-solving known theorems. Research indicates that RAG integration
improves accuracy by ~15-20% while dramatically reducing computation time for
problems with known solutions.

AGENTS:
------
1. Context Extractor - Information filter (signal from noise)
2. Memory Indexer - Vector DB archivist (long-term storage)
3. Retrieval Specialist - RAG integration (external lookups)

REFERENCE:
---------
- Phase_3_Build_Order_Breakdown.md: Step 2
- Phase_3_installs_the_cognitive_immune_system.md: Actions 2.1-2.3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum, auto
import hashlib
import json
import logging
from datetime import datetime
import numpy as np

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase3.knowledge.knowledge_management')
except ImportError:
    logger = logging.getLogger(__name__)


# ===========================================================================
# RETRIEVAL RESULT TYPES
# ===========================================================================

class RetrievalConfidence(Enum):
    """Confidence levels for retrieved knowledge"""
    EXACT_MATCH = auto()      # Identical theorem found
    HIGH_SIMILARITY = auto()  # Very similar, likely applicable
    MODERATE = auto()         # Related, may be useful
    LOW = auto()              # Loosely related
    NO_MATCH = auto()         # Nothing relevant found


@dataclass
class RetrievalResult:
    """
    Result from knowledge retrieval

    Used to determine whether solving can be skipped (for EXACT_MATCH
    or HIGH_SIMILARITY) or if the retrieved information should be
    used as context for solving.
    """
    confidence: RetrievalConfidence
    theorem_id: Optional[str] = None
    theorem_content: Optional[str] = None
    proof_sketch: Optional[str] = None
    source: str = "internal"  # 'internal', 'mathlib', 'loogle'
    similarity_score: float = 0.0

    def should_skip_solving(self) -> bool:
        """Determine if retrieval is good enough to skip solving"""
        return self.confidence in [
            RetrievalConfidence.EXACT_MATCH,
            RetrievalConfidence.HIGH_SIMILARITY
        ]

    def __repr__(self) -> str:
        return f"RetrievalResult({self.confidence.name}, score={self.similarity_score:.2f})"


@dataclass
class ContextPacket:
    """
    Filtered context for a sub-task

    Contains only the information relevant to the current sub-task,
    preventing token bloat and solver distraction.
    """
    relevant_variables: Dict[str, Any]
    active_constraints: Dict[str, Any]
    prior_results: List[Dict[str, Any]]
    problem_summary: str
    token_count: int

    def __repr__(self) -> str:
        return f"ContextPacket(vars={len(self.relevant_variables)}, tokens={self.token_count})"


@dataclass
class MemoryEntry:
    """
    Entry in the long-term memory (Vector Database)

    Represents a stored mathematical result that can be retrieved
    for future problems.
    """
    entry_id: str
    timestamp: datetime
    problem_signature: str
    result: Any
    proof_trace: Optional[str]
    embedding: Optional[np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ===========================================================================
# AGENT 2.1: THE CONTEXT EXTRACTOR
# ===========================================================================

class ContextExtractorAgent:
    """
    Agent 2.1: The Context Extractor - Information Filter

    Sits between the User/Orchestrator and the Blackboard.
    Filters signal from noise to ensure solvers operate on clean,
    token-efficient context.

    WHAT IT DOES:
    - Parses full problem history from Blackboard
    - Extracts only relevant variables, constraints, and results
    - Generates concise problem summaries
    - Manages token budget to prevent context overflow

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 2.1
    """

    def __init__(self, blackboard, max_context_tokens: int = 2048):
        """
        Initialize with Blackboard reference and token budget.

        Args:
            blackboard: Phase 0 Blackboard instance
            max_context_tokens: Maximum tokens to include in context
        """
        self.blackboard = blackboard
        self.max_context_tokens = max_context_tokens
        self.extractions_performed = 0
        print("    [OK] Context Extractor Agent initialized")

    def extract_context(self, conversation_id: str,
                       target_variables: Set[str],
                       problem_type: str) -> ContextPacket:
        """
        Extract relevant context for a sub-task.

        Filters the full problem history to return only information
        that directly impacts the current sub-task.
        """
        self.extractions_performed += 1

        # Retrieve all entries for this conversation
        all_entries = self._get_entries(conversation_id)

        # Filter for relevance
        relevant_entries = self._filter_relevant(
            all_entries, target_variables, problem_type
        )

        # Extract structured information
        variables = self._extract_variable_values(relevant_entries)
        constraints = self._extract_constraints(relevant_entries)
        prior_results = self._extract_prior_results(relevant_entries)

        # Compute problem summary
        summary = self._generate_summary(relevant_entries)

        # Estimate token count
        token_count = self._estimate_tokens(variables, constraints,
                                           prior_results, summary)

        # Truncate if exceeds budget
        if token_count > self.max_context_tokens:
            prior_results = self._truncate_to_budget(
                prior_results,
                self.max_context_tokens - self._estimate_tokens(
                    variables, constraints, [], summary
                )
            )
            token_count = self.max_context_tokens

        return ContextPacket(
            relevant_variables=variables,
            active_constraints=constraints,
            prior_results=prior_results,
            problem_summary=summary,
            token_count=token_count
        )

    def _get_entries(self, conversation_id: str) -> List[Dict]:
        """Get entries from Blackboard for a conversation"""
        try:
            if hasattr(self.blackboard, 'get_entries'):
                return self.blackboard.get_entries(conversation_id)
            elif hasattr(self.blackboard, 'get_by_conversation'):
                entries = self.blackboard.get_by_conversation(conversation_id)
                return [self._entry_to_dict(e) for e in entries]
            else:
                return []
        except (AttributeError, TypeError, KeyError) as e:
            logger.debug(f"Could not get blackboard entries for {conversation_id}: {e}")
            return []

    def _entry_to_dict(self, entry) -> Dict:
        """Convert Blackboard entry to dictionary"""
        if isinstance(entry, dict):
            return entry
        return {
            'entry_id': getattr(entry, 'entry_id', ''),
            'entry_type': str(getattr(entry, 'entry_type', '')),
            'content': getattr(entry, 'content', None),
            'status': str(getattr(entry, 'status', '')),
            'tags': getattr(entry, 'tags', []),
            'metadata': getattr(entry, 'metadata', {}),
            'variables': list(getattr(entry, 'variables', [])),
        }

    def _filter_relevant(self, entries: List[Dict],
                        target_variables: Set[str],
                        problem_type: str) -> List[Dict]:
        """Filter entries for relevance to current sub-task"""
        relevant = []

        for entry in entries:
            # Check if entry mentions target variables
            entry_vars = set(entry.get('variables', []))
            if entry_vars.intersection(target_variables):
                relevant.append(entry)
                continue

            # Check if entry is a constraint
            if entry.get('entry_type') == 'constraint_propagation':
                relevant.append(entry)
                continue

            # Check if entry is a confirmed result
            if entry.get('status') == 'VERIFIED':
                relevant.append(entry)

        return relevant

    def _extract_variable_values(self, entries: List[Dict]) -> Dict[str, Any]:
        """Extract known variable values from entries"""
        values = {}
        for entry in entries:
            if 'variable_values' in entry:
                values.update(entry['variable_values'])
            # Also check metadata
            metadata = entry.get('metadata', {})
            if isinstance(metadata, dict) and 'variable_values' in metadata:
                values.update(metadata['variable_values'])
        return values

    def _extract_constraints(self, entries: List[Dict]) -> Dict[str, Any]:
        """Extract active constraints"""
        constraints = {}
        for entry in entries:
            if entry.get('entry_type') == 'constraint_propagation':
                constraint = entry.get('constraint')
                if constraint:
                    var = getattr(constraint, 'variable', None) or constraint.get('variable')
                    if var:
                        constraints[var] = constraint
        return constraints

    def _extract_prior_results(self, entries: List[Dict]) -> List[Dict]:
        """Extract verified prior results"""
        results = []
        for entry in entries:
            if entry.get('status') == 'VERIFIED':
                results.append({
                    'expression': entry.get('content'),
                    'result': entry.get('result'),
                    'method': entry.get('method')
                })
        return results

    def _generate_summary(self, entries: List[Dict]) -> str:
        """Generate concise problem summary"""
        problem_types = set()
        operations = []

        for entry in entries:
            if 'problem_type' in entry:
                problem_types.add(entry['problem_type'])
            if 'operation' in entry:
                operations.append(entry['operation'])

        if problem_types or operations:
            return f"Problem types: {problem_types}. Operations: {operations[:5]}"
        return "No prior context available."

    def _estimate_tokens(self, variables, constraints,
                        results, summary) -> int:
        """Rough token count estimation (~4 chars per token)"""
        total_chars = (
            len(json.dumps(variables, default=str)) +
            len(json.dumps({str(k): str(v) for k, v in constraints.items()})) +
            len(json.dumps(results, default=str)) +
            len(summary)
        )
        return total_chars // 4

    def _truncate_to_budget(self, results: List[Dict],
                           budget: int) -> List[Dict]:
        """Truncate results to fit token budget (keep most recent)"""
        truncated = []
        current_tokens = 0

        for result in reversed(results):
            result_tokens = len(json.dumps(result, default=str)) // 4
            if current_tokens + result_tokens <= budget:
                truncated.insert(0, result)
                current_tokens += result_tokens
            else:
                break

        return truncated

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'extractions_performed': self.extractions_performed,
            'max_context_tokens': self.max_context_tokens
        }


# ===========================================================================
# AGENT 2.2: THE MEMORY INDEXER
# ===========================================================================

class MemoryIndexerAgent:
    """
    Agent 2.2: The Memory Indexer - Vector Database Archivist

    Responsible for writing confirmed results to the Vector Database.
    Transforms the Blackboard from temporary scratchpad to persistent
    long-term memory.

    WHAT IT DOES:
    - Generates unique IDs and signatures for problems
    - Computes embeddings for semantic search
    - Stores results in Vector Database
    - Creates persistent records for future retrieval

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 2.2
    """

    def __init__(self, vector_db, embedding_model=None):
        """
        Initialize with Vector Database and embedding model.

        Args:
            vector_db: Phase 0 Vector Database instance
            embedding_model: Model for generating mathematical embeddings
                           (optional, uses hash-based fallback if None)
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.index_count = 0
        print("    [OK] Memory Indexer Agent initialized")

    def index_result(self, conversation_id: str,
                    problem_statement: str,
                    result: Any,
                    proof_trace: Optional[str] = None,
                    metadata: Dict[str, Any] = None) -> str:
        """
        Index a confirmed result in the Vector Database.

        Called when a Supervisor confirms a result.
        Creates a permanent record for future retrieval.

        Returns:
            entry_id: Unique ID of the stored entry
        """
        # Generate unique ID
        entry_id = self._generate_entry_id(conversation_id, problem_statement)

        # Generate problem signature for matching
        signature = self._compute_problem_signature(problem_statement)

        # Generate embedding for semantic search
        embedding = self._generate_embedding(problem_statement, result)

        # Create memory entry
        entry = MemoryEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            problem_signature=signature,
            result=result,
            proof_trace=proof_trace,
            embedding=embedding,
            metadata=metadata or {}
        )

        # Store in Vector Database
        self._store_entry(entry)

        self.index_count += 1
        return entry_id

    def _generate_entry_id(self, conversation_id: str,
                          problem_statement: str) -> str:
        """Generate unique ID for memory entry"""
        content = f"{conversation_id}:{problem_statement}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _compute_problem_signature(self, problem_statement: str) -> str:
        """
        Compute canonical signature for problem matching.

        Normalizes the problem to enable matching of equivalent
        formulations (e.g., "integrate x^2" vs "find integral of x squared").
        """
        # Simple normalization - in production, use OMDoc canonicalization
        normalized = problem_statement.lower()
        normalized = normalized.replace(" ", "")
        # Remove common variations
        for old, new in [("integrate", "int"), ("differentiate", "diff"),
                        ("derivative", "diff"), ("integral", "int")]:
            normalized = normalized.replace(old, new)
        return hashlib.md5(normalized.encode()).hexdigest()

    def _generate_embedding(self, problem: str, result: Any) -> np.ndarray:
        """
        Generate vector embedding for semantic search.

        Combines problem statement and result for comprehensive embedding.
        """
        combined = f"{problem} => {result}"

        # Use embedding model if available
        if self.embedding_model and hasattr(self.embedding_model, 'encode'):
            try:
                return self.embedding_model.encode(combined)
            except (RuntimeError, TypeError, ValueError) as e:
                logger.debug(f"Could not generate embedding with model: {e}")

        # Fallback: simple hash-based pseudo-embedding
        hash_val = int(hashlib.md5(combined.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        return np.random.randn(256).astype(np.float32)

    def _store_entry(self, entry: MemoryEntry) -> None:
        """Store entry in Vector Database"""
        try:
            if hasattr(self.vector_db, 'store'):
                # Use Phase 0 VectorDatabase interface
                from symbo_agentic_reasoners.core.vector_database import VectorEntry
                vector_entry = VectorEntry(
                    entry_id=entry.entry_id,
                    content=entry.result,
                    embedding=entry.embedding.tolist() if entry.embedding is not None else None,
                    metadata={
                        'signature': entry.problem_signature,
                        'proof_trace': entry.proof_trace,
                        'timestamp': entry.timestamp.isoformat(),
                        **entry.metadata
                    },
                    entry_type='mathematical_result'
                )
                self.vector_db.store(vector_entry)
            elif hasattr(self.vector_db, 'insert'):
                # Alternative interface
                self.vector_db.insert({
                    'id': entry.entry_id,
                    'embedding': entry.embedding.tolist() if entry.embedding is not None else [],
                    'signature': entry.problem_signature,
                    'result': str(entry.result),
                    'proof_trace': entry.proof_trace,
                    'timestamp': entry.timestamp.isoformat(),
                    'metadata': entry.metadata
                })
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            # Log but don't fail - indexing is best-effort (data/type errors)
            logger.warning(f"Memory indexing failed (data error): {e}")
        except (RuntimeError, IOError, OSError) as e:
            # Log but don't fail - indexing is best-effort (system/IO errors)
            logger.warning(f"Memory indexing failed (system error): {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'entries_indexed': self.index_count,
            'has_embedding_model': self.embedding_model is not None
        }


# ===========================================================================
# AGENT 2.3: THE RETRIEVAL SPECIALIST (RAG INTEGRATION)
# ===========================================================================

class RetrievalSpecialistAgent:
    """
    Agent 2.3: The Retrieval Specialist - RAG Integration

    External liaison responsible for querying mathematical repositories.
    Implements "Look-Before-You-Leap" pattern to short-circuit solving.

    WHAT IT DOES:
    - Queries internal Vector Database for similar problems
    - Checks for exact signature matches
    - Queries external sources (Mathlib, Loogle) if available
    - Returns confidence-scored results

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 2.3
    """

    # Similarity thresholds for confidence classification
    EXACT_THRESHOLD = 0.98
    HIGH_THRESHOLD = 0.85
    MODERATE_THRESHOLD = 0.70
    LOW_THRESHOLD = 0.50

    def __init__(self, vector_db, embedding_model=None,
                 external_sources: List[str] = None):
        """
        Initialize with Vector Database and external source connections.

        Args:
            vector_db: Phase 0 Vector Database for internal lookups
            embedding_model: Model for query embedding
            external_sources: List of external libraries (e.g., ['mathlib', 'loogle'])
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.external_sources = external_sources or []
        self.queries_performed = 0
        self.cache_hits = 0
        print("    [OK] Retrieval Specialist Agent initialized")

    def query(self, problem_statement: str,
             problem_type: str = None,
             top_k: int = 5) -> RetrievalResult:
        """
        Query for existing theorems/results matching the problem.

        This is the core "Look-Before-You-Leap" method.
        Should be called BEFORE engaging solvers.
        """
        self.queries_performed += 1

        # Check for exact signature match first (fastest)
        signature = self._compute_signature(problem_statement)
        exact_match = self._check_exact_match(signature)
        if exact_match:
            self.cache_hits += 1
            return RetrievalResult(
                confidence=RetrievalConfidence.EXACT_MATCH,
                theorem_id=exact_match.get('id'),
                theorem_content=exact_match.get('result'),
                proof_sketch=exact_match.get('proof_trace'),
                source='internal',
                similarity_score=1.0
            )

        # Generate query embedding for semantic search
        query_embedding = self._generate_query_embedding(problem_statement)

        # Search internal Vector Database
        internal_results = self._search_internal(query_embedding, top_k)

        # Check internal semantic matches
        if internal_results:
            best = internal_results[0]
            similarity = best.get('similarity', 0)
            confidence = self._classify_confidence(similarity)
            if confidence != RetrievalConfidence.NO_MATCH:
                if confidence in [RetrievalConfidence.EXACT_MATCH,
                                 RetrievalConfidence.HIGH_SIMILARITY]:
                    self.cache_hits += 1
                return RetrievalResult(
                    confidence=confidence,
                    theorem_id=best.get('id'),
                    theorem_content=best.get('result'),
                    proof_sketch=best.get('proof_trace'),
                    source='internal',
                    similarity_score=similarity
                )

        # Query external sources if internal fails
        for source in self.external_sources:
            external_result = self._query_external(source, problem_statement)
            if external_result and external_result.confidence != RetrievalConfidence.NO_MATCH:
                return external_result

        # No relevant results found
        return RetrievalResult(
            confidence=RetrievalConfidence.NO_MATCH,
            similarity_score=0.0
        )

    def _generate_query_embedding(self, problem: str) -> np.ndarray:
        """Generate embedding for the query"""
        if self.embedding_model and hasattr(self.embedding_model, 'encode'):
            try:
                return self.embedding_model.encode(problem)
            except (RuntimeError, TypeError, ValueError) as e:
                logger.debug(f"Could not generate query embedding with model: {e}")

        # Fallback: hash-based pseudo-embedding
        hash_val = int(hashlib.md5(problem.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        return np.random.randn(256).astype(np.float32)

    def _search_internal(self, query_embedding: np.ndarray,
                        top_k: int) -> List[Dict]:
        """Search internal Vector Database"""
        try:
            if hasattr(self.vector_db, 'search'):
                results = self.vector_db.search(
                    query_vector=query_embedding.tolist(),
                    top_k=top_k
                )
                return results if results else []
            elif hasattr(self.vector_db, 'query'):
                results = self.vector_db.query(
                    query_embedding=query_embedding.tolist(),
                    n_results=top_k
                )
                return results if results else []
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.debug(f"Could not search vector database: {e}")
        return []

    def _compute_signature(self, problem: str) -> str:
        """Compute problem signature for exact matching"""
        normalized = problem.lower().replace(" ", "")
        return hashlib.md5(normalized.encode()).hexdigest()

    def _check_exact_match(self, signature: str) -> Optional[Dict]:
        """Check for exact signature match in database"""
        try:
            if hasattr(self.vector_db, 'get_by_signature'):
                return self.vector_db.get_by_signature(signature)
            elif hasattr(self.vector_db, 'get_by_metadata'):
                return self.vector_db.get_by_metadata('signature', signature)
        except (AttributeError, TypeError, KeyError) as e:
            logger.debug(f"Could not check exact match for signature: {e}")
        return None

    def _classify_confidence(self, similarity: float) -> RetrievalConfidence:
        """Classify confidence based on similarity score"""
        if similarity >= self.EXACT_THRESHOLD:
            return RetrievalConfidence.EXACT_MATCH
        elif similarity >= self.HIGH_THRESHOLD:
            return RetrievalConfidence.HIGH_SIMILARITY
        elif similarity >= self.MODERATE_THRESHOLD:
            return RetrievalConfidence.MODERATE
        elif similarity >= self.LOW_THRESHOLD:
            return RetrievalConfidence.LOW
        else:
            return RetrievalConfidence.NO_MATCH

    def _query_external(self, source: str,
                       problem: str) -> Optional[RetrievalResult]:
        """
        Query external mathematical library.

        Extension point for integrating external theorem databases.
        Currently returns None as external APIs are not configured.

        To enable external queries:
        - Mathlib: Implement HTTP client for Mathlib4 API when available
        - Loogle: Implement Loogle search API integration
        """
        if source == 'mathlib':
            return self._query_mathlib(problem)
        elif source == 'loogle':
            return self._query_loogle(problem)
        return None

    def _query_mathlib(self, problem: str) -> Optional[RetrievalResult]:
        """
        Query Mathlib for matching theorems.

        Extension point: Returns None until Mathlib API client is configured.
        The system operates correctly without external APIs, using local
        vector database for theorem retrieval.
        """
        return None

    def _query_loogle(self, problem: str) -> Optional[RetrievalResult]:
        """
        Query Loogle for matching theorems.

        Extension point: Returns None until Loogle API client is configured.
        Loogle (loogle.lean-lang.org) provides type-based theorem search
        for Lean/Mathlib theorems.
        """
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'queries_performed': self.queries_performed,
            'cache_hits': self.cache_hits,
            'hit_rate': self.cache_hits / max(1, self.queries_performed) * 100,
            'external_sources': self.external_sources
        }


# ===========================================================================
# KNOWLEDGE MANAGEMENT TEAM COORDINATOR
# ===========================================================================

class KnowledgeManagementTeam:
    """
    Coordinator for the Knowledge Management Team.

    Provides unified interface for context extraction, memory indexing,
    and retrieval operations.

    KEY PROTOCOLS:
    - look_before_leap(): Check for existing solutions before solving
    - extract_context(): Get relevant context for a sub-task
    - record_result(): Store confirmed results for future retrieval

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Team Coordinator
    """

    def __init__(self, blackboard, vector_db, embedding_model=None,
                 external_sources: List[str] = None):
        """
        Initialize the Knowledge Management Team.

        Args:
            blackboard: Phase 0 Blackboard for context extraction
            vector_db: Phase 0 Vector Database for long-term memory
            embedding_model: Model for embeddings (optional)
            external_sources: External library connections
        """
        print("  [KNOWLEDGE MANAGEMENT TEAM - The Librarians]")
        self.context_extractor = ContextExtractorAgent(blackboard)
        self.memory_indexer = MemoryIndexerAgent(vector_db, embedding_model)
        self.retrieval_specialist = RetrievalSpecialistAgent(
            vector_db, embedding_model, external_sources
        )
        print("    [OK] Knowledge Management Team assembled")

    def look_before_leap(self, problem_statement: str) -> RetrievalResult:
        """
        The "Look-Before-You-Leap" protocol.

        Should be called by Orchestrator immediately after classification.
        Returns high-confidence match if available.
        """
        return self.retrieval_specialist.query(problem_statement)

    def extract_context(self, conversation_id: str,
                       target_variables: Set[str],
                       problem_type: str) -> ContextPacket:
        """Extract relevant context for a sub-task"""
        return self.context_extractor.extract_context(
            conversation_id, target_variables, problem_type
        )

    def record_result(self, conversation_id: str,
                     problem: str,
                     result: Any,
                     proof_trace: str = None) -> str:
        """Record a confirmed result for future retrieval"""
        return self.memory_indexer.index_result(
            conversation_id, problem, result, proof_trace
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        return {
            'context_extractor': self.context_extractor.get_statistics(),
            'memory_indexer': self.memory_indexer.get_statistics(),
            'retrieval_specialist': self.retrieval_specialist.get_statistics()
        }
