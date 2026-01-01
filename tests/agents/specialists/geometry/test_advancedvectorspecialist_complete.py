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
ADVANCED VECTOR SPECIALIST TESTS
=================================

Comprehensive test suite for AdvancedVectorSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.geometry.advanced_vector_specialist import (
    AdvancedVectorSpecialist
)


class TestAdvancedVectorSpecialistComplete:
    """Comprehensive tests for AdvancedVectorSpecialist."""

    @pytest.fixture
    def specialist(self):
        return AdvancedVectorSpecialist(agent_id='test_advvector_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_advvector_001'
        assert specialist.service_type == 'math.geometry.vector_advanced'
        assert 'vector_projection' in specialist.capabilities

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'vector_projection', 'v': [3, 4], 'onto': [1, 0]}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test vector projection."""
        request = {'operation': 'vector_projection', 'v': [3, 4], 'onto': [1, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        # proj_{[1,0]}[3,4] = [3, 0]
        proj = result['projection']
        assert abs(proj[0] - 3.0) < 1e-10
        assert abs(proj[1] - 0.0) < 1e-10

    def test_complex_problem_solving(self, specialist):
        """Test Gram-Schmidt orthogonalization."""
        request = {'operation': 'gram_schmidt', 'vectors': [[1, 1, 0], [1, 0, 1], [0, 1, 1]]}
        result = specialist.process_request(request)
        assert result['success'] is True
        # Check orthogonality
        orth = result['orthonormal_basis']
        for i in range(len(orth)):
            for j in range(i+1, len(orth)):
                dot = sum(orth[i][k] * orth[j][k] for k in range(len(orth[i])))
                assert abs(dot) < 1e-10

    def test_invalid_input_handling(self, specialist):
        # Zero vector
        request = {'operation': 'vector_projection', 'v': [1, 2], 'onto': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # Projection onto same direction
        request = {'operation': 'vector_projection', 'v': [3, 4], 'onto': [3, 4]}
        result = specialist.process_request(request)
        proj = result['projection']
        assert abs(proj[0] - 3.0) < 1e-10
        assert abs(proj[1] - 4.0) < 1e-10

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'vector_projection', 'v': [1, 2], 'onto': [1, 0]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'gram_schmidt'})
        assert specialist.beliefs.get('operation') == 'gram_schmidt'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'gram_schmidt'}
        desires = specialist.deliberate()
        assert 'execute_gram_schmidt' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'vector_projection', 'v': [1, 2], 'onto': [1, 0]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_rodrigues_rotation(self, specialist):
        """Test 3D rotation using Rodrigues formula."""
        # Rotate [1, 0, 0] by 90 degrees around z-axis
        import math
        request = {
            'operation': 'rotate_vector_3d',
            'v': [1, 0, 0],
            'axis': [0, 0, 1],
            'angle': math.pi / 2
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        rotated = result['rotated']
        assert abs(rotated[0] - 0.0) < 1e-10
        assert abs(rotated[1] - 1.0) < 1e-10

    def test_scalar_triple_product(self, specialist):
        """Test scalar triple product."""
        request = {
            'operation': 'scalar_triple_product',
            'a': [1, 0, 0],
            'b': [0, 1, 0],
            'c': [0, 0, 1]
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['scalar_triple_product'] - 1.0) < 1e-10

    def test_coplanarity(self, specialist):
        """Test coplanarity check."""
        request = {
            'operation': 'are_coplanar',
            'points': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['are_coplanar'] is True
