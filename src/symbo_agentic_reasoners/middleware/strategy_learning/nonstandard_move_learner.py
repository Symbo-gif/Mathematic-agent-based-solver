# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
NonStandard Move Learner (Agent 3.6)
=====================================

PURPOSE:
--------
Detects unconventional problem-solving techniques in solution traces.
Focuses on creative, non-obvious moves that break conventional approaches.

NONSTANDARD PATTERNS DETECTED:
-------------------------------
1. Infinite Descent: Proof by contradiction using well-ordering principle
2. Graphical Revisualization: Encoding problems as graph-theoretic structures
3. Fixed-Point Theorems: Using Banach, Brouwer, or other fixed-point methods

DETECTION METHOD:
-----------------
Analyzes proof methods, domain encodings, and specialized technique invocations
to identify creative problem transformations.

REFERENCE:
----------
Phase_4_Build_Order_Breakdown.md: Agent 3.6
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import uuid

from .strategy_patterns import (
    StrategyPattern, StrategyDetectionResult, StrategyDetection,
    StrategyCategory, get_strategy_keywords, StrategyApplication
)

logger = logging.getLogger('symbo_agentic_reasoners.strategy_learning.nonstandard')


class NonStandardMoveLearner:
    """
    Agent 3.6: NonStandard Move Learner

    DIRECTIVE:
    ---------
    Monitor solution traces and detect unconventional techniques that
    represent creative problem-solving approaches. Focus on methods
    that are powerful but not immediately obvious.

    DETECTED PATTERNS:
    -----------------
    - Infinite Descent: Well-ordering contradiction proofs
    - Graphical Revisualization: Graph encoding of problems
    - Fixed-Point Theorems: Banach, Brouwer, Schauder applications

    OUTPUT:
    -------
    Posts StrategyDetection to Blackboard with detected nonstandard patterns
    and confidence scores.
    """

    def __init__(self, blackboard=None, knowledge_graph=None):
        """
        Initialize NonStandard Move Learner

        Args:
            blackboard: Phase 0 Blackboard for event subscription
            knowledge_graph: KnowledgeGraph for strategy persistence
        """
        self.blackboard = blackboard
        self.knowledge_graph = knowledge_graph
        self._lock = threading.RLock()

        # Strategy library
        self.nonstandard_strategies: Dict[str, StrategyPattern] = {}

        # Detection statistics
        self.traces_analyzed = 0
        self.detections_made = 0
        self.high_confidence_detections = 0

        # Initialize strategy library
        self._bootstrap_strategy_library()

        # Subscribe to events
        if self.blackboard:
            self._subscribe_to_events()

        print("    [OK] NonStandard Move Learner (Agent 3.6) initialized")

    def _bootstrap_strategy_library(self):
        """Initialize nonstandard strategy patterns."""
        # Infinite Descent
        self.nonstandard_strategies['infinite_descent'] = StrategyPattern(
            pattern_id='strategy_infinite_descent',
            name='Infinite Descent',
            category=StrategyCategory.NONSTANDARD,
            description='Proof by contradiction using well-ordering of naturals',
            abstract_description='Construct infinite descending sequence to reach contradiction',
            detection_signals=[
                'descent keyword in metadata',
                'contradiction proof method',
                'minimal element construction',
                'well-ordering principle'
            ],
            applicability_conditions=[
                'number theory problems',
                'existence/non-existence proofs',
                'Diophantine equations'
            ],
            composition_compatible=['extremal_elements', 'polya_cycle']
        )

        # Graphical Revisualization
        self.nonstandard_strategies['graphical_revisualization'] = StrategyPattern(
            pattern_id='strategy_graphical_revisualization',
            name='Graphical Revisualization',
            category=StrategyCategory.NONSTANDARD,
            description='Re-encode problem as graph-theoretic structure',
            abstract_description='Leverage graph properties to solve non-graph problems',
            detection_signals=[
                'graph encoding in metadata',
                'graph theory agent invoked',
                'vertex/edge construction',
                'network visualization'
            ],
            applicability_conditions=[
                'combinatorial problems',
                'relation-based problems',
                'connectivity problems'
            ],
            composition_compatible=['problem_re_encoding', 'symmetrization']
        )

        # Fixed-Point Theorems
        self.nonstandard_strategies['fixed_point'] = StrategyPattern(
            pattern_id='strategy_fixed_point',
            name='Fixed-Point Method',
            category=StrategyCategory.NONSTANDARD,
            description='Use fixed-point theorems (Banach, Brouwer, Schauder)',
            abstract_description='Transform existence proof into fixed-point problem',
            detection_signals=[
                'fixed point keyword',
                'banach/brouwer theorem',
                'contraction mapping',
                'iteration convergence'
            ],
            applicability_conditions=[
                'existence proofs',
                'differential equations',
                'iterative methods'
            ],
            composition_compatible=['functional_viewpoint', 'extremal_elements']
        )

    def _subscribe_to_events(self):
        """Subscribe to SOLUTION_TRACE events from Blackboard."""
        try:
            self.blackboard.subscribe(
                agent_id='nonstandard_move_learner_001',
                tags=['SOLUTION_TRACE'],
                callback=self._on_solution_trace
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to traces: {type(e).__name__}: {e}")

    def _on_solution_trace(self, entry):
        """Handle new solution trace from Blackboard."""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            trace_dict = entry.content
            detection = self.analyze_trace(trace_dict)

            if detection and detection.detected_strategies:
                # Post detection to Blackboard
                self._post_detection(detection)

    def analyze_trace(self, trace: Dict) -> Optional[StrategyDetection]:
        """
        Analyze solution trace for nonstandard patterns.

        Args:
            trace: SolutionTrace dictionary

        Returns:
            StrategyDetection with detected patterns, or None
        """
        with self._lock:
            self.traces_analyzed += 1

        trace_id = trace.get('trace_id', 'unknown')
        conversation_id = trace.get('conversation_id', 'unknown')
        agent_sequence = trace.get('agent_sequence', [])
        metadata = trace.get('metadata', {})
        success = trace.get('success', False)

        detected_strategies = []

        # Detect Infinite Descent
        descent_result = self._detect_infinite_descent(agent_sequence, metadata)
        if descent_result:
            detected_strategies.append(descent_result)

        # Detect Graphical Revisualization
        graphical_result = self._detect_graphical_revisualization(agent_sequence, metadata)
        if graphical_result:
            detected_strategies.append(graphical_result)

        # Detect Fixed-Point
        fixed_point_result = self._detect_fixed_point(agent_sequence, metadata)
        if fixed_point_result:
            detected_strategies.append(fixed_point_result)

        if detected_strategies:
            with self._lock:
                self.detections_made += len(detected_strategies)
                self.high_confidence_detections += sum(
                    1 for d in detected_strategies if d.confidence >= 0.7
                )

            # Update strategy statistics
            self._update_strategy_stats(detected_strategies, trace)

            return StrategyDetection(
                trace_id=trace_id,
                conversation_id=conversation_id,
                detected_strategies=detected_strategies,
                detector_agent='nonstandard_move_learner_001'
            )

        return None

    def _detect_infinite_descent(self, agent_sequence: List[str],
                                 metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Infinite Descent pattern.

        Signals:
        - Descent/minimal keywords
        - Contradiction proof method
        - Well-ordering principle
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for descent keywords
        descent_keywords = ['descent', 'minimal', 'well-ordered', 'contradiction',
                           'least', 'smallest']
        if any(kw in metadata_str for kw in descent_keywords):
            evidence.append("Descent/minimality keywords in metadata")
            confidence += 0.35

        # Check for proof method
        if 'proof_method=contradiction' in metadata_str or 'proof_by_contradiction' in metadata_str:
            evidence.append("Proof by contradiction method")
            confidence += 0.30

        # Check for number theory agents (common domain for descent)
        if any('number' in a or 'diophantine' in a for a in sequence_lower):
            evidence.append("Number theory context (descent-compatible)")
            confidence += 0.20

        # Check for explicit descent detection
        if 'descent_applied' in metadata_str or 'infinite_descent' in metadata_str:
            evidence.append("Explicit infinite descent applied")
            confidence += 0.40

        # Check for induction/recursion (related to descent)
        if any('induction' in a or 'recursion' in a for a in sequence_lower):
            evidence.append("Inductive/recursive reasoning")
            confidence += 0.15

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_infinite_descent',
                strategy_name='Infinite Descent',
                category=StrategyCategory.NONSTANDARD,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_graphical_revisualization(self, agent_sequence: List[str],
                                         metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Graphical Revisualization pattern.

        Signals:
        - Graph encoding keywords
        - Graph theory agents
        - Vertex/edge construction
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for graph keywords
        graph_keywords = ['graph', 'vertex', 'edge', 'network', 'node',
                         'connectivity', 'path', 'cycle']
        if any(kw in metadata_str for kw in graph_keywords):
            evidence.append("Graph-theoretic keywords in metadata")
            confidence += 0.35

        # Check for graph theory agents
        if any('graph' in a or 'network' in a for a in sequence_lower):
            evidence.append("Graph theory specialist invoked")
            confidence += 0.40

        # Check for discrete math agents
        if any('discrete' in a or 'combinatorial' in a for a in sequence_lower):
            evidence.append("Discrete/combinatorial context")
            confidence += 0.15

        # Check for explicit graph encoding
        if 'graph_encoding' in metadata_str or 'visualization_added' in metadata_str:
            evidence.append("Explicit graph encoding applied")
            confidence += 0.35

        # Check for problem type (non-graph problem encoded as graph)
        problem_type = metadata.get('problem_type', '').lower()
        if problem_type and 'graph' not in problem_type:
            if any(kw in metadata_str for kw in graph_keywords):
                evidence.append("Non-graph problem encoded as graph")
                confidence += 0.25

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_graphical_revisualization',
                strategy_name='Graphical Revisualization',
                category=StrategyCategory.NONSTANDARD,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_fixed_point(self, agent_sequence: List[str],
                           metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Fixed-Point Method pattern.

        Signals:
        - Fixed point keywords
        - Banach/Brouwer theorem references
        - Contraction mapping
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for fixed point keywords
        fp_keywords = ['fixed point', 'fixpoint', 'banach', 'brouwer',
                      'contraction', 'schauder', 'kakutani']
        if any(kw in metadata_str for kw in fp_keywords):
            evidence.append("Fixed-point theorem keywords in metadata")
            confidence += 0.40

        # Check for functional analysis agents
        if any('functional' in a or 'analysis' in a for a in sequence_lower):
            evidence.append("Functional analysis specialist invoked")
            confidence += 0.30

        # Check for iteration/convergence
        iteration_keywords = ['iteration', 'convergence', 'limit', 'sequence']
        if any(kw in metadata_str for kw in iteration_keywords):
            evidence.append("Iterative convergence analysis")
            confidence += 0.20

        # Check for explicit fixed point application
        if 'fixed_point_theorem' in metadata_str or 'iteration_applied' in metadata_str:
            evidence.append("Explicit fixed-point theorem application")
            confidence += 0.35

        # Check for differential equation context (common for fixed point)
        if any('differential' in a or 'ode' in a or 'pde' in a for a in sequence_lower):
            evidence.append("Differential equation context (fixed-point compatible)")
            confidence += 0.15

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_fixed_point',
                strategy_name='Fixed-Point Method',
                category=StrategyCategory.NONSTANDARD,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _update_strategy_stats(self, detections: List[StrategyDetectionResult],
                               trace: Dict):
        """Update strategy effectiveness statistics."""
        problem_type = trace.get('problem_type', 'unknown')
        success = trace.get('success', False)

        for detection in detections:
            strategy_id = detection.strategy_id.replace('strategy_', '')
            if strategy_id in self.nonstandard_strategies:
                strategy = self.nonstandard_strategies[strategy_id]
                strategy.add_application(success, problem_type)

                # Store in KnowledgeGraph if available
                if self.knowledge_graph and hasattr(self.knowledge_graph, 'record_strategy_application'):
                    app = StrategyApplication(
                        application_id=f"app_{uuid.uuid4().hex[:8]}",
                        strategy_id=detection.strategy_id,
                        trace_id=trace.get('trace_id', 'unknown'),
                        conversation_id=trace.get('conversation_id', 'unknown'),
                        problem_type=problem_type,
                        domain=problem_type,
                        success=success,
                        time_ms=trace.get('time_taken_ms', 0),
                        detection_confidence=detection.confidence
                    )
                    try:
                        self.knowledge_graph.record_strategy_application(app)
                    except Exception as e:
                        logger.debug(f"Could not record strategy application: {type(e).__name__}: {e}")

    def _post_detection(self, detection: StrategyDetection):
        """Post detection to Blackboard."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

            entry = create_entry(
                entry_type=EntryType.OBSERVATION,
                content={
                    'detection_type': 'NONSTANDARD_STRATEGY',
                    'trace_id': detection.trace_id,
                    'conversation_id': detection.conversation_id,
                    'strategies': [
                        {
                            'strategy_id': s.strategy_id,
                            'strategy_name': s.strategy_name,
                            'category': s.category.value,
                            'confidence': s.confidence,
                            'evidence': s.evidence
                        }
                        for s in detection.detected_strategies
                    ]
                },
                author_agent='nonstandard_move_learner_001',
                conversation_id=detection.conversation_id,
                tags=['STRATEGY_DETECTION', 'NONSTANDARD', detection.trace_id],
                metadata={
                    'detector': 'nonstandard_move_learner',
                    'detection_count': len(detection.detected_strategies)
                }
            )

            self.blackboard.post(entry)

        except Exception as e:
            logger.debug(f"Could not post detection to blackboard: {type(e).__name__}: {e}")

    def get_strategy_effectiveness(self, strategy_name: str) -> Dict[str, Any]:
        """
        Get effectiveness metrics for a strategy.

        Args:
            strategy_name: Strategy identifier (e.g., 'infinite_descent')

        Returns:
            Dict with success_rate, applications, domain_effectiveness
        """
        if strategy_name not in self.nonstandard_strategies:
            return {}

        strategy = self.nonstandard_strategies[strategy_name]
        return {
            'name': strategy.name,
            'success_rate': strategy.success_rate,
            'total_applications': strategy.total_applications,
            'success_count': strategy.success_count,
            'domains_effective': strategy.domains_effective
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get learner statistics."""
        return {
            'traces_analyzed': self.traces_analyzed,
            'detections_made': self.detections_made,
            'high_confidence_detections': self.high_confidence_detections,
            'detection_rate': (self.detections_made / max(1, self.traces_analyzed)),
            'strategies_tracked': len(self.nonstandard_strategies)
        }


if __name__ == "__main__":
    """Test NonStandard Move Learner"""
    print("=" * 80)
    print("NONSTANDARD MOVE LEARNER TEST")
    print("=" * 80)
    print()

    # Initialize learner
    learner = NonStandardMoveLearner()
    print()

    # Test trace 1: Infinite Descent
    print("Test 1: Infinite Descent Detection")
    print("-" * 40)
    trace1 = {
        'trace_id': 'trace_001',
        'conversation_id': 'conv_001',
        'problem_type': 'number_theory',
        'agent_sequence': [
            'number_theory_specialist_001',
            'contradiction_prover_001',
            'induction_agent_001'
        ],
        'success': True,
        'time_taken_ms': 1400,
        'metadata': {
            'proof_method': 'contradiction',
            'descent_applied': True,
            'minimal_element': 'constructed',
            'well_ordering': True
        }
    }

    detection1 = learner.analyze_trace(trace1)
    if detection1:
        print(f"Detected {len(detection1.detected_strategies)} strategies:")
        for s in detection1.detected_strategies:
            print(f"  - {s.strategy_name}: {s.confidence:.2%} confidence")
            print(f"    Evidence: {', '.join(s.evidence)}")
    else:
        print("No strategies detected")
    print()

    # Test trace 2: Graphical Revisualization
    print("Test 2: Graphical Revisualization Detection")
    print("-" * 40)
    trace2 = {
        'trace_id': 'trace_002',
        'conversation_id': 'conv_002',
        'problem_type': 'combinatorics',
        'agent_sequence': [
            'combinatorial_agent_001',
            'graph_theory_specialist_001',
            'discrete_math_001'
        ],
        'success': True,
        'time_taken_ms': 1050,
        'metadata': {
            'graph_encoding': 'bipartite',
            'visualization_added': True,
            'vertices': 'states',
            'edges': 'transitions'
        }
    }

    detection2 = learner.analyze_trace(trace2)
    if detection2:
        print(f"Detected {len(detection2.detected_strategies)} strategies:")
        for s in detection2.detected_strategies:
            print(f"  - {s.strategy_name}: {s.confidence:.2%} confidence")
            print(f"    Evidence: {', '.join(s.evidence)}")
    else:
        print("No strategies detected")
    print()

    # Test trace 3: Fixed-Point Method
    print("Test 3: Fixed-Point Method Detection")
    print("-" * 40)
    trace3 = {
        'trace_id': 'trace_003',
        'conversation_id': 'conv_003',
        'problem_type': 'differential_equations',
        'agent_sequence': [
            'functional_analysis_001',
            'differential_equation_solver_001',
            'convergence_analyzer_001'
        ],
        'success': True,
        'time_taken_ms': 1600,
        'metadata': {
            'fixed_point_theorem': 'banach',
            'iteration_applied': True,
            'convergence': 'proven',
            'contraction_constant': 0.8
        }
    }

    detection3 = learner.analyze_trace(trace3)
    if detection3:
        print(f"Detected {len(detection3.detected_strategies)} strategies:")
        for s in detection3.detected_strategies:
            print(f"  - {s.strategy_name}: {s.confidence:.2%} confidence")
            print(f"    Evidence: {', '.join(s.evidence)}")
    else:
        print("No strategies detected")
    print()

    # Show statistics
    print("LEARNER STATISTICS:")
    print("-" * 40)
    stats = learner.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Show strategy effectiveness
    print("STRATEGY EFFECTIVENESS:")
    print("-" * 40)
    for strategy_name in ['infinite_descent', 'graphical_revisualization', 'fixed_point']:
        eff = learner.get_strategy_effectiveness(strategy_name)
        if eff:
            print(f"  {eff['name']}:")
            print(f"    Success Rate: {eff['success_rate']:.2%}")
            print(f"    Applications: {eff['total_applications']}")

    print()
    print("=" * 80)
    print("NONSTANDARD MOVE LEARNER TEST COMPLETE")
    print("=" * 80)
