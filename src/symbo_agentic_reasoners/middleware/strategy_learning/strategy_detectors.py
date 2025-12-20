# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Strategy Detectors
==================

Granular detection functions for specific problem-solving strategies.
These detectors provide reusable, composable pattern matching logic.

DETECTOR FUNCTIONS:
-------------------
Each detector analyzes a solution trace and returns a confidence score
(0.0-1.0) along with supporting evidence.

CATEGORIES:
-----------
- Structural: Pólya Cycle, Re-encoding, Local-Global
- Heuristic: Invariant, Extremal, Symmetrization, Functional
- Nonstandard: Infinite Descent, Graphical, Fixed-Point
- Meta: Template Mining, Multi-Solution

USAGE:
------
Import individual detectors or use detect_all_strategies() for comprehensive analysis.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DetectorResult:
    """Result from a strategy detector."""
    confidence: float  # 0.0-1.0
    evidence: List[str]
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ===========================================================================
# STRUCTURAL STRATEGY DETECTORS
# ===========================================================================

def detect_polya_cycle(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Pólya 4-Phase Cycle pattern.

    Signals:
    - Phase transitions: understand → plan → execute → reflect
    - Reformulation after failed attempts
    - Retrospective analysis
    - Decomposition → solution → verification pattern

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Phase 1: Understanding (structure recognition)
    has_understanding = any('structure' in a or 'recogni' in a or 'parse' in a
                           for a in sequence_lower)
    if has_understanding:
        evidence.append("Understanding phase: structure recognition")
        confidence += 0.20

    # Phase 2: Planning (decomposition/strategy selection)
    has_planning = any('decompos' in a or 'strateg' in a or 'plan' in a
                      for a in sequence_lower)
    if has_planning:
        evidence.append("Planning phase: decomposition")
        confidence += 0.25

    # Phase 3: Execution (solver agents)
    solver_count = sum(1 for a in sequence_lower if 'solver' in a or 'agent' in a)
    if solver_count > 0:
        evidence.append(f"Execution phase: {solver_count} solver invocations")
        confidence += 0.20

    # Phase 4: Reflection (verification/retrospective)
    has_reflection = any('verif' in a or 'ax_prover' in a or 'check' in a
                        for a in sequence_lower)
    if has_reflection:
        evidence.append("Reflection phase: verification")
        confidence += 0.20

    # Iteration indicator (multiple attempts)
    if solver_count > 1:
        evidence.append("Iterative refinement detected")
        confidence += 0.15

    # Metadata signals
    if any(kw in metadata_str for kw in ['reformulate', 'retrospect', 'decompose']):
        evidence.append("Pólya keywords in metadata")
        confidence += 0.15

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence,
        metadata={'phases_detected': len(evidence)}
    )


def detect_problem_re_encoding(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Problem Re-encoding pattern.

    Signals:
    - Domain shift (algebraic ↔ geometric ↔ combinatorial)
    - Notation translator invoked
    - Encoding change in metadata

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Translator/encoding agents
    if any('translat' in a or 'notation' in a or 'encoding' in a
          for a in sequence_lower):
        evidence.append("Notation translator/encoder invoked")
        confidence += 0.40

    # Domain keywords in metadata
    domain_keywords = ['geometric', 'algebraic', 'combinatorial', 'probabilistic',
                      'notation', 'encode', 'translate', 'formulation']
    if any(kw in metadata_str for kw in domain_keywords):
        evidence.append("Domain shift keywords detected")
        confidence += 0.30

    # Explicit domain shift
    if 'domain_shift' in metadata_str or 'encoding_shift' in metadata_str:
        evidence.append("Explicit domain/encoding shift")
        confidence += 0.30

    # Cross-domain agents
    domains = []
    if any('algebra' in a for a in sequence_lower):
        domains.append('algebraic')
    if any('geom' in a for a in sequence_lower):
        domains.append('geometric')
    if any('combin' in a or 'discrete' in a for a in sequence_lower):
        domains.append('combinatorial')

    if len(domains) >= 2:
        evidence.append(f"Cross-domain agents: {', '.join(domains)}")
        confidence += 0.25

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence,
        metadata={'domains': domains}
    )


