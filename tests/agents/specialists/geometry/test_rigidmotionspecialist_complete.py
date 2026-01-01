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
RIGID MOTION SPECIALIST TESTS
==============================

Comprehensive test suite for RigidMotionSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock
import math

from symbo_agentic_reasoners.agents.specialists.geometry.rigid_motion_specialist import (
    RigidMotionSpecialist
)


class TestRigidMotionSpecialistComplete:
    """Comprehensive tests for RigidMotionSpecialist."""

    @pytest.fixture
    def specialist(self):
        return RigidMotionSpecialist(agent_id='test_rigid_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def rotation_90_2d(self):
        """90 degree rotation in 2D."""
        return [[0, -1], [1, 0]]

    @pytest.fixture
    def rotation_90_z(self):
        """90 degree rotation around z-axis in 3D."""
        return [[0, -1, 0], [1, 0, 0], [0, 0, 1]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_rigid_001'
        assert specialist.service_type == 'math.geometry.rigid_motion'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'verify_rigid_motion'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, rotation_90_2d):
        """Test rigid motion verification."""
        request = {'operation': 'verify_rigid_motion', 'A': rotation_90_2d}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_rigid_motion'] is True

    def test_complex_problem_solving(self, specialist, rotation_90_z):
        """Test 3D decomposition (screw motion)."""
        request = {'operation': 'decompose_rigid_motion_3d', 'A': rotation_90_z, 'b': [0, 0, 1]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['type'] == 'screw_motion'

    def test_invalid_input_handling(self, specialist):
        # Non-orthogonal matrix
        request = {'operation': 'verify_rigid_motion', 'A': [[1, 1], [0, 1]]}
        result = specialist.process_request(request)
        assert result['is_rigid_motion'] is False

    def test_edge_cases(self, specialist):
        # Identity
        request = {'operation': 'decompose_rigid_motion_2d', 'A': [[1, 0], [0, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        decomp = result['decomposition']
        assert decomp[0]['type'] == 'identity'

        # Pure translation
        request = {'operation': 'decompose_rigid_motion_2d', 'A': [[1, 0], [0, 1]], 'b': [1, 2]}
        result = specialist.process_request(request)
        decomp = result['decomposition']
        assert decomp[0]['type'] == 'translation'

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, rotation_90_2d):
        specialist.process_request({'operation': 'verify_rigid_motion', 'A': rotation_90_2d})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'screw_motion_params'})
        assert specialist.beliefs.get('operation') == 'screw_motion_params'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'screw_motion_params'}
        desires = specialist.deliberate()
        assert 'execute_screw_motion_params' in desires

    def test_bdi_execute_step(self, specialist, rotation_90_2d):
        specialist.beliefs = {'operation': 'verify_rigid_motion', 'A': rotation_90_2d}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_distance_preservation(self, specialist, rotation_90_2d):
        """Test distance preservation proof."""
        points = [[0, 0], [1, 0], [0, 1]]
        request = {
            'operation': 'distance_preservation_proof',
            'A': rotation_90_2d,
            'b': [1, 1],
            'points': points
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['distance_preserved'] is True

    def test_angle_preservation(self, specialist, rotation_90_2d):
        """Test angle preservation proof."""
        triangles = [[[0, 0], [1, 0], [0, 1]]]
        request = {
            'operation': 'angle_preservation_proof',
            'A': rotation_90_2d,
            'b': [0, 0],
            'triangles': triangles
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['angle_preserved'] is True

    def test_decompose_2d_reflection(self, specialist):
        """Test 2D decomposition for reflection."""
        # Reflection across x-axis
        request = {'operation': 'decompose_rigid_motion_2d', 'A': [[1, 0], [0, -1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_proper'] is False

    def test_rigid_motion_from_frames(self, specialist):
        """Test computing rigid motion from frame correspondences."""
        request = {
            'operation': 'rigid_motion_from_frames',
            'origin1': [0, 0, 0],
            'basis1': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            'origin2': [1, 0, 0],
            'basis2': [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]  # 90 degree rotation around z
        }
        result = specialist.process_request(request)
        assert result['success'] is True
