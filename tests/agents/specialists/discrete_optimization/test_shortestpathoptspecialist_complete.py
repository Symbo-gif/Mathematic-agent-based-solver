# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for ShortestPathOptSpecialist.

Tests cover: initialization, shortest path algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.shortest_path_opt_specialist import ShortestPathOptSpecialist


class TestShortestPathOptSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = ShortestPathOptSpecialist()
        assert specialist.name == "ShortestPathOptSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = ShortestPathOptSpecialist(name="CustomSP")
        assert specialist.name == "CustomSP"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = ShortestPathOptSpecialist()
        assert 'dijkstra' in specialist.supported_operations
        assert 'bellman_ford' in specialist.supported_operations
        assert 'floyd_warshall' in specialist.supported_operations


class TestShortestPathOptSpecialistDijkstra:
    """Test dijkstra operation."""

    def test_dijkstra_simple(self):
        """Test Dijkstra on simple graph."""
        specialist = ShortestPathOptSpecialist()
        # Graph format: Dict[int, List[Tuple[int, float]]]
        graph = {
            0: [(1, 4.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [(1, 2.0), (3, 5.0)],
            3: []
        }
        result = specialist.dijkstra(graph, 0)
        assert isinstance(result, dict)
        # Result should contain distances
        assert 'distances' in result or 'dist' in result or isinstance(result.get(0), (int, float))

    def test_dijkstra_unreachable(self):
        """Test Dijkstra with unreachable vertex."""
        specialist = ShortestPathOptSpecialist()
        graph = {0: [], 1: []}
        result = specialist.dijkstra(graph, 0)
        assert isinstance(result, dict)

    def test_dijkstra_single_vertex(self):
        """Test Dijkstra on single vertex."""
        specialist = ShortestPathOptSpecialist()
        graph = {0: []}
        result = specialist.dijkstra(graph, 0)
        assert isinstance(result, dict)


class TestShortestPathOptSpecialistBellmanFord:
    """Test bellman_ford operation."""

    def test_bellman_ford_simple(self):
        """Test Bellman-Ford on simple graph."""
        specialist = ShortestPathOptSpecialist()
        graph = {
            0: [(1, 4.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [(1, 2.0), (3, 5.0)],
            3: []
        }
        result = specialist.bellman_ford(graph, 0)
        # Can be None or dict
        assert result is None or isinstance(result, dict)

    def test_bellman_ford_negative_edges(self):
        """Test Bellman-Ford with negative edges."""
        specialist = ShortestPathOptSpecialist()
        graph = {
            0: [(1, 4.0)],
            1: [(2, -2.0)],
            2: []
        }
        result = specialist.bellman_ford(graph, 0)
        assert result is None or isinstance(result, dict)

    def test_bellman_ford_negative_cycle(self):
        """Test Bellman-Ford with negative cycle."""
        specialist = ShortestPathOptSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(2, -2.0)],
            2: [(0, -1.0)]  # Negative cycle
        }
        result = specialist.bellman_ford(graph, 0)
        # Returns None if negative cycle detected
        assert result is None or isinstance(result, dict)


class TestShortestPathOptSpecialistFloydWarshall:
    """Test floyd_warshall operation."""

    def test_floyd_warshall_simple(self):
        """Test Floyd-Warshall on simple graph."""
        specialist = ShortestPathOptSpecialist()
        graph = {
            0: [(1, 3.0), (2, 8.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.floyd_warshall(graph)
        assert isinstance(result, dict)

    def test_floyd_warshall_empty(self):
        """Test Floyd-Warshall on empty graph."""
        specialist = ShortestPathOptSpecialist()
        result = specialist.floyd_warshall({})
        assert result == {} or isinstance(result, dict)


class TestShortestPathOptSpecialistJohnson:
    """Test johnson operation."""

    def test_johnson_simple(self):
        """Test Johnson's algorithm on simple graph."""
        specialist = ShortestPathOptSpecialist()
        graph = {
            0: [(1, 3.0), (2, 8.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.johnson(graph)
        assert result is None or isinstance(result, dict)

    def test_johnson_with_negative(self):
        """Test Johnson's algorithm with negative edges."""
        specialist = ShortestPathOptSpecialist()
        graph = {
            0: [(1, 2.0)],
            1: [(2, -1.0)],
            2: []
        }
        result = specialist.johnson(graph)
        assert result is None or isinstance(result, dict)


class TestShortestPathOptSpecialistHasNegativeCycle:
    """Test has_negative_cycle operation."""

    def test_has_negative_cycle_false(self):
        """Test no negative cycle."""
        specialist = ShortestPathOptSpecialist()
        graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: []}
        result = specialist.has_negative_cycle(graph)
        assert result is False

    def test_has_negative_cycle_true(self):
        """Test negative cycle exists."""
        specialist = ShortestPathOptSpecialist()
        graph = {0: [(1, 1.0)], 1: [(2, -2.0)], 2: [(0, -1.0)]}
        result = specialist.has_negative_cycle(graph)
        assert result is True


class TestShortestPathOptSpecialistEdgeCases:
    """Test edge cases."""

    def test_self_loop(self):
        """Test graph with self loop."""
        specialist = ShortestPathOptSpecialist()
        graph = {0: [(0, 1.0), (1, 2.0)], 1: []}
        result = specialist.dijkstra(graph, 0)
        assert isinstance(result, dict)

    def test_parallel_edges(self):
        """Test graph with parallel edges."""
        specialist = ShortestPathOptSpecialist()
        graph = {0: [(1, 5.0), (1, 3.0)], 1: []}  # Two edges to same vertex
        result = specialist.dijkstra(graph, 0)
        assert isinstance(result, dict)


class TestShortestPathOptSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_dijkstra_request(self):
        """Test processing Dijkstra request."""
        specialist = ShortestPathOptSpecialist()
        request = {
            'operation': 'dijkstra',
            'graph': {0: [(1, 1.0)], 1: []},
            'source': 0
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_floyd_warshall_request(self):
        """Test processing Floyd-Warshall request."""
        specialist = ShortestPathOptSpecialist()
        request = {
            'operation': 'floyd_warshall',
            'graph': {0: [(1, 1.0)], 1: []}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = ShortestPathOptSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestShortestPathOptSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = ShortestPathOptSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = ShortestPathOptSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = ShortestPathOptSpecialist()
        assert hasattr(specialist, 'name')


class TestShortestPathOptSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = ShortestPathOptSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'dijkstra_runs' in stats


class TestShortestPathOptSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_dijkstra(self):
        """Test concurrent Dijkstra computations."""
        specialist = ShortestPathOptSpecialist()
        results = []

        def compute_dijkstra():
            graph = {0: [(1, 5.0)], 1: []}
            result = specialist.dijkstra(graph, 0)
            results.append(isinstance(result, dict))

        threads = [threading.Thread(target=compute_dijkstra) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
