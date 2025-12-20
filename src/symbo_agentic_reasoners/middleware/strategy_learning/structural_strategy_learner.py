# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Structural Strategy Learner (Agent 3.4)
========================================

PURPOSE:
--------
Detects global structural patterns in problem-solving traces.
Focuses on high-level coordination patterns that organize the solution process.

STRUCTURAL STRATEGIES DETECTED:
--------------------------------
1. Pólya Cycle: Iterative refinement through understand → plan → execute → reflect
2. Problem Re-encoding: Translation between domains (algebraic ↔ geometric ↔ combinatorial)
3. Local-Global: Specialist analysis → supervisor synthesis pattern

DETECTION METHOD:
-----------------
Analyzes agent_sequence, timestamps, and metadata from SolutionTrace to identify:
- Phase transitions in problem-solving
- Domain shifts in representation
- Coordination patterns between specialists and supervisors

REFERENCE:
----------
Phase_4_Build_Order_Breakdown.md: Agent 3.4
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

logger = logging.getLogger('symbo_agentic_reasoners.strategy_learning.structural')


class StructuralStrategyLearner:
    """
    Agent 3.4: Structural Strategy Learner

    DIRECTIVE:
    ---------
    Monitor solution traces and detect global structural patterns that organize
    the problem-solving process. Focus on coordination patterns rather than
    domain-specific techniques.

    DETECTED PATTERNS:
    -----------------
    - Pólya Cycle: 4-phase iterative refinement
    - Problem Re-encoding: Cross-domain translation
    - Local-Global: Specialist-supervisor coordination

    OUTPUT:
    -------
    Posts StrategyDetection to Blackboard with detected structural patterns
    and confidence scores.
    """

    def __init__(self, blackboard=None, knowledge_graph=None):
        """
        Initialize Structural Strategy Learner

        Args:
            blackboard: Phase 0 Blackboard for event subscription
            knowledge_graph: KnowledgeGraph for strategy persistence
        """
        self.blackboard = blackboard
        self.knowledge_graph = knowledge_graph
        self._lock = threading.RLock()

        # Strategy library (loaded from KnowledgeGraph or bootstrapped)
        self.structural_strategies: Dict[str, StrategyPattern] = {}

        # Detection statistics
        self.traces_analyzed = 0
        self.detections_made = 0
        self.high_confidence_detections = 0

        # Initialize strategy library
        self._bootstrap_strategy_library()

        # Subscribe to events
        if self.blackboard:
            self._subscribe_to_events()

        print("    [OK] Structural Strategy Learner (Agent 3.4) initialized")

    def _bootstrap_strategy_library(self):
        """Initialize structural strategy patterns."""
        # Pólya Cycle pattern
        self.structural_strategies['polya_cycle'] = StrategyPattern(
            pattern_id='strategy_polya_cycle',
            name='Pólya Cycle',
            category=StrategyCategory.STRUCTURAL,
            description='Iterative 4-phase problem-solving: understand → plan → execute → reflect',
            abstract_description='Cyclic refinement through retrospective analysis',
            detection_signals=[
                'phase transitions in agent sequence',
                'reformulation after failed attempt',
                'retrospective verification',
                'decomposition → solution → retrospect pattern'
            ],
            applicability_conditions=[
                'complex problems requiring multiple attempts',
                'problems with unclear solution path',
                'optimization problems'
            ],
            composition_compatible=['invariant_method', 'problem_re_encoding']
        )

        # Problem Re-encoding pattern
        self.structural_strategies['problem_re_encoding'] = StrategyPattern(
            pattern_id='strategy_problem_re_encoding',
            name='Problem Re-encoding',
            category=StrategyCategory.STRUCTURAL,
            description='Translating problem between domains (algebraic ↔ geometric ↔ combinatorial)',
            abstract_description='Domain shift to reveal hidden structure',
            detection_signals=[
                'notation translator invoked',
                'domain shift in metadata',
                'geometric interpretation of algebraic problem',
                'algebraic formulation of geometric problem'
            ],
            applicability_conditions=[
                'problems with multiple natural representations',
                'stuck on one representation',
                'isomorphic structures in different domains'
            ],
            composition_compatible=['functional_viewpoint', 'graphical_revisualization']
        )

        # Local-Global pattern
        self.structural_strategies['local_global'] = StrategyPattern(
            pattern_id='strategy_local_global',
            name='Local-Global Coordination',
            category=StrategyCategory.STRUCTURAL,
            description='Specialist agents analyze local aspects, supervisor synthesizes global solution',
            abstract_description='Divide-and-conquer with centralized synthesis',
            detection_signals=[
                'multiple specialists invoked',
                'supervisor or coordinator in sequence',
                'parallel agent invocations',
                'synthesis phase after analysis'
            ],
            applicability_conditions=[
                'multi-aspect problems',
                'problems decomposable into independent subproblems',
                'requiring expert knowledge from multiple domains'
            ],
            composition_compatible=['symmetrization', 'extremal_elements']
        )

    def _subscribe_to_events(self):
        """Subscribe to SOLUTION_TRACE events from Blackboard."""
        try:
            self.blackboard.subscribe(
                agent_id='structural_strategy_learner_001',
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
        Analyze solution trace for structural patterns.

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

        # Detect Pólya Cycle
        polya_result = self._detect_polya_cycle(agent_sequence, metadata)
        if polya_result:
            detected_strategies.append(polya_result)

        # Detect Problem Re-encoding
        encoding_result = self._detect_re_encoding(agent_sequence, metadata)
        if encoding_result:
            detected_strategies.append(encoding_result)

        # Detect Local-Global
        local_global_result = self._detect_local_global(agent_sequence, metadata)
        if local_global_result:
            detected_strategies.append(local_global_result)

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
                detector_agent='structural_strategy_learner_001'
            )

        return None

    def _detect_polya_cycle(self, agent_sequence: List[str],
                           metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Pólya Cycle pattern.

        Signals:
        - Reformulation keywords in metadata
        - Decomposition → solving → verification pattern
        - Multiple attempts (retrospect → retry)
        """
        evidence = []
        confidence = 0.0

        # Check for phase keywords
        keywords = get_strategy_keywords('polya_cycle')

        # Check metadata for reformulation signals
        if any(key in str(metadata).lower() for key in ['reformulate', 'decompose', 'retrospect']):
            evidence.append("Reformulation keywords in metadata")
            confidence += 0.25

        # Check agent sequence for pattern
        sequence_lower = [a.lower() for a in agent_sequence]

        # Look for structure_recognizer → decomposition → solver → verification
        has_structure_recognition = any('structure' in a or 'recogni' in a for a in sequence_lower)
        has_decomposition = any('decompos' in a or 'break' in a for a in sequence_lower)
        has_verification = any('verif' in a or 'ax_prover' in a for a in sequence_lower)

        if has_structure_recognition and has_decomposition:
            evidence.append("Decomposition pattern detected")
            confidence += 0.30

        if has_verification:
            evidence.append("Retrospective verification")
            confidence += 0.20

        # Check for multiple solver invocations (iteration)
        solver_agents = [a for a in sequence_lower if 'solver' in a or 'agent' in a]
        if len(solver_agents) > 1:
            evidence.append(f"Iterative solving ({len(solver_agents)} attempts)")
            confidence += 0.25

        if confidence >= 0.3:  # Minimum threshold
            return StrategyDetectionResult(
                strategy_id='strategy_polya_cycle',
                strategy_name='Pólya Cycle',
                category=StrategyCategory.STRUCTURAL,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_re_encoding(self, agent_sequence: List[str],
                           metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Problem Re-encoding pattern.

        Signals:
        - Domain shift keywords
        - Notation translator in sequence
        - Encoding change in metadata
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Check for notation/encoding keywords
        encoding_keywords = ['notation', 'translate', 'encode', 'geometric', 'algebraic',
                            'combinatorial', 'probabilistic']
        if any(kw in metadata_str for kw in encoding_keywords):
            evidence.append("Encoding/translation keywords in metadata")
            confidence += 0.30

        # Check for translator agents
        if any('translat' in a or 'notation' in a for a in sequence_lower):
            evidence.append("Notation translator invoked")
            confidence += 0.35

        # Check for domain shift signals
        if 'domain_shift' in metadata_str or 'encoding_shift' in metadata_str:
            evidence.append("Explicit domain shift detected")
            confidence += 0.30

        # Check for cross-domain agents in sequence
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

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_problem_re_encoding',
                strategy_name='Problem Re-encoding',
                category=StrategyCategory.STRUCTURAL,
                confidence=min(confidence, 1.0),
                evidence=evidence
            )

        return None

    def _detect_local_global(self, agent_sequence: List[str],
                            metadata: Dict) -> Optional[StrategyDetectionResult]:
        """
        Detect Local-Global coordination pattern.

        Signals:
        - Multiple specialists followed by supervisor/coordinator
        - Parallel invocations (analysis_scope: local)
        - Synthesis phase
        """
        evidence = []
        confidence = 0.0

        sequence_lower = [a.lower() for a in agent_sequence]
        metadata_str = str(metadata).lower()

        # Count specialists
        specialists = [a for a in sequence_lower if 'specialist' in a or 'expert' in a]

        if len(specialists) >= 2:
            evidence.append(f"Multiple specialists invoked ({len(specialists)})")
            confidence += 0.35

        # Check for supervisor/coordinator
        has_supervisor = any('supervisor' in a or 'coordinator' in a or 'orchestrat' in a
                            for a in sequence_lower)

        if has_supervisor and len(specialists) >= 1:
            evidence.append("Supervisor coordinates specialists")
            confidence += 0.40

        # Check metadata for local/global signals
        if 'local' in metadata_str and 'global' in metadata_str:
            evidence.append("Local-global scope in metadata")
            confidence += 0.20

        # Check for synthesis keywords
        if any(kw in metadata_str for kw in ['synthesis', 'integration', 'coordination']):
            evidence.append("Synthesis phase detected")
            confidence += 0.15

        # Structural pattern: multiple agents → single coordinator
        if len(set(agent_sequence)) >= 3 and has_supervisor:
            evidence.append("Divide-and-conquer structure")
            confidence += 0.20

        if confidence >= 0.3:
            return StrategyDetectionResult(
                strategy_id='strategy_local_global',
                strategy_name='Local-Global Coordination',
                category=StrategyCategory.STRUCTURAL,
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
            if strategy_id in self.structural_strategies:
                strategy = self.structural_strategies[strategy_id]
                strategy.add_application(success, problem_type)

                # Store in KnowledgeGraph if available
                if self.knowledge_graph and hasattr(self.knowledge_graph, 'record_strategy_application'):
                    app = StrategyApplication(
                        application_id=f"app_{uuid.uuid4().hex[:8]}",
                        strategy_id=detection.strategy_id,
                        trace_id=trace.get('trace_id', 'unknown'),
                        conversation_id=trace.get('conversation_id', 'unknown'),
                        problem_type=problem_type,
                        domain=problem_type,  # Using problem_type as domain for now
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
                    'detection_type': 'STRUCTURAL_STRATEGY',
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
                author_agent='structural_strategy_learner_001',
                conversation_id=detection.conversation_id,
                tags=['STRATEGY_DETECTION', 'STRUCTURAL', detection.trace_id],
                metadata={
                    'detector': 'structural_strategy_learner',
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
            strategy_name: Strategy identifier (e.g., 'polya_cycle')

        Returns:
            Dict with success_rate, applications, domain_effectiveness
        """
        if strategy_name not in self.structural_strategies:
            return {}

        strategy = self.structural_strategies[strategy_name]
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
            'strategies_tracked': len(self.structural_strategies)
        }