def detect_local_global(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Local-Global coordination pattern.

    Signals:
    - Multiple specialists → supervisor synthesis
    - Parallel agent invocations
    - Local analysis → global integration

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Count specialists
    specialists = [a for a in sequence_lower if 'specialist' in a or 'expert' in a]
    if len(specialists) >= 2:
        evidence.append(f"Multiple specialists ({len(specialists)})")
        confidence += 0.35

    # Supervisor/coordinator
    has_supervisor = any('supervisor' in a or 'coordinator' in a or 'orchestrat' in a
                        for a in sequence_lower)
    if has_supervisor:
        evidence.append("Supervisor coordination detected")
        confidence += 0.40

    # Local/global metadata
    if 'local' in metadata_str and 'global' in metadata_str:
        evidence.append("Local-global scope markers")
        confidence += 0.20

    # Synthesis keywords
    if any(kw in metadata_str for kw in ['synthesis', 'integration', 'coordination']):
        evidence.append("Synthesis/integration phase")
        confidence += 0.15

    # Structural pattern: diversity → unity
    if len(set(agent_sequence)) >= 3 and has_supervisor:
        evidence.append("Divide-and-conquer structure")
        confidence += 0.20

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence,
        metadata={'specialist_count': len(specialists)}
    )


# ===========================================================================
# HEURISTIC STRATEGY DETECTORS
# ===========================================================================

