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
HITTING TIME SPECIALIST TESTS
==============================

Comprehensive test suite for HittingTimeSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.hitting_time_specialist import (
    HittingTimeSpecialist
)


class TestHittingTimeSpecialistComplete:
    """Comprehensive tests for HittingTimeSpecialist."""

    @pytest.fixture
    def specialist(self):
        return HittingTimeSpecialist(agent_id='test_hitting_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def simple_chain(self):
        return [[0.5, 0.5, 0], [0.25, 0.5, 0.25], [0, 0.5, 0.5]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_hitting_001'
        assert specialist.service_type == 'math.probability.discrete.hitting'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'mean_hitting_time', 'P': [[0.5, 0.5], [0.5, 0.5]], 'source': 0, 'target': 1}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, simple_chain):
        """Test mean hitting time calculation."""
        request = {'operation': 'mean_hitting_time', 'P': simple_chain, 'source': 0, 'target': 2}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 'mean_hitting_time' in result

    def test_complex_problem_solving(self, specialist):
        """Test absorption probabilities with absorbing chain."""
        P = [[1.0, 0.0, 0.0], [0.3, 0.4, 0.3], [0.0, 0.0, 1.0]]
        request = {'operation': 'absorption_probabilities', 'P': P, 'absorbing_states': [0, 2]}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_invalid_input_handling(self, specialist, simple_chain):
        # Source = Target
        request = {'operation': 'mean_hitting_time', 'P': simple_chain, 'source': 0, 'target': 0}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['mean_hitting_time'] == 0

    def test_edge_cases(self, specialist):
        # Single state
        request = {'operation': 'mean_hitting_time', 'P': [[1.0]], 'source': 0, 'target': 0}
        result = specialist.process_request(request)
        assert result['mean_hitting_time'] == 0

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, simple_chain):
        specialist.process_request({'operation': 'mean_hitting_time', 'P': simple_chain, 'source': 0, 'target': 1})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'mean_hitting_time', 'source': 0})
        assert specialist.beliefs.get('source') == 0

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'mean_hitting_time'}
        desires = specialist.deliberate()
        assert 'execute_mean_hitting_time' in desires

    def test_bdi_execute_step(self, specialist, simple_chain):
        specialist.beliefs = {'operation': 'mean_hitting_time', 'P': simple_chain, 'source': 0, 'target': 2}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_gambler_ruin(self, specialist):
        """Test gambler's ruin problem."""
        request = {'operation': 'gambler_ruin', 'p': 0.5, 'initial': 5, 'target': 10}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_commute_time(self, specialist, simple_chain):
        """Test commute time (round trip hitting time)."""
        request = {'operation': 'commute_time', 'P': simple_chain, 'state_a': 0, 'state_b': 2}
        result = specialist.process_request(request)
        assert result['success'] is True
