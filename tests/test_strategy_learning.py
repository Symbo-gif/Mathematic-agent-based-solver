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
Strategy Learning System - Comprehensive Test Suite
====================================================

Tests all components of the strategy learning system:
- Strategy detectors
- Strategy learner agents (3.4-3.7)
- Strategy coordinator (3.8)
- Strategy transfer engine
- KnowledgeGraph integration
- Meta-learning integration

USAGE:
------
python -m pytest tests/test_strategy_learning.py -v
or
python tests/test_strategy_learning.py
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.middleware.strategy_learning.strategy_patterns import (
    StrategyPattern, StrategyDetectionResult, StrategyCategory
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_detectors import (
    detect_polya_cycle, detect_problem_re_encoding, detect_invariant_method,
    detect_extremal_elements, detect_all_strategies
)
from symbo_agentic_reasoners.middleware.strategy_learning.structural_strategy_learner import (
    StructuralStrategyLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.heuristic_pattern_learner import (
    HeuristicPatternLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.nonstandard_move_learner import (
    NonStandardMoveLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.meta_strategy_learner import (
    MetaStrategyLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_coordinator import (
    StrategyCoordinator
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_transfer_engine import (
    StrategyTransferEngine, TransferCandidate
)


class TestStrategyDetectors(unittest.TestCase):
    """Test individual strategy detector functions."""

    def setUp(self):
        """Set up test trace data."""
        self.polya_trace = {
            'agent_sequence': [
                'structure_recognizer_001',
                'decomposition_agent_001',
                'solver_001',
                'ax_prover_001'
            ],
            'metadata': {
                'problem_reformulated': True,
                'decompose': True,
                'retrospective_check': True
            }
        }

        self.invariant_trace = {
            'agent_sequence': [
                'symmetry_specialist_001',
                'invariant_measure_001'
            ],
            'metadata': {
                'invariant_found': True,
                'preserved_quantity': 'energy'
            }
        }

    def test_polya_cycle_detection(self):
        """Test Pólya Cycle detection."""
        result = detect_polya_cycle(
            self.polya_trace['agent_sequence'],
            self.polya_trace['metadata']
        )

        self.assertGreaterEqual(result.confidence, 0.7)
        self.assertGreater(len(result.evidence), 0)
        self.assertIn('phase', result.evidence[0].lower())

    def test_invariant_method_detection(self):
        """Test Invariant Method detection."""
        result = detect_invariant_method(
            self.invariant_trace['agent_sequence'],
            self.invariant_trace['metadata']
        )

        self.assertGreaterEqual(result.confidence, 0.7)
        self.assertIn('invariant', ' '.join(result.evidence).lower())

    def test_detect_all_strategies(self):
        """Test comprehensive strategy detection."""
        results = detect_all_strategies(
            self.polya_trace['agent_sequence'],
            self.polya_trace['metadata'],
            min_confidence=0.3
        )

        self.assertGreater(len(results), 0)
        self.assertIn('polya_cycle', results)


class TestStrategyLearners(unittest.TestCase):
    """Test strategy learner agents."""

    def setUp(self):
        """Set up test learners."""
        self.structural_learner = StructuralStrategyLearner()
        self.heuristic_learner = HeuristicPatternLearner()
        self.nonstandard_learner = NonStandardMoveLearner()
        self.meta_learner = MetaStrategyLearner()

    def test_structural_learner_detection(self):
        """Test structural strategy learner."""
        trace = {
            'trace_id': 'test_001',
            'conversation_id': 'conv_001',
            'problem_type': 'algebra',
            'agent_sequence': [
                'structure_recognizer_001',
                'decomposition_agent_001',
                'ax_prover_001'
            ],
            'success': True,
            'time_taken_ms': 1000,
            'metadata': {
                'problem_reformulated': True,
                'decomposition_applied': True
            }
        }

        detection = self.structural_learner.analyze_trace(trace)

        self.assertIsNotNone(detection)
        self.assertGreater(len(detection.detected_strategies), 0)

    def test_heuristic_learner_detection(self):
        """Test heuristic pattern learner."""
        trace = {
            'trace_id': 'test_002',
            'conversation_id': 'conv_002',
            'problem_type': 'optimization',
            'agent_sequence': [
                'optimization_agent_001',
                'extremal_analysis_001'
            ],
            'success': True,
            'time_taken_ms': 900,
            'metadata': {
                'extremal_element': 'maximum',
                'optimization_applied': True
            }
        }

        detection = self.heuristic_learner.analyze_trace(trace)

        self.assertIsNotNone(detection)
        self.assertTrue(
            any(s.strategy_name == 'Extremal Elements'
                for s in detection.detected_strategies)
        )

    def test_nonstandard_learner_detection(self):
        """Test nonstandard move learner."""
        trace = {
            'trace_id': 'test_003',
            'conversation_id': 'conv_003',
            'problem_type': 'number_theory',
            'agent_sequence': [
                'number_theory_specialist_001',
                'contradiction_prover_001'
            ],
            'success': True,
            'time_taken_ms': 1200,
            'metadata': {
                'proof_method': 'contradiction',
                'descent_applied': True
            }
        }

        detection = self.nonstandard_learner.analyze_trace(trace)

        self.assertIsNotNone(detection)
        self.assertTrue(
            any(s.strategy_name == 'Infinite Descent'
                for s in detection.detected_strategies)
        )

    def test_meta_learner_template_mining(self):
        """Test meta learner template mining."""
        # Add similar traces to build template
        for i in range(4):
            trace = {
                'trace_id': f'test_00{i}',
                'conversation_id': f'conv_00{i}',
                'problem_type': 'algebra',
                'agent_sequence': ['structure_recognizer_001', 'solver_001'],
                'success': True,
                'time_taken_ms': 800,
                'metadata': {'domain': 'algebra'}
            }
            self.meta_learner.analyze_trace(trace)

        self.assertGreater(self.meta_learner.templates_discovered, 0)

    def test_learner_statistics(self):
        """Test learner statistics."""
        stats = self.structural_learner.get_statistics()

        self.assertIn('traces_analyzed', stats)
        self.assertIn('detections_made', stats)
        self.assertGreaterEqual(stats['traces_analyzed'], 0)


class TestStrategyCoordinator(unittest.TestCase):
    """Test strategy coordinator."""

    def setUp(self):
        """Set up coordinator."""
        self.coordinator = StrategyCoordinator()

    def test_coordinator_initialization(self):
        """Test coordinator initializes all learners."""
        self.assertIsNotNone(self.coordinator.structural_learner)
        self.assertIsNotNone(self.coordinator.heuristic_learner)
        self.assertIsNotNone(self.coordinator.nonstandard_learner)
        self.assertIsNotNone(self.coordinator.meta_learner)

    def test_coordinator_aggregation(self):
        """Test strategy aggregation."""
        trace = {
            'trace_id': 'test_agg',
            'conversation_id': 'conv_agg',
            'problem_type': 'optimization',
            'agent_sequence': [
                'structure_recognizer_001',
                'symmetry_specialist_001',
                'optimization_agent_001'
            ],
            'success': True,
            'time_taken_ms': 1500,
            'metadata': {
                'decompose': True,
                'symmetry_detected': True,
                'extremal_element': 'maximum'
            }
        }

        aggregated = self.coordinator.analyze_trace(trace)

        self.assertIsNotNone(aggregated)
        self.assertGreater(len(aggregated.all_strategies), 0)
        self.assertIsNotNone(aggregated.dominant_strategy)

    def test_coordinator_strategy_recommendation(self):
        """Test strategy recommendations."""
        problem_context = {
            'problem_type': 'algebra',
            'metadata': {'complexity': 'medium'}
        }

        recommendation = self.coordinator.get_strategy_recommendation(problem_context)

        self.assertIn('problem_type', recommendation)
        self.assertIn('suggested_templates', recommendation)

    def test_coordinator_statistics(self):
        """Test coordinator statistics."""
        stats = self.coordinator.get_statistics()

        self.assertIn('coordinator', stats)
        self.assertIn('structural_learner', stats)
        self.assertGreaterEqual(stats['coordinator']['coordinations'], 0)


class TestStrategyTransferEngine(unittest.TestCase):
    """Test strategy transfer engine."""

    def setUp(self):
        """Set up transfer engine."""
        self.engine = StrategyTransferEngine()

    def test_domain_mappings(self):
        """Test domain concept mappings."""
        self.assertGreater(len(self.engine.domain_mappings), 0)

        # Check algebra->geometry mapping exists
        key = ('algebra', 'geometry')
        self.assertIn(key, self.engine.domain_mappings)

        mapping = self.engine.domain_mappings[key]
        self.assertGreater(len(mapping.concept_mappings), 0)
        self.assertGreater(mapping.similarity_score, 0)

    def test_transfer_result_recording(self):
        """Test recording transfer results."""
        candidate = TransferCandidate(
            strategy_id='strategy_test',
            strategy_name='Test Strategy',
            category=StrategyCategory.HEURISTIC,
            source_domain='algebra',
            target_domain='geometry',
            source_effectiveness=0.8,
            estimated_target_effectiveness=0.7,
            transfer_confidence='high',
            adaptation_needed=[],
            supporting_evidence=[]
        )

        self.engine.record_transfer_result(
            transfer_id='transfer_test',
            candidate=candidate,
            success=True,
            actual_effectiveness=0.72
        )

        self.assertEqual(self.engine.transfers_attempted, 1)
        self.assertEqual(self.engine.successful_transfers, 1)

    def test_transfer_statistics(self):
        """Test transfer engine statistics."""
        stats = self.engine.get_statistics()

        self.assertIn('transfers_proposed', stats)
        self.assertIn('transfers_attempted', stats)
        self.assertIn('domain_mappings', stats)
        self.assertGreater(stats['domain_mappings'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete system."""

    def test_end_to_end_strategy_learning(self):
        """Test complete strategy learning pipeline."""
        # Create coordinator
        coordinator = StrategyCoordinator()

        # Simulate solution trace with multiple strategies
        trace = {
            'trace_id': 'integration_001',
            'conversation_id': 'conv_int_001',
            'problem_type': 'optimization',
            'agent_sequence': [
                'structure_recognizer_001',
                'decomposition_agent_001',
                'symmetry_specialist_001',
                'optimization_agent_001',
                'ax_prover_001'
            ],
            'success': True,
            'time_taken_ms': 2000,
            'metadata': {
                'problem_reformulated': True,
                'decomposition_applied': True,
                'symmetry_detected': True,
                'extremal_element': 'maximum',
                'optimization_applied': True
            }
        }

        # Analyze trace
        aggregated = coordinator.analyze_trace(trace)

        # Verify multi-strategy detection
        self.assertIsNotNone(aggregated)
        self.assertGreater(len(aggregated.all_strategies), 1)

        # Verify different categories detected
        categories = set(s.category for s in aggregated.all_strategies)
        self.assertGreater(len(categories), 1)

        # Verify confidence calculation
        self.assertGreater(aggregated.confidence_score, 0)

        print(f"\n[Integration Test] Detected {len(aggregated.all_strategies)} strategies")
        print(f"  Dominant: {aggregated.dominant_strategy.strategy_name}")
        print(f"  Confidence: {aggregated.confidence_score:.2%}")


def run_tests():
    """Run all tests."""
    print("=" * 80)
    print("STRATEGY LEARNING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyDetectors))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyLearners))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyCoordinator))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyTransferEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 80)
    print(f"TESTS RUN: {result.testsRun}")
    print(f"PASSED: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"FAILED: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
