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
SIMILARITY TRANSFORMATION SPECIALIST TESTS
===========================================

Comprehensive test suite for SimilarityTransformationSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock
import math

from symbo_agentic_reasoners.agents.specialists.geometry.similarity_transformation_specialist import (
    SimilarityTransformationSpecialist
)


class TestSimilarityTransformationSpecialistComplete:
    """Comprehensive tests for SimilarityTransformationSpecialist."""

    @pytest.fixture
    def specialist(self):
        return SimilarityTransformationSpecialist(agent_id='test_similarity_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def scaling_2x(self):
        """2x scaling matrix."""
        return [[2, 0], [0, 2]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_similarity_001'
        assert specialist.service_type == 'math.geometry.similarity'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'classify_similarity'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, scaling_2x):
        """Test similarity classification."""
        request = {'operation': 'classify_similarity', 'A': scaling_2x, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_similarity'] is True
        assert abs(result['ratio'] - 2.0) < 1e-10

    def test_complex_problem_solving(self, specialist):
        """Test similar triangles check."""
        tri1 = [[0, 0], [3, 0], [0, 4]]
        tri2 = [[0, 0], [6, 0], [0, 8]]
        request = {'operation': 'are_similar_triangles', 'triangle1': tri1, 'triangle2': tri2}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['are_similar'] is True

    def test_invalid_input_handling(self, specialist):
        # Non-similarity (shear)
        request = {'operation': 'classify_similarity', 'A': [[1, 1], [0, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['is_similarity'] is False

    def test_edge_cases(self, specialist):
        # Identity (ratio = 1)
        request = {'operation': 'classify_similarity', 'A': [[1, 0], [0, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['is_similarity'] is True
        assert abs(result['ratio'] - 1.0) < 1e-10

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, scaling_2x):
        specialist.process_request({'operation': 'classify_similarity', 'A': scaling_2x, 'b': [0, 0]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'similarity_ratio'})
        assert specialist.beliefs.get('operation') == 'similarity_ratio'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'similarity_ratio'}
        desires = specialist.deliberate()
        assert 'execute_similarity_ratio' in desires

    def test_bdi_execute_step(self, specialist, scaling_2x):
        specialist.beliefs = {'operation': 'classify_similarity', 'A': scaling_2x, 'b': [0, 0]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_spiral_similarity(self, specialist):
        """Test spiral similarity parameters."""
        # 45 degree rotation with sqrt(2) scaling
        angle = math.pi / 4
        s = math.sqrt(2)
        A = [[s * math.cos(angle), -s * math.sin(angle)],
             [s * math.sin(angle), s * math.cos(angle)]]
        request = {'operation': 'spiral_similarity_params', 'A': A, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert abs(result['ratio'] - s) < 1e-10

    def test_decompose_similarity(self, specialist, scaling_2x):
        """Test similarity decomposition."""
        request = {'operation': 'decompose_similarity', 'A': scaling_2x, 'b': [1, 2]}
        result = specialist.process_request(request)
        assert result['success'] is True
