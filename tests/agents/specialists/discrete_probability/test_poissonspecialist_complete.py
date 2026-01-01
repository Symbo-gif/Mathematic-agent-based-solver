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
POISSON SPECIALIST TESTS
=========================

Comprehensive test suite for PoissonSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.poisson_specialist import (
    PoissonSpecialist
)


class TestPoissonSpecialistComplete:
    """Comprehensive tests for PoissonSpecialist."""

    @pytest.fixture
    def specialist(self):
        return PoissonSpecialist(agent_id='test_poisson_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_poisson_001'
        assert specialist.service_type == 'math.probability.discrete.poisson'
        assert 'pmf' in specialist.capabilities

    def test_df_registration(self, specialist, mock_df):
        """Test DF registration."""
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        """Test blackboard entry creation."""
        problem = {'operation': 'pmf', 'k': 5, 'lam': 3.0}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test simple PMF calculation."""
        # P(X=0) for lambda=1 should be e^{-1}
        request = {'operation': 'pmf', 'k': 0, 'lam': 1.0}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['pmf'] - np.exp(-1)) < 1e-10

    def test_complex_problem_solving(self, specialist):
        """Test CDF and sum of Poissons."""
        # CDF
        request = {'operation': 'cdf', 'k': 5, 'lam': 3.0}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 0.7 < result['cdf'] < 1.0

        # Sum of Poissons
        request = {'operation': 'sum_poisson', 'lambdas': [1.0, 2.0, 3.0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['combined_lambda'] - 6.0) < 1e-10

    def test_invalid_input_handling(self, specialist):
        """Test invalid input handling."""
        # Negative lambda
        request = {'operation': 'pmf', 'k': 5, 'lam': -1.0}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        """Test edge cases."""
        # Lambda = 0: X is always 0
        request = {'operation': 'pmf', 'k': 0, 'lam': 0.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

        request = {'operation': 'pmf', 'k': 1, 'lam': 0.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 0.0

    def test_error_reporting(self, specialist):
        """Test error reporting."""
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        """Test statistics reporting."""
        specialist.process_request({'operation': 'pmf', 'k': 0, 'lam': 1.0})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        """Test BDI update_beliefs."""
        specialist.update_beliefs({'operation': 'pmf', 'lam': 5.0})
        assert specialist.beliefs.get('lam') == 5.0

    def test_bdi_deliberate(self, specialist):
        """Test BDI deliberate."""
        specialist.beliefs = {'operation': 'pmf'}
        desires = specialist.deliberate()
        assert 'execute_pmf' in desires

    def test_bdi_execute_step(self, specialist):
        """Test BDI execute_step."""
        specialist.beliefs = {'operation': 'pmf', 'k': 3, 'lam': 2.0}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_expectation_variance(self, specialist):
        """Test expectation and variance (both equal lambda)."""
        request = {'operation': 'expectation', 'lam': 5.0}
        result = specialist.process_request(request)
        assert abs(result['expectation'] - 5.0) < 1e-10

        request = {'operation': 'variance', 'lam': 5.0}
        result = specialist.process_request(request)
        assert abs(result['variance'] - 5.0) < 1e-10

    def test_binomial_approximation(self, specialist):
        """Test Poisson as binomial approximation."""
        request = {'operation': 'binomial_approximation', 'n': 100, 'p': 0.03}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['lambda'] - 3.0) < 1e-10
