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
COUPLING MIXING SPECIALIST TESTS
=================================

Comprehensive test suite for CouplingMixingSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.coupling_mixing_specialist import (
    CouplingMixingSpecialist
)


class TestCouplingMixingSpecialistComplete:
    """Comprehensive tests for CouplingMixingSpecialist."""

    @pytest.fixture
    def specialist(self):
        return CouplingMixingSpecialist(agent_id='test_coupling_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def ergodic_chain(self):
        return [[0.7, 0.3], [0.4, 0.6]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_coupling_001'
        assert specialist.service_type == 'math.probability.discrete.mixing'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'total_variation_distance', 'mu': [0.5, 0.5], 'nu': [0.7, 0.3]}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test total variation distance."""
        request = {'operation': 'total_variation_distance', 'mu': [0.5, 0.5], 'nu': [0.7, 0.3]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 0 <= result['tv_distance'] <= 1

    def test_complex_problem_solving(self, specialist, ergodic_chain):
        """Test mixing time estimation."""
        request = {'operation': 'mixing_time', 'P': ergodic_chain, 'epsilon': 0.01}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 'mixing_time' in result

    def test_invalid_input_handling(self, specialist):
        # Invalid distributions (don't sum to 1)
        request = {'operation': 'total_variation_distance', 'mu': [0.3, 0.3], 'nu': [0.5, 0.5]}
        result = specialist.process_request(request)
        # Should handle gracefully

    def test_edge_cases(self, specialist):
        # Identical distributions (TV = 0)
        request = {'operation': 'total_variation_distance', 'mu': [0.5, 0.5], 'nu': [0.5, 0.5]}
        result = specialist.process_request(request)
        assert abs(result['tv_distance']) < 1e-10

        # Disjoint distributions (TV = 1)
        request = {'operation': 'total_variation_distance', 'mu': [1, 0], 'nu': [0, 1]}
        result = specialist.process_request(request)
        assert abs(result['tv_distance'] - 1.0) < 1e-10

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'total_variation_distance', 'mu': [0.5, 0.5], 'nu': [0.7, 0.3]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'spectral_gap', 'epsilon': 0.01})
        assert specialist.beliefs.get('epsilon') == 0.01

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'spectral_gap'}
        desires = specialist.deliberate()
        assert 'execute_spectral_gap' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'total_variation_distance', 'mu': [0.5, 0.5], 'nu': [0.7, 0.3]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_spectral_gap(self, specialist, ergodic_chain):
        """Test spectral gap calculation."""
        request = {'operation': 'spectral_gap', 'P': ergodic_chain}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 0 < result['spectral_gap'] <= 1

    def test_coupling_bound(self, specialist, ergodic_chain):
        """Test coupling bound on convergence."""
        request = {'operation': 'coupling_bound', 'P': ergodic_chain, 't': 10}
        result = specialist.process_request(request)
        assert result['success'] is True
