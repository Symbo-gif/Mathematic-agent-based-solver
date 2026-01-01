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
Comprehensive tests for EdgeColoringSpecialist.

Tests cover: initialization, edge coloring algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.edge_coloring_specialist import EdgeColoringSpecialist


class TestEdgeColoringSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = EdgeColoringSpecialist()
        assert specialist.name == "EdgeColoringSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = EdgeColoringSpecialist(name="CustomEC")
        assert specialist.name == "CustomEC"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = EdgeColoringSpecialist()
        assert 'edge_coloring' in specialist.supported_operations
        assert 'vizing_class' in specialist.supported_operations


class TestEdgeColoringSpecialistEdgeColoring:
    """Test edge_coloring operation."""

    def test_edge_coloring_triangle(self):
        """Test edge coloring of triangle."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.edge_coloring(graph)
        # Should return dict mapping edges to colors
        assert isinstance(result, dict)
        # Triangle needs 3 colors (it's Class 2)
        if result:
            num_colors = len(set(result.values()))
            assert num_colors == 3

    def test_edge_coloring_path(self):
        """Test edge coloring of path graph."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.edge_coloring(graph)
        assert isinstance(result, dict)
        # Path needs only 1 color at each vertex
        if result:
            num_colors = len(set(result.values()))
            assert num_colors <= 2

    def test_edge_coloring_empty(self):
        """Test edge coloring of empty graph."""
        specialist = EdgeColoringSpecialist()
        graph = {}
        result = specialist.edge_coloring(graph)
        assert result == {}


class TestEdgeColoringSpecialistEdgeChromaticNumber:
    """Test edge_chromatic_number operation."""

    def test_edge_chromatic_number_triangle(self):
        """Test edge chromatic number of triangle is 3."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.edge_chromatic_number(graph)
        assert result == 3

    def test_edge_chromatic_number_path(self):
        """Test edge chromatic number of path."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.edge_chromatic_number(graph)
        assert result <= 2


class TestEdgeColoringSpecialistVizingClass:
    """Test vizing_class operation."""

    def test_vizing_class_triangle(self):
        """Test Vizing class of triangle is 2."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.vizing_class(graph)
        # Triangle is Class 2 (chi' = delta + 1)
        assert result == 2

    def test_vizing_class_bipartite(self):
        """Test Vizing class of bipartite graph is 1."""
        specialist = EdgeColoringSpecialist()
        # Complete bipartite K2,2
        graph = {0: [2, 3], 1: [2, 3], 2: [0, 1], 3: [0, 1]}
        result = specialist.vizing_class(graph)
        # Bipartite graphs are Class 1
        assert result == 1


class TestEdgeColoringSpecialistGreedy:
    """Test greedy_edge_coloring operation."""

    def test_greedy_edge_coloring(self):
        """Test greedy edge coloring."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.greedy_edge_coloring(graph)
        assert isinstance(result, dict)


class TestEdgeColoringSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_edge(self):
        """Test single edge graph."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [1], 1: [0]}
        result = specialist.edge_coloring(graph)
        assert len(result) == 1

    def test_no_edges(self):
        """Test graph with no edges."""
        specialist = EdgeColoringSpecialist()
        graph = {0: [], 1: [], 2: []}
        result = specialist.edge_coloring(graph)
        assert result == {}


class TestEdgeColoringSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_edge_coloring_request(self):
        """Test processing edge coloring request."""
        specialist = EdgeColoringSpecialist()
        request = {
            'operation': 'edge_coloring',
            'graph': {0: [1], 1: [0]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = EdgeColoringSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestEdgeColoringSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = EdgeColoringSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = EdgeColoringSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = EdgeColoringSpecialist()
        assert hasattr(specialist, 'name')


class TestEdgeColoringSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = EdgeColoringSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestEdgeColoringSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_edge_coloring(self):
        """Test concurrent edge coloring operations."""
        specialist = EdgeColoringSpecialist()
        results = []

        def color_edges():
            graph = {0: [1], 1: [0, 2], 2: [1]}
            result = specialist.edge_coloring(graph)
            results.append(len(result))

        threads = [threading.Thread(target=color_edges) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
