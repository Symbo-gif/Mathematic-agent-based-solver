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
BARYCENTRIC COORDINATES SPECIALIST TESTS
=========================================

Comprehensive test suite for BarycentricCoordinatesSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.geometry.barycentric_coordinates_specialist import (
    BarycentricCoordinatesSpecialist
)


class TestBarycentricCoordinatesSpecialistComplete:
    """Comprehensive tests for BarycentricCoordinatesSpecialist."""

    @pytest.fixture
    def specialist(self):
        return BarycentricCoordinatesSpecialist(agent_id='test_bary_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def triangle(self):
        return [[0, 0], [1, 0], [0, 1]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_bary_001'
        assert specialist.service_type == 'math.geometry.barycentric'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'cartesian_to_barycentric'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, triangle):
        """Test Cartesian to barycentric conversion."""
        # Centroid has barycentric coords (1/3, 1/3, 1/3)
        request = {
            'operation': 'cartesian_to_barycentric',
            'point': [1/3, 1/3],
            'vertices': triangle
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        coords = result['barycentric']
        for c in coords:
            assert abs(c - 1/3) < 1e-10

    def test_complex_problem_solving(self, specialist, triangle):
        """Test triangle centers."""
        request = {'operation': 'triangle_centers', 'vertices': triangle}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 'centroid' in result
        assert 'incenter' in result

    def test_invalid_input_handling(self, specialist):
        # Degenerate triangle
        request = {
            'operation': 'cartesian_to_barycentric',
            'point': [0.5, 0.5],
            'vertices': [[0, 0], [1, 1], [2, 2]]  # Collinear
        }
        result = specialist.process_request(request)
        assert result['success'] is False or 'degenerate' in str(result)

    def test_edge_cases(self, specialist, triangle):
        # Point at vertex
        request = {
            'operation': 'cartesian_to_barycentric',
            'point': [0, 0],
            'vertices': triangle
        }
        result = specialist.process_request(request)
        coords = result['barycentric']
        assert abs(coords[0] - 1.0) < 1e-10
        assert abs(coords[1]) < 1e-10
        assert abs(coords[2]) < 1e-10

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, triangle):
        specialist.process_request({
            'operation': 'cartesian_to_barycentric',
            'point': [0.25, 0.25],
            'vertices': triangle
        })
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'incenter'})
        assert specialist.beliefs.get('operation') == 'incenter'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'triangle_centers'}
        desires = specialist.deliberate()
        assert 'execute_triangle_centers' in desires

    def test_bdi_execute_step(self, specialist, triangle):
        specialist.beliefs = {
            'operation': 'cartesian_to_barycentric',
            'point': [0.25, 0.25],
            'vertices': triangle
        }
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_barycentric_to_cartesian(self, specialist, triangle):
        """Test barycentric to Cartesian conversion."""
        request = {
            'operation': 'barycentric_to_cartesian',
            'barycentric': [1/3, 1/3, 1/3],
            'vertices': triangle
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        point = result['cartesian']
        assert abs(point[0] - 1/3) < 1e-10
        assert abs(point[1] - 1/3) < 1e-10

    def test_point_in_simplex(self, specialist, triangle):
        """Test point in simplex check."""
        # Inside
        request = {
            'operation': 'point_in_simplex',
            'point': [0.25, 0.25],
            'vertices': triangle
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['inside'] is True

        # Outside
        request = {
            'operation': 'point_in_simplex',
            'point': [1, 1],
            'vertices': triangle
        }
        result = specialist.process_request(request)
        assert result['inside'] is False

    def test_n_dimensional_simplex(self, specialist):
        """Test with 3D tetrahedron."""
        vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
        request = {
            'operation': 'cartesian_to_barycentric',
            'point': [0.25, 0.25, 0.25],
            'vertices': vertices
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        # Check coords sum to 1
        assert abs(sum(result['barycentric']) - 1.0) < 1e-10
