# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Strategy Transfer Engine
=========================

PURPOSE:
--------
Enables transfer of successful problem-solving strategies across domains.
Identifies abstract patterns that generalize beyond specific problem types.

CORE CAPABILITIES:
------------------
1. Domain Abstraction: Extract domain-agnostic strategy representations
2. Transfer Candidate Identification: Find strategies effective in source domain
3. Adaptation: Modify strategies for target domain compatibility
4. Transfer Validation: Track success of transferred strategies

TRANSFER PROCESS:
-----------------
Source Domain → Abstract Pattern → Target Domain Adaptation → Validation

EXAMPLE:
--------
Invariant Method successful in algebra (80% success rate)
→ Abstract: "Find preserved quantities"
→ Transfer to geometry: "Find geometric invariants"
→ Validate with new problems

REFERENCE:
----------
Phase_4_Build_Order_Breakdown.md: Cross-domain transfer
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
import threading

from .strategy_patterns import StrategyPattern, StrategyCategory

logger = logging.getLogger('symbo_agentic_reasoners.strategy_learning.transfer')


@dataclass
class DomainMapping:
    """Mapping between concepts in source and target domains."""
    source_domain: str
    target_domain: str
    concept_mappings: Dict[str, str]  # source_concept -> target_concept
    similarity_score: float  # 0.0-1.0

    @property
    def is_strong_mapping(self) -> bool:
        """Check if this is a strong domain mapping."""
        return self.similarity_score >= 0.7


@dataclass
class TransferCandidate:
    """A strategy candidate for cross-domain transfer."""
    strategy_id: str
    strategy_name: str
    category: StrategyCategory
    source_domain: str
    target_domain: str
    source_effectiveness: float
    estimated_target_effectiveness: float
    transfer_confidence: str  # 'high', 'medium', 'low', 'exploratory'
    adaptation_needed: List[str]  # List of required adaptations
    supporting_evidence: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TransferResult:
    """Result of applying a transferred strategy."""
    transfer_id: str
    candidate: TransferCandidate
    applied: bool
    success: bool
    actual_effectiveness: float
    feedback: str
    timestamp: datetime = field(default_factory=datetime.now)


