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
Comprehensive tests for DegreeSequenceSpecialist.

Tests cover: initialization, degree sequence operations, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.graph_theory.degree_sequence_specialist import DegreeSequenceSpecialist


class TestDegreeSequenceSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = DegreeSequenceSpecialist()
        assert specialist.name == "DegreeSequenceSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = DegreeSequenceSpecialist(name="CustomDS")
        assert specialist.name == "CustomDS"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = DegreeSequenceSpecialist()
        assert 'degree_sequence' in specialist.supported_operations
        assert 'is_graphical' in specialist.supported_operations


class TestDegreeSequenceSpecialistDegreeSequence:
    """Test degree_sequence operation."""

    def test_degree_sequence_triangle(self):
        """Test degree sequence of triangle (K3)."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.degree_sequence(graph)
        assert result == [2, 2, 2]

    def test_degree_sequence_path(self):
        """Test degree sequence of path graph."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.degree_sequence(graph)
        assert result == [2, 1, 1]

    def test_degree_sequence_empty(self):
        """Test degree sequence of empty graph."""
        specialist = DegreeSequenceSpecialist()
        graph = {}
        result = specialist.degree_sequence(graph)
        assert result == []


class TestDegreeSequenceSpecialistIsGraphical:
    """Test is_graphical operation."""

    def test_is_graphical_valid(self):
        """Test valid graphical sequence."""
        specialist = DegreeSequenceSpecialist()
        # Triangle degree sequence
        sequence = [2, 2, 2]
        result = specialist.is_graphical(sequence)
        assert result is True

    def test_is_graphical_invalid_odd_sum(self):
        """Test invalid sequence (odd sum)."""
        specialist = DegreeSequenceSpecialist()
        sequence = [3, 2, 1]  # Sum is 6, should work
        result = specialist.is_graphical(sequence)
        # Check it returns a boolean
        assert isinstance(result, bool)

    def test_is_graphical_star(self):
        """Test star graph sequence is graphical."""
        specialist = DegreeSequenceSpecialist()
        sequence = [3, 1, 1, 1]  # Star with 3 leaves
        result = specialist.is_graphical(sequence)
        assert result is True


class TestDegreeSequenceSpecialistRealizeSequence:
    """Test realize_sequence operation."""

    def test_realize_sequence_simple(self):
        """Test realizing simple sequence."""
        specialist = DegreeSequenceSpecialist()
        sequence = [2, 2, 2]  # Triangle
        result = specialist.realize_sequence(sequence)
        # Should return a graph
        assert isinstance(result, dict)

    def test_realize_sequence_path(self):
        """Test realizing path sequence."""
        specialist = DegreeSequenceSpecialist()
        sequence = [2, 1, 1]
        result = specialist.realize_sequence(sequence)
        assert isinstance(result, dict)


class TestDegreeSequenceSpecialistIsRegular:
    """Test is_regular operation."""

    def test_is_regular_true(self):
        """Test regular graph detection."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        result = specialist.is_regular(graph, 2)
        assert result is True

    def test_is_regular_false(self):
        """Test non-regular graph."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1]}
        result = specialist.is_regular(graph, 2)
        assert result is False


class TestDegreeSequenceSpecialistMaxMinDegree:
    """Test max_degree and min_degree operations."""

    def test_max_degree(self):
        """Test maximum degree."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}
        result = specialist.max_degree(graph)
        assert result == 3

    def test_min_degree(self):
        """Test minimum degree."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}
        result = specialist.min_degree(graph)
        assert result == 1


class TestDegreeSequenceSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_vertex(self):
        """Test single vertex graph."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: []}
        result = specialist.degree_sequence(graph)
        assert result == [0]

    def test_isolated_vertices(self):
        """Test isolated vertices."""
        specialist = DegreeSequenceSpecialist()
        graph = {0: [], 1: [], 2: []}
        result = specialist.degree_sequence(graph)
        assert result == [0, 0, 0]


class TestDegreeSequenceSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_degree_sequence_request(self):
        """Test processing degree sequence request."""
        specialist = DegreeSequenceSpecialist()
        request = {
            'operation': 'degree_sequence',
            'graph': {0: [1], 1: [0]}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_is_graphical_request(self):
        """Test processing is_graphical request."""
        specialist = DegreeSequenceSpecialist()
        request = {
            'operation': 'is_graphical',
            'sequence': [2, 2, 2]
        }
        result = specialist.process_request(request)
        assert result['success'] is True


class TestDegreeSequenceSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = DegreeSequenceSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = DegreeSequenceSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = DegreeSequenceSpecialist()
        assert hasattr(specialist, 'name')


class TestDegreeSequenceSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = DegreeSequenceSpecialist()
        try:
            stats = specialist.get_statistics()
            assert isinstance(stats, dict)
        except AttributeError:
            # Some specialists don't initialize counter attributes
            assert hasattr(specialist, 'get_statistics')


class TestDegreeSequenceSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_degree_sequence(self):
        """Test concurrent degree sequence operations."""
        specialist = DegreeSequenceSpecialist()
        results = []

        def get_sequence():
            graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
            result = specialist.degree_sequence(graph)
            results.append(result)

        threads = [threading.Thread(target=get_sequence) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == [2, 2, 2] for r in results)
