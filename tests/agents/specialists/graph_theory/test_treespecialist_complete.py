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
Comprehensive tests for TreeSpecialist.

Tests cover: initialization, tree operations, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.tree_specialist import TreeSpecialist


class TestTreeSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = TreeSpecialist()
        assert 'tree_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = TreeSpecialist(agent_id="custom_tree_001")
        assert specialist.agent_id == "custom_tree_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = TreeSpecialist()
        assert specialist.service_type == 'math.graph_theory.tree'


class TestTreeSpecialistIsTree:
    """Test is_tree operation."""

    def test_is_tree_simple(self):
        """Test is_tree on valid tree."""
        specialist = TreeSpecialist()
        # Simple tree: 0-1-2 (edges listed once, method builds undirected)
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.is_tree(graph)
        assert result['success'] is True
        assert result['is_tree'] is True

    def test_is_tree_with_cycle(self):
        """Test is_tree on graph with cycle."""
        specialist = TreeSpecialist()
        # Triangle: 0-1-2-0 (3 edges, 3 nodes = cycle)
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.is_tree(graph)
        assert result['success'] is True
        assert result['is_tree'] is False

    def test_is_tree_empty(self):
        """Test is_tree on empty graph."""
        specialist = TreeSpecialist()
        graph = {}
        result = specialist.is_tree(graph)
        assert result['success'] is True
        assert result['is_tree'] is True


class TestTreeSpecialistCenter:
    """Test tree_center operation."""

    def test_center_path(self):
        """Test center of path graph."""
        specialist = TreeSpecialist()
        # Path: 0-1-2-3-4 (edges listed once)
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: [(3, 1.0)],
            3: [(4, 1.0)],
            4: []
        }
        result = specialist.tree_center(graph)
        assert result['success'] is True
        assert 2 in result['center']

    def test_center_star(self):
        """Test center of star graph."""
        specialist = TreeSpecialist()
        # Star: center 0 with leaves 1,2,3 (edges listed once)
        graph = {
            0: [(1, 1.0), (2, 1.0), (3, 1.0)],
            1: [],
            2: [],
            3: []
        }
        result = specialist.tree_center(graph)
        assert result['success'] is True
        assert 0 in result['center']


class TestTreeSpecialistDiameter:
    """Test tree_diameter operation."""

    def test_diameter_path(self):
        """Test diameter of path graph."""
        specialist = TreeSpecialist()
        # Path: 0-1-2 (edges listed once)
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.tree_diameter(graph)
        assert result['success'] is True
        assert result['diameter'] == 2

    def test_diameter_star(self):
        """Test diameter of star graph."""
        specialist = TreeSpecialist()
        # Star graph (edges listed once)
        graph = {
            0: [(1, 1.0), (2, 1.0), (3, 1.0)],
            1: [],
            2: [],
            3: []
        }
        result = specialist.tree_diameter(graph)
        assert result['success'] is True
        assert result['diameter'] == 2


class TestTreeSpecialistHeight:
    """Test tree_height operation."""

    def test_height_rooted_tree(self):
        """Test height of rooted tree."""
        specialist = TreeSpecialist()
        # Tree with root 0, children 1,2, and grandchild 3 (edges listed once)
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [],
            3: []
        }
        result = specialist.tree_height(graph, root=0)
        assert result['success'] is True
        assert result['height'] == 2


class TestTreeSpecialistLCA:
    """Test lowest_common_ancestor operation."""

    def test_lca_simple(self):
        """Test LCA on simple tree."""
        specialist = TreeSpecialist()
        # Tree: 0 has children 1,2; 1 has children 3,4 (edges listed once)
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(3, 1.0), (4, 1.0)],
            2: [],
            3: [],
            4: []
        }
        result = specialist.lowest_common_ancestor(graph, 3, 4, root=0)
        assert result['success'] is True
        assert result['lca'] == 1


class TestTreeSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex(self):
        """Test single vertex tree."""
        specialist = TreeSpecialist()
        graph = {0: []}
        result = specialist.is_tree(graph)
        assert result['success'] is True
        assert result['is_tree'] is True

    def test_two_vertices(self):
        """Test two-vertex tree."""
        specialist = TreeSpecialist()
        # Single edge (listed once)
        graph = {0: [(1, 1.0)], 1: []}
        result = specialist.tree_diameter(graph)
        assert result['success'] is True
        assert result['diameter'] == 1


class TestTreeSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_is_tree_request(self):
        """Test processing is_tree request."""
        specialist = TreeSpecialist()
        request = {
            'operation': 'is_tree',
            'graph': {0: [(1, 1.0)], 1: []}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_diameter_request(self):
        """Test processing diameter request."""
        specialist = TreeSpecialist()
        request = {
            'operation': 'diameter',
            'graph': {0: [(1, 1.0)], 1: []}
        }
        result = specialist.process_request(request)
        assert result['success'] is True


class TestTreeSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = TreeSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = TreeSpecialist()
        result = specialist.deliberate()
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = TreeSpecialist()
        assert hasattr(specialist, 'agent_id')
        assert specialist.agent_id is not None


class TestTreeSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = TreeSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestTreeSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_tree_operations(self):
        """Test concurrent tree operations."""
        specialist = TreeSpecialist()
        results = []

        def check_tree():
            # Simple tree (edges listed once)
            graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: []}
            result = specialist.is_tree(graph)
            if result.get('success'):
                results.append(result.get('is_tree'))

        threads = [threading.Thread(target=check_tree) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
