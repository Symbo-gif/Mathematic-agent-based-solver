# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Strategy Coordinator (Agent 3.8)
=================================

PURPOSE:
--------
Coordinates all strategy learner agents and aggregates their detections
into unified insights. Acts as the integration layer between strategy
learning and the main orchestrator.

RESPONSIBILITIES:
-----------------
1. Aggregate detections from all learner agents (3.4-3.7)
2. Resolve conflicts when multiple detections overlap
3. Maintain unified view of detected strategies
4. Provide strategy recommendations to orchestrator
5. Post consolidated insights to Blackboard

INTEGRATION:
------------
- Receives detections from 4 learner agents
- Provides unified API for strategy queries
- Updates AgentSelectorOptimizer with strategy-based routing

REFERENCE:
----------
Phase_4_Build_Order_Breakdown.md: Agent 3.8
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import threading
from collections import defaultdict

from .strategy_patterns import (
    StrategyPattern, StrategyDetectionResult, StrategyDetection,
    StrategyCategory, TemplatePattern
)
from .structural_strategy_learner import StructuralStrategyLearner
from .heuristic_pattern_learner import HeuristicPatternLearner
from .nonstandard_move_learner import NonStandardMoveLearner
from .meta_strategy_learner import MetaStrategyLearner

logger = logging.getLogger('symbo_agentic_reasoners.strategy_learning.coordinator')


@dataclass
class AggregatedDetection:
    """
    Aggregated strategy detection from multiple learners.

    Combines detections from different agents with conflict resolution.
    """
    trace_id: str
    conversation_id: str
    structural_strategies: List[StrategyDetectionResult] = field(default_factory=list)
    heuristic_strategies: List[StrategyDetectionResult] = field(default_factory=list)
    nonstandard_strategies: List[StrategyDetectionResult] = field(default_factory=list)
    meta_patterns: Dict[str, Any] = field(default_factory=dict)
    dominant_strategy: Optional[StrategyDetectionResult] = None
    confidence_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def all_strategies(self) -> List[StrategyDetectionResult]:
        """Get all detected strategies across all categories."""
        return (self.structural_strategies +
                self.heuristic_strategies +
                self.nonstandard_strategies)

    @property
    def high_confidence_strategies(self) -> List[StrategyDetectionResult]:
        """Get only high-confidence detections (>= 0.7)."""
        return [s for s in self.all_strategies if s.confidence >= 0.7]