if __name__ == "__main__":
    """Test Structural Strategy Learner"""
    print("=" * 80)
    print("STRUCTURAL STRATEGY LEARNER TEST")
    print("=" * 80)
    print()

    # Initialize learner
    learner = StructuralStrategyLearner()
    print()

    # Test trace 1: Pólya Cycle pattern
    print("Test 1: Pólya Cycle Detection")
    print("-" * 40)
    trace1 = {
        'trace_id': 'trace_001',
        'conversation_id': 'conv_001',
        'problem_type': 'integration',
        'agent_sequence': [
            'structure_recognizer_001',
            'decomposition_agent_001',
            'symbolic_integration_001',
            'ax_prover_001'
        ],
        'success': True,
        'time_taken_ms': 1200,
        'metadata': {
            'problem_reformulated': True,
            'decomposition_applied': True
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

    # Test trace 2: Problem Re-encoding
    print("Test 2: Problem Re-encoding Detection")
    print("-" * 40)
    trace2 = {
        'trace_id': 'trace_002',
        'conversation_id': 'conv_002',
        'problem_type': 'geometry',
        'agent_sequence': [
            'geometric_agent_001',
            'notation_translator_001',
            'algebraic_solver_001'
        ],
        'success': True,
        'time_taken_ms': 800,
        'metadata': {
            'domain_shift': 'geometric_to_algebraic',
            'notation_changed': True
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

    # Test trace 3: Local-Global coordination
    print("Test 3: Local-Global Coordination Detection")
    print("-" * 40)
    trace3 = {
        'trace_id': 'trace_003',
        'conversation_id': 'conv_003',
        'problem_type': 'optimization',
        'agent_sequence': [
            'algebra_specialist_001',
            'calculus_specialist_001',
            'geometry_specialist_001',
            'coordinator_001'
        ],
        'success': True,
        'time_taken_ms': 1500,
        'metadata': {
            'analysis_scope': 'local',
            'synthesis': True,
            'coordination': True
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
    for strategy_name in ['polya_cycle', 'problem_re_encoding', 'local_global']:
        eff = learner.get_strategy_effectiveness(strategy_name)
        if eff:
            print(f"  {eff['name']}:")
            print(f"    Success Rate: {eff['success_rate']:.2%}")
            print(f"    Applications: {eff['total_applications']}")

    print()
    print("=" * 80)
    print("STRUCTURAL STRATEGY LEARNER TEST COMPLETE")
    print("=" * 80)
