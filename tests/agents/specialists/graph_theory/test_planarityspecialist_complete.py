# Copyright 2025 Mathematic Agent Based Solver
# Licensed under the Apache License, Version 2.0

"""
Comprehensive tests for PlanaritySpecialist.

Tests cover: initialization, planarity testing, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.planarity_specialist import PlanaritySpecialist


class TestPlanaritySpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = PlanaritySpecialist()
        assert specialist.name == "PlanaritySpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = PlanaritySpecialist(name="CustomPlanarity")
        assert specialist.name == "CustomPlanarity"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = PlanaritySpecialist()
        assert 'is_planar' in specialist.supported_operations
        assert 'planar_embedding' in specialist.supported_operations


class TestPlanaritySpecialistIsPlanar:
    """Test is_planar operation."""

    def test_is_planar_k4(self):
        """Test K4 is planar."""
        specialist = PlanaritySpecialist()
        # Complete graph K4
        k4 = {i: [j for j in range(4) if j != i] for i in range(4)}
        result = specialist.is_planar(k4)
        assert result is True

    def test_is_planar_k5(self):
        """Test K5 is not planar."""
        specialist = PlanaritySpecialist()
        # Complete graph K5
        k5 = {i: [j for j in range(5) if j != i] for i in range(5)}
        result = specialist.is_planar(k5)
        assert result is False

    def test_is_planar_k33(self):
        """Test K3,3 is not planar."""
        specialist = PlanaritySpecialist()
        # Complete bipartite K3,3
        k33 = {
            0: [3, 4, 5], 1: [3, 4, 5], 2: [3, 4, 5],
            3: [0, 1, 2], 4: [0, 1, 2], 5: [0, 1, 2]
        }
        result = specialist.is_planar(k33)
        assert result is False

    def test_is_planar_empty(self):
        """Test empty graph is planar."""
        specialist = PlanaritySpecialist()
        result = specialist.is_planar({})
        assert result is True

    def test_is_planar_tree(self):
        """Test trees are planar."""
        specialist = PlanaritySpecialist()
        # Star graph
        star = {0: [1, 2, 3, 4], 1: [0], 2: [0], 3: [0], 4: [0]}
        result = specialist.is_planar(star)
        assert result is True


class TestPlanaritySpecialistPlanarEmbedding:
    """Test planar_embedding operation."""

    def test_planar_embedding_triangle(self):
        """Test planar embedding of triangle."""
        specialist = PlanaritySpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.planar_embedding(graph)
        assert result is not None
        assert isinstance(result, dict)

    def test_planar_embedding_nonplanar(self):
        """Test planar embedding of non-planar graph returns None."""
        specialist = PlanaritySpecialist()
        k5 = {i: [j for j in range(5) if j != i] for i in range(5)}
        result = specialist.planar_embedding(k5)
        assert result is None


class TestPlanaritySpecialistFindKuratowski:
    """Test find_kuratowski operation."""

    def test_find_kuratowski_k5(self):
        """Test finding K5 Kuratowski subgraph."""
        specialist = PlanaritySpecialist()
        k5 = {i: [j for j in range(5) if j != i] for i in range(5)}
        result = specialist.find_kuratowski(k5)
        assert result is not None
        assert len(result) >= 5

    def test_find_kuratowski_planar(self):
        """Test no Kuratowski for planar graph."""
        specialist = PlanaritySpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.find_kuratowski(graph)
        assert result is None


class TestPlanaritySpecialistFaceCount:
    """Test face_count operation."""

    def test_face_count_triangle(self):
        """Test face count of triangle using Euler formula."""
        specialist = PlanaritySpecialist()
        # Triangle: V=3, E=3, F = E - V + 2 = 2
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.face_count(graph)
        assert result == 2

    def test_face_count_empty(self):
        """Test face count of empty graph."""
        specialist = PlanaritySpecialist()
        result = specialist.face_count({})
        assert result == 1  # Outer infinite face


class TestPlanaritySpecialistOuterplanar:
    """Test is_outerplanar operation."""

    def test_is_outerplanar_cycle(self):
        """Test cycle is outerplanar."""
        specialist = PlanaritySpecialist()
        # C4
        c4 = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}
        result = specialist.is_outerplanar(c4)
        assert result is True

    def test_is_outerplanar_k4(self):
        """Test K4 is not outerplanar."""
        specialist = PlanaritySpecialist()
        k4 = {i: [j for j in range(4) if j != i] for i in range(4)}
        result = specialist.is_outerplanar(k4)
        assert result is False


class TestPlanaritySpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = PlanaritySpecialist()
        graph = {0: []}
        result = specialist.is_planar(graph)
        assert result is True

    def test_two_vertices(self):
        """Test two vertex graph."""
        specialist = PlanaritySpecialist()
        graph = {0: [1], 1: [0]}
        result = specialist.is_planar(graph)
        assert result is True


class TestPlanaritySpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_is_planar_request(self):
        """Test processing planarity request."""
        specialist = PlanaritySpecialist()
        request = {
            'operation': 'is_planar',
            'graph': {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['result'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = PlanaritySpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestPlanaritySpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = PlanaritySpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = PlanaritySpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = PlanaritySpecialist()
        assert hasattr(specialist, 'name')


class TestPlanaritySpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = PlanaritySpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')
        assert 'planarity_tests' in stats


class TestPlanaritySpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_planarity_checks(self):
        """Test concurrent planarity checking."""
        specialist = PlanaritySpecialist()
        results = []

        def check_planarity():
            graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
            result = specialist.is_planar(graph)
            results.append(result)

        threads = [threading.Thread(target=check_planarity) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
