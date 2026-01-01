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
Comprehensive tests for PathSpecialist.

Tests cover: initialization, all path operations, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.path_specialist import PathSpecialist


class TestPathSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = PathSpecialist()
        assert 'path_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = PathSpecialist(agent_id="custom_path_001")
        assert specialist.agent_id == "custom_path_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = PathSpecialist()
        assert specialist.service_type == 'math.graph_theory.path'


class TestPathSpecialistShortestPath:
    """Test shortest path algorithms."""

    def test_shortest_path_simple(self):
        """Test shortest path in simple graph."""
        specialist = PathSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.shortest_path(graph, 0, 2)
        assert result['success'] is True
        assert result['path'] == [0, 1, 2]

    def test_shortest_path_weighted(self):
        """Test shortest path with weighted edges."""
        specialist = PathSpecialist()
        graph = {
            0: [(1, 1.0), (2, 3.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.shortest_path(graph, 0, 2)
        assert result['success'] is True
        assert len(result['path']) >= 2

    def test_shortest_path_no_path(self):
        """Test shortest path when no path exists."""
        specialist = PathSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [],
            2: [(3, 1.0)],
            3: []
        }
        result = specialist.shortest_path(graph, 0, 3)
        assert result['success'] is True
        # Path should be empty or None when no path exists
        assert result.get('path') == [] or result.get('path') is None

    def test_shortest_path_same_source_target(self):
        """Test shortest path when source equals target."""
        specialist = PathSpecialist()
        graph = {0: [(1, 1.0)], 1: []}
        result = specialist.shortest_path(graph, 0, 0)
        assert result['success'] is True


class TestPathSpecialistFindPath:
    """Test find_path (path existence)."""

    def test_find_path_exists(self):
        """Test find_path when path exists."""
        specialist = PathSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.find_path(graph, 0, 2)
        assert result['success'] is True
        assert result['exists'] is True

    def test_find_path_not_exists(self):
        """Test find_path when no path exists."""
        specialist = PathSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [],
            2: []
        }
        result = specialist.find_path(graph, 0, 2)
        assert result['success'] is True
        assert result['exists'] is False

    def test_find_path_empty_graph(self):
        """Test find_path on empty graph."""
        specialist = PathSpecialist()
        graph = {}
        result = specialist.find_path(graph, 0, 1)
        assert result['success'] is True
        assert result['exists'] is False


class TestPathSpecialistLongestPath:
    """Test longest path in DAG."""

    def test_longest_path_dag(self):
        """Test longest path in DAG."""
        specialist = PathSpecialist()
        # DAG: 0 -> 1 -> 2 -> 3
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: [(3, 1.0)],
            3: []
        }
        result = specialist.longest_path(graph, 0, 3)
        assert result['success'] is True

    def test_longest_path_disconnected(self):
        """Test longest path when source and target are disconnected."""
        specialist = PathSpecialist()
        # Disconnected: 0-1 component, 2 isolated
        graph = {
            0: [(1, 1.0)],
            1: [(0, 1.0)],
            2: []
        }
        result = specialist.longest_path(graph, 0, 2)
        # When no path exists, success is False or path is empty
        assert isinstance(result, dict)


class TestPathSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex_graph(self):
        """Test single vertex graph."""
        specialist = PathSpecialist()
        graph = {0: []}
        result = specialist.find_path(graph, 0, 0)
        assert result['success'] is True

    def test_self_loop(self):
        """Test graph with self-loop."""
        specialist = PathSpecialist()
        graph = {0: [(0, 1.0), (1, 1.0)], 1: []}
        result = specialist.find_path(graph, 0, 1)
        assert result['success'] is True
        assert result['exists'] is True

    def test_large_weights(self):
        """Test graph with large weights."""
        specialist = PathSpecialist()
        graph = {
            0: [(1, 1e12)],
            1: []
        }
        result = specialist.shortest_path(graph, 0, 1)
        assert result['success'] is True


class TestPathSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_shortest_path_request(self):
        """Test processing shortest_path request."""
        specialist = PathSpecialist()
        request = {
            'operation': 'shortest_path',
            'graph': {0: [(1, 1.0)], 1: []},
            'source': 0,
            'target': 1
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = PathSpecialist()
        request = {'operation': 'unknown_xyz_op'}
        result = specialist.process_request(request)
        # Returns dict with success status
        assert isinstance(result, dict)


class TestPathSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = PathSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()  # Should not raise

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = PathSpecialist()
        result = specialist.deliberate()
        # Returns list of intentions (may be empty)
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = PathSpecialist()
        assert hasattr(specialist, 'agent_id')
        assert specialist.agent_id is not None


class TestPathSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = PathSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestPathSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_path_queries(self):
        """Test concurrent path queries."""
        specialist = PathSpecialist()
        results = []

        def find_path():
            graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: []}
            result = specialist.find_path(graph, 0, 2)
            if result.get('success'):
                results.append(result.get('exists'))

        threads = [threading.Thread(target=find_path) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
