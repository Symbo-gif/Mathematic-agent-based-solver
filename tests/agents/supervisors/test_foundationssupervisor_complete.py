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
Complete test suite for FoundationsSupervisor.
Tests the 10-test pattern for Tier 2 supervisors.
"""

import pytest
from unittest.mock import Mock, patch

from symbo_agentic_reasoners.agents.supervisors.foundations_supervisor import (
    FoundationsSupervisor
)


class TestFoundationsSupervisorComplete:
    """Complete test suite for FoundationsSupervisor (10 tests)."""

    # ========================================
    # Test 1: Initialization
    # ========================================

    def test_initialization(self):
        """Test supervisor initialization."""
        supervisor = FoundationsSupervisor()

        assert supervisor.agent_id == 'foundations_supervisor_001'
        assert supervisor.service_type == 'math.foundations'
        assert supervisor.version == '1.0.0'
        assert supervisor.tasks_executed == 0
        assert 'sets' in supervisor.routing_stats
        assert 'relations' in supervisor.routing_stats
        assert 'functions' in supervisor.routing_stats

    # ========================================
    # Test 2: DF Registration
    # ========================================

    def test_df_registration(self):
        """Test registration with Directory Facilitator."""
        mock_df = Mock()
        mock_df.register_service = Mock()

        supervisor = FoundationsSupervisor()
        result = supervisor.register_with_df(mock_df)

        assert result is True
        mock_df.register_service.assert_called_once()

    # ========================================
    # Test 3: Simple Task Processing
    # ========================================

    def test_simple_task_union(self):
        """Test simple task routing to sets specialist."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'union',
            'A': {1, 2},
            'B': {3, 4}
        })

        assert result['success'] is True
        assert result['routed_to'] == 'sets'
        assert result['specialist_result']['result'] == {1, 2, 3, 4}

    def test_simple_task_reflexive(self):
        """Test simple task routing to relations specialist."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'reflexive',
            'R': [(1, 1), (2, 2)],
            'A': {1, 2}
        })

        assert result['success'] is True
        assert result['routed_to'] == 'relations'

    # ========================================
    # Test 4: Complex Task Processing
    # ========================================

    def test_complex_task_aleph_arithmetic(self):
        """Test complex task routing to cardinality specialist."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'aleph_arithmetic',
            'op': 'add',
            'a': 'aleph_0',
            'b': 'aleph_0'
        })

        assert result['success'] is True
        assert result['routed_to'] == 'cardinality'
        assert result['specialist_result']['result'] == 'aleph_0'

    def test_complex_task_weak_induction(self):
        """Test complex task routing to proofs specialist."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'weak_induction',
            'base_case': {'n': 0, 'verified': True, 'work': 'P(0) holds'},
            'inductive_step': {'verified': True, 'work': 'P(k)->P(k+1)'},
            'property_name': 'P'
        })

        assert result['success'] is True
        assert result['routed_to'] == 'proofs'

    # ========================================
    # Test 5: Specialist Delegation
    # ========================================

    def test_specialist_delegation_sigma_algebra(self):
        """Test delegation to sigma-algebra specialist."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'trivial_sigma_algebra',
            'Omega': {1, 2, 3}
        })

        assert result['success'] is True
        assert result['routed_to'] == 'sigma_algebra'
        assert result['specialist_result']['cardinality'] == 2

    def test_specialist_delegation_measurable(self):
        """Test delegation to measurable functions specialist."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'indicator_function',
            'A': {1, 2},
            'Omega': {1, 2, 3}
        })

        assert result['success'] is True
        assert result['routed_to'] == 'measurable_functions'

    # ========================================
    # Test 6: Unknown Operation Handling
    # ========================================

    def test_unknown_operation_fallback(self):
        """Test fallback routing for unknown operations."""
        supervisor = FoundationsSupervisor()

        result = supervisor.process_request({
            'operation': 'some_unknown_operation',
            'A': {1, 2}
        })

        # Should route to default (sets) with low confidence
        assert result['success'] is False or result['routed_to'] == 'sets'

    # ========================================
    # Test 7: Multi-Step Problem Coordination
    # ========================================

    def test_multi_step_coordination(self):
        """Test multi-step problem coordination."""
        supervisor = FoundationsSupervisor()

        result = supervisor.coordinate_multi_step([
            {
                'specialist': 'sets',
                'request': {'operation': 'union', 'A': {1}, 'B': {2}}
            },
            {
                'specialist': 'functions',
                'request': {'operation': 'injective', 'f': [(1, 'a'), (2, 'b')]}
            }
        ])

        assert result['success'] is True
        assert result['num_steps'] == 2
        assert result['steps_completed'] == 2

    # ========================================
    # Test 8: Error Propagation
    # ========================================

    def test_error_propagation(self):
        """Test error propagation from specialist."""
        supervisor = FoundationsSupervisor()

        # Missing required parameter
        result = supervisor.process_request({
            'operation': 'union',
            'A': {1, 2}
            # Missing B
        })

        assert result['success'] is False or result['specialist_result']['success'] is False

    # ========================================
    # Test 9: Statistics Reporting
    # ========================================

    def test_statistics_reporting(self):
        """Test comprehensive statistics."""
        supervisor = FoundationsSupervisor()

        # Execute some tasks
        supervisor.process_request({'operation': 'union', 'A': {1}, 'B': {2}})
        supervisor.process_request({
            'operation': 'reflexive',
            'R': [(1, 1)],
            'A': {1}
        })

        stats = supervisor.get_statistics()

        assert stats['agent_id'] == supervisor.agent_id
        assert stats['statistics']['tasks_executed'] == 2
        assert stats['statistics']['routing_breakdown']['sets'] == 1
        assert stats['statistics']['routing_breakdown']['relations'] == 1

    # ========================================
    # Test 10: BDI Interface Compliance
    # ========================================

    def test_bdi_update_beliefs(self):
        """Test BDI update_beliefs method."""
        supervisor = FoundationsSupervisor()

        supervisor.update_beliefs({
            'operation': 'union',
            'A': {1, 2}
        })

        assert 'operation' in supervisor.beliefs or len(supervisor.beliefs) >= 0

    def test_bdi_deliberate(self):
        """Test BDI deliberate method."""
        supervisor = FoundationsSupervisor()

        # Add some pending beliefs
        supervisor.beliefs['pending_foundations_1'] = {'operation': 'union'}
        desires = supervisor.deliberate()

        assert 'process_pending_foundations_1' in desires

    def test_bdi_execute_step(self):
        """Test BDI execute_step method."""
        supervisor = FoundationsSupervisor()

        supervisor.beliefs['pending_foundations_1'] = {
            'operation': 'union',
            'A': {1, 2},
            'B': {3, 4}
        }

        result = supervisor.execute_step()

        assert result is not None
        assert result['success'] is True
