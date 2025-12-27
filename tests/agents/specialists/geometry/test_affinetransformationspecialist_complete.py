# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
AFFINE TRANSFORMATION SPECIALIST TESTS
=======================================

Comprehensive test suite for AffineTransformationSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.geometry.affine_transformation_specialist import (
    AffineTransformationSpecialist
)


class TestAffineTransformationSpecialistComplete:
    """Comprehensive tests for AffineTransformationSpecialist."""

    @pytest.fixture
    def specialist(self):
        return AffineTransformationSpecialist(agent_id='test_affine_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_affine_001'
        assert specialist.service_type == 'math.geometry.affine'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'apply_affine'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test applying affine transformation."""
        A = [[2, 0], [0, 2]]
        b = [1, 1]
        points = [[0, 0], [1, 0], [0, 1]]
        request = {'operation': 'apply_affine', 'A': A, 'b': b, 'points': points}
        result = specialist.process_request(request)
        assert result['success'] is True
        # [0,0] -> [1,1], [1,0] -> [3,1], [0,1] -> [1,3]
        transformed = result['transformed_points']
        assert abs(transformed[0][0] - 1) < 1e-10
        assert abs(transformed[0][1] - 1) < 1e-10

    def test_complex_problem_solving(self, specialist):
        """Test affine from point correspondences."""
        source = [[0, 0], [1, 0], [0, 1]]
        target = [[1, 1], [3, 1], [1, 3]]
        request = {'operation': 'affine_from_points', 'source_points': source, 'target_points': target}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_invalid_input_handling(self, specialist):
        # Singular matrix
        request = {'operation': 'inverse_affine', 'A': [[1, 1], [1, 1]], 'b': [0, 0]}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # Identity transformation
        request = {'operation': 'apply_affine', 'A': [[1, 0], [0, 1]], 'b': [0, 0], 'points': [[1, 2]]}
        result = specialist.process_request(request)
        assert result['transformed_points'][0] == [1, 2]

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'apply_affine', 'A': [[1, 0], [0, 1]], 'b': [0, 0], 'points': [[1, 1]]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'compose_affine'})
        assert specialist.beliefs.get('operation') == 'compose_affine'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'compose_affine'}
        desires = specialist.deliberate()
        assert 'execute_compose_affine' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'apply_affine', 'A': [[1, 0], [0, 1]], 'b': [1, 1], 'points': [[0, 0]]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_compose_affine(self, specialist):
        """Test affine composition."""
        A1, b1 = [[2, 0], [0, 2]], [1, 0]
        A2, b2 = [[1, 0], [0, 1]], [0, 1]
        request = {'operation': 'compose_affine', 'A1': A1, 'b1': b1, 'A2': A2, 'b2': b2}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_inverse_affine(self, specialist):
        """Test affine inverse."""
        A = [[2, 0], [0, 3]]
        b = [1, 2]
        request = {'operation': 'inverse_affine', 'A': A, 'b': b}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_shear_transform(self, specialist):
        """Test shear transformation construction."""
        request = {'operation': 'shear_transform', 'direction': 0, 'factor': 0.5, 'dimension': 2}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['A'][0][1] == 0.5

    def test_affine_hull(self, specialist):
        """Test affine hull computation."""
        points = [[0, 0], [1, 0], [2, 0]]  # Collinear - 1D affine hull
        request = {'operation': 'affine_hull', 'points': points}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['dimension'] == 1
