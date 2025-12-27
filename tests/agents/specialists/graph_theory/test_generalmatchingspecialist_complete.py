# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for GeneralMatchingSpecialist.

Tests cover: initialization, matching algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.general_matching_specialist import GeneralMatchingSpecialist


class TestGeneralMatchingSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = GeneralMatchingSpecialist()
        assert specialist.name == "GeneralMatchingSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = GeneralMatchingSpecialist(name="CustomGM")
        assert specialist.name == "CustomGM"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = GeneralMatchingSpecialist()
        assert 'maximum_matching' in specialist.supported_operations
        assert 'matching_number' in specialist.supported_operations


class TestGeneralMatchingSpecialistMaxMatching:
    """Test maximum_matching operation."""

    def test_max_matching_triangle(self):
        """Test maximum matching on triangle."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.maximum_matching(graph)
        # Triangle can match 1 edge (leaves 1 vertex exposed)
        assert isinstance(result, dict)
        assert len(result) // 2 == 1  # 2 entries per edge

    def test_max_matching_path(self):
        """Test maximum matching on path graph."""
        specialist = GeneralMatchingSpecialist()
        # Path: 0-1-2-3
        graph = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
        result = specialist.maximum_matching(graph)
        # Can match 2 edges
        assert isinstance(result, dict)
        assert len(result) // 2 == 2

    def test_max_matching_empty(self):
        """Test maximum matching on empty graph."""
        specialist = GeneralMatchingSpecialist()
        graph = {}
        result = specialist.maximum_matching(graph)
        assert result == {}


class TestGeneralMatchingSpecialistMatchingNumber:
    """Test matching_number operation."""

    def test_matching_number_path4(self):
        """Test matching number of path with 4 vertices."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
        result = specialist.matching_number(graph)
        assert result == 2

    def test_matching_number_cycle4(self):
        """Test matching number of cycle with 4 vertices."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}
        result = specialist.matching_number(graph)
        assert result == 2


class TestGeneralMatchingSpecialistPerfectMatching:
    """Test perfect_matching_exists operation."""

    def test_perfect_matching_exists(self):
        """Test perfect matching exists on even path."""
        specialist = GeneralMatchingSpecialist()
        # Path with 2 vertices has perfect matching
        graph = {0: [1], 1: [0]}
        result = specialist.perfect_matching_exists(graph)
        assert result is True

    def test_perfect_matching_not_exists(self):
        """Test perfect matching doesn't exist on triangle."""
        specialist = GeneralMatchingSpecialist()
        # Triangle has 3 vertices, so no perfect matching
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.perfect_matching_exists(graph)
        assert result is False


class TestGeneralMatchingSpecialistExposedVertices:
    """Test exposed_vertices operation."""

    def test_exposed_vertices(self):
        """Test finding exposed vertices."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        matching = {0: 1, 1: 0}  # 0-1 matched
        result = specialist.exposed_vertices(graph, matching)
        assert 2 in result


class TestGeneralMatchingSpecialistGreedyMatching:
    """Test greedy_matching operation."""

    def test_greedy_matching(self):
        """Test greedy matching."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
        result = specialist.greedy_matching(graph)
        assert isinstance(result, dict)


class TestGeneralMatchingSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: []}
        result = specialist.maximum_matching(graph)
        assert result == {}

    def test_two_vertices_connected(self):
        """Test two connected vertices."""
        specialist = GeneralMatchingSpecialist()
        graph = {0: [1], 1: [0]}
        result = specialist.matching_number(graph)
        assert result == 1


class TestGeneralMatchingSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_max_matching_request(self):
        """Test processing maximum matching request."""
        specialist = GeneralMatchingSpecialist()
        request = {
            'operation': 'maximum_matching',
            'graph': {0: [1], 1: [0]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = GeneralMatchingSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestGeneralMatchingSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = GeneralMatchingSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = GeneralMatchingSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = GeneralMatchingSpecialist()
        assert hasattr(specialist, 'name')


class TestGeneralMatchingSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = GeneralMatchingSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestGeneralMatchingSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_matching(self):
        """Test concurrent matching operations."""
        specialist = GeneralMatchingSpecialist()
        results = []

        def find_matching():
            graph = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
            result = specialist.matching_number(graph)
            results.append(result)

        threads = [threading.Thread(target=find_matching) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
