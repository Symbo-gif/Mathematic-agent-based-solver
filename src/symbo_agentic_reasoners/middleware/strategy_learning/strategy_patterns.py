# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Strategy Pattern Data Structures
=================================

Core data classes for strategy detection, learning, and application.

COMPONENTS:
-----------
- StrategyPattern: Reusable pattern definition
- StrategyDetection: Detection result from trace analysis
- StrategyDetectionResult: Structured detection output
- TemplatePattern: Meta-level template for problem classification
- StrategyApplication: Record of strategy use on specific problem

USAGE:
------
These classes are used by:
- Strategy learner agents (3.4-3.7) for detection
- Strategy coordinator (3.8) for aggregation
- KnowledgeGraph for persistence
- AgentSelectorOptimizer for routing decisions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class StrategyCategory(Enum):
    """Categories of problem-solving strategies."""
    STRUCTURAL = "structural"  # Global patterns (Pólya, re-encoding, local-global)
    HEURISTIC = "heuristic"    # Deep patterns (invariants, extremal, symmetrization, functional)
    NONSTANDARD = "nonstandard"  # Unconventional (descent, graphical, fixed-point)
    META = "meta"              # Meta-level (template mining, multi-solution)


class DetectionConfidence(Enum):
    """Confidence levels for strategy detection."""
    HIGH = "high"          # >= 0.7 confidence
    MEDIUM = "medium"      # >= 0.5 confidence
    LOW = "low"           # >= 0.3 confidence
    UNCERTAIN = "uncertain"  # < 0.3 confidence


@dataclass
class StrategyPattern:
    """
    Reusable problem-solving pattern.

    Represents a known strategy with its characteristics and success history.
    """
    pattern_id: str
    name: str  # e.g., "Pólya Cycle", "Invariant Method"
    category: StrategyCategory
    description: str  # Human-readable description
    abstract_description: str  # Domain-agnostic description
    detection_signals: List[str]  # Patterns in trace that indicate use
    applicability_conditions: List[str]  # When to apply
    example_problems: List[str] = field(default_factory=list)
    composition_compatible: List[str] = field(default_factory=list)  # Compatible strategy IDs
    success_count: int = 0
    total_applications: int = 0
    domains_effective: Dict[str, float] = field(default_factory=dict)  # domain -> success_rate

    @property
    def success_rate(self) -> float:
        """Overall success rate."""
        if self.total_applications == 0:
            return 0.0
        return self.success_count / self.total_applications

    def add_application(self, success: bool, domain: str):
        """Record a new application."""
        self.total_applications += 1
        if success:
            self.success_count += 1

        # Update domain-specific success rate
        if domain not in self.domains_effective:
            self.domains_effective[domain] = 0.0

        # Running average
        current_rate = self.domains_effective[domain]
        n = sum(1 for d in [domain] * self.total_applications if d == domain)
        new_rate = ((current_rate * (n - 1)) + (1.0 if success else 0.0)) / n
        self.domains_effective[domain] = new_rate


@dataclass
class StrategyDetectionResult:
    """
    Result of strategy detection on a solution trace.

    Produced by individual strategy detectors (3.4-3.7).
    """
    strategy_id: str
    strategy_name: str
    category: StrategyCategory
    confidence: float  # 0.0-1.0
    evidence: List[str]  # Detected signals explaining why
    trace_segment: Optional[Tuple[int, int]] = None  # (start_idx, end_idx) in agent_sequence
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def confidence_level(self) -> DetectionConfidence:
        """Categorize confidence."""
        if self.confidence >= 0.7:
            return DetectionConfidence.HIGH
        elif self.confidence >= 0.5:
            return DetectionConfidence.MEDIUM
        elif self.confidence >= 0.3:
            return DetectionConfidence.LOW
        else:
            return DetectionConfidence.UNCERTAIN


@dataclass
class StrategyDetection:
    """
    Full detection record for a trace.

    Aggregates all detected strategies for a single problem-solving session.
    """
    trace_id: str
    conversation_id: str
    detected_strategies: List[StrategyDetectionResult]
    detector_agent: str  # Which agent detected this
    detection_time: datetime = field(default_factory=datetime.now)
    blackboard_entry_id: Optional[str] = None  # Posted to Blackboard

    @property
    def high_confidence_strategies(self) -> List[StrategyDetectionResult]:
        """Get only high-confidence detections."""
        return [s for s in self.detected_strategies
                if s.confidence_level == DetectionConfidence.HIGH]

    def get_dominant_strategy(self) -> Optional[StrategyDetectionResult]:
        """Get strategy with highest confidence."""
        if not self.detected_strategies:
            return None
        return max(self.detected_strategies, key=lambda s: s.confidence)


