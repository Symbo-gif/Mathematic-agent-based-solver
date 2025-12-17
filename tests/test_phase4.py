# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
PHASE 4 TESTS
=============

Comprehensive tests for Phase 4: Dynamic Governance & Resilience

TESTS COVER:
-----------
1. Conflict Resolution Team
   - Debate Moderator (FMAD Protocol)
   - Evidence Weigher (Truth Hierarchy)
   - Consensus Builder (Expertise Voting)

2. Failure Analysis Team
   - Error Classifier
   - Root Cause Analyzer
   - Alternative Path Generator

3. Meta-Learning Team
   - Performance Monitor
   - Agent Selector Optimizer
   - Adaptive Dispatcher

4. System Integration
   - Appellate Protocol
   - Post-Mortem Protocol

REFERENCE:
---------
Phase_4_Build_Order_Breakdown.md: Section 4 (Verification Checklist)
"""

import sys
import os
import unittest
from datetime import datetime

# Add paths


class TestConflictResolutionTeam(unittest.TestCase):
    """Tests for Conflict Resolution Team"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        from symbo_agentic_reasoners.middleware.conflict_resolution import (
            ConflictResolutionTeam,
            EvidenceType,
            EvidenceWeigher
        )
        cls.team = ConflictResolutionTeam()
        cls.EvidenceType = EvidenceType
        cls.weigher = EvidenceWeigher()

    def test_team_components_present(self):
        """Test: All team components are initialized"""
        self.assertIsNotNone(self.team.debate_moderator)
        self.assertIsNotNone(self.team.evidence_weigher)
        self.assertIsNotNone(self.team.consensus_builder)

    def test_evidence_hierarchy_immutable(self):
        """Test: Evidence hierarchy is properly ordered"""
        hierarchy = self.weigher.TRUTH_HIERARCHY
        self.assertEqual(hierarchy[self.EvidenceType.FORMAL_PROOF], 4)
        self.assertEqual(hierarchy[self.EvidenceType.SYMBOLIC_DERIVATION], 3)
        self.assertEqual(hierarchy[self.EvidenceType.NUMERICAL_APPROXIMATION], 2)
        self.assertEqual(hierarchy[self.EvidenceType.HEURISTIC_GUESS], 1)

    def test_conflict_detection(self):
        """Test: Conflict detection works correctly"""
        # Same results - no conflict
        results_same = [
            {'agent_id': 'a1', 'result': 'x^2'},
            {'agent_id': 'a2', 'result': 'x^2'}
        ]
        self.assertFalse(self.team.check_for_conflict(results_same))

        # Different results - conflict
        results_diff = [
            {'agent_id': 'a1', 'result': 'x^2'},
            {'agent_id': 'a2', 'result': 'x^2 + 1'}
        ]
        self.assertTrue(self.team.check_for_conflict(results_diff))

    def test_symbolic_beats_numerical(self):
        """Test: Symbolic derivation beats numerical approximation"""
        conflict_data = {
            'subtask_id': 'test_001',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'symbolic_001',
                    'result': 'x^2',
                    'method_used': 'symbolic_algebra',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'numerical_001',
                    'result': 'x^2.0001',
                    'method_used': 'numerical_approximation',
                    'evidence_type': 'NUMERICAL_APPROXIMATION',
                    'confidence': 0.99
                }
            ]
        }

        ruling = self.team.resolve_conflict(conflict_data)
        self.assertEqual(ruling.ruling_type, 'AUTOMATIC')
        self.assertEqual(ruling.winner_agent, 'symbolic_001')
        self.assertEqual(ruling.evidence_type, 'SYMBOLIC_DERIVATION')

    def test_formal_proof_beats_all(self):
        """Test: Formal proof beats all other evidence types"""
        conflict_data = {
            'subtask_id': 'test_002',
            'domain': 'algebra',
            'results': [
                {
                    'agent_id': 'prover_001',
                    'result': 'QED',
                    'method_used': 'ax_prover',
                    'ax_prover_verified': True,
                    'confidence': 1.0
                },
                {
                    'agent_id': 'symbolic_001',
                    'result': 'True',
                    'method_used': 'symbolic_derivation',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.95
                }
            ]
        }

        ruling = self.team.resolve_conflict(conflict_data)
        self.assertEqual(ruling.winner_agent, 'prover_001')
        self.assertEqual(ruling.evidence_type, 'FORMAL_PROOF')


