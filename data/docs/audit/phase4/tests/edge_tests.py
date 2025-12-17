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

import unittest
import sys
import os
from dataclasses import dataclass, field
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from symbo_agentic_reasoners_phase4.phase4_system import Phase4System
from symbo_agentic_reasoners_phase4.governance.conflict_resolution import EvidenceType, Ruling
from symbo_agentic_reasoners_phase4.failure_analysis.failure_analysis_team import ErrorType, RemedyAction

class Phase4EdgeTests(unittest.TestCase):
    """
    Edge tests for Phase 4 System.
    Verifies specific capabilities and boundary conditions of the Self-Correcting System.
    """

    @classmethod
    def setUpClass(cls):
        print("\n[EdgeTests] Initializing Phase 4 System...")
        cls.system = Phase4System()
        cls.system.start()

    @classmethod
    def tearDownClass(cls):
        print("\n[EdgeTests] Shutting down Phase 4 System...")
        cls.system.shutdown()

    # -------------------------------------------------------------------------
    # Conflict Resolution Tests
    # -------------------------------------------------------------------------

    def test_conflict_resolution_hierarchy(self):
        """Test that Symbolic Derivation beats Numerical Approximation."""
        conflict_data = {
            'subtask_id': 'test_conflict_1',
            'conversation_id': 'test_conv_1',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'symbolic_agent',
                    'result': 'exact_answer',
                    'method_used': 'symbolic_method',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'numerical_agent',
                    'result': 'approx_answer',
                    'method_used': 'numerical_method',
                    'evidence_type': 'NUMERICAL_APPROXIMATION',
                    'confidence': 0.99
                }
            ]
        }
        ruling = self.system.resolve_conflict(conflict_data)
        self.assertEqual(ruling.winner_agent, 'symbolic_agent')
        self.assertEqual(ruling.ruling_type, 'AUTOMATIC')

    def test_conflict_resolution_consensus(self):
        """Test that consensus is reached when hierarchy is equal."""
        # Both provide symbolic derivation, but one has higher weighted score
        # Assuming 'calculus_supervisor' gets 2.0 weight in 'calculus' domain
        conflict_data = {
            'subtask_id': 'test_conflict_2',
            'conversation_id': 'test_conv_2',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'calculus_supervisor_agent',
                    'result': 'expert_answer',
                    'method_used': 'symbolic_method',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.8  # Weighted: 0.8 * 2.0 = 1.6
                },
                {
                    'agent_id': 'general_agent',
                    'result': 'general_answer',
                    'method_used': 'symbolic_method',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9  # Weighted: 0.9 * 1.0 = 0.9
                }
            ]
        }
        ruling = self.system.resolve_conflict(conflict_data)
        self.assertEqual(ruling.winner_agent, 'calculus_supervisor_agent')
        self.assertEqual(ruling.ruling_type, 'CONSENSUS')

    # -------------------------------------------------------------------------
    # Failure Analysis Tests
    # -------------------------------------------------------------------------

    def test_failure_handling_domain_error(self):
        """Test that a domain error triggers an alternative plan."""
        failure_data = {
            'error_message': 'Method inapplicable: domain error',
            'agent_id': 'test_agent',
            'step': 'test_step',
            'conversation_id': 'test_fail_1'
        }
        result = self.system.handle_failure(failure_data)
        self.assertEqual(result['report']['error_type'], ErrorType.DOMAIN.name)
        self.assertEqual(result['report']['remedy_action'], RemedyAction.TRIGGER_ALTERNATIVE.name)
        self.assertIsNotNone(result.get('recovery_plan'))

    def test_failure_handling_computational_error(self):
        """Test that a computational error suggests resource increase."""
        failure_data = {
            'error_message': 'Timeout exceeded',
            'agent_id': 'test_agent',
            'step': 'test_step',
            'conversation_id': 'test_fail_2'
        }
        result = self.system.handle_failure(failure_data)
        self.assertEqual(result['report']['error_type'], ErrorType.COMPUTATIONAL.name)
        self.assertEqual(result['report']['remedy_action'], RemedyAction.REQUEST_RESOURCES.name)

    # -------------------------------------------------------------------------
    # Meta-Learning Tests
    # -------------------------------------------------------------------------

    def test_team_recommendation(self):
        """Test team recommendation logic."""
        # Simple problem
        simple_context = {'problem_type': 'algebra', 'simple_expression': True}
        rec_simple = self.system.get_team_recommendation(simple_context)
        self.assertTrue(rec_simple['team_size'] < 5)

        # Complex problem
        complex_context = {'problem_type': 'proof', 'involves_proof': True}
        rec_complex = self.system.get_team_recommendation(complex_context)
        self.assertTrue(rec_complex['team_size'] > 5)

    def test_optimization_trigger(self):
        """Test that optimization runs without error."""
        try:
            results = self.system.run_optimization()
            self.assertIn('tables_updated', results)
        except Exception as e:
            self.fail(f"Optimization failed with error: {e}")

if __name__ == '__main__':
    unittest.main()
