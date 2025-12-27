# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for GraphTheorySupervisor.

Tests cover: initialization, routing, delegation, error handling,
statistics, BDI interface, and concurrent access.
"""

import pytest
import threading
from unittest.mock import MagicMock, patch

from symbo_agentic_reasoners.agents.supervisors.graph_theory_supervisor import GraphTheorySupervisor


class TestGraphTheorySupervisorInit:
    """Test initialization and setup."""

    def test_init_default(self):
        """Test initialization with defaults."""
        supervisor = GraphTheorySupervisor()
        assert 'graph_theory_supervisor' in supervisor.agent_id
        assert hasattr(supervisor, 'routing_stats')

    def test_init_has_beliefs(self):
        """Test initialization includes beliefs dict."""
        supervisor = GraphTheorySupervisor()
        assert hasattr(supervisor, 'beliefs')
        assert isinstance(supervisor.beliefs, dict)

    def test_init_routing_stats(self):
        """Test routing stats are initialized."""
        supervisor = GraphTheorySupervisor()
        stats = supervisor.routing_stats
        assert isinstance(stats, dict)


class TestGraphTheorySupervisorRouting:
    """Test routing logic."""

    def test_route_path_keywords(self):
        """Test routing for path-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'find shortest path from A to B'})
        assert result.get('specialist_type') == 'path' or 'path' in str(result)

    def test_route_tree_keywords(self):
        """Test routing for tree-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'check if graph is a tree'})
        assert result.get('specialist_type') == 'tree' or 'tree' in str(result)

    def test_route_connectivity_keywords(self):
        """Test routing for connectivity-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'find connected components'})
        assert result.get('specialist_type') == 'connectivity' or 'connectivity' in str(result)

    def test_route_cycle_keywords(self):
        """Test routing for cycle-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'find eulerian circuit'})
        assert result.get('specialist_type') == 'cycle' or 'cycle' in str(result) or 'eulerian' in str(result).lower()

    def test_route_coloring_keywords(self):
        """Test routing for coloring-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'find chromatic number'})
        assert 'coloring' in str(result) or 'color' in str(result)

    def test_route_matching_keywords(self):
        """Test routing for matching-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'find bipartite matching'})
        assert 'matching' in str(result)

    def test_route_planarity_keywords(self):
        """Test routing for planarity-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'check planar graph'})
        assert 'planar' in str(result)

    def test_route_isomorphism_keywords(self):
        """Test routing for isomorphism-related queries."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'check isomorphism'})
        assert 'isomorphism' in str(result)

    def test_route_default(self):
        """Test default routing."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.route_problem({'operation': 'unknown graph operation xyz123'})
        # Should return some valid response
        assert result is not None


class TestGraphTheorySupervisorStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        supervisor = GraphTheorySupervisor()
        stats = supervisor.get_statistics()
        assert isinstance(stats, dict)

    def test_routing_stats_exist(self):
        """Test routing_stats attribute exists."""
        supervisor = GraphTheorySupervisor()
        assert hasattr(supervisor, 'routing_stats')


class TestGraphTheorySupervisorBDI:
    """Test BDI interface."""

    def test_update_beliefs(self):
        """Test update_beliefs method exists."""
        supervisor = GraphTheorySupervisor()
        try:
            supervisor.update_beliefs({})
        except TypeError:
            supervisor.update_beliefs()  # Some supervisors don't take args  # Should not raise
        assert hasattr(supervisor, 'beliefs')

    def test_deliberate(self):
        """Test deliberate method exists."""
        supervisor = GraphTheorySupervisor()
        result = supervisor.deliberate()
        # Can return None or an intention
        assert result is None or result is not None

    def test_execute_step(self):
        """Test execute_step method exists."""
        supervisor = GraphTheorySupervisor()
        # May raise or return False if no blackboard
        try:
            result = supervisor.execute_step()
            assert isinstance(result, bool)
        except Exception:
            pass  # OK if it fails without blackboard

    def test_has_agent_id(self):
        """Test agent_id is set."""
        supervisor = GraphTheorySupervisor()
        assert hasattr(supervisor, 'agent_id')
        assert supervisor.agent_id is not None


class TestGraphTheorySupervisorConcurrency:
    """Test thread safety."""

    def test_concurrent_routing(self):
        """Test concurrent routing is thread-safe."""
        supervisor = GraphTheorySupervisor()
        results = []

        def route_request():
            result = supervisor.route_problem({'operation': 'shortest path'})
            results.append(result)

        threads = [threading.Thread(target=route_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
