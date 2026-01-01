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
DISCRETE MOMENT SPECIALIST TESTS
=================================

Comprehensive test suite for DiscreteMomentSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.discrete_moment_specialist import (
    DiscreteMomentSpecialist
)


class TestDiscreteMomentSpecialistComplete:
    """Comprehensive tests for DiscreteMomentSpecialist."""

    @pytest.fixture
    def specialist(self):
        return DiscreteMomentSpecialist(agent_id='test_moment_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_moment_001'
        assert specialist.service_type == 'math.probability.discrete.moments'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'raw_moment', 'k': 2, 'values': [0, 1], 'probs': [0.5, 0.5]}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test raw moment calculation."""
        # E[X^2] for Bernoulli(0.5): 0^2*0.5 + 1^2*0.5 = 0.5
        request = {'operation': 'raw_moment', 'k': 2, 'values': [0, 1], 'probs': [0.5, 0.5]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['moment'] - 0.5) < 1e-10

    def test_complex_problem_solving(self, specialist):
        """Test MGF calculation."""
        # M(t) = E[e^{tX}] for Bernoulli(0.5) at t=0 should be 1
        request = {'operation': 'mgf', 't': 0, 'values': [0, 1], 'probs': [0.5, 0.5]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['mgf'] - 1.0) < 1e-10

    def test_invalid_input_handling(self, specialist):
        # Probabilities don't sum to 1
        request = {'operation': 'raw_moment', 'k': 1, 'values': [0, 1], 'probs': [0.3, 0.3]}
        result = specialist.process_request(request)
        # Should handle or warn

    def test_edge_cases(self, specialist):
        # Single value (degenerate)
        request = {'operation': 'raw_moment', 'k': 1, 'values': [5], 'probs': [1.0]}
        result = specialist.process_request(request)
        assert abs(result['moment'] - 5.0) < 1e-10

        # Zero probability values
        request = {'operation': 'raw_moment', 'k': 1, 'values': [0, 1, 2], 'probs': [0.5, 0.0, 0.5]}
        result = specialist.process_request(request)
        assert abs(result['moment'] - 1.0) < 1e-10

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'raw_moment', 'k': 1, 'values': [0, 1], 'probs': [0.5, 0.5]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'central_moment', 'k': 2})
        assert specialist.beliefs.get('k') == 2

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'central_moment'}
        desires = specialist.deliberate()
        assert 'execute_central_moment' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'raw_moment', 'k': 1, 'values': [0, 1], 'probs': [0.5, 0.5]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_central_moment(self, specialist):
        """Test central moment (variance is 2nd central moment)."""
        # Var(X) = E[(X-mu)^2] for Bernoulli(0.5) = 0.25
        request = {'operation': 'central_moment', 'k': 2, 'values': [0, 1], 'probs': [0.5, 0.5]}
        result = specialist.process_request(request)
        assert abs(result['moment'] - 0.25) < 1e-10

    def test_factorial_moment(self, specialist):
        """Test factorial moment."""
        request = {'operation': 'factorial_moment', 'k': 2, 'values': [0, 1, 2, 3], 'probs': [0.25, 0.25, 0.25, 0.25]}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_standardized_moments(self, specialist):
        """Test skewness and kurtosis."""
        request = {'operation': 'standardized_moments', 'values': [0, 1], 'probs': [0.5, 0.5]}
        result = specialist.process_request(request)
        assert result['success'] is True
        # Bernoulli(0.5) is symmetric, skewness = 0
        assert abs(result['skewness']) < 1e-10
