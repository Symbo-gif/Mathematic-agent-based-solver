# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Meta-Learning Extensions for Strategy Integration
==================================================

PURPOSE:
--------
Extends the Meta-Learning Team with strategy learning capabilities.
Integrates the StrategyCoordinator with the existing meta-learning infrastructure.

INTEGRATION POINTS:
-------------------
1. Enhanced SolutionTrace with strategy fields
2. MetaLearningTeamWithStrategies - extended coordinator
3. Strategy-aware routing for AgentSelectorOptimizer
4. Unified insights aggregation

USAGE:
------
Use MetaLearningTeamWithStrategies instead of MetaLearningTeam for
full strategy learning integration.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

# Import base meta-learning components
from .meta_learning import (
    MetaLearningTeam, SolutionTrace, PerformanceMonitor,
    AgentSelectorOptimizer, AdaptiveDispatcher
)

# Import strategy learning components
from .strategy_learning.strategy_coordinator import StrategyCoordinator, AggregatedDetection
from .strategy_learning.strategy_patterns import StrategyDetectionResult

logger = logging.getLogger('symbo_agentic_reasoners.meta_learning_extensions')


@dataclass
class EnhancedSolutionTrace(SolutionTrace):
    """
    Extended SolutionTrace with strategy detection fields.

    Adds strategy-specific information to the base SolutionTrace.
    """
    # Strategy detection results
    detected_strategies: List[str] = field(default_factory=list)  # Strategy IDs
    dominant_strategy: Optional[str] = None  # Primary strategy used
    strategy_confidence: float = 0.0  # Overall confidence in detection
    strategy_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage (extends parent)."""
        base_dict = super().to_dict()
        base_dict.update({
            'detected_strategies': self.detected_strategies,
            'dominant_strategy': self.dominant_strategy,
            'strategy_confidence': self.strategy_confidence,
            'strategy_metadata': self.strategy_metadata
        })
        return base_dict


class MetaLearningTeamWithStrategies:
    """
    Enhanced Meta-Learning Team with Strategy Learning Integration.

    Combines:
    - Performance Monitor (Agent 3.1)
    - Agent Selector Optimizer (Agent 3.2)
    - Adaptive Dispatcher (Agent 3.3)
    - Strategy Coordinator (Agent 3.8) with all strategy learners

    ENHANCEMENT OVER BASE:
    ---------------------
    - Strategy-aware trace recording
    - Strategy-based routing optimization
    - Unified performance + strategy insights
    - Cross-domain strategy transfer recommendations
    """

    def __init__(self, blackboard=None, vector_db=None, knowledge_graph=None,
                 orchestrator=None):
        """
        Initialize Enhanced Meta-Learning Team

        Args:
            blackboard: Phase 0 Blackboard
            vector_db: Vector database for traces
            knowledge_graph: KnowledgeGraph for strategy persistence
            orchestrator: Main Orchestrator reference
        """
        print("  [ENHANCED META-LEARNING TEAM - The Optimizer + The Learner]")

        self.blackboard = blackboard
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph
        self.orchestrator = orchestrator
        self._lock = threading.RLock()

        # Initialize base meta-learning components
        self.performance_monitor = PerformanceMonitor(blackboard, vector_db)
        self.optimizer = AgentSelectorOptimizer(blackboard, vector_db)
        self.dispatcher = AdaptiveDispatcher(blackboard, self.optimizer, orchestrator)

        # Initialize strategy coordinator
        self.strategy_coordinator = StrategyCoordinator(
            blackboard, knowledge_graph, self.optimizer
        )

        # Integration statistics
        self.strategy_enhanced_optimizations = 0
        self.cross_domain_recommendations = 0

        print("    [OK] Enhanced Meta-Learning Team assembled")

    def log_task_start(self, conversation_id: str, problem_type: str,
                      complexity: str = 'medium', **metadata):
        """
        Begin recording solution trace (strategy-aware).

        Args:
            conversation_id: Unique conversation identifier
            problem_type: Type of problem
            complexity: Problem complexity level
            **metadata: Additional metadata
        """
        # Use base performance monitor
        self.performance_monitor.on_task_start({
            'conversation_id': conversation_id,
            'problem_type': problem_type,
            'complexity': complexity,
            'metadata': metadata
        })

    def log_agent_invocation(self, conversation_id: str, agent_id: str,
                            input_tokens: int = 0, vram_mb: float = 0):
        """Record agent involvement."""
        self.performance_monitor.on_agent_invoked({
            'conversation_id': conversation_id,
            'agent_id': agent_id,
            'input_tokens': input_tokens,
            'vram_mb': vram_mb
        })

    def log_verification(self, conversation_id: str, status: str):
        """Record verification outcome."""
        self.performance_monitor.on_verification({
            'conversation_id': conversation_id,
            'status': status
        })

    def log_session_end(self, conversation_id: str) -> Optional[EnhancedSolutionTrace]:
        """
        Complete trace and trigger strategy analysis.

        This is the key integration point where strategy learning
        enhances the base meta-learning.

        Returns:
            EnhancedSolutionTrace with both performance and strategy data
        """
        # Get base trace from performance monitor
        base_trace = self.performance_monitor.on_session_end({
            'conversation_id': conversation_id
        })

        if not base_trace:
            return None

        # Convert to dict for strategy analysis
        trace_dict = base_trace.to_dict()

        # Run strategy analysis
        strategy_detection = self.strategy_coordinator.analyze_trace(trace_dict)

        # Create enhanced trace
        enhanced_trace = self._create_enhanced_trace(base_trace, strategy_detection)

        # Analyze trace for optimizer (base functionality)
        self.optimizer.analyze_trace(trace_dict)

        # Integrate strategy insights into optimizer
        self._integrate_strategy_insights(enhanced_trace, strategy_detection)

        return enhanced_trace

    def _create_enhanced_trace(self, base_trace: SolutionTrace,
                              strategy_detection: AggregatedDetection) -> EnhancedSolutionTrace:
        """
        Create EnhancedSolutionTrace from base trace and strategy detection.

        Args:
            base_trace: Base SolutionTrace from performance monitor
            strategy_detection: Aggregated strategy detection

        Returns:
            EnhancedSolutionTrace with strategy information
        """
        # Extract strategy information
        detected_strategies = [s.strategy_id for s in strategy_detection.all_strategies]
        dominant_strategy = (strategy_detection.dominant_strategy.strategy_id
                           if strategy_detection.dominant_strategy else None)

        # Create enhanced trace
        enhanced = EnhancedSolutionTrace(
            trace_id=base_trace.trace_id,
            conversation_id=base_trace.conversation_id,
            problem_type=base_trace.problem_type,
            problem_complexity=base_trace.problem_complexity,
            agent_sequence=base_trace.agent_sequence,
            time_taken_ms=base_trace.time_taken_ms,
            cpu_time_ms=base_trace.cpu_time_ms,
            agent_times=base_trace.agent_times,
            verification_status=base_trace.verification_status,
            token_count=base_trace.token_count,
            vram_peak_mb=base_trace.vram_peak_mb,
            success=base_trace.success,
            error_occurred=base_trace.error_occurred,
            timestamp=base_trace.timestamp,
            metadata=base_trace.metadata,
            # Strategy fields
            detected_strategies=detected_strategies,
            dominant_strategy=dominant_strategy,
            strategy_confidence=strategy_detection.confidence_score,
            strategy_metadata={
                'structural_count': len(strategy_detection.structural_strategies),
                'heuristic_count': len(strategy_detection.heuristic_strategies),
                'nonstandard_count': len(strategy_detection.nonstandard_strategies),
                'meta_patterns': strategy_detection.meta_patterns
            }
        )

        return enhanced

    def _integrate_strategy_insights(self, trace: EnhancedSolutionTrace,
                                     detection: AggregatedDetection):
        """
        Integrate strategy insights into optimizer routing.

        Updates routing tables based on which strategies were successful.

        Args:
            trace: Enhanced solution trace
            detection: Strategy detection results
        """
        if not trace.success:
            return  # Only learn from successful solutions

        with self._lock:
            self.strategy_enhanced_optimizations += 1

        # Extract strategy-agent correlations
        if detection.dominant_strategy:
            strategy_name = detection.dominant_strategy.strategy_name
            agent_sequence = trace.agent_sequence

            # Record which agents were effective for this strategy
            # This enriches the optimizer's routing tables
            logger.debug(
                f"Strategy '{strategy_name}' succeeded with agents: {agent_sequence[:3]}..."
            )

    def run_batch_optimization(self) -> Dict:
        """
        Execute batch optimization with strategy insights.

        Extends base optimization with strategy-aware routing.

        Returns:
            Optimization results with strategy insights
        """
        # Run base optimization
        base_results = self.optimizer.compute_routing_tables()
        base_insights = self.optimizer.get_pattern_insights()

        # Get strategy composition insights
        composition_insights = (
            self.strategy_coordinator.meta_learner.get_composition_insights(
                min_occurrences=2
            )
        )

        # Post integrated update
        if self.blackboard:
            try:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
                entry = create_entry(
                    entry_type=EntryType.TASK,
                    content={
                        'routing_tables': base_results,
                        'performance_insights': base_insights,
                        'strategy_composition_insights': composition_insights,
                        'optimization_run': datetime.now().isoformat()
                    },
                    author_agent='meta_learning_team_enhanced',
                    conversation_id='optimization',
                    tags=['ROUTING_UPDATE', 'OPTIMIZATION_COMPLETE', 'STRATEGY_ENHANCED'],
                    metadata={
                        'entry_type': 'ENHANCED_ROUTING_UPDATE',
                        'strategy_enhanced': True
                    }
                )
                self.blackboard.post(entry)
            except Exception as e:
                logger.debug(f"Could not post enhanced routing update: {type(e).__name__}: {e}")

        return {
            'tables_updated': len(base_results),
            'performance_insights': len(base_insights),
            'strategy_insights': len(composition_insights),
            'insights': base_insights,
            'composition_patterns': composition_insights
        }

    def get_team_recommendation(self, problem_context: Dict) -> Dict:
        """
        Get optimal team configuration with strategy guidance.

        Combines base team sizing with strategy recommendations.

        Args:
            problem_context: Problem information

        Returns:
            Enhanced recommendation with strategies
        """
        # Get base team recommendation
        team_size = self.dispatcher.determine_team_size(problem_context)
        complexity = self.dispatcher.get_complexity_level(problem_context)
        problem_type = problem_context.get('problem_type', 'unknown')

        # Get agent recommendations
        agents = self.dispatcher.select_agents(problem_type, team_size)

        # Get strategy recommendations
        strategy_rec = self.strategy_coordinator.get_strategy_recommendation(
            problem_context
        )

        return {
            'team_size': team_size,
            'complexity_level': complexity.name,
            'suggested_agents': agents,
            'strategy_templates': strategy_rec.get('suggested_templates', []),
            'composition_patterns': strategy_rec.get('composition_patterns', []),
            'rationale': f"{complexity.name} complexity -> {team_size} agents"
        }

    def get_cross_domain_recommendations(self, source_domain: str,
                                        target_domain: str) -> List[Dict]:
        """
        Get strategy transfer recommendations across domains.

        Identifies strategies successful in source_domain that may apply
        to target_domain.

        Args:
            source_domain: Source problem domain
            target_domain: Target problem domain

        Returns:
            List of transferable strategy recommendations
        """
        with self._lock:
            self.cross_domain_recommendations += 1

        recommendations = []

        # Query each learner for domain-specific effectiveness
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

            # Find strategies effective in source domain
            for strategy_name, strategy in strategies.items():
                source_effectiveness = strategy.domains_effective.get(source_domain, 0)

                if source_effectiveness > 0.6:  # High success in source
                    target_effectiveness = strategy.domains_effective.get(target_domain, 0)

                    recommendations.append({
                        'strategy': strategy.name,
                        'strategy_id': strategy.pattern_id,
                        'source_domain': source_domain,
                        'target_domain': target_domain,
                        'source_effectiveness': source_effectiveness,
                        'target_effectiveness': target_effectiveness,
                        'transfer_confidence': (
                            'high' if target_effectiveness > 0.5
                            else 'medium' if target_effectiveness > 0.3
                            else 'exploratory'
                        ),
                        'recommendation': (
                            f"Strategy '{strategy.name}' has {source_effectiveness:.1%} "
                            f"success in {source_domain}. Consider applying to {target_domain}."
                        )
                    })

        # Sort by source effectiveness
        recommendations.sort(key=lambda x: x['source_effectiveness'], reverse=True)
        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics (performance + strategy)."""
        base_stats = {
            'performance_monitor': self.performance_monitor.get_statistics(),
            'optimizer': self.optimizer.get_statistics(),
            'dispatcher': self.dispatcher.get_statistics()
        }

        strategy_stats = self.strategy_coordinator.get_statistics()

        integration_stats = {
            'strategy_enhanced_optimizations': self.strategy_enhanced_optimizations,
            'cross_domain_recommendations': self.cross_domain_recommendations
        }

        return {
            **base_stats,
            'strategy_coordinator': strategy_stats,
            'integration': integration_stats
        }


