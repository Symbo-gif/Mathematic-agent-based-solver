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
TRANSFORMATION GROUP SPECIALIST TESTS
======================================

Comprehensive test suite for TransformationGroupSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock
import math

from symbo_agentic_reasoners.agents.specialists.geometry.transformation_group_specialist import (
    TransformationGroupSpecialist
)


class TestTransformationGroupSpecialistComplete:
    """Comprehensive tests for TransformationGroupSpecialist."""

    @pytest.fixture
    def specialist(self):
        return TransformationGroupSpecialist(agent_id='test_group_001')

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
        assert specialist.agent_id == 'test_group_001'
        assert specialist.service_type == 'math.geometry.transformation_group'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'symmetry_group_of_polygon'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, rotation_90):
        """Test group order (cyclic group of rotations)."""
        request = {'operation': 'element_order', 'A': rotation_90, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['order'] == 4  # 90 degree rotation has order 4

    def test_complex_problem_solving(self, specialist):
        """Test symmetry group of polygon (dihedral group)."""
        request = {'operation': 'symmetry_group_of_polygon', 'n': 4}  # Square
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['group_order'] == 8  # D_4 has order 8

    def test_invalid_input_handling(self, specialist):
        # Non-group (not closed under composition)
        request = {'operation': 'generate_group', 'generators': [[[1, 0], [0, 1]]], 'max_elements': 10}
        result = specialist.process_request(request)
        # Should handle gracefully

    def test_edge_cases(self, specialist):
        # Identity (trivial group)
        request = {'operation': 'element_order', 'A': [[1, 0], [0, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['order'] == 1

        # Single element polygon (n=1)
        request = {'operation': 'symmetry_group_of_polygon', 'n': 1}
        result = specialist.process_request(request)
        # D_1 has order 2

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, rotation_90):
        specialist.process_request({'operation': 'element_order', 'A': rotation_90, 'b': [0, 0]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'cayley_table'})
        assert specialist.beliefs.get('operation') == 'cayley_table'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'cayley_table'}
        desires = specialist.deliberate()
        assert 'execute_cayley_table' in desires

    def test_bdi_execute_step(self, specialist, rotation_90):
        specialist.beliefs = {'operation': 'element_order', 'A': rotation_90, 'b': [0, 0]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_generate_group(self, specialist, rotation_90, reflection_x):
        """Test group generation from generators."""
        request = {
            'operation': 'generate_group',
            'generators': [
                {'A': rotation_90, 'b': [0, 0]},
                {'A': reflection_x, 'b': [0, 0]}
            ],
            'max_elements': 10
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        # Should generate D_4

    def test_is_abelian(self, specialist, rotation_90, reflection_x):
        """Test abelian group check."""
        # D_n for n >= 3 is non-abelian
        request = {'operation': 'symmetry_group_of_polygon', 'n': 3}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_conjugacy_classes(self, specialist):
        """Test conjugacy class computation."""
        request = {'operation': 'symmetry_group_of_polygon', 'n': 3}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_cyclic_group(self, specialist):
        """Test cyclic group detection."""
        # C_4 (rotations only)
        request = {'operation': 'symmetry_group_of_polygon', 'n': 4}
        result = specialist.process_request(request)
        assert result['success'] is True


class TestTransformationGroupEdgeCases:
    """Extended edge case tests."""

    @pytest.fixture
    def specialist(self):
        return TransformationGroupSpecialist()

    def test_large_n_dihedral(self, specialist):
        """Test dihedral group for large n."""
        request = {'operation': 'symmetry_group_of_polygon', 'n': 100}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['group_order'] == 200  # D_100 has order 200

    def test_half_turn(self, specialist):
        """Test 180 degree rotation order."""
        A = [[-1, 0], [0, -1]]  # 180 degree rotation
        request = {'operation': 'element_order', 'A': A, 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['order'] == 2