@dataclass
class TemplatePattern:
    """
    Meta-level template for problem classification.

    Used by MetaStrategyLearner (3.7) for template mining.
    Represents "principle that cracked it" abstraction.
    """
    template_id: str
    principle_name: str  # e.g., "symmetry_exploitation", "reduction_to_base_case"
    description: str
    problem_signatures: List[str]  # Characteristic features of problems solved by this
    strategy_sequence: List[str]  # Typical strategy IDs in sequence
    agent_pattern: List[str]  # Typical agent invocation pattern
    success_count: int = 0
    last_used: Optional[datetime] = None
    domains: List[str] = field(default_factory=list)

    def matches_problem(self, problem_signature: str) -> bool:
        """Check if problem matches this template."""
        # Simple keyword matching (could be enhanced with embeddings)
        return any(sig in problem_signature for sig in self.problem_signatures)


@dataclass
class StrategyApplication:
    """
    Record of a strategy being applied to a specific problem.

    Stored in KnowledgeGraph strategy_applications table.
    """
    application_id: str
    strategy_id: str
    trace_id: str
    conversation_id: str
    problem_type: str
    domain: str
    success: bool
    time_ms: float
    complexity_before: Optional[str] = None
    complexity_after: Optional[str] = None
    detection_confidence: float = 1.0
    applied_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'application_id': self.application_id,
            'strategy_id': self.strategy_id,
            'trace_id': self.trace_id,
            'conversation_id': self.conversation_id,
            'problem_type': self.problem_type,
            'domain': self.domain,
            'success': self.success,
            'time_ms': self.time_ms,
            'complexity_before': self.complexity_before,
            'complexity_after': self.complexity_after,
            'detection_confidence': self.detection_confidence,
            'applied_at': self.applied_at.isoformat(),
            'metadata': self.metadata
        }


# Predefined strategy vocabularies for detection
STRATEGY_KEYWORDS = {
    # Structural strategies
    'polya_cycle': {
        'keywords': ['reformulate', 'decompose', 'retrospect', 're-recognize', 'simplify',
                    'surrogate', 'lift solution', 'phase'],
        'agent_patterns': ['structure_recognizer', 'decomposition', 'verification'],
        'metadata_signals': ['problem_reformulated', 'decomposition_applied', 'retrospective_check']
    },
    'problem_re_encoding': {
        'keywords': ['notation', 'translate', 'algebraic', 'geometric', 'combinatorial',
                    'probabilistic', 'encode', 'formulation'],
        'agent_patterns': ['notation_translator', 'structure_recognizer'],
        'metadata_signals': ['notation_changed', 'encoding_shift', 'domain_shift']
    },
    'local_global': {
        'keywords': ['special case', 'generalize', 'invariant', 'local', 'global', 'synthesis'],
        'agent_patterns': ['specialist', 'supervisor', 'coordinator'],
        'metadata_signals': ['analysis_scope', 'local_analysis', 'global_synthesis']
    },

    # Heuristic patterns
    'invariant_method': {
        'keywords': ['invariant', 'preserved', 'conserved', 'unchanged', 'symmetry'],
        'agent_patterns': ['invariant_measure', 'conserved_quantity', 'symmetry'],
        'metadata_signals': ['preserved_quantity', 'invariant_found']
    },
    'extremal_elements': {
        'keywords': ['extremal', 'maximum', 'minimum', 'optimal', 'greedy', 'exchange'],
        'agent_patterns': ['optimization', 'extremal'],
        'metadata_signals': ['extremal_element', 'optimization_applied']
    },
    'symmetrization': {
        'keywords': ['symmetric', 'symmetry', 'automorphism', 'group', 'averaging'],
        'agent_patterns': ['symmetry', 'group_theory', 'geometry'],
        'metadata_signals': ['symmetry_detected', 'symmetrization_applied']
    },
    'functional_viewpoint': {
        'keywords': ['functional', 'generating function', 'recurrence', 'operator'],
        'agent_patterns': ['functional_analysis', 'generating_function'],
        'metadata_signals': ['encoding_functional', 'generating_function_used']
    },

    # Nonstandard moves
    'infinite_descent': {
        'keywords': ['descent', 'minimal', 'contradiction', 'well-ordered'],
        'agent_patterns': ['contradiction_prover', 'induction', 'number_theory'],
        'metadata_signals': ['proof_method=contradiction', 'descent_applied']
    },
    'graphical_revisualization': {
        'keywords': ['graph', 'vertex', 'edge', 'network', 'visualization'],
        'agent_patterns': ['graph_theory', 'discrete_math'],
        'metadata_signals': ['visualization_added', 'graph_encoding']
    },
    'fixed_point': {
        'keywords': ['fixed point', 'banach', 'brouwer', 'contraction', 'iteration'],
        'agent_patterns': ['functional_analysis', 'fixed_point'],
        'metadata_signals': ['fixed_point_theorem', 'iteration_applied']
    },

    # Meta strategies
    'template_mining': {
        'keywords': ['similar', 'template', 'pattern', 'analogy', 'precedent'],
        'agent_patterns': ['pattern_indexer', 'retrieval'],
        'metadata_signals': ['similar_problems_found', 'template_match']
    },
    'multi_solution_synthesis': {
        'keywords': ['multiple solutions', 'alternative', 'synthesis', 'comparison'],
        'agent_patterns': ['verification', 'comparison'],
        'metadata_signals': ['solution_count', 'multiple_verification']
    }
}