class TestFailureAnalysisTeam(unittest.TestCase):
    """Tests for Failure Analysis Team"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        from symbo_agentic_reasoners.middleware.failure_analysis_team import (
            FailureAnalysisTeam,
            ErrorType,
            RemedyAction
        )
        cls.team = FailureAnalysisTeam()
        cls.ErrorType = ErrorType
        cls.RemedyAction = RemedyAction

    def test_team_components_present(self):
        """Test: All team components are initialized"""
        self.assertIsNotNone(self.team.error_classifier)
        self.assertIsNotNone(self.team.root_cause_analyzer)
        self.assertIsNotNone(self.team.alternative_path_generator)

    def test_timeout_classified_as_computational(self):
        """Test: Timeout errors are classified as COMPUTATIONAL"""
        error_type, remedy = self.team.classify_error(
            "Timeout exceeded: operation took > 30 seconds"
        )
        self.assertEqual(error_type, self.ErrorType.COMPUTATIONAL)
        self.assertEqual(remedy, self.RemedyAction.REQUEST_RESOURCES)

    def test_memory_classified_as_computational(self):
        """Test: Memory errors are classified as COMPUTATIONAL"""
        error_type, remedy = self.team.classify_error(
            "Out of memory: cannot allocate buffer"
        )
        self.assertEqual(error_type, self.ErrorType.COMPUTATIONAL)
        self.assertEqual(remedy, self.RemedyAction.REQUEST_RESOURCES)

    def test_invalid_inference_classified_as_logical(self):
        """Test: Invalid inference errors are classified as LOGICAL"""
        error_type, remedy = self.team.classify_error(
            "Assertion failed: step 3 does not follow from step 2"
        )
        self.assertEqual(error_type, self.ErrorType.LOGICAL)
        self.assertEqual(remedy, self.RemedyAction.TRIGGER_REFINEMENT)

    def test_domain_error_classified_correctly(self):
        """Test: Domain errors are classified as DOMAIN"""
        error_type, remedy = self.team.classify_error(
            "Cannot apply method: precondition violation"
        )
        self.assertEqual(error_type, self.ErrorType.DOMAIN)
        self.assertEqual(remedy, self.RemedyAction.TRIGGER_ALTERNATIVE)

    def test_alternative_generated_for_domain_error(self):
        """Test: Alternative plan generated for domain errors"""
        result = self.team.handle_failure({
            'error_message': 'Cannot apply Risch algorithm: not elementary',
            'agent_id': 'symbolic_integration_001',
            'step': 'symbolic_integration',
            'conversation_id': 'test_001'
        })

        self.assertIn('recovery_plan', result)
        self.assertIsNotNone(result['recovery_plan'])
        self.assertIn('strategies', result['recovery_plan'])
        self.assertTrue(len(result['recovery_plan']['strategies']) > 0)

    def test_fallback_strategies_defined(self):
        """Test: Fallback strategies are properly defined"""
        from symbo_agentic_reasoners.middleware.failure_analysis_team import (
            AlternativePathGenerator
        )
        gen = AlternativePathGenerator()

        strategies = gen.FALLBACK_STRATEGIES
        self.assertIn('symbolic_integration', strategies)
        self.assertIn('matrix_inversion', strategies)
        self.assertIn('algebraic_solving', strategies)


class TestMetaLearningTeam(unittest.TestCase):
    """Tests for Meta-Learning Team"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        from symbo_agentic_reasoners.middleware.meta_learning_team import (
            MetaLearningTeam,
            ComplexityLevel
        )
        cls.team = MetaLearningTeam()
        cls.ComplexityLevel = ComplexityLevel

    def test_team_components_present(self):
        """Test: All team components are initialized"""
        self.assertIsNotNone(self.team.performance_monitor)
        self.assertIsNotNone(self.team.optimizer)
        self.assertIsNotNone(self.team.dispatcher)

    def test_trace_logging(self):
        """Test: Solution traces are properly logged"""
        # Log a complete trace
        self.team.log_task_start('test_conv', 'integration')
        self.team.log_agent_invocation('test_conv', 'integration_001', 100)
        self.team.log_verification('test_conv', 'VERIFIED')
        trace = self.team.log_session_end('test_conv')

        self.assertIsNotNone(trace)
        self.assertEqual(trace.problem_type, 'integration')
        self.assertTrue(trace.success)
        self.assertIn('integration_001', trace.agent_sequence)

    def test_complexity_estimation_simple(self):
        """Test: Simple problems get low complexity"""
        simple_context = {
            'problem_type': 'algebra',
            'simple_expression': True,
            'standard_form': True
        }
        rec = self.team.get_team_recommendation(simple_context)
        self.assertEqual(rec['complexity_level'], 'SIMPLE')
        self.assertEqual(rec['team_size'], 3)  # Skeleton crew

    def test_complexity_estimation_complex(self):
        """Test: Complex problems get high complexity"""
        complex_context = {
            'problem_type': 'proof',
            'involves_proof': True,
            'multiple_steps': True,
            'novel_pattern': True
        }
        rec = self.team.get_team_recommendation(complex_context)
        self.assertEqual(rec['complexity_level'], 'COMPLEX')
        self.assertEqual(rec['team_size'], 12)  # Full debate team

    def test_routing_table_computation(self):
        """Test: Routing tables are computed from traces"""
        # Add some traces
        for i in range(10):
            self.team.log_task_start(f'routing_test_{i}', 'calculus')
            self.team.log_agent_invocation(f'routing_test_{i}', 'calculus_agent', 50)
            self.team.log_verification(f'routing_test_{i}', 'VERIFIED')
            self.team.log_session_end(f'routing_test_{i}')

        # Run optimization
        results = self.team.run_batch_optimization()

        self.assertIn('tables_updated', results)
        self.assertGreater(results['tables_updated'], 0)

    def test_team_size_scaling(self):
        """Test: Team size scales with complexity"""
        dispatcher = self.team.dispatcher

        # Simple -> Skeleton Crew
        simple = {'simple_expression': True}
        size1 = dispatcher.determine_team_size(simple)
        self.assertEqual(size1, 3)

        # Complex -> Full Team
        complex_ctx = {'involves_proof': True, 'novel_pattern': True, 'multiple_steps': True}
        size2 = dispatcher.determine_team_size(complex_ctx)
        self.assertEqual(size2, 12)


