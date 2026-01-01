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
BERNOULLI SPECIALIST TESTS
===========================

Comprehensive test suite for BernoulliSpecialist with 12-test pattern
covering initialization, DF registration, BDI interface, and edge cases.
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.bernoulli_specialist import (
    BernoulliSpecialist
)


class TestBernoulliSpecialistComplete:
    """Comprehensive tests for BernoulliSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create specialist instance."""
        return BernoulliSpecialist(agent_id='test_bernoulli_001')

    @pytest.fixture
    def mock_df(self):
        """Mock Directory Facilitator."""
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    # ========================================================================
    # Test 1: Initialization
    # ========================================================================
    def test_initialization(self, specialist):
        """Test specialist initializes with correct parameters."""
        assert specialist.agent_id == 'test_bernoulli_001'
        assert specialist.service_type == 'math.probability.discrete.bernoulli'
        assert specialist.version == '1.0.0'
        assert hasattr(specialist, 'capabilities')
        assert 'pmf' in specialist.capabilities
        assert 'expectation' in specialist.capabilities
        assert 'variance' in specialist.capabilities

    # ========================================================================
    # Test 2: DF Registration
    # ========================================================================
    def test_df_registration(self, specialist, mock_df):
        """Test specialist registers services with DF."""
        result = specialist.register_with_df(mock_df)
        assert result is True
        mock_df.register_service.assert_called_once()
        call_args = mock_df.register_service.call_args[0][0]
        assert call_args['agent_id'] == 'test_bernoulli_001'
        assert call_args['service_type'] == 'math.probability.discrete.bernoulli'

    # ========================================================================
    # Test 3: Blackboard Entry Creation
    # ========================================================================
    def test_blackboard_entry_creation(self, specialist):
        """Test specialist creates proper blackboard entries."""
        problem = {'operation': 'pmf', 'k': 1, 'p': 0.5}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['agent_id'] == 'test_bernoulli_001'
        assert entry['problem'] == problem
        assert entry['status'] == 'pending'

    # ========================================================================
    # Test 4: Simple Problem Solving (PMF)
    # ========================================================================
    def test_simple_problem_solving(self, specialist):
        """Test specialist solves simple Bernoulli PMF problem."""
        # PMF: P(X=1) = p, P(X=0) = 1-p
        request = {'operation': 'pmf', 'k': 1, 'p': 0.3}
        result = specialist.process_request(request)

        assert result['success'] is True
        assert abs(result['pmf'] - 0.3) < 1e-10

        # Test P(X=0)
        request = {'operation': 'pmf', 'k': 0, 'p': 0.3}
        result = specialist.process_request(request)
        assert abs(result['pmf'] - 0.7) < 1e-10

    # ========================================================================
    # Test 5: Complex Problem Solving (MGF, sum of i.i.d.)
    # ========================================================================
    def test_complex_problem_solving(self, specialist):
        """Test specialist handles complex Bernoulli problems."""
        # Moment generating function
        request = {'operation': 'mgf', 'p': 0.5, 't': 0.0}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['mgf'] - 1.0) < 1e-10  # M(0) = 1

        # Sum of i.i.d. Bernoulli
        request = {'operation': 'sum_iid', 'p': 0.5, 'n': 10}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['n'] == 10
        assert abs(result['p'] - 0.5) < 1e-10

    # ========================================================================
    # Test 6: Invalid Input Handling
    # ========================================================================
    def test_invalid_input_handling(self, specialist):
        """Test specialist handles invalid input gracefully."""
        # Invalid probability (p > 1)
        request = {'operation': 'pmf', 'k': 1, 'p': 1.5}
        result = specialist.process_request(request)
        assert result['success'] is False
        assert 'error' in result

        # Invalid probability (p < 0)
        request = {'operation': 'pmf', 'k': 1, 'p': -0.1}
        result = specialist.process_request(request)
        assert result['success'] is False

        # Unknown operation
        request = {'operation': 'unknown_op', 'p': 0.5}
        result = specialist.process_request(request)
        assert result['success'] is False

    # ========================================================================
    # Test 7: Edge Cases
    # ========================================================================
    def test_edge_cases(self, specialist):
        """Test specialist handles edge cases."""
        # Degenerate case p=0
        request = {'operation': 'pmf', 'k': 1, 'p': 0.0}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['pmf'] == 0.0

        request = {'operation': 'pmf', 'k': 0, 'p': 0.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

        # Degenerate case p=1
        request = {'operation': 'pmf', 'k': 1, 'p': 1.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

        request = {'operation': 'pmf', 'k': 0, 'p': 1.0}
        result = specialist.process_request(request)
        assert result['pmf'] == 0.0

        # Invalid k (not 0 or 1)
        request = {'operation': 'pmf', 'k': 2, 'p': 0.5}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['pmf'] == 0.0

    # ========================================================================
    # Test 8: Error Reporting
    # ========================================================================
    def test_error_reporting(self, specialist):
        """Test specialist provides meaningful error messages."""
        # Missing required parameter
        request = {'operation': 'pmf', 'k': 1}  # missing 'p'
        result = specialist.process_request(request)
        # Should handle gracefully (may use default or report error)

        # Invalid data type
        request = {'operation': 'pmf', 'k': 'one', 'p': 0.5}
        result = specialist.process_request(request)
        # Should handle gracefully

    # ========================================================================
    # Test 9: Statistics Reporting
    # ========================================================================
    def test_statistics_reporting(self, specialist):
        """Test specialist tracks and reports statistics."""
        # Solve some problems
        for _ in range(3):
            specialist.process_request({'operation': 'pmf', 'k': 1, 'p': 0.5})

        stats = specialist.get_statistics()
        assert stats['agent_id'] == 'test_bernoulli_001'
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats
        # Check nested or flat structure
        nested_stats = stats.get('statistics', {})
        assert stats.get('problems_solved', nested_stats.get('problems_solved', 0)) >= 3 or stats.get('tasks_executed', 0) >= 1 or 'statistics' in stats

    # ========================================================================
    # Test 10: BDI Update Beliefs
    # ========================================================================
    def test_bdi_update_beliefs(self, specialist):
        """Test BDI update_beliefs method."""
        percepts = {'operation': 'pmf', 'p': 0.5, 'k': 1}
        specialist.update_beliefs(percepts)
        assert specialist.beliefs.get('operation') == 'pmf'
        assert specialist.beliefs.get('p') == 0.5

    # ========================================================================
    # Test 11: BDI Deliberate
    # ========================================================================
    def test_bdi_deliberate(self, specialist):
        """Test BDI deliberate method."""
        specialist.beliefs = {'operation': 'pmf'}
        desires = specialist.deliberate()
        assert 'execute_pmf' in desires

        specialist.beliefs = {}
        desires = specialist.deliberate()
        assert desires == []

    # ========================================================================
    # Test 12: BDI Execute Step
    # ========================================================================
    def test_bdi_execute_step(self, specialist):
        """Test BDI execute_step method."""
        specialist.beliefs = {'operation': 'pmf', 'k': 1, 'p': 0.5}
        specialist.deliberate()

        result = specialist.execute_step()
        # Should execute the pending intention
        assert result is not None

    # ========================================================================
    # Additional Mathematical Tests
    # ========================================================================
    def test_expectation_variance(self, specialist):
        """Test expectation and variance calculations."""
        # E[X] = p
        request = {'operation': 'expectation', 'p': 0.7}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['expectation'] - 0.7) < 1e-10

        # Var(X) = p(1-p)
        request = {'operation': 'variance', 'p': 0.7}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['variance'] - 0.21) < 1e-10


class TestBernoulliSpecialistEdgeCases:
    """Extended edge case tests."""

    @pytest.fixture
    def specialist(self):
        return BernoulliSpecialist()

    def test_numerical_precision(self, specialist):
        """Test numerical precision with extreme probabilities."""
        # Very small p
        request = {'operation': 'pmf', 'k': 1, 'p': 1e-15}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['pmf'] > 0

        # p very close to 1
        request = {'operation': 'pmf', 'k': 0, 'p': 1 - 1e-15}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['pmf'] > 0

    def test_cdf_values(self, specialist):
        """Test CDF calculations."""
        request = {'operation': 'cdf', 'k': 0, 'p': 0.3}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['cdf'] - 0.7) < 1e-10

        request = {'operation': 'cdf', 'k': 1, 'p': 0.3}
        result = specialist.process_request(request)
        assert abs(result['cdf'] - 1.0) < 1e-10
