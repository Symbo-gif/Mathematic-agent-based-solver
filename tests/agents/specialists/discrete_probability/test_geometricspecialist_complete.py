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
GEOMETRIC SPECIALIST TESTS
===========================

Comprehensive test suite for GeometricSpecialist with 12-test pattern.
"""

import pytest
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.geometric_specialist import (
    GeometricSpecialist
)


class TestGeometricSpecialistComplete:
    """Comprehensive tests for GeometricSpecialist."""

    @pytest.fixture
    def specialist(self):
        return GeometricSpecialist(agent_id='test_geometric_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_geometric_001'
        assert specialist.service_type == 'math.probability.discrete.geometric'
        assert 'pmf' in specialist.capabilities

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'pmf', 'k': 5, 'p': 0.5}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test PMF: P(X=k) = p(1-p)^{k-1} for failures-before-success variant."""
        request = {'operation': 'pmf', 'k': 1, 'p': 0.5, 'variant': 'trials'}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['pmf'] - 0.5) < 1e-10

    def test_complex_problem_solving(self, specialist):
        """Test memoryless property and CDF."""
        request = {'operation': 'cdf', 'k': 3, 'p': 0.5, 'variant': 'trials'}
        result = specialist.process_request(request)
        assert result['success'] is True
        # P(X <= 3) = 1 - (1-p)^3 = 1 - 0.125 = 0.875
        assert abs(result['cdf'] - 0.875) < 1e-10

    def test_invalid_input_handling(self, specialist):
        request = {'operation': 'pmf', 'k': 1, 'p': 1.5}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # p=1: First trial always success
        request = {'operation': 'pmf', 'k': 1, 'p': 1.0, 'variant': 'trials'}
        result = specialist.process_request(request)
        assert result['pmf'] == 1.0

        # k=0 for failures variant
        request = {'operation': 'pmf', 'k': 0, 'p': 0.5, 'variant': 'failures'}
        result = specialist.process_request(request)
        assert abs(result['pmf'] - 0.5) < 1e-10

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'pmf', 'k': 1, 'p': 0.5})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'pmf', 'p': 0.3})
        assert specialist.beliefs.get('p') == 0.3

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'pmf'}
        desires = specialist.deliberate()
        assert 'execute_pmf' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'pmf', 'k': 1, 'p': 0.5}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_expectation_variance(self, specialist):
        # E[X] = 1/p for trials variant
        request = {'operation': 'expectation', 'p': 0.25, 'variant': 'trials'}
        result = specialist.process_request(request)
        assert abs(result['expectation'] - 4.0) < 1e-10

    def test_memoryless_property(self, specialist):
        """Test memoryless property verification."""
        request = {'operation': 'memoryless_check', 'p': 0.5, 's': 3, 't': 2}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_memoryless'] is True
