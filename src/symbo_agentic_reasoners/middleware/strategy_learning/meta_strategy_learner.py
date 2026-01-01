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
Meta Strategy Learner (Agent 3.7)
==================================

PURPOSE:
--------
Detects meta-level patterns across multiple solution traces.
Operates at a higher abstraction level to identify templates and compositions.

META PATTERNS DETECTED:
-----------------------
1. Template Mining: Identifying reusable problem templates and analogies
2. Multi-Solution Synthesis: Detecting when multiple approaches are combined
3. Strategy Composition: Learning which strategies work well together

DETECTION METHOD:
-----------------
Analyzes patterns across multiple traces, looking for:
- Recurring problem structures (templates)
- Multi-path solutions
- Frequently co-occurring strategies

REFERENCE:
----------
Phase_4_Build_Order_Breakdown.md: Agent 3.7
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import threading
import uuid

from .strategy_patterns import (
    StrategyPattern, StrategyDetectionResult, StrategyDetection,
    StrategyCategory, TemplatePattern, StrategyApplication,
    compute_composition_strength
)

logger = logging.getLogger('symbo_agentic_reasoners.strategy_learning.meta')


class MetaStrategyLearner:
    """
    Agent 3.7: Meta Strategy Learner

    DIRECTIVE:
    ---------
    Monitor solution traces at a meta-level to detect higher-order patterns:
    templates that recur across problems, multi-solution approaches, and
    strategy composition patterns.

    DETECTED PATTERNS:
    -----------------
    - Template Mining: Reusable problem templates
    - Multi-Solution Synthesis: Multiple solution paths combined
    - Strategy Composition: Co-occurring strategy patterns

    OUTPUT:
    -------
    Posts meta-level insights to Blackboard and maintains a library of
    discovered templates and composition patterns.
    """

    def __init__(self, blackboard=None, knowledge_graph=None):
        """
        Initialize Meta Strategy Learner

        Args:
            blackboard: Phase 0 Blackboard for event subscription
            knowledge_graph: KnowledgeGraph for template persistence
        """
        self.blackboard = blackboard
        self.knowledge_graph = knowledge_graph
        self._lock = threading.RLock()

        # Template library
        self.templates: Dict[str, TemplatePattern] = {}

        # Trace history for pattern analysis
        self.trace_history: List[Dict] = []
        self.max_history = 100

        # Strategy co-occurrence tracking
        self.strategy_pairs: Counter = Counter()  # (strategy1, strategy2) -> count
        self.successful_pairs: Counter = Counter()  # (strategy1, strategy2) -> success_count

        # Problem signature tracking
        self.problem_signatures: Dict[str, List[str]] = defaultdict(list)  # signature -> [trace_ids]

        # Detection statistics
        self.traces_analyzed = 0
        self.templates_discovered = 0
        self.multi_solution_detections = 0
        self.composition_patterns_found = 0

        # Subscribe to events
        if self.blackboard:
            self._subscribe_to_events()

        print("    [OK] Meta Strategy Learner (Agent 3.7) initialized")

    def _subscribe_to_events(self):
        """Subscribe to SOLUTION_TRACE and STRATEGY_DETECTION events."""
        try:
            self.blackboard.subscribe(
                agent_id='meta_strategy_learner_001',
                tags=['SOLUTION_TRACE'],
                callback=lambda e: self._on_solution_trace(e, 'TRACE')
            )
            self.blackboard.subscribe(
                agent_id='meta_strategy_learner_001',
                tags=['STRATEGY_DETECTION'],
                callback=lambda e: self._on_solution_trace(e, 'DETECTION')
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to events: {type(e).__name__}: {e}")

    def _on_solution_trace(self, entry, event_type: str):
        """Handle solution trace or strategy detection events."""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            if event_type == 'TRACE':
                self.analyze_trace(entry.content)
            elif event_type == 'DETECTION':
                self._process_strategy_detection(entry.content)

    def analyze_trace(self, trace: Dict) -> Optional[Dict]:
        """
        Analyze solution trace for meta-level patterns.

        Args:
            trace: SolutionTrace dictionary

        Returns:
            Dict with detected meta-patterns, or None
        """
        with self._lock:
            self.traces_analyzed += 1

            # Add to history
            self.trace_history.append(trace)
            if len(self.trace_history) > self.max_history:
                self.trace_history.pop(0)

        trace_id = trace.get('trace_id', 'unknown')
        conversation_id = trace.get('conversation_id', 'unknown')

        meta_patterns = {}

        # Detect template matches
        template_result = self._detect_template_match(trace)
        if template_result:
            meta_patterns['template'] = template_result

        # Detect multi-solution synthesis
        multi_solution_result = self._detect_multi_solution(trace)
        if multi_solution_result:
            meta_patterns['multi_solution'] = multi_solution_result

        # Mine new templates from successful solutions
        if trace.get('success', False):
            self._mine_template(trace)

        if meta_patterns:
            # Post insights to Blackboard
            self._post_meta_insights(trace_id, conversation_id, meta_patterns)
            return meta_patterns

        return None

    def _detect_template_match(self, trace: Dict) -> Optional[Dict]:
        """
        Detect if trace matches a known template.

        Returns:
            Template match info or None
        """
        problem_type = trace.get('problem_type', '')
        metadata = trace.get('metadata', {})

        # Create problem signature
        signature = self._create_problem_signature(problem_type, metadata)

        # Check against known templates
        matches = []
        for template_id, template in self.templates.items():
            if template.matches_problem(signature):
                matches.append({
                    'template_id': template_id,
                    'template_name': template.principle_name,
                    'confidence': 0.8,  # Could compute based on signature similarity
                    'expected_strategies': template.strategy_sequence
                })

        if matches:
            return {
                'matched_templates': matches,
                'signature': signature
            }

        return None

    def _detect_multi_solution(self, trace: Dict) -> Optional[Dict]:
        """
        Detect multi-solution synthesis pattern.

        Signals:
        - Multiple verification attempts
        - Alternative solution paths in metadata
        - Comparison/synthesis keywords
        """
        evidence = []
        confidence = 0.0

        metadata = trace.get('metadata', {})
        metadata_str = str(metadata).lower()
        agent_sequence = trace.get('agent_sequence', [])

        # Check for multiple solution indicators
        if 'solution_count' in metadata_str:
            solution_count = metadata.get('solution_count', 1)
            if solution_count > 1:
                evidence.append(f"Multiple solutions generated ({solution_count})")
                confidence += 0.50

        # Check for comparison/synthesis keywords
        synthesis_keywords = ['alternative', 'comparison', 'synthesis', 'multiple']
        if any(kw in metadata_str for kw in synthesis_keywords):
            evidence.append("Multi-solution synthesis keywords detected")
            confidence += 0.30

        # Check for multiple verification passes
        verification_agents = [a for a in agent_sequence if 'verif' in a.lower() or 'ax_prover' in a.lower()]
        if len(verification_agents) > 1:
            evidence.append(f"Multiple verification passes ({len(verification_agents)})")
            confidence += 0.20

        if confidence >= 0.3:
            with self._lock:
                self.multi_solution_detections += 1

            return {
                'confidence': min(confidence, 1.0),
                'evidence': evidence,
                'solution_count': metadata.get('solution_count', len(verification_agents))
            }

        return None

    def _mine_template(self, trace: Dict):
        """
        Extract a template from a successful solution.

        Creates or updates a template pattern based on trace characteristics.
        """
        problem_type = trace.get('problem_type', 'unknown')
        metadata = trace.get('metadata', {})
        agent_sequence = trace.get('agent_sequence', [])

        # Create problem signature
        signature = self._create_problem_signature(problem_type, metadata)

        # Check if we have enough similar problems to create a template
        self.problem_signatures[signature].append(trace.get('trace_id', ''))

        similar_count = len(self.problem_signatures[signature])

        if similar_count >= 3:  # Need at least 3 similar problems
            # Extract principle (simplified - would use more sophisticated analysis)
            principle = self._extract_principle(signature, agent_sequence)

            template_id = f"template_{uuid.uuid4().hex[:8]}"

            # Create or update template
            if signature not in [t.problem_signatures[0] if t.problem_signatures else ''
                                for t in self.templates.values()]:
                with self._lock:
                    self.templates_discovered += 1

                self.templates[template_id] = TemplatePattern(
                    template_id=template_id,
                    principle_name=principle,
                    description=f"Template for {problem_type} problems matching: {signature}",
                    problem_signatures=[signature],
                    strategy_sequence=[],  # Would extract from strategy detections
                    agent_pattern=agent_sequence[:3],  # First 3 agents as pattern
                    success_count=similar_count,
                    last_used=datetime.now(),
                    domains=[problem_type]
                )

    def _process_strategy_detection(self, detection_data: Dict):
        """
        Process strategy detection to learn composition patterns.

        Tracks which strategies appear together and their success rates.
        """
        strategies = detection_data.get('strategies', [])

        if len(strategies) < 2:
            return  # Need at least 2 strategies for composition

        # Extract strategy IDs
        strategy_ids = [s['strategy_id'] for s in strategies]

        # Track all pairs
        for i in range(len(strategy_ids)):
            for j in range(i + 1, len(strategy_ids)):
                pair = tuple(sorted([strategy_ids[i], strategy_ids[j]]))

                with self._lock:
                    self.strategy_pairs[pair] += 1

                # Would track success based on trace outcome
                # For now, assume successful if detected
                with self._lock:
                    self.successful_pairs[pair] += 1
                    self.composition_patterns_found += 1

    def get_composition_insights(self, min_occurrences: int = 3) -> List[Dict]:
        """
        Get insights about strategy compositions.

        Args:
            min_occurrences: Minimum number of times pair must appear

        Returns:
            List of composition insights
        """
        insights = []

        with self._lock:
            for pair, count in self.strategy_pairs.items():
                if count >= min_occurrences:
                    success_count = self.successful_pairs[pair]
                    success_rate = success_count / count if count > 0 else 0

                    # Get known composition strength
                    strategy1 = pair[0].replace('strategy_', '')
                    strategy2 = pair[1].replace('strategy_', '')
                    known_strength = compute_composition_strength(strategy1, strategy2)

                    insights.append({
                        'strategy_pair': pair,
                        'co_occurrence_count': count,
                        'success_rate': success_rate,
                        'known_synergy': known_strength,
                        'learned_synergy': success_rate,
                        'recommendation': 'strong' if success_rate > 0.7 else 'moderate' if success_rate > 0.5 else 'weak'
                    })

        # Sort by success rate
        insights.sort(key=lambda x: x['success_rate'], reverse=True)
        return insights

    def get_template_recommendations(self, problem_type: str,
                                    metadata: Dict) -> List[Dict]:
        """
        Get template recommendations for a new problem.

        Args:
            problem_type: Type of problem
            metadata: Problem metadata

        Returns:
            List of recommended templates
        """
        signature = self._create_problem_signature(problem_type, metadata)

        recommendations = []
        for template_id, template in self.templates.items():
            if template.matches_problem(signature):
                recommendations.append({
                    'template_id': template_id,
                    'principle': template.principle_name,
                    'success_count': template.success_count,
                    'expected_strategies': template.strategy_sequence,
                    'agent_pattern': template.agent_pattern
                })

        # Sort by success count
        recommendations.sort(key=lambda x: x['success_count'], reverse=True)
        return recommendations

    def _create_problem_signature(self, problem_type: str, metadata: Dict) -> str:
        """
        Create a signature string for a problem.

        Signature includes problem type and key characteristics.
        """
        # Extract key features from metadata
        features = [problem_type]

        # Add key metadata fields
        for key in ['domain', 'complexity', 'involves_proof', 'optimization']:
            if key in metadata:
                features.append(f"{key}={metadata[key]}")

        return "|".join(features)

    def _extract_principle(self, signature: str, agent_sequence: List[str]) -> str:
        """
        Extract the principle name from a problem signature.

        Simplified version - would use more sophisticated analysis.
        """
        # Extract from signature
        parts = signature.split('|')
        if len(parts) > 0:
            problem_type = parts[0]

            # Simple heuristics
            if 'optimization' in signature.lower():
                return 'extremal_optimization'
            elif 'symmetry' in signature.lower():
                return 'symmetry_exploitation'
            elif 'proof' in signature.lower():
                return 'proof_construction'
            else:
                return f"{problem_type}_standard_approach"

        return 'general_problem_solving'

    def _post_meta_insights(self, trace_id: str, conversation_id: str,
                           meta_patterns: Dict):
        """Post meta-level insights to Blackboard."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

            entry = create_entry(
                entry_type=EntryType.OBSERVATION,
                content={
                    'detection_type': 'META_STRATEGY',
                    'trace_id': trace_id,
                    'conversation_id': conversation_id,
                    'meta_patterns': meta_patterns
                },
                author_agent='meta_strategy_learner_001',
                conversation_id=conversation_id,
                tags=['STRATEGY_DETECTION', 'META', trace_id],
                metadata={
                    'detector': 'meta_strategy_learner',
                    'pattern_count': len(meta_patterns)
                }
            )

            self.blackboard.post(entry)

        except Exception as e:
            logger.debug(f"Could not post meta insights to blackboard: {type(e).__name__}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get learner statistics."""
        return {
            'traces_analyzed': self.traces_analyzed,
            'templates_discovered': self.templates_discovered,
            'multi_solution_detections': self.multi_solution_detections,
            'composition_patterns_found': self.composition_patterns_found,
            'active_templates': len(self.templates),
            'unique_signatures': len(self.problem_signatures)
        }


if __name__ == "__main__":
    """Test Meta Strategy Learner"""
    print("=" * 80)
    print("META STRATEGY LEARNER TEST")
    print("=" * 80)
    print()

    # Initialize learner
    learner = MetaStrategyLearner()
    print()

    # Test trace 1: Template matching (algebra problem)
    print("Test 1: Building Template Library")
    print("-" * 40)

    # Add similar algebra problems to build template
    for i in range(4):
        trace = {
            'trace_id': f'trace_00{i}',
            'conversation_id': f'conv_00{i}',
            'problem_type': 'algebra',
            'agent_sequence': [
                'structure_recognizer_001',
                'algebraic_solver_001',
                'ax_prover_001'
            ],
            'success': True,
            'time_taken_ms': 800 + i * 100,
            'metadata': {
                'domain': 'algebra',
                'complexity': 'medium',
                'standard_form': True
            }
        }
        result = learner.analyze_trace(trace)
        if i == 0:
            print(f"  Trace {i}: No template yet (building history)")
        elif i == 2:
            print(f"  Trace {i}: Template discovered!")
        else:
            print(f"  Trace {i}: Template match: {result.get('template', {}).get('matched_templates', [])[0]['template_name'] if result and 'template' in result else 'building'}")

    print()

    # Test trace 2: Multi-solution synthesis
    print("Test 2: Multi-Solution Synthesis Detection")
    print("-" * 40)
    trace_multi = {
        'trace_id': 'trace_multi',
        'conversation_id': 'conv_multi',
        'problem_type': 'integration',
        'agent_sequence': [
            'symbolic_integration_001',
            'numerical_integration_001',
            'ax_prover_001',
            'ax_prover_002',
            'comparison_agent_001'
        ],
        'success': True,
        'time_taken_ms': 1500,
        'metadata': {
            'solution_count': 2,
            'multiple_verification': True,
            'alternative_methods': ['symbolic', 'numerical'],
            'synthesis': 'comparison'
        }
    }

    result_multi = learner.analyze_trace(trace_multi)
    if result_multi and 'multi_solution' in result_multi:
        ms = result_multi['multi_solution']
        print(f"  Multi-solution detected: {ms['confidence']:.2%} confidence")
        print(f"  Evidence: {', '.join(ms['evidence'])}")
        print(f"  Solution count: {ms['solution_count']}")
    else:
        print("  No multi-solution pattern detected")
    print()

    # Test strategy composition tracking
    print("Test 3: Strategy Composition Learning")
    print("-" * 40)

    # Simulate strategy detections
    detections = [
        {
            'strategies': [
                {'strategy_id': 'strategy_polya_cycle'},
                {'strategy_id': 'strategy_invariant_method'}
            ]
        },
        {
            'strategies': [
                {'strategy_id': 'strategy_polya_cycle'},
                {'strategy_id': 'strategy_invariant_method'}
            ]
        },
        {
            'strategies': [
                {'strategy_id': 'strategy_polya_cycle'},
                {'strategy_id': 'strategy_invariant_method'}
            ]
        },
        {
            'strategies': [
                {'strategy_id': 'strategy_problem_re_encoding'},
                {'strategy_id': 'strategy_functional_viewpoint'}
            ]
        }
    ]

    for detection in detections:
        learner._process_strategy_detection(detection)

    insights = learner.get_composition_insights(min_occurrences=2)
    print(f"  Found {len(insights)} composition patterns:")
    for insight in insights:
        pair = insight['strategy_pair']
        print(f"    {pair[0]} + {pair[1]}")
        print(f"      Co-occurrences: {insight['co_occurrence_count']}")
        print(f"      Success rate: {insight['success_rate']:.2%}")
        print(f"      Recommendation: {insight['recommendation']}")
    print()

    # Test template recommendations
    print("Test 4: Template Recommendations")
    print("-" * 40)
    recommendations = learner.get_template_recommendations(
        'algebra',
        {'domain': 'algebra', 'complexity': 'medium'}
    )
    print(f"  Found {len(recommendations)} matching templates:")
    for rec in recommendations:
        print(f"    Template: {rec['principle']}")
        print(f"      Success count: {rec['success_count']}")
        print(f"      Agent pattern: {', '.join(rec['agent_pattern'][:3])}")
    print()

    # Show statistics
    print("LEARNER STATISTICS:")
    print("-" * 40)
    stats = learner.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print()
    print("=" * 80)
    print("META STRATEGY LEARNER TEST COMPLETE")
    print("=" * 80)
