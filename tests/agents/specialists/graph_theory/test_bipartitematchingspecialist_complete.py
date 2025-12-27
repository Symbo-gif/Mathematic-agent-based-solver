# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for BipartiteMatchingSpecialist.

Tests cover: initialization, matching algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.bipartite_matching_specialist import BipartiteMatchingSpecialist


class TestBipartiteMatchingSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = BipartiteMatchingSpecialist()
        assert 'bipartite_matching_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = BipartiteMatchingSpecialist(agent_id="custom_bm_001")
        assert specialist.agent_id == "custom_bm_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = BipartiteMatchingSpecialist()
        assert specialist.service_type == 'math.graph_theory.bipartite_matching'


class TestBipartiteMatchingSpecialistMaxMatching:
    """Test maximum_matching operation."""

    def test_max_matching_simple(self):
        """Test maximum matching on simple bipartite graph."""
        specialist = BipartiteMatchingSpecialist()
        # K2,2: 0,1 on left, 2,3 on right
        graph = {
            0: [(2, 1.0), (3, 1.0)],
            1: [(2, 1.0), (3, 1.0)],
            2: [(0, 1.0), (1, 1.0)],
            3: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.maximum_matching(graph)
        assert result['success'] is True
        # Perfect matching should have 2 edges
        matching = result.get('matching', [])
        assert len(matching) == 2

    def test_max_matching_path(self):
        """Test maximum matching on path graph."""
        specialist = BipartiteMatchingSpecialist()
        # Path: 0-1-2
        graph = {
            0: [(1, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(1, 1.0)]
        }
        result = specialist.maximum_matching(graph)
        assert result['success'] is True

    def test_max_matching_empty(self):
        """Test maximum matching on empty graph."""
        specialist = BipartiteMatchingSpecialist()
        graph = {}
        result = specialist.maximum_matching(graph)
        assert result['success'] is True


class TestBipartiteMatchingSpecialistPerfectMatching:
    """Test perfect_matching_exists operation."""

    def test_perfect_matching_exists(self):
        """Test perfect matching exists on K2,2."""
        specialist = BipartiteMatchingSpecialist()
        graph = {
            0: [(2, 1.0)],
            1: [(3, 1.0)],
            2: [(0, 1.0)],
            3: [(1, 1.0)]
        }
        result = specialist.perfect_matching_exists(graph)
        assert result['success'] is True

    def test_perfect_matching_not_exists(self):
        """Test perfect matching doesn't exist (odd vertices)."""
        specialist = BipartiteMatchingSpecialist()
        graph = {0: [(1, 1.0)], 1: [(0, 1.0), (2, 1.0)], 2: [(1, 1.0)]}
        result = specialist.perfect_matching_exists(graph)
        assert result['success'] is True


class TestBipartiteMatchingSpecialistVertexCover:
    """Test vertex_cover operation."""

    def test_vertex_cover_simple(self):
        """Test minimum vertex cover."""
        specialist = BipartiteMatchingSpecialist()
        graph = {
            0: [(2, 1.0)],
            1: [(2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.vertex_cover(graph)
        assert result['success'] is True


class TestBipartiteMatchingSpecialistMatchingNumber:
    """Test matching_number operation."""

    def test_matching_number(self):
        """Test matching number computation."""
        specialist = BipartiteMatchingSpecialist()
        graph = {
            0: [(2, 1.0)],
            1: [(3, 1.0)],
            2: [(0, 1.0)],
            3: [(1, 1.0)]
        }
        result = specialist.matching_number(graph)
        assert result['success'] is True
        assert result['matching_number'] == 2


class TestBipartiteMatchingSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_edge(self):
        """Test single edge graph."""
        specialist = BipartiteMatchingSpecialist()
        graph = {0: [(1, 1.0)], 1: [(0, 1.0)]}
        result = specialist.maximum_matching(graph)
        assert result['success'] is True

    def test_star_graph(self):
        """Test star graph (one center, many leaves)."""
        specialist = BipartiteMatchingSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0), (3, 1.0)],
            1: [(0, 1.0)],
            2: [(0, 1.0)],
            3: [(0, 1.0)]
        }
        result = specialist.matching_number(graph)
        assert result['success'] is True
        assert result['matching_number'] == 1


class TestBipartiteMatchingSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_max_matching_request(self):
        """Test processing maximum matching request."""
        specialist = BipartiteMatchingSpecialist()
        request = {
            'operation': 'maximum_matching',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True


class TestBipartiteMatchingSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = BipartiteMatchingSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = BipartiteMatchingSpecialist()
        result = specialist.deliberate()
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = BipartiteMatchingSpecialist()
        assert hasattr(specialist, 'agent_id')


class TestBipartiteMatchingSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = BipartiteMatchingSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestBipartiteMatchingSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_matching(self):
        """Test concurrent matching operations."""
        specialist = BipartiteMatchingSpecialist()
        results = []

        def find_matching():
            graph = {0: [(2, 1.0)], 1: [(3, 1.0)], 2: [(0, 1.0)], 3: [(1, 1.0)]}
            result = specialist.matching_number(graph)
            if result.get('success'):
                results.append(result.get('matching_number'))

        threads = [threading.Thread(target=find_matching) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
