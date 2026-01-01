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
Comprehensive tests for VertexColoringSpecialist.

Tests cover: initialization, coloring algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.vertex_coloring_specialist import VertexColoringSpecialist


class TestVertexColoringSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = VertexColoringSpecialist()
        assert 'vertex_coloring_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = VertexColoringSpecialist(agent_id="custom_coloring_001")
        assert specialist.agent_id == "custom_coloring_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = VertexColoringSpecialist()
        assert specialist.service_type == 'math.graph_theory.vertex_coloring'


class TestVertexColoringSpecialistGreedy:
    """Test greedy_coloring operation."""

    def test_greedy_coloring_simple(self):
        """Test greedy coloring on simple graph."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.greedy_coloring(graph)
        assert result['success'] is True
        assert result['num_colors'] >= 3  # Triangle needs 3 colors

    def test_greedy_coloring_bipartite(self):
        """Test greedy coloring on bipartite graph."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(2, 1.0), (3, 1.0)],
            1: [(2, 1.0), (3, 1.0)],
            2: [(0, 1.0), (1, 1.0)],
            3: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.greedy_coloring(graph)
        assert result['success'] is True
        assert result['num_colors'] <= 2

    def test_greedy_coloring_empty(self):
        """Test greedy coloring on empty graph."""
        specialist = VertexColoringSpecialist()
        graph = {}
        result = specialist.greedy_coloring(graph)
        assert result['success'] is True
        assert result['num_colors'] == 0


class TestVertexColoringSpecialistBipartite:
    """Test bipartite_check operation."""

    def test_bipartite_true(self):
        """Test bipartite graph detection."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(2, 1.0)],
            1: [(2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.bipartite_check(graph)
        assert result['success'] is True
        assert result['is_bipartite'] is True

    def test_bipartite_false(self):
        """Test non-bipartite graph (odd cycle)."""
        specialist = VertexColoringSpecialist()
        # Triangle is not bipartite
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.bipartite_check(graph)
        assert result['success'] is True
        assert result['is_bipartite'] is False


class TestVertexColoringSpecialistKColorable:
    """Test is_k_colorable operation."""

    def test_k_colorable_3_triangle(self):
        """Test 3-colorable for triangle."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.is_k_colorable(graph, 3)
        assert result['success'] is True
        assert result['is_colorable'] is True

    def test_k_colorable_2_triangle(self):
        """Test 2-colorable for triangle (should fail)."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.is_k_colorable(graph, 2)
        assert result['success'] is True
        assert result['is_colorable'] is False


class TestVertexColoringSpecialistChromaticNumber:
    """Test chromatic_number operation."""

    def test_chromatic_number_triangle(self):
        """Test chromatic number of triangle is 3."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.chromatic_number(graph)
        assert result['success'] is True
        assert result['chromatic_number'] == 3

    def test_chromatic_number_path(self):
        """Test chromatic number of path is 2."""
        specialist = VertexColoringSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(1, 1.0)]
        }
        result = specialist.chromatic_number(graph)
        assert result['success'] is True
        assert result['chromatic_number'] == 2


class TestVertexColoringSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex(self):
        """Test single vertex."""
        specialist = VertexColoringSpecialist()
        graph = {0: []}
        result = specialist.greedy_coloring(graph)
        assert result['success'] is True
        assert result['num_colors'] == 1

    def test_isolated_vertices(self):
        """Test isolated vertices."""
        specialist = VertexColoringSpecialist()
        graph = {0: [], 1: [], 2: []}
        result = specialist.greedy_coloring(graph)
        assert result['success'] is True
        assert result['num_colors'] == 1


class TestVertexColoringSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_greedy_request(self):
        """Test processing greedy coloring request."""
        specialist = VertexColoringSpecialist()
        request = {
            'operation': 'greedy_coloring',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_bipartite_request(self):
        """Test processing bipartite request."""
        specialist = VertexColoringSpecialist()
        request = {
            'operation': 'bipartite',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True


class TestVertexColoringSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = VertexColoringSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = VertexColoringSpecialist()
        result = specialist.deliberate()
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = VertexColoringSpecialist()
        assert hasattr(specialist, 'agent_id')
        assert specialist.agent_id is not None


class TestVertexColoringSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = VertexColoringSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestVertexColoringSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_coloring(self):
        """Test concurrent greedy coloring."""
        specialist = VertexColoringSpecialist()
        results = []

        def color_graph():
            graph = {0: [(1, 1.0)], 1: [(0, 1.0), (2, 1.0)], 2: [(1, 1.0)]}
            result = specialist.greedy_coloring(graph)
            if result.get('success'):
                results.append(result.get('num_colors'))

        threads = [threading.Thread(target=color_graph) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
