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
Comprehensive tests for AssignmentSpecialist.

Tests cover: initialization, assignment algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.assignment_specialist import AssignmentSpecialist


class TestAssignmentSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = AssignmentSpecialist()
        assert specialist.name == "AssignmentSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = AssignmentSpecialist(name="CustomAssign")
        assert specialist.name == "CustomAssign"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = AssignmentSpecialist()
        assert 'hungarian' in specialist.supported_operations
        assert 'greedy_assignment' in specialist.supported_operations


class TestAssignmentSpecialistHungarian:
    """Test hungarian operation."""

    def test_hungarian_simple(self):
        """Test Hungarian algorithm on simple matrix."""
        specialist = AssignmentSpecialist()
        cost_matrix = [
            [1, 2],
            [2, 1]
        ]
        assignment, cost = specialist.hungarian(cost_matrix)
        assert len(assignment) == 2
        assert cost == 2  # Optimal: 0->0, 1->1 or 0->1, 1->0

    def test_hungarian_3x3(self):
        """Test Hungarian algorithm on 3x3 matrix."""
        specialist = AssignmentSpecialist()
        cost_matrix = [
            [4, 2, 5],
            [2, 3, 1],
            [5, 4, 2]
        ]
        assignment, cost = specialist.hungarian(cost_matrix)
        assert len(assignment) == 3
        assert cost <= 6  # Reasonable bound

    def test_hungarian_empty(self):
        """Test Hungarian on empty matrix."""
        specialist = AssignmentSpecialist()
        assignment, cost = specialist.hungarian([])
        assert assignment == []
        assert cost == 0.0


class TestAssignmentSpecialistGreedy:
    """Test greedy_assignment operation."""

    def test_greedy_assignment(self):
        """Test greedy assignment."""
        specialist = AssignmentSpecialist()
        cost_matrix = [
            [1, 3],
            [2, 1]
        ]
        assignment, cost = specialist.greedy_assignment(cost_matrix)
        assert len(assignment) == 2
        assert -1 not in assignment  # All assigned

    def test_greedy_rectangular(self):
        """Test greedy on rectangular matrix."""
        specialist = AssignmentSpecialist()
        cost_matrix = [
            [1, 2, 3],
            [4, 1, 2]
        ]
        assignment, cost = specialist.greedy_assignment(cost_matrix)
        assert len(assignment) == 2


class TestAssignmentSpecialistBottleneck:
    """Test bottleneck_assignment operation."""

    def test_bottleneck_assignment(self):
        """Test bottleneck assignment."""
        specialist = AssignmentSpecialist()
        cost_matrix = [
            [1, 5],
            [5, 2]
        ]
        assignment, max_cost = specialist.bottleneck_assignment(cost_matrix)
        assert len(assignment) == 2
        assert max_cost <= 5


class TestAssignmentSpecialistCostValidation:
    """Test assignment_cost and is_valid_assignment."""

    def test_assignment_cost(self):
        """Test computing assignment cost."""
        specialist = AssignmentSpecialist()
        cost_matrix = [[1, 2], [3, 4]]
        assignment = [0, 1]
        cost = specialist.assignment_cost(cost_matrix, assignment)
        assert cost == 5  # 1 + 4

    def test_is_valid_assignment_true(self):
        """Test valid assignment check."""
        specialist = AssignmentSpecialist()
        assignment = [1, 0, 2]
        result = specialist.is_valid_assignment(assignment, 3, 3)
        assert result is True

    def test_is_valid_assignment_false(self):
        """Test invalid assignment (duplicate)."""
        specialist = AssignmentSpecialist()
        assignment = [0, 0, 1]  # 0 assigned twice
        result = specialist.is_valid_assignment(assignment, 3, 3)
        assert result is False


class TestAssignmentSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_element(self):
        """Test 1x1 matrix."""
        specialist = AssignmentSpecialist()
        cost_matrix = [[5]]
        assignment, cost = specialist.hungarian(cost_matrix)
        assert assignment == [0]
        assert cost == 5

    def test_all_zeros(self):
        """Test all-zero matrix."""
        specialist = AssignmentSpecialist()
        cost_matrix = [[0, 0], [0, 0]]
        assignment, cost = specialist.hungarian(cost_matrix)
        assert cost == 0


class TestAssignmentSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_hungarian_request(self):
        """Test processing Hungarian request."""
        specialist = AssignmentSpecialist()
        request = {
            'operation': 'hungarian',
            'cost_matrix': [[1, 2], [2, 1]]
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = AssignmentSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestAssignmentSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = AssignmentSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = AssignmentSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = AssignmentSpecialist()
        assert hasattr(specialist, 'name')


class TestAssignmentSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = AssignmentSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'hungarian_solved' in stats


class TestAssignmentSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_assignments(self):
        """Test concurrent assignment solving."""
        specialist = AssignmentSpecialist()
        results = []

        def solve_assignment():
            cost_matrix = [[1, 2], [2, 1]]
            _, cost = specialist.hungarian(cost_matrix)
            results.append(cost)

        threads = [threading.Thread(target=solve_assignment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