class TestProtocolIntegration(unittest.TestCase):
    """Tests for Protocol Integration"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        from symbo_agentic_reasoners.integration.protocol_updates import (
            OrchestratorPhase4Update,
            ConflictDetector
        )
        cls.OrchestratorPhase4Update = OrchestratorPhase4Update
        cls.ConflictDetector = ConflictDetector

    def test_conflict_detector_same_results(self):
        """Test: Conflict detector identifies matching results"""
        detector = self.ConflictDetector()

        results = [
            {'result': 'x^2'},
            {'result': 'x^2'}
        ]
        self.assertFalse(detector.check_results(results))

    def test_conflict_detector_different_results(self):
        """Test: Conflict detector identifies different results"""
        detector = self.ConflictDetector()

        results = [
            {'result': 'x^2'},
            {'result': 'x^3'}
        ]
        self.assertTrue(detector.check_results(results))

    def test_conflict_detector_numerical_tolerance(self):
        """Test: Conflict detector handles numerical tolerance"""
        detector = self.ConflictDetector(tolerance=1e-6)

        results = [
            {'result': 3.14159265},
            {'result': 3.14159266}
        ]
        # These should match within tolerance
        self.assertFalse(detector.check_results(results))

    def test_protocol_update_initialization(self):
        """Test: Protocol update initializes correctly"""
        class MockOrchestrator:
            def accept_result(self, r):
                return r

        update = self.OrchestratorPhase4Update(
            orchestrator=MockOrchestrator()
        )

        self.assertTrue(update.appellate_active)


class TestPhase4Integration(unittest.TestCase):
    """Integration tests for complete Phase 4 system"""

    @classmethod
    def setUpClass(cls):
        """Set up integration test - this may take a moment"""
        # Skip if imports fail (infrastructure not available)
        try:
            from symbo_agentic_reasoners.core.system import Phase4System
            cls.system = Phase4System()
            cls.system_available = True
        except Exception as e:
            print(f"Phase 4 system initialization skipped: {e}")
            cls.system_available = False

    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        if cls.system_available:
            try:
                cls.system.shutdown()
            except Exception:
                pass

    def test_system_health_check(self):
        """Test: Full system health check passes"""
        if not self.system_available:
            self.skipTest("Phase 4 system not available")

        health = self.system.health_check()
        self.assertTrue(health['conflict_resolution_team'])
        self.assertTrue(health['failure_analysis_team'])
        self.assertTrue(health['meta_learning_team'])

    def test_end_to_end_conflict_resolution(self):
        """Test: End-to-end conflict resolution works"""
        if not self.system_available:
            self.skipTest("Phase 4 system not available")

        conflict_data = {
            'subtask_id': 'e2e_test',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'symbolic_001',
                    'result': 'sin(x)',
                    'method_used': 'symbolic',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'heuristic_001',
                    'result': 'sin(x)',
                    'method_used': 'pattern_match',
                    'evidence_type': 'HEURISTIC_GUESS',
                    'confidence': 0.8
                }
            ]
        }

        ruling = self.system.resolve_conflict(conflict_data)
        self.assertIsNotNone(ruling)
        self.assertEqual(ruling.winner_agent, 'symbolic_001')

    def test_end_to_end_failure_recovery(self):
        """Test: End-to-end failure recovery works"""
        if not self.system_available:
            self.skipTest("Phase 4 system not available")

        failure_data = {
            'error_message': 'Integration timeout exceeded',
            'agent_id': 'integration_001',
            'step': 'symbolic_integration',
            'conversation_id': 'e2e_failure'
        }

        result = self.system.handle_failure(failure_data)
        self.assertIn('report', result)
        self.assertEqual(result['report']['error_type'], 'COMPUTATIONAL')


def run_tests():
    """Run all Phase 4 tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConflictResolutionTeam))
    suite.addTests(loader.loadTestsFromTestCase(TestFailureAnalysisTeam))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaLearningTeam))
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4Integration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 4 TEST SUITE")
    print("=" * 80)
    print()

    result = run_tests()

    print()
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 80)
