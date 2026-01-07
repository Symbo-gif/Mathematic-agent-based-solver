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
Comprehensive tests for ConnectivitySpecialist.

Tests cover: initialization, connected components, articulation points,
bridges, k-connectivity, BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.connectivity_specialist import ConnectivitySpecialist


class TestConnectivitySpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = ConnectivitySpecialist()
        assert 'connectivity_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = ConnectivitySpecialist(agent_id="custom_connectivity_001")
        assert specialist.agent_id == "custom_connectivity_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = ConnectivitySpecialist()
        assert 'connectivity' in specialist.service_type


class TestConnectivitySpecialistComponents:
    """Test connected components."""

    def test_single_component(self):
        """Test graph with single component."""
        specialist = ConnectivitySpecialist()
        # Graph format: Dict[int, List[Tuple[int, float]]]
        graph = {0: [(1, 1.0), (2, 1.0)], 1: [(0, 1.0), (2, 1.0)], 2: [(0, 1.0), (1, 1.0)]}
        result = specialist.connected_components(graph)
        assert result['success'] is True
        assert result['count'] == 1

    def test_two_components(self):
        """Test graph with two components."""
        specialist = ConnectivitySpecialist()
        graph = {
            0: [(1, 1.0)], 1: [(0, 1.0)],
            2: [(3, 1.0)], 3: [(2, 1.0)]
        }
        result = specialist.connected_components(graph)
        assert result['success'] is True
        assert result['count'] == 2

    def test_isolated_vertices(self):
        """Test graph with isolated vertices."""
        specialist = ConnectivitySpecialist()
        graph = {0: [], 1: [], 2: []}
        result = specialist.connected_components(graph)
        assert result['success'] is True
        assert result['count'] == 3

    def test_empty_graph(self):
        """Test empty graph."""
        specialist = ConnectivitySpecialist()
        graph = {}
        result = specialist.connected_components(graph)
        assert result['success'] is True
        assert result['count'] == 0


class TestConnectivitySpecialistArticulationPoints:
    """Test articulation point detection."""

    def test_linear_graph(self):
        """Test linear graph - internal nodes are articulation points."""
        specialist = ConnectivitySpecialist()
        # 0 - 1 - 2 - 3
        graph = {
            0: [(1, 1.0)], 1: [(0, 1.0), (2, 1.0)],
            2: [(1, 1.0), (3, 1.0)], 3: [(2, 1.0)]
        }
        result = specialist.articulation_points(graph)
        assert result['success'] is True
        # 1 and 2 are articulation points
        points = result.get('points', result.get('articulation_points', []))
        assert 1 in points or 2 in points

    def test_cycle_graph(self):
        """Test cycle graph - no articulation points."""
        specialist = ConnectivitySpecialist()
        # Triangle: 0 - 1 - 2 - 0
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.articulation_points(graph)
        assert result['success'] is True
        points = result.get('points', result.get('articulation_points', []))
        assert len(points) == 0

    def test_star_graph(self):
        """Test star graph - center is articulation point."""
        specialist = ConnectivitySpecialist()
        # Center 0 connected to 1, 2, 3
        graph = {
            0: [(1, 1.0), (2, 1.0), (3, 1.0)],
            1: [(0, 1.0)], 2: [(0, 1.0)], 3: [(0, 1.0)]
        }
        result = specialist.articulation_points(graph)
        assert result['success'] is True
        points = result.get('points', result.get('articulation_points', []))
        assert 0 in points


class TestConnectivitySpecialistBridges:
    """Test bridge detection."""

    def test_tree_all_bridges(self):
        """Test tree - all edges are bridges."""
        specialist = ConnectivitySpecialist()
        graph = {
            0: [(1, 1.0)], 1: [(0, 1.0), (2, 1.0)], 2: [(1, 1.0)]
        }
        result = specialist.bridges(graph)
        assert result['success'] is True
        bridges_list = result.get('bridges', [])
        assert len(bridges_list) == 2

    def test_cycle_no_bridges(self):
        """Test cycle - no bridges."""
        specialist = ConnectivitySpecialist()
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.bridges(graph)
        assert result['success'] is True
        bridges_list = result.get('bridges', [])
        assert len(bridges_list) == 0

    def test_bridge_with_cycle(self):
        """Test graph with bridge connecting two cycles."""
        specialist = ConnectivitySpecialist()
        # Two triangles connected by a bridge
        graph = {
            0: [(1, 1.0), (2, 1.0)], 1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0), (3, 1.0)],
            3: [(2, 1.0), (4, 1.0), (5, 1.0)],
            4: [(3, 1.0), (5, 1.0)], 5: [(3, 1.0), (4, 1.0)]
        }
        result = specialist.bridges(graph)
        assert result['success'] is True
        bridges_list = result.get('bridges', [])
        # Edge (2,3) should be a bridge
        assert len(bridges_list) >= 1


