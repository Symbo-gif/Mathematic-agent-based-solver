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
Comprehensive tests for KnapsackSpecialist.

Tests cover: initialization, knapsack algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.knapsack_specialist import KnapsackSpecialist


class TestKnapsackSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = KnapsackSpecialist()
        assert specialist.name == "KnapsackSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = KnapsackSpecialist(name="CustomKnapsack")
        assert specialist.name == "CustomKnapsack"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = KnapsackSpecialist()
        assert 'knapsack_01' in specialist.supported_operations
        assert 'knapsack_unbounded' in specialist.supported_operations


class TestKnapsackSpecialist01:
    """Test knapsack_01 operation."""

    def test_knapsack_01_simple(self):
        """Test 0/1 knapsack on simple instance."""
        specialist = KnapsackSpecialist()
        items = [(60, 10), (100, 20), (120, 30)]  # (value, weight)
        capacity = 50
        value, selected = specialist.knapsack_01(items, capacity)
        assert value == 220  # Items 1 and 2

    def test_knapsack_01_empty(self):
        """Test 0/1 knapsack with no items."""
        specialist = KnapsackSpecialist()
        value, selected = specialist.knapsack_01([], 100)
        assert value == 0
        assert selected == []

    def test_knapsack_01_zero_capacity(self):
        """Test 0/1 knapsack with zero capacity."""
        specialist = KnapsackSpecialist()
        items = [(10, 5), (20, 10)]
        value, selected = specialist.knapsack_01(items, 0)
        assert value == 0


class TestKnapsackSpecialistUnbounded:
    """Test knapsack_unbounded operation."""

    def test_knapsack_unbounded(self):
        """Test unbounded knapsack."""
        specialist = KnapsackSpecialist()
        items = [(10, 5), (30, 10)]  # (value, weight)
        capacity = 20
        value, counts = specialist.knapsack_unbounded(items, capacity)
        assert value >= 60  # At least 2x item 2

    def test_knapsack_unbounded_empty(self):
        """Test unbounded knapsack with no items."""
        specialist = KnapsackSpecialist()
        value, counts = specialist.knapsack_unbounded([], 100)
        assert value == 0


class TestKnapsackSpecialistFractional:
    """Test knapsack_fractional operation."""

    def test_knapsack_fractional(self):
        """Test fractional knapsack."""
        specialist = KnapsackSpecialist()
        items = [(60, 10), (100, 20), (120, 30)]  # (value, weight)
        capacity = 50
        value, fractions = specialist.knapsack_fractional(items, capacity)
        assert value >= 220  # At least as good as 0/1

    def test_knapsack_fractional_exact_fit(self):
        """Test fractional knapsack with exact fit."""
        specialist = KnapsackSpecialist()
        items = [(10, 10), (20, 10)]
        capacity = 20
        value, fractions = specialist.knapsack_fractional(items, capacity)
        assert value == 30  # Both items fully used


class TestKnapsackSpecialistSubsetSum:
    """Test subset_sum operation."""

    def test_subset_sum_exists(self):
        """Test subset sum that exists."""
        specialist = KnapsackSpecialist()
        numbers = [3, 34, 4, 12, 5, 2]
        target = 9
        exists, subset = specialist.subset_sum(numbers, target)
        assert exists is True
        assert subset is not None
        assert sum(numbers[i] for i in subset) == target

    def test_subset_sum_not_exists(self):
        """Test subset sum that doesn't exist."""
        specialist = KnapsackSpecialist()
        numbers = [1, 2, 3]
        target = 7
        exists, subset = specialist.subset_sum(numbers, target)
        assert exists is False

    def test_subset_sum_zero(self):
        """Test subset sum with target zero."""
        specialist = KnapsackSpecialist()
        numbers = [1, 2, 3]
        target = 0
        exists, subset = specialist.subset_sum(numbers, target)
        assert exists is True
        assert subset == []


class TestKnapsackSpecialistMultiple:
    """Test multiple_knapsack operation."""

    def test_multiple_knapsack(self):
        """Test multiple knapsack."""
        specialist = KnapsackSpecialist()
        items = [(10, 5), (20, 10), (15, 7)]
        capacities = [12, 15]
        result = specialist.multiple_knapsack(items, capacities)
        assert 'total_value' in result
        assert 'assignments' in result


class TestKnapsackSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_item_fits(self):
        """Test single item that fits."""
        specialist = KnapsackSpecialist()
        items = [(10, 5)]
        value, selected = specialist.knapsack_01(items, 10)
        assert value == 10
        assert 0 in selected

    def test_all_items_too_heavy(self):
        """Test all items too heavy."""
        specialist = KnapsackSpecialist()
        items = [(100, 50), (200, 100)]
        value, selected = specialist.knapsack_01(items, 10)
        assert value == 0


class TestKnapsackSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_knapsack_01_request(self):
        """Test processing 0/1 knapsack request."""
        specialist = KnapsackSpecialist()
        request = {
            'operation': 'knapsack_01',
            'items': [(10, 5), (20, 10)],
            'capacity': 15
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = KnapsackSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestKnapsackSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = KnapsackSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = KnapsackSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = KnapsackSpecialist()
        assert hasattr(specialist, 'name')


class TestKnapsackSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = KnapsackSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'knapsack_01_solved' in stats


class TestKnapsackSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_solves(self):
        """Test concurrent knapsack solving."""
        specialist = KnapsackSpecialist()
        results = []

        def solve():
            items = [(60, 10), (100, 20), (120, 30)]
            value, _ = specialist.knapsack_01(items, 50)
            results.append(value)

        threads = [threading.Thread(target=solve) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 220 for r in results)