def detect_invariant_method(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Invariant Method pattern.

    Signals:
    - Invariant/symmetry keywords
    - Preserved quantities
    - Conservation laws

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Invariant keywords
    if any(kw in metadata_str for kw in ['invariant', 'preserved', 'conserved', 'constant']):
        evidence.append("Invariant/preservation keywords")
        confidence += 0.35

    # Symmetry/invariant agents
    if any('symmetry' in a or 'invariant' in a for a in sequence_lower):
        evidence.append("Symmetry/invariant specialist")
        confidence += 0.40

    # Explicit invariant detection
    if 'invariant_found' in metadata_str or 'preserved_quantity' in metadata_str:
        evidence.append("Explicit invariant identified")
        confidence += 0.30

    # Transformation analysis
    if any('transform' in a for a in sequence_lower):
        evidence.append("Transformation analysis")
        confidence += 0.15

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


def detect_extremal_elements(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Extremal Elements pattern.

    Signals:
    - Max/min computation
    - Optimization agents
    - Greedy algorithms

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Extremal keywords
    extremal_kw = ['extremal', 'maximum', 'minimum', 'optimal', 'greedy',
                   'maximal', 'minimal']
    if any(kw in metadata_str for kw in extremal_kw):
        evidence.append("Extremal/optimization keywords")
        confidence += 0.35

    # Optimization agents
    if any('optim' in a or 'extremal' in a or 'greedy' in a for a in sequence_lower):
        evidence.append("Optimization specialist")
        confidence += 0.40

    # Explicit extremal element
    if 'extremal_element' in metadata_str or 'optimization_applied' in metadata_str:
        evidence.append("Explicit extremal analysis")
        confidence += 0.30

    # Calculus-based extremal (derivatives)
    if any('calculus' in a or 'derivative' in a for a in sequence_lower):
        evidence.append("Calculus-based extremal analysis")
        confidence += 0.20

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


def detect_symmetrization(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Symmetrization pattern.

    Signals:
    - Symmetry exploitation
    - Group theory
    - Automorphisms

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Symmetry keywords
    if any(kw in metadata_str for kw in ['symmetric', 'symmetry', 'automorphism', 'group']):
        evidence.append("Symmetry keywords")
        confidence += 0.35

    # Symmetry/group agents
    if any('symmetry' in a or 'group' in a for a in sequence_lower):
        evidence.append("Symmetry/group theory specialist")
        confidence += 0.40

    # Geometry (often symmetry-related)
    if any('geom' in a for a in sequence_lower):
        evidence.append("Geometric analysis")
        confidence += 0.15

    # Explicit symmetrization
    if 'symmetry_detected' in metadata_str or 'symmetrization_applied' in metadata_str:
        evidence.append("Explicit symmetrization")
        confidence += 0.30

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


def detect_functional_viewpoint(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Functional Viewpoint pattern.

    Signals:
    - Generating functions
    - Functional equations
    - Operator methods

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Functional keywords
    if any(kw in metadata_str for kw in ['generating function', 'functional', 'operator']):
        evidence.append("Functional encoding keywords")
        confidence += 0.35

    # Functional analysis agents
    if any('functional' in a or 'generating' in a for a in sequence_lower):
        evidence.append("Functional analysis specialist")
        confidence += 0.40

    # Explicit functional encoding
    if 'encoding_functional' in metadata_str or 'generating_function_used' in metadata_str:
        evidence.append("Explicit functional encoding")
        confidence += 0.30

    # Recurrence/series
    if any('recurrence' in a or 'series' in a for a in sequence_lower):
        evidence.append("Recurrence/series analysis")
        confidence += 0.20

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


# ===========================================================================
# NONSTANDARD STRATEGY DETECTORS
# ===========================================================================

def detect_infinite_descent(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Infinite Descent pattern.

    Signals:
    - Contradiction proofs
    - Minimal element construction
    - Well-ordering principle

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Descent keywords
    if any(kw in metadata_str for kw in ['descent', 'minimal', 'contradiction', 'least']):
        evidence.append("Descent/minimality keywords")
        confidence += 0.35

    # Proof method
    if 'proof_method=contradiction' in metadata_str or 'proof_by_contradiction' in metadata_str:
        evidence.append("Proof by contradiction")
        confidence += 0.30

    # Number theory context
    if any('number' in a or 'diophantine' in a for a in sequence_lower):
        evidence.append("Number theory context")
        confidence += 0.20

    # Explicit descent
    if 'descent_applied' in metadata_str or 'infinite_descent' in metadata_str:
        evidence.append("Explicit infinite descent")
        confidence += 0.40

    # Induction (related)
    if any('induction' in a for a in sequence_lower):
        evidence.append("Inductive reasoning")
        confidence += 0.15

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


def detect_graphical_revisualization(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Graphical Revisualization pattern.

    Signals:
    - Graph encoding
    - Network visualization
    - Vertex/edge construction

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Graph keywords
    if any(kw in metadata_str for kw in ['graph', 'vertex', 'edge', 'network', 'node']):
        evidence.append("Graph-theoretic keywords")
        confidence += 0.35

    # Graph theory agents
    if any('graph' in a or 'network' in a for a in sequence_lower):
        evidence.append("Graph theory specialist")
        confidence += 0.40

    # Discrete math context
    if any('discrete' in a or 'combinatorial' in a for a in sequence_lower):
        evidence.append("Discrete/combinatorial context")
        confidence += 0.15

    # Explicit graph encoding
    if 'graph_encoding' in metadata_str or 'visualization_added' in metadata_str:
        evidence.append("Explicit graph encoding")
        confidence += 0.35

    # Non-graph problem encoded as graph
    problem_type = metadata.get('problem_type', '').lower()
    if problem_type and 'graph' not in problem_type:
        if any(kw in metadata_str for kw in ['graph', 'vertex', 'edge']):
            evidence.append("Non-graph problem encoded as graph")
            confidence += 0.25

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


def detect_fixed_point(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Fixed-Point Method pattern.

    Signals:
    - Fixed-point theorems (Banach, Brouwer)
    - Contraction mappings
    - Iterative convergence

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Fixed-point keywords
    if any(kw in metadata_str for kw in ['fixed point', 'banach', 'brouwer', 'contraction']):
        evidence.append("Fixed-point theorem keywords")
        confidence += 0.40

    # Functional analysis agents
    if any('functional' in a or 'analysis' in a for a in sequence_lower):
        evidence.append("Functional analysis specialist")
        confidence += 0.30

    # Iteration/convergence
    if any(kw in metadata_str for kw in ['iteration', 'convergence', 'limit']):
        evidence.append("Iterative convergence analysis")
        confidence += 0.20

    # Explicit fixed-point
    if 'fixed_point_theorem' in metadata_str or 'iteration_applied' in metadata_str:
        evidence.append("Explicit fixed-point application")
        confidence += 0.35

    # Differential equations (common application)
    if any('differential' in a or 'ode' in a or 'pde' in a for a in sequence_lower):
        evidence.append("Differential equation context")
        confidence += 0.15

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


# ===========================================================================
# META STRATEGY DETECTORS
# ===========================================================================

def detect_template_mining(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Template Mining pattern.

    Signals:
    - Similar problem retrieval
    - Analogy-based reasoning
    - Pattern matching

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Template keywords
    if any(kw in metadata_str for kw in ['similar', 'template', 'pattern', 'analogy']):
        evidence.append("Template/analogy keywords")
        confidence += 0.35

    # Retrieval/pattern agents
    if any('retrieval' in a or 'pattern' in a or 'indexer' in a for a in sequence_lower):
        evidence.append("Pattern retrieval specialist")
        confidence += 0.40

    # Explicit template match
    if 'similar_problems_found' in metadata_str or 'template_match' in metadata_str:
        evidence.append("Explicit template match")
        confidence += 0.40

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence
    )


def detect_multi_solution_synthesis(agent_sequence: List[str], metadata: Dict) -> DetectorResult:
    """
    Detect Multi-Solution Synthesis pattern.

    Signals:
    - Multiple verification passes
    - Alternative solution paths
    - Solution comparison

    Returns:
        DetectorResult with confidence and evidence
    """
    evidence = []
    confidence = 0.0

    sequence_lower = [a.lower() for a in agent_sequence]
    metadata_str = str(metadata).lower()

    # Solution count
    solution_count = metadata.get('solution_count', 1)
    if solution_count > 1:
        evidence.append(f"Multiple solutions ({solution_count})")
        confidence += 0.50

    # Synthesis keywords
    if any(kw in metadata_str for kw in ['alternative', 'comparison', 'synthesis', 'multiple']):
        evidence.append("Multi-solution keywords")
        confidence += 0.30

    # Multiple verification
    verification_count = sum(1 for a in sequence_lower if 'verif' in a or 'ax_prover' in a)
    if verification_count > 1:
        evidence.append(f"Multiple verification passes ({verification_count})")
        confidence += 0.20

    return DetectorResult(
        confidence=min(confidence, 1.0),
        evidence=evidence,
        metadata={'solution_count': solution_count}
    )


# ===========================================================================
# COMPREHENSIVE DETECTION
# ===========================================================================

def detect_all_strategies(agent_sequence: List[str],
                         metadata: Dict,
                         min_confidence: float = 0.3) -> Dict[str, DetectorResult]:
    """
    Run all strategy detectors on a trace.

    Args:
        agent_sequence: Ordered list of agents invoked
        metadata: Trace metadata
        min_confidence: Minimum confidence threshold for inclusion

    Returns:
        Dict mapping strategy names to DetectorResults
    """
    detectors = {
        'polya_cycle': detect_polya_cycle,
        'problem_re_encoding': detect_problem_re_encoding,
        'local_global': detect_local_global,
        'invariant_method': detect_invariant_method,
        'extremal_elements': detect_extremal_elements,
        'symmetrization': detect_symmetrization,
        'functional_viewpoint': detect_functional_viewpoint,
        'infinite_descent': detect_infinite_descent,
        'graphical_revisualization': detect_graphical_revisualization,
        'fixed_point': detect_fixed_point,
        'template_mining': detect_template_mining,
        'multi_solution_synthesis': detect_multi_solution_synthesis
    }

    results = {}
    for name, detector in detectors.items():
        result = detector(agent_sequence, metadata)
        if result.confidence >= min_confidence:
            results[name] = result

    return results


if __name__ == "__main__":
    """Test strategy detectors"""
    print("=" * 80)
    print("STRATEGY DETECTORS TEST")
    print("=" * 80)
    print()

    # Test trace with multiple strategies
    test_trace = {
        'agent_sequence': [
            'structure_recognizer_001',
            'decomposition_agent_001',
            'symmetry_specialist_001',
            'optimization_agent_001',
            'ax_prover_001'
        ],
        'metadata': {
            'problem_reformulated': True,
            'decompose': True,
            'symmetry_detected': True,
            'extremal_element': 'maximum',
            'optimization_applied': True,
            'retrospective_check': True
        }
    }

    print("Analyzing trace...")
    print(f"Agent sequence: {len(test_trace['agent_sequence'])} agents")
    print()

    # Run all detectors
    results = detect_all_strategies(
        test_trace['agent_sequence'],
        test_trace['metadata'],
        min_confidence=0.3
    )

    print(f"Detected {len(results)} strategies:")
    print("-" * 80)

    # Sort by confidence
    sorted_results = sorted(results.items(), key=lambda x: x[1].confidence, reverse=True)

    for strategy_name, result in sorted_results:
        print(f"\n{strategy_name.replace('_', ' ').title()}:")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Evidence:")
        for ev in result.evidence:
            print(f"    - {ev}")

    print()
    print("=" * 80)
    print("STRATEGY DETECTORS TEST COMPLETE")
    print("=" * 80)