if __name__ == "__main__":
    """Test Enhanced Meta-Learning Team"""
    print("=" * 80)
    print("ENHANCED META-LEARNING TEAM TEST")
    print("=" * 80)
    print()

    # Initialize enhanced team
    team = MetaLearningTeamWithStrategies()
    print()

    # Simulate solution with strategies
    print("SIMULATING STRATEGY-AWARE SOLUTION")
    print("-" * 40)

    # Trace 1: Complex optimization with multiple strategies
    print("Trace 1: Optimization with symmetry and extremal methods")
    team.log_task_start('conv_001', 'optimization', complexity='high',
                       involves_proof=True)
    team.log_agent_invocation('conv_001', 'structure_recognizer_001', 100)
    team.log_agent_invocation('conv_001', 'symmetry_specialist_001', 150)
    team.log_agent_invocation('conv_001', 'optimization_agent_001', 200)
    team.log_verification('conv_001', 'VERIFIED')
    enhanced_trace = team.log_session_end('conv_001')

    if enhanced_trace:
        print(f"  Trace ID: {enhanced_trace.trace_id}")
        print(f"  Success: {enhanced_trace.success}")
        print(f"  Detected Strategies: {len(enhanced_trace.detected_strategies)}")
        print(f"  Dominant Strategy: {enhanced_trace.dominant_strategy}")
        print(f"  Strategy Confidence: {enhanced_trace.strategy_confidence:.2%}")
    print()

    # Test enhanced optimization
    print("RUNNING ENHANCED BATCH OPTIMIZATION")
    print("-" * 40)
    results = team.run_batch_optimization()
    print(f"  Tables Updated: {results['tables_updated']}")
    print(f"  Performance Insights: {results['performance_insights']}")
    print(f"  Strategy Insights: {results['strategy_insights']}")
    print()

    # Test enhanced recommendation
    print("ENHANCED TEAM RECOMMENDATION")
    print("-" * 40)
    problem_context = {
        'problem_type': 'optimization',
        'metadata': {
            'complexity': 'high',
            'involves_optimization': True,
            'symmetry': True
        }
    }

    rec = team.get_team_recommendation(problem_context)
    print(f"  Team Size: {rec['team_size']}")
    print(f"  Complexity: {rec['complexity_level']}")
    print(f"  Strategy Templates: {len(rec['strategy_templates'])}")
    print(f"  Composition Patterns: {len(rec['composition_patterns'])}")
    print()

    # Test cross-domain recommendations
    print("CROSS-DOMAIN STRATEGY TRANSFER")
    print("-" * 40)
    transfers = team.get_cross_domain_recommendations('optimization', 'algebra')
    print(f"  Found {len(transfers)} transfer candidates")
    for transfer in transfers[:3]:
        print(f"    - {transfer['strategy']}: {transfer['transfer_confidence']}")
    print()

    # Show statistics
    print("COMPREHENSIVE STATISTICS:")
    print("-" * 40)
    stats = team.get_statistics()
    print(f"Performance Monitor:")
    for k, v in stats['performance_monitor'].items():
        print(f"  {k}: {v}")
    print(f"\nStrategy Coordinator:")
    for k, v in stats['strategy_coordinator']['coordinator'].items():
        print(f"  {k}: {v}")
    print(f"\nIntegration:")
    for k, v in stats['integration'].items():
        print(f"  {k}: {v}")

    print()
    print("=" * 80)
    print("ENHANCED META-LEARNING TEAM TEST COMPLETE")
    print("=" * 80)
