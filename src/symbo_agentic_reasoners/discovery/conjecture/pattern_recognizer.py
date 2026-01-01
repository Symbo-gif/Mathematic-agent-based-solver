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
Pattern Recognizer - "The Filter"
==================================

Agent 1.2 of the Conjecture Generation Team

Sifts through millions of synthetic theorems from the Dreamer. Uses heuristics
to filter out trivial tautologies and identifies "interesting" non-trivial
relationships that appear frequently but lack formal names.

Filtering Criteria:
- Novelty score: Has this pattern been seen before?
- Structural complexity: Is it non-trivial?
- Cross-domain applicability: Does it generalize?
- Theorem-space density analysis: Is it in an interesting region?

Output: CandidateConjecture objects ready for formalization

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 1
Reference: Phase_6_Build_Order_Breakdown.md, Step 1
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Generator, Dict, Any, Set, Tuple
from datetime import datetime
from enum import Enum
from collections import defaultdict

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Expr, Symbol, simplify, expand, parse_expr
)

from .synthetic_data_generator import SyntheticTheorem, Eq

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.conjecture_generation.pattern_recognizer')
except ImportError:
    logger = logging.getLogger(__name__)


class ConjectureStatus(Enum):
    """Status of a conjecture through the discovery pipeline"""
    GENERATED = 'generated'      # Created by Synthetic Data Generator
    FILTERED = 'filtered'        # Passed Pattern Recognizer
    FORMALIZED = 'formalized'    # Converted to formal representation
    SUBMITTED = 'submitted'      # Sent to Deep Search Team
    PROVING = 'proving'          # Active proof search
    PROVEN = 'proven'            # Successfully proven
    REFUTED = 'refuted'          # Counter-example found
    TIMEOUT = 'timeout'          # Search exhausted resources
    UNDECIDABLE = 'undecidable'  # Classified as undecidable


@dataclass
class CandidateConjecture:
    """
    A conjecture that has passed the Pattern Recognizer's filters.
    Ready for formalization and proof attempts.

    Attributes:
        conjecture_id: Unique identifier
        source_theorem: The original synthetic theorem
        interestingness_score: 0-1 score for how interesting the pattern is
        novelty_score: 0-1 score for how novel this is
        cross_domain_applicability: Domains where this might apply
        status: Current status in the pipeline
        priority: Priority for proof attempts (higher = more important)

    Formalization fields (populated by ConjectureFormalizer):
        lean4_statement: Lean4 code representation
        omdoc_representation: OMDoc XML representation
        sympy_form: SymPy expression form
    """
    conjecture_id: str
    source_theorem: SyntheticTheorem
    interestingness_score: float
    novelty_score: float
    cross_domain_applicability: List[str]
    status: ConjectureStatus = ConjectureStatus.FILTERED
    priority: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)

    # Formalization outputs (populated by Conjecture Formalizer)
    lean4_statement: Optional[str] = None
    omdoc_representation: Optional[str] = None
    native_form: Optional[Expr] = None  # Native symbolic expression
    verification_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'conjecture_id': self.conjecture_id,
            'source_theorem': self.source_theorem.to_dict(),
            'interestingness_score': self.interestingness_score,
            'novelty_score': self.novelty_score,
            'cross_domain_applicability': self.cross_domain_applicability,
            'status': self.status.value,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'has_lean4': self.lean4_statement is not None,
            'has_omdoc': self.omdoc_representation is not None
        }