class StrategyTransferEngine:
    """
    Cross-Domain Strategy Transfer Engine

    DIRECTIVE:
    ---------
    Identify successful strategies in one domain and adapt them for use
    in different domains. Learn which strategies transfer well and which
    require significant adaptation.

    PROCESS:
    -------
    1. Identify high-performing strategies in source domain
    2. Abstract strategy to domain-independent representation
    3. Map to target domain concepts
    4. Generate adapted strategy recommendation
    5. Track and validate transferred strategies

    OUTPUT:
    ------
    Transfer candidates with adaptation guidance and confidence scores
    """

    def __init__(self, strategy_coordinator=None, knowledge_graph=None):
        """
        Initialize Strategy Transfer Engine

        Args:
            strategy_coordinator: StrategyCoordinator reference
            knowledge_graph: KnowledgeGraph for transfer history
        """
        self.strategy_coordinator = strategy_coordinator
        self.knowledge_graph = knowledge_graph
        self._lock = threading.RLock()

        # Domain concept mappings
        self.domain_mappings: Dict[Tuple[str, str], DomainMapping] = {}

        # Transfer history
        self.transfer_candidates: List[TransferCandidate] = []
        self.transfer_results: List[TransferResult] = []

        # Statistics
        self.transfers_proposed = 0
        self.transfers_attempted = 0
        self.successful_transfers = 0

        # Bootstrap domain mappings
        self._bootstrap_domain_mappings()

        print("    [OK] Strategy Transfer Engine initialized")

    def _bootstrap_domain_mappings(self):
        """Initialize common domain concept mappings."""
        # Algebra ↔ Geometry
        self.domain_mappings[('algebra', 'geometry')] = DomainMapping(
            source_domain='algebra',
            target_domain='geometry',
            concept_mappings={
                'equation': 'geometric_constraint',
                'variable': 'coordinate',
                'expression': 'geometric_object',
                'simplify': 'reduce_configuration',
                'solve': 'construct',
                'factor': 'decompose_figure',
                'invariant': 'geometric_invariant',
                'symmetry': 'geometric_symmetry',
                'extremal': 'optimal_configuration'
            },
            similarity_score=0.75
        )

        # Geometry ↔ Algebra (reverse)
        self.domain_mappings[('geometry', 'algebra')] = DomainMapping(
            source_domain='geometry',
            target_domain='algebra',
            concept_mappings={
                'point': 'variable',
                'line': 'linear_equation',
                'angle': 'expression',
                'congruent': 'equal',
                'similar': 'proportional',
                'construct': 'solve',
                'geometric_invariant': 'algebraic_invariant',
                'symmetry': 'automorphism'
            },
            similarity_score=0.75
        )

        # Algebra ↔ Combinatorics
        self.domain_mappings[('algebra', 'combinatorics')] = DomainMapping(
            source_domain='algebra',
            target_domain='combinatorics',
            concept_mappings={
                'sum': 'count',
                'product': 'arrangement',
                'factor': 'partition',
                'generating_function': 'enumeration',
                'recursion': 'recurrence_relation',
                'invariant': 'combinatorial_invariant'
            },
            similarity_score=0.70
        )

        # Optimization ↔ All domains
        for domain in ['algebra', 'geometry', 'combinatorics']:
            self.domain_mappings[('optimization', domain)] = DomainMapping(
                source_domain='optimization',
                target_domain=domain,
                concept_mappings={
                    'minimize': 'find_minimum',
                    'maximize': 'find_maximum',
                    'constraint': 'condition',
                    'objective': 'goal',
                    'greedy': 'local_optimal',
                    'extremal': 'boundary_case'
                },
                similarity_score=0.65
            )

    def identify_transfer_candidates(self, source_domain: str,
                                     target_domain: str,
                                     min_source_effectiveness: float = 0.6,
                                     limit: int = 5) -> List[TransferCandidate]:
        """
        Identify strategies for potential transfer.

        Args:
            source_domain: Domain where strategies are proven
            target_domain: Domain to transfer to
            min_source_effectiveness: Minimum success rate in source
            limit: Maximum candidates to return

        Returns:
            List of transfer candidates sorted by confidence
        """
        if not self.strategy_coordinator:
            return []

        with self._lock:
            self.transfers_proposed += len(self.transfer_candidates)

        candidates = []

        # Get domain mapping
        domain_key = (source_domain, target_domain)
        mapping = self.domain_mappings.get(domain_key)

        # Query all learners for effective strategies
        for learner_name in ['structural', 'heuristic', 'nonstandard']:
            if learner_name == 'structural':
                learner = self.strategy_coordinator.structural_learner
                strategies = learner.structural_strategies
            elif learner_name == 'heuristic':
                learner = self.strategy_coordinator.heuristic_learner
                strategies = learner.heuristic_strategies
            else:
                learner = self.strategy_coordinator.nonstandard_learner
                strategies = learner.nonstandard_strategies

            # Find effective strategies in source domain
            for strategy_name, strategy in strategies.items():
                source_eff = strategy.domains_effective.get(source_domain, 0)

                if source_eff >= min_source_effectiveness:
                    # Check target effectiveness
                    target_eff = strategy.domains_effective.get(target_domain, 0)

                    # Estimate transfer potential
                    estimated_eff, confidence, adaptations = self._estimate_transfer(
                        strategy, source_domain, target_domain, mapping
                    )

                    # Create candidate
                    candidate = TransferCandidate(
                        strategy_id=strategy.pattern_id,
                        strategy_name=strategy.name,
                        category=strategy.category,
                        source_domain=source_domain,
                        target_domain=target_domain,
                        source_effectiveness=source_eff,
                        estimated_target_effectiveness=estimated_eff,
                        transfer_confidence=confidence,
                        adaptation_needed=adaptations,
                        supporting_evidence=self._get_transfer_evidence(
                            strategy, source_domain, target_domain, mapping
                        )
                    )

                    candidates.append(candidate)

        # Sort by estimated effectiveness and confidence
        confidence_order = {'high': 3, 'medium': 2, 'low': 1, 'exploratory': 0}
        candidates.sort(
            key=lambda c: (confidence_order.get(c.transfer_confidence, 0),
                          c.estimated_target_effectiveness),
            reverse=True
        )

        return candidates[:limit]

    def _estimate_transfer(self, strategy: StrategyPattern,
                          source_domain: str, target_domain: str,
                          mapping: Optional[DomainMapping]) -> Tuple[float, str, List[str]]:
        """
        Estimate transfer effectiveness and confidence.

        Returns:
            (estimated_effectiveness, confidence_level, adaptations_needed)
        """
        source_eff = strategy.domains_effective.get(source_domain, 0)
        target_eff = strategy.domains_effective.get(target_domain, 0)

        adaptations = []

        # If already applied in target, use actual data
        if target_eff > 0:
            if target_eff >= 0.7:
                return target_eff, 'high', []
            elif target_eff >= 0.5:
                return target_eff, 'medium', ['minor_adaptation']
            elif target_eff >= 0.3:
                return target_eff, 'low', ['significant_adaptation']
            else:
                return target_eff, 'exploratory', ['major_rethinking']

        # Estimate based on domain mapping
        if mapping and mapping.is_strong_mapping:
            # Strong mapping → high transfer potential
            estimated = source_eff * 0.85  # Expect 85% retention
            confidence = 'high'
            adaptations = ['terminology_mapping']
        elif mapping:
            # Weak mapping → moderate transfer potential
            estimated = source_eff * 0.65  # Expect 65% retention
            confidence = 'medium'
            adaptations = ['concept_adaptation', 'terminology_mapping']
        else:
            # No mapping → exploratory
            estimated = source_eff * 0.4  # Expect 40% retention
            confidence = 'exploratory'
            adaptations = ['domain_analysis', 'custom_adaptation', 'validation_needed']

        # Adjust based on strategy category
        if strategy.category == StrategyCategory.STRUCTURAL:
            # Structural strategies often transfer well
            estimated *= 1.1
            if estimated >= 0.7 and confidence == 'medium':
                confidence = 'high'
        elif strategy.category == StrategyCategory.META:
            # Meta strategies are domain-agnostic
            estimated *= 1.2
            if confidence == 'exploratory':
                confidence = 'low'

        return min(estimated, 1.0), confidence, adaptations

    def _get_transfer_evidence(self, strategy: StrategyPattern,
                               source_domain: str, target_domain: str,
                               mapping: Optional[DomainMapping]) -> List[str]:
        """
        Generate supporting evidence for transfer recommendation.

        Returns:
            List of evidence strings
        """
        evidence = []

        source_eff = strategy.domains_effective.get(source_domain, 0)
        target_eff = strategy.domains_effective.get(target_domain, 0)

        # Source effectiveness
        evidence.append(
            f"{source_eff:.1%} success rate in {source_domain} "
            f"({strategy.total_applications} applications)"
        )

        # Existing target performance
        if target_eff > 0:
            evidence.append(f"Already used in {target_domain} with {target_eff:.1%} success")

        # Domain mapping quality
        if mapping:
            evidence.append(
                f"{mapping.similarity_score:.1%} domain similarity "
                f"({len(mapping.concept_mappings)} concept mappings)"
            )

        # Strategy universality
        num_domains = len(strategy.domains_effective)
        if num_domains >= 3:
            evidence.append(f"Proven across {num_domains} domains (highly transferable)")

        # Abstract description
        evidence.append(f"Abstract principle: {strategy.abstract_description}")

        return evidence

    def record_transfer_result(self, transfer_id: str, candidate: TransferCandidate,
                               success: bool, actual_effectiveness: float,
                               feedback: str = ""):
        """
        Record the result of applying a transferred strategy.

        Args:
            transfer_id: Unique transfer identifier
            candidate: The transfer candidate that was applied
            success: Whether the transfer was successful
            actual_effectiveness: Measured effectiveness
            feedback: Optional feedback on the transfer
        """
        with self._lock:
            self.transfers_attempted += 1
            if success:
                self.successful_transfers += 1

        result = TransferResult(
            transfer_id=transfer_id,
            candidate=candidate,
            applied=True,
            success=success,
            actual_effectiveness=actual_effectiveness,
            feedback=feedback
        )

        self.transfer_results.append(result)

        # Update domain mapping strength based on result
        if success:
            self._update_domain_mapping(candidate, actual_effectiveness)

    def _update_domain_mapping(self, candidate: TransferCandidate,
                               actual_effectiveness: float):
        """Update domain mapping strength based on successful transfer."""
        domain_key = (candidate.source_domain, candidate.target_domain)

        if domain_key in self.domain_mappings:
            mapping = self.domain_mappings[domain_key]

            # Adjust similarity score (running average)
            current_score = mapping.similarity_score
            transfer_score = actual_effectiveness / candidate.source_effectiveness

            # Weight: 80% current, 20% new evidence
            mapping.similarity_score = current_score * 0.8 + transfer_score * 0.2

    def get_transfer_recommendations(self, problem_context: Dict) -> List[TransferCandidate]:
        """
        Get transfer recommendations for a new problem.

        Args:
            problem_context: Problem information including target domain

        Returns:
            List of recommended strategy transfers
        """
        target_domain = problem_context.get('problem_type', 'unknown')

        # Find source domains where we have good strategies
        source_domains = set()
        if self.strategy_coordinator:
            # Query all learners for domains with good strategies
            for learner in [self.strategy_coordinator.structural_learner,
                           self.strategy_coordinator.heuristic_learner,
                           self.strategy_coordinator.nonstandard_learner]:
                for strategy in learner.structural_strategies.values() if hasattr(learner, 'structural_strategies') else []:
                    source_domains.update(strategy.domains_effective.keys())

        # Get transfer candidates from all good source domains
        all_candidates = []
        for source_domain in source_domains:
            if source_domain != target_domain:
                candidates = self.identify_transfer_candidates(
                    source_domain, target_domain, limit=3
                )
                all_candidates.extend(candidates)

        # Sort and return top recommendations
        confidence_order = {'high': 3, 'medium': 2, 'low': 1, 'exploratory': 0}
        all_candidates.sort(
            key=lambda c: (confidence_order.get(c.transfer_confidence, 0),
                          c.estimated_target_effectiveness),
            reverse=True
        )

        return all_candidates[:5]

    def get_statistics(self) -> Dict[str, Any]:
        """Get transfer engine statistics."""
        success_rate = (self.successful_transfers / max(1, self.transfers_attempted)) * 100

        return {
            'transfers_proposed': self.transfers_proposed,
            'transfers_attempted': self.transfers_attempted,
            'successful_transfers': self.successful_transfers,
            'success_rate': success_rate,
            'domain_mappings': len(self.domain_mappings),
            'transfer_results_recorded': len(self.transfer_results)
        }


