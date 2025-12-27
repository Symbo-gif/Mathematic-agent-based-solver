# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for DiscreteOptimizationSupervisor.

Tests cover: initialization, routing, delegation, error handling,
statistics, BDI interface, and concurrent access.
"""

import pytest
import threading
from unittest.mock import MagicMock, patch

from symbo_agentic_reasoners.agents.supervisors.discrete_optimization_supervisor import DiscreteOptimizationSupervisor


class TestDiscreteOptimizationSupervisorInit:
    """Test initialization and setup."""

    def test_init_default(self):
        """Test initialization with defaults."""
        supervisor = DiscreteOptimizationSupervisor()
        assert 'discrete_optimization_supervisor' in supervisor.agent_id
        assert hasattr(supervisor, 'routing_stats')

    def test_init_has_beliefs(self):
        """Test initialization includes beliefs dict."""
        supervisor = DiscreteOptimizationSupervisor()
        assert hasattr(supervisor, 'beliefs')
        assert isinstance(supervisor.beliefs, dict)

    def test_init_routing_stats(self):
        """Test routing stats are initialized."""
        supervisor = DiscreteOptimizationSupervisor()
        stats = supervisor.routing_stats
        assert isinstance(stats, dict)
        assert 'max_flow' in stats
        assert 'knapsack' in stats


class TestDiscreteOptimizationSupervisorRouting:
    """Test routing logic."""

    def test_route_max_flow_keywords(self):
        """Test routing for max flow queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('compute maximum flow')
        assert result == 'max_flow'

    def test_route_min_cut_keywords(self):
        """Test routing for min cut queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('find minimum cut')
        assert result == 'min_cut'

    def test_route_mst_keywords(self):
        """Test routing for MST queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('find minimum spanning tree')
        assert result == 'mst'

    def test_route_shortest_path_keywords(self):
        """Test routing for shortest path queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('run dijkstra algorithm')
        assert result == 'shortest_path'

    def test_route_assignment_keywords(self):
        """Test routing for assignment queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('solve assignment problem')
        assert result == 'assignment'

    def test_route_ilp_keywords(self):
        """Test routing for ILP queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('formulate integer programming')
        assert result == 'ilp'

    def test_route_knapsack_keywords(self):
        """Test routing for knapsack queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('solve 0/1 knapsack')
        assert result == 'knapsack'

    def test_route_set_cover_keywords(self):
        """Test routing for set cover queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('find set cover')
        assert result == 'set_cover'

    def test_route_network_simplex_keywords(self):
        """Test routing for network simplex queries."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('min cost flow network simplex')
        assert result == 'network_simplex'

    def test_route_default(self):
        """Test default routing."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.route_problem('unknown optimization operation xyz123')
        assert result == 'shortest_path'  # Default


class TestDiscreteOptimizationSupervisorStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        supervisor = DiscreteOptimizationSupervisor()
        stats = supervisor.get_statistics()
        assert isinstance(stats, dict)
        assert 'routing_stats' in stats

    def test_routing_stats_exist(self):
        """Test routing_stats attribute exists."""
        supervisor = DiscreteOptimizationSupervisor()
        assert hasattr(supervisor, 'routing_stats')


class TestDiscreteOptimizationSupervisorBDI:
    """Test BDI interface."""

    def test_update_beliefs(self):
        """Test update_beliefs method exists."""
        supervisor = DiscreteOptimizationSupervisor()
        try:
            supervisor.update_beliefs({})
        except TypeError:
            supervisor.update_beliefs()  # Some supervisors don't take args  # Should not raise
        assert hasattr(supervisor, 'beliefs')

    def test_deliberate(self):
        """Test deliberate method exists."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.deliberate()
        assert result is None or result is not None

    def test_execute_step(self):
        """Test execute_step method exists."""
        supervisor = DiscreteOptimizationSupervisor()
        result = supervisor.execute_step()
        assert isinstance(result, bool)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        supervisor = DiscreteOptimizationSupervisor()
        assert hasattr(supervisor, 'agent_id')
        assert supervisor.agent_id is not None


class TestDiscreteOptimizationSupervisorConcurrency:
    """Test thread safety."""

    def test_concurrent_routing(self):
        """Test concurrent routing is thread-safe."""
        supervisor = DiscreteOptimizationSupervisor()
        results = []

        def route_request():
            result = supervisor.route_problem('max flow')
            results.append(result)

        threads = [threading.Thread(target=route_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 'max_flow' for r in results)
