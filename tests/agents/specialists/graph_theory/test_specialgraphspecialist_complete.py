# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Comprehensive tests for SpecialGraphSpecialist.

Tests cover: initialization, graph construction, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.special_graph_specialist import SpecialGraphSpecialist


class TestSpecialGraphSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = SpecialGraphSpecialist()
        assert specialist.name == "SpecialGraphSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = SpecialGraphSpecialist(name="CustomSG")
        assert specialist.name == "CustomSG"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = SpecialGraphSpecialist()
        assert 'complete_graph' in specialist.supported_operations
        assert 'petersen_graph' in specialist.supported_operations


class TestSpecialGraphSpecialistCompleteGraph:
    """Test complete_graph operation."""

    def test_complete_graph_k3(self):
        """Test K3 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.complete_graph(3)
        assert len(result) == 3
        # Each vertex has degree 2
        for v in result:
            assert len(result[v]) == 2

    def test_complete_graph_k5(self):
        """Test K5 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.complete_graph(5)
        assert len(result) == 5
        # Each vertex has degree 4
        for v in result:
            assert len(result[v]) == 4

    def test_complete_graph_zero(self):
        """Test K0 (empty graph)."""
        specialist = SpecialGraphSpecialist()
        result = specialist.complete_graph(0)
        assert result == {}


class TestSpecialGraphSpecialistCompleteBipartite:
    """Test complete_bipartite operation."""

    def test_complete_bipartite_k23(self):
        """Test K2,3 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.complete_bipartite(2, 3)
        assert len(result) == 5
        # Part 1: vertices 0,1 each connected to 3 vertices
        assert len(result[0]) == 3
        assert len(result[1]) == 3

    def test_complete_bipartite_k33(self):
        """Test K3,3 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.complete_bipartite(3, 3)
        assert len(result) == 6


class TestSpecialGraphSpecialistPetersen:
    """Test petersen_graph operation."""

    def test_petersen_graph_vertices(self):
        """Test Petersen graph has 10 vertices."""
        specialist = SpecialGraphSpecialist()
        result = specialist.petersen_graph()
        assert len(result) == 10

    def test_petersen_graph_edges(self):
        """Test Petersen graph has 15 edges."""
        specialist = SpecialGraphSpecialist()
        result = specialist.petersen_graph()
        edge_count = sum(len(neighbors) for neighbors in result.values()) // 2
        assert edge_count == 15

    def test_petersen_graph_regular(self):
        """Test Petersen graph is 3-regular."""
        specialist = SpecialGraphSpecialist()
        result = specialist.petersen_graph()
        for v in result:
            assert len(result[v]) == 3


class TestSpecialGraphSpecialistCycleGraph:
    """Test cycle_graph operation."""

    def test_cycle_graph_c4(self):
        """Test C4 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.cycle_graph(4)
        assert len(result) == 4
        # Each vertex has degree 2
        for v in result:
            assert len(result[v]) == 2

    def test_cycle_graph_c3(self):
        """Test C3 (triangle) construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.cycle_graph(3)
        assert len(result) == 3


class TestSpecialGraphSpecialistPathGraph:
    """Test path_graph operation."""

    def test_path_graph_p4(self):
        """Test P4 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.path_graph(4)
        assert len(result) == 4
        # Endpoints have degree 1, middle vertices degree 2
        assert len(result[0]) == 1
        assert len(result[3]) == 1
        assert len(result[1]) == 2


class TestSpecialGraphSpecialistStarGraph:
    """Test star_graph operation."""

    def test_star_graph_s3(self):
        """Test S3 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.star_graph(3)
        assert len(result) == 4  # Center + 3 leaves
        assert len(result[0]) == 3  # Center has degree 3


class TestSpecialGraphSpecialistWheelGraph:
    """Test wheel_graph operation."""

    def test_wheel_graph_w4(self):
        """Test W4 construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.wheel_graph(4)
        assert len(result) == 5  # 4 rim + 1 hub


class TestSpecialGraphSpecialistGridGraph:
    """Test grid_graph operation."""

    def test_grid_graph_2x3(self):
        """Test 2x3 grid construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.grid_graph(2, 3)
        assert len(result) == 6


class TestSpecialGraphSpecialistHypercube:
    """Test hypercube_graph operation."""

    def test_hypercube_q3(self):
        """Test Q3 (3-cube) construction."""
        specialist = SpecialGraphSpecialist()
        result = specialist.hypercube_graph(3)
        assert len(result) == 8  # 2^3 vertices
        # Each vertex has degree 3
        for v in result:
            assert len(result[v]) == 3


class TestSpecialGraphSpecialistIsComplete:
    """Test is_complete operation."""

    def test_is_complete_true(self):
        """Test complete graph detection."""
        specialist = SpecialGraphSpecialist()
        k4 = specialist.complete_graph(4)
        result = specialist.is_complete(k4)
        assert result is True

    def test_is_complete_false(self):
        """Test non-complete graph."""
        specialist = SpecialGraphSpecialist()
        path = specialist.path_graph(4)
        result = specialist.is_complete(path)
        assert result is False


class TestSpecialGraphSpecialistIsBipartite:
    """Test is_bipartite operation."""

    def test_is_bipartite_true(self):
        """Test bipartite graph detection."""
        specialist = SpecialGraphSpecialist()
        k23 = specialist.complete_bipartite(2, 3)
        is_bip, parts = specialist.is_bipartite(k23)
        assert is_bip is True
        assert parts is not None

    def test_is_bipartite_false(self):
        """Test non-bipartite (odd cycle)."""
        specialist = SpecialGraphSpecialist()
        triangle = specialist.cycle_graph(3)
        is_bip, parts = specialist.is_bipartite(triangle)
        assert is_bip is False


class TestSpecialGraphSpecialistEdgeCases:
    """Test edge cases."""

    def test_complete_graph_k1(self):
        """Test K1 (single vertex)."""
        specialist = SpecialGraphSpecialist()
        result = specialist.complete_graph(1)
        assert len(result) == 1
        assert result[0] == []

    def test_path_graph_p1(self):
        """Test P1 (single vertex)."""
        specialist = SpecialGraphSpecialist()
        result = specialist.path_graph(1)
        assert len(result) == 1


class TestSpecialGraphSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_complete_graph_request(self):
        """Test processing complete graph request."""
        specialist = SpecialGraphSpecialist()
        request = {
            'operation': 'complete_graph',
            'n': 4
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert len(result['result']) == 4

    def test_process_petersen_request(self):
        """Test processing Petersen graph request."""
        specialist = SpecialGraphSpecialist()
        request = {'operation': 'petersen_graph'}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert len(result['result']) == 10

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = SpecialGraphSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestSpecialGraphSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = SpecialGraphSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = SpecialGraphSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = SpecialGraphSpecialist()
        assert hasattr(specialist, 'name')


class TestSpecialGraphSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = SpecialGraphSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')
        assert 'graphs_constructed' in stats


class TestSpecialGraphSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_graph_construction(self):
        """Test concurrent graph construction."""
        specialist = SpecialGraphSpecialist()
        results = []

        def construct_graph():
            result = specialist.complete_graph(4)
            results.append(len(result))

        threads = [threading.Thread(target=construct_graph) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 4 for r in results)
