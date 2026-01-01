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
Heuristic Pattern Learner (Agent 3.5)
======================================

PURPOSE:
--------
Detects deep mathematical heuristics in problem-solving traces.
Focuses on domain-specific techniques that exploit mathematical structure.

HEURISTIC PATTERNS DETECTED:
-----------------------------
1. Invariant Method: Finding preserved quantities under transformations
2. Extremal Elements: Using maximal/minimal elements to guide construction
3. Symmetrization: Exploiting symmetry to simplify problems
4. Functional Viewpoint: Using generating functions or functional equations

DETECTION METHOD:
-----------------
Analyzes mathematical transformations, agent specializations, and metadata
to identify characteristic signatures of each heuristic pattern.

REFERENCE:
----------
Phase_4_Build_Order_Breakdown.md: Agent 3.5
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

logger = logging.getLogger('symbo_agentic_reasoners.strategy_learning.heuristic')


class HeuristicPatternLearner:
    """
    Agent 3.5: Heuristic Pattern Learner

    DIRECTIVE:
    ---------
    Monitor solution traces and detect deep mathematical heuristics that
    exploit problem structure. Focus on domain-specific techniques rather
    than general coordination patterns.

    DETECTED PATTERNS:
    -----------------
    - Invariant Method: Preserved quantities
    - Extremal Elements: Min/max based construction
    - Symmetrization: Symmetry exploitation
    - Functional Viewpoint: Generating functions and operators

    OUTPUT:
    -------
    Posts StrategyDetection to Blackboard with detected heuristic patterns
    and confidence scores.
    """

    def __init__(self, blackboard=None, knowledge_graph=None):
        """
        Initialize Heuristic Pattern Learner

        Args:
            blackboard: Phase 0 Blackboard for event subscription
            knowledge_graph: KnowledgeGraph for strategy persistence
        """
        self.blackboard = blackboard
        self.knowledge_graph = knowledge_graph
        self._lock = threading.RLock()

        # Strategy library
        self.heuristic_strategies: Dict[str, StrategyPattern] = {}

        # Detection statistics
        self.traces_analyzed = 0
        self.detections_made = 0
        self.high_confidence_detections = 0

        # Initialize strategy library
        self._bootstrap_strategy_library()

        # Subscribe to events
        if self.blackboard:
            self._subscribe_to_events()

        print("    [OK] Heuristic Pattern Learner (Agent 3.5) initialized")

    def _bootstrap_strategy_library(self):
        """Initialize heuristic strategy patterns."""
        # Invariant Method
        self.heuristic_strategies['invariant_method'] = StrategyPattern(
            pattern_id='strategy_invariant_method',
            name='Invariant Method',
            category=StrategyCategory.HEURISTIC,
            description='Find quantities preserved under problem transformations',
            abstract_description='Identify invariant structure to simplify analysis',
            detection_signals=[
                'invariant keyword in metadata',
                'symmetry specialist invoked',
                'conserved quantity identified',
                'transformation-preserving property'
            ],
            applicability_conditions=[
                'problems with symmetry',
                'iterative or recursive structures',
                'transformation-based problems'
            ],
            composition_compatible=['symmetrization', 'polya_cycle']
        )

        # Extremal Elements
        self.heuristic_strategies['extremal_elements'] = StrategyPattern(
            pattern_id='strategy_extremal_elements',
            name='Extremal Elements',
            category=StrategyCategory.HEURISTIC,
            description='Use maximal/minimal elements to guide construction or proof',
            abstract_description='Leverage extreme cases to constrain possibilities',
            detection_signals=[
                'extremal keyword in metadata',
                'optimization agent invoked',
                'maximum/minimum computed',
                'greedy algorithm applied'
            ],
            applicability_conditions=[
                'optimization problems',
                'existence proofs',
                'combinatorial problems'
            ],
            composition_compatible=['local_global', 'invariant_method']
        )

        # Symmetrization
        self.heuristic_strategies['symmetrization'] = StrategyPattern(
            pattern_id='strategy_symmetrization',
            name='Symmetrization',
            category=StrategyCategory.HEURISTIC,
            description='Exploit or impose symmetry to reduce problem complexity',
            abstract_description='Use symmetry to eliminate degrees of freedom',
            detection_signals=[
                'symmetry keyword in metadata',
                'group theory agent invoked',
                'automorphism detected',
                'averaging over symmetry group'
            ],
            applicability_conditions=[
                'problems with inherent symmetry',
                'geometric problems',
                'group-theoretic structures'
            ],
            composition_compatible=['invariant_method', 'local_global']
        )

        # Functional Viewpoint
        self.heuristic_strategies['functional_viewpoint'] = StrategyPattern(
            pattern_id='strategy_functional_viewpoint',
            name='Functional Viewpoint',
            category=StrategyCategory.HEURISTIC,
            description='Use generating functions, functional equations, or operators',
            abstract_description='Encode sequences/problems as functions for algebraic manipulation',
            detection_signals=[
                'generating function keyword',
                'functional analysis agent',
                'operator encoding',
                'recurrence relation'
            ],
            applicability_conditions=[
                'combinatorial enumeration',
                'sequence problems',
                'recurrence relations'
            ],
            composition_compatible=['problem_re_encoding', 'algebraic_manipulation']
        )

    def _subscribe_to_events(self):
        """Subscribe to SOLUTION_TRACE events from Blackboard."""
        try:
            self.blackboard.subscribe(
                agent_id='heuristic_pattern_learner_001',
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
        Analyze solution trace for heuristic patterns.

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

        # Detect Invariant Method
        invariant_result = self._detect_invariant_method(agent_sequence, metadata)
        if invariant_result:
            detected_strategies.append(invariant_result)

        # Detect Extremal Elements
        extremal_result = self._detect_extremal_elements(agent_sequence, metadata)
        if extremal_result:
            detected_strategies.append(extremal_result)

        # Detect Symmetrization
        symmetry_result = self._detect_symmetrization(agent_sequence, metadata)
        if symmetry_result:
            detected_strategies.append(symmetry_result)

        # Detect Functional Viewpoint
        functional_result = self._detect_functional_viewpoint(agent_sequence, metadata)
        if functional_result:
            detected_strategies.append(functional_result)

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
                detector_agent='heuristic_pattern_learner_001'
            )

        return None

    def _detect_invariant_method(self, agent_sequence: List[str],
                                 metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Invariant Method pattern.

        Signals:
        - Invariant/symmetry keywords
        - Conserved quantity agents
        - Preservation properties in metadata
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for invariant keywords
        invariant_keywords = ['invariant', 'preserved', 'conserved', 'unchanged', 'constant']
        if any(kw in metadata_str for kw in invariant_keywords):
            evidence.append("Invariant/preservation keywords in metadata")
            confidence += 0.35

        # Check for symmetry agents
        if any('symmetry' in a or 'invariant' in a for a in sequence_lower):
            evidence.append("Symmetry/invariant specialist invoked")
            confidence += 0.40

        # Check for explicit invariant detection
        if 'invariant_found' in metadata_str or 'preserved_quantity' in metadata_str:
            evidence.append("Explicit invariant identified")
            confidence += 0.30

        # Check for transformation-related agents
        if any('transform' in a for a in sequence_lower):
            evidence.append("Transformation analysis performed")
            confidence += 0.15

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_invariant_method',
                strategy_name='Invariant Method',
                category=StrategyCategory.HEURISTIC,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_extremal_elements(self, agent_sequence: List[str],
                                  metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Extremal Elements pattern.

        Signals:
        - Extremal/optimization keywords
        - Max/min computation
        - Greedy algorithms
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for extremal keywords
        extremal_keywords = ['extremal', 'maximum', 'minimum', 'optimal', 'greedy',
                             'maximal', 'minimal', 'sup', 'inf']
        if any(kw in metadata_str for kw in extremal_keywords):
            evidence.append("Extremal/optimization keywords in metadata")
            confidence += 0.35

        # Check for optimization agents
        if any('optim' in a or 'extremal' in a or 'greedy' in a for a in sequence_lower):
            evidence.append("Optimization specialist invoked")
            confidence += 0.40

        # Check for explicit extremal element detection
        if 'extremal_element' in metadata_str or 'optimization_applied' in metadata_str:
            evidence.append("Explicit extremal analysis")
            confidence += 0.30

        # Check for calculus agents (often used for extremal problems)
        if any('calculus' in a or 'derivative' in a for a in sequence_lower):
            evidence.append("Calculus-based extremal analysis")
            confidence += 0.20

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_extremal_elements',
                strategy_name='Extremal Elements',
                category=StrategyCategory.HEURISTIC,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_symmetrization(self, agent_sequence: List[str],
                              metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Symmetrization pattern.

        Signals:
        - Symmetry keywords
        - Group theory agents
        - Automorphism detection
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for symmetry keywords
        symmetry_keywords = ['symmetric', 'symmetry', 'automorphism', 'group',
                            'averaging', 'equivariant', 'conjugate']
        if any(kw in metadata_str for kw in symmetry_keywords):
            evidence.append("Symmetry keywords in metadata")
            confidence += 0.35

        # Check for symmetry/group theory agents
        if any('symmetry' in a or 'group' in a for a in sequence_lower):
            evidence.append("Symmetry/group theory specialist invoked")
            confidence += 0.40

        # Check for geometry agents (often involve symmetry)
        if any('geom' in a for a in sequence_lower):
            evidence.append("Geometric analysis (symmetry-adjacent)")
            confidence += 0.15

        # Check for explicit symmetry detection
        if 'symmetry_detected' in metadata_str or 'symmetrization_applied' in metadata_str:
            evidence.append("Explicit symmetrization applied")
            confidence += 0.30

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_symmetrization',
                strategy_name='Symmetrization',
                category=StrategyCategory.HEURISTIC,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_functional_viewpoint(self, agent_sequence: List[str],
                                     metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Functional Viewpoint pattern.

        Signals:
        - Generating function keywords
        - Functional analysis agents
        - Recurrence relation handling
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for functional keywords
        functional_keywords = ['generating function', 'functional', 'operator',
                              'recurrence', 'series', 'transform']
        if any(kw in metadata_str for kw in functional_keywords):
            evidence.append("Functional encoding keywords in metadata")
            confidence += 0.35

        # Check for functional analysis agents
        if any('functional' in a or 'generating' in a for a in sequence_lower):
            evidence.append("Functional analysis specialist invoked")
            confidence += 0.40

        # Check for explicit functional encoding
        if 'encoding_functional' in metadata_str or 'generating_function_used' in metadata_str:
            evidence.append("Explicit functional encoding applied")
            confidence += 0.30

        # Check for recurrence/series agents
        if any('recurrence' in a or 'series' in a for a in sequence_lower):
            evidence.append("Recurrence/series analysis")
            confidence += 0.20

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_functional_viewpoint',
                strategy_name='Functional Viewpoint',
                category=StrategyCategory.HEURISTIC,
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
            if strategy_id in self.heuristic_strategies:
                strategy = self.heuristic_strategies[strategy_id]
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
                    'detection_type': 'HEURISTIC_STRATEGY',
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
                author_agent='heuristic_pattern_learner_001',
                conversation_id=detection.conversation_id,
                tags=['STRATEGY_DETECTION', 'HEURISTIC', detection.trace_id],
                metadata={
                    'detector': 'heuristic_pattern_learner',
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
            strategy_name: Strategy identifier (e.g., 'invariant_method')

        Returns:
            Dict with success_rate, applications, domain_effectiveness
        """
        if strategy_name not in self.heuristic_strategies:
            return {}

        strategy = self.heuristic_strategies[strategy_name]
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
            'strategies_tracked': len(self.heuristic_strategies)
        }


if __name__ == "__main__":
    """Test Heuristic Pattern Learner"""
    print("=" * 80)
    print("HEURISTIC PATTERN LEARNER TEST")
    print("=" * 80)
    print()

    # Initialize learner
    learner = HeuristicPatternLearner()
    print()

    # Test trace 1: Invariant Method
    print("Test 1: Invariant Method Detection")
    print("-" * 40)
    trace1 = {
        'trace_id': 'trace_001',
        'conversation_id': 'conv_001',
        'problem_type': 'algebra',
        'agent_sequence': [
            'symmetry_specialist_001',
            'invariant_measure_001',
            'algebraic_solver_001'
        ],
        'success': True,
        'time_taken_ms': 900,
        'metadata': {
            'invariant_found': True,
            'preserved_quantity': 'total_energy',
            'symmetry': 'rotational'
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

    # Test trace 2: Extremal Elements
    print("Test 2: Extremal Elements Detection")
    print("-" * 40)
    trace2 = {
        'trace_id': 'trace_002',
        'conversation_id': 'conv_002',
        'problem_type': 'optimization',
        'agent_sequence': [
            'calculus_specialist_001',
            'optimization_agent_001',
            'extremal_analysis_001'
        ],
        'success': True,
        'time_taken_ms': 1100,
        'metadata': {
            'optimization_applied': True,
            'extremal_element': 'maximum',
            'method': 'greedy'
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

    # Test trace 3: Symmetrization
    print("Test 3: Symmetrization Detection")
    print("-" * 40)
    trace3 = {
        'trace_id': 'trace_003',
        'conversation_id': 'conv_003',
        'problem_type': 'geometry',
        'agent_sequence': [
            'geometric_agent_001',
            'symmetry_detector_001',
            'group_theory_001'
        ],
        'success': True,
        'time_taken_ms': 850,
        'metadata': {
            'symmetry_detected': True,
            'symmetrization_applied': True,
            'group': 'dihedral'
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

    # Test trace 4: Functional Viewpoint
    print("Test 4: Functional Viewpoint Detection")
    print("-" * 40)
    trace4 = {
        'trace_id': 'trace_004',
        'conversation_id': 'conv_004',
        'problem_type': 'combinatorics',
        'agent_sequence': [
            'combinatorial_agent_001',
            'generating_function_001',
            'series_solver_001'
        ],
        'success': True,
        'time_taken_ms': 1300,
        'metadata': {
            'encoding_functional': True,
            'generating_function_used': True,
            'recurrence': 'fibonacci-like'
        }
    }

    detection4 = learner.analyze_trace(trace4)
    if detection4:
        print(f"Detected {len(detection4.detected_strategies)} strategies:")
        for s in detection4.detected_strategies:
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
    for strategy_name in ['invariant_method', 'extremal_elements',
                          'symmetrization', 'functional_viewpoint']:
        eff = learner.get_strategy_effectiveness(strategy_name)
        if eff:
            print(f"  {eff['name']}:")
            print(f"    Success Rate: {eff['success_rate']:.2%}")
            print(f"    Applications: {eff['total_applications']}")

    print()
    print("=" * 80)
    print("HEURISTIC PATTERN LEARNER TEST COMPLETE")
    print("=" * 80)