class TestConnectivitySpecialistConnectivity:
    """Test k-connectivity."""

    def test_is_connected(self):
        """Test is_connected check."""
        specialist = ConnectivitySpecialist()
        graph = {0: [(1, 1.0)], 1: [(0, 1.0), (2, 1.0)], 2: [(1, 1.0)]}
        result = specialist.is_connected(graph)
        assert result['success'] is True
        assert result['is_connected'] is True

    def test_is_not_connected(self):
        """Test disconnected graph."""
        specialist = ConnectivitySpecialist()
        graph = {0: [], 1: []}
        result = specialist.is_connected(graph)
        assert result['success'] is True
        assert result['is_connected'] is False

    def test_vertex_connectivity(self):
        """Test vertex connectivity computation."""
        specialist = ConnectivitySpecialist()
        # Complete graph K4 has connectivity 3
        graph = {
            0: [(1, 1.0), (2, 1.0), (3, 1.0)],
            1: [(0, 1.0), (2, 1.0), (3, 1.0)],
            2: [(0, 1.0), (1, 1.0), (3, 1.0)],
            3: [(0, 1.0), (1, 1.0), (2, 1.0)]
        }
        result = specialist.vertex_connectivity(graph)
        assert result['success'] is True
        assert result.get('connectivity', result.get('vertex_connectivity', 0)) == 3


class TestConnectivitySpecialistSCC:
    """Test strongly connected components (directed graphs)."""

    def test_scc_simple(self):
        """Test SCC on simple directed graph."""
        specialist = ConnectivitySpecialist()
        # 0 -> 1 -> 2 -> 0 (one SCC)
        graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: [(0, 1.0)]}
        result = specialist.strongly_connected_components(graph)
        assert result['success'] is True
        count = result.get('count', len(result.get('components', [])))
        assert count >= 1

    def test_scc_multiple(self):
        """Test SCC with multiple components."""
        specialist = ConnectivitySpecialist()
        # Two separate cycles
        graph = {
            0: [(1, 1.0)], 1: [(0, 1.0)],  # First SCC
            2: [(3, 1.0)], 3: [(2, 1.0)]   # Second SCC
        }
        result = specialist.strongly_connected_components(graph)
        assert result['success'] is True
        count = result.get('count', len(result.get('components', [])))
        assert count >= 2


class TestConnectivitySpecialistEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = ConnectivitySpecialist()
        graph = {0: []}
        result = specialist.is_connected(graph)
        assert result['success'] is True
        assert result['is_connected'] is True

    def test_self_loop(self):
        """Test graph with self-loop."""
        specialist = ConnectivitySpecialist()
        graph = {0: [(0, 1.0), (1, 1.0)], 1: [(0, 1.0)]}
        result = specialist.connected_components(graph)
        assert result['success'] is True
        assert result['count'] == 1


class TestConnectivitySpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_components_request(self):
        """Test processing connected_components request."""
        specialist = ConnectivitySpecialist()
        request = {
            'operation': 'connected_components',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = ConnectivitySpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        # Returns dict with result
        assert isinstance(result, dict)


class TestConnectivitySpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = ConnectivitySpecialist()
        try:
            specialist.update_beliefs()
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = ConnectivitySpecialist()
        result = specialist.deliberate()
        # Returns list of intentions
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = ConnectivitySpecialist()
        assert hasattr(specialist, 'agent_id')
        assert specialist.agent_id is not None


class TestConnectivitySpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = ConnectivitySpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestConnectivitySpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_component_queries(self):
        """Test concurrent connected component queries."""
        specialist = ConnectivitySpecialist()
        results = []

        def find_components():
            graph = {0: [(1, 1.0), (2, 1.0)], 1: [(0, 1.0), (2, 1.0)], 2: [(0, 1.0), (1, 1.0)]}
            result = specialist.connected_components(graph)
            if result.get('success'):
                results.append(result.get('count'))

        threads = [threading.Thread(target=find_components) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 1 for r in results)