# Strategy composition patterns (which strategies work well together)
COMPOSITION_PATTERNS = {
    ('polya_cycle', 'invariant_method'): 0.85,  # High synergy
    ('problem_re_encoding', 'functional_viewpoint'): 0.80,
    ('local_global', 'symmetrization'): 0.75,
    ('invariant_method', 'symmetrization'): 0.82,
    ('extremal_elements', 'greedy'): 0.78,  # Note: greedy is a heuristic
    ('template_mining', 'multi_solution_synthesis'): 0.70,
}


def get_strategy_keywords(strategy_name: str) -> Dict[str, List[str]]:
    """
    Get detection keywords for a strategy.

    Args:
        strategy_name: Strategy identifier (e.g., 'polya_cycle')

    Returns:
        Dict with 'keywords', 'agent_patterns', 'metadata_signals'
    """
    return STRATEGY_KEYWORDS.get(strategy_name, {
        'keywords': [],
        'agent_patterns': [],
        'metadata_signals': []
    })


def compute_composition_strength(strategy1: str, strategy2: str) -> float:
    """
    Get composition strength between two strategies.

    Args:
        strategy1: First strategy name
        strategy2: Second strategy name

    Returns:
        Composition strength (0.0-1.0), 0.5 if unknown
    """
    # Try both orderings
    key1 = (strategy1, strategy2)
    key2 = (strategy2, strategy1)

    return COMPOSITION_PATTERNS.get(key1,
           COMPOSITION_PATTERNS.get(key2, 0.5))


if __name__ == "__main__":
    """Test strategy pattern data structures."""
    print("=" * 80)
    print("STRATEGY PATTERNS TEST")
    print("=" * 80)

    # Create a strategy pattern
    pattern = StrategyPattern(
        pattern_id="strategy_invariant_method",
        name="Invariant Method",
        category=StrategyCategory.HEURISTIC,
        description="Find quantities preserved under transformations",
        abstract_description="Identify invariant structure to simplify problem",
        detection_signals=["invariant keyword", "symmetry detected"],
        applicability_conditions=["has_symmetry=true", "domain=algebra|topology"]
    )

    # Simulate applications
    pattern.add_application(success=True, domain="algebra")
    pattern.add_application(success=True, domain="algebra")
    pattern.add_application(success=False, domain="topology")
    pattern.add_application(success=True, domain="topology")

    print(f"\nStrategy Pattern: {pattern.name}")
    print(f"  Category: {pattern.category.value}")
    print(f"  Success Rate: {pattern.success_rate:.2%}")
    print(f"  Applications: {pattern.total_applications}")
    print(f"  Domain Effectiveness:")
    for domain, rate in pattern.domains_effective.items():
        print(f"    {domain}: {rate:.2%}")

    # Test detection result
    detection = StrategyDetectionResult(
        strategy_id="strategy_invariant_method",
        strategy_name="Invariant Method",
        category=StrategyCategory.HEURISTIC,
        confidence=0.85,
        evidence=["Found 'invariant' in blackboard", "symmetry_specialist invoked"]
    )

    print(f"\nDetection Result:")
    print(f"  Strategy: {detection.strategy_name}")
    print(f"  Confidence: {detection.confidence:.2%} ({detection.confidence_level.value})")
    print(f"  Evidence: {', '.join(detection.evidence)}")

    # Test keywords
    keywords = get_strategy_keywords('polya_cycle')
    print(f"\nPólya Cycle Detection Signals:")
    print(f"  Keywords: {', '.join(keywords['keywords'][:5])}...")
    print(f"  Agent Patterns: {', '.join(keywords['agent_patterns'])}")

    # Test composition
    strength = compute_composition_strength('polya_cycle', 'invariant_method')
    print(f"\nComposition Strength (Pólya + Invariant): {strength:.2%}")

    print("\nStrategy patterns operational!")