class StrategyCoordinator:
    """
    Agent 3.8: Strategy Coordinator

    DIRECTIVE:
    ---------
    Coordinate all strategy learner agents and provide unified strategy
    insights to the orchestrator. Aggregate detections, resolve conflicts,
    and maintain comprehensive strategy knowledge.

    COMPONENTS:
    ----------
    - Structural Strategy Learner (3.4)
    - Heuristic Pattern Learner (3.5)
    - NonStandard Move Learner (3.6)
    - Meta Strategy Learner (3.7)

    OUTPUT:
    -------
    Unified strategy recommendations and insights for orchestrator
    routing decisions.
    """

    def __init__(self, blackboard=None, knowledge_graph=None, optimizer=None):
        """
        Initialize Strategy Coordinator

        Args:
            blackboard: Phase 0 Blackboard
            knowledge_graph: KnowledgeGraph for strategy persistence
            optimizer: AgentSelectorOptimizer reference
        """
        self.blackboard = blackboard
        self.knowledge_graph = knowledge_graph
        self.optimizer = optimizer
        self._lock = threading.RLock()

        # Initialize all learner agents
        print("  [STRATEGY COORDINATOR - The Learner]")
        self.structural_learner = StructuralStrategyLearner(blackboard, knowledge_graph)
        self.heuristic_learner = HeuristicPatternLearner(blackboard, knowledge_graph)
        self.nonstandard_learner = NonStandardMoveLearner(blackboard, knowledge_graph)
        self.meta_learner = MetaStrategyLearner(blackboard, knowledge_graph)

        # Detection aggregation
        self.aggregated_detections: Dict[str, AggregatedDetection] = {}
        self.max_detections = 100

        # Statistics
        self.coordinations = 0
        self.conflicts_resolved = 0
        self.recommendations_provided = 0

        # Subscribe to strategy detection events
        if self.blackboard:
            self._subscribe_to_detections()

        print("    [OK] Strategy Coordinator assembled")

    def _subscribe_to_detections(self):
        """Subscribe to strategy detection events from all learners."""
        try:
            self.blackboard.subscribe(
                agent_id='strategy_coordinator_001',
                tags=['STRATEGY_DETECTION'],
                callback=self._on_strategy_detection
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to detections: {type(e).__name__}: {e}")

    def _on_strategy_detection(self, entry):
        """Handle strategy detection from learner agents."""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            self._aggregate_detection(entry.content)

    def analyze_trace(self, trace: Dict) -> AggregatedDetection:
        """
        Coordinate all learners to analyze a trace.

        Args:
            trace: SolutionTrace dictionary

        Returns:
            AggregatedDetection with unified insights
        """
        with self._lock:
            self.coordinations += 1

        trace_id = trace.get('trace_id', 'unknown')
        conversation_id = trace.get('conversation_id', 'unknown')

        # Get detections from all learners
        structural_detection = self.structural_learner.analyze_trace(trace)
        heuristic_detection = self.heuristic_learner.analyze_trace(trace)
        nonstandard_detection = self.nonstandard_learner.analyze_trace(trace)
        meta_result = self.meta_learner.analyze_trace(trace)

        # Create aggregated detection
        aggregated = AggregatedDetection(
            trace_id=trace_id,
            conversation_id=conversation_id
        )

        # Add structural strategies
        if structural_detection:
            aggregated.structural_strategies = structural_detection.detected_strategies

        # Add heuristic strategies
        if heuristic_detection:
            aggregated.heuristic_strategies = heuristic_detection.detected_strategies

        # Add nonstandard strategies
        if nonstandard_detection:
            aggregated.nonstandard_strategies = nonstandard_detection.detected_strategies

        # Add meta patterns
        if meta_result:
            aggregated.meta_patterns = meta_result

        # Resolve conflicts and determine dominant strategy
        self._resolve_conflicts(aggregated)

        # Calculate overall confidence
        aggregated.confidence_score = self._calculate_confidence(aggregated)

        # Store aggregated detection
        with self._lock:
            self.aggregated_detections[trace_id] = aggregated
            if len(self.aggregated_detections) > self.max_detections:
                # Remove oldest
                oldest = min(self.aggregated_detections.keys(),
                           key=lambda k: self.aggregated_detections[k].timestamp)
                del self.aggregated_detections[oldest]

        # Post aggregated insights
        self._post_aggregated_insights(aggregated)

        # Update optimizer if available
        if self.optimizer:
            self._update_optimizer(aggregated, trace)

        return aggregated

    def _aggregate_detection(self, detection_data: Dict):
        """Aggregate a detection from a learner agent."""
        trace_id = detection_data.get('trace_id', 'unknown')
        detection_type = detection_data.get('detection_type', '')

        # Get or create aggregated detection
        with self._lock:
            if trace_id not in self.aggregated_detections:
                self.aggregated_detections[trace_id] = AggregatedDetection(
                    trace_id=trace_id,
                    conversation_id=detection_data.get('conversation_id', 'unknown')
                )

            aggregated = self.aggregated_detections[trace_id]

        # Add strategies based on detection type
        strategies = detection_data.get('strategies', [])
        if detection_type == 'STRUCTURAL_STRATEGY':
            for s in strategies:
                aggregated.structural_strategies.append(
                    self._dict_to_detection_result(s)
                )
        elif detection_type == 'HEURISTIC_STRATEGY':
            for s in strategies:
                aggregated.heuristic_strategies.append(
                    self._dict_to_detection_result(s)
                )
        elif detection_type == 'NONSTANDARD_STRATEGY':
            for s in strategies:
                aggregated.nonstandard_strategies.append(
                    self._dict_to_detection_result(s)
                )
        elif detection_type == 'META_STRATEGY':
            aggregated.meta_patterns = detection_data.get('meta_patterns', {})

        # Re-resolve conflicts
        self._resolve_conflicts(aggregated)

    def _dict_to_detection_result(self, strategy_dict: Dict) -> StrategyDetectionResult:
        """Convert dictionary to StrategyDetectionResult."""
        return StrategyDetectionResult(
            strategy_id=strategy_dict.get('strategy_id', 'unknown'),
            strategy_name=strategy_dict.get('strategy_name', 'unknown'),
            category=StrategyCategory(strategy_dict.get('category', 'structural')),
            confidence=strategy_dict.get('confidence', 0.0),
            evidence=strategy_dict.get('evidence', [])
        )

    def _resolve_conflicts(self, aggregated: AggregatedDetection):
        """
        Resolve conflicts between overlapping detections.

        Sets the dominant_strategy based on confidence and category priority.
        """
        all_strategies = aggregated.all_strategies

        if not all_strategies:
            return

        # Category priority: META > NONSTANDARD > HEURISTIC > STRUCTURAL
        # (More specific strategies take precedence)
        category_priority = {
            StrategyCategory.META: 4,
            StrategyCategory.NONSTANDARD: 3,
            StrategyCategory.HEURISTIC: 2,
            StrategyCategory.STRUCTURAL: 1
        }

        # Sort by confidence first, then category priority
        sorted_strategies = sorted(
            all_strategies,
            key=lambda s: (s.confidence, category_priority.get(s.category, 0)),
            reverse=True
        )

        # Check for conflicts (same category, similar confidence)
        conflicts = 0
        for i in range(len(sorted_strategies) - 1):
            s1, s2 = sorted_strategies[i], sorted_strategies[i + 1]
            if s1.category == s2.category and abs(s1.confidence - s2.confidence) < 0.1:
                conflicts += 1

        if conflicts > 0:
            with self._lock:
                self.conflicts_resolved += conflicts

        # Set dominant strategy
        aggregated.dominant_strategy = sorted_strategies[0]

    def _calculate_confidence(self, aggregated: AggregatedDetection) -> float:
        """
        Calculate overall confidence score for aggregated detection.

        Considers:
        - Number of high-confidence detections
        - Diversity of categories detected
        - Presence of meta-patterns
        """
        all_strategies = aggregated.all_strategies

        if not all_strategies:
            return 0.0

        # Average confidence of all detections
        avg_confidence = sum(s.confidence for s in all_strategies) / len(all_strategies)

        # Bonus for multiple categories
        categories_detected = len(set(s.category for s in all_strategies))
        category_bonus = categories_detected * 0.05

        # Bonus for meta-patterns
        meta_bonus = 0.1 if aggregated.meta_patterns else 0.0

        # Bonus for high-confidence detections
        high_conf_ratio = len(aggregated.high_confidence_strategies) / max(1, len(all_strategies))
        high_conf_bonus = high_conf_ratio * 0.15

        total_confidence = avg_confidence + category_bonus + meta_bonus + high_conf_bonus
        return min(total_confidence, 1.0)

    def _post_aggregated_insights(self, aggregated: AggregatedDetection):
        """Post aggregated insights to Blackboard."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

            entry = create_entry(
                entry_type=EntryType.OBSERVATION,
                content={
                    'detection_type': 'AGGREGATED_STRATEGIES',
                    'trace_id': aggregated.trace_id,
                    'conversation_id': aggregated.conversation_id,
                    'structural_count': len(aggregated.structural_strategies),
                    'heuristic_count': len(aggregated.heuristic_strategies),
                    'nonstandard_count': len(aggregated.nonstandard_strategies),
                    'meta_patterns': aggregated.meta_patterns,
                    'dominant_strategy': {
                        'name': aggregated.dominant_strategy.strategy_name,
                        'category': aggregated.dominant_strategy.category.value,
                        'confidence': aggregated.dominant_strategy.confidence
                    } if aggregated.dominant_strategy else None,
                    'overall_confidence': aggregated.confidence_score
                },
                author_agent='strategy_coordinator_001',
                conversation_id=aggregated.conversation_id,
                tags=['STRATEGY_INSIGHTS', 'AGGREGATED', aggregated.trace_id],
                metadata={
                    'coordinator': 'strategy_coordinator',
                    'total_strategies': len(aggregated.all_strategies)
                }
            )

            self.blackboard.post(entry)

        except Exception as e:
            logger.debug(f"Could not post aggregated insights: {type(e).__name__}: {e}")

    def _update_optimizer(self, aggregated: AggregatedDetection, trace: Dict):
        """Update AgentSelectorOptimizer with strategy insights."""
        # Extract dominant strategy for routing enhancement
        if not aggregated.dominant_strategy:
            return

        # Would integrate with optimizer to adjust routing based on strategies
        # For now, just log the intent
        logger.debug(f"Strategy insights available for optimization: {aggregated.dominant_strategy.strategy_name}")

    def get_strategy_recommendation(self, problem_context: Dict) -> Dict[str, Any]:
        """
        Get strategy recommendation for a new problem.

        Args:
            problem_context: Problem information

        Returns:
            Recommendation with suggested strategies and agents
        """
        with self._lock:
            self.recommendations_provided += 1

        # Get template recommendations from meta learner
        problem_type = problem_context.get('problem_type', 'unknown')
        metadata = problem_context.get('metadata', {})

        template_recs = self.meta_learner.get_template_recommendations(
            problem_type, metadata
        )

        # Get composition insights
        composition_insights = self.meta_learner.get_composition_insights(min_occurrences=2)

        # Build recommendation
        recommendation = {
            'problem_type': problem_type,
            'suggested_templates': template_recs[:3],  # Top 3
            'composition_patterns': composition_insights[:3],  # Top 3
            'timestamp': datetime.now().isoformat()
        }

        return recommendation

    def get_strategy_effectiveness(self, strategy_name: str,
                                   category: str = None) -> Dict[str, Any]:
        """
        Get effectiveness metrics for a specific strategy.

        Args:
            strategy_name: Strategy identifier
            category: Category filter (structural, heuristic, nonstandard)

        Returns:
            Effectiveness metrics
        """
        # Query appropriate learner based on category
        if category == 'structural' or category is None:
            result = self.structural_learner.get_strategy_effectiveness(strategy_name)
            if result:
                return result

        if category == 'heuristic' or category is None:
            result = self.heuristic_learner.get_strategy_effectiveness(strategy_name)
            if result:
                return result

        if category == 'nonstandard' or category is None:
            result = self.nonstandard_learner.get_strategy_effectiveness(strategy_name)
            if result:
                return result

        return {}

    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator and all learner statistics."""
        return {
            'coordinator': {
                'coordinations': self.coordinations,
                'conflicts_resolved': self.conflicts_resolved,
                'recommendations_provided': self.recommendations_provided,
                'aggregated_detections': len(self.aggregated_detections)
            },
            'structural_learner': self.structural_learner.get_statistics(),
            'heuristic_learner': self.heuristic_learner.get_statistics(),
            'nonstandard_learner': self.nonstandard_learner.get_statistics(),
            'meta_learner': self.meta_learner.get_statistics()
        }


if __name__ == "__main__":
    """Test Strategy Coordinator"""
    print("=" * 80)
    print("STRATEGY COORDINATOR TEST")
    print("=" * 80)
    print()

    # Initialize coordinator
    coordinator = StrategyCoordinator()
    print()

    # Test trace 1: Complex trace with multiple strategies
    print("Test 1: Multi-Strategy Detection")
    print("-" * 40)
    trace1 = {
        'trace_id': 'trace_001',
        'conversation_id': 'conv_001',
        'problem_type': 'optimization',
        'agent_sequence': [
            'structure_recognizer_001',
            'decomposition_agent_001',
            'symmetry_specialist_001',
            'optimization_agent_001',
            'ax_prover_001'
        ],
        'success': True,
        'time_taken_ms': 1800,
        'metadata': {
            'problem_reformulated': True,
            'symmetry_detected': True,
            'extremal_element': 'maximum',
            'optimization_applied': True
        }
    }

    detection1 = coordinator.analyze_trace(trace1)
    print(f"Aggregated Detection:")
    print(f"  Structural: {len(detection1.structural_strategies)}")
    print(f"  Heuristic: {len(detection1.heuristic_strategies)}")
    print(f"  Nonstandard: {len(detection1.nonstandard_strategies)}")
    print(f"  Overall Confidence: {detection1.confidence_score:.2%}")
    if detection1.dominant_strategy:
        print(f"  Dominant Strategy: {detection1.dominant_strategy.strategy_name}")
        print(f"    Confidence: {detection1.dominant_strategy.confidence:.2%}")
    print()

    # Test trace 2: Simpler trace
    print("Test 2: Simple Strategy Detection")
    print("-" * 40)
    trace2 = {
        'trace_id': 'trace_002',
        'conversation_id': 'conv_002',
        'problem_type': 'algebra',
        'agent_sequence': [
            'structure_recognizer_001',
            'algebraic_solver_001'
        ],
        'success': True,
        'time_taken_ms': 600,
        'metadata': {
            'standard_form': True
        }
    }

    detection2 = coordinator.analyze_trace(trace2)
    print(f"Aggregated Detection:")
    print(f"  Total strategies detected: {len(detection2.all_strategies)}")
    print(f"  High-confidence: {len(detection2.high_confidence_strategies)}")
    print(f"  Overall Confidence: {detection2.confidence_score:.2%}")
    print()

    # Test strategy recommendation
    print("Test 3: Strategy Recommendation")
    print("-" * 40)
    problem_context = {
        'problem_type': 'optimization',
        'metadata': {
            'complexity': 'high',
            'involves_optimization': True
        }
    }

    recommendation = coordinator.get_strategy_recommendation(problem_context)
    print(f"Recommendation for {recommendation['problem_type']} problem:")
    if recommendation['suggested_templates']:
        print(f"  Suggested templates: {len(recommendation['suggested_templates'])}")
        for template in recommendation['suggested_templates']:
            print(f"    - {template['principle']} (success: {template['success_count']})")
    print()

    # Test strategy effectiveness query
    print("Test 4: Strategy Effectiveness Query")
    print("-" * 40)
    effectiveness = coordinator.get_strategy_effectiveness('polya_cycle')
    if effectiveness:
        print(f"  Strategy: {effectiveness['name']}")
        print(f"  Success Rate: {effectiveness['success_rate']:.2%}")
        print(f"  Applications: {effectiveness['total_applications']}")
    else:
        print("  No effectiveness data yet")
    print()

    # Show statistics
    print("COORDINATOR STATISTICS:")
    print("-" * 40)
    stats = coordinator.get_statistics()
    print(f"Coordinator:")
    for key, value in stats['coordinator'].items():
        print(f"  {key}: {value}")
    print()
    print(f"Learner Agents:")
    for learner in ['structural_learner', 'heuristic_learner',
                    'nonstandard_learner', 'meta_learner']:
        print(f"  {learner}:")
        for key, value in stats[learner].items():
            print(f"    {key}: {value}")

    print()
    print("=" * 80)
    print("STRATEGY COORDINATOR TEST COMPLETE")
    print("=" * 80)
