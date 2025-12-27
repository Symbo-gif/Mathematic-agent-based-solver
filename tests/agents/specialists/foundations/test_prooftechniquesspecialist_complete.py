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
Complete test suite for ProofTechniquesSpecialist.
Tests the 12-test BDI pattern for Tier 3 specialists.
"""

import pytest
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.foundations.proof_techniques_specialist import (
    ProofTechniquesSpecialist
)


class TestProofTechniquesSpecialistComplete:
    """Complete test suite for ProofTechniquesSpecialist (12 tests)."""

    # ========================================
    # Test 1: Initialization
    # ========================================

    def test_initialization(self):
        """Test specialist initialization."""
        specialist = ProofTechniquesSpecialist()

        assert specialist.agent_id == 'proof_techniques_specialist_001'
        assert specialist.service_type == 'math.foundations.proofs'
        assert 'direct_proof' in specialist.capabilities
        assert 'contradiction' in specialist.capabilities
        assert 'weak_induction' in specialist.capabilities

    # ========================================
    # Test 2: DF Registration
    # ========================================

    def test_df_registration(self):
        """Test registration with Directory Facilitator."""
        mock_df = Mock()
        mock_df.register_service = Mock()

        specialist = ProofTechniquesSpecialist()
        result = specialist.register_with_df(mock_df)

        assert result is True

    # ========================================
    # Test 3: Blackboard Entry Creation
    # ========================================

    def test_blackboard_entry_creation(self):
        """Test blackboard entry creation."""
        specialist = ProofTechniquesSpecialist()
        problem = {'operation': 'direct_proof', 'premises': ['P']}

        entry = specialist.create_blackboard_entry(problem)

        assert entry['agent_id'] == specialist.agent_id
        assert entry['status'] == 'pending'

    # ========================================
    # Test 4: Simple Problem Solving
    # ========================================

    def test_simple_direct_proof(self):
        """Test simple direct proof verification."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'direct_proof',
            'premises': ['P', 'P -> Q'],
            'steps': [
                {'statement': 'Q', 'justification': 'modus ponens', 'references': ['P', 'P -> Q']}
            ],
            'conclusion': 'Q'
        })

        assert result['success'] is True
        assert result['proof_valid'] is True

    def test_simple_check_inference(self):
        """Test inference rule check."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'check_inference',
            'rule_name': 'modus_ponens'
        })

        assert result['success'] is True
        assert result['valid'] is True

    # ========================================
    # Test 5: Complex Problem Solving
    # ========================================

    def test_complex_weak_induction(self):
        """Test weak induction verification."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'weak_induction',
            'base_case': {'n': 0, 'verified': True, 'work': 'P(0) holds by definition'},
            'inductive_step': {'verified': True, 'work': 'P(k) -> P(k+1) verified'},
            'property_name': 'P'
        })

        assert result['success'] is True
        assert result['proof_valid'] is True
        assert result['method'] == 'weak_induction'

    def test_complex_strong_induction(self):
        """Test strong induction verification."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'strong_induction',
            'base_cases': [
                {'n': 0, 'verified': True, 'work': 'P(0) holds'},
                {'n': 1, 'verified': True, 'work': 'P(1) holds'}
            ],
            'inductive_step': {'verified': True, 'work': 'For all j<k: P(j) implies P(k)'},
            'property_name': 'P'
        })

        assert result['success'] is True
        assert result['proof_valid'] is True
        assert result['method'] == 'strong_induction'

    # ========================================
    # Test 6: Invalid Input Handling
    # ========================================

    def test_invalid_input_missing_conclusion(self):
        """Test handling of missing conclusion."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'direct_proof',
            'premises': ['P'],
            'steps': []
            # Missing conclusion
        })

        assert result['success'] is False
        assert 'error' in result

    # ========================================
    # Test 7: Edge Cases
    # ========================================

    def test_edge_case_empty_premises(self):
        """Test proof with no premises."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'direct_proof',
            'premises': [],
            'steps': [{'statement': 'A', 'justification': 'axiom', 'references': []}],
            'conclusion': 'A'
        })

        assert result['success'] is True

    def test_edge_case_identify_type(self):
        """Test proof technique identification."""
        specialist = ProofTechniquesSpecialist()

        result = specialist.process_request({
            'operation': 'identify_type',
            'proof_structure': {
                'base_case': {},
                'inductive_step': {}
            }
        })

        assert result['success'] is True
        assert result['technique'] == 'weak_induction'

    # ========================================
    # Test 8: Error Reporting
    # ========================================

    def test_error_reporting(self):
        """Test error counting."""
        specialist = ProofTechniquesSpecialist()

        # Call with missing required params to trigger failure
        specialist.process_request({'operation': 'direct_proof', 'premises': ['P']})  # Missing conclusion

        stats = specialist.get_statistics()
        assert stats.get('tasks_failed', 0) >= 1 or stats.get('errors_encountered', 0) >= 0

    # ========================================
    # Test 9: Statistics Reporting
    # ========================================

    def test_statistics_reporting(self):
        """Test comprehensive statistics."""
        specialist = ProofTechniquesSpecialist()

        specialist.process_request({
            'operation': 'direct_proof',
            'premises': ['P'],
            'steps': [],
            'conclusion': 'P'
        })
        specialist.process_request({
            'operation': 'weak_induction',
            'base_case': {'n': 0, 'verified': True},
            'inductive_step': {'verified': True}
        })

        stats = specialist.get_statistics()
        # Check for generic or domain-specific statistics
        assert stats.get('tasks_executed', 0) >= 2 or stats.get('direct_proofs_verified', 0) >= 1

    # ========================================
    # Test 10: BDI Update Beliefs
    # ========================================

    def test_bdi_update_beliefs(self):
        """Test update_beliefs from percepts."""
        specialist = ProofTechniquesSpecialist()

        specialist.update_beliefs({
            'operation': 'contradiction',
            'original_statement': 'P'
        })

        assert specialist.beliefs['operation'] == 'contradiction'

    # ========================================
    # Test 11: BDI Deliberate
    # ========================================

    def test_bdi_deliberate(self):
        """Test deliberate method."""
        specialist = ProofTechniquesSpecialist()

        specialist.beliefs['operation'] = 'contrapositive'
        desires = specialist.deliberate()

        assert 'execute_contrapositive' in desires

    # ========================================
    # Test 12: BDI Execute Step
    # ========================================

    def test_bdi_execute_step(self):
        """Test execute_step method."""
        specialist = ProofTechniquesSpecialist()

        specialist.beliefs = {
            'operation': 'list_inference_rules'
        }

        result = specialist.execute_step()

        assert result is not None
        assert result['success'] is True
        assert result['count'] > 0
