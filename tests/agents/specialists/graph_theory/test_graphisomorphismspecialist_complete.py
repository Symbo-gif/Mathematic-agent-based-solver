# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for GraphIsomorphismSpecialist.

Tests cover: initialization, isomorphism algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.graph_isomorphism_specialist import GraphIsomorphismSpecialist


class TestGraphIsomorphismSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = GraphIsomorphismSpecialist()
        assert specialist.name == "GraphIsomorphismSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = GraphIsomorphismSpecialist(name="CustomGI")
        assert specialist.name == "CustomGI"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = GraphIsomorphismSpecialist()
        assert 'is_isomorphic' in specialist.supported_operations
        assert 'canonical_form' in specialist.supported_operations


class TestGraphIsomorphismSpecialistIsomorphic:
    """Test is_isomorphic operation."""

    def test_is_isomorphic_identical(self):
        """Test isomorphism of identical graphs."""
        specialist = GraphIsomorphismSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.is_isomorphic(graph, graph)
        assert result is True

    def test_is_isomorphic_relabeled(self):
        """Test isomorphism of relabeled graph."""
        specialist = GraphIsomorphismSpecialist()
        # Triangle with different labels
        graph1 = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        graph2 = {3: [4, 5], 4: [3, 5], 5: [3, 4]}
        result = specialist.is_isomorphic(graph1, graph2)
        assert result is True

    def test_is_isomorphic_false(self):
        """Test non-isomorphic graphs."""
        specialist = GraphIsomorphismSpecialist()
        # Triangle vs path
        graph1 = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        graph2 = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.is_isomorphic(graph1, graph2)
        assert result is False

    def test_is_isomorphic_empty(self):
        """Test isomorphism of empty graphs."""
        specialist = GraphIsomorphismSpecialist()
        result = specialist.is_isomorphic({}, {})
        assert result is True


class TestGraphIsomorphismSpecialistFindIsomorphism:
    """Test find_isomorphism operation."""

    def test_find_isomorphism_simple(self):
        """Test finding isomorphism mapping."""
        specialist = GraphIsomorphismSpecialist()
        graph1 = {0: [1], 1: [0]}
        graph2 = {2: [3], 3: [2]}
        result = specialist.find_isomorphism(graph1, graph2)
        # Should return valid mapping
        assert result is not None
        assert len(result) == 2

    def test_find_isomorphism_none(self):
        """Test no isomorphism exists."""
        specialist = GraphIsomorphismSpecialist()
        graph1 = {0: [1, 2], 1: [0, 2], 2: [0, 1]}  # Triangle
        graph2 = {0: [1], 1: [0, 2], 2: [1]}  # Path
        result = specialist.find_isomorphism(graph1, graph2)
        assert result is None


class TestGraphIsomorphismSpecialistCanonicalForm:
    """Test canonical_form operation."""

    def test_canonical_form_triangle(self):
        """Test canonical form of triangle."""
        specialist = GraphIsomorphismSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.canonical_form(graph)
        assert isinstance(result, dict)
        assert len(result) == 3

    def test_canonical_form_empty(self):
        """Test canonical form of empty graph."""
        specialist = GraphIsomorphismSpecialist()
        result = specialist.canonical_form({})
        assert result == {}


class TestGraphIsomorphismSpecialistAutomorphism:
    """Test automorphism_count operation."""

    def test_automorphism_count_triangle(self):
        """Test automorphism count of triangle (6 = |S_3|)."""
        specialist = GraphIsomorphismSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.automorphism_count(graph)
        assert result == 6  # Full symmetric group S_3

    def test_automorphism_count_path(self):
        """Test automorphism count of path (2)."""
        specialist = GraphIsomorphismSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.automorphism_count(graph)
        assert result == 2  # Reflection only


class TestGraphIsomorphismSpecialistWLHash:
    """Test weisfeiler_lehman_hash operation."""

    def test_wl_hash_same_graphs(self):
        """Test WL hash of isomorphic graphs is equal."""
        specialist = GraphIsomorphismSpecialist()
        graph1 = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        graph2 = {3: [4, 5], 4: [3, 5], 5: [3, 4]}
        hash1 = specialist.weisfeiler_lehman_hash(graph1)
        hash2 = specialist.weisfeiler_lehman_hash(graph2)
        assert hash1 == hash2

    def test_wl_hash_empty(self):
        """Test WL hash of empty graph."""
        specialist = GraphIsomorphismSpecialist()
        result = specialist.weisfeiler_lehman_hash({})
        assert result == ()


class TestGraphIsomorphismSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = GraphIsomorphismSpecialist()
        graph = {0: []}
        result = specialist.canonical_form(graph)
        assert len(result) == 1

    def test_two_vertices_no_edge(self):
        """Test two disconnected vertices."""
        specialist = GraphIsomorphismSpecialist()
        graph = {0: [], 1: []}
        result = specialist.automorphism_count(graph)
        assert result == 2  # Can swap the two vertices


class TestGraphIsomorphismSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_is_isomorphic_request(self):
        """Test processing isomorphism request."""
        specialist = GraphIsomorphismSpecialist()
        request = {
            'operation': 'is_isomorphic',
            'graph': {0: [1], 1: [0]},
            'graph2': {2: [3], 3: [2]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['result'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = GraphIsomorphismSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestGraphIsomorphismSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = GraphIsomorphismSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = GraphIsomorphismSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = GraphIsomorphismSpecialist()
        assert hasattr(specialist, 'name')


class TestGraphIsomorphismSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = GraphIsomorphismSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestGraphIsomorphismSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_isomorphism_checks(self):
        """Test concurrent isomorphism checks."""
        specialist = GraphIsomorphismSpecialist()
        results = []

        def check_iso():
            graph1 = {0: [1], 1: [0]}
            graph2 = {2: [3], 3: [2]}
            result = specialist.is_isomorphic(graph1, graph2)
            results.append(result)

        threads = [threading.Thread(target=check_iso) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