class PatternRecognizer:
    """
    Agent 1.2: The Filter

    Sifts through synthetic theorems to identify interesting, non-trivial
    patterns that warrant formal proof attempts.

    Key capabilities:
    - Tautology detection and filtering
    - Novelty scoring based on pattern frequency
    - Cross-domain applicability analysis
    - Interestingness scoring using multiple heuristics
    - Streaming filter for memory efficiency

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    def __init__(self, knowledge_base=None, novelty_threshold: float = 0.3):
        """
        Initialize the Pattern Recognizer.

        Args:
            knowledge_base: Phase 3 knowledge management for known theorem lookup
            novelty_threshold: Minimum novelty score to pass filter (0-1)
        """
        self.knowledge_base = knowledge_base
        self.novelty_threshold = novelty_threshold

        # Pattern tracking
        self.seen_hashes: Set[str] = set()
        self.pattern_counts: Dict[str, int] = defaultdict(int)
        self.domain_patterns: Dict[str, Set[str]] = defaultdict(set)

        # Known trivial patterns to filter
        self.trivial_patterns = {
            'x = x',
            '0 = 0',
            'True',
            'x + 0 = x',
            'x * 1 = x',
            'x * 0 = 0'
        }

        # Statistics
        self.stats = {
            'theorems_processed': 0,
            'passed_filter': 0,
            'rejected_tautology': 0,
            'rejected_duplicate': 0,
            'rejected_known': 0,
            'rejected_low_complexity': 0,
            'rejected_low_novelty': 0
        }

    def filter_stream(
        self,
        theorem_stream: Generator[SyntheticTheorem, None, None],
        batch_size: int = 100,
        max_candidates: int = None
    ) -> Generator[CandidateConjecture, None, None]:
        """
        Filter theorems and yield candidate conjectures.

        Args:
            theorem_stream: Stream of synthetic theorems
            batch_size: Process in batches of this size
            max_candidates: Maximum candidates to yield (None for no limit)

        Yields:
            CandidateConjecture objects that pass all filters
        """
        batch = []
        candidate_count = 0

        for theorem in theorem_stream:
            batch.append(theorem)

            if len(batch) >= batch_size:
                candidates = self._process_batch(batch)
                for candidate in candidates:
                    if max_candidates and candidate_count >= max_candidates:
                        return
                    yield candidate
                    candidate_count += 1
                batch = []

        # Process remaining
        if batch:
            candidates = self._process_batch(batch)
            for candidate in candidates:
                if max_candidates and candidate_count >= max_candidates:
                    return
                yield candidate
                candidate_count += 1

    def filter_batch(self, theorems: List[SyntheticTheorem]) -> List[CandidateConjecture]:
        """
        Filter a batch of theorems and return interesting candidates.

        Args:
            theorems: List of synthetic theorems to filter

        Returns:
            List of CandidateConjecture objects
        """
        return self._process_batch(theorems)

    def _process_batch(self, theorems: List[SyntheticTheorem]) -> List[CandidateConjecture]:
        """Process a batch of theorems and return interesting candidates"""
        candidates = []

        for theorem in theorems:
            self.stats['theorems_processed'] += 1

            # Run through filter stages
            if not self._passes_all_filters(theorem):
                continue

            # Elevate to candidate
            candidate = self._elevate_to_candidate(theorem)
            if candidate:
                candidates.append(candidate)
                self.stats['passed_filter'] += 1

        return candidates

    def _passes_all_filters(self, theorem: SyntheticTheorem) -> bool:
        """Check if theorem passes all filter stages"""

        # Stage 1: Deduplication
        thm_hash = theorem.compute_hash()
        if thm_hash in self.seen_hashes:
            self.stats['rejected_duplicate'] += 1
            return False
        self.seen_hashes.add(thm_hash)

        # Stage 2: Tautology detection
        if self._is_tautology(theorem):
            self.stats['rejected_tautology'] += 1
            return False

        # Stage 3: Complexity threshold
        if theorem.complexity_score < 0.1:
            self.stats['rejected_low_complexity'] += 1
            return False

        # Stage 4: Known theorem check
        if self._is_known_theorem(theorem):
            self.stats['rejected_known'] += 1
            return False

        # Stage 5: Novelty check
        if not self._is_novel(theorem):
            self.stats['rejected_low_novelty'] += 1
            return False

        return True

    def _is_tautology(self, theorem: SyntheticTheorem) -> bool:
        """
        Check if theorem is a trivial tautology.

        Detects patterns like:
        - x = x (reflexivity)
        - Trivially true statements
        - Zero-effect operations
        """
        conclusion = theorem.conclusion
        conclusion_str = str(conclusion)

        # Check against known trivial patterns
        for pattern in self.trivial_patterns:
            if pattern in conclusion_str:
                return True

        # Check for reflexive equality (x = x)
        if isinstance(conclusion, Eq):
            try:
                # Direct equality
                if conclusion.lhs == conclusion.rhs:
                    return True

                # Simplification makes them equal
                diff = simplify(conclusion.lhs - conclusion.rhs)
                if diff == 0 or (hasattr(diff, 'is_zero') and diff.is_zero):
                    return True

                # Try expanding both sides
                lhs_exp = expand(conclusion.lhs)
                rhs_exp = expand(conclusion.rhs)
                if lhs_exp == rhs_exp:
                    return True
            except (TypeError, AttributeError, ValueError) as e:
                logger.debug(f"Could not check reflexive equality: {e}")

        # Check for True statements
        try:
            if conclusion == True or conclusion is True:
                return True
        except (TypeError, AttributeError) as e:
            logger.debug(f"Could not check True statement: {e}")

        return False

    def _is_known_theorem(self, theorem: SyntheticTheorem) -> bool:
        """
        Check if theorem is already known in the knowledge base.

        Uses Phase 3 RAG infrastructure if available.
        """
        if self.knowledge_base is None:
            return False

        try:
            # Query knowledge base for similar theorems
            natural_language = theorem.to_natural_language()
            results = self.knowledge_base.search(natural_language, top_k=3)

            for result in results:
                if result.get('similarity', 0) > 0.95:
                    return True
            return False
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.debug(f"Could not check knowledge base: {e}")
            return False

    def _is_novel(self, theorem: SyntheticTheorem) -> bool:
        """
        Check if theorem pattern is novel enough to be interesting.

        Uses pattern frequency analysis - patterns that appear too often
        are likely trivial, but patterns that appear a few times may
        indicate an interesting relationship.
        """
        # Extract structural pattern
        pattern = self._extract_pattern(theorem)

        # Track pattern frequency
        self.pattern_counts[pattern] += 1
        self.domain_patterns[theorem.domain].add(pattern)

        count = self.pattern_counts[pattern]

        # Novel if in the "sweet spot":
        # - Seen at least twice (not random noise)
        # - Not seen too many times (not trivial)
        novelty_score = self._compute_novelty_score(count)

        theorem.novelty_score = novelty_score
        return novelty_score >= self.novelty_threshold

    def _extract_pattern(self, theorem: SyntheticTheorem) -> str:
        """
        Extract structural pattern for novelty detection.

        Creates a signature based on:
        - Domain
        - Conclusion type
        - Premise types
        - Number of symbols
        """
        conclusion_type = type(theorem.conclusion).__name__
        premise_types = sorted([type(p).__name__ for p in theorem.premises])

        # Count free symbols
        symbol_count = len(theorem.conclusion.free_symbols) if hasattr(theorem.conclusion, 'free_symbols') else 0

        pattern = f"{theorem.domain}:{conclusion_type}:{','.join(premise_types)}:{symbol_count}"
        return pattern

    def _compute_novelty_score(self, pattern_count: int) -> float:
        """
        Compute novelty score based on pattern frequency.

        Sweet spot is around 3-10 occurrences:
        - < 3: Too rare, might be noise
        - 3-10: Interesting pattern
        - > 10: Too common, likely trivial

        Returns:
            Float between 0 and 1
        """
        if pattern_count < 2:
            return 0.2  # Low novelty for very rare patterns
        elif pattern_count <= 5:
            return 0.9  # High novelty for patterns seen a few times
        elif pattern_count <= 10:
            return 0.7  # Medium-high novelty
        elif pattern_count <= 50:
            return 0.4  # Decreasing novelty
        elif pattern_count <= 100:
            return 0.2  # Low novelty
        else:
            return 0.1  # Very low novelty for common patterns

    def _elevate_to_candidate(self, theorem: SyntheticTheorem) -> Optional[CandidateConjecture]:
        """
        Elevate an interesting theorem to a candidate conjecture.

        Computes final scores and identifies cross-domain applicability.
        """
        # Compute interestingness score
        interestingness = self._compute_interestingness(theorem)

        # Assess cross-domain applicability
        applicability = self._assess_cross_domain(theorem)

        # Compute priority
        priority = self._compute_priority(theorem, interestingness)

        return CandidateConjecture(
            conjecture_id=f"cand_{theorem.theorem_id}",
            source_theorem=theorem,
            interestingness_score=interestingness,
            novelty_score=theorem.novelty_score,
            cross_domain_applicability=applicability,
            priority=priority
        )

    def _compute_interestingness(self, theorem: SyntheticTheorem) -> float:
        """
        Compute interestingness score using multiple factors.

        Factors:
        - Complexity score (40%)
        - Number of derivation steps (20%)
        - Novelty score (30%)
        - Domain bonus (10%)
        """
        # Base complexity contribution
        score = theorem.complexity_score * 0.4

        # Derivation steps contribution
        steps_score = min(1.0, len(theorem.derivation_steps) / 5) * 0.2
        score += steps_score

        # Novelty contribution (higher novelty = more interesting)
        score += theorem.novelty_score * 0.3

        # Domain bonus for harder domains
        domain_bonuses = {
            'number_theory': 0.1,
            'combinatorics': 0.08,
            'analysis': 0.06,
            'geometry': 0.04,
            'algebra': 0.02,
            'linear_algebra': 0.03
        }
        score += domain_bonuses.get(theorem.domain, 0)

        return min(1.0, round(score, 3))

    def _assess_cross_domain(self, theorem: SyntheticTheorem) -> List[str]:
        """
        Assess which domains might benefit from this theorem.

        Analyzes the structure and symbols used to identify
        potential cross-domain applications.
        """
        domains = [theorem.domain]

        try:
            expr_str = str(theorem.conclusion)

            # Check for cross-domain indicators
            if 'sin' in expr_str or 'cos' in expr_str or 'tan' in expr_str:
                if 'geometry' not in domains:
                    domains.append('geometry')
                if 'analysis' not in domains:
                    domains.append('analysis')

            if 'exp' in expr_str or 'log' in expr_str:
                if 'analysis' not in domains:
                    domains.append('analysis')

            if 'Mod' in expr_str or 'gcd' in expr_str or 'factorial' in expr_str:
                if 'number_theory' not in domains:
                    domains.append('number_theory')

            if 'binomial' in expr_str or 'Sum' in expr_str:
                if 'combinatorics' not in domains:
                    domains.append('combinatorics')

            if 'Matrix' in expr_str or 'det' in expr_str or 'trace' in expr_str:
                if 'linear_algebra' not in domains:
                    domains.append('linear_algebra')

            if 'Integral' in expr_str or 'Derivative' in expr_str:
                if 'analysis' not in domains:
                    domains.append('analysis')

        except (TypeError, AttributeError) as e:
            logger.debug(f"Could not analyze expression for domains: {e}")

        return list(set(domains))

    def _compute_priority(self, theorem: SyntheticTheorem, interestingness: float) -> float:
        """
        Compute priority for proof attempts.

        Higher priority means the conjecture should be attempted sooner.
        """
        # Base priority from interestingness
        priority = interestingness * 0.6

        # Complexity adjustment (not too complex, not too simple)
        complexity = theorem.complexity_score
        if 0.3 <= complexity <= 0.7:
            priority += 0.2  # Sweet spot
        elif complexity < 0.3:
            priority += 0.05  # Too simple
        else:
            priority += 0.1  # Too complex

        # Domain priority
        domain_priorities = {
            'number_theory': 0.15,
            'combinatorics': 0.12,
            'geometry': 0.1,
            'analysis': 0.08,
            'algebra': 0.05,
            'linear_algebra': 0.07
        }
        priority += domain_priorities.get(theorem.domain, 0)

        return min(1.0, round(priority, 3))

    def get_statistics(self) -> Dict[str, Any]:
        """Get filter statistics"""
        pass_rate = 0
        if self.stats['theorems_processed'] > 0:
            pass_rate = self.stats['passed_filter'] / self.stats['theorems_processed'] * 100

        return {
            **self.stats,
            'unique_patterns': len(self.pattern_counts),
            'patterns_per_domain': {d: len(p) for d, p in self.domain_patterns.items()},
            'pass_rate_percent': round(pass_rate, 2)
        }

    def reset(self):
        """Reset filter state"""
        self.seen_hashes.clear()
        self.pattern_counts.clear()
        self.domain_patterns.clear()
        for key in self.stats:
            self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if filter is healthy"""
        return True  # Filter is stateless beyond caches
