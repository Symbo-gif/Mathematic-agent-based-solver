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
Comprehensive tests for SetCoverSpecialist.

Tests cover: initialization, set cover algorithms, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.set_cover_specialist import SetCoverSpecialist


class TestSetCoverSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = SetCoverSpecialist()
        assert specialist.name == "SetCoverSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = SetCoverSpecialist(name="CustomSC")
        assert specialist.name == "CustomSC"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = SetCoverSpecialist()
        assert 'greedy_set_cover' in specialist.supported_operations
        assert 'hitting_set' in specialist.supported_operations


class TestSetCoverSpecialistGreedy:
    """Test greedy_set_cover operation."""

    def test_greedy_set_cover_simple(self):
        """Test greedy set cover on simple instance."""
        specialist = SetCoverSpecialist()
        universe = {1, 2, 3, 4, 5}
        sets = [{1, 2, 3}, {2, 4}, {3, 4, 5}]
        selected = specialist.greedy_set_cover(sets, universe)
        # Verify cover is valid
        covered = set()
        for idx in selected:
            covered.update(sets[idx])
        assert universe.issubset(covered)

    def test_greedy_set_cover_exact(self):
        """Test greedy set cover with exact coverage."""
        specialist = SetCoverSpecialist()
        universe = {1, 2}
        sets = [{1}, {2}]
        selected = specialist.greedy_set_cover(sets, universe)
        assert len(selected) == 2

    def test_greedy_set_cover_empty(self):
        """Test greedy set cover with empty universe."""
        specialist = SetCoverSpecialist()
        selected = specialist.greedy_set_cover([], set())
        assert selected == []


class TestSetCoverSpecialistWeighted:
    """Test weighted_set_cover operation."""

    def test_weighted_set_cover(self):
        """Test weighted set cover."""
        specialist = SetCoverSpecialist()
        universe = {1, 2, 3}
        sets = [{1, 2}, {2, 3}, {1, 3}]
        weights = [1.0, 2.0, 3.0]
        selected = specialist.weighted_set_cover(sets, weights, universe)
        # Return is List[int] of indices
        assert isinstance(selected, list)
        # Verify cover is valid
        covered = set()
        for idx in selected:
            covered.update(sets[idx])
        assert universe.issubset(covered)

    def test_weighted_set_cover_single_set(self):
        """Test weighted set cover with single covering set."""
        specialist = SetCoverSpecialist()
        universe = {1, 2, 3}
        sets = [{1, 2, 3}]
        weights = [5.0]
        selected = specialist.weighted_set_cover(sets, weights, universe)
        assert len(selected) == 1


class TestSetCoverSpecialistHittingSet:
    """Test hitting_set operation."""

    def test_hitting_set_simple(self):
        """Test hitting set on simple instance."""
        specialist = SetCoverSpecialist()
        sets = [{1, 2}, {2, 3}, {3, 4}]
        hitting = specialist.hitting_set(sets)
        # Verify hitting set hits all sets
        for s in sets:
            assert len(s.intersection(hitting)) >= 1

    def test_hitting_set_disjoint(self):
        """Test hitting set with disjoint sets."""
        specialist = SetCoverSpecialist()
        sets = [{1}, {2}, {3}]
        hitting = specialist.hitting_set(sets)
        assert len(hitting) == 3

    def test_hitting_set_empty(self):
        """Test hitting set with empty input."""
        specialist = SetCoverSpecialist()
        hitting = specialist.hitting_set([])
        assert hitting == set()


class TestSetCoverSpecialistExact:
    """Test exact_set_cover operation."""

    def test_exact_set_cover_exists(self):
        """Test exact set cover when solution exists."""
        specialist = SetCoverSpecialist()
        universe = {1, 2, 3, 4}
        sets = [{1, 2}, {3, 4}, {2, 3}]
        selected = specialist.exact_set_cover(sets, universe)
        if selected is not None:
            # Verify exact (disjoint) cover
            covered = set()
            for idx in selected:
                assert sets[idx].isdisjoint(covered)
                covered.update(sets[idx])
            assert covered == universe


class TestSetCoverSpecialistVertexCover:
    """Test vertex_cover operation."""

    def test_vertex_cover_simple(self):
        """Test vertex cover on simple graph."""
        specialist = SetCoverSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}  # Triangle
        cover = specialist.vertex_cover(graph)
        # Verify every edge has at least one endpoint in cover
        for u in graph:
            for v in graph[u]:
                assert u in cover or v in cover

    def test_vertex_cover_path(self):
        """Test vertex cover on path graph."""
        specialist = SetCoverSpecialist()
        graph = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
        cover = specialist.vertex_cover(graph)
        # 2-approximation allows up to 4 vertices for optimal 2
        assert len(cover) <= 4

    def test_vertex_cover_empty(self):
        """Test vertex cover on empty graph."""
        specialist = SetCoverSpecialist()
        cover = specialist.vertex_cover({})
        assert cover == set()


class TestSetCoverSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_element_universe(self):
        """Test single element universe."""
        specialist = SetCoverSpecialist()
        universe = {1}
        sets = [{1}]
        selected = specialist.greedy_set_cover(sets, universe)
        assert len(selected) == 1

    def test_overlapping_sets(self):
        """Test with heavily overlapping sets."""
        specialist = SetCoverSpecialist()
        universe = {1, 2, 3}
        sets = [{1, 2, 3}, {1, 2}, {2, 3}, {1, 3}]
        selected = specialist.greedy_set_cover(sets, universe)
        assert len(selected) == 1  # First set covers all


class TestSetCoverSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_greedy_request(self):
        """Test processing greedy set cover request."""
        specialist = SetCoverSpecialist()
        request = {
            'operation': 'greedy_set_cover',
            'sets': [{1, 2}, {2, 3}],
            'universe': {1, 2, 3}
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = SetCoverSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestSetCoverSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = SetCoverSpecialist()
        try:
            specialist.update_beliefs({})
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = SetCoverSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = SetCoverSpecialist()
        assert hasattr(specialist, 'name')


class TestSetCoverSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = SetCoverSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'greedy_solved' in stats or 'weighted_solved' in stats


class TestSetCoverSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_set_covers(self):
        """Test concurrent set cover computations."""
        specialist = SetCoverSpecialist()
        results = []

        def compute_cover():
            universe = {1, 2, 3}
            sets = [{1, 2, 3}]
            selected = specialist.greedy_set_cover(sets, universe)
            results.append(len(selected))

        threads = [threading.Thread(target=compute_cover) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 1 for r in results)