if __name__ == "__main__":
    """Test Strategy Transfer Engine"""
    print("=" * 80)
    print("STRATEGY TRANSFER ENGINE TEST")
    print("=" * 80)
    print()

    # Initialize engine (standalone test without coordinator)
    engine = StrategyTransferEngine()
    print()

    # Test domain mappings
    print("DOMAIN MAPPINGS:")
    print("-" * 40)
    for (source, target), mapping in engine.domain_mappings.items():
        print(f"{source} -> {target}: {mapping.similarity_score:.1%} similarity")
        print(f"  Key mappings: {list(mapping.concept_mappings.items())[:3]}")
    print()

    # Test transfer candidate identification (simulated)
    print("TRANSFER CANDIDATE IDENTIFICATION:")
    print("-" * 40)
    print("(Requires StrategyCoordinator - skipping in standalone test)")
    print()

    # Test transfer result recording
    print("TRANSFER RESULT RECORDING:")
    print("-" * 40)

    # Create a mock candidate
    from .strategy_patterns import StrategyCategory
    mock_candidate = TransferCandidate(
        strategy_id='strategy_invariant_method',
        strategy_name='Invariant Method',
        category=StrategyCategory.HEURISTIC,
        source_domain='algebra',
        target_domain='geometry',
        source_effectiveness=0.80,
        estimated_target_effectiveness=0.68,
        transfer_confidence='high',
        adaptation_needed=['terminology_mapping'],
        supporting_evidence=[
            "80% success in algebra",
            "Strong domain mapping available"
        ]
    )

    # Record successful transfer
    engine.record_transfer_result(
        transfer_id='transfer_001',
        candidate=mock_candidate,
        success=True,
        actual_effectiveness=0.72,
        feedback="Invariant method successfully adapted to geometric invariants"
    )

    print(f"Recorded transfer result: {mock_candidate.strategy_name}")
    print(f"  Source: {mock_candidate.source_domain} ({mock_candidate.source_effectiveness:.1%})")
    print(f"  Target: {mock_candidate.target_domain} ({0.72:.1%} actual)")
    print()

    # Show statistics
    print("TRANSFER ENGINE STATISTICS:")
    print("-" * 40)
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print()
    print("=" * 80)
    print("STRATEGY TRANSFER ENGINE TEST COMPLETE")
    print("=" * 80)
