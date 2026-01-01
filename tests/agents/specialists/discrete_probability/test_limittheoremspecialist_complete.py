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
LIMIT THEOREM SPECIALIST TESTS
===============================

Comprehensive test suite for LimitTheoremSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.limit_theorem_specialist import (
    LimitTheoremSpecialist
)


class TestLimitTheoremSpecialistComplete:
    """Comprehensive tests for LimitTheoremSpecialist."""

    @pytest.fixture
    def specialist(self):
        return LimitTheoremSpecialist(agent_id='test_limit_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_limit_001'
        assert specialist.service_type == 'math.probability.discrete.limit'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'weak_law', 'n': 100, 'mu': 0.5, 'sigma': 0.5, 'epsilon': 0.1}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test weak law of large numbers bound."""
        request = {'operation': 'weak_law', 'n': 100, 'mu': 0, 'sigma': 1, 'epsilon': 0.1}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 'bound' in result

    def test_complex_problem_solving(self, specialist):
        """Test CLT approximation."""
        request = {'operation': 'clt', 'n': 100, 'mu': 0, 'sigma': 1, 'x': 0}
        result = specialist.process_request(request)
        assert result['success'] is True
        # P(S_n/sqrt(n) <= 0) should be approximately 0.5
        assert 0.4 < result['probability'] < 0.6

    def test_invalid_input_handling(self, specialist):
        # Negative n
        request = {'operation': 'weak_law', 'n': -10, 'mu': 0, 'sigma': 1, 'epsilon': 0.1}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # Very large n (should give tight bound)
        request = {'operation': 'weak_law', 'n': 1000000, 'mu': 0, 'sigma': 1, 'epsilon': 0.01}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['bound'] < 0.1

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'weak_law', 'n': 100, 'mu': 0, 'sigma': 1, 'epsilon': 0.1})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'clt', 'n': 100})
        assert specialist.beliefs.get('n') == 100

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'clt'}
        desires = specialist.deliberate()
        assert 'execute_clt' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'weak_law', 'n': 100, 'mu': 0, 'sigma': 1, 'epsilon': 0.1}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_chebyshev_bound(self, specialist):
        """Test Chebyshev inequality."""
        request = {'operation': 'chebyshev_bound', 'sigma': 1, 'k': 2}
        result = specialist.process_request(request)
        assert result['success'] is True
        # P(|X - mu| >= 2*sigma) <= 1/4
        assert abs(result['bound'] - 0.25) < 1e-10

    def test_hoeffding_bound(self, specialist):
        """Test Hoeffding's inequality."""
        request = {'operation': 'hoeffding_bound', 'n': 100, 't': 0.1, 'a': 0, 'b': 1}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 0 < result['bound'] < 1

    def test_sample_size_required(self, specialist):
        """Test sample size calculation for given precision."""
        request = {'operation': 'sample_size_required', 'epsilon': 0.1, 'delta': 0.05, 'sigma': 1}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['n'] > 0
