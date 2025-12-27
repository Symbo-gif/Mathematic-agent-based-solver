# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for MaxFlowSpecialist.

Tests cover: initialization, all max flow operations, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.max_flow_specialist import MaxFlowSpecialist


class TestMaxFlowSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = MaxFlowSpecialist()
        assert specialist.name == "MaxFlowSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = MaxFlowSpecialist(name="CustomMaxFlow")
        assert specialist.name == "CustomMaxFlow"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = MaxFlowSpecialist()
        assert 'max_flow' in specialist.supported_operations
        assert 'edmonds_karp' in specialist.supported_operations


class TestMaxFlowSpecialistEdmondsKarp:
    """Test Edmonds-Karp max flow algorithm."""

    def test_edmonds_karp_simple(self):
        """Test Edmonds-Karp on simple network."""
        specialist = MaxFlowSpecialist()
        # graph[u][v] = capacity
        graph = {
            0: {1: 10.0},
            1: {2: 10.0},
            2: {}
        }
        result = specialist.edmonds_karp(graph, 0, 2)
        assert result == 10.0

    def test_edmonds_karp_multiple_paths(self):
        """Test Edmonds-Karp with multiple paths."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 10.0, 2: 10.0},
            1: {3: 10.0},
            2: {3: 10.0},
            3: {}
        }
        result = specialist.edmonds_karp(graph, 0, 3)
        assert result == 20.0

    def test_edmonds_karp_bottleneck(self):
        """Test Edmonds-Karp with bottleneck."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 100.0},
            1: {2: 5.0},  # bottleneck
            2: {3: 100.0},
            3: {}
        }
        result = specialist.edmonds_karp(graph, 0, 3)
        assert result == 5.0

    def test_edmonds_karp_disconnected(self):
        """Test Edmonds-Karp on disconnected graph."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 10.0},
            1: {},
            2: {3: 10.0},
            3: {}
        }
        result = specialist.edmonds_karp(graph, 0, 3)
        assert result == 0.0


class TestMaxFlowSpecialistMaxFlow:
    """Test max_flow method (Ford-Fulkerson variant)."""

    def test_max_flow_simple(self):
        """Test max_flow on simple network."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 10.0},
            1: {2: 10.0},
            2: {}
        }
        result = specialist.max_flow(graph, 0, 2)
        assert result == 10.0

    def test_max_flow_with_flow(self):
        """Test max_flow returns correct value."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 5.0, 2: 5.0},
            1: {3: 5.0},
            2: {3: 5.0},
            3: {}
        }
        result = specialist.max_flow(graph, 0, 3)
        assert result == 10.0


class TestMaxFlowSpecialistMinCut:
    """Test min cut computation."""

    def test_min_cut_simple(self):
        """Test min cut on simple network."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 10.0},
            1: {2: 10.0},
            2: {}
        }
        # min_cut_from_flow requires the flow and graph
        result = specialist.min_cut_from_flow(graph, 0, 2)
        # Should return set of reachable vertices from source in residual
        assert isinstance(result, (set, list))


class TestMaxFlowSpecialistEdgeCases:
    """Test edge cases."""

    def test_empty_graph(self):
        """Test empty graph."""
        specialist = MaxFlowSpecialist()
        graph = {}
        result = specialist.edmonds_karp(graph, 0, 1)
        assert result == 0.0

    def test_source_equals_sink(self):
        """Test source equals sink."""
        specialist = MaxFlowSpecialist()
        graph = {0: {1: 10.0}, 1: {}}
        result = specialist.edmonds_karp(graph, 0, 0)
        assert result == float('inf')

    def test_zero_capacity(self):
        """Test zero capacity edge."""
        specialist = MaxFlowSpecialist()
        graph = {0: {1: 0.0}, 1: {}}
        result = specialist.edmonds_karp(graph, 0, 1)
        assert result == 0.0

    def test_single_edge(self):
        """Test single edge network."""
        specialist = MaxFlowSpecialist()
        graph = {0: {1: 42.0}, 1: {}}
        result = specialist.edmonds_karp(graph, 0, 1)
        assert result == 42.0

    def test_large_capacity(self):
        """Test large capacity values."""
        specialist = MaxFlowSpecialist()
        graph = {0: {1: 1e12}, 1: {}}
        result = specialist.edmonds_karp(graph, 0, 1)
        assert result == 1e12


class TestMaxFlowSpecialistComplexNetworks:
    """Test complex network structures."""

    def test_diamond_network(self):
        """Test diamond-shaped network."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 10.0, 2: 10.0},
            1: {3: 10.0},
            2: {3: 10.0},
            3: {}
        }
        result = specialist.edmonds_karp(graph, 0, 3)
        assert result == 20.0

    def test_linear_chain(self):
        """Test linear chain network."""
        specialist = MaxFlowSpecialist()
        graph = {
            0: {1: 10.0},
            1: {2: 10.0},
            2: {3: 10.0},
            3: {}
        }
        result = specialist.edmonds_karp(graph, 0, 3)
        assert result == 10.0


class TestMaxFlowSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_edmonds_karp_request(self):
        """Test processing edmonds_karp request."""
        specialist = MaxFlowSpecialist()
        request = {
            'operation': 'edmonds_karp',
            'graph': {0: {1: 10.0}, 1: {}},
            'source': 0,
            'sink': 1
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = MaxFlowSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestMaxFlowSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = MaxFlowSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = MaxFlowSpecialist()
        action = specialist.deliberate()
        assert action is None

    def test_execute_step_no_blackboard(self):
        """Test execute_step with no blackboard."""
        specialist = MaxFlowSpecialist()
        result = specialist.execute_step()
        assert result is False


class TestMaxFlowSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = MaxFlowSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'flows_computed' in stats

    def test_statistics_increment(self):
        """Test that statistics increment correctly."""
        specialist = MaxFlowSpecialist()
        graph = {0: {1: 10.0}, 1: {}}
        specialist.edmonds_karp(graph, 0, 1)
        stats = specialist.get_statistics()
        assert stats.get('flows_computed', 0) >= 1


class TestMaxFlowSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_flow_computations(self):
        """Test concurrent flow computations."""
        specialist = MaxFlowSpecialist()
        results = []

        def compute_flow():
            graph = {0: {1: 10.0}, 1: {}}
            result = specialist.edmonds_karp(graph, 0, 1)
            results.append(result)

        threads = [threading.Thread(target=compute_flow) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 10.0 for r in results)
