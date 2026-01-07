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
Comprehensive tests for ILPFormulationSpecialist.

Tests cover: initialization, ILP formulations, edge cases,
BDI interface, and concurrent access.
"""

import pytest
import threading

from symbo_agentic_reasoners.agents.specialists.discrete_optimization.ilp_formulation_specialist import ILPFormulationSpecialist


class TestILPFormulationSpecialistInit:
    """Test initialization and setup."""

    def test_init_default_name(self):
        """Test initialization with default name."""
        specialist = ILPFormulationSpecialist()
        assert specialist.name == "ILPFormulationSpecialist"

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        specialist = ILPFormulationSpecialist(name="CustomILP")
        assert specialist.name == "CustomILP"

    def test_supported_operations(self):
        """Test supported operations list."""
        specialist = ILPFormulationSpecialist()
        assert 'formulate_knapsack' in specialist.supported_operations
        assert 'formulate_tsp' in specialist.supported_operations


class TestILPFormulationSpecialistKnapsack:
    """Test formulate_knapsack operation."""

    def test_formulate_knapsack(self):
        """Test knapsack formulation."""
        specialist = ILPFormulationSpecialist()
        items = [(60, 10), (100, 20), (120, 30)]
        capacity = 50
        ilp = specialist.formulate_knapsack(items, capacity)
        assert ilp['type'] == 'knapsack'
        assert ilp['variables'] == 3
        assert len(ilp['binary_indices']) == 3

    def test_formulate_knapsack_empty(self):
        """Test knapsack formulation with empty items."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_knapsack([], 100)
        assert ilp['variables'] == 0


class TestILPFormulationSpecialistTSP:
    """Test formulate_tsp operation."""

    def test_formulate_tsp(self):
        """Test TSP formulation."""
        specialist = ILPFormulationSpecialist()
        distances = [
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ]
        ilp = specialist.formulate_tsp(distances)
        assert ilp['type'] == 'TSP'
        assert ilp['variables'] > 0
        assert len(ilp['binary_indices']) > 0

    def test_formulate_tsp_empty(self):
        """Test TSP formulation with empty matrix."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_tsp([])
        assert ilp['variables'] == 0


class TestILPFormulationSpecialistVertexCover:
    """Test formulate_vertex_cover operation."""

    def test_formulate_vertex_cover(self):
        """Test vertex cover formulation."""
        specialist = ILPFormulationSpecialist()
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        ilp = specialist.formulate_vertex_cover(graph)
        assert ilp['type'] == 'vertex_cover'
        assert ilp['variables'] == 3

    def test_formulate_vertex_cover_empty(self):
        """Test vertex cover formulation with empty graph."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_vertex_cover({})
        assert ilp['variables'] == 0


class TestILPFormulationSpecialistSetCover:
    """Test formulate_set_cover operation."""

    def test_formulate_set_cover(self):
        """Test set cover formulation."""
        specialist = ILPFormulationSpecialist()
        sets = [{1, 2}, {2, 3}, {1, 3}]
        universe = {1, 2, 3}
        ilp = specialist.formulate_set_cover(sets, universe)
        assert ilp['type'] == 'set_cover'
        assert ilp['variables'] == 3


class TestILPFormulationSpecialistRelaxation:
    """Test lp_relaxation operation."""

    def test_lp_relaxation(self):
        """Test LP relaxation."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_knapsack([(10, 5)], 10)
        lp = specialist.lp_relaxation(ilp)
        assert lp['binary_indices'] == []
        assert 'relaxation' in lp['type']


class TestILPFormulationSpecialistValidation:
    """Test validate_formulation operation."""

    def test_validate_formulation_valid(self):
        """Test valid formulation."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_knapsack([(10, 5)], 10)
        result = specialist.validate_formulation(ilp)
        assert result['valid'] is True

    def test_validate_formulation_invalid(self):
        """Test invalid formulation."""
        specialist = ILPFormulationSpecialist()
        ilp = {'variables': 2, 'objective': [1], 'constraints_A': [], 'constraints_b': [], 'binary_indices': []}
        result = specialist.validate_formulation(ilp)
        assert result['valid'] is False


class TestILPFormulationSpecialistEdgeCases:
    """Test edge cases."""

    def test_single_item_knapsack(self):
        """Test single item knapsack."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_knapsack([(10, 5)], 10)
        assert ilp['variables'] == 1

    def test_single_set_cover(self):
        """Test single set cover."""
        specialist = ILPFormulationSpecialist()
        ilp = specialist.formulate_set_cover([{1, 2}], {1, 2})
        assert ilp['variables'] == 1


class TestILPFormulationSpecialistRequestProcessing:
    """Test request processing interface."""

    def test_process_knapsack_request(self):
        """Test processing knapsack formulation request."""
        specialist = ILPFormulationSpecialist()
        request = {
            'operation': 'formulate_knapsack',
            'items': [(10, 5)],
            'capacity': 10
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        specialist = ILPFormulationSpecialist()
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False


class TestILPFormulationSpecialistBDI:
    """Test BDI interface."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard."""
        specialist = ILPFormulationSpecialist()
        try:
            specialist.update_beliefs()
        except TypeError:
            # Some specialists don't accept arguments
            specialist.update_beliefs()

    def test_deliberate_no_pending(self):
        """Test deliberate with no pending tasks."""
        specialist = ILPFormulationSpecialist()
        result = specialist.deliberate()
        assert result is None

    def test_has_name(self):
        """Test name is set."""
        specialist = ILPFormulationSpecialist()
        assert hasattr(specialist, 'name')


class TestILPFormulationSpecialistStatistics:
    """Test statistics functionality."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        specialist = ILPFormulationSpecialist()
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
        assert 'formulations' in stats


class TestILPFormulationSpecialistConcurrency:
    """Test thread safety."""

    def test_concurrent_formulations(self):
        """Test concurrent ILP formulations."""
        specialist = ILPFormulationSpecialist()
        results = []

        def formulate():
            items = [(10, 5), (20, 10)]
            ilp = specialist.formulate_knapsack(items, 15)
            results.append(ilp['variables'])

        threads = [threading.Thread(target=formulate) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(r == 2 for r in results)
