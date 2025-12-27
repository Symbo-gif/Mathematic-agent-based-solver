# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for BranchBoundSpecialist.

Tests cover: initialization, B&B algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.branch_bound_specialist import BranchBoundSpecialist


class TestBranchBoundSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = BranchBoundSpecialist()
        assert specialist.name == "BranchBoundSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = BranchBoundSpecialist(name="CustomBB")
        assert specialist.name == "CustomBB"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = BranchBoundSpecialist()
        assert 'solve_knapsack' in specialist.supported_operations
        assert 'solve_tsp' in specialist.supported_operations


class TestBranchBoundSpecialistKnapsack:
    """Test solve_knapsack operation."""

    def test_knapsack_simple(self):
        """Test B&B knapsack on simple instance."""
        specialist = BranchBoundSpecialist()
        items = [(60, 10), (100, 20), (120, 30)]  # (value, weight)
        capacity = 50
        value, selected = specialist.solve_knapsack(items, capacity)
        assert value >= 220  # Can fit items 1 and 2

    def test_knapsack_empty(self):
        """Test B&B knapsack with no items."""
        specialist = BranchBoundSpecialist()
        value, selected = specialist.solve_knapsack([], 100)
        assert value == 0
        assert selected == []

    def test_knapsack_zero_capacity(self):
        """Test B&B knapsack with zero capacity."""
        specialist = BranchBoundSpecialist()
        items = [(10, 5), (20, 10)]
        value, selected = specialist.solve_knapsack(items, 0)
        assert value == 0


class TestBranchBoundSpecialistTSP:
    """Test solve_tsp operation."""

    def test_tsp_simple(self):
        """Test B&B TSP on simple instance."""
        specialist = BranchBoundSpecialist()
        distances = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]
        cost, tour = specialist.solve_tsp(distances)
        assert len(tour) == 4
        assert cost <= 80  # Reasonable bound

    def test_tsp_empty(self):
        """Test B&B TSP with empty input."""
        specialist = BranchBoundSpecialist()
        cost, tour = specialist.solve_tsp([])
        assert cost == 0

    def test_tsp_single_city(self):
        """Test B&B TSP with single city."""
        specialist = BranchBoundSpecialist()
        distances = [[0]]
        cost, tour = specialist.solve_tsp(distances)
        assert tour == [0]


class TestBranchBoundSpecialistStrategies:
    """Test branching_strategies operation."""

    def test_branching_strategies(self):
        """Test available branching strategies."""
        specialist = BranchBoundSpecialist()
        strategies = specialist.branching_strategies()
        assert isinstance(strategies, list)
        assert 'most_fractional' in strategies


class TestBranchBoundSpecialistBoundPrune:
    """Test compute_bound and prune operations."""

    def test_compute_bound(self):
        """Test bound computation."""
        specialist = BranchBoundSpecialist()
        node = {'solution': [0.5, 0.5], 'objective': [10, 20]}
        bound = specialist.compute_bound(node)
        assert bound == 15  # 0.5*10 + 0.5*20

    def test_prune_maximization(self):
        """Test pruning in maximization."""
        specialist = BranchBoundSpecialist()
        result = specialist.prune(10, 15, 'maximization')
        assert result is True  # 10 <= 15, prune

    def test_prune_minimization(self):
        """Test pruning in minimization."""
        specialist = BranchBoundSpecialist()
        result = specialist.prune(15, 10, 'minimization')
        assert result is True  # 15 >= 10, prune


class TestBranchBoundSpecialistEdgeCases:
    """Test edge cases."""

    def test_knapsack_large_item(self):
        """Test item too large for knapsack."""
        specialist = BranchBoundSpecialist()
        items = [(100, 50)]  # Weight > capacity
        value, selected = specialist.solve_knapsack(items, 10)
        assert value == 0

    def test_tsp_two_cities(self):
        """Test TSP with two cities."""
        specialist = BranchBoundSpecialist()
        distances = [[0, 5], [5, 0]]
        cost, tour = specialist.solve_tsp(distances)
        assert cost == 10  # Round trip


class TestBranchBoundSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_knapsack_request(self):
        """Test processing knapsack request."""
        specialist = BranchBoundSpecialist()
        request = {
            'operation': 'solve_knapsack',
            'items': [(60, 10), (100, 20)],
            'capacity': 30
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = BranchBoundSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestBranchBoundSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = BranchBoundSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = BranchBoundSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = BranchBoundSpecialist()
        assert hasattr(specialist, 'name')


class TestBranchBoundSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = BranchBoundSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'problems_solved' in stats


class TestBranchBoundSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_solves(self):
        """Test concurrent B&B solving."""
        specialist = BranchBoundSpecialist()
        results = []

        def solve():
            items = [(10, 5), (20, 10)]
            value, _ = specialist.solve_knapsack(items, 15)
            results.append(value)

        threads = [threading.Thread(target=solve) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 30 for r in results)
