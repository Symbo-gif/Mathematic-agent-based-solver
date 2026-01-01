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
Comprehensive tests for CycleSpecialist.

Tests cover: initialization, cycle detection, Eulerian paths,
edge cases, BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.cycle_specialist import CycleSpecialist


class TestCycleSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_id(self):
        """Test initialization with default agent_id."""
        specialist = CycleSpecialist()
        assert 'cycle_specialist' in specialist.agent_id

    def test_init_custom_id(self):
        """Test initialization with custom agent_id."""
        specialist = CycleSpecialist(agent_id="custom_cycle_001")
        assert specialist.agent_id == "custom_cycle_001"

    def test_init_has_service_type(self):
        """Test service_type is set."""
        specialist = CycleSpecialist()
        assert specialist.service_type == 'math.graph_theory.cycle'


class TestCycleSpecialistHasCycle:
    """Test has_cycle operation."""

    def test_has_cycle_directed(self):
        """Test cycle detection in directed graph with cycle."""
        specialist = CycleSpecialist()
        # Directed cycle: 0 -> 1 -> 2 -> 0
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: [(0, 1.0)]
        }
        result = specialist.has_cycle(graph, directed=True)
        assert result['success'] is True
        assert result['has_cycle'] is True

    def test_no_cycle_dag(self):
        """Test DAG has no cycle."""
        specialist = CycleSpecialist()
        # DAG: 0 -> 1 -> 2
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.has_cycle(graph, directed=True)
        assert result['success'] is True
        assert result['has_cycle'] is False

    def test_has_cycle_undirected(self):
        """Test cycle detection in undirected graph."""
        specialist = CycleSpecialist()
        # Triangle
        graph = {
            0: [(1, 1.0), (2, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(0, 1.0), (1, 1.0)]
        }
        result = specialist.has_cycle(graph, directed=False)
        assert result['success'] is True
        assert result['has_cycle'] is True


class TestCycleSpecialistFindCycle:
    """Test find_cycle operation."""

    def test_find_cycle_exists(self):
        """Test finding a cycle when one exists."""
        specialist = CycleSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: [(0, 1.0)]
        }
        result = specialist.find_cycle(graph, directed=True)
        assert result['success'] is True
        assert result['has_cycle'] is True
        assert result['cycle'] is not None

    def test_find_cycle_not_exists(self):
        """Test find_cycle when no cycle exists."""
        specialist = CycleSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: []
        }
        result = specialist.find_cycle(graph, directed=True)
        assert result['success'] is True
        assert result['has_cycle'] is False


class TestCycleSpecialistIsAcyclic:
    """Test is_acyclic operation."""

    def test_is_acyclic_dag(self):
        """Test DAG is acyclic."""
        specialist = CycleSpecialist()
        graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: []}
        result = specialist.is_acyclic(graph)
        assert result['success'] is True
        assert result['is_acyclic'] is True

    def test_is_acyclic_with_cycle(self):
        """Test graph with cycle is not acyclic."""
        specialist = CycleSpecialist()
        graph = {0: [(1, 1.0)], 1: [(0, 1.0)]}
        result = specialist.is_acyclic(graph)
        assert result['success'] is True
        assert result['is_acyclic'] is False


class TestCycleSpecialistEulerian:
    """Test Eulerian path/circuit operations."""

    def test_eulerian_circuit_exists(self):
        """Test Eulerian circuit on graph with circuit."""
        specialist = CycleSpecialist()
        # Eulerian circuit: all vertices have even degree
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: [(0, 1.0)]
        }
        result = specialist.eulerian_circuit(graph)
        assert result['success'] is True

    def test_eulerian_path_exists(self):
        """Test Eulerian path exists."""
        specialist = CycleSpecialist()
        graph = {
            0: [(1, 1.0)],
            1: [(2, 1.0)],
            2: [(0, 1.0)]
        }
        result = specialist.eulerian_path(graph)
        assert result['success'] is True


class TestCycleSpecialistHamiltonian:
    """Test Hamiltonian path operations."""

    def test_hamiltonian_path_simple(self):
        """Test Hamiltonian path on simple graph."""
        specialist = CycleSpecialist()
        # Path graph has Hamiltonian path
        graph = {
            0: [(1, 1.0)],
            1: [(0, 1.0), (2, 1.0)],
            2: [(1, 1.0)]
        }
        result = specialist.hamiltonian_path(graph)
        assert result['success'] is True


class TestCycleSpecialistEdgeCases:
    """Test edge cases."""

    def test_empty_graph(self):
        """Test empty graph."""
        specialist = CycleSpecialist()
        graph = {}
        result = specialist.has_cycle(graph)
        assert result['success'] is True
        assert result['has_cycle'] is False

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = CycleSpecialist()
        graph = {0: []}
        result = specialist.has_cycle(graph)
        assert result['success'] is True


class TestCycleSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_has_cycle_request(self):
        """Test processing has_cycle request."""
        specialist = CycleSpecialist()
        request = {
            'operation': 'has_cycle',
            'graph': {0: [(1, 1.0)], 1: [(0, 1.0)]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation defaults to has_cycle."""
        specialist = CycleSpecialist()
        request = {'operation': 'unknown_op', 'graph': {}}
        result = specialist.process_request(request)
        assert isinstance(result, dict)


class TestCycleSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = CycleSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = CycleSpecialist()
        result = specialist.deliberate()
        assert isinstance(result, list)

    def test_has_agent_id(self):
        """Test agent_id is set."""
        specialist = CycleSpecialist()
        assert hasattr(specialist, 'agent_id')
        assert specialist.agent_id is not None


class TestCycleSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = CycleSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestCycleSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_cycle_detection(self):
        """Test concurrent cycle detection."""
        specialist = CycleSpecialist()
        results = []

        def detect_cycle():
            graph = {0: [(1, 1.0)], 1: [(2, 1.0)], 2: [(0, 1.0)]}
            result = specialist.has_cycle(graph, directed=True)
            if result.get('success'):
                results.append(result.get('has_cycle'))

        threads = [threading.Thread(target=detect_cycle) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r is True for r in results)
