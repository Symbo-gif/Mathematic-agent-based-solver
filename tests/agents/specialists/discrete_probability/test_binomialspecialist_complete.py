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
BINOMIAL SPECIALIST TESTS
==========================

Comprehensive test suite for BinomialSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.binomial_specialist import (
    BinomialSpecialist
)


class TestBinomialSpecialistComplete:
    """Comprehensive tests for BinomialSpecialist."""

    @pytest.fixture
    def specialist(self):
        return BinomialSpecialist(agent_id='test_binomial_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_binomial_001'
        assert specialist.service_type == 'math.probability.discrete.binomial'
        assert 'pmf' in specialist.capabilities
        assert 'cdf' in specialist.capabilities
        assert 'normal_approximation' in specialist.capabilities

    def test_df_registration(self, specialist, mock_df):
        """Test DF registration."""
        result = specialist.register_with_df(mock_df)
        assert result is True
        mock_df.register_service.assert_called_once()

    def test_blackboard_entry_creation(self, specialist):
        """Test blackboard entry creation."""
        problem = {'operation': 'pmf', 'k': 5, 'n': 10, 'p': 0.5}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['agent_id'] == 'test_binomial_001'
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test simple PMF calculation."""
        # P(X=5) for n=10, p=0.5
        request = {'operation': 'pmf', 'k': 5, 'n': 10, 'p': 0.5}
        result = specialist.process_request(request)
        assert result['success'] is True
        # C(10,5) * 0.5^10 = 252/1024 ≈ 0.246
        assert abs(result['pmf'] - 0.24609375) < 1e-6

    def test_complex_problem_solving(self, specialist):
        """Test CDF and normal approximation."""
        # CDF: P(X <= 5) for n=10, p=0.5
        request = {'operation': 'cdf', 'k': 5, 'n': 10, 'p': 0.5}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 0.5 < result['cdf'] < 0.7

        # Normal approximation for large n
        request = {'operation': 'normal_approximation', 'k': 50, 'n': 100, 'p': 0.5}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_invalid_input_handling(self, specialist):
        """Test invalid input handling."""
        # k > n
        request = {'operation': 'pmf', 'k': 11, 'n': 10, 'p': 0.5}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['pmf'] == 0.0

        # Invalid p
        request = {'operation': 'pmf', 'k': 5, 'n': 10, 'p': 1.5}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        """Test edge cases."""
        # p=0: X is always 0
        request = {'operation': 'pmf', 'k': 0, 'n': 10, 'p': 0.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

        # p=1: X is always n
        request = {'operation': 'pmf', 'k': 10, 'n': 10, 'p': 1.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

        # n=0
        request = {'operation': 'pmf', 'k': 0, 'n': 0, 'p': 0.5}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

    def test_error_reporting(self, specialist):
        """Test error reporting."""
        request = {'operation': 'unknown_op'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        """Test statistics reporting."""
        specialist.process_request({'operation': 'pmf', 'k': 5, 'n': 10, 'p': 0.5})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        """Test BDI update_beliefs."""
        specialist.update_beliefs({'operation': 'pmf', 'n': 10})
        assert specialist.beliefs.get('n') == 10

    def test_bdi_deliberate(self, specialist):
        """Test BDI deliberate."""
        specialist.beliefs = {'operation': 'pmf'}
        desires = specialist.deliberate()
        assert 'execute_pmf' in desires

    def test_bdi_execute_step(self, specialist):
        """Test BDI execute_step."""
        specialist.beliefs = {'operation': 'pmf', 'k': 5, 'n': 10, 'p': 0.5}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_expectation_variance(self, specialist):
        """Test expectation and variance."""
        # E[X] = np
        request = {'operation': 'expectation', 'n': 10, 'p': 0.3}
        result = specialist.process_request(request)
        assert abs(result['expectation'] - 3.0) < 1e-10

        # Var(X) = np(1-p)
        request = {'operation': 'variance', 'n': 10, 'p': 0.3}
        result = specialist.process_request(request)
        assert abs(result['variance'] - 2.1) < 1e-10

    def test_mode_calculation(self, specialist):
        """Test mode calculation."""
        request = {'operation': 'mode', 'n': 10, 'p': 0.3}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['mode'] == 3  # floor((n+1)p) = floor(3.3) = 3
