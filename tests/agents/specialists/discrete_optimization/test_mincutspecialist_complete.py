# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for MinCutSpecialist.

Tests cover: initialization, min-cut algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.min_cut_specialist import MinCutSpecialist


class TestMinCutSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = MinCutSpecialist()
        assert specialist.name == "MinCutSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = MinCutSpecialist(name="CustomMinCut")
        assert specialist.name == "CustomMinCut"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = MinCutSpecialist()
        assert 'st_min_cut' in specialist.supported_operations
        assert 'global_min_cut' in specialist.supported_operations


class TestMinCutSpecialistSTMinCut:
    """Test st_min_cut operation."""

    def test_st_min_cut_simple(self):
        """Test s-t min cut on simple network."""
        specialist = MinCutSpecialist()
        # Graph format: Dict[int, Dict[int, float]]
        graph = {
            0: {1: 10.0, 2: 5.0},
            1: {2: 4.0, 3: 8.0},
            2: {3: 9.0},
            3: {}
        }
        S, T, cut_value = specialist.st_min_cut(graph, 0, 3)
        assert cut_value > 0
        assert 0 in S
        assert 3 in T

    def test_st_min_cut_disconnected(self):
        """Test s-t min cut when disconnected."""
        specialist = MinCutSpecialist()
        graph = {0: {}, 1: {}}
        S, T, cut_value = specialist.st_min_cut(graph, 0, 1)
        assert cut_value == 0

    def test_st_min_cut_single_edge(self):
        """Test s-t min cut with single edge."""
        specialist = MinCutSpecialist()
        graph = {0: {1: 5.0}, 1: {}}
        S, T, cut_value = specialist.st_min_cut(graph, 0, 1)
        assert cut_value == 5.0


class TestMinCutSpecialistGlobalMinCut:
    """Test global_min_cut operation (Stoer-Wagner)."""

    def test_global_min_cut_empty(self):
        """Test global min cut on empty graph."""
        specialist = MinCutSpecialist()
        S, T, cut_value = specialist.global_min_cut({})
        assert cut_value == 0

    def test_global_min_cut_single_vertex(self):
        """Test global min cut with single vertex."""
        specialist = MinCutSpecialist()
        graph = {0: {}}
        S, T, cut_value = specialist.global_min_cut(graph)
        assert cut_value == 0


class TestMinCutSpecialistCutValue:
    """Test cut_value operation."""

    def test_cut_value_computation(self):
        """Test cut value computation."""
        specialist = MinCutSpecialist()
        graph = {
            0: {1: 5.0, 2: 3.0},
            1: {0: 5.0, 2: 4.0},
            2: {0: 3.0, 1: 4.0}
        }
        # Cut: {0} vs {1, 2}
        S = {0}
        value = specialist.cut_value(graph, S)
        assert value == 8.0  # 5 + 3


class TestMinCutSpecialistMinCutEdges:
    """Test min_cut_edges operation."""

    def test_min_cut_edges(self):
        """Test min cut edges computation."""
        specialist = MinCutSpecialist()
        graph = {
            0: {1: 2.0},
            1: {0: 2.0, 2: 3.0},
            2: {1: 3.0}
        }
        S = {0}
        T = {1, 2}
        edges = specialist.min_cut_edges(graph, S, T)
        assert len(edges) > 0


class TestMinCutSpecialistEdgeCases:
    """Test edge cases."""

    def test_two_vertices_one_edge(self):
        """Test two vertices with one edge."""
        specialist = MinCutSpecialist()
        graph = {0: {1: 7.0}, 1: {}}
        S, T, cut_value = specialist.st_min_cut(graph, 0, 1)
        assert cut_value == 7.0

    def test_simple_path_network(self):
        """Test simple path network."""
        specialist = MinCutSpecialist()
        graph = {
            0: {1: 10.0},
            1: {2: 5.0},
            2: {}
        }
        S, T, cut_value = specialist.st_min_cut(graph, 0, 2)
        assert cut_value == 5.0  # Minimum of 10 and 5


class TestMinCutSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_st_min_cut_request(self):
        """Test processing s-t min cut request."""
        specialist = MinCutSpecialist()
        request = {
            'operation': 'st_min_cut',
            'graph': {0: {1: 5.0}, 1: {}},
            'source': 0,
            'sink': 1
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = MinCutSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestMinCutSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = MinCutSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = MinCutSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = MinCutSpecialist()
        assert hasattr(specialist, 'name')


class TestMinCutSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = MinCutSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'st_cuts' in stats or 'global_cuts' in stats


class TestMinCutSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_min_cuts(self):
        """Test concurrent min cut computations."""
        specialist = MinCutSpecialist()
        results = []

        def compute_cut():
            graph = {0: {1: 5.0}, 1: {}}
            S, T, cut_value = specialist.st_min_cut(graph, 0, 1)
            results.append(cut_value)

        threads = [threading.Thread(target=compute_cut) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
        assert all(r == 5.0 for r in results)
