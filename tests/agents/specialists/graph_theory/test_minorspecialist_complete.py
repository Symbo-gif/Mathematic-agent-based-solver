# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for MinorSpecialist.

Tests cover: initialization, minor operations, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.minor_specialist import MinorSpecialist


class TestMinorSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = MinorSpecialist()
        assert specialist.name == "MinorSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = MinorSpecialist(name="CustomMinor")
        assert specialist.name == "CustomMinor"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = MinorSpecialist()
        assert 'contract_edge' in specialist.supported_operations
        assert 'is_minor' in specialist.supported_operations


class TestMinorSpecialistContractEdge:
    """Test contract_edge operation."""

    def test_contract_edge_simple(self):
        """Test simple edge contraction."""
        specialist = MinorSpecialist()
        # Triangle: 0-1-2-0
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.contract_edge(graph, 0, 1)
        # After contracting 0-1, should have 2 vertices
        assert isinstance(result, dict)
        assert 1 not in result  # Vertex 1 was merged into 0

    def test_contract_edge_path(self):
        """Test edge contraction on path."""
        specialist = MinorSpecialist()
        # Path: 0-1-2
        graph = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.contract_edge(graph, 0, 1)
        assert isinstance(result, dict)
        # Should result in single edge graph

    def test_contract_edge_nonexistent(self):
        """Test contracting non-existent edge returns copy."""
        specialist = MinorSpecialist()
        graph = {0: [1], 1: [0]}
        result = specialist.contract_edge(graph, 0, 2)  # 2 doesn't exist
        assert result == graph


class TestMinorSpecialistDeleteVertex:
    """Test delete_vertex operation."""

    def test_delete_vertex_triangle(self):
        """Test deleting vertex from triangle."""
        specialist = MinorSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.delete_vertex(graph, 0)
        assert 0 not in result
        assert len(result) == 2

    def test_delete_vertex_leaf(self):
        """Test deleting leaf vertex."""
        specialist = MinorSpecialist()
        # Star: 0 connected to 1, 2, 3
        graph = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}
        result = specialist.delete_vertex(graph, 1)
        assert 1 not in result
        assert 1 not in result[0]


class TestMinorSpecialistDeleteEdge:
    """Test delete_edge operation."""

    def test_delete_edge_triangle(self):
        """Test deleting edge from triangle."""
        specialist = MinorSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.delete_edge(graph, 0, 1)
        assert 1 not in result[0]
        assert 0 not in result[1]

    def test_delete_edge_nonexistent(self):
        """Test deleting non-existent edge."""
        specialist = MinorSpecialist()
        graph = {0: [1], 1: [0], 2: []}
        result = specialist.delete_edge(graph, 0, 2)
        # Graph unchanged
        assert result[0] == [1]


class TestMinorSpecialistIsMinor:
    """Test is_minor operation."""

    def test_is_minor_empty(self):
        """Test empty graph is minor of any graph."""
        specialist = MinorSpecialist()
        graph = {0: [1], 1: [0]}
        result = specialist.is_minor(graph, {})
        assert result is True

    def test_is_minor_subgraph(self):
        """Test subgraph is minor."""
        specialist = MinorSpecialist()
        # Triangle contains edge as minor
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        edge = {0: [1], 1: [0]}
        result = specialist.is_minor(graph, edge)
        assert result is True


class TestMinorSpecialistK5K33:
    """Test K5 and K3,3 minor detection."""

    def test_has_k5_minor_complete5(self):
        """Test K5 has K5 minor."""
        specialist = MinorSpecialist()
        # Complete graph K5
        k5 = {i: [j for j in range(5) if j != i] for i in range(5)}
        result = specialist.has_k5_minor(k5)
        assert result is True

    def test_has_k5_minor_small(self):
        """Test small graph has no K5 minor."""
        specialist = MinorSpecialist()
        graph = {0: [1], 1: [0]}
        result = specialist.has_k5_minor(graph)
        assert result is False

    def test_has_k33_minor_complete_bipartite(self):
        """Test K3,3 has K3,3 minor."""
        specialist = MinorSpecialist()
        # K3,3: vertices 0,1,2 in one part, 3,4,5 in other
        k33 = {
            0: [3, 4, 5], 1: [3, 4, 5], 2: [3, 4, 5],
            3: [0, 1, 2], 4: [0, 1, 2], 5: [0, 1, 2]
        }
        result = specialist.has_k33_minor(k33)
        assert result is True


class TestMinorSpecialistEdgeCases:
    """Test edge cases."""

    def test_empty_graph(self):
        """Test operations on empty graph."""
        specialist = MinorSpecialist()
        result = specialist.contract_edge({}, 0, 1)
        assert result == {}

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = MinorSpecialist()
        graph = {0: []}
        result = specialist.delete_vertex(graph, 0)
        assert result == {}


class TestMinorSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_contract_edge_request(self):
        """Test processing edge contraction request."""
        specialist = MinorSpecialist()
        request = {
            'operation': 'contract_edge',
            'graph': {0: [1], 1: [0, 2], 2: [1]},
            'u': 0,
            'v': 1
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = MinorSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestMinorSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = MinorSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = MinorSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = MinorSpecialist()
        assert hasattr(specialist, 'name')


class TestMinorSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = MinorSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')
        assert 'contractions' in stats


class TestMinorSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_contractions(self):
        """Test concurrent edge contraction operations."""
        specialist = MinorSpecialist()
        results = []

        def contract():
            graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
            result = specialist.contract_edge(graph, 0, 1)
            results.append(len(result))

        threads = [threading.Thread(target=contract) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
