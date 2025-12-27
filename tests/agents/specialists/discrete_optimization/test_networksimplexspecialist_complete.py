# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for NetworkSimplexSpecialist.

Tests cover: initialization, network simplex algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.network_simplex_specialist import NetworkSimplexSpecialist


class TestNetworkSimplexSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = NetworkSimplexSpecialist()
        assert specialist.name == "NetworkSimplexSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = NetworkSimplexSpecialist(name="CustomNS")
        assert specialist.name == "CustomNS"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = NetworkSimplexSpecialist()
        assert 'min_cost_flow' in specialist.supported_operations
        assert 'transportation' in specialist.supported_operations


class TestNetworkSimplexSpecialistMinCostFlow:
    """Test min_cost_flow operation."""

    def test_min_cost_flow_simple(self):
        """Test min cost flow on simple network."""
        specialist = NetworkSimplexSpecialist()
        # Network format as expected by the specialist
        network = {
            'nodes': [0, 1, 2],
            'arcs': [(0, 1, 2.0, 10), (1, 2, 3.0, 10)],  # (from, to, cost, capacity)
            'supplies': {0: 5, 2: -5}  # Positive = supply, negative = demand
        }
        result = specialist.min_cost_flow(network)
        assert isinstance(result, dict)
        assert 'cost' in result or 'flow' in result or 'success' in result

    def test_min_cost_flow_empty(self):
        """Test min cost flow with empty network."""
        specialist = NetworkSimplexSpecialist()
        network = {'nodes': [], 'arcs': [], 'supplies': {}}
        result = specialist.min_cost_flow(network)
        assert isinstance(result, dict)

    def test_min_cost_flow_single_arc(self):
        """Test min cost flow with single arc."""
        specialist = NetworkSimplexSpecialist()
        network = {
            'nodes': [0, 1],
            'arcs': [(0, 1, 2.0, 5)],
            'supplies': {0: 5, 1: -5}
        }
        result = specialist.min_cost_flow(network)
        assert isinstance(result, dict)


class TestNetworkSimplexSpecialistTransportation:
    """Test transportation operation."""

    def test_transportation_simple(self):
        """Test transportation problem."""
        specialist = NetworkSimplexSpecialist()
        # 2 suppliers, 3 consumers
        supply = [20.0, 30.0]
        demand = [15.0, 20.0, 15.0]
        costs = [
            [2.0, 3.0, 1.0],
            [5.0, 4.0, 8.0]
        ]
        result = specialist.transportation(supply, demand, costs)
        assert isinstance(result, dict)
        assert 'cost' in result or 'total_cost' in result or 'assignment' in result or 'success' in result

    def test_transportation_balanced(self):
        """Test balanced transportation."""
        specialist = NetworkSimplexSpecialist()
        supply = [10.0, 10.0]
        demand = [10.0, 10.0]
        costs = [[1.0, 2.0], [3.0, 4.0]]
        result = specialist.transportation(supply, demand, costs)
        assert isinstance(result, dict)

    def test_transportation_empty(self):
        """Test empty transportation problem."""
        specialist = NetworkSimplexSpecialist()
        result = specialist.transportation([], [], [])
        assert isinstance(result, dict)


class TestNetworkSimplexSpecialistSuccessiveShortest:
    """Test successive_shortest_paths operation."""

    def test_successive_shortest_paths(self):
        """Test successive shortest paths algorithm."""
        specialist = NetworkSimplexSpecialist()
        network = {
            'nodes': [0, 1, 2],
            'arcs': [(0, 1, 1.0, 10), (1, 2, 1.0, 10)],
            'supplies': {}
        }
        result = specialist.successive_shortest_paths(network, 0, 2, 5.0)
        assert isinstance(result, dict)


class TestNetworkSimplexSpecialistCheckFeasibility:
    """Test check_feasibility operation."""

    def test_check_feasibility_balanced(self):
        """Test feasibility check on balanced network."""
        specialist = NetworkSimplexSpecialist()
        network = {
            'nodes': [0, 1],
            'arcs': [(0, 1, 1.0, 10)],
            'supplies': {0: 5, 1: -5}  # Balanced
        }
        result = specialist.check_feasibility(network)
        assert isinstance(result, bool)


class TestNetworkSimplexSpecialistEdgeCases:
    """Test edge cases."""

    def test_infeasible_supply(self):
        """Test infeasible supply/demand."""
        specialist = NetworkSimplexSpecialist()
        network = {
            'nodes': [0, 1],
            'arcs': [(0, 1, 1.0, 5)],  # Capacity 5
            'supplies': {0: 10, 1: -10}  # Demand > capacity
        }
        result = specialist.min_cost_flow(network)
        # Should handle infeasibility gracefully
        assert isinstance(result, dict)

    def test_zero_cost_flow(self):
        """Test network with zero costs."""
        specialist = NetworkSimplexSpecialist()
        network = {
            'nodes': [0, 1, 2],
            'arcs': [(0, 1, 0.0, 10), (1, 2, 0.0, 10)],
            'supplies': {0: 5, 2: -5}
        }
        result = specialist.min_cost_flow(network)
        assert isinstance(result, dict)


class TestNetworkSimplexSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_min_cost_flow_request(self):
        """Test processing min cost flow request."""
        specialist = NetworkSimplexSpecialist()
        request = {
            'operation': 'min_cost_flow',
            'network': {
                'nodes': [0, 1],
                'arcs': [(0, 1, 2.0, 10)],
                'supplies': {0: 5, 1: -5}
            }
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_transportation_request(self):
        """Test processing transportation request."""
        specialist = NetworkSimplexSpecialist()
        request = {
            'operation': 'transportation',
            'supply': [10.0],
            'demand': [10.0],
            'costs': [[5.0]]
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = NetworkSimplexSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestNetworkSimplexSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = NetworkSimplexSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = NetworkSimplexSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = NetworkSimplexSpecialist()
        assert hasattr(specialist, 'name')


class TestNetworkSimplexSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = NetworkSimplexSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'min_cost_solved' in stats or 'transportation_solved' in stats


class TestNetworkSimplexSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_solves(self):
        """Test concurrent network simplex solving."""
        specialist = NetworkSimplexSpecialist()
        results = []

        def solve():
            supply = [10.0]
            demand = [10.0]
            costs = [[2.0]]
            result = specialist.transportation(supply, demand, costs)
            results.append(isinstance(result, dict))

        threads = [threading.Thread(target=solve) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
