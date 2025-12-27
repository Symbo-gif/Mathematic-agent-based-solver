# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
HYPERGEOMETRIC SPECIALIST TESTS
================================

Comprehensive test suite for HypergeometricSpecialist with 12-test pattern.
"""

import pytest
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.hypergeometric_specialist import (
    HypergeometricSpecialist
)


class TestHypergeometricSpecialistComplete:
    """Comprehensive tests for HypergeometricSpecialist."""

    @pytest.fixture
    def specialist(self):
        return HypergeometricSpecialist(agent_id='test_hypergeom_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_hypergeom_001'
        assert specialist.service_type == 'math.probability.discrete.hypergeometric'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'pmf', 'k': 2, 'N': 20, 'K': 7, 'n': 5}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test PMF for drawing without replacement."""
        # Deck of 20 cards, 7 special, draw 5, probability of exactly 2 special
        request = {'operation': 'pmf', 'k': 2, 'N': 20, 'K': 7, 'n': 5}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 0 < result['pmf'] < 1

    def test_complex_problem_solving(self, specialist):
        """Test CDF and binomial approximation."""
        request = {'operation': 'cdf', 'k': 3, 'N': 50, 'K': 20, 'n': 10}
        result = specialist.process_request(request)
        assert result['success'] is True

        request = {'operation': 'binomial_approximation', 'N': 1000, 'K': 100, 'n': 10}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_invalid_input_handling(self, specialist):
        # k > min(K, n)
        request = {'operation': 'pmf', 'k': 10, 'N': 20, 'K': 5, 'n': 8}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['pmf'] == 0.0

        # n > N
        request = {'operation': 'pmf', 'k': 2, 'N': 10, 'K': 5, 'n': 15}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # All successes possible
        request = {'operation': 'pmf', 'k': 5, 'N': 20, 'K': 10, 'n': 5}
        result = specialist.process_request(request)
        assert result['success'] is True

        # K=0: No successes possible
        request = {'operation': 'pmf', 'k': 0, 'N': 20, 'K': 0, 'n': 5}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'pmf', 'k': 2, 'N': 20, 'K': 7, 'n': 5})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'pmf', 'N': 100})
        assert specialist.beliefs.get('N') == 100

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'pmf'}
        desires = specialist.deliberate()
        assert 'execute_pmf' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'pmf', 'k': 2, 'N': 20, 'K': 7, 'n': 5}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_expectation_variance(self, specialist):
        # E[X] = n*K/N
        request = {'operation': 'expectation', 'N': 20, 'K': 8, 'n': 5}
        result = specialist.process_request(request)
        assert abs(result['expectation'] - 2.0) < 1e-10
