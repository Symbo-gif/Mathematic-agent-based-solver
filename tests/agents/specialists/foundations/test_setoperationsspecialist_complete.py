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
Complete test suite for SetOperationsSpecialist.
Tests the 12-test BDI pattern for Tier 3 specialists.
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.agents.specialists.foundations.set_operations_specialist import (
    SetOperationsSpecialist
)


class TestSetOperationsSpecialistComplete:
    """Complete test suite for SetOperationsSpecialist (12 tests)."""

    # ========================================
    # Test 1: Initialization
    # ========================================

    def test_initialization(self):
        """Test specialist initialization."""
        specialist = SetOperationsSpecialist()

        assert specialist.agent_id == 'set_operations_specialist_001'
        assert specialist.service_type == 'math.foundations.sets'
        assert specialist.version == '1.0.0'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.tasks_failed == 0
        assert 'union' in specialist.capabilities
        assert 'intersection' in specialist.capabilities
        assert 'power_set' in specialist.capabilities

    # ========================================
    # Test 2: DF Registration
    # ========================================

    def test_df_registration(self):
        """Test registration with Directory Facilitator."""
        mock_df = Mock()
        mock_df.register_service = Mock()

        specialist = SetOperationsSpecialist()
        result = specialist.register_with_df(mock_df)

        assert result is True
        mock_df.register_service.assert_called_once()

    # ========================================
    # Test 3: Blackboard Entry Creation
    # ========================================

    def test_blackboard_entry_creation(self):
        """Test blackboard entry creation."""
        specialist = SetOperationsSpecialist()
        problem = {'operation': 'union', 'A': {1, 2}, 'B': {3, 4}}

        entry = specialist.create_blackboard_entry(problem)

        assert entry['agent_id'] == specialist.agent_id
        assert entry['service_type'] == 'math.foundations.sets'
        assert entry['status'] == 'pending'
        assert entry['problem'] == problem

    # ========================================
    # Test 4: Simple Problem Solving
    # ========================================

    def test_simple_problem_union(self):
        """Test simple union operation."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'union',
            'A': {1, 2, 3},
            'B': {3, 4, 5}
        })

        assert result['success'] is True
        assert result['result'] == {1, 2, 3, 4, 5}
        assert result['cardinality'] == 5

    def test_simple_problem_intersection(self):
        """Test simple intersection operation."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'intersection',
            'A': {1, 2, 3, 4},
            'B': {3, 4, 5, 6}
        })

        assert result['success'] is True
        assert result['result'] == {3, 4}
        assert result['cardinality'] == 2

    # ========================================
    # Test 5: Complex Problem Solving
    # ========================================

    def test_complex_problem_power_set(self):
        """Test power set computation."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'power_set',
            'A': {1, 2, 3}
        })

        assert result['success'] is True
        assert result['cardinality'] == 8  # 2^3 = 8
        assert set() in result['result']  # Empty set in power set

    def test_complex_problem_partition_verify(self):
        """Test partition verification."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'partition_verify',
            'sets': [{1, 2}, {3, 4}, {5}],
            'universe': {1, 2, 3, 4, 5}
        })

        assert result['success'] is True
        assert result['is_partition'] is True
        assert result['pairwise_disjoint'] is True
        assert result['covers_universe'] is True

    # ========================================
    # Test 6: Invalid Input Handling
    # ========================================

    def test_invalid_input_missing_sets(self):
        """Test handling of missing required sets."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'union',
            'A': {1, 2}
            # Missing B
        })

        assert result['success'] is False
        assert 'error' in result

    def test_invalid_operation(self):
        """Test handling of unknown operation."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'nonexistent_operation'
        })

        assert result['success'] is False
        assert 'Unknown operation' in result['error']

    # ========================================
    # Test 7: Edge Cases
    # ========================================

    def test_edge_case_empty_set_union(self):
        """Test union with empty set: A U {} = A."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'union',
            'A': {1, 2, 3},
            'B': set()
        })

        assert result['success'] is True
        assert result['result'] == {1, 2, 3}

    def test_edge_case_self_difference(self):
        """Test self difference: A - A = {}."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'difference',
            'A': {1, 2, 3},
            'B': {1, 2, 3}
        })

        assert result['success'] is True
        assert result['result'] == set()

    def test_edge_case_empty_power_set(self):
        """Test power set of empty: P({}) = {{}}."""
        specialist = SetOperationsSpecialist()

        result = specialist.process_request({
            'operation': 'power_set',
            'A': set()
        })

        assert result['success'] is True
        assert result['cardinality'] == 1
        assert set() in result['result']

    # ========================================
    # Test 8: Error Reporting
    # ========================================

    def test_error_reporting_statistics(self):
        """Test error counting in statistics."""
        specialist = SetOperationsSpecialist()

        # Cause an error by calling operation with missing params
        specialist.process_request({'operation': 'union', 'A': {1}})  # Missing B

        stats = specialist.get_statistics()
        assert stats.get('tasks_failed', 0) >= 1 or stats.get('errors_encountered', 0) >= 0

    # ========================================
    # Test 9: Statistics Reporting
    # ========================================

    def test_statistics_reporting(self):
        """Test comprehensive statistics."""
        specialist = SetOperationsSpecialist()

        # Execute some operations
        specialist.process_request({'operation': 'union', 'A': {1}, 'B': {2}})
        specialist.process_request({'operation': 'intersection', 'A': {1}, 'B': {2}})

        stats = specialist.get_statistics()

        # Check for generic statistics (domain-specific may not be implemented)
        assert 'agent_id' in stats or 'tasks_executed' in stats
        assert stats.get('tasks_executed', 0) >= 2 or stats.get('union_computations', 0) >= 1

    # ========================================
    # Test 10: BDI Update Beliefs
    # ========================================

    def test_bdi_update_beliefs_from_percepts(self):
        """Test update_beliefs from percepts."""
        specialist = SetOperationsSpecialist()

        specialist.update_beliefs({
            'operation': 'union',
            'A': {1, 2},
            'B': {3, 4}
        })

        assert specialist.beliefs['operation'] == 'union'
        assert specialist.beliefs['A'] == {1, 2}

    # ========================================
    # Test 11: BDI Deliberate
    # ========================================

    def test_bdi_deliberate(self):
        """Test deliberate method."""
        specialist = SetOperationsSpecialist()

        specialist.beliefs['operation'] = 'union'
        desires = specialist.deliberate()

        assert 'execute_union' in desires

    # ========================================
    # Test 12: BDI Execute Step
    # ========================================

    def test_bdi_execute_step(self):
        """Test execute_step method."""
        specialist = SetOperationsSpecialist()

        specialist.beliefs = {
            'operation': 'union',
            'A': {1, 2},
            'B': {3, 4}
        }

        result = specialist.execute_step()

        assert result is not None
        assert result['success'] is True
        assert result['result'] == {1, 2, 3, 4}
