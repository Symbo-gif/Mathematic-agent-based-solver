# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Heuristic Transfer Learning Engine
===================================

Enables cross-domain transfer of problem-solving heuristics for research-level reasoning.

CAPABILITIES:
------------
- Abstract domain-specific heuristics to general patterns
- Identify transfer candidates based on domain similarity
- Adapt heuristics from source to target domain
- Track transfer success/failure to refine similarity matrix
- Build domain similarity graph

TRANSFER PROCESS:
-----------------
1. Heuristic Abstraction: Extract domain-agnostic pattern
2. Candidate Identification: Find similar domains
3. Adaptation: Translate vocabulary to target domain
4. Validation: Apply and track success
5. Learning: Update similarity matrix

EXAMPLES:
---------
- "Iterative refinement" applies across: numerical methods, optimization, SAT solving
- "Divide and conquer" applies across: sorting, FFT, matrix multiplication
- "Dynamic programming" applies across: optimization, graph algorithms, string matching

REFERENCE:
---------
- Plan: Days 30-31 - Heuristic transfer engine
- Target: Cross-domain intelligence for research problems
"""

import logging
import json
from typing import Dict, Any, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger('symbo_agentic_reasoners.heuristic_transfer')


@dataclass
class AbstractHeuristic:
    """Domain-agnostic heuristic pattern."""
    pattern_name: str  # 'iterative_refinement', 'greedy', 'divide_conquer', etc.
    description: str
    source_domain: str
    source_vocabulary: Dict[str, str]  # Domain-specific terms
    abstract_algorithm: List[str]  # Algorithm steps in abstract form
    applicability_conditions: List[str]
    success_rate: float = 0.0
    transfer_count: int = 0


@dataclass
class DomainSimilarity:
    """Similarity between two domains."""
    domain1: str
    domain2: str
    similarity_score: float  # 0.0-1.0
    shared_primitives: List[str]
    shared_techniques: List[str]
    transfer_successes: int = 0
    transfer_attempts: int = 0


class HeuristicTransferEngine:
    """
    Cross-domain transfer learning for mathematical heuristics.

    Enables research-level problem solving by transferring successful
    patterns between related mathematical domains.
    """

    def __init__(self, similarity_db_path: str = None):
        """Initialize heuristic transfer engine."""
        if similarity_db_path is None:
            similarity_db_path = "data/transfer_learning/domain_similarity.json"

        self.db_path = Path(similarity_db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Domain similarity matrix
        self.similarity_matrix: Dict[Tuple[str, str], DomainSimilarity] = {}

        # Abstract heuristic library
        self.heuristics: Dict[str, AbstractHeuristic] = {}

        # Load existing data
        self._load_similarity_matrix()
        self._initialize_known_similarities()
        self._initialize_common_heuristics()

        logger.info("Heuristic Transfer Engine initialized")
        logger.info(f"  Domain pairs: {len(self.similarity_matrix)}")
        logger.info(f"  Abstract heuristics: {len(self.heuristics)}")

    def _initialize_known_similarities(self):
        """Initialize known domain similarities."""
        # Define domain relationships based on shared structure
        similarities = [
            ('linear_algebra', 'real_analysis', 0.8, ['vector_spaces', 'norms', 'inner_products']),
            ('linear_algebra', 'functional_analysis', 0.9, ['operators', 'spaces', 'norms']),
            ('abstract_algebra', 'category_theory', 0.85, ['morphisms', 'composition', 'universal_properties']),
            ('number_theory', 'cryptography', 0.7, ['modular_arithmetic', 'primes', 'factorization']),
            ('differential_equations', 'physics', 0.9, ['dynamics', 'evolution', 'conservation']),
            ('real_analysis', 'complex_analysis', 0.75, ['limits', 'continuity', 'integration']),
            ('logic', 'computer_science', 0.8, ['algorithms', 'decidability', 'complexity']),
            ('optimization', 'numerical_methods', 0.85, ['iterative_methods', 'convergence', 'approximation']),
        ]

        for domain1, domain2, score, shared in similarities:
            key = tuple(sorted([domain1, domain2]))
            self.similarity_matrix[key] = DomainSimilarity(
                domain1=domain1,
                domain2=domain2,
                similarity_score=score,
                shared_primitives=shared,
                shared_techniques=[]
            )

    def _initialize_common_heuristics(self):
        """Initialize library of common abstract heuristics."""
        self.heuristics['iterative_refinement'] = AbstractHeuristic(
            pattern_name='iterative_refinement',
            description='Start with approximation, iteratively improve until convergence',
            source_domain='numerical_methods',
            source_vocabulary={'iterate': 'iterate', 'tolerance': 'tolerance', 'converge': 'converge'},
            abstract_algorithm=[
                '1. Initialize with guess x₀',
                '2. Compute improvement: x_{n+1} = improve(x_n)',
                '3. Check convergence: |x_{n+1} - x_n| < ε',
                '4. Repeat until convergence'
            ],
            applicability_conditions=['has_distance_metric', 'has_improvement_operator']
        )

        self.heuristics['divide_and_conquer'] = AbstractHeuristic(
            pattern_name='divide_and_conquer',
            description='Split problem into smaller subproblems, solve recursively, combine',
            source_domain='algorithms',
            source_vocabulary={},
            abstract_algorithm=[
                '1. BASE: If problem size ≤ threshold, solve directly',
                '2. DIVIDE: Split into k subproblems',
                '3. CONQUER: Solve each subproblem recursively',
                '4. COMBINE: Merge solutions'
            ],
            applicability_conditions=['decomposable', 'subproblem_independence']
        )

        self.heuristics['greedy_selection'] = AbstractHeuristic(
            pattern_name='greedy_selection',
            description='Make locally optimal choice at each step',
            source_domain='optimization',
            source_vocabulary={'objective': 'objective', 'feasible': 'feasible'},
            abstract_algorithm=[
                '1. Initialize solution S = ∅',
                '2. While not complete:',
                '   - Choose best available element by greedy criterion',
                '   - Add to solution if feasible',
                '3. Return S'
            ],
            applicability_conditions=['matroid_structure', 'greedy_choice_property']
        )

    def find_transfer_candidates(
        self,
        problem_domain: str,
        heuristic_name: str
    ) -> List[Tuple[str, float]]:
        """
        Find candidate domains for transferring heuristic.

        Args:
            problem_domain: Domain of current problem
            heuristic_name: Heuristic to transfer

        Returns:
            List of (target_domain, similarity_score) sorted by score
        """
        candidates = []

        for (d1, d2), similarity in self.similarity_matrix.items():
            if problem_domain in [d1, d2]:
                target = d2 if problem_domain == d1 else d1
                candidates.append((target, similarity.similarity_score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def abstract_heuristic(
        self,
        domain_specific_heuristic: Dict[str, Any],
        source_domain: str
    ) -> AbstractHeuristic:
        """
        Abstract domain-specific heuristic to general pattern.

        Args:
            domain_specific_heuristic: Heuristic from specific domain
            source_domain: Source domain

        Returns:
            Abstract heuristic
        """
        # Extract pattern type
        pattern_type = domain_specific_heuristic.get('pattern', 'unknown')

        # Create abstract version
        return AbstractHeuristic(
            pattern_name=pattern_type,
            description=domain_specific_heuristic.get('description', ''),
            source_domain=source_domain,
            source_vocabulary=domain_specific_heuristic.get('vocabulary', {}),
            abstract_algorithm=domain_specific_heuristic.get('steps', []),
            applicability_conditions=domain_specific_heuristic.get('conditions', [])
        )

    def adapt_heuristic(
        self,
        abstract_heuristic: AbstractHeuristic,
        target_domain: str,
        target_vocabulary: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Adapt abstract heuristic to target domain.

        Args:
            abstract_heuristic: Abstract heuristic pattern
            target_domain: Target domain
            target_vocabulary: Domain-specific vocabulary mapping

        Returns:
            Adapted heuristic for target domain
        """
        # Translate algorithm steps
        adapted_steps = []
        for step in abstract_heuristic.abstract_algorithm:
            adapted_step = step
            # Replace source vocabulary with target vocabulary
            for abstract_term, target_term in target_vocabulary.items():
                adapted_step = adapted_step.replace(abstract_term, target_term)
            adapted_steps.append(adapted_step)

        return {
            'pattern': abstract_heuristic.pattern_name,
            'domain': target_domain,
            'algorithm': adapted_steps,
            'source_domain': abstract_heuristic.source_domain,
            'applicability': abstract_heuristic.applicability_conditions
        }

    def record_transfer_attempt(
        self,
        source_domain: str,
        target_domain: str,
        heuristic_name: str,
        success: bool
    ):
        """
        Record transfer attempt to update similarity matrix.

        Args:
            source_domain, target_domain: Domains involved
            heuristic_name: Heuristic transferred
            success: Whether transfer succeeded
        """
        key = tuple(sorted([source_domain, target_domain]))

        if key in self.similarity_matrix:
            similarity = self.similarity_matrix[key]
            similarity.transfer_attempts += 1
            if success:
                similarity.transfer_successes += 1

            # Update similarity score based on success rate
            if similarity.transfer_attempts > 0:
                success_rate = similarity.transfer_successes / similarity.transfer_attempts
                # Blend with prior: 80% prior + 20% empirical
                similarity.similarity_score = 0.8 * similarity.similarity_score + 0.2 * success_rate

        self._save_similarity_matrix()

    def get_similar_domains(
        self,
        domain: str,
        min_similarity: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Get domains similar to given domain.

        Args:
            domain: Query domain
            min_similarity: Minimum similarity threshold

        Returns:
            List of (similar_domain, similarity_score)
        """
        similar = []

        for (d1, d2), sim in self.similarity_matrix.items():
            if domain in [d1, d2] and sim.similarity_score >= min_similarity:
                other = d2 if domain == d1 else d1
                similar.append((other, sim.similarity_score))

        return sorted(similar, key=lambda x: x[1], reverse=True)

    def _load_similarity_matrix(self):
        """Load similarity matrix from disk."""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                # Reconstruct similarity objects
                for key_str, sim_data in data.items():
                    d1, d2 = json.loads(key_str)
                    key = tuple(sorted([d1, d2]))
                    self.similarity_matrix[key] = DomainSimilarity(**sim_data)

    def _save_similarity_matrix(self):
        """Save similarity matrix to disk."""
        data = {}
        for key, similarity in self.similarity_matrix.items():
            key_str = json.dumps(list(key))
            data[key_str] = {
                'domain1': similarity.domain1,
                'domain2': similarity.domain2,
                'similarity_score': similarity.similarity_score,
                'shared_primitives': similarity.shared_primitives,
                'shared_techniques': similarity.shared_techniques,
                'transfer_successes': similarity.transfer_successes,
                'transfer_attempts': similarity.transfer_attempts
            }

        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)


# Singleton
_transfer_engine = None

def get_transfer_engine() -> HeuristicTransferEngine:
    """Get global transfer engine instance."""
    global _transfer_engine
    if _transfer_engine is None:
        _transfer_engine = HeuristicTransferEngine()
    return _transfer_engine


if __name__ == "__main__":
    print("=" * 80)
    print("HEURISTIC TRANSFER ENGINE TEST")
    print("=" * 80)

    engine = HeuristicTransferEngine()

    # Test similarity queries
    print("\nDomains similar to 'linear_algebra':")
    similar = engine.get_similar_domains('linear_algebra')
    for domain, score in similar:
        print(f"  {domain}: {score:.2f}")

    # Test transfer candidate finding
    print("\nTransfer candidates for 'iterative_refinement' from 'optimization':")
    candidates = engine.find_transfer_candidates('optimization', 'iterative_refinement')
    for domain, score in candidates[:3]:
        print(f"  {domain}: {score:.2f}")

    # Test heuristic abstraction
    print("\nAbstract heuristics available:")
    for name, heuristic in engine.heuristics.items():
        print(f"  {name}: {heuristic.description[:60]}...")

    print("\nTransfer Engine operational!")
