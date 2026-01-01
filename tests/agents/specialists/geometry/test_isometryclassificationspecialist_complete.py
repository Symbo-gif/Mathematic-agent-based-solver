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
ISOMETRY CLASSIFICATION SPECIALIST TESTS
=========================================

Comprehensive test suite for IsometryClassificationSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock
import math

from symbo_agentic_reasoners.agents.specialists.geometry.isometry_classification_specialist import (
    IsometryClassificationSpecialist
)


class TestIsometryClassificationSpecialistComplete:
    """Comprehensive tests for IsometryClassificationSpecialist."""

    @pytest.fixture
    def specialist(self):
        return IsometryClassificationSpecialist(agent_id='test_isometry_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def rotation_90(self):
        """90 degree rotation matrix."""
        return [[0, -1], [1, 0]]

    @pytest.fixture
    def reflection_x(self):
        """Reflection across x-axis."""
        return [[1, 0], [0, -1]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_isometry_001'
        assert specialist.service_type == 'math.geometry.isometry'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'classify_isometry'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, rotation_90):
        """Test isometry classification."""
        request = {'operation': 'classify_isometry', 'A': rotation_90, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['type'] == 'rotation'

    def test_complex_problem_solving(self, specialist, rotation_90, reflection_x):
        """Test isometry composition."""
        request = {
            'operation': 'compose_isometries',
            'A1': rotation_90, 'b1': [0, 0],
            'A2': reflection_x, 'b2': [0, 0]
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_invalid_input_handling(self, specialist):
        # Non-orthogonal matrix
        request = {'operation': 'classify_isometry', 'A': [[1, 1], [0, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is False or result['is_isometry'] is False

    def test_edge_cases(self, specialist):
        # Identity
        request = {'operation': 'classify_isometry', 'A': [[1, 0], [0, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['type'] == 'identity'

        # Pure translation
        request = {'operation': 'classify_isometry', 'A': [[1, 0], [0, 1]], 'b': [1, 2]}
        result = specialist.process_request(request)
        assert result['type'] == 'translation'

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, rotation_90):
        specialist.process_request({'operation': 'classify_isometry', 'A': rotation_90, 'b': [0, 0]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'classify_isometry'})
        assert specialist.beliefs.get('operation') == 'classify_isometry'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'classify_isometry'}
        desires = specialist.deliberate()
        assert 'execute_classify_isometry' in desires

    def test_bdi_execute_step(self, specialist, rotation_90):
        specialist.beliefs = {'operation': 'classify_isometry', 'A': rotation_90, 'b': [0, 0]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_fixed_points(self, specialist, rotation_90):
        """Test fixed point detection."""
        request = {'operation': 'fixed_points', 'A': rotation_90, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_isometry_order(self, specialist, rotation_90):
        """Test isometry order (period)."""
        request = {'operation': 'isometry_order', 'A': rotation_90, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['order'] == 4  # 90 degree rotation has order 4

    def test_glide_reflection(self, specialist):
        """Test glide reflection classification."""
        # Reflection across x-axis with translation along x
        request = {
            'operation': 'classify_isometry',
            'A': [[1, 0], [0, -1]],
            'b': [1, 0]
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['type'] == 'glide_reflection'
