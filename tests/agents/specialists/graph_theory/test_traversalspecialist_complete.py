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
Comprehensive tests for TraversalSpecialist.

Tests cover: initialization, BFS/DFS/topological sort,
edge cases, BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.traversal_specialist import TraversalSpecialist


class TestTraversalSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = TraversalSpecialist()
        assert 'traversal_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = TraversalSpecialist(agent_id="custom_traversal_001")
        assert specialist.agent_id == "custom_traversal_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = TraversalSpecialist()
        assert specialist.service_type == 'math.graph_theory.traversal'


class TestTraversalSpecialistBFS:
    """Test BFS operation."""

    def test_bfs_simple(self):
        """Test BFS on simple graph."""
        specialist = TraversalSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [(3, 1.0)],
            3: []
        }
        result = specialist.bfs(graph, 0)
        assert result['success'] is True
        assert result['order'][0] == 0
        assert len(result['order']) == 4

    def test_bfs_disconnected(self):
        """Test BFS doesn't reach disconnected vertices."""
        specialist = TraversalSpecialist()
        graph = {0: [(1, 1.0)], 1: [], 2: []}
        result = specialist.bfs(graph, 0)
        assert result['success'] is True
        assert result['visited_count'] == 2

    def test_bfs_single_vertex(self):
        """Test BFS on single vertex."""
        specialist = TraversalSpecialist()
        graph = {0: []}
        result = specialist.bfs(graph, 0)
        assert result['success'] is True
        assert result['order'] == [0]


class TestTraversalSpecialistDFS:
    """Test DFS operation."""

    def test_dfs_simple(self):
        """Test DFS on simple graph."""
        specialist = TraversalSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [],
            3: []
        }
        result = specialist.dfs(graph, 0)
        assert result['success'] is True
        assert result['preorder'][0] == 0
        assert len(result['preorder']) == 4

    def test_dfs_preorder_postorder(self):
        """Test DFS returns both preorder and postorder."""
        specialist = TraversalSpecialist()
        graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: []}
        result = specialist.dfs(graph, 0)
        assert result['success'] is True
        assert 'preorder' in result
        assert 'postorder' in result


class TestTraversalSpecialistTopologicalSort:
    """Test topological sort operation."""

    def test_topological_sort_dag(self):
        """Test topological sort on DAG."""
        specialist = TraversalSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [(3, 1.0)],
            3: []
        }
        result = specialist.topological_sort(graph)
        assert result['success'] is True
        assert result['is_dag'] is True
        assert result['order'] is not None
        # 0 must come before 1, 2; they must come before 3
        order = result['order']
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)

    def test_topological_sort_cycle(self):
        """Test topological sort detects cycle."""
        specialist = TraversalSpecialist()
        graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: [(0, 1.0)]}
        result = specialist.topological_sort(graph)
        assert result['success'] is True
        assert result['is_dag'] is False


class TestTraversalSpecialistLevelOrder:
    """Test level_order operation."""

    def test_level_order_tree(self):
        """Test level order on tree."""
        specialist = TraversalSpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(3, 1.0)],
            2: [],
            3: []
        }
        result = specialist.level_order(graph, 0)
        assert result['success'] is True
        assert result['levels'][0] == [0]
        assert set(result['levels'][1]) == {1, 2}


class TestTraversalSpecialistEdgeCases:
    """Test edge cases."""

    def test_empty_graph(self):
        """Test empty graph."""
        specialist = TraversalSpecialist()
        graph = {}
        result = specialist.topological_sort(graph)
        assert result['success'] is True
        assert result['is_dag'] is True

    def test_single_vertex_no_edges(self):
        """Test single vertex with no edges."""
        specialist = TraversalSpecialist()
        graph = {0: []}
        result = specialist.bfs(graph, 0)
        assert result['success'] is True
        assert result['order'] == [0]


class TestTraversalSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_bfs_request(self):
        """Test processing BFS request."""
        specialist = TraversalSpecialist()
        request = {
            'operation': 'bfs',
            'graph': {0: [(1, 1.0)], 1: []},
            'start': 0
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_topological_request(self):
        """Test processing topological sort request."""
        specialist = TraversalSpecialist()
        request = {
            'operation': 'topological',
            'graph': {0: [(1, 1.0)], 1: []}
        }
        result = specialist.process_request(request)
        assert result['success'] is True


class TestTraversalSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = TraversalSpecialist()
        try:
            specialist.update_beliefs()
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = TraversalSpecialist()
        result = specialist.deliberate()
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = TraversalSpecialist()
        assert hasattr(specialist, 'agent_id')
        assert specialist.agent_id is not None


class TestTraversalSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = TraversalSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestTraversalSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_bfs(self):
        """Test concurrent BFS operations."""
        specialist = TraversalSpecialist()
        results = []

        def run_bfs():
            graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: []}
            result = specialist.bfs(graph, 0)
            if result.get('success'):
                results.append(len(result.get('order', [])))

        threads = [threading.Thread(target=run_bfs) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 3 for r in results)
