# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for MSTSpecialist.

Tests cover: initialization, Prim/Kruskal algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.mst_specialist import MSTSpecialist


class TestMSTSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = MSTSpecialist()
        assert specialist.name == "MSTSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = MSTSpecialist(name="CustomMST")
        assert specialist.name == "CustomMST"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = MSTSpecialist()
        assert hasattr(specialist, 'supported_operations')


class TestMSTSpecialistPrim:
    """Test Prim's algorithm."""

    def test_prim_simple(self):
        """Test Prim's on simple triangle graph."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0), (2, 3.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 3.0), (1, 1.0)]
        }
        result = specialist.prim(graph)
        # Returns list of edges
        assert isinstance(result, list)
        assert len(result) == 2
        # Total weight should be 2
        total_weight = sum(edge[2] for edge in result)
        assert total_weight == 2.0

    def test_prim_linear(self):
        """Test Prim's on linear graph."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(0, 1.0), (2, 2.0)],
            2: [(1, 2.0)]
        }
        result = specialist.prim(graph)
        assert len(result) == 2
        total_weight = sum(edge[2] for edge in result)
        assert total_weight == 3.0

    def test_prim_single_vertex(self):
        """Test Prim's on single vertex."""
        specialist = MSTSpecialist()
        graph = {0: []}
        result = specialist.prim(graph)
        assert isinstance(result, list)
        assert len(result) == 0


class TestMSTSpecialistKruskal:
    """Test Kruskal's algorithm."""

    def test_kruskal_simple(self):
        """Test Kruskal's on simple graph."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0), (2, 3.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 3.0), (1, 1.0)]
        }
        result = specialist.kruskal(graph)
        assert isinstance(result, list)
        assert len(result) == 2
        total_weight = sum(edge[2] for edge in result)
        assert total_weight == 2.0

    def test_kruskal_disconnected(self):
        """Test Kruskal's on disconnected graph."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0)], 1: [(0, 1.0)],
            2: [(3, 2.0)], 3: [(2, 2.0)]
        }
        result = specialist.kruskal(graph)
        # Spanning forest - should have 2 edges for 4 vertices in 2 components
        assert isinstance(result, list)


class TestMSTSpecialistEdgeCases:
    """Test edge cases."""

    def test_empty_graph(self):
        """Test empty graph."""
        specialist = MSTSpecialist()
        graph = {}
        result = specialist.prim(graph)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_complete_graph(self):
        """Test complete graph K4."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0), (2, 2.0), (3, 3.0)],
            1: [(0, 1.0), (2, 4.0), (3, 5.0)],
            2: [(0, 2.0), (1, 4.0), (3, 6.0)],
            3: [(0, 3.0), (1, 5.0), (2, 6.0)]
        }
        result = specialist.prim(graph)
        assert len(result) == 3  # n-1 edges for n vertices

    def test_parallel_edges_min_chosen(self):
        """Test that minimum edge is chosen with parallel edges."""
        specialist = MSTSpecialist()
        # Graph with two edges between 0 and 1
        graph = {
            0: [(1, 1.0), (1, 5.0)],
            1: [(0, 1.0), (0, 5.0)]
        }
        result = specialist.prim(graph)
        assert len(result) == 1
        # Should choose weight 1, not 5
        assert result[0][2] == 1.0


class TestMSTSpecialistVerification:
    """Test MST verification."""

    def test_verify_mst_valid(self):
        """Test verify MST on valid tree."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0), (2, 2.0)],
            1: [(0, 1.0), (2, 3.0)],
            2: [(0, 2.0), (1, 3.0)]
        }
        tree = [(0, 1, 1.0), (0, 2, 2.0)]
        result = specialist.is_mst(graph, tree)
        assert result is True

    def test_mst_weight(self):
        """Test MST weight computation."""
        specialist = MSTSpecialist()
        graph = {
            0: [(1, 1.0), (2, 2.0)],
            1: [(0, 1.0), (2, 3.0)],
            2: [(0, 2.0), (1, 3.0)]
        }
        weight = specialist.mst_weight(graph)
        assert weight == 3.0


class TestMSTSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_prim_request(self):
        """Test processing prim request."""
        specialist = MSTSpecialist()
        request = {
            'operation': 'prim',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_kruskal_request(self):
        """Test processing kruskal request."""
        specialist = MSTSpecialist()
        request = {
            'operation': 'kruskal',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = MSTSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestMSTSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = MSTSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = MSTSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_execute_step_no_blackboard(self):
        """Test execute_step with no blackboard."""
        specialist = MSTSpecialist()
        result = specialist.execute_step()
        assert result is False


class TestMSTSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = MSTSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)


class TestMSTSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_mst_computations(self):
        """Test concurrent MST computations."""
        specialist = MSTSpecialist()
        results = []

        def compute_mst():
            graph = {
                0: [(1, 1.0), (2, 2.0)],
                1: [(0, 1.0), (2, 3.0)],
                2: [(0, 2.0), (1, 3.0)]
            }
            mst = specialist.prim(graph)
            total = sum(e[2] for e in mst)
            results.append(total)

        threads = [threading.Thread(target=compute_mst) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 3.0 for r in results)
